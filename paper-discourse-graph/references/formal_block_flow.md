# Formal Block Flow

Use this reference when reviewing methods, theory, or appendix sections
where prose hands off to notation, equations, algorithms, or other
formal blocks.

## Core Model

Treat paragraphs, notation, and equations as different node types in
one reader-state graph.

- A paragraph manages attention and meaning. It tells the reader what
  problem is alive, what object is needed, why it matters, and what
  question should be answered next.
- Notation manages compression and identity. It gives a stable name to
  an object the reader should track, including type, scope,
  dependencies, and relationship to nearby symbols.
- An equation manages formal commitment. It defines an object, update
  law, loss, constraint, conservation identity, diagnostic readout, or
  decision rule.
- The paragraph after a formal block manages interpretation. It tells
  the reader what changed and how to use the formal object.

The target loop is:

```text
paragraph motivates need
-> notation names object
-> equation makes one formal commitment
-> paragraph interprets consequence
```

## Local Audit

For each paragraph/equation neighborhood, write:

```text
Before this block, reader knows:
This block introduces:
This block depends on:
This block answers:
This block leaves open:
```

Then decide whether the block is doing one of five jobs:

- **Setup**: creates the need for a formal object.
- **Naming**: introduces notation and its scope.
- **Commitment**: defines or constrains something formally.
- **Interpretation**: translates the formal object back into meaning.
- **Reuse**: recalls a prior formal object without changing its meaning.

## Consistency Checks

Check consistency at several layers, not only at the symbol level.

- **Semantic consistency**: the same word or symbol keeps the same
  meaning unless the relationship is explicitly explained.
- **Scope consistency**: the reader knows whether an object is local,
  global, deployed, benchmark-specific, optional, downstream, or
  appendix-only.
- **Role consistency**: the equation's role matches the paragraph's
  promise. Do not let an intuition paragraph abruptly hand off to
  dense notation unless it also creates the need for that notation.
- **Evidence consistency**: a figure, table, algorithm, or appendix
  supports the active claim instead of introducing a new setting early.
- **Reader-state consistency**: after the block, the reader knows more
  and carries fewer unresolved objects.

## Failure Patterns

- **Missing setup**: an equation appears before the prose makes the
  reader want it.
- **Missing payoff**: an equation is correct but the next prose does
  not say what it means.
- **Symbol scope debt**: new notation appears without type, scope,
  dependency, or relationship to nearby symbols.
- **Notation alias confusion**: two similar symbols appear, such as a
  learned object and an effective/proxy object, without explaining the
  distinction.
- **Equation overload**: one block introduces too many objects for the
  reader to bind at once.
- **Dangling reference**: a paragraph starts with "this factor",
  "these modes", or "such a map" when the antecedent is not locally
  visible.

## Intervention Patterns

Prefer the smallest edit that restores the loop.

- Add one setup sentence before the equation: "The planner needs a
  quantity that ... We therefore define ..."
- Add one naming sentence: "Here X is local, Y is deployed, and Z is a
  fixed metric used only in this step."
- Split an overloaded equation into definition plus use.
- Add one payoff sentence after the equation: "This means ...", "The
  key point is ...", or "Operationally, ..."
- Move appendix-only details out of the main flow unless they answer
  the live reader question.

## Good Review Questions

- Before this formal block appears, has the paper made the reader want
  it?
- Does each new symbol have a type, scope, dependency, and lifetime?
- Does the equation make one clear commitment?
- Does the next sentence translate the formal commitment back into the
  story?
- If a later paragraph says "this" or "these", is the antecedent still
  locally visible?
