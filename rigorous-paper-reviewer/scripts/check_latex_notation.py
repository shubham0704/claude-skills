#!/usr/bin/env python3
"""Audit first use, explanation, and role drift of notation in LaTeX.

This is a deliberately conservative static checker. It inventories symbols in
math mode, follows ``\\input``/``\\include`` order, and reports likely notation
debt. It does not attempt to parse TeX completely or establish mathematical
correctness; its output is triage for a human notation pass.
"""
from __future__ import annotations

import argparse
import bisect
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator, Sequence


MATH_ENVS = (
    "equation",
    "equation*",
    "align",
    "align*",
    "aligned",
    "gather",
    "gather*",
    "multline",
    "multline*",
    "split",
)
MATH_RE = re.compile(
    rf"\\begin\{{(?P<env>{'|'.join(re.escape(name) for name in MATH_ENVS)})\}}"
    r"(?P<env_body>.*?)\\end\{(?P=env)\}"
    r"|(?<!\\)\\\[(?P<bracket>.*?)\\\]"
    r"|(?<!\\)\\\((?P<paren>.*?)\\\)"
    r"|(?<!\\)\$\$(?P<dollars>.*?)(?<!\\)\$\$"
    r"|(?<!\\)\$(?!\$)(?P<inline>.*?)(?<!\\)\$",
    re.DOTALL,
)
INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
FRAME_RE = re.compile(r"\\begin\{frame\}(?:\[[^]]*\])?(?:\{([^}]*)\})?")
FRAME_TITLE_RE = re.compile(r"\\frametitle\{([^}]*)\}")
SECTION_RE = re.compile(r"\\(section|subsection|subsubsection)\*?\{([^}]*)\}")
RELATION_RE = re.compile(r"\\coloneqq|\\triangleq|:=|(?<![<>!])=(?!=)|\\in\b|\\sim\b")

GREEK_SYMBOLS = {
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta",
    "eta", "theta", "vartheta", "iota", "kappa", "lambda", "mu", "nu",
    "xi", "omicron", "pi", "varpi", "rho", "varrho", "sigma", "varsigma",
    "tau", "upsilon", "phi", "varphi", "chi", "psi", "omega", "Gamma",
    "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Upsilon", "Phi",
    "Psi", "Omega", "ell",
}
STYLE_COMMANDS = {"mathcal", "mathscr", "mathbb", "mathbf", "boldsymbol", "mathsf"}
PRESERVE_DECORATORS = {"hat", "widehat", "tilde", "widetilde", "bar", "overline"}
DROP_DECORATORS = {"dot", "ddot", "vec"}
SKIP_GROUP_COMMANDS = {
    "text", "textrm", "textsf", "texttt", "textbf", "textit", "mathrm", "mbox",
    "operatorname", "label", "tag", "ref", "eqref", "autoref", "cref",
    "Cref", "cite", "citep", "citet", "color", "url", "href", "phantom",
    "begin", "end",
}
SKIP_COMMANDS = {
    "left", "right", "big", "Big", "bigg", "Bigg", "bigl", "bigr", "Bigl",
    "Bigr", "biggl", "biggr", "Biggl", "Biggr", "quad", "qquad", "cdot",
    "times", "otimes", "oplus", "mid", "vert", "Vert", "langle", "rangle",
    "le", "leq", "ge", "geq", "neq", "approx", "propto", "to", "mapsto",
    "rightarrow", "leftarrow", "Rightarrow", "Leftarrow", "iff", "implies",
    "sum", "prod", "int", "oint", "min", "max", "argmin", "argmax", "inf",
    "sup", "lim", "log", "exp", "sin", "cos", "tan", "det", "diag", "tr",
    "nabla", "partial", "sqrt", "frac", "tfrac", "dfrac",
    "underbrace", "overbrace", "boxed", "mathrel", "mathbin", "mathop", "top",
    "perp", "star", "ast", "dagger", "pm", "mp", "colon", "Pr", "E",
}
DEFAULT_IGNORE = {
    "i", "j", "k", "n", "t", "e", r"\pi", r"\infty",
    r"\mathbb{R}", r"\mathbb{C}", r"\mathbb{N}", r"\mathbb{Z}", r"\mathbb{P}",
    r"\mathbb{E}", r"\mathbb{S}",
}
EXPLANATION_AFTER_RE = re.compile(
    r"^\s*(?:is|are|denotes?|represents?|means?|refers?\s+to|stands?\s+for|"
    r"measures?|collects?|contains?|stores?|generates?|removes?|locates?|"
    r"selects?|acts?|changes?|governs?|parameteri[sz]es?|advances?|determines?|"
    r"makes?|says?|follows?|may\s+(?:change|select|denote)|the\b|a\b|an\b)",
    re.IGNORECASE,
)
EXPLANATION_BEFORE_RE = re.compile(
    r"(?:state|input|output|belief|kernel|law|parameter|measurement|observation|"
    r"trajectory|policy|cost|loss|energy|damping|inertia|potential|momentum|"
    r"coordinate|space|graph|map|operator|matrix|tensor|horizon|mass|rod|length|"
    r"torque|step|scaffold|infer|estimate|predict|learn)\s*$",
    re.IGNORECASE,
)
DEFINITION_CONTEXT_RE = re.compile(
    r"\b(?:define|denote|write|let|called|given|collect|model|state|law|kernel|"
    r"objective|problem|dynamics|measurement|observation)\b",
    re.IGNORECASE,
)
TEMPORAL_SUBSCRIPT_RE = re.compile(
    r"^(?:[tijkn]|[0-9]+|[tijkn0-9][tijkn0-9:+\-KH]*|0:t(?:[-+]\d+)?)$"
)


