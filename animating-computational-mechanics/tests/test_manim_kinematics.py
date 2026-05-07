"""
Smoke test for the Manim recipes in RECIPES.md.

Implements a minimal version of R2 (Kinematics2D motion mapping) modelled on
the gallery's `Kinematics2D` class. Verifies:
  1. ManimCE imports cleanly.
  2. The `apply_function(lambda X: phi(X, t))` pattern compiles and renders.
  3. A short MP4 lands on disk.

Run as a Manim scene from the test directory:

    cd tests
    manim -ql --media_dir out/manim test_manim_kinematics.py KinematicsSmoke

(`-ql` = 480p15, fast. Use `-qh` for 1080p60.)

Or invoke this file as a regular Python script — it will shell out to manim
itself, with sensible defaults.
"""
from __future__ import annotations

from manim import (
    MovingCameraScene,
    ValueTracker,
    Triangle,
    UP,
    RIGHT,
    always_redraw,
    linear,
)


class KinematicsSmoke(MovingCameraScene):
    """Minimal Kinematics2D — reference triangle morphed by phi(X, t)."""

    def construct(self):
        time = ValueTracker(0.0)
        reference = Triangle().stretch(1.3, dim=1).move_to(2 * UP + 1.25 * RIGHT)

        def phi(X, t):
            x0 = (1 - 0.25 * t) * X[0] + t * (X[1] - 2) ** 2 + 2.5 * t
            x1 = (1 + 0.25 * t) * X[1] + 0.25 * t
            x2 = X[2]
            return (x0, x1, x2)

        current = always_redraw(
            lambda: reference.copy().apply_function(
                lambda X: phi(X, time.get_value())
            )
        )

        self.add(reference, current)
        self.wait(0.1)
        self.play(time.animate.set_value(1.0), run_time=1.5, rate_func=linear)
        self.wait(0.1)


def _shell_render() -> int:
    """If run as a script, shell out to manim CLI at low quality."""
    import subprocess
    import sys
    from pathlib import Path

    here = Path(__file__).resolve().parent
    out = here / "out" / "manim"
    out.mkdir(parents=True, exist_ok=True)

    cmd = [
        "manim",
        "-ql",
        "--media_dir", str(out),
        "--disable_caching",
        str(Path(__file__).resolve()),
        "KinematicsSmoke",
    ]
    print("running:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        print("FAIL")
        return result.returncode

    # Find the produced .mp4.
    mp4s = list(out.rglob("*.mp4"))
    if not mp4s:
        print("FAIL: no .mp4 produced")
        return 1

    mp4 = mp4s[0]
    size_kb = mp4.stat().st_size / 1024
    if size_kb < 5:
        print(f"FAIL: mp4 suspiciously small ({size_kb:.1f} KB)")
        return 1

    print(f"[ok] rendered {mp4} ({size_kb:.1f} KB)")
    print("PASS")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(_shell_render())
