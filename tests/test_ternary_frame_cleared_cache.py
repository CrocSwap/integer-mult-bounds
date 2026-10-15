#!/usr/bin/env python3
"""Focused controls for the ternary-frame cleared-cache tooling package."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from fractions import Fraction as Q
from hashlib import sha256
from math import lcm
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "ternary-frame-cleared-cache"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from audit_joint_frames import matrix  # noqa: E402
import experiments.ternary_side as production  # noqa: E402

BASE = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_SHA256 = "93379b6e70cf58bb55432d9f2d1c0e0305c20a075bfe3cc219deabd927afd375"
OPTIMIZED_SHA256 = "eba4acc6f44c5d56aa8d225266a4a951fc1f1cb84819cdc104e1847578403878"


def load_baseline():
    spec = importlib.util.spec_from_file_location(
        "ternary_frame_cleared_baseline", PACKAGE / "baseline.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TernaryFrameClearedCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline()

    def test_baseline_bytes_match_base_commit(self):
        original = subprocess.check_output(
            ["git", "show", f"{BASE}:scripts/experiments/ternary_side.py"],
            cwd=ROOT,
        )
        self.assertEqual((PACKAGE / "baseline.py").read_bytes(), original)
        self.assertEqual(sha256(original).hexdigest(), ORIGINAL_SHA256)
        self.assertEqual(
            sha256((SCRIPTS / "experiments" / "ternary_side.py").read_bytes()).hexdigest(),
            OPTIMIZED_SHA256,
        )

    def test_frames_match_baseline_on_h8(self):
        graph = production.build(8, retain_graph=True)
        self.assertEqual(
            self.baseline.verify_invocation_frames(graph),
            production.verify_invocation_frames(graph),
        )

    def test_cleared_product_matches_fraction_sum(self):
        A = matrix([[Q(1, 2), Q(1, 3)], [Q(-1), Q(2, 5)]])
        B = matrix([[Q(3), Q(0)], [Q(1, 4), Q(-2)]])
        slow = tuple(
            tuple(sum(A[i][t] * B[t][j] for t in range(2)) for j in range(2))
            for i in range(2)
        )
        DA = DB = 1
        for row in A:
            for x in row:
                if x.denominator != 1:
                    DA = lcm(DA, x.denominator)
        for row in B:
            for x in row:
                if x.denominator != 1:
                    DB = lcm(DB, x.denominator)
        Ai = [[x.numerator * (DA // x.denominator) for x in row] for row in A]
        Bi = [[x.numerator * (DB // x.denominator) for x in row] for row in B]
        scale = DA * DB
        fast = tuple(
            tuple(Q(sum(Ai[i][t] * Bi[t][j] for t in range(2)), scale) for j in range(2))
            for i in range(2)
        )
        self.assertEqual(slow, fast)

    def test_certificate_pin_only_ternary_side(self):
        rel = "certificates/ternary-side.json"
        base = json.loads(
            subprocess.check_output(["git", "show", f"{BASE}:{rel}"], cwd=ROOT)
        )
        live = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        self.assertEqual(base["source_sha256"]["scripts/experiments/ternary_side.py"], ORIGINAL_SHA256)
        self.assertEqual(live["source_sha256"]["scripts/experiments/ternary_side.py"], OPTIMIZED_SHA256)
        restored = json.loads(json.dumps(live))
        restored["source_sha256"]["scripts/experiments/ternary_side.py"] = base[
            "source_sha256"
        ]["scripts/experiments/ternary_side.py"]
        companion = "scripts/experiments/disjoint_tensor.py"
        expected = "23763a4b6086fb3d19f9282fff5c118f53fa52e7a7f17da1bde990bd4cf8b6ac"
        if restored["source_sha256"].get(companion) != base["source_sha256"].get(companion):
            self.assertEqual(restored["source_sha256"].get(companion), expected)
            self.assertEqual(sha256((ROOT / companion).read_bytes()).hexdigest(), expected)
            restored["source_sha256"][companion] = base["source_sha256"][companion]
        self.assertEqual(restored, base)


if __name__ == "__main__":
    unittest.main()
