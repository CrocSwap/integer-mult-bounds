#!/usr/bin/env python3
"""Focused controls for the production Leech byte-lane tooling package."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import subprocess
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "leech-minor-production"
sys.path.insert(0, str(ROOT / "scripts"))

from experiments import affine_vector_screens as production  # noqa: E402

ORIGINAL_SHA256 = "756778eeca27f490adc7354a122dc50c40375156259991469c47a90949118ea1"
BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"


class LeechMinorProductionTests(unittest.TestCase):
    def test_baseline_matches_base_commit_bytes(self):
        original = subprocess.check_output(
            ["git", "show", f"{BASE_COMMIT}:scripts/experiments/affine_vector_screens.py"],
            cwd=ROOT,
        )
        self.assertEqual((PACKAGE / "baseline.py").read_bytes(), original)
        self.assertEqual(sha256(original).hexdigest(), ORIGINAL_SHA256)
        self.assertNotEqual(
            sha256((ROOT / "scripts/experiments/affine_vector_screens.py").read_bytes()).hexdigest(),
            ORIGINAL_SHA256,
        )

    def test_lanes_match_baseline_on_frozen_fixtures(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "affine_vector_screens_baseline", PACKAGE / "baseline.py"
        )
        baseline = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(baseline)
        data = json.loads(
            (ROOT / "scripts/experiments/affine_vector_witnesses.json").read_text(
                encoding="utf-8"
            )
        )
        for fixture in data["leech"]:
            self.assertEqual(
                baseline.leech_minor(**fixture),
                production.leech_minor(**fixture),
            )

    def test_certificate_only_changes_affine_vector_screens_pin(self):
        base = json.loads(
            subprocess.check_output(
                ["git", "show", f"{BASE_COMMIT}:certificates/affine-vector-screens.json"],
                cwd=ROOT,
            )
        )
        live = json.loads(
            (ROOT / "certificates/affine-vector-screens.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            live["source_sha256"]["scripts/experiments/affine_vector_screens.py"],
            sha256((ROOT / "scripts/experiments/affine_vector_screens.py").read_bytes()).hexdigest(),
        )
        restored = deepcopy(live)
        restored["source_sha256"]["scripts/experiments/affine_vector_screens.py"] = ORIGINAL_SHA256
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
        self.assertIn("PASS_LEECH_MINOR_PRODUCTION", proc.stdout)


if __name__ == "__main__":
    unittest.main()
