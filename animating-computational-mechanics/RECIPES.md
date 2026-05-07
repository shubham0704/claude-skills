# Recipes — Animating Computational Mechanics

Each recipe maps a **mechanics concept** to a runnable code skeleton. Lift the skeleton, swap in the user's data, render. Skeletons are written for Matplotlib `3.10.1`, ManimCE `0.18.1`, Blender `4.5`.

Keep the skeletons unchanged in spirit when adapting — the structure (data prep → animate fn → save) is what makes them debuggable. Don't refactor the recipe to "look nicer".

---

## R1 — Stress tensor on infinitesimal sphere (Matplotlib)

**Mechanics:** Cauchy stress $\sigma_{ij}$, six independent components. For each component, set all others to zero and visualize the resulting traction $\mathbf{t} = \sigma \mathbf{n}$ at sample points on a unit sphere. Rotating the camera reveals the three-dimensional structure.

**Recipe:** `2×3` panel grid, one sphere per component, a `FuncAnimation` rotating all six in sync.

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Sample points on the unit sphere
N_PHI, N_THETA = 12, 8
phi = np.linspace(0, 2*np.pi, N_PHI, endpoint=False)
theta = np.linspace(0.1, np.pi-0.1, N_THETA)
PHI, THETA = np.meshgrid(phi, theta)
nx = np.sin(THETA) * np.cos(PHI)
ny = np.sin(THETA) * np.sin(PHI)
nz = np.cos(THETA)
N = np.stack([nx.ravel(), ny.ravel(), nz.ravel()], axis=-1)  # (M, 3)

def stress_component(i, j):
    sigma = np.zeros((3, 3))
    sigma[i, j] = sigma[j, i] = 1.0   # symmetric
    return sigma

components = [(0,0), (1,1), (2,2), (0,1), (0,2), (1,2)]
labels = ["σ11", "σ22", "σ33", "σ12", "σ13", "σ23"]

fig = plt.figure(figsize=(12, 8))
axes = [fig.add_subplot(2, 3, k+1, projection='3d') for k in range(6)]

def animate(frame):
    azim = -60 + frame / 2
    for ax, (i, j), lbl in zip(axes, components, labels):
        ax.cla()
        sigma = stress_component(i, j)
        T = N @ sigma.T  # tractions at each sample point
        ax.plot_surface(nx, ny, nz, alpha=0.2, color='gray', linewidth=0)
        ax.quiver(N[:,0], N[:,1], N[:,2],
                  N[:,0], N[:,1], N[:,2], length=0.3, color='red')   # normals
        ax.quiver(N[:,0], N[:,1], N[:,2],
                  T[:,0], T[:,1], T[:,2], length=0.3, color='white') # tractions
        ax.set_title(lbl)
        ax.view_init(elev=20, azim=azim)
        ax.set_axis_off()

ani = FuncAnimation(fig, animate, frames=180, interval=50)
ani.save("stress_sphere.mp4", dpi=120, bitrate=-1)
```

**Pedagogical note:** Run the same animation with the camera locked and a *rotation* applied to the basis (i.e., `sigma = R @ sigma @ R.T`). Students see the components shuffle while the tractions on the sphere stay put — this is invariance of the tensor.

---

## R1b — Stress tensor on infinitesimal cube (Matplotlib)

**Mechanics:** Same six components, but on a cube whose normals align with the basis. Each *column* of $\sigma$ is then literally the traction on the corresponding cube face. This is the cleanest pedagogical view of "stress = matrix of tractions in this basis".

```python
# (data prep as in R1, but N becomes the six face normals ±e_i)
faces = np.eye(3)
N = np.concatenate([faces, -faces], axis=0)
```

The rest is identical to R1 with `plot_surface` replaced by drawing 12 cube edges via `Line3DCollection`.

---

## R2 — Nonlinear motion mapping (Manim)

**Mechanics:** $x = \varphi(X, t)$ continuously deforming a reference body into a deformed configuration. Manim's `apply_function` is purpose-built for this; `Transform` is *not* (it's restricted to predefined shape pairs).

```python
from manim import *

