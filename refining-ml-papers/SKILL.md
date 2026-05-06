---
name: refining-ml-papers
description: Refines ML/scientific LaTeX papers based on reviewer or advisor feedback. Handles structural reorganization (moving problem statements, merging sections), concrete instantiations of abstract tables, cross-file deduplication, and compilation verification. Use when the user requests paper revisions, addresses reviewer comments, restructures sections, or improves exposition clarity.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash, Task, TaskCreate, TaskUpdate, TaskList, EnterPlanMode
---

# Refining ML Papers: From Feedback to Camera-Ready

This skill captures battle-tested patterns for revising scientific LaTeX papers in response to reviewer/advisor feedback. Built from extensive revision work on multi-file ICML-style papers with Overleaf git workflows.

## When to Use This Skill

Invoke when the user:
- Has reviewer or advisor feedback to address
- Wants to restructure paper sections (move content, merge sections)
- Needs to explain tables or figures with concrete examples
- Asks to improve exposition clarity or reduce redundancy
- Wants to fix LaTeX compilation issues after restructuring
- Needs to prepare a camera-ready or arXiv version

## Core Methodology

### Phase 1: Understand the Paper Architecture

Before making ANY changes:

1. **Map the file structure**: `Glob` for `**/*.tex` to find all LaTeX files
2. **Identify the main file** and all `\input{}` dependencies
3. **Read the target sections** completely before editing
4. **Check for shared macros**: Look for `\providecommand` / `\newcommand` patterns that indicate cross-file dependencies
5. **Note existing labels**: `Grep` for `\label{` and `\ref{` to understand cross-reference graph

```
# Typical modular structure:
main_arxiv.tex          # Preamble + abstract + introduction + \input{} calls
methods.tex             # Section 3
experiments.tex         # Section 4
appendix.tex            # Appendix
appendix_casimir.tex    # Specialized appendix
references.bib          # Bibliography
```

### Phase 2: Plan Changes with Feedback Mapping

Map each piece of feedback to a **concrete file + line range + action**:

| Feedback | Action | File(s) | Risk |
|----------|--------|---------|------|
| "Problem statement too late" | Move to Sec 1 + slim Sec 3 | main.tex + methods.tex | Cross-ref breakage |
| "Table entries unclear" | Add concrete instantiations paragraph | main.tex | None |
| "Sections redundant" | Merge + back-reference | methods.tex | Label conflicts |
| "Abstract doesn't state problem" | Restructure abstract | main.tex | None |

**Always use `EnterPlanMode`** for multi-file restructuring. Present the plan before editing.

### Phase 3: Implementation Patterns

#### Pattern 1: Moving Content Earlier (e.g., Problem Statement to Introduction)

This is the most common revision request. The three-step protocol:

1. **Add** the content in its new location (e.g., new `\paragraph{Problem setting.}` in Introduction)
2. **Slim** the original location to a back-reference: "As described in Section~\ref{sec:intro}, ..."
3. **Preserve** all `\label{}` tags or update `\ref{}` calls

**Key principle**: The moved content should be a **self-contained summary**, not a copy-paste. The original section keeps the technical details.

Example structure for a problem-setting paragraph in the Introduction:
```latex
\paragraph{Problem setting.}
We consider the [setting name]: we observe only [what's observed]
at discrete times; [what's latent] are latent and never measured.
The goal is to [goal (a)] and [goal (b)].
[Method] addresses this via [solution sketch: 2-3 stages].
Given [input], [method] produces [output];
Section~\ref{sec:methods} details the components.
```

#### Pattern 2: Explaining Abstract Tables with Concrete Instantiations

When a table maps systems to mathematical components, add a `\paragraph{Concrete instantiations.}` that walks through 2-3 representative rows:

```latex
\paragraph{Concrete instantiations.}
To make the mapping from physical system to $(V, M, D)$ template explicit,
we walk through three representative entries from Table~\ref{tab:...}:
\begin{itemize}
\item \textbf{System A} (REGIME).
  State $q = ...$, momentum $p = ...$.
  [Component 1] encodes [physical meaning];
  [Component 2] is [given/learned because...];
  [Component 3] is [the unknown that method learns].

\item \textbf{System B} (DIFFERENT REGIME).
  [Same structure, different system, showing contrast]

\item \textbf{System C} (CROSS-DOMAIN).
  [Non-obvious domain to show generality]
\end{itemize}
```

