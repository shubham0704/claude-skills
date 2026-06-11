# Paper Discourse Graph

`paper-discourse-graph` audits LaTeX papers as reader-state graphs.
It helps answer questions like:

- Where does the reader lose the thread?
- Which paragraphs plant questions without paying them off?
- Which equations or figures appear before the story makes them
  inevitable?
- Which blocks are story, justification, evidence, implementation, or
  boundary material?

It is useful before line editing a section for flow, readability,
compression, rhythm, or story coherence.

## Agent Invocation

Ask directly:

```text
Use paper-discourse-graph to audit section 3 for abrupt jumps,
detours, and whether each paragraph plants or pays off a reader
question. Do not edit yet.
```

The agent should read `SKILL.md`, choose a profile, run the CLI when
useful, and return ranked findings with file/line references.

## CLI Usage

From this skill directory:

```bash
python scripts/discourse_graph_audit.py path/to/section.tex \
  --section 3 \
  --profile references/profiles/default_scientific_paper.json \
  --out path/to/discourse_graph_sec3.md \
  --json-out path/to/discourse_graph_sec3.json
```

For C-PHAST:

```bash
python scripts/discourse_graph_audit.py paper/sec/3_method_arxiv.tex \
  --section 3 \
  --profile references/profiles/cphast.json \
  --out paper/docs/plans/discourse_graph_sec3.md \
  --json-out paper/docs/plans/discourse_graph_sec3.json
```

Optional prompt-ready node chunks:

```bash
python scripts/discourse_graph_audit.py path/to/section.tex \
  --section 3 \
  --out path/to/discourse_graph_sec3.md \
  --llm-jsonl path/to/discourse_nodes_sec3.jsonl
```

## Profiles

Profiles are JSON so the tool stays dependency-free. Use
`references/profiles/default_scientific_paper.json` for general
papers and copy it into a project when you need local vocabulary.

The bundled `cphast.json` profile includes C-PHAST terms such as
typed factors, charts, ports, PHASTCore, and action cards.

## Output

The Markdown report includes:

- section outline
- top manual inspection targets
- optional topic checks
- node table with planted/answered reader questions
- risk labels such as `abrupt`, `detour`, `unpaid_question`, and
  `premature_notation`

The JSON report preserves the same graph for downstream tooling.

## Limits

This is a heuristic audit, not a parser proof or a writing oracle.
Use the output to focus human or agent review on likely story breaks.
