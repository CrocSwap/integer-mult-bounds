#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Semantic boundary and fail-closed replay controls, including optimized Python."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as primary
import independent as other
from common import HERE, read


def export(destination):
    package = destination / "research" / HERE.name
    shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
    for source in read(HERE / "SOURCES.json")["files"]:
        if source["usage"] == "input":
            target = destination / source["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE.parents[1] / source["path"], target)
    return package


def run(package, script="verify.py", *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / script), *args],
                          cwd=package.parent.parent, capture_output=True, text=True,
                          encoding="utf-8", timeout=120)


class Controls(unittest.TestCase):
    def test_model_and_sharpness_boundaries(self):
        for word, r in [([("u", 1, 1)], 2), ([("a", 0, 1)], 2),
                        ([("a", True, 1)], 2), ([("a", 4, 1)], 2), ([], True)]:
            with self.assertRaises(ValueError):
                primary.formal(word, r)
        with self.assertRaises(ValueError):
            primary.fixture((4,), 2)  # pure central target is not in the sharp family
        self.assertEqual(primary.floor((5,)), [2, 2, 2])
        self.assertEqual(primary.floor((3,)), [2, 2, 2])
        self.assertEqual(primary.floor((1, 2)), [2, 4, 2])
        self.assertEqual(len(primary.DIRECT[4]), 8)
        self.assertEqual(sum(primary.floor((4,))), 6)  # no false claim of sharpness

    def test_dirty_kernel_and_legitimate_dirty_loops(self):
        word, target = primary.fixture((5, 6), 3)
        # Two repeated noncoordinate nilpotent factors restore the extra row exactly.
        loop = [("a", 4, 1), ("a", 4, 1)]
        self.assertEqual(primary.formal(loop + word, 3), target)
        self.assertEqual(other.regular_word(loop + word, 3), other.regular_word(word, 3))
        self.assertNotEqual(primary.formal(loop[:1] + word, 3), target)
        # A diagnostic extra-role error is invisible in Q and on clean-extra inputs.
        bad = dict(target)
        for g in (0, 1, 32, 33):
            rows = list(bad.get(g, (0, 0, 0)))
            rows[-1] ^= 4
            bad[g] = tuple(rows)
        bad = {g: rows for g, rows in bad.items() if any(rows)}
        self.assertNotEqual(bad, target)
        self.assertEqual(primary.formal_image(bad, 3), primary.formal_image(target, 3))
        for g in set(bad) | set(target):
            diff = [a ^ b for a, b in zip(bad.get(g, (0, 0, 0)), target.get(g, (0, 0, 0)))]
            self.assertEqual([v & 3 for v in diff], [0, 0, 0])
        changed = 0
        for h in range(64):
            difference = 0
            for g in (0, 1, 32, 33):
                difference ^= 1 << other.GROUP[g][h]
            self.assertEqual(difference.bit_count(), 4)
            changed += difference != 0
        self.assertEqual(changed, 64)

    def test_both_spans_and_rank_price(self):
        xs, ys = [1, 2, 3], [1, 1, 1]
        self.assertEqual(primary.rank(xs), 2)
        self.assertEqual(primary.rank(ys), 1)
        summed = [0, 0]
        for x, y in zip(xs, ys):
            summed = [a ^ b for a, b in zip(summed, primary.outer(x, y, 2))]
        self.assertEqual(summed, [0, 0])
        # A rank-two coupling would act on both roles per letter at an illegal unit price.
        self.assertNotIn((1, 2), [primary.outer(x, y, 2) for x in range(1, 4) for y in range(1, 4)])
        expanded = [(a, 1 << role, 1 << role) for a in "abab" for role in range(2)]
        self.assertEqual(primary.formal(expanded, 2), {8: (1, 2)})
        self.assertEqual(sum(primary.floor((1, 1))), 8)
        # Formal noncommutative order must be preserved, even if some targets are involutions.
        self.assertNotEqual(primary.formal([("a", 1, 1), ("b", 1, 1)], 1),
                            primary.formal([("b", 1, 1), ("a", 1, 1)], 1))

    def test_primary_and_independent_receipt_corruption(self):
        for name, key, script in [("EXPECTED.json", "formal_witnesses", "verify.py"),
                                  ("INDEPENDENT.json", "faithful_basis_columns", "independent.py")]:
            with tempfile.TemporaryDirectory() as tmp:
                package = export(Path(tmp))
                data = read(package / name)
                data[key] -= 1
                (package / name).write_text(json.dumps(data), encoding="utf-8")
                result = run(package, script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("receipt mismatch", result.stderr)

    def test_missing_duplicate_nonfinite_and_typed_receipts(self):
        for change in ("missing", "duplicate", "nonfinite", "bool"):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                package = export(Path(tmp))
                path = package / "EXPECTED.json"
                original = path.read_text(encoding="utf-8")
                if change == "missing":
                    path.unlink()
                elif change == "duplicate":
                    path.write_text(original.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1'), encoding="utf-8")
                elif change == "nonfinite":
                    path.write_text(original.replace('"schema_version": 1', '"schema_version": NaN'), encoding="utf-8")
                else:
                    path.write_text(original.replace('"schema_version": 1', '"schema_version": true'), encoding="utf-8")
                self.assertNotEqual(run(package).returncode, 0)
                if change == "missing":
                    self.assertFalse(path.exists())

    def test_source_drift_and_missing_inventory(self):
        for mode in ("bytes", "inventory"):
            with tempfile.TemporaryDirectory() as tmp:
                package = export(Path(tmp))
                data = read(package / "SOURCES.json")
                record = next(x for x in data["files"] if x["usage"] == "input")
                if mode == "bytes":
                    with (Path(tmp) / record["path"]).open("ab") as stream:
                        stream.write(b"\nchanged input\n")
                else:
                    data["files"].remove(record)
                    (package / "SOURCES.json").write_text(json.dumps(data), encoding="utf-8")
                self.assertNotEqual(run(package).returncode, 0)

    def test_occupied_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = export(Path(tmp))
            occupied = Path(tmp) / "occupied.json"
            occupied.write_bytes(b"sentinel\n")
            result = run(package, "verify.py", "--write", str(occupied))
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(occupied.read_bytes(), b"sentinel\n")

    def test_readonly_optimized_relocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = export(root)
            files = sorted(p for p in root.rglob("*") if p.is_file())
            before = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            for file in files:
                file.chmod(0o444)
            directories = sorted((p for p in root.rglob("*") if p.is_dir()), reverse=True)
            for directory in directories:
                directory.chmod(0o555)
            try:
                for script in ("verify.py", "independent.py"):
                    result = run(package, script)
                    self.assertEqual(result.returncode, 0, result.stderr)
                after = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in root.rglob("*") if p.is_file()}
                self.assertEqual(before, after)
            finally:
                for directory in directories:
                    directory.chmod(0o755)
                for file in files:
                    file.chmod(0o644)


if __name__ == "__main__":
    unittest.main(verbosity=2)
