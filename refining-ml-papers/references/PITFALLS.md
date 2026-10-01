# LaTeX Pitfalls in Paper Revision

Comprehensive reference for LaTeX issues encountered during paper restructuring, compiled from real revision sessions.

## Package Conflicts

### xcolor Option Clash
**Symptom**: `Option clash for package xcolor`
**Cause**: Your document loads `\usepackage[table]{xcolor}` but the conference style file (e.g., `icml2026.sty`) also loads `xcolor` without options.
**Fix**: Use `\PassOptionsToPackage` *before* loading the style:
```latex
\PassOptionsToPackage{table}{xcolor}
\usepackage[preprint]{icml2026}
% Do NOT also write \usepackage{xcolor} — the style file handles it
```

### hyperref Conflicts
**Symptom**: `pdfauthor already defined` or similar
**Cause**: hyperref loaded twice (by you and by style file)
**Fix**: Check if the style file loads hyperref. If so, remove your `\usepackage{hyperref}` or load it conditionally.

## Cross-Reference Issues

### Undefined References After Section Merge
**Symptom**: `Reference 'sec:methods:ph' undefined`
**Cause**: You removed a `\subsection` that had a `\label`, but refs to it still exist in other files.
**Fix**:
```bash
# Find all references to the label
grep -rn "ref{sec:methods:ph}" *.tex
# Either update the refs or keep the label in its new location
```

### Multiply-Defined Labels After Content Move
**Symptom**: `Label 'eq:ph_dynamics' multiply defined`
**Cause**: You added the equation in the introduction but forgot to remove the label from the original location in methods.
**Fix**: Keep the label only in the *canonical* location (usually the first occurrence). Remove duplicates.

