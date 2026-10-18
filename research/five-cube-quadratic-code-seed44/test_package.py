#!/usr/bin/env python3
"""Bounded mathematical and packaging controls. Apache-2.0; AI-assisted."""

import copy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


primary = load("verify")
oracle = load("independent")


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = json.loads((HERE / "CERTIFICATE.json").read_text())

    def test_complete_regeneration_and_independent_replay(self):
        generated = primary.compute_certificate()
        self.assertEqual(primary.canonical_bytes(generated), (HERE / "CERTIFICATE.json").read_bytes())
        oracle.check_source_files(self.certificate)
        result = oracle.verify_data(self.certificate)
        self.assertEqual(result["ordered_term_ranks"], 3136)

    def test_exact_rank_controls(self):
        cases = [([], 0), ([[]], 0), ([[0, 0], [0, 0]], 0), ([[2]], 1),
                 ([[1, 1], [1, -1]], 2), ([[1, 2], [2, 4]], 1),
                 ([[0, 2, 0], [0, 0, 3]], 2), ([[0, 0], [1, 2]], 1)]
        for matrix, rank in cases:
            with self.subTest(matrix=matrix):
                self.assertEqual(primary.rational_rank(matrix), rank)
                self.assertEqual(oracle.exact_rank(matrix), rank)
        self.assertEqual(oracle.exact_rank([[Fraction(1, 2), 1], [1, 2]]), 1)
        # The changed all-ones Gram has a two-total cost 2, so the floor is
        # specific to the inherited quadratic Gram, not every common label.
        self.assertEqual(2 * oracle.exact_rank([[1] * 16 for _ in range(16)]), 2)

    def test_coverage_and_symmetry_faults(self):
        bad = copy.deepcopy(self.certificate)
        bad["transports"].pop()
        with self.assertRaisesRegex(ValueError, "coverage omitted"):
            oracle.check_transports(bad)
        bad = copy.deepcopy(self.certificate)
        edge = next(row for row in bad["transports"] if row[1] != 0)
        edge[2] = next(g for g in range(9) if oracle.transform(edge[1], g) != edge[0])
        with self.assertRaisesRegex(ValueError, "false polynomial"):
            oracle.check_transports(bad)
        bad = copy.deepcopy(self.certificate)
        bad["transports"].append(bad["transports"][-1])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            oracle.check_transports(bad)

    def test_potential_and_word_faults(self):
        r = self.certificate["orbits"][0]
        functions = [[(f >> x) & 1 for x in range(32)]
                     for f in primary.factor_masks(r["mask"])]
        decoder = oracle.geometry()[3]
        mutations = []
        wrong_target = copy.deepcopy(r["unrestricted"])
        wrong_target["potential"][17] += 1
        mutations.append(wrong_target)
        false_unreachable = copy.deepcopy(r["unrestricted"])
        false_unreachable["potential"][17] = None
        mutations.append(false_unreachable)
        missing_term = copy.deepcopy(r["unrestricted"])
        missing_term["word"].pop()
        mutations.append(missing_term)
        same_price_wrong_map = copy.deepcopy(r["unrestricted"])
        same_price_wrong_map["word"] = [[1, 1], [1, 2]]
        mutations.append(same_price_wrong_map)
        free_decoder = copy.deepcopy(r["unrestricted"])
        free_decoder["minimum"] = 0
        mutations.append(free_decoder)
        wrong_cap = copy.deepcopy(r["unrestricted"])
        wrong_cap["rank_cap"] = 15
        mutations.append(wrong_cap)
        for receipt in mutations:
            with self.subTest(receipt=receipt["rank_cap"]):
                with self.assertRaises(ValueError):
                    oracle.check_potential(receipt, r["ranks"], functions, decoder)
        # An incorrect coefficient target must not be accepted by a decoder
        # that happens to have the right total rank.
        bad = copy.deepcopy(self.certificate)
        bad["target_coefficient_matrix_bits"] ^= 1
        with self.assertRaisesRegex(ValueError, "wrong matrix target"):
            oracle.verify_data(bad)
        # Zero-cost transitions must impose equality on the potential.
        weights = [[16] * 7 for _ in range(7)]
        weights[0][0] = 0
        free_edge = primary.shortest_paths(weights, 32)
        self.assertEqual(free_edge["minimum"], 16)
        self.assertEqual(free_edge["potential"][1], 0)
        primary.validate_graph_certificate(weights, free_edge)
        free_edge["potential"][1] = 1
        with self.assertRaisesRegex(ValueError, "potential violates"):
            primary.validate_graph_certificate(weights, free_edge)
        with self.assertRaisesRegex(ValueError, "edge potential"):
            oracle.check_potential(free_edge, weights, functions, decoder)

    def test_actual_rank_corruption(self):
        bad = copy.deepcopy(self.certificate)
        bad["orbits"][0]["ranks"][0][0] = 0
        with self.assertRaisesRegex(ValueError, "rational rank table mismatch"):
            oracle.verify_data(bad)

    def test_relocation_sources_and_output_preservation(self):
        with tempfile.TemporaryDirectory(prefix="quadratic package ") as directory:
            root = Path(directory)
            package = root / "standalone copy"
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            for file in package.rglob("*"):
                if file.is_file():
                    file.chmod(0o444)
            for script, marker in [("verify.py", "PASS_FIVE_CUBE_QUADRATIC_CODES"),
                                   ("independent.py", "PASS_INDEPENDENT_QUADRATIC_CODES")]:
                result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / script)],
                                        cwd=root, text=True, capture_output=True, timeout=120)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(marker, result.stdout)
            output = root / "occupied.json"
            output.write_text("preserve me\n")
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"),
                                     "--write", str(output)], cwd=root, text=True,
                                    capture_output=True, timeout=120)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_text(), "preserve me\n")
            fresh = root / "fresh.json"
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"),
                                     "--write", str(fresh)], cwd=root, text=True,
                                    capture_output=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(fresh.read_bytes(), (HERE / "CERTIFICATE.json").read_bytes())
            source = package / "sources" / "PR1046-PROOF.md"
            source.chmod(0o644)
            source.write_bytes(source.read_bytes() + b"\ncorrupted\n")
            for script in ["verify.py", "independent.py"]:
                result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / script)],
                                        cwd=root, text=True, capture_output=True, timeout=120)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("source", result.stderr.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
