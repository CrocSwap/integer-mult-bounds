#!/usr/bin/env python3
"""Focused controls for the shared-point merge-construction tooling package."""
from __future__ import annotations

from hashlib import sha256
import importlib.util
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "shared-point-init"
sys.path.insert(0, str(ROOT / "scripts"))

import shared_point_circuit as production  # noqa: E402


def load_baseline():
    spec = importlib.util.spec_from_file_location("baseline_spc_init_test", PACKAGE / "baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SharedPointInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline()

    def test_baseline_matches_base_commit_bytes(self):
        import subprocess

        original = subprocess.check_output(
            ["git", "show", "0b1cccf86e2f5132ed286a26ef0a681a495740ea:scripts/shared_point_circuit.py"],
            cwd=ROOT,
        )
        self.assertEqual((PACKAGE / "baseline.py").read_bytes(), original)

    def test_small_circuit_structure_and_receipts_match(self):
        for h in (6, 8, 10):
            old = self.baseline.SharedPointCircuit(h)
            new = production.SharedPointCircuit(h)
            self.assertEqual(old.args, new.args)
            self.assertEqual(old.core, new.core)
            self.assertEqual(old.union, new.union)
            self.assertEqual(old.provenance, new.provenance)
            self.assertEqual(old.outputs, new.outputs)
            self.assertEqual(old.active, new.active)
            self.assertEqual(old.merged, new.merged)
            self.assertEqual(old.additions, new.additions)
            self.assertEqual(old.verify(), new.verify())

    def test_support_rejection_preserved(self):
        circuit = production.SharedPointCircuit(8)
        node = next(n for n in circuit.active if circuit.args[n])
        a, _b = circuit.args[node]
        circuit.core[node] = circuit.core[a]
        with self.assertRaises(AssertionError):
            circuit.verify()
        with self.assertRaises(AssertionError):
            self.baseline.SharedPointCircuit.verify(circuit)

    def test_production_digest_pin(self):
        self.assertEqual(
            sha256((ROOT / "scripts/shared_point_circuit.py").read_bytes()).hexdigest(),
            "360d9bffc0f55315fe294789b72c71c79e0991524555b3a5f42a2ca504d7da95",
        )


if __name__ == "__main__":
    unittest.main()
