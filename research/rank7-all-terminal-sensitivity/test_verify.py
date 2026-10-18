#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral checks and separate finite oracles for terminal sensitivity."""

import copy
import itertools
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as Q
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import frames
import verify as V


class TerminalSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        V.authenticate()
        cls.tariffs = V.load_tariffs()
        cls.word = V.read_json(V.ROOT / V.SOURCE / "data/WORD-base.json.gz")
        cls.record = V.read_json(V.ROOT / V.SOURCE / "data/STAGE1-FRAME-EDITS.json")
        cls.certificate = V.read_json(V.ROOT / V.SOURCE / "certificates/RELAX-CAP.json")
        cls.receipt = V.read_json(V.PACKAGE / "RESULT.json")
        b = Q(cls.receipt["target_complex_saving"])
        cls.costs = {r: tuple(r * x for x in cls.tariffs.power_interval(Q(73, r), b))
                     for r in range(1, 49)}

    def test_frame_geometry_against_point_sets(self):
        # Complete subspace catalogue in F2^4, built from all generator subsets.
        spaces = {frames.basis(list(gens)) for size in range(5)
                  for gens in itertools.combinations(range(1, 16), size)}
        self.assertEqual(len(spaces), 67)
        points = {}
        for space in spaces:
            values = {0}
            for vector in space:
                values |= {value ^ vector for value in values}
            points[space] = values
            self.assertEqual(len(values), 1 << len(space))
        for outer in spaces:
            for inner in spaces:
                self.assertEqual(frames.contains(outer, inner), points[inner] <= points[outer])
        for bad in ([-1], [512], [True], list(range(513))):
            with self.assertRaises(ValueError):
                frames.basis(bad)

    def test_all_22_literal_single_widenings(self):
        rows, profile, widths = frames.terminal_changes(self.word, self.record)
        for row in rows:
            with self.subTest(helper=row["helper"]):
                word = copy.deepcopy(self.word)
                word["helper_final"][str(row["helper"])] = row["old"]
                expected = dict(profile)
                expected[1] += 1
                inventory = dict(widths)
                inventory[row["width_before"]] -= 1
                inventory[row["width_after"]] += 1
                word["report"]["local_profile"] = {str(r): n for r, n in expected.items()}
                word["report"]["width_inventory"] = {str(r): n for r, n in inventory.items()}
                _, _, _, actual, actual_widths = frames.recount(word)
                self.assertEqual(dict(actual), expected)
                self.assertEqual(dict(actual_widths), inventory)

    def test_reject_stale_endpoint_and_entrance_claims(self):
        for kind in ("old", "missing", "duplicate", "entrance", "terminal"):
            word, record = copy.deepcopy(self.word), copy.deepcopy(self.record)
            if kind == "old":
                record["helper_final_changes"]["249"]["old"] = record["groups"]["V45"][0]
            elif kind == "missing":
                record["groups"]["A"][1].pop()
            elif kind == "duplicate":
                record["groups"]["A"][1][0] = 249
            elif kind == "entrance":
                word["start_extra"]["450"] = []
            else:
                word["helper_final"]["249"] = record["helper_final_changes"]["249"]["old"]
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                frames.terminal_changes(word, record)

    def test_pattern_completeness_by_combinations(self):
        oracle = set()
        for capacity in V.CAPS:
            for length in range(capacity // 4 + 1):
                for widths in itertools.combinations_with_replacement(V.WIDTHS, length):
                    if sum(widths) <= capacity:
                        oracle.add((capacity, widths))
        self.assertEqual(set(V.patterns()), oracle)
        self.assertEqual(len(oracle), 2551)
        for capacity in V.CAPS:
            self.assertIn((capacity, ()), oracle)

    def test_dual_equations_and_width_class_identity(self):
        local = {int(r): n for r, n in self.certificate["local_per_call"].items()}
        inventory = {int(r): n for r, n in self.certificate["inventory_per_call"].items()}
        dual, base, _ = V.dual_certificate(self.certificate, local, inventory, self.costs)
        # Verify the formal dual directly on each defining pattern, without elimination.
        for entry in self.certificate["basis_patterns"]:
            column = V.features(entry["capacity"], tuple(entry["widths"]))
            idle = entry["capacity"] - sum(entry["widths"])
            for rank in V.IDLE:
                self.assertEqual(sum(n * row[rank] for n, row in zip(column, dual, strict=True)),
                                 int(idle == rank))
        expected = {1: Q(9), 3: Q(9, 20), 5: Q(9, 4), 48: Q(-9, 20)}
        self.assertEqual(V.sensitivity(dual, 6), expected)
        self.assertEqual(V.sensitivity(dual, 7), expected)
        self.assertEqual(V.strings(base), self.receipt["base_polynomial"])
        # At zero saving every change conserves rank mass and the surcharge is zero.
        self.assertEqual(sum(r * c for r, c in expected.items()), 0)

    def test_reject_bad_primal(self):
        local = {int(r): n for r, n in self.certificate["local_per_call"].items()}
        inventory = {int(r): n for r, n in self.certificate["inventory_per_call"].items()}
        for kind in ("overfull", "duplicate", "count", "width"):
            cert = copy.deepcopy(self.certificate)
            if kind == "overfull":
                cert["basis_patterns"][0]["widths"] = [9]
            elif kind == "duplicate":
                cert["basis_patterns"][1] = cert["basis_patterns"][0]
            elif kind == "count":
                cert["basis_patterns"][0]["count_per_replica"] = "673"
            else:
                inventory = dict(inventory)
                inventory[6] += 1
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                V.dual_certificate(cert, local, inventory, self.costs)

    def test_exact_power_enclosures(self):
        for rank in (1, 3, 5, 7, 8, 48):
            for numerator, denominator in ((0, 1), (1, 128), (1, 200), (3, 512)):
                low, high = self.tariffs.power_interval(Q(73, rank), Q(numerator, denominator))
                exact = Q(73, rank) ** numerator
                self.assertLessEqual(low ** denominator, exact)
                self.assertGreaterEqual(high ** denominator, exact)
        for value, exponent in ((Q(0), Q(0)), (Q(74), Q(0)), (Q(2), Q(1))):
            with self.assertRaises(ValueError):
                self.tariffs.power_interval(value, exponent)

    def test_every_subset_by_count_and_positive_control(self):
        values = [Q(self.receipt["normalized_lower_by_count"][str(k)]) for k in range(23)]
        self.assertLess(values[0], 1)
        self.assertTrue(all(value > 1 for value in values[1:]))
        self.assertTrue(all(a < b for a, b in itertools.pairwise(values)))
        self.assertLess(Q(self.receipt["literal_original_moment"][1]), 1)
        # Independent count via binomial multiplicities, without enumerating subsets.
        self.assertEqual(self.receipt["nonempty_subsets"], sum(comb(22, k) for k in range(1, 23)))
        self.assertEqual(self.receipt["nonempty_subsets"], 4194303)

    def test_sharp_occurrence_count_and_singleton_primals(self):
        self.assertEqual(self.receipt["potential_occurrences"], 22 * 666)
        self.assertEqual(self.receipt["sharp_fractional_failure_count"], 2)
        bounds = self.receipt["normalized_lower_by_occurrence_count"]
        self.assertLess(Q(bounds["1"]), 1)
        self.assertGreater(Q(bounds["2"]), Q(1000000000041, 10**12))
        for width in (6, 7):
            primal = self.receipt["singleton_fractional_primals"][str(width)]
            amounts = list(map(Q, primal["basis_amounts_at_T74"]))
            self.assertTrue(all(n >= 0 for n in amounts))
            capacity = {c: Q(0) for c in V.CAPS}
            inventory = {w: Q(0) for w in V.WIDTHS}
            for entry, amount in zip(self.certificate["basis_patterns"], amounts, strict=True):
                capacity[entry["capacity"]] += amount
                for w in entry["widths"]:
                    inventory[w] += amount
            self.assertEqual(capacity, dict(zip(V.CAPS, [74 * n for n in (672, 448, 448, 448)], strict=True)))
            expected = {int(w): Q(666 * n) for w, n in self.certificate["inventory_per_call"].items()}
            expected[width] -= 1
            expected[width + 1] += 1
            self.assertEqual(inventory, expected)
            self.assertLess(Q(primal["moment"][1]), 1)

    def test_json_and_interval_sign_controls(self):
        with self.assertRaises(ValueError):
            json.loads('{"x": 1, "x": 2}', object_pairs_hook=V.pairs)
        self.assertEqual(V.interval({1: Q(2), 2: Q(-3)}, {1: (Q(2), Q(3)), 2: (Q(5), Q(7))}),
                         (Q(-17), Q(-9)))
        with self.assertRaises(ValueError):
            V.solve([[Q(0)] * 10] * 10, [[Q(0)] * 4] * 10)

    def test_optimized_git_free_read_only_export_and_source_rejection(self):
        sources = V.read_json(V.PACKAGE / "SOURCES.json")
        inputs = [V.ROOT / e["path"] for e in sources["files"] if e["usage"] == "input"]
        local = [p for p in V.PACKAGE.iterdir() if p.is_file()]
        with tempfile.TemporaryDirectory(prefix="terminal-export-") as directory:
            root = Path(directory)
            for path in local + inputs:
                target = root / path.relative_to(V.ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
                target.chmod(0o444)
            script = root / V.PACKAGE.relative_to(V.ROOT) / "verify.py"
            command = [sys.executable, "-I", "-O", "-B", "-Werror", str(script)]
            result = subprocess.run(command, cwd=root, capture_output=True, text=True,
                                    timeout=120, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_ALL_TERMINAL_SENSITIVITY", result.stdout)
            corrupt = root / V.SOURCE / "data/STAGE1-FRAME-EDITS.json"
            corrupt.chmod(0o644)
            corrupt.write_bytes(corrupt.read_bytes() + b" ")
            corrupt.chmod(0o444)
            result = subprocess.run(command, cwd=root, capture_output=True, text=True,
                                    timeout=120, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source SHA256", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
