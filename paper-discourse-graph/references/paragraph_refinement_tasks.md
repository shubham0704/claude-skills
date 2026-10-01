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

- Can I summarize this paragraph in 6--10 words?
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

## GRE-Style Paragraph Logic

Use this lens when a paragraph feels correct sentence by sentence but
still feels overloaded, abrupt, or hard to follow.

### Five Tests

1. **Topic promise.** The first sentence should make one clear promise:
   what the paragraph is about and why it exists.
2. **Unity.** Every later sentence should serve that promise. If a
   sentence serves a different promise, split the paragraph or make the
   relationship explicit.
3. **Coherence.** Each sentence should begin from known ground and add
   one new object, relation, example, or boundary. This is the
   given-to-new rule.
4. **Development.** The paragraph should give enough example,
   mechanism, notation, or evidence for the reader to believe the
   topic promise without turning into a list.
5. **Transition.** The ending should pay off the paragraph or hand the
   reader to the next live question.

### Sentence-Flow Ledger

For overloaded paragraphs, make a small ledger before editing:

```text
S1 job:
S1 connects back to:
S1 adds:
S1 plants reader question:

S2 job:
S2 connects back to:
S2 adds:
S2 plants/answers:
...
Paragraph summary in 6--10 words:
Payoff sentence:
Next paragraph handoff:
```

Allowed sentence jobs:

- **Topic promise**: states the paragraph's main object and direction.
- **Scene/example**: makes the idea visible before abstraction.
- **Mechanism**: explains how the object works.
- **Definition**: names an object and gives scope.
- **Formalization**: introduces notation, equation, or algorithm.
- **Interpretation**: translates formal material back into meaning.
- **Boundary**: limits the claim or prevents misreading.
- **Payoff**: states what the reader now understands.
- **Handoff**: makes the next paragraph feel necessary.

### Overload Signals

Split or restructure the paragraph when:

- It cannot be summarized in 6--10 words.
- It has more than one topic promise.
- Adjacent sentences have unrelated jobs, e.g. definition -> topology
  exception -> notation convention -> future work.
- It introduces more than two or three new objects before giving
  payoff.
- The subject changes repeatedly: chart -> topology -> metadata ->
  notation -> state refresh -> future work.
- An equation appears before an example makes the reader want it.
- A boundary sentence sounds like a disclaimer because the main claim
  was not scoped earlier.

### Intervention Patterns

- Put a concrete example before abstraction.
- Move notation after the reader has a visible need for it.
- Convert a list into a chain: object -> mechanism -> consequence.
- Split definition, boundary, and future-work material into separate
  paragraphs when each has its own topic promise.
- Add a payoff sentence in plain English: "This matters because ..."
  or a more paper-native equivalent.
- Add a handoff sentence only when the next paragraph changes the live
  question.

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
