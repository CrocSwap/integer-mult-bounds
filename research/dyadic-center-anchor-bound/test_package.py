#!/usr/bin/env python3
"""Independent finite arithmetic and portable-package failure controls.

Apache-2.0. Ross Richardson, with substantial OpenAI Codex assistance.
Both implementations are AI-assisted, not independent human reviews.
"""
import importlib.util
from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("anchor_for_tests", HERE / "anchor.py")
anchor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(anchor)


class AnchorTests(unittest.TestCase):
    def test_independent_literal_matrix_products(self):
        # Direct dot products use neither the affine quotient checker nor
        # the orbit-count formula. Cover all 128 anchors at h8, including
        # mathematically valid factors outside the priced alphabet.
        for bits in range(128):
            b = [i+1 for i in range(7) if bits & (1 << i)]
            f = anchor.factor(8, 0, b)
            masks = [sum(1 << i for i in t) for t in f["triples"]]
            for sm, u in zip(masks, f["scatter"]):
                for tm, v in zip(masks, f["gather"]):
                    self.assertEqual(sum(a*b for a, b in zip(u, v)), (sm & tm).bit_count()-1)

    def test_integer_domain_reduction(self):
        # Independent two-value gather test, including negative/large offsets.
        accepted = 0
        for vector in product((-1, 0, 1, 2), repeat=7):
            direct = all(-b in (-1, 0, 1) and 1-b in (-1, 0, 1) for b in vector)
            try:
                selected = anchor.classify_integral_anchor(8, 0, [0, *vector])
            except ValueError:
                self.assertFalse(direct)
            else:
                self.assertTrue(direct)
                self.assertEqual(selected, tuple(i+1 for i, b in enumerate(vector) if b))
                accepted += 1
        self.assertEqual(accepted, 128)

    def test_every_pivot_and_anchor_at_h8(self):
        for pivot in range(8):
            coordinates = [i for i in range(8) if i != pivot]
            for bits in range(128):
                b = [i for j, i in enumerate(coordinates) if bits & (1 << j)]
                f = anchor.factor(8, pivot, b)
                maximum = max(abs(x) for row in f["scatter"] for x in row)
                self.assertEqual(maximum <= 2, len(b) <= 4)
                self.assertEqual(anchor.affine_identity(f), 56)
                if len(b) <= 4:
                    cost = anchor.literal_price(f)
                    self.assertEqual(cost["G"]+cost["H"], (714, 713, 702, 716, 748)[len(b)])

    def test_all_h_polynomial_certificate(self):
        rows = json.loads((HERE / "CERTIFICATE.json").read_text())["positive_newton_coefficients"]
        self.assertTrue(anchor.check_positive_certificate(rows))
        # Supplemental checks of the independently counted subset formula.
        # These samples do not replace the polynomial identity or positivity proof.
        for h in range(10, 102, 2):
            for k, row in enumerate(rows, 1):
                expected = sum(a*anchor.choose(h-10, j) for j, a in enumerate(row))
                self.assertEqual(anchor.orbit(h, k)["G_plus_H"]-anchor.orbit(h, 0)["G_plus_H"],
                                 expected)
                self.assertGreater(expected, 0)

    def test_corrupt_factor_dimensions_and_types(self):
        good = anchor.factor(8, 0, [])
        for key in ("gather", "scatter", "triples"):
            bad = deepcopy(good)
            bad[key].pop()
            with self.assertRaisesRegex(ValueError, "incomplete factor dimensions"):
                anchor.affine_identity(bad)
        bad = deepcopy(good)
        bad["scatter"][0] = tuple(True if i == 0 else a for i, a in enumerate(bad["scatter"][0]))
        with self.assertRaisesRegex(ValueError, "invalid factor row"):
            anchor.affine_identity(bad)

    def relocate(self, directory):
        root = Path(directory) / "minimal tree with spaces"
        target = root / "research/dyadic-center-anchor-bound"
        target.mkdir(parents=True)
        for name in ("verify.py", "anchor.py", "SOURCES.json", "CERTIFICATE.json", "EXPECTED.json"):
            shutil.copy2(HERE / name, target / name)
        pins = json.loads((HERE / "SOURCES.json").read_text())
        for name in pins["sha256"]:
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, destination)
        return root, target

    def execute(self, target):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(target / "verify.py")],
                              cwd=target.parents[1], capture_output=True, text=True, timeout=120)

    def test_optimized_minimal_relocation(self):
        with tempfile.TemporaryDirectory(prefix="center-anchor-") as directory:
            _, target = self.relocate(directory)
            before = (target / "EXPECTED.json").read_bytes()
            result = self.execute(target)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            self.assertIn("PASS_CENTER_ANCHOR_BOUND", result.stdout)
            self.assertEqual((target / "EXPECTED.json").read_bytes(), before)

    def test_source_corruption_rejected_without_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="center-anchor-") as directory:
            root, target = self.relocate(directory)
            source = root / "scripts/experiments/complex_centers.py"
            source.write_text(source.read_text()+"\n# altered input\n")
            before = (target / "EXPECTED.json").read_bytes()
            result = self.execute(target)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source hash mismatch", result.stderr)
            self.assertEqual((target / "EXPECTED.json").read_bytes(), before)

    def test_polynomial_corruption_rejected_without_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="center-anchor-") as directory:
            _, target = self.relocate(directory)
            path = target / "CERTIFICATE.json"
            certificate = json.loads(path.read_text())
            certificate["positive_newton_coefficients"][0][0] = 21
            path.write_text(json.dumps(certificate))
            before = (target / "EXPECTED.json").read_bytes()
            result = self.execute(target)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("polynomial identity failed", result.stderr)
            self.assertEqual((target / "EXPECTED.json").read_bytes(), before)

    def test_typed_receipt_corruption_rejected_without_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="center-anchor-") as directory:
            _, target = self.relocate(directory)
            path = target / "EXPECTED.json"
            receipt = json.loads(path.read_text())
            # False == 0 in Python; canonical JSON comparison must reject it.
            receipt["h26_unique_minimizer_k"] = False
            path.write_text(json.dumps(receipt))
            before = path.read_bytes()
            result = self.execute(target)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("expected receipt mismatch", result.stderr)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
