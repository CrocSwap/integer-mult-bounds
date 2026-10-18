#!/usr/bin/env python3
"""Independent numeric oracle and artifact/failure controls. Apache-2.0."""

import gzip
import hashlib
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
V = runpy.run_path(str(PACKAGE / "verify.py"))


def decimal_value(value):
    return Decimal(value.numerator) / Decimal(value.denominator)


def oracle_gain(before, after, saving):
    p = 1 - decimal_value(saving)
    return sum(Decimal(n - m) * (Decimal(r).ln() * p).exp()
               for r, (n, m) in enumerate(zip(before, after, strict=True), 1))


def exported_tree(destination):
    package = destination / "research" / PACKAGE.name
    shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
    for entry in json.loads((PACKAGE / "SOURCES.json").read_text())["files"]:
        if entry["usage"] == "input":
            path = destination / entry["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / entry["path"], path)
    return package


def replay(package, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B", "-W", "error",
                           str(package / "verify.py"), *map(str, args)],
                          cwd=package.parent, capture_output=True, text=True,
                          timeout=30, check=False)


class CertificateTests(unittest.TestCase):
    def test_independent_decimal_enclosures_and_root_signs(self):
        words, saving, _ = V["load_sources"]()
        profiles, _ = V["validate_profiles"](words)
        logs = {r: V["log_bounds"](r) for r in range(1, 9)}
        result = json.loads((PACKAGE / "RESULT.json").read_text())
        with localcontext() as context:
            context.prec = 100
            for a in (Fraction(0), saving, Fraction(1, 99), Fraction(1, 50)):
                for rank in range(1, 9):
                    lo, hi = V["power_bounds"](rank, a, logs)
                    actual = (Decimal(rank) if a == 0 else
                              (Decimal(rank).ln() * (1 - decimal_value(a))).exp())
                    self.assertLessEqual(decimal_value(lo), actual)
                    self.assertLessEqual(actual, decimal_value(hi))
                    self.assertLess(hi - lo, Fraction(1, 10**25))
            for pr in (2662, 2712):
                record = result["comparisons"][str(pr)]
                for key, a in (("selected_gain", saving),
                               ("planning_target_gain", Fraction(1, 99))):
                    lo, hi = map(Fraction, record[key])
                    actual = oracle_gain(profiles[2586], profiles[pr], a)
                    self.assertLess(decimal_value(lo), actual)
                    self.assertLess(actual, decimal_value(hi))
                left, right = map(Fraction, record["one_H1_break_even"]["saving_bracket"])
                self.assertEqual(right - left, Fraction(1, 10**12))
                self.assertLess(oracle_gain(profiles[2586], profiles[pr], left), 1)
                self.assertGreater(oracle_gain(profiles[2586], profiles[pr], right), 1)

    def test_primitive_saving_is_not_kappa(self):
        words, saving, kappa = V["load_sources"]()
        profiles, _ = V["validate_profiles"](words)
        logs = {r: V["log_bounds"](r) for r in range(1, 9)}
        correct = V["gain_bounds"](profiles[2586], profiles[2712], saving, logs)
        wrong = V["gain_bounds"](profiles[2586], profiles[2712], Fraction(kappa), logs)
        self.assertLess(wrong[1], correct[0])

    def test_git_free_read_only_replay_and_recompression(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = exported_tree(root)
            source = package / "inputs/PR2712-WORD.json.gz"
            payload = gzip.decompress(source.read_bytes())
            source.write_bytes(gzip.compress(payload, compresslevel=1, mtime=123))
            files = list(root.rglob("*"))
            before = {p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in files if p.is_file()}
            for path in files:
                if path.is_file():
                    path.chmod(0o444)
            result = replay(package)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_P104_FUSION_COST_HEADROOM", result.stdout)
            after = {p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            self.assertFalse((root / ".git").exists())

    def test_changed_source_rejected_before_math(self):
        with tempfile.TemporaryDirectory() as directory:
            package = exported_tree(Path(directory))
            source = package / "inputs/PR2662-WORD.json.gz"
            data = json.loads(gzip.decompress(source.read_bytes()))
            data["program"].pop()
            source.write_bytes(gzip.compress(json.dumps(data).encode(), mtime=0))
            result = replay(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source SHA256", result.stderr)

    def test_changed_receipt_and_output_overwrite_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = exported_tree(Path(directory))
            receipt = package / "RESULT.json"
            original = receipt.read_text()
            data = json.loads(original)
            data["comparisons"]["2712"]["selected_gain"] = ["1", "2"]
            receipt.write_text(json.dumps(data))
            result = replay(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("stored result mismatch", result.stderr)
            receipt.write_text(original)
            target = Path(directory) / "existing.json"
            target.write_text("preserve this\n")
            result = replay(package, "--out", target)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FileExistsError", result.stderr)
            self.assertEqual(target.read_text(), "preserve this\n")

    def test_historical_selected_record_is_frozen_and_authenticated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = exported_tree(root)
            live = root / "certificates/selected-result.json"
            live.parent.mkdir(parents=True)
            live.write_text("deliberately different live record\n")
            result = replay(package)
            self.assertEqual(result.returncode, 0, result.stderr)
            frozen = package / "inputs/SELECTED-AT-BASE.json"
            frozen.write_bytes(frozen.read_bytes() + b"\n")
            result = replay(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source SHA256", result.stderr)

    def test_resource_limits_and_mathematical_boundaries(self):
        with self.assertRaisesRegex(ValueError, "event bound"):
            V["profile_from_word"]({"schema_version": 1, "program": [["sign"]] * 6001})
        with self.assertRaisesRegex(ValueError, "exponential domain"):
            V["exp_negative_bounds"](Fraction(101, 100))
        with self.assertRaisesRegex(ValueError, "binary vector"):
            V["binary_rank"]([512])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "oversized.gz"
            path.write_bytes(gzip.compress(b"0" * 2_000_001))
            with self.assertRaisesRegex(ValueError, "input payload bound"):
                V["read_bounded"](path, True)
        self.assertEqual(V["exp_negative_bounds"](Fraction(0)), (1, 1))
        self.assertEqual(V["log_bounds"](1), (0, 0))
        self.assertEqual(V["binary_rank"]([1, 2, 3]), 2)


if __name__ == "__main__":
    unittest.main()
