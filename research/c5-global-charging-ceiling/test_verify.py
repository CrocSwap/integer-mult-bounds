#!/usr/bin/env python3
"""Behavioral controls for the scoped charging certificate. Apache-2.0."""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location("charging_primary", HERE / "verify.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load the fixed primary checker")
primary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(primary)


class ChargingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.planes = primary.load_planes(ROOT)
        cls.receipt = primary.compute(ROOT)

    def cli(self, script, *args, success=True):
        run = subprocess.run(
            [sys.executable, "-I", "-O", "-B", "-Werror", str(script), *map(str, args)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(run.returncode == 0, success, run.stdout + run.stderr)
        return run

    def copy_fixture(self, directory):
        root = Path(directory)
        package = root / "research/c5-global-charging-ceiling"
        package.mkdir(parents=True)
        for name in ("verify.py", "independent.py", "SOURCES.json", "RESULT.json"):
            shutil.copyfile(HERE / name, package / name)
        inputs = root / primary.INPUTS
        inputs.mkdir(parents=True)
        for name in primary.PINS:
            shutil.copyfile(ROOT / primary.INPUTS / name, inputs / name)
        return root, package

    def test_public_optimized_commands(self):
        self.assertIn(
            "PASS_C5_GLOBAL_CHARGING_CEILING", self.cli(HERE / "verify.py").stdout
        )
        self.assertIn("PASS_INDEPENDENT", self.cli(HERE / "independent.py").stdout)

    def test_weights_and_equality_seam(self):
        ranks = self.receipt["full_support_local_ranks"]
        positions = [ranks.index(d) for d in (7, 8, 9)]
        checked = 0
        for a in range(11):
            for b in range(11):
                for c in range(11):
                    if a + b + c:
                        weights = [0] * 23
                        for i, w in zip(positions, (a, b, c), strict=True):
                            weights[i] = w
                        actual = primary.bound(weights, ranks, 9)
                        expected = Fraction(180 * (a + b + c), 7 * a + 8 * b + 9 * c)
                        self.assertEqual(actual, expected)
                        self.assertLessEqual(actual, Fraction(180, 7))
                        self.assertEqual(actual == Fraction(180, 7), b + c == 0)
                        checked += 1
        self.assertEqual(checked, 1330)

    def test_invalid_weights_and_matrices(self):
        ranks = self.receipt["full_support_local_ranks"]
        for weights in ([0] * 23, [-1] * 23, [1] * 22, [0.5] * 23):
            with self.assertRaises(ValueError):
                primary.bound(weights, ranks, 9)
        with self.assertRaises(ValueError):
            primary.binary_rank([4], 2)
        with self.assertRaises(ValueError):
            primary.tariff(self.planes, [-1], [0])

    def test_full_support_rejects_naive_charging(self):
        ranks = self.receipt["full_support_local_ranks"]
        self.assertEqual(sum(ranks), 193)
        self.assertGreater(sum(ranks), 9)  # The unnormalized sum is not a paid tariff.
        for d in (7, 8, 9):
            weights = [int(r == d) for r in ranks]
            self.assertEqual(primary.bound(weights, ranks, 9), Fraction(180, d))
        self.assertLess(Fraction(180, 7), 26)
        self.assertLess(Fraction(4140, 193), 22)

    def test_integer_rounding_does_not_overclaim(self):
        for value, ceiling in ((Fraction(180, 7), 26), (Fraction(4140, 193), 22)):
            self.assertEqual(-(-value.numerator // value.denominator), ceiling)
            self.assertLess(ceiling - 1, value)
            self.assertLess(value, ceiling)
        self.assertEqual(self.receipt["largest_integer_floor_not_excluded"], 26)

    def test_complete_plane_and_signed_cancellation(self):
        self.assertEqual(primary.tariff(self.planes, [], [0]), 0)
        self.assertEqual(primary.tariff(self.planes, [0], [0]), 2)
        self.assertEqual(
            primary.cancelling_pair_control(self.planes)["total_cost"], 242
        )
        with self.assertRaisesRegex(ValueError, "signed cancellation"):
            primary.cancelling_pair_control(self.planes, last_weight=1)
        for i in range(56):
            for j in range(56):
                self.assertEqual(
                    primary.tariff(self.planes, [i], [j]),
                    primary.tariff(self.planes, [j], [i]),
                )

    def test_each_live_source_corruption_rejects_both(self):
        for name in primary.PINS:
            with tempfile.TemporaryDirectory() as tmp:
                root, package = self.copy_fixture(tmp)
                source = root / primary.INPUTS / name
                source.write_bytes(source.read_bytes() + b"\n")
                for command in ("verify.py", "independent.py"):
                    run = self.cli(package / command, success=False)
                    self.assertIn("source authentication", run.stderr)

    def test_receipt_failure_never_repairs_or_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, package = self.copy_fixture(tmp)
            result = package / "RESULT.json"
            raw = result.read_bytes()
            value = json.loads(raw)
            value["full_support_global_rank"] = 10
            result.write_text(json.dumps(value))
            changed = result.read_bytes()
            for command in ("verify.py", "independent.py"):
                self.cli(package / command, success=False)
                self.assertEqual(result.read_bytes(), changed)
            self.cli(package / "verify.py", "--emit-to", result, success=False)
            self.assertEqual(result.read_bytes(), changed)
            result.unlink()
            self.cli(package / "verify.py", success=False)
            self.assertFalse(result.exists())
            destination = package / "new.json"
            self.cli(package / "verify.py", "--emit-to", destination)
            self.assertEqual(json.loads(destination.read_bytes()), json.loads(raw))

    def test_changed_manifest_pin_rejects_primary(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, package = self.copy_fixture(tmp)
            manifest = package / "SOURCES.json"
            value = json.loads(manifest.read_bytes())
            value["files"][-1]["sha256"] = "0" * 64
            manifest.write_text(json.dumps(value))
            run = self.cli(package / "verify.py", success=False)
            self.assertIn("live pins changed", run.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