@dataclass
class SourceLine:
    text: str
    path: Path
    line: int
    unit_id: str = "front"
    unit_title: str = "Front matter"


@dataclass
class MathSpan:
    body: str
    start: int
    end: int
    kind: str
    source: SourceLine


@dataclass
class SymbolToken:
    symbol: str
    display: str
    start: int
    end: int


@dataclass
class Occurrence:
    symbol: str
    display: str
    position: int
    path: str
    line: int
    unit_id: str
    unit_title: str
    role: str
    definition: bool = False
    numeric_definition: bool = False
    explained: bool = False


@dataclass
class Issue:
    severity: str
    code: str
    symbol: str
    message: str
    path: str
    line: int
    unit: str


@dataclass
class AuditResult:
    target: str
    scope: str
    document_kind: str
    units: int
    symbols: dict[str, dict[str, Any]] = field(default_factory=dict)
    issues: list[Issue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "scope": self.scope,
            "document_kind": self.document_kind,
            "units": self.units,
            "summary": {
                "symbols": len(self.symbols),
                "errors": sum(issue.severity == "ERROR" for issue in self.issues),
                "warnings": sum(issue.severity == "WARNING" for issue in self.issues),
                "info": sum(issue.severity == "INFO" for issue in self.issues),
            },
            "issues": [asdict(issue) for issue in self.issues],
            "symbols": self.symbols,
        }


