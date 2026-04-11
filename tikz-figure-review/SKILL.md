---
name: tikz-figure-review
description: "Review and fix alignment, label collision, clipping, legend-over-data, overlap, and layout issues in TikZ and pgfplots figures inside LaTeX documents. Use when the user wants to review figures in a paper, tutorial, lecture notes, or thesis before submission; when a reviewer flags figure problems; when a rendered figure visibly has overlap, clipping, or label collisions; when setting up a per-figure review workflow across a large document; or when the user shows a screenshot of a figure that looks wrong. Trigger proactively whenever the user mentions figure alignment, TikZ layout, pgfplots legends/axes, figure cleanup, or asks to fix a figure — even if they don't explicitly say 'review'. Covers a fast iteration loop: extract each tikzpicture into a standalone, compile to PNG, fix, sync back to the main file."
version: 1.0.0
---

# TikZ / pgfplots Figure Review

You help the user review TikZ and pgfplots figures in LaTeX documents
and fix alignment, label collision, clipping, and legend-over-data
issues. This skill captures 11 failure modes learned from reviewing
40+ figures across two real documents, plus the extract-standalone
iteration workflow that makes per-figure fixes fast.

## 1. Workflow

The cheapest iteration loop is: **extract → standalone compile → PNG →
view → edit → repeat**, keeping the main document untouched until the
standalone is clean.

### 1.1 One-time setup (per project)

Create a working directory (e.g. `figures_check/`) with:

- `_preamble.tex` — mirrors the relevant packages, TikZ libraries,
  `pgfplots` compat version, and **all custom math commands** (`\grad`,
  `\Hp`, `\vq`, etc.) from the main document. Without these the
  standalone will fail with "undefined control sequence".
- One `figN_<name>.tex` per figure, using
  `\documentclass[border=8pt]{standalone}` and `\input{_preamble}`. The
  body is **only** the `\begin{tikzpicture} … \end{tikzpicture}` block —
  no caption, no `figure` environment.

Known pitfall: `pgfplots compat` mismatch. The main document may pin a
newer compat level than the local TeX install supports. Set the
preamble to the **lowest** compat that works on the local install (e.g.
1.17) and do **not** sync that one line back to the main document.

### 1.2 Per-figure compile / render

```bash
cd figures_check
pdflatex -interaction=nonstopmode figN_name.tex > figN_name.log 2>&1
pdftoppm -r 200 -png figN_name.pdf figN_name
# produces figN_name-1.png
```

200 dpi is enough to read labels; go to 300 dpi only for fine alignment
checks.

### 1.3 Parallel review

Once every standalone compiles and has a fresh PNG, dispatch review
subagents. Each subagent gets:

- The PNG path (to view via the Read tool).
- The standalone `.tex` path (for fast iteration).
- The **line range** in the main `.tex` (for syncing the fix back).
- Explicit instructions to edit **both** files and keep the
  `tikzpicture` body identical.
- A re-render command and a "max 3 iterations" cap.
- A pointer to this SKILL file as reference.

**Batching:** for <10 figures, one subagent per figure is fine. For 20+
figures, dispatch 5–7 subagents each handling 5–6 figures grouped
thematically (e.g. "all phase portraits", "all schematic pipelines").
Thirty-plus individual subagents is slow and noisy — batching gives
each subagent a coherent context without over-fragmenting.

Cross-references like `\eqref{eq:foo}` and `\ref{prop:bar}` will not
resolve inside a standalone. Tell subagents to use placeholders in the
standalone and **keep the original refs** when editing the main file.

### 1.4 Scaling to many-figure documents (20+ figures)

For large documents, don't hand-extract each tikzpicture — dispatch a
dedicated **extraction subagent** first. Give it:

- The main `.tex` path and a grep-verified list of `\begin{tikzpicture}`
  line numbers.
- A naming scheme (`figNN_semantic_label.tex`).
- The shared `_preamble.tex` path.
- Instructions to copy each tikzpicture **verbatim** (preserving
  indentation, comments, line breaks) into `\documentclass{standalone}`
  wrappers, and to run `pdflatex` + `pdftoppm` on all of them.

The extraction subagent will also surface **compile-blocking bugs** that
prevent the main document from building at all (see §2.8 for a classic
pgfplots `\foreach` bug). Tell it to fix any such bugs in the standalone
copy only, and report them so a review subagent can propagate the fix
back to the main file.

If figures `\addplot table {...}` from external `.dat` files, symlink
the data directory into the scratch dir rather than copying:
```bash
cd figures_check && ln -s ../phase-data phase-data
```

---

## 2. Common issues and canonical fixes

