"""
Smoke test for the animating-computational-mechanics skill.

Implements R3 (deformation gradient F on a unit circle of line elements) using
matplotlib only — no Manim/Blender dependency. Verifies:
  1. matplotlib FuncAnimation runs to completion against the installed version
  2. The recipe structure (data prep -> animate(frame) -> save) works end-to-end
  3. Output GIF is non-trivially sized and viewable

Mathematics:
  Reference circle of N line element vectors r_i = (cos a_i, sin a_i).
  At each frame, F(t) is interpolated linearly from F_0 = I to F_1 (target).
  Each r_i maps to F(t) @ r_i; the deformed shape is the ellipse F(t) S^1.

Run: python tests/test_deformation_gradient.py
Expected output:
  - tests/out/deformation_gradient.gif
  - tests/out/deformation_gradient_frame00.png  (first-frame static fallback)
  - prints PASS / FAIL summary
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")  # headless

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)

GIF_PATH = OUT / "deformation_gradient.gif"
FRAME_PATH = OUT / "deformation_gradient_frame00.png"

# Reference: unit circle, N sample line element vectors.
N_SAMPLES = 16
angles = np.linspace(0, 2 * np.pi, N_SAMPLES, endpoint=False)
ref_vecs = np.stack([np.cos(angles), np.sin(angles)], axis=-1)  # (N, 2)
circle_th = np.linspace(0, 2 * np.pi, 200)
circle = np.stack([np.cos(circle_th), np.sin(circle_th)], axis=-1)  # (200, 2)

# Target deformation gradient (Flaschel Fig. 6 example).
F0 = np.eye(2)
F1 = np.array([[1.23, 0.84], [0.34, 2.27]])

N_FRAMES = 60


def F_at(frame: int) -> np.ndarray:
    """Linear interpolation in frame index from F0 to F1."""
    t = frame / (N_FRAMES - 1)
    return (1 - t) * F0 + t * F1


fig, ax = plt.subplots(figsize=(6, 6))


def animate(frame: int):
    ax.cla()
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.set_facecolor("#0a1230")

    # Reference circle and line elements (faint, fixed).
    ax.plot(circle[:, 0], circle[:, 1], color="#888", lw=1, alpha=0.5)
    for v in ref_vecs:
        ax.plot([0, v[0]], [0, v[1]], color="#4488ff", lw=0.8, alpha=0.4)

    # Deformed shape under F(t).
    F = F_at(frame)
    ell = circle @ F.T
    ax.plot(ell[:, 0], ell[:, 1], color="gold", lw=2)

    # Deformed line elements F r_i.
    def_vecs = ref_vecs @ F.T
    for v in def_vecs:
        ax.plot([0, v[0]], [0, v[1]], color="white", lw=1.0)

    # Title showing F components.
    ax.set_title(
        f"F = [[{F[0,0]:.2f}, {F[0,1]:.2f}], "
        f"[{F[1,0]:.2f}, {F[1,1]:.2f}]]",
        color="white",
        fontfamily="monospace",
    )
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_color("white")


def main() -> int:
    failures: list[str] = []

    # Save first frame as static PNG.
    animate(0)
    fig.savefig(FRAME_PATH, dpi=100, facecolor="#0a1230")
    if not FRAME_PATH.exists() or FRAME_PATH.stat().st_size < 1_000:
        failures.append(f"first-frame PNG missing or too small: {FRAME_PATH}")

    # Render animation.
    ani = FuncAnimation(fig, animate, frames=N_FRAMES, interval=50)
    writer = PillowWriter(fps=20)
    ani.save(GIF_PATH, writer=writer, dpi=80)

    if not GIF_PATH.exists():
        failures.append(f"GIF not written: {GIF_PATH}")
    else:
        size_kb = GIF_PATH.stat().st_size / 1024
        if size_kb < 10:
            failures.append(f"GIF suspiciously small: {size_kb:.1f} KB")
        else:
            print(f"[ok] wrote {GIF_PATH} ({size_kb:.1f} KB)")
            print(f"[ok] wrote {FRAME_PATH}")

    # Sanity check: the deformed ellipse at the final frame should not lie
    # within the reference circle (F1 stretches significantly).
    ell_final = circle @ F1.T
    radii = np.linalg.norm(ell_final, axis=1)
    if radii.max() < 1.0:
        failures.append(
            f"deformed ellipse never exceeds reference radius "
            f"(max radius = {radii.max():.3f})"
        )
    else:
        print(f"[ok] deformed ellipse max radius = {radii.max():.3f} > 1")

    if failures:
        print("\nFAIL:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
