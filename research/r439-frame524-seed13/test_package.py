#!/usr/bin/env python3
"""Relocation and rejection checks for the frame-524 evidence package.

Only the verifier, independent factor checker, committed receipts and pinned
source closure are copied. No Git checkout, search module, native build, or
original working-directory state is available to the subprocesses.
Ross Richardson, with substantial OpenAI Codex assistance; Apache-2.0.
"""

from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = Path("research/r439-frame524-seed13")


class PackageChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="frame524 review with spaces ")
        cls.root = Path(cls.scratch.name) / "relocated repo with spaces"
        cls.here = cls.root / PACKAGE
        cls.here.mkdir(parents=True)
        pins = json.loads((HERE / "SOURCES.json").read_text())
        for name in pins["sha256"]:
            destination = cls.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        for name in ("verify.py", "factor_check.py", "SOURCES.json",
                     "CANDIDATE.json", "CERTIFICATE.json"):
            shutil.copyfile(HERE / name, cls.here / name)
        cls.caller = Path(cls.scratch.name) / "unrelated caller with spaces"
        cls.caller.mkdir()

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def execute(self, *arguments, optimized=False):
        flags = ["-I", "-B"] + (["-O"] if optimized else [])
        return subprocess.run(
            [sys.executable, *flags, str(self.here / "verify.py"), *map(str, arguments)],
            cwd=self.caller, capture_output=True, text=True, timeout=120)

    def rejected(self, reason, *arguments, optimized=True):
        result = self.execute(*arguments, optimized=optimized)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(reason, result.stderr, result.stdout + result.stderr)
        self.assertNotIn("PASS_R439_FRAME524 ", result.stdout)
        return result

    @contextmanager
    def mutate_json(self, filename, change):
        path = self.here / filename
        original = path.read_bytes()
        value = json.loads(original)
        change(value)
        path.write_text(json.dumps(value) + "\n")
        try:
            yield
        finally:
            path.write_bytes(original)

    def test_01_relocated_replay_and_optimized_replay(self):
        self.assertFalse((self.here / "search.py").exists())
        self.assertFalse((self.root / ".git").exists())
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self.execute(optimized=optimized)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("PASS_R439_FRAME524 block=41->27", result.stdout)
                self.assertIn("no_new_kappa", result.stdout)

    def test_02_corrupted_certificate_is_rejected(self):
        def change(value):
            value["candidate"]["invoice"]["ADDs"] -= 1
        with self.mutate_json("CERTIFICATE.json", change):
            self.rejected("certificate differs from fresh replay")

    def test_03_corrupted_pinned_source_is_rejected(self):
        relative = "research/e8-bit-p111-tuned/code/xcheck_p.py"
        path = self.root / relative
        original = path.read_bytes()
        path.write_bytes(original + b"\n# damaged source\n")
        try:
            self.rejected("source mismatch: " + relative)
        finally:
            path.write_bytes(original)

    def test_04_false_donor_metadata_is_rejected(self):
        def change(value):
            # The first identity destination is 81; register 8 is a distinct
            # donor, so this changes its integer target row without changing
            # the separately encoded primitive operation witness.
            self.assertEqual(value["factors"][0]["optimal_order"][0], 81)
            value["factors"][0]["donor_coefficients"][0][0] += 1
        with self.mutate_json("CANDIDATE.json", change):
            self.rejected("candidate donor coefficients do not realize the target row")

    def test_05_false_optimum_coverage_is_rejected(self):
        def change(value):
            value["factors"][0]["coverage"]["minimum_cost_orders"] += 1
        with self.mutate_json("CANDIDATE.json", change):
            self.rejected("candidate coverage mismatch: minimum_cost_orders")

    def test_06_inconsistent_source_base_is_rejected(self):
        def change(value):
            value["base_commit"] = "0" * 40
        with self.mutate_json("SOURCES.json", change):
            self.rejected("candidate metadata mismatch: base_commit")

    def test_07_existing_word_output_is_preserved(self):
        destination = self.caller / "existing word with spaces.json.gz"
        sentinel = b"existing output must survive\x00\xff"
        destination.write_bytes(sentinel)
        try:
            result = self.execute("--word", destination, optimized=True)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("output already exists", result.stderr)
            self.assertEqual(destination.read_bytes(), sentinel)
        finally:
            destination.unlink()


if __name__ == "__main__":
    unittest.main(verbosity=2)
