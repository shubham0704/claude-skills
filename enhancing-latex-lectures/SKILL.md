---
name: enhancing-latex-lectures
description: Enhances LaTeX lecture notes by analyzing pedagogical reference materials (like Todorov's PDFs) and systematically adding stunning visualizations, concrete examples, and intuitive explanations. Use when the user requests improving lectures, adding visualizations from papers, or adopting another author's teaching style.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash, TodoWrite
---

# Enhancing LaTeX Lectures with Pedagogical Excellence

This Skill helps you systematically enhance LaTeX lecture notes by analyzing exemplary pedagogical materials and incorporating their best practices—especially stunning visualizations, concrete-to-abstract progressions, and multiple perspectives on concepts.

## When to Use This Skill

Invoke when the user:
- Asks to "enhance lecture X with visualizations from [author/paper]"
- Wants to "add [author]'s teaching approach" to materials
- Requests "beautiful diagrams" or "stunning visualizations" from reference PDFs
- Says "compare our examples vs [author]'s examples"
- Wants to systematically improve multiple lectures

## Core Methodology

### Phase 1: Analyze Reference Material

1. **Read the reference PDF/paper carefully** (use Read tool for PDFs)
2. **Identify stunning visualizations** by page number:
   - 3-panel comparisons showing multiple perspectives
   - Spacetime heatmaps (state × time evolution)
   - Convergence plots with quantitative comparisons
   - Geometric interpretations (simplex diagrams, phase portraits)
   - Side-by-side method comparisons
3. **Extract pedagogical patterns**:
   - Concrete examples before abstract theory
   - Quantitative validation (R² values, error metrics)
   - "Why this matters" insight boxes
   - Common pitfall warnings
4. **Note specific page numbers** for attribution

### Phase 2: Create Enhancement Plan

Create a **structured enhancement plan** with 4-6 additions:

```markdown
## Enhancement Plan for Lecture X

**Enhancement 1: [Concept] Visualization**
- From [Author] Page X
- What: [3-panel diagram / heatmap / etc.]
- Why: [Highest conceptual impact / most stunning / etc.]
- Where: After line Y in section Z

**Enhancement 2: ...**
[Repeat for each enhancement]
```

**Prioritization criteria**:
- HIGHEST conceptual impact (choose 1-2)
- Most stunning visually (choose 1-2)
- Concrete examples that ground abstract theory
- Quantitative validation of claims

### Phase 3: Implementation

For each enhancement:

1. **Find insertion point** using Grep/Read
2. **Add subsection** with descriptive title (e.g., "3.2a Understanding the KL Divergence Cost")
3. **Implement visualization** with proper TikZ/PGFPlots syntax
4. **Add insight boxes** using tcolorbox:
   - `\begin{tcolorbox}[colback=blue!5,colframe=blue!75!black,title={...},sharp corners,enhanced]`
   - Colors: blue (theorems), green (results), purple (insights), orange (algorithms)
5. **Attribute source**: "Source: [Author]'s [Document] (page X)"

### Phase 4: Compilation & Debugging

1. **Compile after EACH enhancement**: `pdflatex -interaction=nonstopmode lecture_X.tex`
2. **If errors occur**:
   - Check for unescaped underscores (`_` → `\_`)
   - Verify tcolorbox has `enhanced` option
   - Check for balanced braces in titles
   - Ensure `\addlegendentry` not `\addlegend` in pgfplots
   - Add missing packages to preamble if needed
3. **Track progress** with TodoWrite tool
4. **Report final page count and file size**

## Visualization Patterns to Implement

### Pattern 1: Three-Panel Comparisons
**Use when**: Showing same concept from three perspectives

```latex
\begin{tikzpicture}[scale=1.0]
\begin{scope}[shift={(0,0)}]
  % Panel 1
  \node[above, font=\large\bfseries] at (3, 4.8) {Perspective 1};
  \begin{axis}[...]
    \addplot3[surf] {...};
  \end{axis}
\end{scope}

\begin{scope}[shift={(7,0)}]
  % Panel 2
\end{scope}

\begin{scope}[shift={(14,0)}]
  % Panel 3
\end{scope}
\end{tikzpicture}
```

### Pattern 2: Spacetime Heatmaps
**Use when**: Showing evolution over state and time

```latex
\begin{axis}[
    width=5cm, height=4cm,
    xlabel={State $x$},
    ylabel={Time $t$},
    colormap/viridis,
    view={0}{90},
    colorbar,
]
\addplot3[surf, shader=interp, samples=25] {function(x,y)};
\end{axis}
```

### Pattern 3: Convergence Comparisons
**Use when**: Comparing algorithm performance quantitatively

```latex
\begin{axis}[
    ymode=log,
    xlabel={Iteration},
    ylabel={Error},
    legend pos=north east,
]
\addplot[thick, blue, mark=*] coordinates {(0,10) (10,1) (20,0.1)};
\addlegendentry{Method 1}

\addplot[thick, red, mark=square*] coordinates {(0,10) (50,1) (100,0.1)};
\addlegendentry{Method 2}
\end{axis}
```

### Pattern 4: Insight Boxes
**Use when**: Explaining WHY something matters

```latex
\begin{tcolorbox}[colback=purple!5,colframe=purple!70!black,
  title={\textbf{WHY THIS MATTERS}},sharp corners,enhanced]

\textbf{Key insight:} [One-sentence revelation]

\begin{itemize}
  \item \textbf{Computational:} [Practical benefit]
  \item \textbf{Conceptual:} [Theoretical insight]
  \item \textbf{Historical:} [Connection to prior work]
\end{itemize}

\textbf{Trade-off:} [What you give up]
\end{tcolorbox}
```

## Pedagogical Principles (from Todorov's Style)

**Concrete-to-Abstract**: Always provide a specific example before general theory
- ✓ "Coin biasing: p*=0.62 balances target 0.7 vs KL cost"
- ✗ "KL divergence penalizes deviation from passive dynamics"

**Multiple Perspectives**: Show the SAME concept in 3+ ways
- Algebraic equation
- Geometric visualization
- Physical intuition
- Computational algorithm

**Quantitative Validation**: Never make claims without numbers
- R² correlation values
- Mean/max error percentages
- Speedup factors (5×, 13×, etc.)
- Convergence iteration counts

**Stunning Visuals**: Prioritize visualizations that make you say "wow"
- 6-panel spacetime heatmaps showing noise effects
- Rainbow colormaps (viridis, plasma, cool)
- Side-by-side comparisons with identical scales
- Scatter plots with regression lines

## Common LaTeX Pitfalls & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Undefined control sequence \T` | Missing macro | Add `\newcommand{\T}{\top}` to preamble |
| `\addlegend` not found | Wrong pgfplots command | Use `\addlegendentry{}` |
| `Unescaped _` in text | Underscore in filename | Escape: `Lecture\_19.tex` |
| `Missing } inserted` in tcolorbox | Missing `enhanced` option | Add `,enhanced]` to options |
| `compat=1.18 unknown` | Old TeX installation | Use `\pgfplotsset{compat=1.17}` |
| `Incomplete \ifx` in foreach | Missing `\relax` | Add after `\numexpr\i+1\relax` |

## Output Format

After implementing all enhancements, provide:

```markdown
## Summary: Enhanced Lecture X

**Enhancements added**: 5

**Enhancement 1: [Title]** (lines A-B)
- From [Author] Page X
- Added: [3-panel diagram / heatmap / etc.]
- Key insight: [What students learn]

[Repeat for each]

**Compilation**: ✅ SUCCESS
- File: lecture_X.pdf
- Pages: 45
- Size: 627 KB
- Errors: 0
```

## Progressive Disclosure

For detailed examples of successful enhancements, see:
- `EXAMPLES.md` - Complete implementations from Lectures 16, 17, 19
- `VISUALIZATION_GALLERY.md` - All visualization patterns with code

## Testing & Validation

Before marking complete:
- [ ] All enhancements compile without errors
- [ ] Each visualization has proper attribution
- [ ] Insight boxes explain WHY concepts matter
- [ ] At least one quantitative comparison included
- [ ] Final PDF page count reported
- [ ] TodoWrite used to track progress
