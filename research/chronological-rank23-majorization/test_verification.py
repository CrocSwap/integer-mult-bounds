#!/usr/bin/env python3
"""Defect-sensitive checks of the two mathematical evidence consumers."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.primary = module("verify")
        cls.secondary = module("independent")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="rank23-evidence-")
        self.root = Path(self.temp.name)
        self.pkg = self.root / "research/chronological-rank23-majorization"
        self.pkg.mkdir(parents=True)
        for name in ("verify.py", "independent.py", "RESULT.json", "INDEPENDENT.json"):
            shutil.copy2(HERE / name, self.pkg / name)
        source = self.root / self.primary.ARCHIVE
        source.parent.mkdir(parents=True)
        shutil.copy2(ROOT / self.primary.ARCHIVE, source)

    def tearDown(self):
        for directory, dirs, files in os.walk(self.root):
            os.chmod(directory, 0o755)
            for name in files:
                os.chmod(Path(directory) / name, 0o644)
        self.temp.cleanup()

    def run_checker(self, name, *args):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(self.pkg / name), *args],
                              cwd=self.root, capture_output=True, text=True, timeout=30)

    def expect_failure(self, name, fragment):
        result = self.run_checker(name)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(fragment, result.stderr)

    def test_actual_detector_removal_exposes_control_failure(self):
        # The suite must go red if the actual mathematical detector is removed.
        with patch.object(self.primary, "verify_majorization", return_value=None):
            with self.assertRaisesRegex(self.primary.Invalid, "unexpected acceptance"):
                self.primary.controls()
        with patch.object(self.secondary, "check_majorization", return_value=None):
            with self.assertRaisesRegex(self.secondary.Rejected, "control-accepted"):
                self.secondary.control_checks()

    def test_independent_partition_counts_agree(self):
        first = self.primary.compute()
        second = self.secondary.compute_record()
        expected = {tuple(row["ranks"]): row["all_legal_partitions"] for row in first["run_types"]}
        observed = {tuple(row["run"]): row["chronological_partitions"] for row in second["run_types"]}
        self.assertEqual(expected, observed)
        self.assertEqual(sum(expected.values()), 23499934)

    def test_missing_duplicate_and_balanced_corruption_fail(self):
        for script, receipt in (("verify.py", "RESULT.json"), ("independent.py", "INDEPENDENT.json")):
            with self.subTest(script=script):
                path = self.pkg / receipt
                original = path.read_bytes()
                path.unlink()
                result = self.run_checker(script)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(path.exists(), "missing evidence must not be regenerated")
                path.write_text('{"duplicate":1,"duplicate":2}')
                self.expect_failure(script, "duplicate")
                value = json.loads(original)
                if script == "verify.py":
                    # Same count and total rank mass: 2+4 -> 3+3. Aggregate
                    # mass-only validation would incorrectly accept this.
                    profile = value["optimal_profile"]
                    profile["2"] -= 1
                    profile["4"] -= 1
                    profile["3"] += 2
                else:
                    value["run_types"][-1]["chronological_partitions"] += 1
                path.write_text(json.dumps(value))
                result = self.run_checker(script)
                self.assertNotEqual(result.returncode, 0, "corrupt evidence accepted")
                value = json.loads(original)
                key = next(k for k, v in value.items() if type(v) is int)
                value[key] = float(value[key])
                path.write_text(json.dumps(value))
                result = self.run_checker(script)
                self.assertNotEqual(result.returncode, 0, "wrong integer type accepted")
                path.write_bytes(original)

    def test_source_drift_rejected_by_both(self):
        path = self.root / self.primary.ARCHIVE
        original = path.read_bytes()
        path.write_bytes(original + b"source drift")
        self.expect_failure("verify.py", "archive pin")
        self.expect_failure("independent.py", "archive-sha256")

    def test_explicit_generation_matches_and_refuses_overwrite(self):
        path = self.pkg / "RESULT.json"
        original = path.read_bytes()
        path.unlink()
        result = self.run_checker("verify.py", "--write")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.read_bytes(), original)
        result = self.run_checker("verify.py", "--write")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FileExistsError", result.stderr)
        self.assertEqual(path.read_bytes(), original)
        independent = self.run_checker("independent.py", "--json")
        self.assertEqual(independent.returncode, 0, independent.stderr)
        self.assertEqual(json.loads(independent.stdout), json.loads((self.pkg / "INDEPENDENT.json").read_text()))

    def test_optimized_relocated_read_only_replay(self):
        def digests():
            return {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in self.root.rglob("*") if path.is_file()}
        before = digests()
        for directory, dirs, files in os.walk(self.root):
            for name in files:
                os.chmod(Path(directory) / name, 0o444)
            os.chmod(directory, 0o555)
        for script in ("verify.py", "independent.py"):
            result = self.run_checker(script)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(digests(), before)


if __name__ == "__main__":
    unittest.main()
