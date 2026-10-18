#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Real source/receipt corruptions and boundary controls for the B509 package."""
from pathlib import Path
import copy
import gzip
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIMARY = runpy.run_path(str(HERE / "verify.py"))


class PackageControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = json.loads(gzip.decompress((ROOT / PRIMARY["INPUTS"][0]).read_bytes()))

    def run_copy(self, mutation=None, errors=None):
        with tempfile.TemporaryDirectory(prefix="b509-check-") as tmp:
            root = Path(tmp)
            package = root / "research" / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            for name in PRIMARY["INPUTS"]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            if mutation:
                mutation(root, package)
            for script in ("verify.py", "independent.py"):
                result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / script)],
                                        cwd=root, capture_output=True, text=True, timeout=90)
                if errors:
                    self.assertNotEqual(result.returncode, 0, script + " accepted corruption")
                    self.assertIn(errors[script], result.stderr)
                else:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("PASS_", result.stdout)

    @staticmethod
    def receipt_mutator(change):
        def mutate(_root, package):
            path = package / "CERTIFICATE.json"
            receipt = json.loads(path.read_text())
            change(receipt)
            path.write_text(json.dumps(receipt))
        return mutate

    def test_relocated_optimized_replays(self):
        self.run_copy()

    def test_missing_inverse_donor_rejected_by_both_engines(self):
        def change(r):
            r["shared"]["inverse_rows"][0] ^= 2
        self.run_copy(self.receipt_mutator(change), {
            "verify.py": "certificate differs", "independent.py": "inverse Boolean map"})

    def test_undercharged_carrier_bill_rejected_by_both_engines(self):
        def change(r):
            r["shared"]["minimal_block_climbs"]["2"] = 6
        self.run_copy(self.receipt_mutator(change), {
            "verify.py": "certificate differs", "independent.py": "all-carrier climb bill"})

    def test_false_rank_three_receipt_rejected_by_both_engines(self):
        def change(r):
            r["shared"]["footprints"][1]["two_sided_rank"] = 3
        self.run_copy(self.receipt_mutator(change), {
            "verify.py": "certificate differs", "independent.py": "Boolean/minor footprint"})

    def test_source_drift_rejected_by_both_engines(self):
        def change(root, _package):
            path = root / PRIMARY["INPUTS"][0]
            word = json.loads(gzip.decompress(path.read_bytes()))
            word["B"][283][1] = 22
            path.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
        self.run_copy(change, {"verify.py": "source digest", "independent.py": "source SHA256"})

    def test_lower_frame_gate_rejected_on_actual_word(self):
        word = copy.deepcopy(self.word)
        word["B"][283][0] = 182
        # trace directly because changing its frame removes it from the B509 slice.
        with self.assertRaisesRegex(ValueError, "illegal frame move"):
            PRIMARY["trace"](word, PRIMARY["Geometry"](word))

    def test_endpoint_preserving_stale_cleanup_rejected(self):
        word = copy.deepcopy(self.word)
        # A cancelling pair preserves every binary endpoint and frame path but
        # violates the retained literal-cleanup boundary.
        word["C"].extend([copy.deepcopy(word["C"][-1]), copy.deepcopy(word["C"][-1])])
        with self.assertRaisesRegex(ValueError, "stale literal cleanup"):
            PRIMARY["analyze"](word)


if __name__ == "__main__":
    unittest.main(verbosity=2)
