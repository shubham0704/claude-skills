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
SYMBOL_RE = re.compile(r"\\(?P<base>[A-Za-z]+)(?:_\{(?P<braced>[^{}]*(?:\{[^{}]*\}[^{}]*)*)\}|_(?P<plain>[A-Za-z0-9]+))?")
APPENDIX_EVIDENCE_RE = re.compile(
    r"\bappendix\b.*\b(uses|reports|shows|evaluates|demonstrates|validates|confirms|proves)\b",
    re.IGNORECASE,
)
ALGORITHM_ACTION_RE = re.compile(
    r"\balgorithm\b.*\b(instantiates?|parses?|calls?|reads?|applies?|wraps?|starts?|executes?|assembles?)\b",
    re.IGNORECASE,
)
ALGORITHM_SPECIFICITY_RE = re.compile(r"\b(lines?|stages?|steps?|eq\.|equation|line\s+\d+)\b", re.IGNORECASE)
SETTING_CONTEXT_RE = re.compile(r"\b(experiment|study|setting|benchmark|diagnostic|sweep|specialization)\b", re.IGNORECASE)
SYMBOL_RELATION_RE = re.compile(
    r"\b(not|rather than|while|whereas|distinct|same|denotes|appears in|used only|only by|proxy|metric|shorthand)\b",
    re.IGNORECASE,
)
FORMAL_BLOCK_KINDS = {"equation", "align", "gather", "multline"}
FORMAL_SETUP_RE = re.compile(
    r"\b(define|denote|write|let|model|use|given|resulting|following|becomes|yields|"
    r"transition|loss|objective|score|readout|constraint|factor|operator|map|update|"
    r"identity|evaluate|evaluates|compute|computes|match|matches|penalty|term|"
    r"parameteri[sz]e|parameteri[sz]ed|we obtain|we have)\b",
    re.IGNORECASE,
)
FORMAL_PAYOFF_RE = re.compile(
    r"\b(where|here|this|these|therefore|thus|means|corresponds|in words|intuitively|"
    r"operationally|the key|we use|reads|captures|ensures|guarantees|prevents|allows|"
    r"gives|implies|reduces|rolls|rollout|evaluates|computes|matches|supervised|"
    r"so|because)\b",
    re.IGNORECASE,
)
SCOPE_EXPLANATION_RE = re.compile(
    r"\b(where|with|denotes|defined|lives|belongs|maps|from|to|over|for each|"
    r"local|global|target|fixed|optional|zero when|absent|dimension|scope|type)\b",
    re.IGNORECASE,
)
INTUITION_PROMISE_RE = re.compile(
    r"\b(intuition|intuitive|conceptually|in words|simple|visible|readability|picture)\b",
    re.IGNORECASE,
)
DANGLING_REFERENCE_RE = re.compile(
    r"^\s*(this|these|that|such)\s+"
    r"(?P<noun>factor|map|setting|spectrum|operator|diagnostic|channel|mode|interface|"
    r"contract|term|quantity|score|rule|transition|wrapper|pipeline|vector|matrix|"
    r"table|figure|claim|object)s?\b",
    re.IGNORECASE,
)
LATEX_SYMBOL_IGNORE = {
    "begin",
    "end",
    "label",
    "ref",
    "eqref",
    "autoref",
    "cref",
    "Cref",
    "cite",
    "citet",
    "citep",
    "frac",
    "tfrac",
    "dfrac",
    "left",
    "right",
    "big",
    "Big",
    "bigl",
    "bigr",
    "Bigl",
    "Bigr",
    "mathrm",
    "mathbf",
    "mathcal",
    "mathbb",
    "text",
    "operatorname",
    "top",
    "T",
    "qquad",
    "quad",
    "ldots",
    "cdots",
    "times",
    "le",
    "ge",
    "leq",
    "geq",
    "in",
    "to",
    "circ",
    "colon",
}


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


def configured_values(profile: Profile, key: str) -> tuple[str, ...]:
    values = profile.risk_rules.get(key, []) if isinstance(profile.risk_rules, dict) else []
    return tuple(str(v) for v in values)


