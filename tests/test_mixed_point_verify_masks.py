#!/usr/bin/env python3
"""Focused controls for the mixed-point Circuit.verify mask tooling package."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
import subprocess
import unittest
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "mixed-point-verify-masks"
sys.path.insert(0, str(ROOT / "scripts"))

from experiments import mixed_point_circuit as production  # noqa: E402

ORIGINAL_SHA256 = "f509362b5031976a22af351fd158ae0b4520fa4f286a5176ec37023d672a7ddc"
OPTIMIZED_SHA256 = "cc98eeada267814fa2c0bc5f3ebb844f614d667c74d16d80d7ef29b1f90e0aa5"
BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"


def load_baseline():
    spec = importlib.util.spec_from_file_location("baseline_mpc_test", PACKAGE / "baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clear_caches():
    production.build.cache_clear()
    production.plan.cache_clear()
    production.kernel.cache_clear()
    production.vector.cache_clear()


class MixedPointVerifyMasksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline()

    def test_baseline_matches_base_commit_bytes(self):
        original = subprocess.check_output(
            ["git", "show", f"{BASE_COMMIT}:scripts/experiments/mixed_point_circuit.py"],
            cwd=ROOT,
        )
        self.assertEqual((PACKAGE / "baseline.py").read_bytes(), original)
        self.assertEqual(sha256(original).hexdigest(), ORIGINAL_SHA256)
        self.assertEqual(
            sha256((ROOT / "scripts/experiments/mixed_point_circuit.py").read_bytes()).hexdigest(),
            OPTIMIZED_SHA256,
        )

    def test_closed_form_matches_historical_genexpr(self):
        for args in ((12, 3, 3, 0), (12, 3, 3, 1), (16, 3, 3, 1), (14, 2, 2, 0)):
            clear_caches()
            circuit = production.build(*args)
            full = (1 << len(circuit.inputs)) - 1
            vertex = [0] * circuit.n
            for i, source in enumerate(circuit.inputs):
                for point in source:
                    vertex[point] |= 1 << i
            r = circuit.r
            for target, node in zip(circuit.targets, circuit.outputs):
                old = sum(
                    1 << i
                    for i, source in enumerate(circuit.inputs)
                    if len(set(source) & set(target)) == r
                )
                expected = 0
                for U in combinations(target, r):
                    keep = set(U)
                    mask = full
                    for point in target:
                        if point in keep:
                            mask &= vertex[point]
                        else:
                            mask &= full ^ vertex[point]
                    expected |= mask
                self.assertEqual(old, expected)
                self.assertEqual(circuit.support[node], expected)

    def test_or_mutant_differs_for_r1(self):
        clear_caches()
        circuit = production.build(12, 3, 3, 1)
        full = (1 << len(circuit.inputs)) - 1
        vertex = [0] * circuit.n
        for i, source in enumerate(circuit.inputs):
            for point in source:
                vertex[point] |= 1 << i
        target = circuit.targets[0]
        or_hit = 0
        for point in target:
            or_hit |= vertex[point]
        expected = 0
        for U in combinations(target, 1):
            keep = set(U)
            mask = full
            for point in target:
                if point in keep:
                    mask &= vertex[point]
                else:
                    mask &= full ^ vertex[point]
            expected |= mask
        self.assertNotEqual(or_hit, expected)

    def test_verify_returns_true_and_matches_baseline(self):
        for args in ((12, 3, 3, 0), (16, 3, 3, 1), (20, 3, 3, 1)):
            clear_caches()
            circuit = production.build(*args)
            self.assertTrue(self.baseline.Circuit.verify(circuit))
            self.assertTrue(circuit.verify())

    def test_support_rejection_preserved(self):
        clear_caches()
        circuit = production.build(12, 3, 3, 1)
        circuit.support[circuit.outputs[0]] ^= 1
        with self.assertRaises(ValueError):
            circuit.verify()

    def test_certificates_only_change_mixed_point_circuit_pin(self):
        for rel in (
            "certificates/mixed-point-audit.json",
            "certificates/parity-side.json",
        ):
            base = json.loads(
                subprocess.check_output(["git", "show", f"{BASE_COMMIT}:{rel}"], cwd=ROOT)
            )
            live = json.loads((ROOT / rel).read_text(encoding="utf-8"))
            key = "scripts/experiments/mixed_point_circuit.py"
            self.assertEqual(live["source_sha256"][key], OPTIMIZED_SHA256)
            restored = deepcopy(live)
            restored["source_sha256"][key] = ORIGINAL_SHA256
            # Retain the independently reviewed DisjointTensor production update.
            companion = "scripts/experiments/disjoint_tensor.py"
            if companion in restored["source_sha256"]:
                self.assertEqual(restored["source_sha256"][companion], "23763a4b6086fb3d19f9282fff5c118f53fa52e7a7f17da1bde990bd4cf8b6ac")
                restored["source_sha256"][companion] = base["source_sha256"][companion]
            self.assertEqual(restored, base)


if __name__ == "__main__":
    unittest.main()
