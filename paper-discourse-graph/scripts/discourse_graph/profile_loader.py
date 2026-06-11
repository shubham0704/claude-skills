"""Load project profiles for discourse-graph audits.

Profiles are JSON on purpose: this remains dependency-free and can run inside
paper repos without installing PyYAML.
"""

from __future__ import annotations

import json
from pathlib import Path

from .schema import Profile, TopicCheck


def default_profile() -> Profile:
    return Profile(
        name="default_scientific_paper",
        central_question="What should the reader understand, believe, and remember after this section?",
        audience={
            "primary": "technical paper readers",
            "needs": [
                "visible grounding before dense notation",
                "nearby payoff after a planted question",
                "clear handoffs between motivation, mechanism, evidence, and limits",
            ],
        },
        role_keywords={},
        domain_terms={},
        topic_checks=[],
        risk_rules={},
    )


def profile_from_dict(data: dict) -> Profile:
    checks = [
        TopicCheck(
            name=item.get("name", "Topic Check"),
            scope_heading_terms=list(item.get("scope_heading_terms", [])),
            terms=list(item.get("terms", [])),
            bridge_terms=list(item.get("bridge_terms", [])),
            detour_terms=list(item.get("detour_terms", [])),
            answered_question=item.get("answered_question", ""),
        )
        for item in data.get("topic_checks", [])
    ]
    base = default_profile()
    return Profile(
        name=data.get("name", base.name),
        central_question=data.get("central_question", base.central_question),
        audience=data.get("audience", base.audience),
        domain_terms=data.get("domain_terms", base.domain_terms),
        role_keywords=data.get("role_keywords", base.role_keywords),
        topic_checks=checks,
        risk_rules=data.get("risk_rules", base.risk_rules),
    )


def load_profile(path: Path | None) -> Profile:
    if path is None:
        return default_profile()
    data = json.loads(path.read_text(encoding="utf-8"))
    return profile_from_dict(data)
