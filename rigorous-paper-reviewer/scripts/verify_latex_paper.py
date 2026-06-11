#!/usr/bin/env python3
"""Static verifier for theory-heavy LaTeX papers.

This script does not prove mathematical correctness.
It checks project hygiene, section structure, labels/refs, theorem/proof presence,
figure/table metadata, and a few heuristic signals for rigor-oriented papers.

The checks are document-kind aware. A conference paper and a standalone theory
note have different surface forms, so the verifier should not demand an
Introduction/Conclusion/complexity block from a note that has a route map,
claims-and-support section, and open-problem closure instead.
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
ROUTE_MAP_RE = re.compile(r"\b(route map|what this note does|the chain|we proceed|we now)\b", re.IGNORECASE)
CLAIM_SIGNPOST_RE = re.compile(
    r"\b(contribution|we contribute|we show|we prove|we establish|claims? and their support|what is standard|what is new)\b",
    re.IGNORECASE,
)
THEORY_NOTE_HINT_RE = re.compile(
    r"\b(master equation|fokker|generator|filtering|zakai|kushner|realization|standing assumptions|"
    r"open problems?|claims? and their support|what this note does|route map|the chain)\b",
    re.IGNORECASE,
)
THEORY_BEARING_TITLE_RE = re.compile(
    r"\b(theorem|lemma|proposition|claim|analysis|derivation|generator|master equation|fokker|filtering|"
    r"realization|port-hamiltonian|stochastic|closed-loop|claims?)\b",
    re.IGNORECASE,
)
CONCLUSION_LIKE_TITLE_RE = re.compile(r"\b(conclusion|discussion|future|open problems?|claims?, experiments)\b", re.IGNORECASE)
EXPERIMENT_LIKE_TITLE_RE = re.compile(r"\b(experiment|numerical|results?|evaluation|obligations?)\b", re.IGNORECASE)
VERIFY_MARKER_RE = re.compile(r"\[(?:verify|citation needed|check)\]|\bTODO\b|\bFIXME\b", re.IGNORECASE)
THEOREM_ENVS = {
    "theorem", "lemma", "corollary", "proposition", "definition",
    "assumption", "remark", "claim", "example", "algorithm"
}
PROOF_ENVS = {"proof"}
FIGURE_ENVS = {"figure", "figure*"}
TABLE_ENVS = {"table", "table*"}
KIND_CHOICES = ("auto", "conference-paper", "theory-note")


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


def has_title_like(section_titles: Sequence[str], pattern: re.Pattern[str]) -> bool:
    return any(pattern.search(title) for title in section_titles)


def has_title_term(section_titles: Sequence[str], terms: Sequence[str]) -> bool:
    return any(any(term in title for term in terms) for title in section_titles)


def detect_document_kind(
    explicit_kind: str,
    target: Path,
    main_file: Path | None,
    section_titles: Sequence[str],
    combined: str,
) -> str:
    if explicit_kind != "auto":
        return explicit_kind

    path_blob = f"{target} {main_file or ''}".lower()
    title_blob = " ".join(section_titles)
    theory_note_score = 0

    if "docs/theory" in path_blob or "/theory/" in path_blob:
        theory_note_score += 1
    if has_title_term(section_titles, ["purpose", "route map", "what this note does", "the chain"]):
        theory_note_score += 2
    if has_title_term(section_titles, ["claims and their support", "what is standard", "what is new", "open problems"]):
        theory_note_score += 2
    if THEORY_NOTE_HINT_RE.search(title_blob):
        theory_note_score += 1
    if THEORY_NOTE_HINT_RE.search(combined[:18000]):
        theory_note_score += 1

    conference_score = 0
    if has_title_term(section_titles, ["introduction", "related work", "experiments", "conclusion"]):
        conference_score += 2
    if "\\begin{abstract}" in combined[:12000]:
        conference_score += 1

    if theory_note_score >= 3 and theory_note_score >= conference_score:
        return "theory-note"
    return "conference-paper"


def find_upward(start: Path, relative: str) -> Path | None:
    base = start if start.is_dir() else start.parent
    for parent in [base, *base.parents]:
        candidate = parent / relative
        if candidate.exists():
            return candidate
    return None


def find_bundled_discourse_tool() -> Path | None:
    skills_root = Path(__file__).resolve().parents[2]
    candidate = skills_root / "paper-discourse-graph" / "scripts" / "discourse_graph_audit.py"
    return candidate if candidate.exists() else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Static verifier for LaTeX papers")
    parser.add_argument("target", help="Path to main .tex file or LaTeX project directory")
    parser.add_argument(
        "--kind",
        choices=KIND_CHOICES,
        default="auto",
        help="Document kind. Use theory-note for standalone notes without conference-paper sections.",
    )
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
    doc_kind = detect_document_kind(args.kind, target, main_file, section_titles, combined)
    review_brief = find_upward(main_file or target, "AGENT_REVIEW_BRIEF.md")
    discourse_tool = find_upward(main_file or target, "tools/discourse_graph/cli.py") or find_bundled_discourse_tool()

    has_intro = any("introduction" in t for t in section_titles)
    has_intro_like = has_intro or has_title_term(section_titles, ["purpose", "route map", "what this note does"])
    has_conclusion = any("conclusion" in t for t in section_titles)
    has_conclusion_like = has_conclusion or has_title_like(section_titles, CONCLUSION_LIKE_TITLE_RE)
    has_background = any(any(k in t for k in ["prelim", "background", "notation"]) for t in section_titles)
    has_experiments = any(any(k in t for k in ["experiment", "numerical", "results"]) for t in section_titles)
    has_experiments_like = has_experiments or has_title_like(section_titles, EXPERIMENT_LIKE_TITLE_RE)
    has_theory = any(any(k in t for k in ["theoretical", "analysis", "convergence", "error", "regret"]) for t in section_titles)
    has_theory_like = has_theory or has_title_like(section_titles, THEORY_BEARING_TITLE_RE) or bool(
        re.search(r"\\begin\{(?:theorem|lemma|proposition|claim|assumption)\}", combined)
    )

    if doc_kind == "theory-note":
        if not has_intro_like:
            report.add("MINOR", "Theory note has no Introduction or Purpose/route-map opening.")
        if not has_conclusion_like:
            report.add("MINOR", "Theory note has no Conclusion, claims/open-problems, or discussion-style closing section.")
        if not has_background:
            report.add("MAJOR", "No Notation/Standing assumptions/Background section detected.")
        if not has_theory_like:
            report.add("MAJOR", "No theory-bearing section or theorem/claim/assumption environment detected.")
        if not has_experiments_like:
            report.add("INFO", "No experiment-obligations/results section detected; acceptable for a pure note, but check claim support manually.")
    else:
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
        early_text = main_text[:12000]
        if doc_kind == "theory-note":
            if not (ROADMAP_RE.search(early_text) or ROUTE_MAP_RE.search(early_text)):
                report.add("MINOR", "No route-map or reader-path signpost detected early in the theory note.")
            if not CLAIM_SIGNPOST_RE.search(early_text):
                report.add("MINOR", "No obvious claims-and-support or standard-vs-new signpost detected early in the theory note.")
        else:
            if not ROADMAP_RE.search(early_text):
                report.add("MINOR", "No section-roadmap pattern detected early in the main file.")
            if not CLAIM_SIGNPOST_RE.search(early_text):
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

    if doc_kind != "theory-note" and not BIG_O_RE.search(combined) and not COMPLEXITY_WORD_RE.search(combined):
        report.add("MINOR", "No obvious complexity notation or complexity discussion detected.")
    elif doc_kind == "theory-note" and theorem_counts.get("algorithm", 0) > 0 and not COMPLEXITY_WORD_RE.search(combined):
        report.add("INFO", "Algorithm environment detected in a theory note without complexity discussion; verify this is intentional.")
    if not CONVERGENCE_WORD_RE.search(combined):
        if doc_kind == "theory-note":
            report.add("INFO", "No convergence/regret/error/stability language detected; verify no rate or stability claim is implied.")
        else:
            report.add("MINOR", "No obvious convergence/regret/error/stability language detected.")
    if not APPENDIX_RE.search(combined) and sum(theorem_counts.values()) >= 3:
        report.add("MINOR", "Several theorem-like statements detected but no appendix marker found.")
    if len(cites) == 0:
        report.add("MAJOR", "No citation commands detected.")
    verify_markers = VERIFY_MARKER_RE.findall(combined)
    if verify_markers:
        severity = "MAJOR" if doc_kind == "theory-note" else "MINOR"
        report.add(severity, f"Citation/status verification markers remain ({len(verify_markers)} occurrences).")

    if main_file and "\\input{" not in per_file_text[main_file] and len(tex_files) > 3:
        report.add("INFO", "Project has multiple TeX files but the detected main file does not visibly use \\input{...}; verify project structure manually.")
    if review_brief:
        report.add("INFO", f"Project review brief found: {review_brief}. Read it before judging story, scope, or local terminology.")
    if discourse_tool:
        report.add("INFO", f"Discourse-graph tool found: {discourse_tool}. Use it for paragraph-flow and breadcrumb audits when useful.")

    summary = {
        "main_file": str(main_file) if main_file else None,
        "document_kind": doc_kind,
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
        "review_brief": str(review_brief) if review_brief else None,
        "discourse_graph_tool": str(discourse_tool) if discourse_tool else None,
        "report": report.to_dict(),
    }

    print("# Static LaTeX Review Report")
    print()
    print(f"Main file: {summary['main_file']}")
    print(f"Document kind: {summary['document_kind']}")
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
