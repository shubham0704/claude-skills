# Review gates and skill testing

Use for substantial technical walkthroughs or changes to this skill. Scale the
process to the artifact; a small correction need not trigger an agent group.

## One owner, distinct review responsibilities

The lead author owns the audience contract, prerequisite order, notation, visual
vocabulary, and integrated edits. Reviewers identify failures; do not assign
disjoint slide ranges to independent writers and assume the joins will work.

For substantial work, use independent reviewers when supported and authorized:

| Role | Give them | Ask them to test |
| --- | --- | --- |
| Technical/source reviewer | Audience brief, current sources, implementation, draft, source-to-step map | Mathematics, assumptions, information contract, loss/solver/control-flow fidelity, claim boundaries |
| First-reader reviewer | Audience brief and only the audience-facing prefix revealed so far; spoken narration only for a live-talk test | First unsupported concept, ability to explain the current operation, and what question remains |

Do not give the first reader later slides, the answer key, authoring ledger,
earlier critique, or proposed repair. An expert model has background knowledge;
ask it to identify where the deck supplied the prerequisite, not fill gaps from
its own expertise. Its judgment remains a proxy, not a human comprehension study.

Use fresh context for a genuinely independent pass. If only one agent is
available, make separate passes and report them as self-review, not independence.
Do not create separate user-facing tasks merely to simulate reviewers.

## Review before expensive layout work

1. **Story gate:** check the opening question, audience starting point, major
   dependencies, and intended result. Fix the plan before drawing every slide.
2. **Section gate:** inspect internal progression and both neighboring sections.
   Read the narration continuously; test a meaningful prefix with the first reader.
3. **Technical gate:** check algorithm steps against sources, including what each
   phase receives and returns. Do not mix paper equations with different code
   conventions without explanation. Check whether intermediate values exist on
   every branch, what is held fixed, and what initialization or solver assumes.
4. **Delivery gate:** compress redundant material, check duration, render all
   views, and inspect them in sequence. Rerun relevant checks after repairs.

Technical/source checks begin during drafting, not only after the section gate.
Passes may interleave. Do not demand a rigid four-review ceremony for a small edit.

Return findings in an actionable form:

`location -> what the reader cannot yet do -> missing prerequisite or incorrect claim -> source/example -> smallest repair`

Prioritize the first causal gap; later confusion may disappear when it is fixed.
Recommend reordering, replacement, or recall before assuming more slides are needed.
The lead reconciles findings and rechecks affected transitions and shared layouts.

## Separate verification claims

- Source audit: the explanation agrees with identified sources, with discrepancies disclosed.
- Structural checks: links resolve, stable step IDs refer to real operations, symbols and quantities are accounted for.
- Numerical checks: worked examples and executable computations match their stated assumptions.
- Render review: grouping, visual correspondence, geometry, and readability survive actual rendering.
- Reader test: a specified reader or proxy can answer a question using the material shown so far.

None substitutes for the others. A symbol checker cannot decide that "Hamiltonian"
is meaningful to a novice. Matching an exact explanatory sentence is not a test
of understanding. An agent's fluency is not proof that people will remember it.

## Forward-test a substantial skill change

Choose a fresh realistic task outside the domain that prompted the revision.
Give an independent agent the candidate skill, audience/duration/medium, and
minimum raw source material. Do not supply the intended storyboard, suspected
failure, or expected fix. Keep side effects in an isolated permitted workspace;
do not launch scientific experiments or change live artifacts to test pedagogy.

Review actual decisions and artifacts, not merely a report that the skill was
followed. Useful observable outcomes include:

- The first consequential use has a prerequisite taught in the visible prefix.
- A concrete operation supports the abstract name rather than merely preceding it.
- A reader can trace available inputs to outputs and distinguish changes of phase.
- Algorithm IDs, equations, block colors, and source references identify the same operation.
- Removing a repeated page does not erase a necessary dependency or assumption.
- A worked case reaches the correct result, with the right information available.

Test a prefix without revealing later explanations when recall or transitions
are the claimed improvement. Use a rendered artifact when testing layout; a
storyboard-only exercise cannot validate visual execution. Record observed
failures and remaining limits. Patch only what the test supports, and retest the
affected behavior. Do not claim an improvement over the old skill without a
comparison, or general effectiveness from a single successful exercise.
