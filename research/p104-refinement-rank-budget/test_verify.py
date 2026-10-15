#!/usr/bin/env python3
"""CLI and semantic failure tests for the scoped P104 rank-budget checker."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def load_checker():
    spec = importlib.util.spec_from_file_location("p104_rank_budget", PACKAGE / "verify.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the local checker")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    return checker


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="p104-budget-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / PACKAGE.relative_to(ROOT)
        self.package.mkdir(parents=True)
        for filename in ("verify.py", "SOURCES.json", "EXPECTED.json"):
            shutil.copyfile(PACKAGE / filename, self.package / filename)
        sources = json.loads((PACKAGE / "SOURCES.json").read_text())
        self.files = list(self.package.iterdir())
        for record in sources["files"]:
            if record["usage"] == "input":
                destination = self.root / record["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / record["path"], destination)
                self.files.append(destination)

    def run_cli(self, *arguments, optimized=False):
        flags = ["-I", "-X", "dev", "-W", "error", "-B"]
        if optimized:
            flags.append("-O")
        return subprocess.run(
            [sys.executable, *flags, str(self.package / "verify.py"), *arguments],
            cwd=self.root, text=True, capture_output=True, timeout=30, check=False,
        )

    def assert_pass(self, process):
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stderr, "")
        result = json.loads(process.stdout)
        self.assertEqual(result["status"], "PASS_P104_REFINEMENT_RANK_BUDGET")
        bill = result["conditional_no_progress_credit_budget"]
        self.assertEqual(bill["added_rank_lower_bound_per_call"], 48)
        self.assertEqual(bill["zero_saving_moment_lower_bound"], "585/584")
        self.assertEqual(bill["credit_needed_for_strict_positive_saving_gt"], "104/9")
        self.assertEqual(len(result["rejected_controls"]), 5)
        return result

    def test_normal_replay_is_read_only(self):
        before = {path: hashlib.sha256(path.read_bytes()).digest() for path in self.files}
        self.assert_pass(self.run_cli())
        self.assertEqual({path: hashlib.sha256(path.read_bytes()).digest() for path in self.files}, before)
        self.assertEqual({path for path in self.root.rglob("*") if path.is_file()}, set(self.files))

    def test_optimized_replay(self):
        self.assert_pass(self.run_cli(optimized=True))

    def test_missing_source_rejects(self):
        source = self.root / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
        source.unlink()
        process = self.run_cli()
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("FileNotFoundError", process.stderr)
        self.assertIn("LOWRANK-WITNESS.json", process.stderr)

    def test_corrupt_source_rejects_before_geometry(self):
        source = self.root / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
        source.write_bytes(b"not json")
        process = self.run_cli()
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("source hash mismatch", process.stderr)
        self.assertNotIn("JSONDecodeError", process.stderr)

    def test_oversized_source_rejects_before_hashing(self):
        source = self.root / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
        source.write_bytes(b"x" * 1_048_577)
        process = self.run_cli()
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("input size limit", process.stderr)
        self.assertNotIn("source hash mismatch", process.stderr)

    def test_count_preserving_receipt_corruption_rejects(self):
        path = self.package / "EXPECTED.json"
        receipt = json.loads(path.read_text())
        receipt["survivor_lines"][0] ^= 1
        path.write_text(json.dumps(receipt))
        process = self.run_cli()
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("complete expected receipt", process.stderr)

    def test_output_is_exclusive(self):
        path = self.root / "receipt.json"
        result = self.assert_pass(self.run_cli("--out", str(path)))
        self.assertEqual(json.loads(path.read_text()), result)
        original = path.read_bytes()
        process = self.run_cli("--out", str(path))
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("FileExistsError", process.stderr)
        self.assertEqual(path.read_bytes(), original)

    def test_raw_mass_boundary(self):
        checker = load_checker()
        self.assertEqual(Fraction(checker.budget(44, 8)["zero_saving_moment_lower_bound"]),
                         Fraction(15183, 15184))
        self.assertEqual(Fraction(checker.budget(45, 8)["zero_saving_moment_lower_bound"]),
                         Fraction(60741, 60736))

    def test_two_entering_crossings_need_rank_not_endpoint_count(self):
        checker = load_checker()
        survivors = frozenset(1 << i for i in range(8))
        hull = frozenset(range(256))
        path = [checker.FULL, checker.span([256, 1, 2]), checker.span([256]), checker.span([])]
        self.assertEqual(checker.charged_path(path, [6, 2, 1], survivors, hull), 2)
        with self.assertRaisesRegex(ValueError, "charged its rank"):
            checker.charged_path(path, [1, 1, 1], survivors, hull)


if __name__ == "__main__":
    unittest.main()
