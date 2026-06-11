"""Dependency-free LaTeX reader for discourse graph prototypes."""

from __future__ import annotations

import re

from .heuristics import first_sentence, node_role, normalize_title, strip_latex
from .schema import Node, Profile


HEADING_RE = re.compile(r"\\(?P<kind>section|subsection|subsubsection|paragraph)\*?\{(?P<title>[^{}]*(?:\{[^{}]*\}[^{}]*)*)\}")
BEGIN_ENV_RE = re.compile(
    r"\\begin\{(?P<env>equation\*?|align\*?|gather\*?|multline\*?|figure\*?|table\*?|algorithm\*?|theorem\*?)\}"
)
END_ENV_RE = re.compile(r"\\end\{(?P<env>[^}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:eqref|ref|autoref|cref|Cref)\{([^}]+)\}")
INPUT_RE = re.compile(r"\\input\{([^}]+)\}")
DG_COMMENT_RE = re.compile(r"^%\s*DG:\s*(?P<body>.*)$")


def semantic_comment_role(body: str) -> str:
    role_match = re.search(r"\brole\s*=\s*\"?(?P<role>[A-Za-z_-]+)\"?", body)
    if not role_match:
        return "handoff"
    role = role_match.group("role").lower()
    return {
        "setup": "scene",
        "plant": "question",
        "question": "question",
        "bridge": "mechanism",
        "definition": "definition",
        "notation": "notation",
        "payoff": "payoff",
        "interpretation": "payoff",
        "boundary": "boundary",
        "evidence": "evidence",
        "handoff": "handoff",
    }.get(role, "handoff")


def split_latex_nodes(source: str, section: str, profile: Profile) -> list[Node]:
    lines = source.splitlines()
    nodes: list[Node] = []
    section_path: list[str] = []
    block_path: list[str] = []
    current_heading = ""
    counters = {"h": 0, "p": 0, "eq": 0, "fig": 0, "tab": 0, "alg": 0, "blk": 0}
    paragraph_lines: list[tuple[int, str]] = []

    def make_id(prefix: str) -> str:
        counters[prefix] += 1
        return f"sec{section}.{prefix}{counters[prefix]}"

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if not paragraph_lines:
            return
        text = "\n".join(line for _, line in paragraph_lines).strip()
        start = paragraph_lines[0][0]
        end = paragraph_lines[-1][0]
        paragraph_lines = []
        if not text or not strip_latex(text):
            return
        role = node_role("paragraph_text", text, current_heading, profile)
        nodes.append(
            Node(
                id=make_id("p"),
                kind=role,
                latex_kind="paragraph_text",
                heading=current_heading,
                section_path=list(section_path),
                text=text,
                text_preview=first_sentence(text),
                line_start=start,
                line_end=end,
                labels=LABEL_RE.findall(text),
                refs=REF_RE.findall(text),
                inputs=INPUT_RE.findall(text),
            )
        )

    i = 0
    while i < len(lines):
        line_no = i + 1
        line = lines[i]
        stripped = line.strip()

        dg_comment = DG_COMMENT_RE.match(stripped)
        if dg_comment:
            flush_paragraph()
            body = dg_comment.group("body").strip()
            nodes.append(
                Node(
                    id=make_id("blk"),
                    kind=semantic_comment_role(body),
                    latex_kind="semantic_comment",
                    heading=current_heading,
                    section_path=list(section_path),
                    text=body,
                    text_preview=first_sentence(body) or body[:160],
                    line_start=line_no,
                    line_end=line_no,
                    labels=LABEL_RE.findall(body),
                    refs=REF_RE.findall(body),
                    inputs=INPUT_RE.findall(body),
                )
            )
            i += 1
            continue

        if not stripped or stripped.startswith("%"):
            flush_paragraph()
            i += 1
            continue

        begin = BEGIN_ENV_RE.search(stripped)
        if begin:
            flush_paragraph()
            env = begin.group("env").rstrip("*")
            block = [line]
            start = line_no
            i += 1
            while i < len(lines):
                block.append(lines[i])
                end = END_ENV_RE.search(lines[i])
                if end and env == end.group("env").rstrip("*"):
                    break
                i += 1
            text = "\n".join(block)
            if env in {"equation", "align", "gather", "multline"}:
                prefix = "eq"
            elif env == "figure":
                prefix = "fig"
            elif env == "table":
                prefix = "tab"
            elif env in {"algorithm", "theorem"}:
                prefix = "alg"
            else:
                prefix = "blk"
            nodes.append(
                Node(
                    id=make_id(prefix),
                    kind=node_role(env, text, current_heading, profile),
                    latex_kind=env,
                    heading=current_heading,
                    section_path=list(section_path),
                    text=text,
                    text_preview=first_sentence(text),
                    line_start=start,
                    line_end=i + 1,
                    labels=LABEL_RE.findall(text),
                    refs=REF_RE.findall(text),
                    inputs=INPUT_RE.findall(text),
                )
            )
            i += 1
            continue

        heading = HEADING_RE.search(stripped)
        if heading:
            flush_paragraph()
            kind = heading.group("kind")
            title = normalize_title(heading.group("title"))
            if kind == "section":
                section_path = [title]
                block_path = [title]
            elif kind == "subsection":
                section_path = block_path[:1] + [title]
                block_path = list(section_path)
            elif kind == "subsubsection":
                section_path = block_path[:2] + [title]
                block_path = list(section_path)
            elif kind == "paragraph":
                section_path = block_path + [title]
            current_heading = " / ".join(section_path) if section_path else title
            nodes.append(
                Node(
                    id=make_id("h"),
                    kind=node_role(kind, title, current_heading, profile),
                    latex_kind=kind,
                    heading=current_heading,
                    section_path=list(section_path),
                    text=title,
                    text_preview=title,
                    line_start=line_no,
                    line_end=line_no,
                    labels=LABEL_RE.findall(stripped),
                    refs=REF_RE.findall(stripped),
                    inputs=INPUT_RE.findall(stripped),
                )
            )
            rest = stripped[heading.end() :].strip()
            if rest:
                paragraph_lines.append((line_no, rest))
            i += 1
            continue

        if INPUT_RE.search(stripped) and not paragraph_lines:
            nodes.append(
                Node(
                    id=make_id("fig"),
                    kind="evidence",
                    latex_kind="input",
                    heading=current_heading,
                    section_path=list(section_path),
                    text=stripped,
                    text_preview=first_sentence(stripped),
                    line_start=line_no,
                    line_end=line_no,
                    labels=LABEL_RE.findall(stripped),
                    refs=REF_RE.findall(stripped),
                    inputs=INPUT_RE.findall(stripped),
                )
            )
            i += 1
            continue

        if LABEL_RE.fullmatch(stripped) or stripped in {r"\medskip", r"\noindent"}:
            i += 1
            continue

        paragraph_lines.append((line_no, line))
        i += 1

    flush_paragraph()
    return nodes
