# Beamer implementation notes

Use this reference when the requested output is a LaTeX Beamer walkthrough.
It records layout and notation failures that can survive a successful compile.

## Establish one shared overview

Build one macro for the system map, parameterized by the active block. Use fixed
node positions and a fixed bounding box, then vary emphasis. Render the all-active
view and one focused view before repeating them across the deck.

Use named colors and semantic wrappers for matching equation fragments. Keep the
palette independent of the particular research domain. A small navigation rail
or miniature map is useful only if it preserves orientation without crowding the
content.

For an initial layout, 16:9 with top-aligned frames is often practical:

```latex
\documentclass[aspectratio=169,11pt,t]{beamer}
\usepackage{amsmath,tikz}
\usetikzlibrary{arrows.meta,positioning,calc}
\definecolor{processblue}{RGB}{35,89,140}
\newcommand{\process}[1]{\textcolor{processblue}{#1}}
\tikzset{processbox/.style={
  draw=processblue,rounded corners=2pt,
  text width=3cm,align=center,inner sep=5pt}}
```

These are starting values, not a required theme. Fit the content to the slide
by simplifying or splitting it before shrinking the whole diagram.

## Keep recurring formulations synchronized

Use a second shared macro for the compact formulation and its matching process
blocks, parameterized by the active row or group of rows. Keep the same content
and coordinates on opening, intermediate and closing appearances. Vary emphasis
and the teaching question, not the row order. This prevents equations drifting
apart as separately copied slides are edited.

Place the equations on one side and corresponding named blocks on the other,
with consistent colors. Simple connecting lines can show correspondence; reserve
arrowheads for an actual direction of flow. Keep fuller input/output explanations
in the block-expansion slides when repeating them would crowd this view.

Render one focused view and the fully emphasized closing view before propagating
the macro. Check the longest equation and label. A node's minimum height is not a
height cap: a wrapped subtitle can make it overlap neighboring fixed rows. Shorten
the block label, remove redundant subtitles or increase row spacing rather than
shrinking the whole figure. A compact objective may use text-style operators if
legible; keep an expanded version for detailed derivation.

Review the recurring pages consecutively after final compilation. Their matching
rows should not move when the title, emphasis or explanatory sentence changes.
If movement is hard to judge visually, compare the rendered positions of a shared
text anchor or diagram boundary. Preserve room below the shared view for the
longest explanation and footer.

## Overlay and geometry traps

- Give nodes a `text width`; `minimum width` does not constrain long labels.
  Shorten or deliberately break headings rather than accepting prominent
  automatic hyphenation.
- Opposite port directions need separate arrows and separate labels. Route
  arrows to the receiving boundary; never let a path enter a box, travel inside
  it, then point outward through another edge.
- Keep return-loop labels clear of arrowheads and final approach segments.
  Render the muted version too: a label background can hide a faint arrow.
- TikZ `foreach` creates local scopes. Per-block emphasis values needed after
  the loop must persist or be computed where they are used; do not rely on a
  local definition surviving the loop.
- Reserve space for unrevealed equations with `\uncover` or a fixed overlay area
  when positions should remain stable. `\only` removes hidden content and can
  move everything below it. Preview every reveal, not just the final one.
- Do not use opacity so low that the context disappears entirely. Names,
  orientation and the active block's immediate neighbors should remain findable.
- End a diagram or table paragraph before adding vertical space and prose:

  ```latex
  \end{tikzpicture}
  \par\vspace{2mm}
  A sentence explaining the diagram.
  ```

  Without the paragraph break, the first word may appear beside the diagram,
  while vertical spacing is inserted into an unintended line.
- Reserve footer space. A custom footer should fit within `\paperwidth`; use
  explicit non-discardable end margins where needed, and inspect page numbers.

## Protect equations while coloring them

Color wrappers do not change mathematical grouping. To subtract a colored sum:

```latex
\newcommand{\loss}[1]{\textcolor{red!70!black}{#1}}
\[
\dot E=\loss{-d_1-d_2-d_3}\le0
\qquad\text{or}\qquad
\dot E=-\bigl(\loss{d_1+d_2+d_3}\bigr)\le0.
\]
```

Check the actual displayed signs after reveal macros and color changes. Keep
each overlay syntactically valid when hiding parts of an aligned equation.
Break a long equation deliberately inside a narrow column instead of relying
on compilation warnings to catch it.

## Build, inspect, and deliver

Use the available TeX toolchain and installed package versions. For example:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build slides.tex
pdftoppm -r 180 -png build/slides.pdf build/slide
```

Use another available PDF renderer if needed. On macOS, MacTeX binaries may be
in `/Library/TeX/texbin` even when the noninteractive shell cannot find them.
Use a supported pgfplots compatibility version; do not upgrade the environment
solely to render simple diagrams.

Check compile errors, overfull boxes and page bounds, then inspect the rendered
pages. A clean log does not detect misleading arrows, wrong signs, or words
placed beside a figure. Repeated overview defects belong in the shared macro.

Keep audience slides distinct from speaker notes. Provide the editable TeX and
any required local assets, plus a small rebuild command or script when useful.
Report both frame count and PDF page count if overlays make them differ.
