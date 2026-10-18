"""Semantic and evidence-boundary checks for the bounded Newton audit.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import ast
from fractions import Fraction as F
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("newton_audit", HERE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class NewtonAuditTests(unittest.TestCase):
    def test_non_dyadic_cell_interiors(self):
        # Inputs with odd denominator are outside the primary dyadic input type.
        # The independently interpreted equations must be constant on each cell.
        for p in (1, 3, 5, 8):
            bits, scale = p + 5, 2 ** (p + 5)
            for k in (scale, scale + 1, 2 * scale - 1, 3 * scale, 4 * scale - 1):
                expected, trace = audit.rational.root(F(k, scale), p)
                for offset in (F(1, 3), F(1, 2), F(6, 7)):
                    self.assertEqual(audit.rational.root((k + offset) / scale, p), (expected, trace))
                    if k < 2 * scale:
                        self.assertEqual(audit.rational.inverse((k + offset) / scale, p),
                                         audit.rational.inverse(F(k, scale), p))
            # Crossing the right endpoint changes the finest *input* prefix;
            # an output can still coincide, so output inequality is not assumed.
            self.assertEqual(audit.rational.round_down(F(scale + 1, scale), bits), F(scale + 1, scale))

    def test_residual_sign_is_material(self):
        c, x, t = F(1281, 1024), F(5, 8), 6
        ct = audit.rational.round_down(c, t)
        u = audit.rational.round_down(ct * x, t)
        nxt = audit.rational.round_down(x * (2 - u), t)
        eta1, eta2, eps = u - ct * x, nxt - x * (2 - u), 1 - c * x
        correct = eps ** 2 - c * (c - ct) * x ** 2 + c * x * eta1 - c * eta2
        wrong = eps ** 2 + c * (c - ct) * x ** 2 + c * x * eta1 - c * eta2
        self.assertEqual(1 - c * nxt, correct)
        self.assertNotEqual(1 - c * nxt, wrong)

    def test_scaled_outputs_are_rejected(self):
        xn, xb, _ = audit.fixed.reciprocal(1, 0, 8)
        with self.assertRaisesRegex(ValueError, "cell bound"):
            audit.reciprocal_cell(8192, 13, 8, 2 * xn, xb)
        xn, xb, _ = audit.fixed.square_root(1, 0, 8)
        with self.assertRaisesRegex(ValueError, "cell bound"):
            audit.root_cell(8192, 13, 8, 2 * xn, xb)

    def test_correction_fixtures_satisfy_error_contract(self):
        for a, b, approximation in ((9, 3, F(23, 8)), (14, 5, F(3))):
            self.assertLess(abs(approximation - F(a, b)), F(1, 4))
            trial = approximation.numerator // approximation.denominator
            self.assertEqual(audit.fixed.correct_division(a, b, trial), divmod(a, b))
        for a, approximation in ((16, F(31, 8)), (15, F(4))):
            self.assertGreater(approximation, F(1, 4))
            self.assertLess((approximation - F(1, 4)) ** 2, a)
            self.assertGreater((approximation + F(1, 4)) ** 2, a)
            trial = approximation.numerator // approximation.denominator
            self.assertEqual(audit.fixed.correct_root(a, trial), math.isqrt(a))

    def test_source_tampering_is_rejected(self):
        inventory = json.loads((HERE / "SOURCES.json").read_text())
        with tempfile.TemporaryDirectory(prefix="newton-source-control-") as temporary:
            target = Path(temporary)
            for row in inventory["files"]:
                if row["usage"] == "input":
                    path = target / row["path"]
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes((audit.ROOT / row["path"]).read_bytes())
            with patch.object(audit, "ROOT", target):
                audit.source_check()
                source = target / "upstream/build/sections/09-exact-arithmetic.tex"
                source.write_bytes(source.read_bytes().replace(b"x=5/8", b"x=3/8"))
                with self.assertRaisesRegex(ValueError, "source drift"):
                    audit.source_check()

    def test_oracle_has_no_primary_import(self):
        tree = ast.parse((HERE / "rational.py").read_text())
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        self.assertEqual(len(imports), 1)
        self.assertIsInstance(imports[0], ast.ImportFrom)
        self.assertEqual(imports[0].module, "fractions")

    def test_recorded_domain_and_controls(self):
        receipt = json.loads((HERE / "CERTIFICATE.json").read_text())
        rows = receipt["prefix_cells"]["per_target"]
        self.assertEqual([row["target"] for row in rows], list(range(1, 9)))
        self.assertEqual(sum(row["reciprocal_cells"] for row in rows), 16320)
        self.assertEqual(sum(row["root_cells"] for row in rows), 48960)
        self.assertEqual(receipt["integer_recovery"]["division_inputs"], sum(2 ** n * (2 ** n - 1) for n in range(1, 9)))
        self.assertEqual(receipt["semantic_controls"], audit.semantic_controls())


if __name__ == "__main__":
    unittest.main()
