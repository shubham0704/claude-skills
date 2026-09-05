#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_latex_notation.py"
SPEC = importlib.util.spec_from_file_location("check_latex_notation", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class NotationCheckerTest(unittest.TestCase):
    def audit(self, source: str, *, scope: str = "main", registry: dict | None = None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            main = root / "main.tex"
            main.write_text(source, encoding="utf-8")
            registry_path = None
            if registry is not None:
                registry_path = root / "notation.json"
                registry_path.write_text(json.dumps(registry), encoding="utf-8")
            result, warnings = MODULE.audit(main, scope=scope, registry_path=registry_path)
            self.assertEqual(warnings, [])
            return result

    def test_explained_symbols_do_not_raise_first_use_findings(self):
        result = self.audit(r"""
\documentclass{article}
\begin{document}
Let $x_t$ denote the physical state, $u_t$ the applied input, and $F$ the transition map.
\[
  x_{t+1}=F(x_t,u_t).
\]
\end{document}
""")
        first_use_codes = {issue.code for issue in result.issues if issue.severity != "INFO"}
        self.assertFalse({"N001", "N002", "N003"} & first_use_codes)

    def test_use_before_explanation_across_slides_is_error(self):
        result = self.audit(r"""
\documentclass{beamer}
\begin{document}
\begin{frame}{Prediction}
The estimate depends on $z_t$.
\end{frame}
\begin{frame}{Notation}
Here $z_t$ denotes the latent state.
\end{frame}
\end{document}
""")
        issues = [issue for issue in result.issues if issue.symbol == "z"]
        self.assertTrue(
            any(issue.code == "N002" and issue.severity == "ERROR" for issue in issues),
            result.to_dict(),
        )

    def test_callable_reused_as_numeric_value_is_role_drift(self):
        result = self.audit(r"""
\documentclass{beamer}
\begin{document}
\begin{frame}{World model}
The transition kernel $K$ propagates the physical state $x_t$:
$x_{t+1}\sim K(\cdot\mid x_t)$.
\end{frame}
\begin{frame}{Training}
The context length is $K=10$.
\end{frame}
\end{document}
""")
        issues = [issue for issue in result.issues if issue.symbol == "K"]
        self.assertTrue(
            any(issue.code == "N004" and issue.severity == "ERROR" for issue in issues),
            result.to_dict(),
        )

    def test_main_scope_stops_at_appendix(self):
        source = r"""
\documentclass{article}
\begin{document}
Let $x$ denote the state.
\appendix
The undeclared symbol $w$ appears here.
\end{document}
"""
        main_result = self.audit(source, scope="main")
        all_result = self.audit(source, scope="all")
        self.assertNotIn("w", main_result.symbols)
        self.assertIn("w", all_result.symbols)

    def test_inputs_are_expanded_in_document_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.tex").write_text(
                "\\documentclass{article}\n\\begin{document}\n\\input{first}\n\\input{second}\n\\end{document}\n",
                encoding="utf-8",
            )
            (root / "first.tex").write_text("\\section{Prediction}\nThe estimate uses $a$.\n", encoding="utf-8")
            (root / "second.tex").write_text("\\section{Notation}\nHere $a$ denotes acceleration.\n", encoding="utf-8")
            result, warnings = MODULE.audit(root / "main.tex")
            self.assertEqual(warnings, [])
            issue = next(
                (issue for issue in result.issues if issue.symbol == "a" and issue.code == "N002"),
                None,
            )
            self.assertIsNotNone(issue, result.to_dict())
            assert issue is not None
            self.assertTrue(issue.path.endswith("first.tex"))

    def test_registry_checks_required_first_use_language(self):
        result = self.audit(
            r"""
\documentclass{article}
\begin{document}
Let $O$ be a map and let $Y_t$ denote a measurement.
\[
Y_{t+1}\sim O(\cdot\mid Y_t).
\]
\end{document}
""",
            registry={
                "symbols": {
                    "O": {
                        "meaning": "observation kernel",
                        "terms": ["observation kernel"],
                        "roles": ["callable"],
                    }
                }
            },
        )
        issues = [issue for issue in result.issues if issue.symbol == "O"]
        self.assertTrue(any(issue.code == "N006" for issue in issues))

    def test_unbraced_math_style_is_preserved(self):
        result = self.audit(r"""
\documentclass{article}
\begin{document}
Let $\mathcal G_t$ denote the component graph and $G_t$ the input matrix.
\end{document}
""")
        self.assertIn(r"\mathcal{G}", result.symbols)
        self.assertIn("G", result.symbols)

    def test_derivative_does_not_redeclare_base_symbol(self):
        result = self.audit(r"""
\documentclass{beamer}
\begin{document}
\begin{frame}{Energy}
The energy $H$ is defined by $H(x)=x^2$ and evolves according to $\dot H=-H$.
\end{frame}
\begin{frame}{Horizon}
The forecast horizon is $H=100$.
\end{frame}
\end{document}
""")
        drift = [issue for issue in result.issues if issue.symbol == "H" and issue.code == "N004"]
        self.assertEqual(len(drift), 1, result.to_dict())
        self.assertEqual(drift[0].unit, "Horizon")

    def test_multiple_aligned_definitions_are_detected(self):
        result = self.audit(r"""
\documentclass{article}
\begin{document}
The estimate $\hat q_t$ is predicted position and $\hat p_t$ is predicted momentum.
\[
\begin{aligned}
  \hat q_t&=f(q_t), &\hat p_t&=g(q_t).
\end{aligned}
\]
\end{document}
""")
        self.assertIsNotNone(result.symbols[r"\hat{q}"]["first_definition"])
        self.assertIsNotNone(result.symbols[r"\hat{p}"]["first_definition"])

    def test_tuple_assignment_declares_every_left_hand_symbol(self):
        result = self.audit(r"""
\documentclass{article}
\begin{document}
The policies are defined by
\[
  (\pi_{\rm L}^{\star},\pi_{\rm S}^{\star})
  =\arg\min_{\pi_{\rm L},\pi_{\rm S}} C.
\]
\end{document}
""")
        self.assertIsNotNone(result.symbols[r"\pi_{L}"]["first_definition"])
        self.assertIsNotNone(result.symbols[r"\pi_{S}"]["first_definition"])


if __name__ == "__main__":
    unittest.main()
