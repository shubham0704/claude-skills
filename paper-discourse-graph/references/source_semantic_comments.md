# Source Semantic Comments

Use source-only comments when the author wants durable discourse
bread crumbs for later agent passes without changing the rendered PDF.

## Syntax

Write one-line comments starting with `% DG:`. Use simple key-value
pairs so tools can parse them and humans can skim them.

```tex
% DG: role=setup target=eq:candidate-rollout question="How does a candidate become a typed rollout?"
C-PHAST rolls each candidate forward from the same inferred latent state:
\begin{equation}
...
\label{eq:candidate-rollout}
\end{equation}
% DG: role=payoff source=eq:candidate-rollout meaning="Only future controls differ; the inferred initial state is shared."
```

Recommended keys:

- `role`: `setup`, `plant`, `bridge`, `definition`, `notation`,
  `payoff`, `interpretation`, `boundary`, `evidence`, or `handoff`.
- `target`: label of the block being set up.
- `source`: label of the block being interpreted or recalled.
- `question`: reader question planted here.
- `meaning`: compact interpretation or payoff.
- `introduces_symbol`: symbol introduced nearby.
- `relation`: relationship to a nearby symbol or term.
- `setting_intro`: experiment, benchmark, or setting introduced here.
- `appendix_only`: use `true` when the statement should not carry a
  main-text claim.

## Usage Rules

- Use comments sparingly. Annotate high-value transitions, not every
  paragraph.
- Prefer comments for author intent that heuristics cannot reliably
  infer: symbol relationships, setup/payoff edges, appendix-only
  evidence boundaries, and setting introductions.
- Do not put paper-specific vocabulary into the generic parser. Put
  project-specific terms in the profile.
- Do not use hidden rendered macros unless the project explicitly
  requires them. Comments are safer for arXiv, Overleaf, and
  collaborators.
- Keep comments factual and short. They should help another agent
  understand the source, not become a second paper.

## Examples

```tex
% DG: role=notation introduces_symbol=M_eff relation="fixed inverse-mass metric, not learned Hamiltonian mass"
```

```tex
% DG: role=boundary appendix_only=true source=app:accuracy_transfer:spectral_diagnostics meaning="diagnostic support only, not the full critic"
```

```tex
% DG: role=setting_intro setting_intro="Go2 lateral-push critic" target=tab:safety-critic-main
```
