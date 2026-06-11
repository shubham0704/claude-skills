"""Command-line entry point for discourse-graph audits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .heuristics import annotate_nodes, build_edges
from .latex_reader import split_latex_nodes
from .profile_loader import load_profile
from .render import graph_json, render_markdown, write_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(description="PROTOTYPE LaTeX discourse graph audit.")
    parser.add_argument("source", type=Path, help="LaTeX section file to audit")
    parser.add_argument("--section", default="X", help="Stable id section prefix, e.g. 3")
    parser.add_argument("--profile", type=Path, help="Optional project profile JSON")
    parser.add_argument("--out", type=Path, required=True, help="Markdown report path")
    parser.add_argument("--json-out", type=Path, help="JSON graph path")
    parser.add_argument("--llm-jsonl", type=Path, help="Optional prompt-ready JSONL chunks; no API calls")
    args = parser.parse_args()

    profile = load_profile(args.profile)
    source_text = args.source.read_text(encoding="utf-8")
    nodes = split_latex_nodes(source_text, args.section, profile)
    annotate_nodes(nodes, profile)
    edges = build_edges(nodes)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_markdown(nodes, edges, args.source, args.section, profile), encoding="utf-8")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(graph_json(nodes, edges, args.source, args.section, profile), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if args.llm_jsonl:
        write_jsonl(nodes, args.llm_jsonl)

    print(f"wrote {args.out}")
    if args.json_out:
        print(f"wrote {args.json_out}")
    if args.llm_jsonl:
        print(f"wrote {args.llm_jsonl}")
    print(f"profile={profile.name} nodes={len(nodes)} edges={len(edges)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
