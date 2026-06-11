"""Profile-aware heuristics for discourse graph construction.

These rules are intentionally lightweight. They provide inspection prompts for
an author or agent, not final judgments about a paper.
"""

from __future__ import annotations

import re

from .schema import Edge, Node, Profile, TopicCheck


CITE_RE = re.compile(r"\\cite\w*\{[^}]+\}")
COMMAND_RE = re.compile(r"\\[a-zA-Z]+(?:\[[^\]]*\])?(?:\{[^{}]*\})?")
INLINE_MATH_RE = re.compile(r"\$([^$]+)\$")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "for",
    "from",
    "has",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "our",
    "that",
    "the",
    "their",
    "then",
    "these",
    "this",
    "to",
    "we",
    "when",
    "where",
    "while",
    "with",
}


DEFAULT_ROLE_KEYWORDS = {
    "scene": ("example", "running", "scene", "candidate", "future"),
    "question": ("question", "whether", "why", "how", "what"),
    "claim": ("we show", "we argue", "key property", "distinguishes", "guarantees"),
    "mechanism": ("pipeline", "operator", "layer", "update", "applies", "maps", "instantiates"),
    "definition": ("define", "denote", "let ", "write ", "is denoted", "we use"),
    "notation": ("notation", "tuple", "mathcal", "in\\r", "where $", "$"),
    "justification": ("because", "therefore", "consequently", "the key point", "reason", "supports"),
    "evidence": ("figure", "table", "algorithm", "theorem", "appendix", "experiment", "metric"),
    "boundary": ("assumption", "scope", "limitation", "rather than", "not ", "optional", "when available"),
    "payoff": ("this yields", "thus", "therefore", "answer", "closes", "so "),
    "handoff": ("next", "below", "later", "returned", "deferred", "we now", "finally"),
}


def merged_role_keywords(profile: Profile) -> dict[str, tuple[str, ...]]:
    merged = {role: list(keys) for role, keys in DEFAULT_ROLE_KEYWORDS.items()}
    for role, keys in profile.role_keywords.items():
        merged.setdefault(role, []).extend(keys)
    return {role: tuple(keys) for role, keys in merged.items()}


