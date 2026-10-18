#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Subprocess controls for portable, read-only, fail-closed mathematical replay."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
FILES = ("verify.py", "independent.py", "CERTIFICATE.json", "INDEPENDENT.json")


class PackageControls(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="root star controls ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / "isolated package"
        self.package.mkdir()
        for name in FILES:
            shutil.copyfile(HERE / name, self.package / name)

    def run_checker(self, filename):
        return subprocess.run(
            [sys.executable, "-I", "-O", "-B", str(self.package / filename)],
            cwd=self.root, capture_output=True, text=True, timeout=60,
        )

    def hashes(self):
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.package.iterdir() if p.is_file()}

    def test_primary_optimized_relocated_read_only(self):
        before = self.hashes()
        result = self.run_checker("verify.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_MASKED_ROOT_STAR_ASSEMBLY_FLOOR_64", result.stdout)
        self.assertEqual(before, self.hashes())

    def test_independent_optimized_relocated_read_only(self):
        before = self.hashes()
        result = self.run_checker("independent.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_MASKED_ROOT_STAR_INDEPENDENT", result.stdout)
        self.assertEqual(before, self.hashes())

    def test_primary_rejects_changed_atom_count(self):
        path = self.package / "CERTIFICATE.json"
        certificate = json.loads(path.read_text())
        certificate["atoms"]["rank_histogram"]["7"] += 1
        path.write_text(json.dumps(certificate))
        result = self.run_checker("verify.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("certificate differs", result.stderr)

    def test_primary_rejects_missing_receipt(self):
        (self.package / "CERTIFICATE.json").unlink()
        result = self.run_checker("verify.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("PASS_MASKED", result.stdout)

    def test_independent_rejects_changed_quadratic_premise(self):
        path = self.package / "INDEPENDENT.json"
        certificate = json.loads(path.read_text())
        certificate["quadratic_certificate"]["hypothetical_sum_quadratic_value"] = 0
        path.write_text(json.dumps(certificate))
        result = self.run_checker("independent.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("independent receipt mismatch", result.stderr)

    def test_independent_rejects_missing_receipt(self):
        (self.package / "INDEPENDENT.json").unlink()
        result = self.run_checker("independent.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("PASS_MASKED", result.stdout)

    def test_independent_receipts_agree_on_proof_premises(self):
        first = json.loads((self.package / "CERTIFICATE.json").read_text())
        second = json.loads((self.package / "INDEPENDENT.json").read_text())
        self.assertEqual(first["frames"]["count"], second["frames"])
        self.assertEqual(first["frames"]["orthogonal_pair_frame_multiplicities"],
                         second["orthogonal_pair_frame_multiplicities"])
        self.assertEqual(first["atoms"]["rank_histogram"],
                         second["ordered_support_pair_rank_histogram"])
        self.assertEqual(first["atoms"]["beta7_missed_frame_histogram"],
                         second["rank_seven_missed_frame_histogram"])
        self.assertEqual(first["sharp_decoder"]["costs"], second["coordinate_costs"])
        self.assertEqual(first["sharp_decoder"]["cost"], second["lower_bound"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