class Kinematics2D(MovingCameraScene):
    def construct(self):
        time = ValueTracker(0.0)

        reference = Triangle().stretch(1.3, dim=1).move_to(2*UP + 1.25*RIGHT)

        def phi(X, t):
            x0 = (1 - 0.25*t)*X[0] + t*(X[1] - 2)**2 + 2.5*t
            x1 = (1 + 0.25*t)*X[1] + 0.25*t
            x2 = X[2]
            return (x0, x1, x2)

        current = always_redraw(
            lambda: reference.copy().apply_function(
                lambda X: phi(X, time.get_value())
            )
        )

        self.add(reference, current)
        self.play(time.animate.set_value(1.0), run_time=4, rate_func=linear)
```

Render: `manim -pqh script.py Kinematics2D` (preview, high quality).

**Why `apply_function`, not `Transform`:** `Transform` requires you to know both endpoints as Manim objects in advance. `apply_function` re-evaluates the mapping at every frame from the current `ValueTracker` — exactly the continuum-mechanics motion mapping.

---

## R3 — Deformation gradient $F$ on a unit circle (Manim)

**Mechanics:** $\mathrm{d}x = F \, \mathrm{d}X$. Animate undeformed line element vectors on a unit circle and their image under $F$. Choose components of $F$ that vary in time to expose stretch + shear + rotation.

```python
from manim import *
import numpy as np

class FOnUnitCircle(Scene):
    def construct(self):
        F11 = ValueTracker(1.0)
        F12 = ValueTracker(0.0)
        F21 = ValueTracker(0.0)
        F22 = ValueTracker(1.0)

        circle = Circle(radius=1, color=WHITE)

        def F_matrix():
            return np.array([
                [F11.get_value(), F12.get_value()],
                [F21.get_value(), F22.get_value()],
            ])

        deformed = always_redraw(
            lambda: circle.copy().apply_matrix(F_matrix()).set_color(YELLOW)
        )

        # Sample line element vectors
        N = 12
        angles = np.linspace(0, 2*np.pi, N, endpoint=False)
        arrows_ref = VGroup(*[
            Arrow(ORIGIN, [np.cos(a), np.sin(a), 0], buff=0, color=BLUE)
            for a in angles
        ])
        arrows_def = always_redraw(
            lambda: VGroup(*[
                Arrow(ORIGIN,
                      F_matrix() @ np.array([np.cos(a), np.sin(a)]),
                      buff=0, color=GOLD)
                for a in angles
            ])
        )

        self.add(circle, deformed, arrows_ref, arrows_def)
        self.play(
            F11.animate.set_value(1.23),
            F12.animate.set_value(0.84),
            F21.animate.set_value(0.34),
            F22.animate.set_value(2.27),
            run_time=4, rate_func=linear,
        )
```

This is **the** Flaschel Fig. 6 animation. The 2D form is the canonical first introduction to F — keep it 2D; 3D F adds nothing pedagogically and obscures the message.

---

## R4 — Polar decomposition $F = RU$ (Manim)

**Mechanics:** Right polar decomposition splits F into a rotation R and a symmetric stretch U. Animate as: reference → stretched (apply U) → rotated (apply R), holding each intermediate visible briefly.

```python
from manim import *
import numpy as np

class PolarDecomposition(Scene):
    def construct(self):
        # Target F (from R3)
        F = np.array([[1.23, 0.84], [0.34, 2.27]])
        # Polar decomposition: F = R U with U symm. PSD
        U2 = F.T @ F
        eigvals, eigvecs = np.linalg.eigh(U2)
        U = eigvecs @ np.diag(np.sqrt(eigvals)) @ eigvecs.T
        R = F @ np.linalg.inv(U)

        circle = Circle(radius=1, color=WHITE)
        self.play(Create(circle))

        # Stage 1: apply U (stretch only)
        circle_U = circle.copy().apply_matrix(U).set_color(GOLD)
        self.play(ReplacementTransform(circle.copy(), circle_U), run_time=2)
        self.wait(0.5)

        # Stage 2: apply R (rotation)
        circle_F = circle_U.copy().apply_matrix(R).set_color(GREEN)
        self.play(ReplacementTransform(circle_U, circle_F), run_time=2)
        self.wait()
