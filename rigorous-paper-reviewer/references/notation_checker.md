# LaTeX notation checker

Use `scripts/check_latex_notation.py` to create a reproducible first pass over
symbol introduction and reuse. The checker follows `\input` and `\include` in
document order, reports source locations, treats Beamer frames as review units,
and can stop at `\appendix`.

## Commands

Audit only the main narrative:

```bash
python3 ~/.claude/skills/rigorous-paper-reviewer/scripts/check_latex_notation.py main.tex
```

Audit the supplement or backup slides too:

```bash
python3 ~/.claude/skills/rigorous-paper-reviewer/scripts/check_latex_notation.py main.tex --scope all
```

Use `--json` for machine-readable output, `--include-info` to list symbols that
are declared but not used later, and `--strict` to return a nonzero status when
an error is detected.

## Findings

- `N001`: no formal declaration or nearby prose explanation was detected.
- `N002`: a symbol is used in an earlier section or slide than its first
  declaration or explanation.
- `N003`: an equation introduces a symbol without nearby semantic prose.
- `N004`: callable notation is later reused as a numeric value.
- `N005`: observed roles conflict with a project registry.
- `N006`: required first-use terminology from a registry is absent.
- `N007`: a declared symbol is not used later in the selected scope.

Errors are high-confidence structural conflicts. Warnings are review prompts,
not proof that the manuscript is wrong. In particular, TeX macro expansion,
implicit conventions, prose far from an equation, and overloaded domain
notation require human judgment.

## Optional registry

For a final notation audit, add a small JSON registry beside the manuscript.
It turns project-specific meanings and role expectations into deterministic
checks without teaching the parser domain semantics:

```json
{
  "ignore": ["i", "j"],
  "symbols": {
    "K": {
      "meaning": "controlled transition kernel",
      "terms": ["transition kernel"],
      "roles": ["callable"]
    },
    "\\eta": {
      "meaning": "observation parameters",
      "terms": ["observation parameters"],
      "roles": ["value"]
    }
  }
}
```

Registry keys use the notation as written in math mode. `terms` are
case-insensitive phrases that must occur in the same first-use section or slide.
`roles` may contain `value` and/or `callable`. A value may still be a vector,
matrix, tensor, or set; the label only means that it is not called with an
argument list. Keep the registry restricted to
scientifically important symbols; dummy indices and standard constants belong
in `ignore`.

## Review contract

The tool can establish lexical facts: occurrence order, nearby explanatory
language, and spelling/role reuse. It cannot establish that a description is
physically correct, that two symbols are mathematically equivalent, or that the
reader has enough motivation. After running it, inspect every error and then do
the skill's manual notation and progressive-introduction passes.
