#!/usr/bin/env python3
"""Focused controls for the partial-swap merge-construction tooling package."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "partial-swap-init"
sys.path.insert(0, str(ROOT / "scripts"))

from partial_swap import shared as production  # noqa: E402

BASE_COMMIT = "3b29a00f972bd15871baac0acf5ac204740a9863"
ORIGINAL_SHA256 = "b27c8bfe1de3f7d2d5fb19ac742adf11597c2aaa7add68430443119997e646e8"
OPTIMIZED_SHA256 = "7290bd639600aecff11941d3faf95c9ce95589125cc6a7f7440fb86af7a0f17c"


def load_baseline():
    spec = importlib.util.spec_from_file_location("baseline_pspc_init_test", PACKAGE / "baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PartialSwapInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline()

    def test_baseline_matches_base_commit_bytes(self):
        original = subprocess.check_output(
            ["git", "show", f"{BASE_COMMIT}:scripts/partial_swap/shared.py"],
            cwd=ROOT,
        )
        self.assertEqual((PACKAGE / "baseline.py").read_bytes(), original)
        self.assertEqual(sha256(original).hexdigest(), ORIGINAL_SHA256)

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
            sha256((ROOT / "scripts/partial_swap/shared.py").read_bytes()).hexdigest(),
            OPTIMIZED_SHA256,
        )

    def test_certificate_pin_only(self):
        base = json.loads(
            subprocess.check_output(
                ["git", "show", f"{BASE_COMMIT}:certificates/partial-swap-network.json"],
                cwd=ROOT,
            )
        )
        live = json.loads((ROOT / "certificates/partial-swap-network.json").read_text(encoding="utf-8"))
        self.assertEqual(base["source_sha256"]["scripts/partial_swap/shared.py"], ORIGINAL_SHA256)
        self.assertEqual(live["source_sha256"]["scripts/partial_swap/shared.py"], OPTIMIZED_SHA256)
        restored = deepcopy(live)
        restored["source_sha256"]["scripts/partial_swap/shared.py"] = ORIGINAL_SHA256
        self.assertEqual(restored, base)


if __name__ == "__main__":
    unittest.main()
