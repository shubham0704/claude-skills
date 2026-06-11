# Paragraph Refinement Tasks

Use this reference for late-stage writing passes when the section
already has the right ingredients but each paragraph needs a fresh,
high-quality readability and flow check.

## Fresh-Paragraph Protocol

Treat each paragraph as a small task with local context, not as a
line-edit inside a large blur.

For each paragraph, inspect a window of:

```text
previous paragraph or block
current paragraph
next paragraph or block
nearby figure/table/equation references
```

Then answer:

```text
Live reader state:
What the paragraph is trying to do:
What it introduces:
What it assumes:
What it pays off:
What it leaves open:
Smallest useful edit:
```

## Paragraph Jobs

Assign exactly one primary job before editing:

- **Scene**: makes a concrete situation visible.
- **Question**: plants the problem the next material must answer.
- **Bridge**: connects intuition to notation, equation, table, or
  figure.
- **Definition**: names an object and gives its type/scope.
- **Mechanism**: explains how a construction runs.
- **Evidence**: points to a result, figure, table, or experiment.
- **Payoff**: tells the reader what has been learned.
- **Boundary**: limits scope without sounding defensive.
- **Handoff**: prepares the next paragraph.

If a paragraph has two or more primary jobs, split it or make one job
subordinate.

## Questions To Ask

- Can the reader paraphrase this paragraph after one read?
- Does the first sentence tell the reader why this paragraph exists?
- Does the final sentence either pay off the paragraph or prepare the
  next one?
- Are terms introduced in the order the reader needs them?
- Does a formal term appear before visible intuition?
- Does an appendix, figure, or experiment name appear before enough
  local setup?
- Is the paragraph proving, motivating, explaining, or merely listing?
- Can any long sentence become two shorter sentences without losing
  rhythm?
- Are repeated words such as "recall", "return", "same", "typed", or
  "contract" earning their keep?

## Task List Format

When creating work for another agent, emit independent tasks:

```text
Task P12, lines 167-176
Goal: make the physical-critic paragraph readable as a four-step chain.
Reader state before: deployed transition has just been defined.
Must preserve: G_theta notation, candidate futures, typed consequences,
planner-facing factors, action cards.
Check: the paragraph should not imply C-PHAST directly outputs a scalar
score or learns recovery actions.
Deliverable: proposed rewrite plus one-sentence rationale.
```

Keep each task narrow enough that a fresh agent can solve it without
re-reading the entire paper, but include enough local invariants to
avoid accidental claim drift.

## Edit Discipline

- Do not polish away technical boundaries.
- Do not add disclaimers as a separate defensive paragraph; fold scope
  into the claim.
- Preserve labels, citations, and theorem/equation references unless
  the task explicitly asks to move them.
- Prefer one concrete bridge sentence over repeated "recall" or
  "return to" transitions.
- After editing, reread the previous-current-next paragraph triplet
  aloud for rhythm and reader-state continuity.