```

Pedagogical hook: pause on the U-stretched ellipse with its principal axes labeled, *before* applying R. That ellipse's principal directions are the eigenvectors of U — make them explicit with a `DashedLine`.

---

## R5 — Cauchy / 1st PK / 2nd PK side-by-side (Matplotlib)

**Mechanics:** Three ways to push tractions across the reference/deformed configurations:
- Cauchy: traction on deformed area, normal in deformed config: $\mathrm{d}\hat f = \sigma \, \mathbf{n} \, \mathrm{d}a$
- 1st PK: traction on deformed area, normal in reference config: $\mathrm{d}\hat f = P \, \mathbf{N} \, \mathrm{d}A$
- 2nd PK: reference traction on reference area: $\mathrm{d}\hat F = S \, \mathbf{N} \, \mathrm{d}A$

Animate three small flat area elements with their normals and tractions side-by-side, rotating the orientation through 360°.

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

F = np.array([[1.25, 0.0], [-1.33, 0.75]])  # 2D for clarity
sigma = np.array([[2.0, 0.5], [0.5, 1.0]])
J = np.linalg.det(F)
P = J * sigma @ np.linalg.inv(F).T
S = np.linalg.inv(F) @ P

fig, axes = plt.subplots(1, 3, figsize=(12, 4))
labels = ["Cauchy: σn", "1st PK: PN", "2nd PK: SN"]

def animate(frame):
    theta = 2*np.pi * frame / 180
    N_ref = np.array([np.cos(theta), np.sin(theta)])  # reference normal
    n_def = F @ N_ref
    n_def = n_def / np.linalg.norm(n_def)            # deformed normal
    tractions = [sigma @ n_def, P @ N_ref, S @ N_ref]
    normals = [n_def, N_ref, N_ref]
    for ax, T, N, lbl in zip(axes, tractions, normals, labels):
        ax.cla()
        ax.set_xlim(-2, 2); ax.set_ylim(-2, 2); ax.set_aspect("equal")
        ax.set_title(lbl); ax.set_axis_off()
        ax.quiver(0, 0, N[0], N[1], color="red", scale=4)
        ax.quiver(0, 0, T[0], T[1], color="white", scale=4)

ani = FuncAnimation(fig, animate, frames=180, interval=50)
ani.save("stress_measures.mp4", dpi=120, bitrate=-1)
```

**Pedagogical note (Flaschel Fig. 9):** the *visual* point is that all three encode the same physics; only the bookkeeping (which area, which normal) differs. Keep the three panels at identical scale and sync the rotation across them.

---

## R6 — Parameterized FEM solution function (Manim)

**Mechanics:** $u(x) \approx \sum_{i=0}^n u_i N_i(x)$. Animate by binding each $u_i$ to a `ValueTracker` and showing the piecewise-linear interpolant evolve as the parameters change.

```python
from manim import *
import numpy as np

class ParametrizedSolution(Scene):
    def construct(self):
        n = 5
        x_nodes = np.linspace(0, 1, n+1)
        u_trackers = [ValueTracker(0.0) for _ in range(n+1)]

        axes = Axes(x_range=[0, 1, 0.2], y_range=[0, 1, 0.2],
                    x_length=8, y_length=4)

        def get_curve():
            pts = [axes.c2p(x, t.get_value())
                   for x, t in zip(x_nodes, u_trackers)]
            return VMobject(color=YELLOW).set_points_as_corners(pts)

        curve = always_redraw(get_curve)
        self.add(axes, curve)

        # Animate target nodal values
        target = [0.00, 0.29, 0.48, 0.48, 0.29, 0.00]
        anims = [t.animate.set_value(v) for t, v in zip(u_trackers, target)]
        self.play(*anims, run_time=4)
```

This is Flaschel Fig. 10. Crucial that nodal values become *visible* — add tick labels (`u_1 = 0.29` etc.) that update via `always_redraw`.

---

## R7 — Mesh refinement / FE convergence (Matplotlib)

**Mechanics:** Hold an analytical solution fixed (white), overlay successive FE solutions (yellow) for $n = 2, 4, 8, 16, 32$ elements, animate the transition.

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def analytical(x):
    return x * (1 - x)  # u'' = -2, u(0) = u(1) = 0

def fe_solution(n):
    x = np.linspace(0, 1, n+1)
    return x, analytical(x)  # piecewise linear interpolant of analytical at nodes

fig, ax = plt.subplots(figsize=(8, 4))
mesh_sizes = [2, 4, 8, 16, 32]

xx_fine = np.linspace(0, 1, 400)
yy_true = analytical(xx_fine)

