#!/usr/bin/env python3
"""Relocation and evidence-corruption controls for the isolated research package."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class PackageChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="e8 joint reader ")
        self.root = Path(self.temp.name) / "relocated package"
        shutil.copytree(HERE, self.root, ignore=shutil.ignore_patterns("__pycache__"))

    def tearDown(self):
        self.temp.cleanup()

    def run_script(self, script, *args, optimized=True):
        flags = ["-I", "-B"] + (["-O"] if optimized else [])
        return subprocess.run([sys.executable, *flags, str(self.root / script), *map(str, args)],
                              cwd=self.temp.name, capture_output=True, text=True, timeout=60)

    def require_pass(self, result, marker):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(marker, result.stdout)

    def require_failure(self, result, marker):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(marker, result.stderr)

    def test_relocated_optimized_replay_and_identical_regeneration(self):
        self.require_pass(self.run_script("verify.py"), "PASS_E8_JOINT_READER")
        self.require_pass(self.run_script("independent_check.py"), "PASS_E8_JOINT_INDEPENDENT")
        output = self.root / "regenerated.json"
        self.require_pass(self.run_script("verify.py", "--write", output), "PASS_E8_JOINT_READER")
        self.assertEqual(output.read_bytes(), (self.root / "CERTIFICATE.json").read_bytes())

    def test_primary_rejects_changed_cost_bound(self):
        path = self.root / "CERTIFICATE.json"
        receipt = json.loads(path.read_text())
        receipt["bounds"][36]["combined_lower_bound"] -= 1
        path.write_text(json.dumps(receipt))
        self.require_failure(self.run_script("verify.py"), "certificate mismatch")

    def test_both_reject_changed_flat_capacity(self):
        path = self.root / "CERTIFICATE.json"
        receipt = json.loads(path.read_text())
        receipt["independent_summary"]["flat_capacities"][5] = 21
        path.write_text(json.dumps(receipt))
        self.require_failure(self.run_script("verify.py"), "certificate mismatch")
        self.require_failure(self.run_script("independent_check.py"), "independent_summary mismatch")

    def test_source_corruption_rejected_before_output_write(self):
        source = self.root / "sources/pr631/README.md"
        source.write_bytes(source.read_bytes() + b"\ncorruption\n")
        output = self.root / "must remain unchanged.json"
        output.write_text("sentinel")
        result = self.run_script("verify.py", "--write", output)
        self.require_failure(result, "source SHA256 mismatch")
        self.assertEqual(output.read_text(), "sentinel")

    def test_pinned_predecessor_and_its_negative_controls(self):
        result = self.run_script("sources/pr631/verify.py", "--negative-controls", optimized=False)
        self.require_pass(result, "PASS: optimum star cost/port among <=35 punctures")
        self.assertIn("rejected corrupt geometry, parity and flat", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
