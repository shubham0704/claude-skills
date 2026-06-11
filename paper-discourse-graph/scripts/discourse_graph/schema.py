"""Shared data structures for the discourse-graph audit prototype."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TopicCheck:
    """Profile-defined special inspection pass."""

    name: str
    scope_heading_terms: list[str] = field(default_factory=list)
    terms: list[str] = field(default_factory=list)
    bridge_terms: list[str] = field(default_factory=list)
    detour_terms: list[str] = field(default_factory=list)
    answered_question: str = ""


@dataclass
class Profile:
    """Project-specific discourse preferences kept outside the engine."""

    name: str = "default"
    central_question: str = ""
    audience: dict = field(default_factory=dict)
    domain_terms: dict[str, str] = field(default_factory=dict)
    role_keywords: dict[str, list[str]] = field(default_factory=dict)
    topic_checks: list[TopicCheck] = field(default_factory=list)
    risk_rules: dict = field(default_factory=dict)


@dataclass
class Node:
    id: str
    kind: str
    latex_kind: str
    heading: str
    section_path: list[str]
    text: str
    text_preview: str
    line_start: int
    line_end: int
    labels: list[str] = field(default_factory=list)
    refs: list[str] = field(default_factory=list)
    inputs: list[str] = field(default_factory=list)
    reader_question_answered: str = ""
    question_planted: str = ""
    risk: list[str] = field(default_factory=list)
    score: int = 0


@dataclass
class Edge:
    source: str
    target: str
    type: str
    confidence: float
    note: str = ""
