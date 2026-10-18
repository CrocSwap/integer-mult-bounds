"""Scoped mathematical and failure-detection tests. Apache-2.0.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
"""
import importlib.util
from itertools import permutations, product
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("weighted_fourier_verify", HERE / "verify.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class Tests(unittest.TestCase):
    def test_exact_root_fields_and_fourier_normalization(self):
        for m, expected in [(4, (1, 0, 1)), (12, (1, 0, -1, 0, 1)),
                            (20, (1, 0, -1, 0, 1, 0, -1, 0, 1))]:
            self.assertEqual(V.ORACLE.cyclotomic(m), expected)
            ring = V.ORACLE.Ring(m)
            for i in range(m):
                for j in range(m):
                    self.assertEqual(ring.mul(ring.powers[i], ring.powers[j]),
                                     ring.powers[(i + j) % m])
        for moduli in V.DOMAIN + ((2, 3), (2, 4), (3, 3), (5,)):
            oracle = V.ORACLE.FourierOracle(moduli)
            for i in range(oracle.n):
                reconstructed = oracle.transform(oracle.transform(oracle.basis(i), -1), 1)
                self.assertEqual(reconstructed, tuple(oracle.ring.scale(x, oracle.n)
                                                      for x in oracle.basis(i)))

    def test_unreduced_two_point_domain(self):
        # No forced-weight or matched-address reduction: all 8 * 4**6 tuples.
        g = V.Group((2,))
        oracle = V.ORACLE.FourierOracle((2,))
        ps = tuple(permutations(range(2)))
        ws = tuple(product(range(4), repeat=2))
        total = accepted = 0
        for pi, sigma, rho in product(ps, repeat=3):
            for alpha, beta, omega in product(ws, repeat=3):
                layout = dict(pi=pi, sigma=sigma, rho=rho, alpha=alpha, beta=beta, omega=omega)
                literal = oracle.first_basis_failure(**layout) is None
                self.assertEqual(V.admit(g, **layout), literal)
                self.assertEqual(V.normal_form_condition(g, **layout), literal)
                total += 1
                accepted += int(literal)
        self.assertEqual((total, accepted), (32768, 256))

    def test_arbitrary_reciprocal_forward_gauges(self):
        g = V.Group((4,))
        oracle = V.ORACLE.FourierOracle((4,))
        identity = tuple(range(4))
        u, v = oracle.dense(71, 2), oracle.dense(71, 7)
        for alpha in product(range(4), repeat=4):
            layout = dict(pi=identity, sigma=identity, rho=identity, alpha=alpha,
                          beta=tuple(-a % 4 for a in alpha), omega=(0,) * 4)
            self.assertTrue(V.admit(g, **layout))
            actual, expected = oracle.evaluate(u, v, **layout)
            self.assertEqual(actual, expected)

    def test_unequal_factor_adjoint_and_affine_phases(self):
        g, layout = V.make_affine_layout((2, 4), lambda x: ((x[0] + x[1]) % 2, x[1]),
                                         (1, 3), (0, 1))
        self.assertTrue(V.admit(g, **layout))
        self.assertTrue(V.normal_form_condition(g, **layout))
        expected = tuple(g.index[((x + 1) % 2, (2 * x + y + 3) % 4)]
                         for x, y in g.points)
        self.assertEqual(layout["rho"], expected)
        self.assertNotEqual(layout["pi"], expected)
        inverse_pi = tuple(layout["pi"].index(i) for i in range(g.n))
        self.assertFalse(V.admit(g, **dict(layout, rho=inverse_pi)))

    def test_constant_phase_counterexample_is_literal(self):
        oracle = V.ORACLE.FourierOracle((4,))
        identity = tuple(range(4))
        actual, expected = oracle.evaluate(oracle.basis(0), oracle.basis(0),
            pi=identity, sigma=identity, rho=identity,
            alpha=(1,) * 4, beta=(1,) * 4, omega=(3,) * 4)
        self.assertEqual(actual, ((0, 4), (0, 0), (0, 0), (0, 0)))
        self.assertEqual(expected, ((4, 0), (0, 0), (0, 0), (0, 0)))

    def test_translated_layout_with_asymmetric_forward_phases(self):
        g = V.Group((4,))
        layout = dict(pi=(1, 2, 3, 0), sigma=(1, 2, 3, 0), rho=(1, 2, 3, 0),
                      alpha=(0, 0, 0, 0), beta=(0, 3, 2, 1), omega=(0, 1, 2, 3))
        self.assertTrue(V.admit(g, **layout))
        self.assertTrue(V.normal_form_condition(g, **layout))
        self.assertEqual(V.checked_basis_pairs(V.ORACLE.FourierOracle((4,)), layout), 16)

    def test_source_multiplier_need_not_be_involutive(self):
        g = V.Group((5,))
        pi = (0, 2, 4, 1, 3)
        zeros = (0,) * 5
        layout = dict(pi=pi, sigma=pi, rho=pi, alpha=zeros, beta=zeros, omega=zeros)
        self.assertTrue(V.admit(g, **layout))
        self.assertTrue(V.normal_form_condition(g, **layout))
        self.assertNotEqual(tuple(pi[pi[j]] for j in range(5)), tuple(range(5)))
        self.assertEqual(V.checked_basis_pairs(V.ORACLE.FourierOracle((5,)), layout), 25)

    def test_classification_false_positive_and_false_negative_controls(self):
        with patch.object(V, "coefficient_condition", return_value=True):
            with self.assertRaisesRegex(ValueError, "classification discrepancy"):
                V.census_group((2,))
        with patch.object(V, "coefficient_condition", return_value=False):
            with self.assertRaisesRegex(ValueError, "classification discrepancy"):
                V.census_group((2,))

    def test_nonbijective_and_malformed_admission(self):
        g = V.Group((2,))
        valid = dict(pi=(0, 1), sigma=(0, 1), rho=(0, 1),
                     alpha=(0, 0), beta=(0, 0), omega=(0, 0))
        for field, bad in [("pi", (0, 0)), ("sigma", (True, 0)),
                           ("rho", (1,)), ("alpha", (0, 4)), ("beta", (0, -1))]:
            with self.assertRaises(ValueError):
                V.admit(g, **dict(valid, **{field: bad}))

    def test_source_relocation_and_corruption(self):
        root = HERE.parents[1]
        with tempfile.TemporaryDirectory(prefix="weighted Fourier source ") as tmp:
            target = Path(tmp)
            pins = json.loads((HERE / "SOURCES.json").read_text())
            paths = []
            for row in pins["files"]:
                if row["usage"] == "input":
                    path = target / row["path"]
                    path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(root / row["path"], path)
                    paths.append(path)
            self.assertEqual(V.check_sources(target), V.check_sources())
            source = paths[0]
            original = source.read_bytes()
            source.write_bytes(original + b"\ncorruption\n")
            with self.assertRaisesRegex(ValueError, "source drift"):
                V.check_sources(target)
            source.unlink()
            with self.assertRaises(FileNotFoundError):
                V.check_sources(target)

    def test_write_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "existing.json"
            path.write_text("do not overwrite\n")
            run = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"),
                                  "--write", str(path)], capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("refusing to overwrite", run.stderr)
            self.assertEqual(path.read_text(), "do not overwrite\n")


if __name__ == "__main__":
    unittest.main()
