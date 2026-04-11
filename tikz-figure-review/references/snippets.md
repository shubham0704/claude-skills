# Copy-paste snippets for TikZ / pgfplots figure review

Load this file when you need to grab a specific pattern. Indexed by
failure mode from `SKILL.md §2`.

## Offset an arrow endpoint along a node edge (§2.3)

Use `xshift` / `yshift` on a coordinate reference to push the arrow
endpoint away from the exact edge center. Essential for parallel
arrows between two stacked nodes.

```tex
([xshift=-5pt]node.south)
([yshift=0.4cm]node.east)
```

## Parallel port arrows between two vertically stacked boxes (§2.3)

Two ports between the same pair of nodes. Split into two arrows, each
offset in x, each with its label on the outer side so they never
collide.

```tex
\draw[->, blue!70!black, thick]
  ([xshift=-5pt]plant.south) --
  node[left, font=\scriptsize]{$y = G^T\!\grad H_p$}
  ([xshift=-5pt]ctrl.north);
\draw[<-, orange!70!black, thick]
  ([xshift=5pt]plant.south) --
  node[right, font=\scriptsize]{$u = -y_c$}
  ([xshift=5pt]ctrl.north);
```

The second draw uses `<-` so the arrowhead lands at the plant side
while the label stays on the right.

## Legend outside the plot area (§2.1)

```tex
legend style={font=\small, at={(1.02,1)}, anchor=north west}
```

or the shorthand:

```tex
legend pos=outer north east
```

## Multi-column legend with tight spacing (§2.1)

```tex
legend style={font=\footnotesize,
              legend columns=2,
              /tikz/every even column/.append style={column sep=4pt}}
```

## Translucent legend — data stays visible underneath (§2.1)

Last-resort when the legend has to sit over low-density data. White
fill with 0.9 opacity keeps the legend readable while letting the
curves show through.

```tex
legend style={at={(0.98,0.98)}, anchor=north east,
              font=\footnotesize, fill=white, fill opacity=0.9,
              draw opacity=1, text opacity=1, row sep=-1pt}
```

## Anchor a label next to a marker without covering it (§2.2b)

Split the marker and its label into two separate nodes. Never use the
`node` option on `\fill` — it anchors the label at the dot's center
and buries the text under the glyph.

```tex
\fill[black] (0,0) circle (2.5pt);
\node[font=\small, anchor=west] at (axis cs:0.15, 0.35) {min};
```

For a row of equilibrium labels on a phase portrait, keep all labels
at the same `anchor=west` with a uniform `(dx, dy)` offset from their
dots — more consistent than `above` anchors.

## Edge-anchored annotations beside a column of boxes (§2.5)

Default `anchor=center` places the label centered on the reference
point, which bleeds back into a nearby box. Use an edge anchor facing
the reference node.

```tex
note/.style={font=\scriptsize, gray, align=left, anchor=west}
\node[note] at (<x just past box right edge>, <box y>) {...};
```

## Dashed enclosure with inside-label padding (§2.2a)

```tex
\draw[dashed, gray, rounded corners=8pt]
  (<xmin>, <ymin minus padding>) rectangle (<xmax>, <ymax>);
% Then keep all inner labels at least 0.3 cm from each edge.
```

Caption-style descriptions for the whole enclosure go **outside**, not
on the border (§2.2a).

## Consistent-width stacked pipeline boxes — `text width`, not `minimum width` (§2.7)

`minimum width` is a lower bound, so boxes grow past it when content
is long, and any note positioned relative to the intended edge ends
up inside the real box. `text width` is a hard ceiling — text wraps
instead of expanding the box.

```tex
pstep/.style={draw, rounded corners=4pt, fill=blue!8,
              text width=9.2cm, minimum height=0.75cm, inner sep=4pt,
              align=center, font=\small},
note/.style={font=\scriptsize, gray, align=left, anchor=west}
% Boxes centered at x=0 → right edge at 4.6 + inner sep ≈ 4.64
% Notes at x=5.05 give ~0.4 cm visual gap
\node[pstep] (s1) at (0, 0)   {Step 1: ...};
\node[pstep] (s2) at (0,-1.1) {Step 2: ...};
\node[note]  at (5.05, 0)   {annotation 1};
\node[note]  at (5.05,-1.1) {annotation 2};
```

If wrapping turns a box into two lines, bump the vertical gap between
rows — otherwise rows collide.

## Unrolled `\foreach` substitute for pgfplots style loops (§2.8)

pgfplots does not expand `\foreach` loop variables inside `\addplot`'s
key list, so this looks reasonable but fails with
`Undefined control sequence \clr`:

```tex
% WRONG:
% \foreach \ra/\rb/\clr in {0.22/0.18/blue!80, 0.35/0.28/blue!60}{
%   \addplot[\clr, thick, ...] (...);
% }
```

Unroll explicitly with literal colors:

```tex
\addplot[blue!80, thick, domain=0:360, samples=180]
  ({0.22*cos(x)+0.35}, {0.18*sin(x)});
\addplot[blue!60, thick, domain=0:360, samples=180]
  ({0.35*cos(x)+0.35}, {0.28*sin(x)});
```

## 3D projection keeping all three axes in distinct screen directions (§2.9)

Default `x=(1,0)`, `y=(0,1)`, `z=(-0.45, 0.18)` puts both `+z` and
many cross-product vectors in the same upper-left screen region,
causing label fusion. Send `z` to the lower-left instead.

```tex
\begin{tikzpicture}[
    x={(1.0cm, 0.25cm)},     % right + slightly down
    y={(0cm, 1.0cm)},        % straight up
    z={(-0.55cm, -0.30cm)}   % lower-left — NOT upper-left
]
  \draw[->] (0,0,0) -- (3.6,0,0) node[right] {$x$};
  \draw[->] (0,0,0) -- (0,2.8,0) node[above] {$y$};
  \draw[->] (0,0,0) -- (0,0,2.4) node[below] {$z$};
\end{tikzpicture}
```

## Standalone preamble skeleton (§1.1)

For the `_preamble.tex` file in `figures_check/`. Copy the main
document's packages, tikz libraries, and **all** custom math commands.

```tex
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{mathtools}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,calc,positioning,shapes.geometric,
                decorations.pathreplacing,fit,backgrounds}
\usepackage{pgfplots}
\pgfplotsset{compat=1.17}   % lowest your local TeX supports
\pgfplotsset{every axis plot/.append style={line width=0.8pt}}

%% Mirror of custom math commands — copy every \newcommand the main
%% document defines that's used inside any tikzpicture.
\newcommand{\grad}{\nabla}
\newcommand{\R}{\mathbb{R}}
\newcommand{\vq}{\mathbf{q}}
% ... add the rest here
```

## Standalone wrapper skeleton (§1.1)

For each `figN_name.tex`:

```tex
\documentclass[border=8pt]{standalone}
\input{_preamble}
\begin{document}
<EXACT copy of the \begin{tikzpicture} ... \end{tikzpicture} block>
\end{document}
```

No `\begin{figure}`, no `\caption`, no `\label`. Cross-references
inside tikz nodes (`\eqref{eq:foo}`, `\ref{prop:bar}`) get replaced
with short placeholder text in the standalone — **keep the originals
in the main file**.
