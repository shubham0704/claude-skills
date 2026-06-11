"""Markdown, JSON, and JSONL renderers for discourse graph audits."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .heuristics import lexical_overlap, topic_matches
from .schema import Edge, Node, Profile


def graph_json(nodes: list[Node], edges: list[Edge], source: Path, section: str, profile: Profile) -> dict:
    return {
        "prototype": "discourse_graph_audit",
        "source": str(source),
        "section": section,
        "profile": {
            "name": profile.name,
            "central_question": profile.central_question,
            "audience": profile.audience,
            "domain_terms": profile.domain_terms,
        },
        "nodes": [
            {
                "id": n.id,
                "kind": n.kind,
                "latex_kind": n.latex_kind,
                "heading": n.heading,
                "section_path": n.section_path,
                "line_start": n.line_start,
                "line_end": n.line_end,
                "text_preview": n.text_preview,
                "labels": n.labels,
                "refs": n.refs,
                "inputs": n.inputs,
                "reader_question_answered": n.reader_question_answered,
                "question_planted": n.question_planted,
                "risk": n.risk,
                "risk_score": n.score,
            }
            for n in nodes
        ],
        "edges": [
            {
                "source": e.source,
                "target": e.target,
                "type": e.type,
                "confidence": e.confidence,
                "note": e.note,
            }
            for e in edges
        ],
    }


def md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def outgoing_map(edges: Iterable[Edge]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for e in edges:
        out.setdefault(e.source, []).append(f"{e.type}->{e.target} ({e.confidence:.2f})")
    return out


def render_topic_checks(nodes: list[Node], profile: Profile) -> list[str]:
    lines: list[str] = []
    for check in profile.topic_checks:
        lines.append(f"## {check.name}")
        matches = [n for n in nodes if topic_matches(check, n.heading, n.text) or topic_matches(check, "", n.text_preview)]
        if not matches:
            lines.append(f"No nodes found for terms: {', '.join(check.terms)}.")
            lines.append("")
            continue
        for n in matches:
            prev = nodes[nodes.index(n) - 1] if nodes.index(n) > 0 else None
            nxt = nodes[nodes.index(n) + 1] if nodes.index(n) + 1 < len(nodes) else None
            prev_overlap = lexical_overlap(prev, n) if prev else 0.0
            next_overlap = lexical_overlap(n, nxt) if nxt else 0.0
            verdict = "valid bridge candidate" if "bridge_candidate" in n.risk or next_overlap >= 0.12 else "detour candidate"
            lines.append(
                f"- `{n.id}` lines {n.line_start}-{n.line_end}: {verdict}; "
                f"prev_overlap={prev_overlap:.2f}, next_overlap={next_overlap:.2f}, risk={n.risk}; {n.text_preview}"
            )
        lines.append("")
    return lines


def render_paragraph_tasks(nodes: list[Node], limit: int = 8) -> list[str]:
    candidates = [
        (idx, n)
        for idx, n in enumerate(nodes)
        if n.latex_kind == "paragraph_text" and (n.risk or n.question_planted or n.reader_question_answered)
    ]
    candidates.sort(key=lambda item: (-item[1].score, item[1].line_start, item[1].id))

    lines: list[str] = ["## Paragraph Refinement Task List"]
    if not candidates:
        lines.append("No paragraph-sized refinement tasks were flagged by the current heuristics.")
        lines.append("")
        return lines

    for task_no, (idx, node) in enumerate(candidates[:limit], start=1):
        prev = nodes[idx - 1] if idx > 0 else None
        nxt = nodes[idx + 1] if idx + 1 < len(nodes) else None
        local_refs = sorted(set(node.refs + (prev.refs if prev else []) + (nxt.refs if nxt else [])))
        risk = ", ".join(node.risk) if node.risk else "none"
        goal = "Resolve the flagged flow/readability issue while preserving the paragraph's claim."
        if node.question_planted:
            goal = "Make the planted reader question explicit enough and ensure the payoff is nearby."
        if node.reader_question_answered:
            goal = "Make the paragraph's answer/payoff clear without adding claim drift."

        lines.append(f"### Task P{task_no}: `{node.id}` lines {node.line_start}-{node.line_end}")
        lines.append(f"- Goal: {goal}")
        lines.append(f"- Paragraph job: `{node.kind}` under `{node.heading}`.")
        lines.append(f"- Reader state before: {md_escape(prev.text_preview if prev else 'Start of section.')}")
        lines.append(f"- Current paragraph: {md_escape(node.text_preview)}")
        lines.append(f"- Next local payoff/handoff: {md_escape(nxt.text_preview if nxt else 'End of section.')}")
        lines.append(f"- Risks to inspect: {md_escape(risk)}")
        if local_refs:
            lines.append(f"- Nearby refs to preserve: {', '.join(f'`{ref}`' for ref in local_refs[:8])}")
        lines.append("- Deliverable: proposed rewrite plus one-sentence rationale; preserve labels, citations, and claim boundaries.")
        lines.append("")
    return lines


def render_markdown(nodes: list[Node], edges: list[Edge], source: Path, section: str, profile: Profile) -> str:
    out_edges = outgoing_map(edges)
    lines: list[str] = []
    lines.append("# Discourse Graph Audit")
    lines.append("")
    lines.append(f"- Source: `{source}`")
    lines.append(f"- Section id prefix: `sec{section}`")
    lines.append(f"- Profile: `{profile.name}`")
    lines.append(f"- Central reader question: {profile.central_question}")
    lines.append(f"- Nodes: {len(nodes)}")
    lines.append(f"- Edges: {len(edges)}")
    lines.append("- Prototype status: dependency-free heuristic parser; inspect manually before trusting labels.")
    lines.append("")

    if profile.domain_terms:
        lines.append("## Profile Domain Terms")
        for term, meaning in profile.domain_terms.items():
            lines.append(f"- `{term}`: {meaning}")
        lines.append("")

    lines.append("## Section-Level Outline")
    for n in nodes:
        if n.latex_kind in {"section", "subsection", "subsubsection", "paragraph"}:
            depth = {"section": 0, "subsection": 1, "subsubsection": 2, "paragraph": 3}.get(n.latex_kind, 0)
            indent = "  " * depth
            lines.append(f"{indent}- `{n.id}` {n.latex_kind}: {n.text_preview}")
    lines.append("")

    lines.append("## Top Manual Inspection Targets")
    risky = sorted((n for n in nodes if n.risk), key=lambda n: (-n.score, n.line_start, n.id))[:5]
    if not risky:
        lines.append("No high-risk nodes were flagged by the current heuristics.")
    for n in risky:
        lines.append(
            f"- `{n.id}` lines {n.line_start}-{n.line_end}, `{n.kind}`, risk={n.risk}: {n.text_preview}"
        )
    lines.append("")

    lines.extend(render_paragraph_tasks(nodes))

    if profile.topic_checks:
        lines.extend(render_topic_checks(nodes, profile))

    lines.append("## Paragraph / Block Node Table")
    lines.append(
        "| id | lines | kind | latex | parent heading | preview | answered | planted | outgoing | risk |"
    )
    lines.append("|---|---:|---|---|---|---|---|---|---|---|")
    for n in nodes:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{n.id}`",
                    f"{n.line_start}-{n.line_end}",
                    f"`{n.kind}`",
                    f"`{n.latex_kind}`",
                    md_escape(n.heading),
                    md_escape(n.text_preview),
                    md_escape(n.reader_question_answered),
                    md_escape(n.question_planted),
                    md_escape("; ".join(out_edges.get(n.id, []))[:220]),
                    md_escape(", ".join(n.risk)),
                ]
            )
            + " |"
        )
    lines.append("")

    lines.append("## Risk Label Legend")
    lines.append("- `abrupt`: low lexical continuity plus a dependent opening phrase.")
    lines.append("- `detour`: appendix/theory/topic-heavy branch that may interrupt the main payoff.")
    lines.append("- `unpaid_question`: a planted question/deferred promise without a nearby payoff by heuristic scan.")
    lines.append("- `premature_notation`: dense formal notation with many terms not seen earlier.")
    lines.append("- `weak_parent_link`: paragraph vocabulary has little overlap with the active heading.")
    lines.append("- `bridge_candidate`: local evidence that a suspected detour hands off to the next block.")
    lines.append("- `semantic_comment`: source-only `% DG:` breadcrumb parsed as a graph node; it does not render in PDF.")
    lines.append("- `context_debt`: a named setting/experiment/diagnostic appears before enough local setup.")
    lines.append("- `appendix_claim_leak`: appendix evidence is used as if it were part of the current method story.")
    lines.append("- `symbol_alias_confusion`: a similar symbol with a new subscript appears without explaining the relationship.")
    lines.append("- `coarse_algorithm_reference`: prose invokes an algorithmic action without stage, line, or equation specificity.")
    lines.append("- `missing_formal_setup`: equation-like block appears before prose creates the need for it.")
    lines.append("- `missing_formal_payoff`: equation-like block is not followed by a nearby interpretation.")
    lines.append("- `symbol_scope_debt`: formal block introduces several new symbols without nearby scope/type/dependency prose.")
    lines.append("- `role_mismatch`: prose promises intuition or readability but hands off to dense notation without enough setup.")
    lines.append("- `equation_overload`: formal block introduces many symbolic objects at once.")
    lines.append("- `dangling_reference`: paragraph starts from this/these/such object without a clear local antecedent.")
    return "\n".join(lines) + "\n"


def write_jsonl(nodes: list[Node], path: Path) -> None:
    records = []
    for i, n in enumerate(nodes):
        records.append(
            {
                "id": n.id,
                "parent_heading": n.heading,
                "previous_preview": nodes[i - 1].text_preview if i > 0 else "",
                "current_text": n.text,
                "next_preview": nodes[i + 1].text_preview if i + 1 < len(nodes) else "",
                "nearby_labels": sorted({label for m in nodes[max(0, i - 2) : i + 3] for label in m.labels}),
                "nearby_refs": sorted({ref for m in nodes[max(0, i - 2) : i + 3] for ref in m.refs}),
                "prompt": (
                    "Assign node_type, live_reader_question, planted_question, strongest incoming edge, "
                    "strongest outgoing edge, and risk_label for this LaTeX discourse node."
                ),
            }
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")