When reviewing a new figure, scan for these in the order listed in §3.
Each subsection gives the failure mode, a real example, and a canonical
fix.

### 2.1 Legend sits on top of data

By far the most common issue. `legend pos=north east` (the pgfplots
default) assumes the plot is roughly linearly rising — which is false
for convergence plots, curves that cluster near the top, or bar charts
whose tallest bar is near the right.

**Fix options, in order of preference:**

1. **Move legend outside the axis** — cleanest when there's horizontal
   room in the figure:
   ```tex
   legend style={font=\small, at={(1.02,1)}, anchor=north west}
   % or shorthand:
   legend pos=outer north east
   ```
2. **Raise `ymax`** — if the legend must stay inside, give it empty
   headroom:
   ```tex
   ymin=0, ymax=1.45   % was 1.1 — top bar was 1.0
   ```
3. **Compact the legend** — multi-column, smaller font (see
   `references/snippets.md`).
4. **Opaque legend** — last resort when the legend has to sit over
   low-density data (see `references/snippets.md`).

Pick the fix that preserves the most information. Prefer (1) if the
figure has room; (2) for bar charts where extra headroom is cheap; (3)
when a 4-entry legend is unavoidable; (4) only if nothing else fits.

### 2.2 Text label clipping a box, line, or marker

Two sub-cases:

**(a) A text node sits on the border of a dashed/solid enclosure.**
Seen in an IDA-PBC figure where the `u=-y_c` label and the energy-balance
labels were kissing the closed-loop rectangle.

- Enlarge the enclosure so labels fit fully inside.
- Move the label inward (shift further from the border).
- If the label belongs to an arrow passing through the border, switch
  the label to the **opposite side** of the arrow (`below` → `above`).
- Move captions/descriptions **clearly outside** the enclosure with
  whitespace (don't let them kiss the border).

**(b) A text label is hidden by the glyph it's annotating** (e.g. "min"
on top of a marker dot). This is the **single most common failure mode
on phase portraits**: equilibrium labels (`center` / `saddle` /
`source` / `sink` / `equil.`) placed directly on their marker dots.
Default `above` / `above right` anchors still draw the text touching
the dot. Split into two nodes and anchor the text explicitly:

```tex
\fill[black] (0,0) circle (2.5pt);
\node[font=\small, anchor=west] at (axis cs:0.15, 0.35) {min};
```

The trap: using the `node` option on `\fill` puts the label at the
dot's center anchor, so it sits exactly where the glyph is. Make them
separate and anchor the text. For a whole row of equilibrium labels,
`anchor=west` at `(x_dot + dx, y_dot + dy)` is more consistent than
`anchor=south` because it gives uniform horizontal offset regardless
of how tall the text is.

### 2.3 Bidirectional ports between two boxes → label collision

When two arrows run in the same channel between two nodes (e.g. Plant
⇄ Controller with `y` and `u=-y_c`), a single centered arrow with two
labels always collides. Split into **two parallel arrows** with
`xshift` offsets and opposite label sides:

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

Note the second draw uses `<-` to keep the arrowhead semantically at
the plant side while the label stays on the right.

### 2.4 A third arrow crossing the channel between two boxes

A "Task Oracle → Plant" arrow crossed the plant↔ctrl channel and
dragged its `g̃` label through the port labels. Two fixes combined:

- **Reposition the source node** so the crossing arrow enters from a
  clean edge (e.g. straight `plant.west`, not diagonal through the
  middle).
- **Free up the channel** for port labels only by moving other labels
  to the outside (§2.3).

If the source node is conceptually outside one group and the crossing
arrow must traverse a separator, give it enough horizontal room; push
boxes apart rather than letting an arrow squeeze through.

### 2.5 Notes beside a stack of boxes clip into the boxes

A column of annotation `\node[note]` entries at `x=5.3` with default
`anchor=center` extended from ~`4.3`, but the boxes ended at `x=4.0`.
Only 0.3 cm clearance, and the notes overlapped the box edges.

**Rule:** when placing text nodes next to the **edge** of another node,
always anchor the text on the side facing the reference node:

```tex
note/.style={font=\scriptsize, gray, align=left, anchor=west}
\node[note] at (4.25, 0) {…};   % box right edge at 4.0
```

Default `anchor=center` is correct when the text stands alone in empty
space; `anchor=west/east/north/south` is correct when it sits next to
an edge.

### 2.6 Dashed separators crossed by arrows or labels

Overlay/separator lines (e.g. "Classical GD | SHAPE") must be placed so
nothing arrow or label touches them. Either:

- Add horizontal slack between the separator and the boxes on each
  side, and