### Labels in Comments Still Counted
**Symptom**: Multiply-defined label for a label you think you removed
**Cause**: The label is in a `%` comment but LaTeX still processes `\label{}` inside some environments.
**Fix**: Fully delete (don't just comment) duplicate labels. Or use `\iffalse...\fi` for large commented blocks.

### Label Names Don't Match Section Location
**Symptom**: `\ref{sec:methods:regimes}` resolves to "Sec. 1" instead of expected "Sec. 3"
**Cause**: Content was promoted from Methods to Introduction for the arXiv version, but the label name wasn't updated.
**Fix**: Rename the label to match its actual section (e.g., `sec:intro:regimes`). Grep all files for the old name:
```bash
grep -rn 'sec:methods:regimes' *.tex
```
Then update every occurrence (definition + all references).

### Cross-Reference Points to Wrong Target
**Symptom**: "the FD+TCN observer (Sec. 1)" when the observer is described in Sec. 3.1
**Cause**: The reference was written when the target content was in a different section; after restructuring, it now points to unrelated content.
**Fix**: Verify each `\ref{}` actually resolves to the content the surrounding prose describes — not just that it compiles.

## Table/Figure Layout

### `table*` in Single-Column Mode
**Symptom**: Table renders incorrectly or floats to wrong page
**Cause**: `table*` spans two columns, but you're in `\onecolumn` mode
**Fix**: Replace `table*` with `table` and `figure*` with `figure`

### `\resizebox` in Single-Column
**Symptom**: Table is tiny (was scaled for two-column width)
**Cause**: `\resizebox{\textwidth}` was calibrated for narrow two-column width
**Fix**: Remove `\resizebox` entirely — single-column has enough width. Or use `\small`/`\scriptsize` font size instead.

### TabularX Column Width
**Symptom**: X columns too wide or too narrow after layout change
**Fix**: Adjust `\setlength{\tabcolsep}` and consider switching from `tabularx` to `tabular` if manual control is needed.

## Macro Issues

### `\providecommand` Doesn't Override
**Symptom**: Macro has wrong definition despite your `\providecommand`
**Cause**: `\providecommand` only defines if not already defined. If preamble defines it first, the `\providecommand` in an `\input` file is silently ignored.
**Fix**: Define all shared macros in the main preamble only. Use `\providecommand` in input files as fallback for standalone compilation.

### Undefined Control Sequence in Tables
**Symptom**: `Undefined control sequence \textsc` or `\Mmat`
**Cause**: Custom macro not loaded before the table is processed
**Fix**: Ensure all `\newcommand` declarations appear before `\begin{document}`.

## Compilation Workflow

### The Correct Build Sequence
```bash
pdflatex -interaction=nonstopmode main.tex    # Pass 1: build aux
bibtex main                                    # Resolve citations
pdflatex -interaction=nonstopmode main.tex    # Pass 2: resolve refs
pdflatex -interaction=nonstopmode main.tex    # Pass 3: stabilize
```

**Why 3 passes?** Pass 1 writes `.aux` with label/ref info. Pass 2 reads `.aux` and resolves forward references (may shift page numbers). Pass 3 stabilizes page numbers so refs to page numbers are correct.

### Checking for Issues
```bash
# Undefined references (should be 0)
grep -c "undefined" main.log

# Multiply-defined labels (should be 0)
grep "multiply" main.log

# Citation warnings
grep "Citation.*undefined" main.log

# Overfull boxes (cosmetic but worth checking)
grep "Overfull" main.log | wc -l
```

## Overleaf Git Workflow

### Safe Push Protocol
```bash
# Only stage source files (never build artifacts)
git add main.tex methods.tex experiments.tex references.bib
git commit -m "Descriptive message mapping to feedback"
git push  # Pushes to master; Overleaf syncs automatically
```

### Files to Never Commit
- `.aux`, `.bbl`, `.blg`, `.log`, `.out` — build artifacts
- `.pdf` — Overleaf rebuilds from source
- `.DS_Store` — macOS metadata
- `.synctex.gz` — editor sync file

### Handling Overleaf Conflicts
If someone edited on Overleaf while you worked locally:
```bash
git pull --rebase  # Rebase your changes on top of Overleaf's
# Resolve conflicts if any, then:
git push
```

## BibTeX Issues

### Duplicate Bibliography Entries
**Symptom**: `repeated entry` warning from BibTeX
**Fix**: Search for duplicate keys in `.bib`:
```bash
grep "^@" references.bib | sort | uniq -d
```

### Citation Undefined After First Pass
**Symptom**: `Citation 'smith2023' undefined` after pdflatex
**Cause**: Normal — citations resolve after bibtex + second pdflatex pass
**Fix**: Always run the full 4-command build sequence.

## Float Placement Issues

### Appendix Figures Drifting Into Bibliography
**Symptom**: A figure from the last appendix section appears between bibliography entries or after `\end{document}`.
**Cause**: `[h]` ("here if possible") and `[t]` ("top of page") are suggestions, not commands. LaTeX may place the float on the next available page — which can be the references page.
**Fix**: Use `[H]` (capital H, from `\usepackage{float}`) to force exact placement:
```latex
% Before (drifts):
\begin{figure}[t]

% After (stays put):
\begin{figure}[H]
```
**When to use**: Always for appendix figures near the end of the document. Main paper figures with `[t]` are usually fine because there's enough content afterward.

### Appendix Dead Code Accumulation
**Symptom**: Appendix file is 2x its rendered length due to commented-out blocks.
**Cause**: Iterative revision leaves behind old figures, derivations, and placeholder sections.
**Protocol**:
1. Count commented vs. active lines: `grep -c '^%' appendix.tex` vs `wc -l appendix.tex`
2. If >30% commented, do a cleanup pass
3. Delete: old alternate figures, superseded derivations, empty placeholder subsections ("Left to future work")
4. Keep: brief comments explaining design decisions, TODO markers with clear owners

## Text-Level Issues

### Math in Section Titles
**Symptom**: Bookmark warnings, broken PDF bookmarks
**Cause**: `$x = (q,p)$` in `\section{...}` confuses hyperref
**Fix**: Use `\texorpdfstring`:
```latex
\section{Problem: Learning from \texorpdfstring{$q$}{q}-only Data}
```

### Encoding Issues in Comments
**Symptom**: Mysterious errors near comments
**Cause**: Non-ASCII characters (curly quotes, em-dashes) in comments from copy-paste
**Fix**: Replace with ASCII equivalents: `---` for em-dash, straight quotes, etc.

## Quick Diagnostic Commands

```bash
# Full health check after revision
echo "=== Undefined refs ===" && grep -c "undefined" main.log
echo "=== Multiply defined ===" && grep "multiply" main.log
echo "=== Missing citations ===" && grep "Citation.*undefined" main.log
echo "=== Package warnings ===" && grep "Warning" main.log | grep -v "Font\|float\|size\|rerun" | head -10
echo "=== Page count ===" && grep "Output written" main.log
```
