#!/usr/bin/env python3
"""Static verifier for theory-heavy LaTeX papers.

This script does not prove mathematical correctness.
It checks project hygiene, section structure, labels/refs, theorem/proof presence,
figure/table metadata, and a few heuristic signals for rigor-oriented papers.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

SECTION_RE = re.compile(r"\\(section|subsection|subsubsection)\*?\{([^}]*)\}")
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:ref|eqref|autoref|cref|Cref|pageref)\{([^}]+)\}")
CITE_RE = re.compile(r"\\(?:cite|citet|citep|citealp|citeauthor|citeyear|Citep|Citet)\*?(?:\[[^\]]*\])?\{([^}]+)\}")
ENV_RE = re.compile(r"\\begin\{([^}]+)\}")
CAPTION_RE = re.compile(r"\\caption(?:\[[^\]]*\])?\{", re.MULTILINE)
APPENDIX_RE = re.compile(r"\\appendix|\bappendix\b", re.IGNORECASE)
BIG_O_RE = re.compile(r"O\s*\(")
COMPLEXITY_WORD_RE = re.compile(r"\b(complexity|runtime|time complexity|memory complexity|sample complexity|space complexity)\b", re.IGNORECASE)
CONVERGENCE_WORD_RE = re.compile(r"\b(convergence|regret|error bound|stability|consistency|approximation|rate)\b", re.IGNORECASE)
ROADMAP_RE = re.compile(r"\bIn Section\s+\d|\bSection\s+\d+", re.IGNORECASE)
THEOREM_ENVS = {
    "theorem", "lemma", "corollary", "proposition", "definition",
    "assumption", "remark", "claim", "example", "algorithm"
}
PROOF_ENVS = {"proof"}
FIGURE_ENVS = {"figure", "figure*"}
TABLE_ENVS = {"table", "table*"}


class Report:
    def __init__(self) -> None:
        self.blockers: List[str] = []
        self.major: List[str] = []
        self.minor: List[str] = []
        self.info: List[str] = []

    def add(self, severity: str, message: str) -> None:
        severity = severity.upper()
        if severity == "BLOCKER":
            self.blockers.append(message)
        elif severity == "MAJOR":
            self.major.append(message)
        elif severity == "MINOR":
            self.minor.append(message)
        else:
            self.info.append(message)

    def to_dict(self) -> Dict[str, List[str]]:
        return {
            "BLOCKER": self.blockers,
            "MAJOR": self.major,
            "MINOR": self.minor,
            "INFO": self.info,
        }


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        out = []
        escape = False
        for i, ch in enumerate(line):
            if ch == "\\":
                escape = not escape
                out.append(ch)
                continue
            if ch == "%" and not escape:
                break
            escape = False
            out.append(ch)
        lines.append("".join(out))
    return "\n".join(lines)


def gather_tex_files(target: Path) -> Tuple[Path | None, List[Path]]:
    if target.is_file():
        main = target
        tex_files = sorted({p for p in target.parent.rglob("*.tex") if p.is_file()})
        if main not in tex_files:
            tex_files.append(main)
            tex_files.sort()
        return main, tex_files
    tex_files = sorted(p for p in target.rglob("*.tex") if p.is_file())
    main = None
    for candidate in tex_files:
        text = strip_comments(read_text(candidate))
        if "\\documentclass" in text:
            main = candidate
            break
    return main, tex_files


def split_csv_like_keys(raw_keys: Iterable[str]) -> List[str]:
    out: List[str] = []
    for raw in raw_keys:
        for part in raw.split(","):
            key = part.strip()
            if key:
                out.append(key)
    return out


def find_env_spans(text: str, env_names: Sequence[str]) -> List[Tuple[str, int, int, str]]:
    spans: List[Tuple[str, int, int, str]] = []
    for env in env_names:
        pattern = re.compile(rf"\\begin\{{{re.escape(env)}\}}(.*?)\\end\{{{re.escape(env)}\}}", re.DOTALL)
        for m in pattern.finditer(text):
            spans.append((env, m.start(), m.end(), m.group(1)))
    return sorted(spans, key=lambda x: x[1])


def summarize_sections(text: str) -> List[Tuple[str, str]]:
    return [(m.group(1), m.group(2).strip()) for m in SECTION_RE.finditer(text)]


def count_captions_in_spans(spans: Sequence[Tuple[str, int, int, str]]) -> int:
    return sum(1 for _, _, _, body in spans if CAPTION_RE.search(body))


def labels_in_spans(spans: Sequence[Tuple[str, int, int, str]]) -> int:
    return sum(1 for _, _, _, body in spans if LABEL_RE.search(body))


def main() -> int:
    parser = argparse.ArgumentParser(description="Static verifier for LaTeX papers")
    parser.add_argument("target", help="Path to main .tex file or LaTeX project directory")
    parser.add_argument("--json", action="store_true", help="Emit JSON as well")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    if not target.exists():
        print(f"ERROR: target does not exist: {target}", file=sys.stderr)
        return 2

    main_file, tex_files = gather_tex_files(target)
    if not tex_files:
        print("ERROR: no .tex files found", file=sys.stderr)
        return 2

    report = Report()
    combined_parts: List[str] = []
    per_file_text: Dict[Path, str] = {}
    for tex in tex_files:
        text = strip_comments(read_text(tex))
        per_file_text[tex] = text
        combined_parts.append(f"\n% FILE: {tex}\n{text}\n")
    combined = "\n".join(combined_parts)

    labels = split_csv_like_keys(m.group(1) for m in LABEL_RE.finditer(combined))
    refs = split_csv_like_keys(m.group(1) for m in REF_RE.finditer(combined))
    cites = split_csv_like_keys(m.group(1) for m in CITE_RE.finditer(combined))

    label_counter = Counter(labels)
    duplicate_labels = sorted(k for k, v in label_counter.items() if v > 1)
    undefined_refs = sorted(set(refs) - set(labels))

    if duplicate_labels:
        report.add("BLOCKER", f"Duplicate labels found ({len(duplicate_labels)}): {', '.join(duplicate_labels[:10])}")
    if undefined_refs:
        report.add("BLOCKER", f"Undefined refs found ({len(undefined_refs)}): {', '.join(undefined_refs[:10])}")

    sections = summarize_sections(per_file_text[main_file] if main_file else combined)
    section_titles = [title.lower() for _, title in sections]
    has_intro = any("introduction" in t for t in section_titles)
    has_conclusion = any("conclusion" in t for t in section_titles)
    has_background = any(any(k in t for k in ["prelim", "background", "notation"]) for t in section_titles)
    has_experiments = any(any(k in t for k in ["experiment", "numerical", "results"]) for t in section_titles)
    has_theory = any(any(k in t for k in ["theoretical", "analysis", "convergence", "error", "regret"]) for t in section_titles)

    if not has_intro:
        report.add("MAJOR", "No Introduction section detected.")
    if not has_conclusion:
        report.add("MAJOR", "No Conclusion section detected.")
    if not has_background:
        report.add("MAJOR", "No Background/Preliminaries/Notation section detected.")
    if not has_experiments:
        report.add("MAJOR", "No Experiments/Numerical Results section detected.")
    if not has_theory:
        report.add("MAJOR", "No Theoretical Analysis / Convergence / Error / Regret section detected.")

    if main_file:
        main_text = per_file_text[main_file]
        if not ROADMAP_RE.search(main_text[:12000]):
            report.add("MINOR", "No section-roadmap pattern detected early in the main file.")
        if "contribution" not in main_text[:12000].lower():
            report.add("MINOR", "No obvious contributions list/signpost detected in the introduction region.")

    theorem_spans = find_env_spans(combined, sorted(THEOREM_ENVS))
    proof_spans = find_env_spans(combined, sorted(PROOF_ENVS))
    figure_spans = find_env_spans(combined, sorted(FIGURE_ENVS))
    table_spans = find_env_spans(combined, sorted(TABLE_ENVS))

    theorem_counts = Counter(env for env, *_ in theorem_spans)
    proof_count = len(proof_spans)
    figure_count = len(figure_spans)
    table_count = len(table_spans)

    if sum(theorem_counts.values()) > 0 and proof_count == 0:
        report.add("BLOCKER", "Formal theorem-like environments are present but no proof environment was detected.")
    elif sum(theorem_counts.values()) > proof_count and not APPENDIX_RE.search(combined):
        report.add("MAJOR", "More theorem-like statements than proofs, and no appendix marker was detected.")

    fig_captions = count_captions_in_spans(figure_spans)
    fig_labels = labels_in_spans(figure_spans)
    if figure_count > 0 and fig_captions < figure_count:
        report.add("MAJOR", f"Some figures are missing captions ({fig_captions}/{figure_count} have captions).")
    if figure_count > 0 and fig_labels < figure_count:
        report.add("MINOR", f"Some figures are missing labels ({fig_labels}/{figure_count} have labels).")

    table_captions = count_captions_in_spans(table_spans)
    table_labels = labels_in_spans(table_spans)
    if table_count > 0 and table_captions < table_count:
        report.add("MAJOR", f"Some tables are missing captions ({table_captions}/{table_count} have captions).")
    if table_count > 0 and table_labels < table_count:
        report.add("MINOR", f"Some tables are missing labels ({table_labels}/{table_count} have labels).")

    if not BIG_O_RE.search(combined) and not COMPLEXITY_WORD_RE.search(combined):
        report.add("MINOR", "No obvious complexity notation or complexity discussion detected.")
    if not CONVERGENCE_WORD_RE.search(combined):
        report.add("MINOR", "No obvious convergence/regret/error/stability language detected.")
    if not APPENDIX_RE.search(combined) and sum(theorem_counts.values()) >= 3:
        report.add("MINOR", "Several theorem-like statements detected but no appendix marker found.")
    if len(cites) == 0:
        report.add("MAJOR", "No citation commands detected.")

    if main_file and "\\input{" not in per_file_text[main_file] and len(tex_files) > 3:
        report.add("INFO", "Project has multiple TeX files but the detected main file does not visibly use \\input{...}; verify project structure manually.")

    summary = {
        "main_file": str(main_file) if main_file else None,
        "tex_file_count": len(tex_files),
        "section_count": len(sections),
        "sections": sections,
        "label_count": len(labels),
        "ref_count": len(refs),
        "citation_count": len(cites),
        "duplicate_labels": duplicate_labels,
        "undefined_refs": undefined_refs,
        "theorem_env_counts": dict(theorem_counts),
        "proof_count": proof_count,
        "figure_count": figure_count,
        "table_count": table_count,
        "figure_captions": fig_captions,
        "table_captions": table_captions,
        "report": report.to_dict(),
    }

    print("# Static LaTeX Review Report")
    print()
    print(f"Main file: {summary['main_file']}")
    print(f"TeX files: {summary['tex_file_count']}")
    print(f"Sections: {summary['section_count']}")
    print(f"Labels: {summary['label_count']} | Refs: {summary['ref_count']} | Citations: {summary['citation_count']}")
    print(f"Theorem-like envs: {sum(theorem_counts.values())} | Proofs: {proof_count} | Figures: {figure_count} | Tables: {table_count}")
    print()
    if sections:
        print("## Section outline")
        for level, title in sections:
            print(f"- {level}: {title}")
        print()

    for severity in ["BLOCKER", "MAJOR", "MINOR", "INFO"]:
        items = summary["report"][severity]
        print(f"## {severity}")
        if not items:
            print("- None")
        else:
            for item in items:
                print(f"- {item}")
        print()

    if args.json:
        print("## JSON")
        print(json.dumps(summary, indent=2))

    return 0 if not summary["report"]["BLOCKER"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
