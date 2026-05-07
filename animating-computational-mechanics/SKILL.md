---
name: animating-computational-mechanics
description: "Animate continuum mechanics, tensor calculus, and finite element concepts — deformation gradients, polar decomposition, Cauchy/Piola–Kirchhoff stresses, weak form, mesh convergence — using Matplotlib (FuncAnimation), Manim (ValueTracker / apply_function / Transform), or Blender (bpy + ParaView .obj pipeline). Use when the user wants to make a video for a lecture, paper, or supplement that animates a mechanics concept; when a static figure is failing to convey time evolution or deformation; when the user references the Flaschel 2026 / DrSimulate gallery; when importing FEM simulation results into Blender for photoreal rendering. Trigger proactively if the user mentions animating F, tractions, the weak formulation, or 'making this figure move'. Distilled from Flaschel, *Computer Applications in Engineering Education* 2026 (open access)."
version: 0.1.0
---

# Animating Computational Mechanics

You help the user produce **pedagogical animations of computational mechanics** — continuum kinematics, tensor calculus, and the finite element method — using one of three open-source toolchains: Matplotlib, Manim, or Blender. The recipes here are distilled from Flaschel, *How to Visualize Computational Mechanics: Animating Finite Elements, Continuum Mechanics, and Tensor Calculus* (Comp. Applic. in Engineering Education, 2026; open access; gallery at <https://github.com/DrSimulate/gallery>).

The skill is a decision tree (which tool?) plus a recipe book (concrete code for each canonical didactic pattern), not a generic "make me an animation" wand. Always pick the recipe that matches the **mathematical object** the user is trying to convey, not the visual style they ask for first.

## 1. When to use

Invoke when the user:

- Says "animate F", "show the deformation gradient acting on a unit circle", "rotate the stress tensor", "morph the reference into the deformed configuration".
- Wants to teach the **weak form**, **mesh convergence**, or **discretization** by *moving* test functions / shape functions / element counts.
- Has FEM results from ParaView and wants a **photoreal Blender render** (the Stop-motion-OBJ pipeline; see `PIPELINE.md`).
- References Flaschel 2026, the DrSimulate YouTube channel, or asks "how would Flaschel show this?".
- Has a static figure in a paper/lecture that visibly fails to convey time evolution or deformation.

Do **not** invoke for static figure cleanup (`tikz-figure-review`), for adding still visualizations to lecture notes (`enhancing-latex-lectures`), or for non-mechanics animations.

## 2. Tool selection

The three tools are *not* interchangeable. Pick the one whose primitive matches the mathematics:

| Tool | Native primitive | Use when | Cost |
|------|-----------------|----------|------|
| **Matplotlib** (`FuncAnimation`) | per-frame replot of a 2D/3D scene | Vector fields on a sphere or cube, line plots that evolve, simple 3D scenes with vectors, anything where the data is already in NumPy arrays. | Fastest to write. Renders to MP4/GIF. No surface shading. |
| **Manim** (`Scene` + `ValueTracker` / `Transform` / `apply_function`) | parameter-driven smooth tweening | Geometric morphing (reference → deformed config), continuous variation of a tensor's components, equation algebra animations, anything where smooth interpolation is the message. | Steeper. Renders MP4. Built for math exposition (LaTeX-native, smooth tweens). |
| **Blender** (`bpy` Python API + Stop-motion-OBJ add-on) | per-vertex mesh deformation with surface shading | Photoreal renders for the hero figure of a paper, importing real FEM simulation results, anything where surface texture / lighting carries pedagogical weight. | Highest setup cost. Best output. Requires Blender 4.5 + Stop-motion-OBJ. |

**Default ladder:** start with Matplotlib (cheap to iterate). Move to Manim when the message is *smoothness* or *parametric continuity*. Reach for Blender only when realism is the point or you have ParaView FEM output to bring in.

Software versions used in Flaschel 2026 — pin these in your script preamble:

- Matplotlib `3.10.1`
- ManimCE `0.18.1`
- Blender `4.5`

## 3. Workflow

The cheapest iteration loop is: **write a small Python script → render → view a single frame → fix → re-render**. Don't render the full video on every iteration; use a `--frames 5` flag or `interval` short-circuit while debugging.

### 3.1 Setup

Animations live next to the artifact they support, not in `~/`. For a paper:

```
paper/
  figures/
    f04_deformation_gradient.tex        # static fallback for print
    f04_deformation_gradient.py         # animation source
    f04_deformation_gradient.gif        # animated version (web supplement)
```

For lecture notes, mirror the gallery layout:

```
lecture_07_kinematics/
  src/
    01_F_unit_circle.py
    02_polar_decomposition.py
    03_stress_traction_sphere.py
  out/
    01_F_unit_circle.mp4
    ...
```

### 3.2 Per-animation iteration

1. **Pick the recipe** in `RECIPES.md` that matches the mathematical object.
2. **Stub the data** with placeholder NumPy arrays so you can see *something* render in 30 seconds.
3. **Render 5 frames** at low resolution to check composition (axes, colors, labels).
4. **Render full sequence** at the target resolution only once composition is right.
5. **Save in two formats**: MP4 for embedding, GIF or first-frame PNG for the LaTeX `\includegraphics` fallback.

### 3.3 Embedding in LaTeX

The static-fallback pattern Flaschel uses (papers can't embed video):

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=0.9\linewidth]{figures/f04_deformation_gradient.png}
  \caption{Animation of the deformation gradient acting on a unit
    circle. For the animated version, see
    \url{https://github.com/.../gallery}.}
  \label{fig:F-circle}
\end{figure}
```

For Beamer slides, use `\animategraphics` from the `animate` package on the GIF frames, or embed the MP4 directly with `media9`.

## 4. Didactic patterns (decision table)

Map the mechanics concept to the recipe in `RECIPES.md`:

| Mathematical object | Recipe | Tool |
|--------------------|--------|------|
| Stress tensor $\sigma_{ij}$ on infinitesimal sphere — six tractions | R1 | Matplotlib |
| Stress tensor on infinitesimal cube — column-as-traction | R1b | Matplotlib |
| Nonlinear motion mapping $x = \varphi(X, t)$ — reference→deformed morph | R2 | Manim |
| Deformation gradient $F$ acting on a unit circle of line elements | R3 | Manim or Matplotlib |
| Polar decomposition $F = RU$ — stretch then rotate | R4 | Manim |
| Cauchy / 1st PK / 2nd PK on rotating area element (Nanson's formula) | R5 | Matplotlib or Manim |
| FEM shape function basis $u(x) \approx \sum u_i N_i(x)$ — slider over $u_i$ | R6 | Manim (`Variable`) |
| Mesh convergence — overlay analytical + FE solutions, increase $n$ | R7 | Matplotlib |
| FEM results imported from ParaView, photoreal Blender render | R8 | Blender (see `PIPELINE.md`) |
| Imposed motion mapping on a textured Blender object | R9 | Blender |
| **Basis-rotation invariance — the keystone (tensor vs. matrix)** | **R10** | **Manim** |

Every recipe has the same shape: **(i) prepare data, (ii) define `animate(frame)` or `Scene.construct`, (iii) write to disk**. Recipes are in `RECIPES.md`.

## 5. Didactic principles (from Flaschel)

These are *load-bearing* — each one prevents a specific failure mode in a mechanics animation:

1. **Animate the geometric object, not the equation.** A tensor's meaning lives in what it does to a geometric primitive (line element, area element, sphere). Show $F$ deforming a circle, not the entries of the matrix changing on screen.
2. **Vary the basis to expose invariance.** Once an animation works in one Cartesian frame, *re-render it in a rotated frame* to show the components change but the geometry doesn't. This single move converts "tensor = matrix" into "tensor = invariant object". (R3 + R4.)
3. **Use the infinitesimal element as the visual unit.** Stresses become tractions on a tiny sphere or cube; strains become deformations of a tiny circle or square. The animation's visual scale should make this *small element* central, not the macroscopic body.
4. **Show the right Cauchy / 1st PK / 2nd PK distinction *physically*** — three side-by-side area elements with their tractions, not three matrices on a slide. (R5, after Flaschel Fig. 9.)
5. **For FEM, animate the discretization itself.** Refine the mesh in front of the viewer, with the analytical solution held fixed in white and the FE approximation shown in yellow converging to it. (R7, after Flaschel Fig. 11.)
6. **Continuous parameter sliders beat discrete snapshots.** Manim's `ValueTracker` is purpose-built for this. Use it for parameterized solution functions, varying $u_i$, and the Flory volumetric–isochoric split.

## 6. The ParaView → Blender pipeline (callout)

Worth highlighting because it's non-obvious and it's the workflow that turns a real FEM result into a paper-ready hero figure:

1. Run the FEM simulation in ParaView (or whatever solver outputs VTK).
2. Export the mesh **as a sequence of `.obj` files**, one per timestep.
3. In Blender 4.5, install the **Stop-motion-OBJ** add-on (<https://github.com/neverhood311/Stop-motion-OBJ>).
4. Import the `.obj` sequence as a single mesh that swaps geometry per frame.
5. Apply Blender materials, lighting, and Cycles rendering.

Full procedure in `PIPELINE.md`. This is what produces the dog-bone tensile-test render in Flaschel Fig. 4c.

## 7. Common pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| Animation freezes on first frame | `FuncAnimation` lost reference; Python GC'd it | Bind to a name: `ani = FuncAnimation(...)` then `ani.save(...)` |
| Saved video is blank / black | Forgot `ax.cla()` between frames, or saved before `ani` finished | Call `ax.cla()` at the top of `animate()`; save with `dpi`, `bitrate=-1` |
| Manim `Transform` ignores the function | `Transform` is for *predefined* shape pairs | Use `apply_function(lambda X: phi(X, t))` for arbitrary motion mappings |
| Blender import shows only first frame | Stop-motion-OBJ add-on not enabled | Edit → Preferences → Add-ons → enable Stop-motion-OBJ; reload `.blend` |
| Tensor "rotation" looks wrong in 3D | Camera elevation/azimuth changing along with rotation | Lock camera (`ax.view_init(elev=20, azim=-60)`) and rotate the *object* |
| GIF too large to embed | Default 100 fps × 200 dpi | `fps=15`, `dpi=80` for previews; pick MP4 for final |
| `bpy` script "works" but no mesh | Script ran in headless Python, not Blender's interpreter | Run with `blender --background --python script.py` or paste into Blender's Text Editor |
| FEM `.obj` sequence misaligned in Blender | Per-frame meshes have different vertex counts | Stop-motion-OBJ supports this; native Blender shape-key approach does not |

## 8. Output format

When you finish an animation task, report:

```
## Animation: <one-line description>

- Tool: Matplotlib | Manim | Blender
- Recipe: R<n> from RECIPES.md
- Files:
  - <path>.py      (source)
  - <path>.mp4     (full-res, <duration>s, <size>)
  - <path>.png     (first frame, for LaTeX fallback)
- Mechanics object animated: <e.g. "deformation gradient F on unit circle">
- Invariance check: <yes / no — did you re-render in a rotated frame?>
```

The invariance check (point 2 in §5) is the single most informative thing you can do to convince a viewer the animation is *teaching the tensor*, not just decorating a slide.

## 9. References

- M. Flaschel, *How to Visualize Computational Mechanics: Animating Finite Elements, Continuum Mechanics, and Tensor Calculus*, Comp. Applic. in Engineering Education **34**:e70189 (2026). DOI: 10.1002/cae.70189. Open access.
- **Gallery (authoritative source code)**: <https://github.com/DrSimulate/gallery>. Single-file `manim.py`, `matplotlib_animate.py`, `blender.py` — every recipe in this skill cross-references a class or block in those files. When a recipe needs more depth, *open the gallery file*; it's the reference implementation.
- YouTube: Dr. Simulate
- Stop-motion-OBJ: <https://github.com/neverhood311/Stop-motion-OBJ>

### Gallery cross-reference

| Recipe | Gallery class / region |
|--------|------------------------|
| R1 — stress on sphere | `matplotlib_animate.py` "Stress Tensor Components - Infinitesimal Sphere" |
| R1b — stress on cube | `matplotlib_animate.py` "Stress Tensor Components - Infinitesimal Cube" |
| R2 — motion mapping | `manim.py` `Kinematics2D` |
| R3 — F on unit circle | `manim.py` `KinematicsDeformationGradient2D` |
| R5 — Cauchy/PK1/PK2 | `manim.py` `AreaElementRotationCauchy` (3D version) |
| R6 — FEM shape functions | `manim.py` `FiniteElements` (uses `Variable`, not raw `ValueTracker`) |
| R7 — mesh refinement | `manim.py` `FiniteElementsMeshRefinement` (with `fem_1d_poisson` helper) |
| R8 — ParaView→Blender | gallery README "Finite Element Simulation Results in Blender" |
| R9 — Blender motion | `blender.py` water drop |
| **R10 — invariance** | **`manim.py` `TensorComponents`** |

## 10. Progressive disclosure

- `RECIPES.md` — concrete, runnable code for each pattern R1–R9.
- `PIPELINE.md` — the ParaView → Blender pipeline in detail.
- `tests/test_deformation_gradient.py` — end-to-end working matplotlib example, doubles as a smoke test for the skill.