**Selection heuristic**: Pick one fully-specified (KNOWN), one partially-specified (PARTIAL), and one from a surprising domain (non-mechanical, ecological, etc.).

#### Pattern 3: Abstract Restructuring (Problem-First)

Reviewers often complain the abstract leads with the framework instead of the problem. The canonical structure:

1. **Context** (1 sentence): Why this domain matters
2. **Problem** (1-2 sentences): What we're solving, what's observed vs. latent
3. **Framework** (1 sentence): The structural insight that enables the solution
4. **Method** (1-2 sentences): What the method does concretely
5. **Results** (1 sentence): Key empirical finding
6. **Insight** (1 sentence): What we learned (e.g., identifiability vs. forecasting)

**Anti-pattern**: Starting with "$\dot{x} = (J-R)\nabla H(x)$" before the reader knows what problem is being solved.

#### Pattern 4: Section Merging / Deduplication

When two sections overlap (e.g., Sec 3.1 and Sec 3.2 both introduce PH dynamics):

1. **Identify the canonical location** (usually the first occurrence)
2. **Move unique content** from the later section into the earlier one
3. **Replace the later section** with a back-reference paragraph
4. **Update the section roadmap** (the "This section describes..." paragraph)
5. **Check all `\ref{}`** calls to the removed/merged subsection labels

#### Pattern 5: Cross-File Consistency After Restructuring

After moving content between files, verify:
- Labels defined in one file aren't duplicated in another
- `\ref{}` calls still resolve (compile and check log)
- Notation is consistent (same macro names for the same symbols)
- Commented-out content in the original location is cleaned up or marked

#### Pattern 6: Cross-Reference Connectivity Audit

For a thorough review (not just compilation), audit the full cross-reference graph:

1. **Grep all `\label{}`** and **`\ref{}`** across every `.tex` file
2. **Check label naming matches location**: A label `sec:methods:X` should be defined in the methods section, not the introduction. Rename mislocated labels.
3. **Find orphan labels**: Defined but never referenced — typically fine for internal appendix structure, but flag any in the main paper
4. **Find dangling refs**: Referenced but not defined — even in commented-out code, these signal stale content
5. **Verify back-references**: If methods.tex opens with "As described in Sec 1...", confirm the label resolves to the right paragraph

**Real example**: `sec:methods:regimes` was defined in the Introduction (promoted for arXiv) but the name implied Methods. Every `\ref` resolved to Sec 1 when readers expected Sec 3. Renamed to `sec:intro:regimes`.

#### Pattern 7: Table Claim Verification

When a table summarizes properties (identifiability, convergence, complexity):

1. **Check each cell against its detailed description** in the appendix or body text
2. **Flag qualified claims presented as unqualified** (e.g., "Yes" when the appendix says "up to overall scale")
3. **Check notation consistency**: Symbols in table columns shouldn't clash with established notation (e.g., $D_0$ for mass base diagonal when $D$ is reserved for damping → rename to $m_0$)
4. **Add footnotes for caveats**: Use `$^\dagger$` with caption text rather than silent simplification

#### Pattern 8: Appendix Cleanup & Prose Quality

Appendix sections often accumulate dead code and robotic prose:

1. **Delete empty placeholders**: Subsections that say only "Left to future work" — remove entirely
2. **Clean commented-out blocks**: >50 commented lines with no active content nearby → delete
3. **Add regime/group headers**: When listing many items back-to-back (e.g., 9 systems), group them with `\paragraph{}` headers and 1-2 connecting sentences
4. **Fix float drift**: Appendix figures with `[h]` or `[t]` often drift into the bibliography → use `[H]` (requires `\usepackage{float}`)

#### Pattern 9: Mechanism-Before-Claim Prose

When body prose sounds like a slogan or summary card, rewrite it so the reader sees the mechanism before the claim.

Watch for sentences like:
- "This provides an interface for domain knowledge."
- "This shows the model is interpretable."
- "This is the main diagnostic lesson."
- "The result demonstrates robustness."

Replace them with the concrete chain:
- **Modeling choice**: what component, constraint, chart, loss, or algorithm step changes?
- **Failure mode**: what goes wrong without it?
- **Isolating evidence**: which ablation, metric, figure, or table shows the effect?
- **Scope**: what does the result not prove?

