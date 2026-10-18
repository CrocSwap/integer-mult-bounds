#!/usr/bin/env python3
"""Focused controls for the mixed-point scalar digest tooling package."""
from __future__ import annotations

from hashlib import sha256
import importlib.util
import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "mixed-point-scalar-digest"
sys.path.insert(0, str(ROOT / "scripts"))

from experiments.mixed_point_circuit import build  # noqa: E402
import audit_mixed_point as production  # noqa: E402


def load_baseline():
    spec = importlib.util.spec_from_file_location("baseline_amp_test", PACKAGE / "baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MixedPointScalarDigestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline()

    def test_baseline_matches_base_commit_bytes(self):
        import subprocess

        original = subprocess.check_output(
            ["git", "show", "0b1cccf86e2f5132ed286a26ef0a681a495740ea:scripts/audit_mixed_point.py"],
            cwd=ROOT,
        )
        self.assertEqual((PACKAGE / "baseline.py").read_bytes(), original)

    def test_encoding_matches_json_dumps(self):
        samples = [(0, None), (3, (1, 2)), (100, None), (9, (8, 7))]
        for node, edge in samples:
            old = json.dumps((node, edge), separators=(",", ":")) + "\n"
            if edge is None:
                new = f"[{node},null]\n"
            else:
                new = f"[{node},[{edge[0]},{edge[1]}]]\n"
            self.assertEqual(old, new)

    def test_none_mutant_differs(self):
        self.assertNotEqual("[0,None]\n", json.dumps((0, None), separators=(",", ":")) + "\n")

    def test_small_circuit_receipts_match(self):
        build.cache_clear()
        c = build(12, 3, 3, 1, common=True)
        self.assertEqual(self.baseline.scalar_check(c), production.scalar_check(c))

    def test_support_rejection_preserved(self):
        build.cache_clear()
        c = build(10, 3, 3, 1, common=True)
        # Corrupt one addition support; both engines must reject.
        node = next(n for n in c.active if c.args[n])
        a, b = c.args[node]
        c.support[node] = c.support[a]  # drop the right child bits
        with self.assertRaises(ValueError):
            production.scalar_check(c)
        with self.assertRaises(ValueError):
            self.baseline.scalar_check(c)

    def test_production_digest_pin(self):
        self.assertEqual(
            sha256((ROOT / "scripts/audit_mixed_point.py").read_bytes()).hexdigest(),
            "fc7ca3e07d8a3ad54e894c387a89b310ae0b7048763cd48bb27f5daeb0d73dba",
        )


if __name__ == "__main__":
    unittest.main()
