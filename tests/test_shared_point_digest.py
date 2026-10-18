#!/usr/bin/env python3
"""Focused controls for the shared-point verify digest tooling package."""
from __future__ import annotations

from hashlib import sha256
import importlib.util
import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "shared-point-digest"
sys.path.insert(0, str(ROOT / "scripts"))

import shared_point_circuit as production  # noqa: E402


def load_baseline():
    spec = importlib.util.spec_from_file_location("baseline_spc_test", PACKAGE / "baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SharedPointDigestTests(unittest.TestCase):
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

    def test_encoding_matches_json_dumps(self):
        samples = [
            (1, None, None),
            (5, (1, 2), (0, 3)),
            (9, None, None),
            (100, (8, 7), (2, 4)),
        ]
        for node, edge, prov in samples:
            old = json.dumps((node, edge, prov), separators=(",", ":")) + "\n"
            if edge is None:
                new = f"[{node},null,null]\n"
            else:
                a, b = edge
                common, local = prov
                new = f"[{node},[{a},{b}],[{common},{local}]]\n"
            self.assertEqual(old, new)
        out_old = json.dumps((0, (0, 1, 2), 22), separators=(",", ":")) + "\n"
        self.assertEqual(out_old, "[0,[0,1,2],22]\n")

    def test_none_mutant_differs(self):
        self.assertNotEqual(
            "[0,None,None]\n",
            json.dumps((0, None, None), separators=(",", ":")) + "\n",
        )

    def test_small_circuit_receipts_match(self):
        for h in (6, 8, 10):
            circuit = production.SharedPointCircuit(h)
            self.assertEqual(
                self.baseline.SharedPointCircuit.verify(circuit),
                circuit.verify(),
            )

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
        # Accepted #2054 frame-containment successor retains the digest code;
        # its exact earlier production source remains independently pinned.
        self.assertEqual(
            sha256((ROOT / 'research/shared-point-frame-contains/baseline.py').read_bytes()).hexdigest(),
            'f5abbf6d61f3c10349416a3e1a1ed038bbd1279ed223367f2df549de46dd7ea5')
        self.assertEqual(
            sha256((ROOT / "scripts/shared_point_circuit.py").read_bytes()).hexdigest(),
            "360d9bffc0f55315fe294789b72c71c79e0991524555b3a5f42a2ca504d7da95",
        )


if __name__ == "__main__":
    unittest.main()