Example:
```latex
% Weak
Domain charts provide an interface for target manifolds.

% Stronger
If q lives on a constrained space Q, raw Euclidean coordinates make the
constraint a learned behavior rather than a structural fact.  PHAST therefore
uses a chart z = chi(q) before phase-state inference.  In predator--prey,
the log-positive chart removes negative-population rollouts and improves
H=100 error under observation noise without changing the rollout architecture.
```

Use contribution lists in the introduction when helpful, but avoid claim-map
language in technical body paragraphs. Body paragraphs should teach the reader
the mechanism, not recite the claim.

### Phase 4: Compilation & Verification

**Always compile after changes.** The full verification workflow:

```bash
# Full build (from the paper directory)
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

**Post-compilation checks:**
```bash
# Zero undefined references
grep -c "undefined" main.log
# Zero multiply-defined labels
grep "multiply" main.log
# Check for other warnings (filter noise)
grep -i "warning" main.log | grep -v "Font\|pdf\|Unused\|size\|rerun\|float\|empty\|draft"
```

**Visual verification**: Read the PDF pages where changes were made to confirm rendering.

### Phase 5: Git Workflow (Overleaf)

For Overleaf-backed papers:
- Commit with descriptive messages referencing the feedback addressed
- Push directly to master (Overleaf syncs from master)
- Only commit `.tex` and `.bib` files; exclude build artifacts (`.aux`, `.log`, `.pdf`, `.bbl`, `.blg`, `.out`)

## Common Revision Patterns by Feedback Type

### "The paper doesn't state the problem clearly"
→ Pattern 1 (move to intro) + Pattern 3 (rewrite abstract)

### "I don't understand what Table X means"
→ Pattern 2 (concrete instantiations)

### "Sections 3.1 and 3.2 seem redundant"
→ Pattern 4 (merge + back-reference)

### "The abstract is too technical / leads with equations"
→ Pattern 3 (problem-first abstract)

### "The notation is introduced too late"
→ Move notation paragraph earlier; keep formal definition in Methods

## LaTeX Pitfalls in Paper Revision

See `PITFALLS.md` for the complete reference. Critical ones:

| Issue | Cause | Fix |
|-------|-------|-----|
| xcolor option clash | Style file loads xcolor; you also load it | `\PassOptionsToPackage{table}{xcolor}` BEFORE `\usepackage{icml2026}` |
| Undefined `\ref` after merge | Label moved to different file | Check `\label{}` exists in the new location |
| `table*` in single-column | Switched from two-column to one-column | Replace `table*` → `table`, `figure*` → `figure` |
| Multiply-defined labels | Merged sections both had `\label{sec:ph}` | Rename one; update all `\ref{}` calls |
| `\providecommand` doesn't override | Macro already defined in preamble | Use `\renewcommand` or define only in preamble |

## Output Format

After implementing all revisions:

```markdown
## Revision Summary

| Part | File | What Changed |
|------|------|-------------|
| A | main.tex | Abstract rewritten: problem before framework |
| B | main.tex | New "Problem setting" paragraph in Sec 1 |
| C | methods.tex | Sec 3.1 slimmed to back-reference |
| D | main.tex | Concrete instantiations for Table 1 |

Build: clean (N pages, 0 undefined refs, 0 warnings)
```

## Progressive Disclosure

For detailed examples and pitfalls:
- `PATTERNS.md` — Complete before/after examples from real revisions
- `PITFALLS.md` — Comprehensive LaTeX pitfalls with fixes

## Validation Checklist

Before marking revision complete:
- [ ] All feedback items addressed with specific file + line changes
- [ ] Full compilation passes (pdflatex + bibtex + pdflatex × 2)
- [ ] Zero undefined references in log
- [ ] Zero multiply-defined labels
- [ ] PDF visually verified on affected pages
- [ ] No redundant content between sections (no reader déjà vu)
- [ ] Abstract states the problem before the framework
- [ ] All tables with abstract entries have concrete explanations nearby
- [ ] Label names match the section they're defined in (no `sec:methods:X` in intro)
- [ ] Table claims match detailed text (footnote any qualified claims)
- [ ] No notation collisions across columns/sections (e.g., $D_0$ for mass vs. $D$ for damping)
- [ ] Appendix: no empty placeholder sections, no large commented-out blocks
- [ ] Appendix: figures use `[H]` placement (not `[h]`/`[t]` which drift)
- [ ] Git committed with descriptive message mapping to feedback
