# Develop the argument before polishing the paper

Use when starting a paper or substantially reframing its contribution. For a
local correction, reuse the existing story and inspect only the affected chain.
This is an authoring aid, not a required set of headings in the published paper.

## Scientific story brief

Michael J. Black's [Writing a good scientific paper](https://is.mpg.de/news/writing-a-good-scientific-paper)
(8 November 2024) motivates articulating the goal, obstacle, testable hypothesis,
and enabling insight before presenting technical machinery. His distinction
between insight and implementation is useful: a list of modules does not explain
why the approach should work. The workflow below adapts that advice to our
slide-first teaching, source verification, and reversible revision practice;
it is not a prescribed paragraph formula or a promise of novelty.

Write a brief in the project's own terms:

| Question | Record |
| --- | --- |
| Who needs the result? | Audience, concrete task, and consequence of getting it wrong. |
| What obstructs progress? | A specific limitation under a stated information or resource contract. |
| What is the proposed insight? | Why a modeling or reasoning choice could remove that obstacle; separate this from its implementation. |
| What already exists? | Closest methods, what they do well, what is borrowed, and the exact remaining difference. |
| What can be tested? | Hypothesis, discriminating comparison, and a result that would weaken it. |
| What do we know now? | Evidence, provenance, scope, contradictory findings, and unresolved questions. |

If the insight cannot be stated without a component catalogue, investigate the
scientific distinction instead of inventing a slogan. A replication, negative
result, benchmark, or useful integration can have a clear contribution without
claiming a new mechanism. Keep motivation, proposed capability, implementation,
and demonstrated result distinct. Do not turn an intended win into a finding.

## Rehearse with slides before substantial prose

For a new paper or major narrative repair, first make a slide-level storyboard
that could teach the argument. Reuse an existing deck when it is source-current.
An outline with figure sketches and narration is enough until a rendered deck
is requested or needed to test visual comprehension. Do not build a polished
deck for a sentence edit or force a fixed number of slides.

Start from the audience's task, encounter the obstacle, expose the proposed
insight, teach enough of the mechanism to evaluate it, then return with evidence.
This is a dependency check, not an obligation to use that exact sequence.
For each meaningful reveal, record the reader's question, available prerequisites,
new operation, interpretation, source/evidence status, and next question.
Read the narration continuously across reveals. A missing conceptual bridge
cannot be fixed just by putting adjacent topics in matching colored boxes.

Use `explain-systems-visually` when available for the teaching sequence and
rendered deck. Retain semantic colors, symbols, algorithm-step identifiers,
and input/output roles across views. A paper may use a compact algorithm where
the deck needed several reveals; keep the correspondence, not the slide count.
Teach unfamiliar foundations once and recall them where needed.

## Translate the rehearsal into a manuscript

Make a small transfer map before copying slide content:

`teaching question -> paper paragraph/figure/equation -> evidence -> retained assumptions`

- Turn spoken transitions into prose that works without the speaker.
- Consolidate overlays and repeated overview maps; keep indispensable definitions.
- Give each figure a question and interpretation. A schematic shows a mechanism;
  it does not establish an empirical advantage.
- Preserve algorithm-to-equation/code correspondence and label any implementation
  discrepancy. Explaining the intended algorithm does not verify the executed one.
- Adapt pacing to print: readers can reread equations but cannot hear narration.
  Do not simply paste slide titles into subsection headings.

Draft a provisional introduction early to expose research and teaching gaps.
Use questions or explicitly pending evidence slots in working notes, never
invented results. Develop method, assumptions, implementation, and evidence in
parallel as available. Finalize introduction, abstract, and conclusion against
the verified work, revising the hypothesis when observations require it.

## Check the return to the opening question

For each important promise, locate the exact evidence and its interpretation.
Distinguish a result for a subproblem from an answer to the end-to-end question.
Useful diagnostics can explain a limitation without demonstrating a deployed
capability. Do not use a smoother transition to conceal an absent experiment.
Supporting domains should test a specific generalization or consequence of the
same argument, not merely enlarge a catalogue of datasets.

Organize related work around meaningful approaches and their assumptions.
Represent strengths and inherited ideas fairly; unfamiliarity with a method is
not evidence that it lacks a capability. Retain source links in the claim ledger.

## Review without teaching the answer to the reviewer

One author owns the integrated argument. For substantial revisions, use separate
technical and cold-reader passes when supported and authorized. Give the reader
only the audience brief and visible artifact, not the intended insight or answer
key. Ask what problem is addressed, why the approach could help, what was shown,
and what remains unresolved, with locations supporting each answer.
Record misconceptions and repair the first causal gap. Agent readers are a
diagnostic proxy, not a measurement of human learning or recall.

Keep these checks separate: scientific support, source/code agreement, reader
understanding, and rendered correctness. A clean compile, fluent retelling, or
agreement among agents does not substitute for the others. Finish with a scoped
before/after comparison and preserve a rollback point when revising real work.
