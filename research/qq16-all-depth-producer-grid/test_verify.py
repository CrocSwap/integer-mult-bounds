"""Algebraic and source/receipt failure controls. Apache-2.0."""

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import binding
import independent
import verify


class Capture(verify.Envelope):
    def __init__(self):
        super().__init__()
        self.values = []

    def observe(self, value, stage):
        self.values.append(value)
        return super().observe(value, stage)


class Controls(unittest.TestCase):
    def test_tensor_line_dominates_every_interior(self):
        cases = 0
        for magnitude in (Fraction(1), Fraction(3, 2)):
            for grid in (-2, 3):
                for slope in (0, 2):
                    for depth in range(1, 6):
                        value = verify.Bound(magnitude, grid, slope, slope)
                        envelope = Capture()
                        envelope.line(value)
                        x = (
                            magnitude * 2 ** (slope * (depth - 1)),
                            grid + slope * (depth - 1),
                        )
                        for _ in range(depth):
                            pair = independent.add(x, x)
                            cross = independent.add(pair, pair)
                            x = independent.scaled(cross, Fraction(1, 2))
                            for actual, bound in zip((pair, cross, x), envelope.values):
                                self.assertLessEqual(
                                    actual[0],
                                    bound.magnitude * 2 ** (bound.a * (depth - 1)),
                                )
                                self.assertLessEqual(
                                    actual[1], bound.grid + bound.b * (depth - 1)
                                )
                            cases += 1
        self.assertEqual(cases, 120)

    def test_carried_stage_is_required(self):
        data = binding.load()
        actual = independent.replay(1, data)
        reset = independent.replay(1, data, reset=True)
        self.assertNotEqual(actual["stages"]["B_1_2"], reset["stages"]["B_1_2"])
        self.assertLess(reset["grid"], actual["grid"])

    def test_invalid_native_and_cover_controls(self):
        packet, recipes, _ = binding.load()
        row = next(r for r in recipes["children"] if r["rank"])
        broken = json.loads(json.dumps(row["right"]))
        broken["matrix_rows"] = [0] * 9
        with self.assertRaisesRegex(ValueError, "invertible"):
            binding.monomial(broken)
        name = next(
            e[2] for e in binding.expand(packet, "B_1_2") if e[0] == "cover_map"
        )
        packet["map_registry"][name]["owner_right_matrix_columns"] = [0] * 73
        with self.assertRaisesRegex(ValueError, "invertible owner"):
            binding.cover_maps(packet)

    def test_zero_and_invalid_domain(self):
        self.assertEqual(verify.Envelope().line(verify.ZERO), verify.ZERO)
        self.assertEqual(verify.UNIT.scale(0), verify.ZERO)
        with self.assertRaisesRegex(ValueError, "dyadic"):
            verify.UNIT.scale(Fraction(1, 3))
        with self.assertRaisesRegex(ValueError, "nonnegative slopes"):
            verify.Bound(Fraction(1), 0, -1, 0)
        for depth in (0, True, 9):
            with self.assertRaises(ValueError):
                independent.Numeric(depth)

    def private_copy(self, root):
        target = root / "research/qq16-all-depth-producer-grid"
        for source in binding.HERE.rglob("*"):
            mode = source.lstat().st_mode
            self.assertTrue(stat.S_ISDIR(mode) or stat.S_ISREG(mode))
        shutil.copytree(binding.HERE, target, copy_function=shutil.copyfile)
        manifest = json.loads((target / "SOURCES.json").read_text())
        for row in manifest["files"]:
            if row["usage"] == "input":
                destination = root / row["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(binding.ROOT / row["path"], destination)
        return target

    def reject(self, target, expected):
        env = dict(os.environ)
        env["PYTHONPYCACHEPREFIX"] = str(target.parents[1] / "private-bytecode")
        result = subprocess.run(
            [sys.executable, "-O", "-Werror", "-B", str(target / "verify.py")],
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
            env=env,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(expected, result.stderr)

    def test_private_source_and_receipt_mutants(self):
        with tempfile.TemporaryDirectory(prefix="qq16-all-depth-controls-") as work:
            root = Path(work)
            target = self.private_copy(root)
            path = target / "SOURCES.json"
            original = path.read_bytes()
            for mutation in ("schema", "usage", "extra"):
                value = json.loads(original)
                if mutation == "schema":
                    value["schema_version"] = True
                elif mutation == "usage":
                    next(r for r in value["files"] if r["usage"] == "input")[
                        "usage"
                    ] = "provenance"
                else:
                    value["files"].append(value["files"][0])
                path.write_text(json.dumps(value))
                self.reject(target, "fixed source manifest")
            path.write_bytes(original)
            receipt = target / "RESULT.json"
            saved = receipt.read_bytes()
            value = json.loads(saved)
            value["grid_slope"] = True
            receipt.write_text(json.dumps(value))
            self.reject(target, "receipt mismatch")
            receipt.write_bytes(saved)
            source = root / binding.CERT
            source.write_bytes(source.read_bytes() + b"changed")
            self.reject(target, "input hash")


if __name__ == "__main__":
    unittest.main(verbosity=2)
