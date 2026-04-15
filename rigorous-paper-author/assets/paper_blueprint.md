# Paper Blueprint for Theory-Heavy LaTeX Papers

## 0. Title
Must communicate object + method + setting, not only brand name.

## 1. Abstract
Contract:
- 1 sentence: problem and why it matters
- 1 sentence: precise gap
- 1-2 sentences: core idea / reformulation / architecture / algorithm
- 1 sentence: main theorem or technical guarantee
- 1 sentence: experimental scope and strongest outcome

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
- every experiment validates a numbered claim
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