def configured_terms(profile: Profile, key: str) -> tuple[str, ...]:
    return tuple(v.lower() for v in configured_values(profile, key))


def configured_int(profile: Profile, key: str, default: int) -> int:
    value = profile.risk_rules.get(key, default) if isinstance(profile.risk_rules, dict) else default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def setting_terms(profile: Profile) -> tuple[str, ...]:
    return configured_terms(profile, "setting_terms")


def confusable_symbol_bases(profile: Profile) -> set[str]:
    return set(configured_values(profile, "confusable_symbol_bases"))


def node_setting_terms(node: Node, profile: Profile) -> set[str]:
    haystack = f"{node.heading} {strip_latex(node.text)}".lower()
    return {term for term in setting_terms(profile) if term and term in haystack}


def normalize_symbol_subscript(raw: str) -> str:
    clean = re.sub(r"\\[A-Za-z]+", "", raw)
    clean = re.sub(r"[^A-Za-z0-9]+", "", clean)
    return clean


def symbol_signatures(text: str, profile: Profile) -> list[tuple[str, str]]:
    tracked_bases = confusable_symbol_bases(profile)
    if not tracked_bases:
        return []

    signatures: list[tuple[str, str]] = []
    for match in SYMBOL_RE.finditer(text):
        base = match.group("base")
        raw_sub = match.group("braced") or match.group("plain") or ""
        if not raw_sub:
            continue
        if base not in tracked_bases:
            continue
        sub = normalize_symbol_subscript(raw_sub)
        if sub:
            signatures.append((base, sub))
    return signatures


def symbol_relationship_explained(text: str) -> bool:
    return bool(SYMBOL_RELATION_RE.search(strip_latex(text)))


def is_formal_block(node: Node) -> bool:
    return node.latex_kind in FORMAL_BLOCK_KINDS


def has_formal_setup(prev: Node | None, node: Node) -> bool:
    if prev is None:
        return False
    if is_formal_block(prev):
        return True
    if prev.latex_kind != "paragraph_text":
        return False
    clean = strip_latex(prev.text)
    return bool(FORMAL_SETUP_RE.search(clean)) or clean.rstrip().endswith(":") or lexical_overlap(prev, node) >= 0.04


def has_formal_payoff(node: Node, nxt: Node | None) -> bool:
    if nxt is None:
        return False
    if is_formal_block(nxt):
        return True
    if nxt.latex_kind != "paragraph_text":
        return False
    clean = strip_latex(nxt.text)
    return bool(FORMAL_PAYOFF_RE.search(clean)) or lexical_overlap(node, nxt) >= 0.04


def math_source_without_latex_commands(text: str) -> str:
    text = re.sub(r"\\(?:begin|end|label|ref|eqref|autoref|cref|Cref)\{[^}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z]+", " ", text)
    text = re.sub(r"[^A-Za-z0-9_]+", " ", text)
    return text


def formal_symbol_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for match in SYMBOL_RE.finditer(text):
        base = match.group("base")
        if base in LATEX_SYMBOL_IGNORE:
            continue
        raw_sub = match.group("braced") or match.group("plain") or ""
        sub = normalize_symbol_subscript(raw_sub)
        tokens.add(f"{base}_{sub}" if sub else base)

    bare_source = math_source_without_latex_commands(text)
    for raw in re.findall(r"\b[A-Za-z][A-Za-z0-9_]*\b", bare_source):
        if raw in LATEX_SYMBOL_IGNORE or raw.startswith(("eq", "fig", "tab", "alg", "sec")):
            continue
        if len(raw) == 1 or "_" in raw or raw[:1].isupper():
            tokens.add(raw)
    return tokens


def has_symbol_scope_explanation(prev: Node | None, nxt: Node | None) -> bool:
    surrounding = " ".join(strip_latex(n.text) for n in (prev, nxt) if n and n.latex_kind == "paragraph_text")
    return bool(SCOPE_EXPLANATION_RE.search(surrounding))


