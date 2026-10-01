---
name: explain-systems-visually
description: "Create or revise technical teaching slides and visual walkthroughs with prerequisite-aware progression, explicit inputs and outputs, stable color-linked equations and algorithm steps, and checks for understanding and recall. Use when readers must connect a system's purpose, components, mathematics, and execution."
---

# Explain Systems Visually

Teach why each object is needed, what it means, and how it advances the opening
question. A readable diagram and a defined symbol do not establish understanding.
Preserve the overall map while revealing each operation and its consequences.

Respect the requested medium, audience, and duration. A teaching walkthrough and
a short research talk need different depth; do not turn every request into a deck
or add slides automatically. Retain an equation-and-text format when requested.

## Establish the teaching contract

Read the current source and implementation before explaining them. Retain their
notation and abstraction boundaries; identify source disagreements instead of
silently combining versions. Separate supplied method, implementation choices,
proposed extensions, and demonstrated results.

State the audience's starting knowledge and one question the explanation should
enable them to answer. Put the intended output or decision near the beginning,
before its machinery. If audience or duration is missing, state a reasonable
assumption; ask only when the answer would materially change the artifact.

For each meaningful block, establish its role, input, operation, output,
persistent state, initialization, and parameters. Mark quantities as supplied,
measured, inferred, learned, solved, or predicted, as applicable at each phase.
An observed quantity in training may be predicted during deployment. A learned
function, integrator, state, and coordinate transform are different objects.
Keep this contract in authoring notes, not as boilerplate on every slide.

## Plan progression before layout

For a new sequence or a flow repair, read
[references/learning-flow.md](references/learning-flow.md). Check three scales:

- Whole explanation: purpose, dependencies, method, consequence, evidence.
- Within each section: establish the need, teach the operation, use its result.
- Adjacent slides or reveals: the next step consumes something already understood.

Use this compact authoring contract for each substantive reveal:
`question -> established prerequisites -> new move -> interpretation -> next question`.
Keep it off the audience slide. Do not demand identical slide structures or equal
amounts of text. Aim for one coherent conceptual move, not necessarily one equation.

Distinguish physical dependency order, execution order, and teaching order. Match
the algorithm's overall progression where useful, but teach a prerequisite before
invoking its name. Do not draw a sequential pipeline for a simultaneous solve.
Read narration across slide boundaries as a continuous explanation before styling.

## Preserve a visual vocabulary

Use a stable overview when a system map helps. Orient, highlight one block,
expand its input-operation-output, trace a concrete case, then reconnect to the
whole. For stateful systems, distinguish within-step computation, between-step
state updates, and between-run learning. Show what persists or resets.

Keep geometry, names, symbols, and role colors stable across related views.
Reuse semantic colors in blocks, equation terms, port labels, and relevant
algorithm lines. Keep explicit labels and grayscale legibility; color reinforces
identity rather than replacing it. Do not assign a new color to every variable.

Label what moves along arrows. Distinguish physical exchange, data dependency,
state carry, and gradients when several coexist. Containment is not execution;
equation-to-block correspondence lines are not flow arrows. Preserve port
directions and distinguish known inputs from inferred or computed quantities.

For Beamer, read [references/beamer.md](references/beamer.md).

## Link the algorithm to its explanation

Give meaningful algorithm steps stable identifiers and link them to the block,
equation, source, and explanation that implement or explain each operation.
Expose the input/output contract before a compressed function call. Distinguish
an explanatory pseudocode name from an actual API. Identify training, one-step
prediction, rollout, and composition as separate operations when they are.

Use the same semantic color for a step and its block. On an expansion, emphasize
the relevant line range; do not show the complete algorithm on every page. Keep
reference identifiers stable when pagination changes. Check control flow: every
consumed quantity must be available on that path, with consequential solver,
initialization, loss, and stopping choices traced to the appropriate source.
Familiar optimizers need less teaching than the model-specific computation.

## Make the mathematics teach the operation

Introduce purpose and a concrete interpretation before relying on shorthand.
Where abstraction is the obstacle, show a small explicit case before the compact
map, matrix, or function name. Explain domain/codomain, units, direction, sign,
and role where they matter. Define a law by what it maps, not just its title.

Separate physical evolution from inference about it, and parameter fitting from
using fixed parameters. Explain constraints versus rates, values versus their
derivatives, and explicit time dependence versus changing arguments when those
distinctions matter. Do not impose these categories on unrelated topics.

When a governing formulation anchors the story, first show a readable compact
view with an intelligible objective. Revisit it at milestones with the same
equations, row positions, labels, and colors, highlighting what is now understood.
Each return must enable a new answer. Secondary definitions can live in a linked
expansion; omitted conditions must not silently change the problem.
Keep decisions, objectives, hard constraints, penalties, and evaluation metrics
distinct. Improved cost alone does not establish optimality or stability.

Show both contributing terms before demonstrating cancellation. Preserve signs,
transposes, grouping, and units through styling; color is not parentheses.
Put claim-limiting assumptions in the main explanation. Separate physical
consistency, numerical solvability, identification, prediction accuracy, and
experimental evidence. A diagram or successful solve is not a proof of all five.
Label illustrative examples as such; do not manufacture supporting experiments.

## When the walkthrough is a rehearsal for a paper

Use the teaching sequence to expose missing premises and unresolved scientific
questions before polishing a manuscript. A storyboard can precede a full deck;
reuse source-current slides rather than automatically regenerating them.
Map each substantive teaching question to a paper paragraph, figure, equation,
or algorithm step, with its evidence and indispensable assumptions.
Keep symbols, semantic colors, and step identities stable, while consolidating
overlays and repeated recall views for print. Supply in prose any bridge that
previously depended on the speaker. A clear illustration is not measured evidence,
and a successful explanation does not by itself demonstrate a novel contribution.

Use `rigorous-paper-author` for the paper's claim and evidence structure when
available. A small paper edit does not require producing a separate slide deck.

## Review, compress, and verify

For substantial walkthroughs, use the gates and reviewer protocol in
[references/review-and-testing.md](references/review-and-testing.md).
One lead author owns the integrated narrative and notation. Small changes may
use separate review passes; substantial technical work benefits from independent
technical and first-reader reviews when delegation is available and authorized.
Do not equate multiple reviewers with demonstrated audience comprehension.

Before adding a slide, try reordering, replacing abstraction with an example,
recalling an earlier anchor, removing repetition, or moving secondary detail to
backup. Teach a foundation once, then retrieve it at the point of need. Preserve
material assumptions and input/output contracts during compression.

Render the actual deliverable and inspect every page or reveal, including dense
pages at full size and adjacent overlays in order. Check mathematical grouping,
labels, arrows, clipping, and positional drift. Sweep for repeated defect classes
and fix shared macros where appropriate. A clean compile, symbol checker, or
phrase-presence test does not establish comprehension or visual correctness.

Deliver the requested artifact and editable source where appropriate, with
speaker notes when useful. Report the checks actually performed and remaining
limits; if rendering was not inspected, do not call it visually verified.