def animate(frame):
    n = mesh_sizes[frame % len(mesh_sizes)]
    x, u = fe_solution(n)
    ax.cla()
    ax.set_xlim(0, 1); ax.set_ylim(-0.05, 0.30)
    ax.plot(xx_fine, yy_true, color="white", lw=2, label="analytical")
    ax.plot(x, u, color="gold", lw=2, marker="o", label=f"FE, n={n}")
    ax.set_facecolor("#0a1230"); ax.set_xticks([]); ax.set_yticks([])
    ax.legend(loc="upper right")

ani = FuncAnimation(fig, animate, frames=len(mesh_sizes)*20, interval=200)
ani.save("mesh_refine.mp4", dpi=120, bitrate=-1)
```

**Pedagogical note (Flaschel Fig. 11):** loop slowly. Students need to *see* the FE curve overlap the analytical one — too-fast refinement ruins the punchline.

---

## R8 — FEM result imported from ParaView (Blender)

See `PIPELINE.md` for the full procedure. Outline:

1. ParaView writes one `.obj` per timestep into `frames/`.
2. Blender 4.5: Edit → Preferences → Add-ons → install **Stop-motion-OBJ**.
3. File → Import → Mesh Sequence (Stop-motion-OBJ) → point at `frames/`.
4. Add a Cycles material, three-point lighting, render `--engine CYCLES`.

```python
# bpy script — assumes frames/0001.obj … frames/0120.obj on disk
import bpy
from bpy_extras.io_utils import ImportHelper

bpy.ops.preferences.addon_enable(module="stop_motion_obj")
bpy.ops.ms.import_sequence(directory="//frames/", fileNamePrefix="",
                            fileExtension="obj")
# Material + lighting via the Blender UI (or paste in here).
bpy.ops.render.render(animation=True)
```

Run with `blender --background --python script.py` (headless) once the `.blend` is set up.

---

## R9 — Imposed motion mapping on a textured Blender object (Blender)

**Mechanics:** prescribed deformation $\varphi(X, t)$ on a generic mesh (no FEM), with photoreal shading.

```python
import bpy
import numpy as np
from mathutils import Vector

TOTAL_FRAMES = 120

def phi(X, t):
    return np.array([
        (1 + 0.75 * t) * X[0],
        X[1],
        (1 - 0.25 * t) * X[2] + 0.35 * t * X[0]**2 - 1.5 * t,
    ])

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4)
obj = bpy.context.active_object
mesh = obj.data
reference = np.array([[v.co.x, v.co.y, v.co.z] for v in mesh.vertices])

mat = bpy.data.materials.new(name="Water")
mat.use_nodes = True
obj.data.materials.append(mat)

for frame in range(1, TOTAL_FRAMES + 1):
    t = frame / TOTAL_FRAMES
    for i, v in enumerate(mesh.vertices):
        v.co = Vector(phi(reference[i], t).tolist())
    for face in mesh.polygons:
        face.use_smooth = True
    obj.keyframe_insert(data_path="location", frame=frame)
    # for actual per-vertex animation use shape keys; this snippet shows
    # the structure — see PIPELINE.md for the production version.
```

**Caveat:** this snippet is illustrative, not production. For real per-vertex animation in Blender use **shape keys** (one per frame) or the Stop-motion-OBJ workflow. Direct vertex mutation across frames is overwritten on re-evaluation.

---

## R10 — Tensor invariance under basis rotation (Manim)

**Mechanics:** A tensor's *components* depend on the basis; the geometric action does not. Animate by rotating the basis (a grid in the background) while holding the deformed shape fixed. The matrix entries on screen change; the unit-circle-to-ellipse mapping stays put.

This is the recipe that converts "tensor = matrix" into "tensor = invariant object" — the single most useful pedagogical animation in the entire collection. Modelled on `TensorComponents` in the [DrSimulate gallery's `manim.py`](https://github.com/DrSimulate/gallery/blob/main/manim.py).

```python
from manim import *
import numpy as np

F_np = np.array([[2.0, 1.0], [0.5, 1.5]])
F_3d = np.array([[2.0, 1.0, 0.0],
                 [0.5, 1.5, 0.0],
                 [0.0, 0.0, 1.0]])

def Q(alpha):
    """In-plane rotation by alpha (rad)."""
    c, s = np.cos(alpha), np.sin(alpha)
    return np.array([[ c, -s, 0],
                     [ s,  c, 0],
                     [ 0,  0, 1]])

def rotate_matrix(F, alpha):
    """Components of F under a rotation of the basis by alpha."""
    Q2 = np.array([[np.cos(alpha), -np.sin(alpha)],
                   [np.sin(alpha),  np.cos(alpha)]])
    return Q2.T @ F @ Q2