def strip_comment(line: str) -> str:
    for index, char in enumerate(line):
        if char != "%":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and line[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2 == 0:
            return line[:index]
    return line


def resolve_main(target: Path) -> Path:
    if target.is_file():
        return target
    preferred = target / "main.tex"
    if preferred.exists():
        return preferred
    candidates = sorted(target.rglob("*.tex"))
    for candidate in candidates:
        if "\\documentclass" in candidate.read_text(encoding="utf-8", errors="replace"):
            return candidate
    raise ValueError(f"no LaTeX entry point found under {target}")


def resolve_include(parent: Path, raw: str) -> Path | None:
    candidate = (parent / raw.strip()).resolve()
    if candidate.suffix == "":
        candidate = candidate.with_suffix(".tex")
    return candidate if candidate.exists() else None


def expand_document(main: Path, scope: str) -> tuple[list[SourceLine], list[str]]:
    lines: list[SourceLine] = []
    warnings: list[str] = []
    active: set[Path] = set()
    appendix_reached = False

    def visit(path: Path) -> None:
        nonlocal appendix_reached
        path = path.resolve()
        if path in active:
            warnings.append(f"cyclic include skipped: {path}")
            return
        active.add(path)
        raw_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line_number, raw_line in enumerate(raw_lines, 1):
            clean = strip_comment(raw_line)
            if "\\appendix" in clean:
                appendix_reached = True
                if scope == "main":
                    break
            if appendix_reached and scope == "main":
                break
            cursor = 0
            for match in INPUT_RE.finditer(clean):
                prefix = clean[cursor:match.start()]
                if prefix.strip():
                    lines.append(SourceLine(prefix, path, line_number))
                included = resolve_include(path.parent, match.group(1))
                if included is None:
                    warnings.append(f"unresolved include at {path}:{line_number}: {match.group(1)}")
                else:
                    visit(included)
                cursor = match.end()
            suffix = clean[cursor:]
            if suffix.strip() or not INPUT_RE.search(clean):
                lines.append(SourceLine(suffix, path, line_number))
        active.remove(path)

    visit(main)
    return lines, warnings


def assign_units(lines: list[SourceLine]) -> tuple[str, int]:
    joined = "\n".join(line.text for line in lines[:100])
    is_beamer = bool(re.search(r"\\documentclass(?:\[[^]]*\])?\{beamer\}", joined))
    if is_beamer:
        frame_index = 0
        current_id = "outside"
        current_title = "Outside frames"
        for line in lines:
            frame_match = FRAME_RE.search(line.text)
            if frame_match:
                frame_index += 1
                current_id = f"slide-{frame_index}"
                current_title = clean_tex_text(frame_match.group(1) or f"Slide {frame_index}")
            title_match = FRAME_TITLE_RE.search(line.text)
            if title_match:
                current_title = clean_tex_text(title_match.group(1))
            line.unit_id = current_id
            line.unit_title = current_title
            if "\\end{frame}" in line.text:
                current_id = "outside"
                current_title = "Outside frames"
        return "beamer", frame_index

    section_index = 0
    current_id = "front"
    current_title = "Front matter"
    for line in lines:
        match = SECTION_RE.search(line.text)
        if match:
            section_index += 1
            current_id = f"section-{section_index}"
            current_title = clean_tex_text(match.group(2))
        line.unit_id = current_id
        line.unit_title = current_title
    return "paper", section_index + 1


def clean_tex_text(text: str) -> str:
    text = re.sub(r"\\(?:textbf|textit|emph|texorpdfstring)\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\[A-Za-z@]+", "", text)
    return re.sub(r"[{}~&]+", " ", text).strip()


def build_text(lines: Sequence[SourceLine], document_kind: str) -> tuple[str, list[int], list[SourceLine]]:
    chunks: list[str] = []
    offsets: list[int] = []
    active_lines: list[SourceLine] = []
    cursor = 0
    in_document = False
    for line in lines:
        if "\\begin{document}" in line.text:
            in_document = True
        if not in_document:
            continue
        if document_kind == "beamer" and line.unit_id == "outside":
            continue
        offsets.append(cursor)
        chunks.append(line.text)
        active_lines.append(line)
        cursor += len(line.text) + 1
    return "\n".join(chunks), offsets, active_lines


def iter_math_spans(text: str, offsets: Sequence[int], lines: Sequence[SourceLine]) -> Iterator[MathSpan]:
    if not offsets:
        return
    for match in MATH_RE.finditer(text):
        group = next(name for name in ("env_body", "bracket", "paren", "dollars", "inline") if match.group(name) is not None)
        start = match.start(group)
        line_index = max(0, bisect.bisect_right(offsets, start) - 1)
        yield MathSpan(
            body=match.group(group),
            start=start,
            end=match.end(group),
            kind="inline" if group in {"paren", "inline"} else "display",
            source=lines[line_index],
        )


def read_command(text: str, start: int) -> tuple[str, int]:
    cursor = start + 1
    while cursor < len(text) and (text[cursor].isalpha() or text[cursor] == "@"):
        cursor += 1
    if cursor == start + 1 and cursor < len(text):
        cursor += 1
    return text[start + 1:cursor], cursor


def read_group(text: str, start: int) -> tuple[str, int] | None:
    cursor = start
    while cursor < len(text) and text[cursor].isspace():
        cursor += 1
    if cursor >= len(text) or text[cursor] != "{":
        return None
    depth = 0
    for index in range(cursor, len(text)):
        if text[index] == "{" and (index == 0 or text[index - 1] != "\\"):
            depth += 1
        elif text[index] == "}" and (index == 0 or text[index - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return text[cursor + 1:index], index + 1
    return None


def read_atom(text: str, start: int) -> tuple[str, int] | None:
    cursor = start
    while cursor < len(text) and text[cursor].isspace():
        cursor += 1
    grouped = read_group(text, cursor)
    if grouped is not None:
        return grouped
    if cursor < len(text) and text[cursor] == "\\":
        command, end = read_command(text, cursor)
        return "\\" + command, end
    if cursor < len(text):
        return text[cursor], cursor + 1
    return None


def normalize_inner_symbol(raw: str) -> str | None:
    raw = raw.strip()
    if re.fullmatch(r"[A-Za-z]", raw):
        return raw
    if re.fullmatch(r"\\[A-Za-z]+", raw) and raw[1:] in GREEK_SYMBOLS:
        return raw
    return None


def normalize_subscript(raw: str) -> str | None:
    value = raw.strip()
    if re.fullmatch(r"\\Delta\s*t", value):
        return r"\Delta t"
    value = re.sub(r"\\(?:mathrm|textrm|text|mathsf)\s*\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\rm\s+", "", value)
    value = value.replace("\\!", "").replace("\\,", "")
    value = re.sub(r"\s+", "", value)
    value = value.strip("{}")
    if not value or len(value) > 24 or "," in value:
        return None
    if TEMPORAL_SUBSCRIPT_RE.fullmatch(value):
        return None
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9]*|\\[A-Za-z]+", value):
        return value
    return None


def consume_scripts(text: str, cursor: int) -> tuple[str | None, int]:
    semantic_subscript: str | None = None
    while True:
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        if cursor >= len(text) or text[cursor] not in "_^":
            break
        marker = text[cursor]
        atom = read_atom(text, cursor + 1)
        if atom is None:
            break
        raw, cursor = atom
        if marker == "_":
            semantic_subscript = normalize_subscript(raw)
    return semantic_subscript, cursor


def scan_symbols(math: str) -> list[SymbolToken]:
    tokens: list[SymbolToken] = []
    cursor = 0
    while cursor < len(math):
        char = math[cursor]
        if char == "\\":
            command, after_command = read_command(math, cursor)
            if command in STYLE_COMMANDS:
                atom = read_atom(math, after_command)
                if atom is not None:
                    inner, end = atom
                    base = normalize_inner_symbol(inner)
                    if base:
                        semantic, end = consume_scripts(math, end)
                        inner_display = base[1:] if base.startswith("\\") else base
                        canonical = f"\\{command}{{{inner_display}}}"
                        if semantic:
                            canonical += f"_{{{semantic}}}"
                        tokens.append(SymbolToken(canonical, math[cursor:end], cursor, end))
                        cursor = end
                        continue
            if command in PRESERVE_DECORATORS or command in DROP_DECORATORS:
                atom = read_atom(math, after_command)
                if atom is not None:
                    inner, end = atom
                    base = normalize_inner_symbol(inner)
                    if base:
                        semantic, end = consume_scripts(math, end)
                        canonical = base if command in DROP_DECORATORS else f"\\{command}{{{base}}}"
                        if semantic:
                            canonical += f"_{{{semantic}}}"
                        tokens.append(SymbolToken(canonical, math[cursor:end], cursor, end))
                        cursor = end
                        continue
            if command in SKIP_GROUP_COMMANDS:
                group = read_group(math, after_command)
                cursor = group[1] if group is not None else after_command
                continue
            if command in GREEK_SYMBOLS:
                semantic, end = consume_scripts(math, after_command)
                canonical = "\\" + command
                if semantic:
                    canonical += f"_{{{semantic}}}"
                tokens.append(SymbolToken(canonical, math[cursor:end], cursor, end))
                cursor = end
                continue
            cursor = after_command
            continue
        if char.isascii() and char.isalpha():
            dimension = re.match(r"(?:em|ex|pt|cm|mm|in)\b", math[cursor:])
            if dimension and cursor > 0 and (math[cursor - 1].isdigit() or math[cursor - 1] == "."):
                cursor += len(dimension.group(0))
                continue
            semantic, end = consume_scripts(math, cursor + 1)
            canonical = char + (f"_{{{semantic}}}" if semantic else "")
            tokens.append(SymbolToken(canonical, math[cursor:end], cursor, end))
            cursor = end
            continue
        cursor += 1
    return tokens


def role_for_token(math: str, token: SymbolToken) -> str:
    tail = math[token.end:]
    tail = re.sub(r"^(?:\s|\\[!,;:]|\\left|\\bigl|\\Bigl|\\biggl|\\Biggl)+", "", tail)
    if re.match(r"^\(\s*t(?:\s*[+\-]\s*\d+)?\s*\)", tail):
        return "value"
    return "callable" if tail.startswith(("(", "[")) else "value"


def split_equations(body: str) -> list[tuple[str, int]]:
    segments: list[tuple[str, int]] = []
    start = 0
    separator = re.compile(r"\\\\(?:\[[^]]*\])?|,\s*(?:&|\\qquad)")
    for match in separator.finditer(body):
        segments.append((body[start:match.start()], start))
        start = match.end()
    segments.append((body[start:], start))
    return segments


def definition_token_indexes(body: str, tokens: Sequence[SymbolToken]) -> dict[int, bool]:
    definitions: dict[int, bool] = {}
    for segment, segment_start in split_equations(body.replace("{=}", "=")):
        relation = RELATION_RE.search(segment)
        if relation is None:
            continue
        lhs_end = segment_start + relation.start()
        lhs_indexes = [index for index, token in enumerate(tokens) if segment_start <= token.start < lhs_end]
        if not lhs_indexes:
            continue
        lhs = segment[:relation.start()].strip().lstrip("&")
        rhs = segment[relation.end():].strip().lstrip("&{(")
        numeric_rhs = bool(re.match(r"^[+\-]?(?:\d|\.\d)", rhs))
        first_token = tokens[lhs_indexes[0]]
        prefix = body[segment_start:first_token.start]
        inside_tuple = prefix.count("(") > prefix.count(")") or prefix.count("[") > prefix.count("]")
        if lhs.startswith(("(", "[")) or (inside_tuple and "," in lhs):
            for index in lhs_indexes:
                definitions[index] = numeric_rhs
            continue
        if len(lhs_indexes) >= 2 and tokens[lhs_indexes[0]].symbol == "d":
            definitions[lhs_indexes[1]] = numeric_rhs
            continue
        candidate = lhs_indexes[0]
        if tokens[candidate].display.lstrip().startswith(tuple(f"\\{name}" for name in DROP_DECORATORS)):
            continue
        definitions[candidate] = numeric_rhs
    return definitions


def explanation_for_span(span: MathSpan, text: str, symbols: Sequence[SymbolToken]) -> bool:
    before = clean_tex_text(text[max(0, span.start - 120):span.start]).lower().rstrip("$\\[({ ")
    after = clean_tex_text(text[span.end:min(len(text), span.end + 160)]).lower().lstrip("$\\])} ")
    if EXPLANATION_AFTER_RE.search(after) or EXPLANATION_BEFORE_RE.search(before):
        return True
    if span.kind == "display" and DEFINITION_CONTEXT_RE.search(before[-100:]):
        return True
    return False


def load_registry(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"ignore": [], "symbols": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("notation registry must be a JSON object")
    if not isinstance(data.get("ignore", []), list) or not isinstance(data.get("symbols", {}), dict):
        raise ValueError("registry fields 'ignore' and 'symbols' must be a list and object")
    return data


def unit_texts(lines: Sequence[SourceLine]) -> dict[str, str]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for line in lines:
        grouped[line.unit_id].append(line.text)
    return {unit: clean_tex_text(" ".join(parts)).lower() for unit, parts in grouped.items()}


def location(occurrence: Occurrence) -> str:
    return f"{occurrence.path}:{occurrence.line}"


def explanation_is_near(first: Occurrence, explanations: Sequence[Occurrence]) -> bool:
    return any(
        item.unit_id == first.unit_id and abs(item.position - first.position) <= 1400
        for item in explanations
    )


def registry_key(raw: str) -> str:
    tokens = scan_symbols(raw)
    return tokens[0].symbol if tokens else raw.strip()


def audit(target: Path, scope: str = "main", registry_path: Path | None = None) -> tuple[AuditResult, list[str]]:
    main = resolve_main(target.resolve())
    lines, loader_warnings = expand_document(main, scope)
    document_kind, unit_count = assign_units(lines)
    text, offsets, active_lines = build_text(lines, document_kind)
    units = unit_texts(active_lines)
    registry = load_registry(registry_path)
    registry_symbols = {registry_key(key): value for key, value in registry.get("symbols", {}).items()}
    ignored = DEFAULT_IGNORE | {registry_key(item) for item in registry.get("ignore", [])}

    occurrences: dict[str, list[Occurrence]] = defaultdict(list)
    for span in iter_math_spans(text, offsets, active_lines):
        tokens = scan_symbols(span.body)
        definition_indexes = definition_token_indexes(span.body, tokens)
        span_explained = explanation_for_span(span, text, tokens)
        for index, token in enumerate(tokens):
            if token.symbol in ignored:
                continue
            absolute_position = span.start + token.start
            line_index = max(0, bisect.bisect_right(offsets, absolute_position) - 1)
            source = active_lines[line_index]
            is_definition = index in definition_indexes
            occurrences[token.symbol].append(
                Occurrence(
                    symbol=token.symbol,
                    display=token.display,
                    position=span.start + token.start,
                    path=str(source.path),
                    line=source.line,
                    unit_id=source.unit_id,
                    unit_title=source.unit_title,
                    role=role_for_token(span.body, token),
                    definition=is_definition,
                    numeric_definition=definition_indexes.get(index, False),
                    explained=span_explained and (span.kind == "inline" or is_definition),
                )
            )

    result = AuditResult(str(main), scope, document_kind, unit_count)
    for symbol, items in sorted(occurrences.items()):
        items.sort(key=lambda item: item.position)
        first = items[0]
        definitions = [item for item in items if item.definition]
        explanations = [item for item in items if item.explained]
        first_declaration = min(definitions + explanations, key=lambda item: item.position) if definitions or explanations else None
        registry_entry = registry_symbols.get(symbol, {})
        terms = [str(term).lower() for term in registry_entry.get("terms", [])]
        registry_explained = bool(terms) and any(term in units.get(first.unit_id, "") for term in terms)
        result.symbols[symbol] = {
            "first_use": {"path": first.path, "line": first.line, "unit": first.unit_title},
            "first_definition": (
                {"path": definitions[0].path, "line": definitions[0].line, "unit": definitions[0].unit_title}
                if definitions else None
            ),
            "roles": sorted({item.role for item in items}),
            "occurrences": len(items),
            "meaning": registry_entry.get("meaning"),
        }

        if first_declaration is None and not registry_explained:
            result.issues.append(Issue(
                "WARNING", "N001", symbol,
                f"{symbol} is used but no formal declaration or nearby prose explanation was detected.",
                first.path, first.line, first.unit_title,
            ))
        elif (
            first_declaration is not None
            and first.position < first_declaration.position
            and first.unit_id != first_declaration.unit_id
            and not registry_explained
        ):
            result.issues.append(Issue(
                "ERROR", "N002", symbol,
                f"{symbol} is first used in '{first.unit_title}' but first declared/explained in '{first_declaration.unit_title}'.",
                first.path, first.line, first.unit_title,
            ))

        near_definition = explanation_is_near(definitions[0], explanations) if definitions else False
        explained_before_definition = bool(definitions) and any(
            item.position <= definitions[0].position for item in explanations
        )
        if definitions and not (near_definition or explained_before_definition or registry_explained):
            definition = definitions[0]
            result.issues.append(Issue(
                "WARNING", "N003", symbol,
                f"{symbol} is formally introduced without a nearby semantic explanation.",
                definition.path, definition.line, definition.unit_title,
            ))

        roles = {item.role for item in items}
        numeric_definitions = [item for item in definitions if item.role == "value" and item.numeric_definition]
        callable_evidence = [item for item in items if item.role == "callable"]
        if numeric_definitions and callable_evidence and "value" in roles and "callable" in roles:
            numeric = numeric_definitions[0]
            callable_use = callable_evidence[0]
            if numeric.unit_id != callable_use.unit_id:
                result.issues.append(Issue(
                    "ERROR", "N004", symbol,
                    f"{symbol} is callable notation in '{callable_use.unit_title}' but is redeclared as a numeric value in '{numeric.unit_title}'.",
                    numeric.path, numeric.line, numeric.unit_title,
                ))

        allowed_roles = set(registry_entry.get("roles", []))
        if allowed_roles and not roles.issubset(allowed_roles):
            result.issues.append(Issue(
                "ERROR", "N005", symbol,
                f"{symbol} has roles {sorted(roles)}, outside registry roles {sorted(allowed_roles)}.",
                first.path, first.line, first.unit_title,
            ))

        if terms and not registry_explained:
            result.issues.append(Issue(
                "WARNING", "N006", symbol,
                f"{symbol} is not explained at first use with any registry term: {', '.join(terms)}.",
                first.path, first.line, first.unit_title,
            ))

        if definitions and not any(item.position > definitions[0].position and not item.definition for item in items):
            definition = definitions[0]
            result.issues.append(Issue(
                "INFO", "N007", symbol,
                f"{symbol} is declared but not used later in the audited scope.",
                definition.path, definition.line, definition.unit_title,
            ))

    severity_rank = {"ERROR": 0, "WARNING": 1, "INFO": 2}
    result.issues.sort(key=lambda issue: (severity_rank[issue.severity], issue.path, issue.line, issue.symbol, issue.code))
    return result, loader_warnings


def render_text(result: AuditResult, loader_warnings: Sequence[str], include_info: bool) -> str:
    visible = [issue for issue in result.issues if include_info or issue.severity != "INFO"]
    output = [
        f"Notation audit: {result.target}",
        f"Scope: {result.scope} | kind: {result.document_kind} | units: {result.units} | symbols: {len(result.symbols)}",
    ]
    for warning in loader_warnings:
        output.append(f"LOADER WARNING: {warning}")
    if not visible:
        output.append("No notation findings at the selected severity level.")
    else:
        for issue in visible:
            output.append(
                f"{issue.severity} {issue.code} {issue.path}:{issue.line} [{issue.unit}] {issue.message}"
            )
    counts = {severity: sum(issue.severity == severity for issue in result.issues) for severity in ("ERROR", "WARNING", "INFO")}
    output.append(
        f"Summary: {counts['ERROR']} error(s), {counts['WARNING']} warning(s), {counts['INFO']} info item(s)."
    )
    output.append("Heuristic audit only: inspect each finding in source before editing mathematical claims.")
    return "\n".join(output)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="Main .tex file or LaTeX project directory")
    parser.add_argument("--scope", choices=("main", "all"), default="main", help="Stop at \\appendix or audit the whole document")
    parser.add_argument("--registry", type=Path, help="Optional JSON registry for meanings, required terms, and roles")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--include-info", action="store_true", help="Show declared-but-unused informational findings")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when ERROR findings are present")
    args = parser.parse_args(argv)

    target = Path(args.target).expanduser()
    try:
        result, loader_warnings = audit(target, args.scope, args.registry)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if args.json:
        payload = result.to_dict()
        payload["loader_warnings"] = list(loader_warnings)
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(result, loader_warnings, args.include_info))

    return 1 if args.strict and any(issue.severity == "ERROR" for issue in result.issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
