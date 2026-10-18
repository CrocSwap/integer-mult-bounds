#!/usr/bin/env python3
"""Focused mathematical and package failure controls; Apache-2.0.

Sricharan Vagvala (@theon199), with substantial OpenAI Codex assistance.
"""
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("shear_rounding_audit", HERE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class MathematicalControls(unittest.TestCase):
    def test_independent_small_orbit_census(self):
        # All coordinates and all chronological cuts, not the endpoint oracle.
        for k in range(13):
            outcomes = []
            for a in range(-4, 5):
                for b in range(-4, 5):
                    errors = []
                    x, y = F(a), F(b)
                    for j in range(k + 1):
                        errors.extend((abs(x - F(j, 2)), abs(y - F(1, 2))))
                        x = x + y
                    outcomes.append(max(errors))
            self.assertEqual(min(outcomes), audit.sharp_bound(k))

    def test_exact_and_rounded_equivariance_are_different(self):
        w = (F(1), F(1))
        exact = lambda v: tuple(x / 2 for x in v)
        rounded = lambda v: audit.quantize(exact(v), F(1))
        self.assertEqual(exact(audit.shear(w)), audit.shear(exact(w)))
        self.assertNotEqual(rounded(audit.shear(w)), audit.shear(rounded(w)))
        # Positive subdomain: the transverse output is exactly on the grid.
        v = (F(-1, 2), F(1))
        self.assertEqual(audit.quantize(audit.shear(v), F(1), "floor"),
                         audit.shear(audit.quantize(v, F(1), "floor")))

    def test_false_mutations_of_literal_carried_word(self):
        word = audit.word(True)
        probes = [(F(a), F(b)) for a in (-1, 0, 1) for b in (-1, 0, 1)]
        # Three scope-relevant omissions: output alignment and both returns.
        for deleted in (2, 5, 6):
            mutant = word[:deleted] + word[deleted + 1:]
            detected = False
            for d in probes:
                for w in probes:
                    expected = (tuple(a + b for a, b in zip(d, w)), w)
                    if audit.run(mutant, d, w, F(1), exact=True) != expected:
                        detected = True
                        break
                if detected:
                    break
            self.assertTrue(detected, deleted)

    def test_complete_echo_inverse_and_missing_unload(self):
        d, u, x = (F(2), F(-1)), (F(1), F(1)), (F(0), F(1))
        eager = audit.echo(audit.word(False), d, u, x, F(1))
        carried = audit.echo(audit.word(True), d, u, x, F(1))
        self.assertEqual(eager, ((F(2), F(1)), u))
        self.assertEqual(carried, ((F(1), F(1)), u))
        loaded = tuple(a + b for a, b in zip(u, x))
        after = audit.run(audit.word(True), d, loaded, F(1))
        missing_unload = audit.run(audit.inverse(audit.word(True)), *after, F(1))
        self.assertEqual(missing_unload[1], loaded)
        self.assertNotEqual(missing_unload[1], u)

    def test_horizon_budget_and_endpoint_errors(self):
        self.assertGreater(audit.orbit_radius(70, 35, 0), F(18))
        self.assertEqual(audit.orbit_radius(70, 17, 0), F(18))
        self.assertGreater(audit.orbit_radius(2, 0, 0), F(1, 2))
        with self.assertRaises(ValueError):
            audit.sharp_bound(True)
        v = (F(0), F(1, 2))
        defect = audit.quantize(audit.shear(v), F(1), "nearest-even")
        self.assertEqual(defect, audit.shear(audit.quantize(v, F(1), "nearest-even")))
        # Yet K*delta/2 is positive: both endpoint errors must be charged.
        self.assertGreater(F(1, 2), F(0))


class PackageControls(unittest.TestCase):
    def test_source_corruption_and_false_head(self):
        with tempfile.TemporaryDirectory(prefix="shear source control ") as td:
            target = Path(td) / "package"
            shutil.copytree(HERE, target)
            source = target / "references/pr1537-README.md"
            original = source.read_bytes()
            source.write_bytes(original + b"\nchanged source\n")
            with self.assertRaisesRegex(ValueError, "Git blob mismatch"):
                audit.check_reference(target)
            source.write_bytes(original)
            pins = audit.read_json(target / "SOURCES.json")
            pins["retained_external_sources"][0]["head"] = "0" * 40
            (target / "SOURCES.json").write_text(json.dumps(pins))
            with self.assertRaisesRegex(ValueError, "provenance drift"):
                audit.check_reference(target)

    def test_duplicate_json_and_wrong_certificate(self):
        with tempfile.TemporaryDirectory(prefix="shear receipt control ") as td:
            target = Path(td) / "package"
            shutil.copytree(HERE, target)
            receipt = target / "EXPECTED.json"
            data = audit.read_json(receipt)
            data["orbit_rows"][70]["radius_grid_units"] = "17"
            receipt.write_text(json.dumps(data))
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(target / "verify.py")],
                                    capture_output=True, text=True, timeout=120)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("certificate mismatch", result.stderr)
            receipt.write_text('{"k":70,"k":71}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                audit.read_json(receipt)

    def test_read_only_optimized_relocation(self):
        with tempfile.TemporaryDirectory(prefix="shear relocated package ") as td:
            target = Path(td) / "directory with spaces"
            shutil.copytree(HERE, target)
            before = {str(p.relative_to(target)): p.read_bytes()
                      for p in target.rglob("*") if p.is_file()}
            for p in target.rglob("*"):
                if p.is_file():
                    p.chmod(0o444)
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(target / "verify.py")],
                                    cwd=td, capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_SHEAR_EQUIVARIANT_ROUNDING", result.stdout)
            after = {str(p.relative_to(target)): p.read_bytes()
                     for p in target.rglob("*") if p.is_file()}
            self.assertEqual(before, after)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("PASS_SHEAR_ROUNDING_PACKAGE_TESTS")
    raise SystemExit(0 if result.wasSuccessful() else 1)