def matrix2text(F):
    return r"\begin{bmatrix}" + \
           f"{F[0,0]:.2f} & {F[0,1]:.2f}" + r"\\" + \
           f"{F[1,0]:.2f} & {F[1,1]:.2f}" + \
           r"\end{bmatrix}"

class TensorInvariance(MovingCameraScene):
    def construct(self):
        alpha = ValueTracker(0.0)

        # Background grid — rotates with the basis.
        grid = NumberPlane(
            x_range=[-6, 6, 1], y_range=[-4, 4, 1],
            background_line_style={"stroke_opacity": 0.4},
        )
        grid_rot = always_redraw(
            lambda: grid.copy().apply_matrix(Q(alpha.get_value()))
        )

        # Component matrix — entries change with the basis.
        F_text = always_redraw(lambda:
            MathTex(r"\boldsymbol{F} = ",
                    matrix2text(rotate_matrix(F_np, -alpha.get_value()))
                    ).move_to(LEFT * 4 + UP * 2.5)
        )

        # Geometric action — does NOT depend on the basis.
        circle = Circle(radius=1, color=WHITE, stroke_width=4)
        ellipse = circle.copy().apply_matrix(F_3d).set_color(GOLD)

        self.add(grid_rot, F_text, circle, ellipse)
        self.wait(0.5)
        self.play(alpha.animate.set_value(30 * DEGREES), run_time=3)
        self.wait(0.5)
        self.play(alpha.animate.set_value(-30 * DEGREES), run_time=4)
        self.wait(0.5)
```

Render: `manim -ql script.py TensorInvariance` (low-quality preview, fast).

**Why this is the keystone recipe:** every other recipe shows *what* a tensor does. This one shows *why* the matrix entries are misleading — different bases, different entries, same physics. Run it once in your lecture and the rest of continuum mechanics gets easier.

---

## Production tips (from the gallery)

These are small, non-obvious details that make a real difference for production-quality output:

**Transparent background for slide compositing (Matplotlib).** When saving an animation that will be overlaid on a colored Beamer slide, use a PNG codec inside the `.mov` container with explicit transparent background:

```python
ani.save(out_path + ".mov",
         codec="png", dpi=DPI, bitrate=-1,
         savefig_kwargs={"transparent": True, "facecolor": "none"})
```

`codec="png"` (not the default) preserves the alpha channel; `facecolor="none"` makes the figure background transparent end-to-end.

**Use Manim's `Variable` for displayed parameters.** When the *value* of a parameter should be visible on screen (e.g. nodal values $u_i$ in R6), prefer `Variable(0, MathTex(r"u_0"), num_decimal_places=2)` over a bare `ValueTracker` + manually-built `MathTex`. `Variable` auto-updates the rendered text and saves boilerplate.

**Cross-dissolve for mesh refinement (Manim).** R7 is shown as a hard cut between mesh sizes; for production, use `FadeOut(old) + FadeIn(new)` in a single `self.play(...)` call so the comparison reads as continuous refinement. The gallery's `FiniteElementsMeshRefinement` is the reference implementation.

**Real FE solver beats hard-coded values.** In R7 the test snippet uses the analytical solution at the nodes as a stand-in for the FE solution. For a real lecture animation, solve the 1D Poisson problem properly (the gallery's `fem_1d_poisson(n, L, f)` helper is ~30 lines and produces honest nodal values; convergence then *means* something).

---

## Recipe selection cheat sheet

```
mechanics object?
├── tensor on infinitesimal element?
│    ├── sphere → R1
│    └── cube   → R1b
├── motion / deformation?
│    ├── arbitrary mapping φ(X, t)        → R2 (Manim)
│    ├── linear F on circle               → R3 (Manim)
│    └── F = RU step-by-step              → R4 (Manim)
├── stress measures comparison?           → R5 (Matplotlib)
├── FEM concept?
│    ├── parameterized u(x) = Σ uᵢ Nᵢ(x) → R6 (Manim)
│    └── mesh convergence                 → R7 (Matplotlib)
├── photoreal output?
│    ├── ParaView FEM result → R8 (Blender, see PIPELINE.md)
│    └── prescribed motion   → R9 (Blender)
└── basis-rotation invariance / tensor-vs-matrix? → R10 (Manim) ← the keystone
```