- Place the separator's own label (e.g. rotated "vs.") in the *empty*
  gap, not at the height of any arrow passing through.

### 2.7 `minimum width` is a minimum, not a cap — use `text width` for consistent stacked boxes

**Seen twice** on stacked pipeline diagrams. Both had

```tex
pstep/.style={draw, ..., minimum width=8cm, minimum height=0.75cm,
              align=center, font=\small}
```

and 5–6 stacked `pstep` nodes. The notes next to each box were
positioned at `x = 4.25` (just past the intended box-right-edge at
`x=4.0`). At 2cm of slack the layout *should* have been clean.

It wasn't: **`minimum width` only establishes a lower bound**. When a
node's content is wider than the minimum, the box grows. One long step
text forces that row's box wider than 8cm, and the annotation note —
positioned relative to the intended right edge — ends up *inside* the
actual box.

**Fix:** replace `minimum width` with `text width` so the text is
forced to wrap into a fixed-width column, making every box the same
size:

```tex
pstep/.style={draw, rounded corners=4pt, fill=blue!8,
              text width=9.2cm, minimum height=0.75cm, inner sep=4pt,
              align=center, font=\small}
```

`text width` is a hard ceiling — text that would exceed it wraps onto
a new line. `inner sep=4pt` adds internal padding so wrapped lines
don't touch the box border. Then place notes cleanly past the real
right edge (text width + inner sep + a small gap).

For a row of 6 stacked `pstep` nodes at 9.2 cm text width centered at
x=0:
- Real box extent: `x ∈ [-4.6, 4.6]` + inner sep
- Notes start at: `x = 5.05` (clear of right edge)

Also bump the vertical gap between rows if the wrapping turns a box
into two lines — otherwise rows collide.

### 2.8 pgfplots `\foreach` + `\addplot[\var, ...]` — macro not expanded

**Compile-blocking bug.** This pattern looks reasonable but fails:

```tex
\foreach \ra/\rb/\clr in {0.22/0.18/blue!80,
                          0.35/0.28/blue!60,
                          0.48/0.38/blue!40}{
  \addplot[\clr, thick, ...]  % ← \clr here is never expanded
    ({\ra*cos(x) + 0.35}, {\rb*sin(x)});
}
```

Error: `! Undefined control sequence. \pgfkeyscurrentkey ->\clr`.

The pgfplots key parser sees `\clr` as a literal key, not as a
`\foreach` loop variable. TikZ `\foreach` captures the text but
pgfplots' own `\pgfkeys` expands inside a different scope that does
not see the foreach variable.

**Fix:** unroll the loop into explicit `\addplot` calls with literal
colors:

```tex
\addplot[blue!80, thick, ...] ({0.22*cos(x)+0.35}, {0.18*sin(x)});
\addplot[blue!60, thick, ...] ({0.35*cos(x)+0.35}, {0.28*sin(x)});
\addplot[blue!40, thick, ...] ({0.48*cos(x)+0.35}, {0.38*sin(x)});
```

(An alternative `color=\clr` form also sometimes works, but unrolling
is the safe choice — it's explicit and won't regress on pgfplots
upgrades.)

Catch this early: when a full-document compile fails with this error,
the extraction phase should still produce a standalone for that
figure, and the standalone *will also fail to compile* until the
unroll is applied. Fix it in the standalone first, then propagate to
the main file.

### 2.9 3D axes and vectors project into the same screen direction

**Seen in a cross-product visualization.** The z-axis was drawn at
`z=(-0.45cm, 0.18cm)` per unit and the cross-product vector at
`(−0.5, 0.2, 2.6)` — both projected to essentially the same upper-left
screen direction. Their labels ended up literally touching: the
z-axis's `z` glyph fused with the cross-product label's `∇H` to read
as `∇H_z`.

This is a projection-space collision: two 3D directions that are
geometrically orthogonal can map to parallel screen vectors under the
wrong choice of `x`/`y`/`z` base vectors.

**Fix:** change the projection so each 3D axis maps to a distinct
screen direction. For an isometric-ish look:

```tex
x={(1.0cm, 0.25cm)},     % right + slightly down
y={(0cm, 1.0cm)},        % straight up
z={(-0.55cm, -0.30cm)}   % lower-left — NOT upper-left
```

Then the cross product (whichever direction it points geometrically)
will project into its own screen region with room for an annotation.

### 2.10 Labels inside a dashed/shaded enclosure get struck through by interior content

**Seen in a cofactor figure** — a "flow tangent to {g=0}" annotation
was placed inside the family of dashed level curves and got sliced by
the innermost contour. Interior content (level sets, grid lines,
arrows) creates a field that no in-plane label can live inside without
eventually being crossed.

