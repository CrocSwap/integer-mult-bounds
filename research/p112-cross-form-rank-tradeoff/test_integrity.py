#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Relocated replay and corruption rejection through the public verifier CLI."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GEOMETRY = Path("research/p112-single-lift/reference-geometry.json")


class IntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="p112-cross-form-replay-")
        cls.root = Path(cls.temp.name)
        cls.package = cls.root / "research/p112-cross-form-rank-tradeoff"
        shutil.copytree(HERE, cls.package, ignore=shutil.ignore_patterns("__pycache__", "*.olean"))
        (cls.root / GEOMETRY).parent.mkdir(parents=True)
        shutil.copyfile(ROOT / GEOMETRY, cls.root / GEOMETRY)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_replay(self, optimized=False):
        return subprocess.run([sys.executable, "-I", "-B"] + (["-O"] if optimized else [])
                              + [str(self.package / "verify.py")], cwd=self.root,
                              text=True, capture_output=True, timeout=120)

    def test_relocation_optimized(self):
        result = self.run_replay(True)
        self.assertEqual(result.returncode, 0, result.stderr[-1500:])
        self.assertIn("PASS_P112_CROSS_FORM_RANK_TRADEOFF", result.stdout)

    def mutate(self, path, transform, expected):
        original = path.read_bytes()
        try:
            path.write_bytes(transform(original))
            result = self.run_replay(True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(expected, result.stderr)
        finally:
            path.write_bytes(original)

    def test_source_drift(self):
        self.mutate(self.root / GEOMETRY, lambda b: b + b"\n", "input pin:")

    def test_predecessor_drift(self):
        self.mutate(self.package / "sources/PR2294-PROOF.md", lambda b: b + b"\n",
                    "predecessor pin:")

    def test_false_receipt(self):
        def alter(payload):
            result = json.loads(payload)
            result["rank_region"]["certified_pairs"] = 100
            return json.dumps(result).encode()
        self.mutate(self.package / "RESULT.json", alter, "committed result equality")

    def test_receipt_type_change(self):
        def alter(payload):
            result = json.loads(payload)
            result["rank_region"]["unresolved_pairs"][0][0] = True
            return json.dumps(result).encode()
        self.mutate(self.package / "RESULT.json", alter, "committed result equality")


if __name__ == "__main__":
    unittest.main()