def has_clear_antecedent(nodes: list[Node], idx: int, noun: str) -> bool:
    window = " ".join(strip_latex(n.text).lower() for n in nodes[max(0, idx - 3) : idx])
    return noun.lower() in window


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
    seen_settings: set[str] = set()
    symbol_history: dict[str, set[str]] = {}
    seen_formal_symbols: set[str] = set()
    overload_threshold = configured_int(profile, "equation_overload_symbol_threshold", 16)
    scope_threshold = configured_int(profile, "symbol_scope_new_threshold", 7)
    open_questions: list[tuple[int, Node]] = []
    for idx, node in enumerate(nodes):
        nxt = nodes[idx + 1] if idx + 1 < len(nodes) else None
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

            dangling = DANGLING_REFERENCE_RE.search(strip_latex(node.text))
            if dangling and overlap < 0.08 and not has_clear_antecedent(nodes, idx, dangling.group("noun")):
                add_risk(node, "dangling_reference")

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
        if APPENDIX_EVIDENCE_RE.search(low):
            add_risk(node, "appendix_claim_leak")
        if ALGORITHM_ACTION_RE.search(low) and not ALGORITHM_SPECIFICITY_RE.search(low):
            add_risk(node, "coarse_algorithm_reference")

        current_settings = node_setting_terms(node, profile)
        if current_settings:
            first_mentions = current_settings - seen_settings
            if first_mentions and SETTING_CONTEXT_RE.search(low):
                add_risk(node, "context_debt")
            seen_settings |= current_settings

        current_symbols = symbol_signatures(node.text, profile)
        for base, sub in current_symbols:
            prior_subs = symbol_history.setdefault(base, set())
            relationship_context = " ".join(
                n.text for n in (prev, node, nxt) if n and n.latex_kind in {"paragraph_text", *FORMAL_BLOCK_KINDS}
            )
            if prior_subs and sub not in prior_subs and not symbol_relationship_explained(relationship_context):
                add_risk(node, "symbol_alias_confusion")
            prior_subs.add(sub)

        if is_formal_block(node):
            formal_symbols = formal_symbol_tokens(node.text)
            new_symbols = formal_symbols - seen_formal_symbols
            if not has_formal_setup(prev, node):
                add_risk(node, "missing_formal_setup")
            if not has_formal_payoff(node, nxt):
                add_risk(node, "missing_formal_payoff")
            if len(formal_symbols) >= overload_threshold:
                add_risk(node, "equation_overload")
            if len(new_symbols) >= scope_threshold and not has_symbol_scope_explanation(prev, nxt):
                add_risk(node, "symbol_scope_debt")
            if (
                prev
                and prev.latex_kind == "paragraph_text"
                and INTUITION_PROMISE_RE.search(strip_latex(prev.text))
                and not FORMAL_SETUP_RE.search(strip_latex(prev.text))
                and len(formal_symbols) >= max(5, overload_threshold // 2)
            ):
                add_risk(node, "role_mismatch")
            seen_formal_symbols |= formal_symbols

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
        "context_debt": 4,
        "appendix_claim_leak": 4,
        "symbol_alias_confusion": 4,
        "coarse_algorithm_reference": 3,
        "missing_formal_setup": 4,
        "missing_formal_payoff": 4,
        "symbol_scope_debt": 4,
        "role_mismatch": 3,
        "equation_overload": 3,
        "dangling_reference": 3,
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
        if is_formal_block(cur) and prev.latex_kind == "paragraph_text":
            edge_type = "sets_up_formal_block"
            confidence = 0.68
        elif is_formal_block(prev) and cur.latex_kind == "paragraph_text":
            edge_type = "interprets_formal_block"
            confidence = 0.68
        elif is_formal_block(prev) and is_formal_block(cur):
            edge_type = "continues_formal_block"
            confidence = 0.6
        elif cur.kind in {"definition", "notation"} and prev.kind in {"scene", "claim", "question", "mechanism"}:
            edge_type = "formalizes"
            confidence = 0.65
        elif cur.kind == "justification":
            edge_type = "justifies"
            confidence = 0.62
        elif cur.kind == "evidence":
            edge_type = "supports_with_evidence"
            confidence = 0.6
        if (
            edge_type not in {"interprets_formal_block", "sets_up_formal_block", "continues_formal_block"}
            and lexical_overlap(prev, cur) < 0.05
            and cur.latex_kind == "paragraph_text"
        ):
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
