---
name: plan-to-dag
description: "Convert large multistep plans, implementation roadmaps, architecture plans, migration plans, or vague next-step requests into dependency-aware DAGs with execution waves, parallel worksets, ownership boundaries, validation gates, and subagent-ready prompts. Use when the user asks for a task graph, DAG, wave plan, dependency plan, implementation breakdown, or subagent prompt pack."
allowed-tools: Read, Grep, Glob, Edit, Write, Bash, Task, TaskCreate, TaskUpdate, TaskList
---

# Plan To DAG

## Core Rule

Turn the plan into an execution graph before implementation. Do not produce a flat task list for work that has dependencies, shared files, rollout gates, or multiple agents.

## Workflow

1. Extract concrete tasks.
2. Mark blockers, dependencies, and shared write surfaces.
3. Classify tasks by type and risk.
4. Build a DAG.
5. Compress the DAG into execution waves.
6. Define validation gates for each wave.
7. Produce subagent prompts only for tasks that can run independently.
8. State what must stay local on the critical path.

## Task Extraction

Convert prose into task nodes. Each node must have:

```text
id:
title:
type: research | design | code | test | docs | migration | ops | review
owner: local | worker | explorer | human | external
write_scope:
inputs:
outputs:
depends_on:
parallel_with:
risk: low | medium | high
validation:
done_when:
```

Prefer small implementation nodes with clear write scopes. Avoid vague nodes such as “integrate platform” or “improve system”.

## Dependency Rules

Use these dependency defaults unless the repo proves otherwise:

- Contracts before producers and consumers.
- Schemas before generated types.
- DB migrations before stores and APIs.
- Store methods before API handlers.
- API handlers before UI integration.
- Runtime registry before runtime execution.
- Feature flags before behavior changes.
- Dual-write before read-path switch.
- Read-path switch before deleting compatibility paths.
- Tests beside each behavior change, not only at the end.
- Docs/ADRs before irreversible architecture changes.

## Parallelization Rules

Parallelize only when write scopes do not overlap and the tasks do not depend on each other.

Good parallel splits:

- schema/type work vs documentation
- platform API tests vs vehicle runtime tests
- UI handoff docs vs backend migration design
- independent app handlers with separate files

Bad parallel splits:

- two workers editing the same generated API file
- implementation before schema is settled
- tests for behavior not yet implemented
- cleanup that touches files active workers are editing

## Wave Design

Group tasks into waves where every task in a wave can start after prior waves complete.

Each wave must include:

```text
wave:
objective:
tasks:
parallelism:
critical_path:
validation_gate:
rollback_or_backout:
commit_boundary:
```

Commit boundaries should align with waves or independently reviewable slices. Avoid a mega-commit that mixes contract, DB, API, UI, and docs.

## Critical Path

Keep blocking work local when immediate next actions depend on it. Use subagents for bounded sidecar work that can run without blocking the main rollout.

Before proposing subagents, explicitly answer:

- What am I doing locally right now?
- Which tasks can safely run in parallel?
- Which files or modules does each worker own?
- What must not be touched by each worker?

## Output Format

For normal planning, output:

1. Direction check.
2. DAG table.
3. Wave plan.
4. Subagent prompt pack.
5. Validation matrix.
6. Risks and kill criteria.

For implementation handoff, add:

- exact repo paths
- file ownership per worker
- forbidden files or behaviors
- expected commits
- test commands

## Subagent Prompt Pack

Each prompt must be self-contained and bounded:

```text
Task:
Context:
Ownership:
Do not touch:
Inputs:
Expected output:
Validation:
Return:
```

Always tell worker subagents:

```text
You are not alone in the codebase. Do not revert edits made by others. Keep your write scope tight and adapt to surrounding changes.
```

For explorer subagents, ask specific codebase questions, not broad “understand everything” prompts.

## Validation

If a structured DAG artifact is useful, emit JSON and validate it with:

```bash
python3 <skill-dir>/scripts/validate_dag.py path/to/dag.json
```

Use `references/dag-json-schema.md` only when a strict machine-readable DAG is requested or when the user asks to save the DAG as an artifact.

## Quality Bar

The DAG is acceptable only if:

- every non-root task has at least one dependency or a clear reason it is root
- no task depends on itself
- no cycles exist
- every wave contains only tasks whose dependencies are in earlier waves
- every task has a validation gate
- subagent tasks have disjoint write scopes
- high-risk tasks have rollback or kill criteria
- the first wave creates evidence or a durable seam, not process-only work