def strip_latex(text: str) -> str:
    text = CITE_RE.sub("[citation]", text)
    text = re.sub(r"~", " ", text)
    text = re.sub(r"\\(?:eqref|ref|autoref|cref|Cref)\{([^}]+)\}", r"ref:\1", text)
    text = re.sub(r"\\label\{[^}]+\}", "", text)
    text = re.sub(r"\\input\{([^}]+)\}", r"input:\1", text)
    text = re.sub(r"\\emph\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textbf\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textsc\{([^}]*)\}", r"\1", text)
    text = COMMAND_RE.sub(lambda m: m.group(0).replace("\\", "").replace("{", " ").replace("}", " "), text)
    text = re.sub(r"[{}]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def first_sentence(text: str, limit: int = 160) -> str:
    clean = strip_latex(text)
    if not clean:
        return ""
    match = re.search(r"(?<=[.!?])\s+", clean)
    sent = clean[: match.start()] if match else clean
    return sent[:limit].rstrip() + ("..." if len(sent) > limit else "")


def words(text: str) -> set[str]:
    return {w.lower() for w in WORD_RE.findall(strip_latex(text)) if len(w) > 2 and w.lower() not in STOPWORDS}


def math_density(text: str) -> int:
    return text.count("$") + text.count("\\") + len(INLINE_MATH_RE.findall(text))


def normalize_title(title: str) -> str:
    return strip_latex(title).strip()


def node_role(latex_kind: str, text: str, heading: str, profile: Profile) -> str:
    if latex_kind in {"equation", "align", "gather", "multline"}:
        return "definition" if any(k in text for k in ("\\label{eq:", ":=")) else "evidence"
    if latex_kind.startswith("figure") or "\\input" in text:
        return "evidence"
    if latex_kind.startswith("table"):
        return "evidence"
    if latex_kind.startswith("algorithm"):
        return "mechanism"
    if latex_kind in {"section", "subsection", "subsubsection", "paragraph"}:
        return "handoff" if latex_kind == "paragraph" else "claim"

    low = strip_latex(text).lower()
    if math_density(text) > 14 and len(words(text)) < 45:
        return "notation"

    scores: dict[str, int] = {}
    for role, keys in merged_role_keywords(profile).items():
        scores[role] = sum(1 for key in keys if key in low)

    for check in profile.topic_checks:
        if topic_matches(check, heading, text) and ("because" in low or "reason" in low or "supports" in low):
            scores["justification"] = scores.get("justification", 0) + 2

    if "?" in text:
        scores["question"] = scores.get("question", 0) + 3
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "claim"


def topic_matches(check: TopicCheck, heading: str, text: str) -> bool:
    heading_low = heading.lower()
    haystack = f"{heading} {strip_latex(text)}".lower()
    if check.scope_heading_terms:
        if not any(term.lower() in heading_low for term in check.scope_heading_terms):
            return False
        return not check.terms or any(term.lower() in haystack for term in check.terms)
    return any(term.lower() in haystack for term in check.terms)


def topic_has_term(check: TopicCheck, node: Node, terms: list[str]) -> bool:
    haystack = f"{node.heading} {strip_latex(node.text)} {node.text_preview}".lower()
    return any(term.lower() in haystack for term in terms)


def question_planted(node: Node) -> str:
    low = strip_latex(node.text).lower()
    heading = node.heading.split(" / ")[-1] if node.heading else "this block"
    if "?" in node.text:
        return first_sentence(node.text)
    if "we now" in low or "below" in low or "next" in low:
        return f"What does the upcoming {heading} block establish?"
    if "deferred" in low or "later" in low or "returned" in low:
        return f"Where is the deferred {heading} detail paid off?"
    if "question" in low or "whether" in low:
        return f"Does {heading} resolve the stated reader question?"
    if node.kind in {"definition", "notation"} and math_density(node.text) > 10:
        return "How will this notation be used?"
    return ""


def question_answered(node: Node, profile: Profile) -> str:
    low = strip_latex(node.text).lower()
    if node.kind == "payoff":
        return "What was the payoff of the preceding setup?"
    if "because" in low or "consequently" in low or "therefore" in low:
        return "Why is the preceding construction valid?"
    if "key point" in low:
        return "What should the reader retain from this construction?"
    if node.kind == "definition":
        return "What object or contract is being defined?"
    if node.kind == "mechanism":
        return "How does the method execute the stated contract?"
    if node.kind == "evidence":
        return "What visual, algorithmic, or tabular evidence supports the text?"
    for check in profile.topic_checks:
        if check.answered_question and topic_matches(check, node.heading, ""):
            return check.answered_question
    return ""


def parent_overlap(node: Node) -> float:
    title = node.heading.split(" / ")[-1] if node.heading else ""
    title_words = words(title)
    if not title_words:
        return 1.0
    body_words = words(node.text)
    return len(title_words & body_words) / max(1, len(title_words))


def lexical_overlap(a: Node, b: Node) -> float:
    aw = words(a.text)
    bw = words(b.text)
    if not aw or not bw:
        return 0.0
    return len(aw & bw) / max(1, min(len(aw), len(bw)))


def add_risk(node: Node, label: str) -> None:
    if label not in node.risk:
        node.risk.append(label)


def annotate_nodes(nodes: list[Node], profile: Profile) -> None:
    prior_words: set[str] = set()
    open_questions: list[tuple[int, Node]] = []
    for idx, node in enumerate(nodes):
        node.question_planted = question_planted(node)
        node.reader_question_answered = question_answered(node, profile)
        if node.question_planted:
            open_questions.append((idx, node))

        if node.kind in {"notation", "definition"} and math_density(node.text) > 16:
            new_terms = words(node.text) - prior_words
            if len(new_terms) > 18:
                add_risk(node, "premature_notation")

        if node.latex_kind in {"paragraph_text", "paragraph"} and parent_overlap(node) < 0.2:
            if len(words(node.text)) > 35:
                add_risk(node, "weak_parent_link")

        prev = nodes[idx - 1] if idx > 0 else None
        if prev and node.latex_kind == "paragraph_text":
            overlap = lexical_overlap(prev, node)
            starts_abrupt = strip_latex(node.text).lower().startswith(
                ("this ", "these ", "it ", "they ", "such ", "the same ", "consequently")
            )
            follows_block_without_bridge = prev.latex_kind in {"input", "figure", "table", "algorithm", "theorem"}
            if overlap < 0.08 and (starts_abrupt or follows_block_without_bridge):
                add_risk(node, "abrupt")

        for check in profile.topic_checks:
            if topic_matches(check, node.heading, node.text):
                if (
                    node.kind in {"justification", "definition", "notation"}
                    or topic_has_term(check, node, check.detour_terms)
                ):
                    add_risk(node, "detour")
                    add_risk(node, "justification_heavy")
                if topic_has_term(check, node, check.bridge_terms):
                    add_risk(node, "bridge_candidate")

        low = strip_latex(node.text).lower()
        if "appendix" in low and "main text" not in low and node.kind != "handoff":
            add_risk(node, "detour")

        prior_words |= words(node.text)

    answer_indices = [i for i, n in enumerate(nodes) if n.reader_question_answered or n.kind in {"payoff", "justification"}]
    for q_idx, q_node in open_questions:
        paid_nearby = any(q_idx < a_idx <= q_idx + 4 for a_idx in answer_indices)
        if not paid_nearby:
            add_risk(q_node, "unpaid_question")

    for node in nodes:
        node.score = risk_score(node)


def risk_score(node: Node) -> int:
    weights = {
        "abrupt": 4,
        "detour": 3,
        "unpaid_question": 5,
        "premature_notation": 4,
        "weak_parent_link": 3,
        "justification_heavy": 2,
        "bridge_candidate": -1,
        "unconnected_evidence": 3,
    }
    return sum(weights.get(r, 1) for r in node.risk)


def build_edges(nodes: list[Node]) -> list[Edge]:
    edges: list[Edge] = []
    label_to_node: dict[str, str] = {}
    for node in nodes:
        for label in node.labels:
            label_to_node[label] = node.id

    for prev, cur in zip(nodes, nodes[1:]):
        edge_type = "hands_off_to"
        confidence = 0.55
        if cur.kind in {"definition", "notation"} and prev.kind in {"scene", "claim", "question", "mechanism"}:
            edge_type = "formalizes"
            confidence = 0.65
        elif cur.kind == "justification":
            edge_type = "justifies"
            confidence = 0.62
        elif cur.kind == "evidence":
            edge_type = "supports_with_evidence"
            confidence = 0.6
        if lexical_overlap(prev, cur) < 0.05 and cur.latex_kind == "paragraph_text":
            edge_type = "interrupts"
            confidence = 0.45
        edges.append(Edge(prev.id, cur.id, edge_type, confidence))

    for node in nodes:
        for ref in node.refs:
            target = label_to_node.get(ref, f"ref:{ref}")
            edge_type = "supports_with_evidence" if ref.startswith(("fig:", "tab:", "alg:")) else "recalls"
            edges.append(Edge(node.id, target, edge_type, 0.7, note=f"latex ref {ref}"))

    for node in nodes:
        if node.latex_kind in {"figure", "table", "algorithm", "input"} and not any(e.target == node.id for e in edges):
            add_risk(node, "unconnected_evidence")
            node.score = risk_score(node)

    return edges
