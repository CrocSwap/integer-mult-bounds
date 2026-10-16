"""Focused controls for the joint-frames cleared-product tooling package."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/joint-frames-cleared-product"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_joint_frames as jf  # noqa: E402


def load_baseline():
    spec = importlib.util.spec_from_file_location(
        "joint_frames_product_baseline", PACKAGE / "baseline.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class JointFramesClearedProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline()

    def test_baseline_bytes_match_base_commit(self):
        original = subprocess.check_output(
            ["git", "show", "0b1cccf86e2f5132ed286a26ef0a681a495740ea:scripts/audit_joint_frames.py"],
            cwd=ROOT,
        )
        self.assertEqual((PACKAGE / "baseline.py").read_bytes(), original)
        self.assertEqual(
            sha256(original).hexdigest(),
            "3df8061392ce0ba42bbde8c02f2a30c8141145e70e9a48c18da73d3aafb14423",
        )

    def test_product_agrees_on_rational_matrices(self):
        A = ((Q(1, 2), Q(1, 3)), (Q(-1), Q(2, 5)))
        B = ((Q(3), Q(0), Q(1, 7)), (Q(1, 4), Q(-2), Q(1)))
        self.assertEqual(self.baseline.product(A, B), jf.product(A, B))
        I = jf.eye(2)
        self.assertEqual(jf.product(I, A), A)
        self.assertEqual(self.baseline.product(I, A), jf.product(I, A))

    def test_empty_left_factor(self):
        self.assertEqual(jf.product(tuple(), ((Q(1),),)), tuple())
        self.assertEqual(self.baseline.product(tuple(), ((Q(1),),)), tuple())

    def test_certificate_pin_only_joint_frames(self):
        rel = "certificates/rank-product-core.json"
        base = json.loads(
            subprocess.check_output(
                ["git", "show", f"0b1cccf86e2f5132ed286a26ef0a681a495740ea:{rel}"],
                cwd=ROOT,
            )
        )
        live = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        self.assertEqual(
            base["source_sha256"]["scripts/audit_joint_frames.py"],
            "3df8061392ce0ba42bbde8c02f2a30c8141145e70e9a48c18da73d3aafb14423",
        )
        self.assertEqual(
            live["source_sha256"]["scripts/audit_joint_frames.py"],
            "818e86b4152b4eeb853f173c9aa795510caa593ec0e25b05a246f1df52575466",
        )
        restored = json.loads(json.dumps(live))
        restored["source_sha256"]["scripts/audit_joint_frames.py"] = base["source_sha256"][
            "scripts/audit_joint_frames.py"
        ]
        self.assertEqual(restored, base)


if __name__ == "__main__":
    unittest.main()
