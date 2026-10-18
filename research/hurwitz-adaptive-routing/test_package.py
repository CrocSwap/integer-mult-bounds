#!/usr/bin/env python3
"""Offline packaging/failure controls; no expensive repository-wide replay."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hurwitz adaptive test ")
        self.copy = Path(self.temporary.name) / "relocated package"
        shutil.copytree(ROOT, self.copy, ignore=shutil.ignore_patterns("__pycache__", "evidence"))

    def tearDown(self):
        self.temporary.cleanup()

    def run_script(self, name="verify.py", expected=0):
        result = subprocess.run([sys.executable, "-I", "-O", "-B", str(self.copy / name)],
                                cwd=self.temporary.name, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_optimized_relocated_replays(self):
        self.assertIn("PASS_HURWITZ_ADAPTIVE_ROUTING", self.run_script())
        self.assertIn("PASS_HURWITZ_ADAPTIVE_CENSUS", self.run_script("independent_census.py"))

    def test_changed_reference_source_rejected(self):
        reference = self.copy / "reference/PR785-PROOF.md"
        reference.write_text(reference.read_text() + "\nchanged source\n")
        self.assertIn("source digest mismatch", self.run_script(expected=1))

    def test_tampered_census_receipt_rejected(self):
        path = self.copy / "CERTIFICATE.json"
        record = json.loads(path.read_text())
        record["four_port_census"]["functions_checked"] = 65535
        path.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n")
        self.assertIn("certificate differs", self.run_script(expected=1))

    def test_omitted_optimal_header_rejected_independently(self):
        path = self.copy / "CERTIFICATE.json"
        record = json.loads(path.read_text())
        record["four_port_census"]["optimal_nonconstant_headers"].pop()
        path.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n")
        self.assertIn("optimal-header list differs", self.run_script("independent_census.py", expected=1))

    def test_changed_decoder_witness_rejected_independently(self):
        path = self.copy / "CERTIFICATE.json"
        record = json.loads(path.read_text())
        record["four_port_census"]["optimal_nonconstant_headers"][0]["raw_source_pairs_by_header"][0] = [[0, 2]]
        path.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n")
        self.assertIn("source-pair witnesses differ", self.run_script("independent_census.py", expected=1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
