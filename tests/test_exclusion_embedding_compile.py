#!/usr/bin/env python3
"""Focused controls for the exclusion embedding compile tooling package."""
from __future__ import annotations

from hashlib import sha256
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "exclusion-embedding-compile"
sys.path.insert(0, str(ROOT / "scripts"))

import exclusion_circuit as production  # noqa: E402

ORIGINAL_SHA256 = "f9fbcd6e85e442cbd0926ac0887414e20735b2dc923d2d5822c803ceb46726d3"
OPTIMIZED_SHA256 = "f066ce9f88f0d8c0b82d7cb3a8d267249e12386e9d1ab65820a3bed54ff0ff78"
BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
N45_VERIFY_SHA = "3b1a4d7731db2950040552672fbc56ebd172e36e3412129030ff2aec472d5f6c"


def load_baseline():
    spec = importlib.util.spec_from_file_location("baseline_emb_compile_test", PACKAGE / "baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExclusionEmbeddingCompileTests(unittest.TestCase):
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

    def test_compile_maps_identical(self):
        for n in (4, 8, 16, 32, 45):
            circuit = production.ExclusionCircuit(n)
            old = self.baseline.ExclusionCircuit.compile(circuit)
            new = circuit.compile()
            self.assertEqual(old, new)

    def test_verify_embedding_identical(self):
        for n in (4, 8, 16, 45):
            circuit = production.ExclusionCircuit(n)
            old = self.baseline.ExclusionCircuit.verify_embedding(circuit)
            new = circuit.verify_embedding()
            self.assertEqual(old, new)

    def test_verify_circuit_sha256_unchanged(self):
        circuit = production.ExclusionCircuit(45)
        old = self.baseline.ExclusionCircuit.verify(circuit)
        new = circuit.verify()
        self.assertEqual(old, new)
        self.assertEqual(new["circuit_sha256"], N45_VERIFY_SHA)

    def test_certificate_pins(self):
        for rel in (
            "certificates/positive-side-core.json",
            "certificates/dyadic-central-factor.json",
            "certificates/ternary-side.json",
            "certificates/disjoint-tensor-compression.json",
        ):
            live = json.loads((ROOT / rel).read_text(encoding="utf-8"))
            self.assertEqual(
                live["source_sha256"]["scripts/exclusion_circuit.py"], OPTIMIZED_SHA256
            )


if __name__ == "__main__":
    unittest.main()