**Fix:** move explanatory labels **outside** the content region, below
or above the enclosure, so they read as captions-for-the-region rather
than as items embedded in it. Use a leader line if you need to point
at something specific.

### 2.11 Arrow paths crossing through other labels or boxes

**Seen in a metriplectic ingredients figure.** Two arrows (`\dot H = 0`
and `\dot S ≥ 0`) were drawn from a central bracket's east edge and
passed through a dashed compatibility box on their way to their
labels. The fix was to reroute both arrows to exit from a different
edge (`node.south`) into empty space below the figure.

**Rule:** when drawing an arrow out of a node, check the straight-line
path to its target against every other box/label on the canvas. If it
passes through anything, either (a) route via a polyline that detours
around the obstacle, or (b) pick a different edge of the source node
so the straight-line path is clear.

---

## 3. Review checklist

Scan each rendered figure for these, in order. Stop at the first "yes"
and fix before moving on — fixes can change what other issues look
like.

1. Is any axis label, title, or tick label clipped or cut off?
2. Does the legend box overlap any data curve, bar, or marker?
3. Does any text node sit on top of a marker dot, another node, or on
   the border of an enclosure (rectangle, ellipse, group)?
4. **Phase portrait specific:** are equilibrium labels
   (`center`/`saddle`/`source`/`sink`/`equil.`) touching their marker
   dots? (§2.2b — the single most common phase-portrait failure mode.)
5. In figures with two boxes and a bidirectional port: are the two
   labels distinguishable, or are they bunched on top of each other?
6. Do crossing arrows drag their labels through other labels?
7. Do annotation notes next to a stack of boxes clip into the stack's
   edges? (`anchor=center` footgun + `minimum width` not being a cap.)
8. Are markers at axis extremes (`xmin`/`xmax`/`ymin`/`ymax`) clipped
   in half?
9. Is there a separator line / region divider that touches any arrow
   or label?
10. **3D diagrams:** do any two 3D vectors project into the same screen
    direction, causing their labels to fuse?
11. **Dashed enclosures:** do any interior labels get struck through
    by content curves/level sets inside the enclosure?
12. **Pipelines / stacks:** do boxes vary in width because their text
    exceeds `minimum width`? (§2.7 — switch to `text width` for
    consistent sizing.)

---

## 4. Copy-paste snippets

A catalog of the code patterns for each failure mode lives in
`references/snippets.md`. Load it when you need to grab a specific
pattern (parallel port arrows, legend-outside-plot, text-width stacked
boxes, 3D projection template, unrolled `\foreach`, etc.) rather than
re-deriving each time.

---

## 5. Pitfalls specific to this workflow

- **Custom macros.** Don't forget to copy `\grad`, `\Hp`, `\Hc`, `\vq`,
  `\R`, `\md`, and any other user-defined command into the standalone
  preamble. The failure mode is a cryptic "Undefined control sequence"
  several seconds into compile.
- **pgfplots compat mismatch.** The standalone preamble should pin the
  compat level your local TeX supports. Do **not** sync that line back
  to the main document.
- **Cross-references (`\eqref`, `\ref`).** These will never resolve in
  a standalone. Use a short placeholder text locally, keep the
  original macros when editing the main file.
- **Subtle sync drift.** After editing in the standalone, diff the two
  `tikzpicture` bodies before declaring victory. It's easy to forget
  one file.
- **Don't delete standalone files.** Keeping them around means the
  next reviewer has a working scaffold — they only have to re-run
  `pdflatex` and look.
- **Subagents may be blocked from running `pdflatex`.** In some
  harness configurations, subagents can `Read`/`Edit` files but cannot
  invoke bash commands (even with `dangerouslyDisableSandbox=true`).
  When this happens, subagents will edit standalone and main files
  symmetrically but won't be able to verify their fix. **The driver
  must re-render** every file each subagent edited and inspect the
  PNG. Brief the subagents up front that they may be blocked, and
  that in that case they should still make their best-guess edits and
  flag them for driver verification.
- **`text width` vs `minimum width` for stacked boxes.** `minimum
  width` is a lower bound, not a cap — use `text width` when you need
  every box in a stack to be the same size regardless of content.
  Bitten twice (§2.7).

---

## 6. Minimal re-render recipe

After any edit to a standalone:

```bash
cd figures_check
pdflatex -interaction=nonstopmode figN_name.tex > /dev/null \
  && pdftoppm -r 200 -png figN_name.pdf figN_name
# then view figN_name-1.png
```

Three iterations should be enough for any single figure. If you're on
iteration four, step back and reconsider the layout as a whole, not
tweak another parameter.
