#!/usr/bin/env python3
"""Behavioral and implementation-mutation controls for the actual replay CLI."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
EXPECTED = "PASS_CLEAN_WORKSPACE_COMPRESSION words=69728 candidates=0 no_new_kappa\n"


class ReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="clean replay controls ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / "research" / PACKAGE.name
        shutil.copytree(PACKAGE, self.package, ignore=shutil.ignore_patterns("__pycache__"))
        sources = json.loads((PACKAGE / "SOURCES.json").read_text())
        for source in sources["files"]:
            if source["usage"] == "input":
                destination = self.root / source["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / source["path"], destination)

    def run_replay(self, optimized: bool = True, extra: tuple[str, ...] = ()) -> subprocess.CompletedProcess:
        options = ["-I", "-B", "-W", "error"]
        if optimized:
            options.append("-O")
        return subprocess.run([sys.executable, *options, str(self.package / "verify.py"), *extra],
                              cwd=self.root, capture_output=True, text=True, timeout=60, check=False)

    def rewrite_engine(self, old: str, new: str) -> None:
        path = self.package / "engine.cpp"
        contents = path.read_text()
        self.assertEqual(contents.count(old), 1)
        path.write_text(contents.replace(old, new))

    def assert_rejected(self, run: subprocess.CompletedProcess, reason: str) -> None:
        self.assertNotEqual(run.returncode, 0)
        self.assertNotIn("PASS_CLEAN_WORKSPACE_COMPRESSION", run.stdout)
        self.assertIn(reason, run.stderr)

    def test_normal_and_optimized_relocated_read_only(self) -> None:
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in self.package.iterdir() if p.is_file()}
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                run = self.run_replay(optimized)
                self.assertEqual((run.returncode, run.stdout, run.stderr), (0, EXPECTED, ""))
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.package.iterdir() if p.is_file()}
        self.assertEqual(after, before)

    def test_receipt_corruption(self) -> None:
        path = self.package / "RESULT.json"
        path.write_text(path.read_text().replace('"oracle_probes": 1223', '"oracle_probes": 1224'))
        self.assert_rejected(self.run_replay(), "receipt mismatch")

    def test_no_quotient_implementation_mutant(self) -> None:
        self.rewrite_engine("grouped[relation.representative[mask]] ^= polynomial[mask];",
                            "grouped[mask] ^= polynomial[mask];")
        self.assert_rejected(self.run_replay(), "independent eigenvector oracle mismatch")

    def test_vacuous_enumeration_implementation_mutant(self) -> None:
        self.rewrite_engine("if (!canonical_rows(encoded, dimension, x)) continue;",
                            "if (!canonical_rows(encoded, dimension, x) || dimension >= 2) continue;")
        self.assert_rejected(self.run_replay(), "missing oracle probe")

    def test_rank_threshold_implementation_mutant(self) -> None:
        self.rewrite_engine("minimum_support >= 3", "minimum_support >= 4")
        self.assert_rejected(self.run_replay(), "rank-three support rejected")

    def test_source_corruption_and_invalid_cli(self) -> None:
        path = self.root / "research/bit-three-register-lower-bound/README.md"
        path.write_bytes(path.read_bytes() + b"\nchanged\n")
        self.assert_rejected(self.run_replay(), "source input changed")
        run = self.run_replay(extra=("--not-an-option",))
        self.assertEqual(run.returncode, 2)
        self.assertIn("unrecognized arguments", run.stderr)


if __name__ == "__main__":
    unittest.main()
