#!/usr/bin/env python3
"""Focused controls for the production data-corner cached-column package."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import subprocess
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "data-corner-production"

ORIGINAL_SHA256 = "d134f43d31b896daf504511991be8608c6ba9d20a6606c57e2e12d4b203b7d44"
PRODUCTION_SHA256 = "406a850d496589cd1216eb709baa84fdd8633048b648f05022ae184d1f279448"
BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"


class DataCornerProductionTests(unittest.TestCase):
    def test_baseline_matches_base_commit_bytes(self):
        original = subprocess.check_output(
            ["git", "show", f"{BASE_COMMIT}:research/copied-fixed/data_corners.cpp"],
            cwd=ROOT,
        )
        self.assertEqual((PACKAGE / "baseline.cpp").read_bytes(), original)
        self.assertEqual(sha256(original).hexdigest(), ORIGINAL_SHA256)
        self.assertEqual(
            sha256((ROOT / "research/copied-fixed/data_corners.cpp").read_bytes()).hexdigest(),
            PRODUCTION_SHA256,
        )
        self.assertNotEqual(PRODUCTION_SHA256, ORIGINAL_SHA256)

    def test_certificate_only_changes_data_corners_local_pin(self):
        base = json.loads(
            subprocess.check_output(
                ["git", "show", f"{BASE_COMMIT}:research/copied-fixed/certificate.json"],
                cwd=ROOT,
            )
        )
        live = json.loads(
            (ROOT / "research/copied-fixed/certificate.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            live["local_sha256"]["research/copied-fixed/data_corners.cpp"],
            PRODUCTION_SHA256,
        )
        restored = deepcopy(live)
        restored["local_sha256"]["research/copied-fixed/data_corners.cpp"] = ORIGINAL_SHA256
        self.assertEqual(restored, base)

    def test_performance_package_vendors_baseline_and_tracks_production(self):
        manifest = json.loads(
            (ROOT / "research/data-corner-performance/SOURCE.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            manifest["sha256"]["research/data-corner-performance/baseline.cpp"],
            ORIGINAL_SHA256,
        )
        self.assertEqual(
            manifest["sha256"]["research/copied-fixed/data_corners.cpp"],
            PRODUCTION_SHA256,
        )
        self.assertEqual(
            manifest["provenance_sha256"]["research/copied-fixed/data_corners.cpp@pre-production"],
            ORIGINAL_SHA256,
        )
        self.assertEqual(
            sha256(
                (ROOT / "research/data-corner-performance/baseline.cpp").read_bytes()
            ).hexdigest(),
            ORIGINAL_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
