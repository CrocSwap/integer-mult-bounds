#!/usr/bin/env python3
"""Focused controls for the exclusion embedding reverse-mask tooling package."""
from __future__ import annotations

from hashlib import sha256
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "exclusion-embedding-masks"
sys.path.insert(0, str(ROOT / "scripts"))

import exclusion_circuit as production  # noqa: E402

ORIGINAL_SHA256 = "b253f9d7318becda1c1f3b24e2287ed44a9c27fcea00cf9d531afb950d0457a0"
OPTIMIZED_SHA256 = "f9fbcd6e85e442cbd0926ac0887414e20735b2dc923d2d5822c803ceb46726d3"
BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
N45_VERIFY_SHA = "3b1a4d7731db2950040552672fbc56ebd172e36e3412129030ff2aec472d5f6c"


def load_baseline():
    spec = importlib.util.spec_from_file_location("baseline_emb_test", PACKAGE / "baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExclusionEmbeddingMasksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline()

    def test_baseline_matches_base_commit_bytes(self):
        original = subprocess.check_output(
            ["git", "show", f"{BASE_COMMIT}:scripts/exclusion_circuit.py"],
            cwd=ROOT,
        )
        self.assertEqual((PACKAGE / "baseline.py").read_bytes(), original)
        self.assertEqual(sha256(original).hexdigest(), ORIGINAL_SHA256)
        self.assertEqual(
            sha256((ROOT / "scripts/exclusion_circuit.py").read_bytes()).hexdigest(),
            OPTIMIZED_SHA256,
        )

    def test_closed_form_matches_historical_genexpr(self):
        for n in (4, 8, 16, 32):
            circuit = production.ExclusionCircuit(n)
            code = circuit.compile()
            target_index = {pair: i for i, pair in enumerate(sorted(circuit.outputs))}
            full = (1 << len(target_index)) - 1
            vertex = [0] * circuit.n
            for target, i in target_index.items():
                bit = 1 << i
                vertex[target[0]] |= bit
                vertex[target[1]] |= bit
            for source, _slot in code["sources"].items():
                old = sum(
                    1 << i
                    for target, i in target_index.items()
                    if not set(source) & set(target)
                )
                new = full ^ (vertex[source[0]] | vertex[source[1]])
                self.assertEqual(old, new)

    def test_xor_mutant_differs(self):
        circuit = production.ExclusionCircuit(8)
        target_index = {pair: i for i, pair in enumerate(sorted(circuit.outputs))}
        full = (1 << len(target_index)) - 1
        vertex = [0] * circuit.n
        for target, i in target_index.items():
            bit = 1 << i
            vertex[target[0]] |= bit
            vertex[target[1]] |= bit
        a, b = next(iter(circuit.compile()["sources"]))
        self.assertNotEqual(full ^ vertex[a] ^ vertex[b], full ^ (vertex[a] | vertex[b]))

    def test_small_circuit_receipts_match(self):
        for n in (4, 6, 8, 12):
            circuit = production.ExclusionCircuit(n)
            self.assertEqual(
                self.baseline.ExclusionCircuit.verify_embedding(circuit),
                circuit.verify_embedding(),
            )

    def test_full_size_receipt(self):
        circuit = production.ExclusionCircuit(45)
        old = self.baseline.ExclusionCircuit.verify_embedding(circuit)
        new = circuit.verify_embedding()
        self.assertEqual(old, new)
        self.assertEqual(new["reversible_roles"], 12556)
        self.assertTrue(new["forward_coefficient_map_exact"])
        self.assertTrue(new["reverse_support_frames_nested"])

    def test_verify_leave_two_out_companion(self):
        text = (ROOT / "scripts" / "exclusion_circuit.py").read_text(encoding="utf-8")
        self.assertIn(
            "assert self.support[node]==full^(vertex[a]|vertex[b])",
            text,
        )
        self.assertIn(
            "assert reverse_frames[slot]==full^(vertex[a]|vertex[b])",
            text,
        )
        self.assertNotIn(
            "sum(1<<i for i,p in enumerate(self.inputs) if a not in p and b not in p)",
            text,
        )


    def test_certificates_only_change_exclusion_pin(self):
        from copy import deepcopy

        for rel in (
            "certificates/positive-side-core.json",
            "certificates/dyadic-central-factor.json",
            "certificates/ternary-side.json",
            "certificates/disjoint-tensor-compression.json",
        ):
            base = json.loads(
                subprocess.check_output(["git", "show", f"{BASE_COMMIT}:{rel}"], cwd=ROOT)
            )
            live = json.loads((ROOT / rel).read_text(encoding="utf-8"))
            self.assertEqual(
                live["source_sha256"]["scripts/exclusion_circuit.py"], OPTIMIZED_SHA256
            )
            restored = deepcopy(live)
            restored["source_sha256"]["scripts/exclusion_circuit.py"] = ORIGINAL_SHA256
            if "scripts/experiments/disjoint_tensor.py" in live["source_sha256"]:
                restored["source_sha256"]["scripts/experiments/disjoint_tensor.py"] = (
                    "102dd59bf96033f96ba0dab4c2aba77b3a7a73b67b0f96929ff8b20a98b91cd8"
                )
            if "scripts/experiments/complex_centers.py" in live["source_sha256"]:
                restored["source_sha256"]["scripts/experiments/complex_centers.py"] = (
                    "3744396587d729253d80980f6310b56e7bf0ea21b165bd178d0d6d4c49faf2e2"
                )
            companion = "scripts/experiments/ternary_side.py"
            if companion in restored["source_sha256"]:
                self.assertEqual(restored["source_sha256"][companion], "eba4acc6f44c5d56aa8d225266a4a951fc1f1cb84819cdc104e1847578403878")
                restored["source_sha256"][companion] = base["source_sha256"][companion]
            self.assertEqual(restored, base)


if __name__ == "__main__":
    unittest.main()
