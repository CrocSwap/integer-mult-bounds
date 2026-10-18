#!/usr/bin/env python3
"""Focused controls for the shared-point frame-contains tooling package."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "shared-point-frame-contains"
sys.path.insert(0, str(ROOT / "scripts"))

import shared_point_circuit as production  # noqa: E402


def load_baseline():
    spec = importlib.util.spec_from_file_location(
        "baseline_spc_frame_contains_test", PACKAGE / "baseline.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SharedPointFrameContainsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline()

    def test_baseline_matches_base_commit_bytes(self):
        import subprocess

        original = subprocess.check_output(
            [
                "git",
                "show",
                "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2:scripts/shared_point_circuit.py",
            ],
            cwd=ROOT,
        )
        self.assertEqual((PACKAGE / "baseline.py").read_bytes(), original)

    def test_small_circuit_verify_and_frames_match(self):
        for h in (6, 8, 10):
            circuit = production.SharedPointCircuit(h)
            self.assertEqual(
                self.baseline.SharedPointCircuit.verify(circuit),
                circuit.verify(),
            )
            code = circuit.compile()
            self.assertEqual(
                self.baseline.SharedPointCircuit.verify_frames(circuit, code),
                circuit.verify_frames(code),
            )

    def test_support_in_bitmasks_match(self):
        circuit = production.SharedPointCircuit(12)
        for node in list(circuit.active)[:80]:
            bits = circuit.core[node]
            while bits:
                bit = bits & -bits
                bits -= bit
                common = bit.bit_length() - 1
                self.assertEqual(
                    self.baseline.SharedPointCircuit.support_in(circuit, node, common),
                    circuit.support_in(node, common),
                )

    def test_nesting_rejection_preserved(self):
        circuit = production.SharedPointCircuit(8)
        code = circuit.compile()
        node = next(n for n in circuit.active if circuit.args[n])
        a, _b = circuit.args[node]
        circuit.core[node] = circuit.core[a]
        circuit.__dict__.pop("_support_in_cache", None)
        with self.assertRaises(AssertionError):
            circuit.verify_frames(code)
        with self.assertRaises(AssertionError):
            self.baseline.SharedPointCircuit.verify_frames(circuit, code)

    def test_production_digest_pin(self):
        from hashlib import sha256

        self.assertEqual(
            sha256((ROOT / "scripts" / "shared_point_circuit.py").read_bytes()).hexdigest(),
            "360d9bffc0f55315fe294789b72c71c79e0991524555b3a5f42a2ca504d7da95",
        )


if __name__ == "__main__":
    unittest.main()
