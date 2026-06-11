---
name: paper-discourse-graph
description: "Audit LaTeX papers as discourse graphs when paragraph flow, story continuity, readability, reader-state breadcrumbs, payoff chains, or figure/equation placement matter. Use when the user asks whether a section feels abrupt, wasteful, machine-generated, monotonous, hard to parse, or wants to zoom in/out across paragraphs before editing."
metadata:
  version: 0.1.4
---

# Paper Discourse Graph

Use this skill to review a paper section as a reader-state graph, not
only as a linear outline. The goal is to see what each paragraph
plants, what it pays off, where notation appears before intuition, and
where a justification detour interrupts the main story.

## 1. Workflow

### 1.1 Establish scope

Identify the source `.tex` file or section to audit. If the user wants
discussion before editing, produce findings and proposed interventions
only.

Look for project-local guidance before running a generic pass:
- `AGENT_REVIEW_BRIEF.md`
- `docs/*review*brief*.md`
- `tools/discourse_graph/profiles/*.json`
- paper-specific profiles or terminology docs

### 1.2 Choose a profile

Use the most specific available profile:
1. user-provided `--profile`
2. project-local profile, if present
3. bundled `references/profiles/cphast.json` for C-PHAST drafts
4. bundled `references/profiles/default_scientific_paper.json`

Profiles define the central reader question, audience needs, domain
terms, and topic checks. Keep project taste in profiles, not in the
engine.

For methods, theory, or appendix sections where paragraphs hand off to
notation and equations, also read
`references/formal_block_flow.md`.
When authoring or revising source files and the user wants durable
machine-readable breadcrumbs for later passes, read
`references/source_semantic_comments.md`.
For late-stage paragraph-by-paragraph refinement, task breakdowns for
fresh agents, or requests to zoom into each paragraph with a fresh
mind, read `references/paragraph_refinement_tasks.md`.

### 1.3 Run the CLI

From this skill directory:

```bash
python scripts/discourse_graph_audit.py <source.tex> \
  --section <stable-id> \
  --profile references/profiles/default_scientific_paper.json \
  --out <report.md> \
  --json-out <graph.json>
```

For C-PHAST:

```bash
python scripts/discourse_graph_audit.py paper/sec/3_method_arxiv.tex \
  --section 3 \
  --profile references/profiles/cphast.json \
  --out paper/docs/plans/discourse_graph_sec3.md \
  --json-out paper/docs/plans/discourse_graph_sec3.json
```

Optional LLM chunks:

```bash
python scripts/discourse_graph_audit.py <source.tex> \
  --section <stable-id> \
  --out <report.md> \
  --llm-jsonl <nodes.jsonl>
```

### 1.4 Interpret the report

Treat the graph as triage, not truth. The labels are prompts for
manual review.

Important node roles:
- `scene`: visible example or running situation
- `question`: planted reader question
- `claim`: assertion or section-level promise
- `mechanism`: method component or construction
- `definition` / `notation`: formal object introduction
- `justification`: reason, proof sketch, or defensive support
- `evidence`: figure, table, theorem, algorithm, or equation block
- `boundary`: scope limit or condition
- `payoff`: answer to earlier setup
- `handoff`: transition to the next object
- `semantic_comment`: source-only `% DG:` breadcrumb used to record
  author intent without rendering in the PDF

Important risk labels:
- `abrupt`: weak continuity into the current block
- `detour`: useful material that may interrupt the active story
- `unpaid_question`: a planted question without nearby payoff
- `premature_notation`: dense formal terms before visible grounding
- `weak_parent_link`: paragraph is weakly tied to its heading
- `bridge_candidate`: possible bridge that may rescue a detour
- `unconnected_evidence`: figure/table/algorithm not clearly recalled
- `context_debt`: named setting or experiment appears before enough
  local setup
- `appendix_claim_leak`: appendix-only evidence is doing main-text
  argumentative work
- `symbol_alias_confusion`: profile-tracked symbols gain a new
  subscript or variant without explaining the relationship
- `coarse_algorithm_reference`: algorithm behavior is described
  without line, stage, equation, or step anchors
- `missing_formal_setup`: equation-like block appears before prose
  creates the need for it
- `missing_formal_payoff`: equation-like block is not followed by a
  nearby interpretation
- `symbol_scope_debt`: formal block introduces several new symbols
  without nearby scope, type, or dependency prose
- `role_mismatch`: prose promises intuition or readability but hands
  off to dense notation without enough setup
- `equation_overload`: formal block introduces many symbolic objects
  at once
- `dangling_reference`: paragraph starts from this/these/such object
  without a clear local antecedent

## 2. Review Taste

For each paragraph or block, ask:
- What does the reader know right now?
- What question did the previous block plant?
- Does this block answer, sharpen, or defer that question?
- Is the payoff close enough, or is the reader carrying too much load?
- Is this block story-bearing, justification-bearing, evidence-bearing,
  implementation-bearing, or boundary-bearing?
- If this became a task for a fresh agent, what local context,
  invariants, and claim boundaries would that task need?

Prefer a chain where understanding progressively accumulates:
visible scene -> reader question -> mechanism -> formal object ->
evidence -> payoff -> next question.

Use visible language before formal terms. A dense equation should feel
inevitable because the previous paragraph made the need for that
object obvious.

For formal blocks, check the local loop:
paragraph motivates need -> notation names object -> equation commits
to definition/update/loss/constraint/readout -> paragraph interprets
what changed for the reader.

## 3. Output Format

Report findings with:
- file and line range
- live reader question
- risk label
- why the current placement breaks or helps the story
- smallest proposed intervention

Use labels:
- **Payoff**: answers a live reader question
- **Plant**: intentionally creates the next question
- **Bridge**: connects intuition to a formal object
- **Detour**: useful but not needed for the current story step
- **Stray**: does not support the current claim chain

When the user asks to discuss, do not edit. Rank the highest-value
changes and ask which ones to land.

## 4. Bundled Resources

- `scripts/discourse_graph_audit.py`: command-line entry point
- `scripts/discourse_graph/`: dependency-free LaTeX segmentation,
  heuristics, schema, and rendering code
- `references/formal_block_flow.md`: detailed rubric for paragraphs,
  notation, equations, interpretation, and consistency
- `references/paragraph_refinement_tasks.md`: late-stage per-paragraph
  task protocol for fresh review passes
- `references/source_semantic_comments.md`: optional `% DG:` comment
  convention for source-level discourse breadcrumbs
- `references/profiles/default_scientific_paper.json`: general profile
- `references/profiles/cphast.json`: C-PHAST profile with typed
  factors, charts, ports, PHASTCore, and action-card checks

## 5. Pitfalls

- Do not treat lexical overlap as a correctness judgment.
- Do not force every paragraph to use explicit transition phrases.
- Do not remove rigorous caveats merely because they are detours;
  decide whether they belong later, in an appendix, or in a tighter
  boundary sentence.
- Do not let profile-specific vocabulary leak into unrelated papers.
- Keep paper-specific notation families in the profile, for example
  `risk_rules.confusable_symbol_bases`, not in the reusable engine.
