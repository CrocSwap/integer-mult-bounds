#!/usr/bin/env python3
"""Focused controls for the production packed central-factor tooling package."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import subprocess
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "central-factor-production"
sys.path.insert(0, str(ROOT / "scripts"))

from experiments import complex_centers as production  # noqa: E402

ORIGINAL_SHA256 = "3744396587d729253d80980f6310b56e7bf0ea21b165bd178d0d6d4c49faf2e2"
BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"


class CentralFactorProductionTests(unittest.TestCase):
    def test_baseline_matches_base_commit_bytes(self):
        original = subprocess.check_output(
            ["git", "show", f"{BASE_COMMIT}:scripts/experiments/complex_centers.py"],
            cwd=ROOT,
        )
        self.assertEqual((PACKAGE / "baseline.py").read_bytes(), original)
        self.assertEqual(sha256(original).hexdigest(), ORIGINAL_SHA256)
        self.assertNotEqual(
            sha256((ROOT / "scripts/experiments/complex_centers.py").read_bytes()).hexdigest(),
            ORIGINAL_SHA256,
        )

    def test_packed_matches_baseline_on_small_heights(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "central_factor_baseline", PACKAGE / "baseline.py"
        )
        baseline = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(baseline)
        for h in (8, 10, 12):
            factor = production.factor(h)
            self.assertEqual(baseline.verify_factor(factor), production.verify_factor(factor))

    def test_certificate_only_changes_complex_centers_pin(self):
        base = json.loads(
            subprocess.check_output(
                ["git", "show", f"{BASE_COMMIT}:certificates/dyadic-central-factor.json"],
                cwd=ROOT,
            )
        )
        live = json.loads(
            (ROOT / "certificates/dyadic-central-factor.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            live["source_sha256"]["scripts/experiments/complex_centers.py"],
            sha256((ROOT / "scripts/experiments/complex_centers.py").read_bytes()).hexdigest(),
        )
        restored = deepcopy(live)
        restored["source_sha256"]["scripts/experiments/complex_centers.py"] = ORIGINAL_SHA256
        companion = "scripts/experiments/disjoint_tensor.py"
        self.assertEqual(restored["source_sha256"][companion], "23763a4b6086fb3d19f9282fff5c118f53fa52e7a7f17da1bde990bd4cf8b6ac")
        restored["source_sha256"][companion] = base["source_sha256"][companion]
        self.assertEqual(restored, base)

    def test_package_verify_script(self):
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(PACKAGE / "verify.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("PASS_CENTRAL_FACTOR_PRODUCTION", proc.stdout)


if __name__ == "__main__":
    unittest.main()
