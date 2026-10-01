# Paper Blueprint for Theory-Heavy LaTeX Papers

Adapt these section purposes to the actual contribution and venue. They are not
a mandatory section list, sentence count, or requirement to invent a theorem.

## 0. Title
Must communicate object + method + setting, not only brand name.

## 1. Abstract
Explain the problem, consequential gap, enabling idea, method, and strongest
supported finding. Include a theorem or guarantee only when central to the work.
Keep empirical scope and assumptions that affect meaning; vary length and order
for the audience rather than filling predetermined sentence slots.

## 2. Introduction
Contract:

- establish problem, stakes, and gap
- explain why existing approaches fail or are incomplete
- introduce your key idea in prose before equations get dense
- list contributions separately
- end with a roadmap paragraph

## 3. Background / Preliminaries / Notation
Contract:

- define spaces, variables, operators, datasets, assumptions
- import only the background the rest of the paper truly needs
- state theorem prerequisites here, not after theorem statements

## 4. Problem Setup
Contract:

- formal objective
- assumptions
- scope and exclusions
- what counts as success

## 5. Method
Contract:

- derive the method from the formal setup
- give architecture / algorithm / variational formulation / discretization
- explain each design choice mathematically
- make interfaces to theory and experiments obvious

## 6. Theoretical Analysis
Contract:

- theorem statements first
- proof sketches in main text if the result is important
- append full proofs to appendix if they are long
- label precisely what each theorem establishes: convergence, regret, approximation, stability, consistency, identifiability, etc.

## 7. Experiments / Numerical Results
Contract:

- each experiment tests a stated claim or resolves a specific uncertainty
- include setup, baselines, metrics, ablations, and failure cases
- do not present experiments as detached demos
- align metrics with theorem quantities when possible

## 8. Conclusion
Contract:

- restate contribution in the language of solved problem + validated claim
- state limitations honestly
- indicate the next mathematically meaningful extension

## 9. Appendix
Contract:

- proofs
- omitted derivations
- implementation details
- extended figures/tables/ablations
- additional numerical analysis

## Section Interface Questions
For each section ask:

- What does this section consume?
- What does this section produce?
- Which later sections break if this section is weak?
