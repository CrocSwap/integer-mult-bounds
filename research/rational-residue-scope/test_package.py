#!/usr/bin/env python3
"""Actual source/receipt corruption and serialization controls. Apache-2.0."""
import gzip
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
V = runpy.run_path(str(HERE / "verify.py"))
C = V["C"]


class PackageTests(unittest.TestCase):
    def clone(self, temporary):
        package = Path(temporary) / "relocated"
        shutil.copytree(HERE, package)
        return package

    def execute(self, package, output):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"),
                               "--output", str(output)], capture_output=True, text=True)

    def test_own_case_recompression_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = self.clone(temporary)
            path = package / "CASE.json.gz"
            value = C["load"](path)
            path.write_bytes(gzip.compress(C["canonical"](value), compresslevel=1, mtime=123456))
            run = self.execute(package, Path(temporary) / "out")
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("PASS_RATIONAL_RESIDUE_SCOPE", run.stdout)

    def test_pinned_code_rejected_before_import(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = self.clone(temporary)
            (package / "vendor/pr1159/dense.py").write_text('raise RuntimeError("must not execute")\n')
            run = self.execute(package, Path(temporary) / "out")
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("source hash mismatch", run.stderr)
            self.assertNotIn("RuntimeError", run.stderr)

    def test_source_container_recompression_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = self.clone(temporary)
            path = package / "vendor/pr1159/CASE.json.gz"
            path.write_bytes(gzip.compress(C["canonical"](C["load"](path)), compresslevel=1, mtime=123456))
            run = self.execute(package, Path(temporary) / "out")
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("source hash mismatch", run.stderr)

    def test_forged_coefficient_case(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = self.clone(temporary)
            path = package / "CASE.json.gz"
            case = C["load"](path)
            case["residue_coefficients"][0][0][0] ^= 1
            path.write_bytes(gzip.compress(C["canonical"](case), mtime=0))
            run = self.execute(package, Path(temporary) / "out")
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("complete regenerated CASE.json.gz", run.stderr)

    def test_underpriced_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = self.clone(temporary)
            path = package / "EXPECTED.json"
            report = C["load"](path)
            report["preparation"]["external_memory"]["head_bit_moves"] = 0
            path.write_text(json.dumps(report))
            run = self.execute(package, Path(temporary) / "out")
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("complete regenerated EXPECTED.json", run.stderr)

    def test_output_must_be_new(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "existing"
            output.mkdir()
            run = self.execute(HERE, output)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("FileExistsError", run.stderr)

    def test_duplicate_and_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.json"
            for text, reason in (('{"x":1,"x":2}', "duplicate JSON key"),
                                 ('{"x":Infinity}', "nonfinite JSON")):
                path.write_text(text)
                with self.assertRaisesRegex(ValueError, reason):
                    C["load"](path)

    def test_actual_source_exceeds_promised_bound(self):
        with self.assertRaisesRegex(ValueError, "actual input exceeds declared bound"):
            V["A"]["lifted_replay"]([[0, 1, 0, 1]], [[[1]]], [[2], [0], [0], [0], [0]],
                                    [[[1]]], 4, None, 1, 0)


if __name__ == "__main__":
    unittest.main()
