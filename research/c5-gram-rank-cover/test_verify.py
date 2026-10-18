#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with OpenAI Codex.
"""Independent geometry, cover, and scalar-boundary controls."""

from fractions import Fraction
import gzip
import json
from pathlib import Path
import tempfile
import unittest

import verify


ROOT = Path(__file__).resolve().parents[2]
CORE = (13, 23, 35, 16, 34)


def bit_dot(a, b):
    return sum(((a >> bit) & 1) * ((b >> bit) & 1)
               for bit in range(max(a, b).bit_length())) % 2


def dense_pairing(left, right):
    matrix = [[bit_dot(a, b) for b in right] for a in left]
    rank = 0
    for column in range(len(right)):
        pivot = next((row for row in range(rank, len(matrix))
                      if matrix[row][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        for row in range(rank + 1, len(matrix)):
            if matrix[row][column]:
                matrix[row] = [a ^ b for a, b in zip(matrix[row], matrix[rank])]
        rank += 1
    return rank


def dfs_cycles(planes):
    neighbors = [set() for _ in planes]
    for i in range(len(planes)):
        for j in range(i + 1, len(planes)):
            if all(bit_dot(a, b) == 0 for a in planes[i] for b in planes[j]):
                neighbors[i].add(j)
                neighbors[j].add(i)
    cycles = {}

    def visit(path):
        if len(path) == 5:
            if (path[0] in neighbors[path[-1]] and
                    all(sum(other in neighbors[node] for other in path) == 2
                        for node in path)):
                cycles.setdefault(tuple(sorted(path)), tuple(path))
            return
        for following in sorted(neighbors[path[-1]]):
            if following > path[0] and following not in path:
                visit(path + [following])

    for first in range(len(planes)):
        visit([first])
    return cycles


def vector(*entries):
    result = [0] * 10
    for index, value in entries:
        result[index] = value
    return tuple(result)


def baseline():
    return [(Fraction(1), vector((a, 1), (b, 1)))
            for a, b in ((1, 2), (3, 4), (5, 6), (7, 8), (9, 0))]


class RankCoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        inputs = ROOT / "research/c5-dyadic-decoder-gate/inputs"
        recipes = json.loads(gzip.decompress(
            (inputs / "DATA-PHASES.json.gz").read_bytes()))["recipes"]
        labels = {row["port"]: row["q"] for row in recipes}
        cls.matching = json.loads((inputs / "MATCHING.json").read_bytes())["matching"]
        cls.planes = [[labels[port] for port in pair] for pair in cls.matching]
        cls.cycles = dfs_cycles(cls.planes)
        cls.core = [cls.planes[i] for i in CORE]

    def test_authenticated_geometry_matches_independent_parse(self):
        matching, planes = verify.load_geometry()
        self.assertEqual(matching, self.matching)
        self.assertEqual(planes, self.planes)
        self.assertEqual([port for i in CORE for port in matching[i]],
                         [21, 16, 41, 29, 69, 57, 35, 22, 64, 54])
        self.assertEqual([label for plane in self.core for label in plane],
                         [289, 49, 194, 134, 304, 56, 50, 193, 200, 196])
        for plane in planes:
            self.assertEqual([[bit_dot(a, b) for b in plane] for a in plane],
                             [[1, 0], [0, 1]])

    def test_induced_cycle_census_matches_independent_dfs(self):
        actual = verify.induced_cycles(self.planes)
        self.assertEqual(len(self.cycles), 23)
        self.assertEqual(len(actual), 23)
        self.assertEqual({tuple(sorted(cycle)) for cycle in actual}, set(self.cycles))

    def test_all_736_full_plane_tariffs_cover_incident_blocks(self):
        checked = 0
        for cycle in self.cycles:
            planes = [self.planes[i] for i in cycle]
            pairs = [(i, j) for i in range(5) for j in range(i + 1, 5)
                     if any(bit_dot(a, b) for a in planes[i] for b in planes[j])]
            self.assertEqual(len(pairs), 5)
            prices = verify.costs_for(planes)
            self.assertEqual(len(prices), 32)
            for mask in range(32):
                with self.subTest(cycle=cycle, mask=mask):
                    full_space = [value for i, plane in enumerate(planes)
                                  if mask & (1 << i) for value in plane]
                    independent = dense_pairing(full_space, full_space)
                    self.assertEqual(prices[mask], independent)
                    self.assertEqual(verify.pairing(full_space, full_space), independent)
                    block_count = sum(bool(mask & ((1 << i) | (1 << j)))
                                      for i, j in pairs)
                    self.assertGreaterEqual(independent, block_count)
                    checked += 1
        self.assertEqual(checked, 736)
        self.assertEqual(verify.costs_for(self.core)[5], 3)

    def test_every_cycle_has_a_cost_twenty_scalar_fit(self):
        for cycle in self.cycles.values():
            with self.subTest(cycle=cycle):
                self.assertEqual(verify.check_gram(
                    [self.planes[i] for i in cycle], baseline()), 20)

    def test_label_only_mask_would_admit_a_false_cost_nineteen_fit(self):
        terms = [(Fraction(1), vector((i, 1))) for i in range(10) if i not in (0, 4)]
        terms.append((Fraction(1), vector((0, 1), (4, 1))))
        self.assertEqual(bit_dot(self.core[0][0], self.core[2][0]), 0)
        price = 0
        for _, row in terms:
            full_space = [value for i, plane in enumerate(self.core)
                          if row[2 * i] or row[2 * i + 1] for value in plane]
            price += dense_pairing(full_space, full_space)
        self.assertEqual(price, 19)
        with self.assertRaises(ValueError):
            verify.check_gram(self.core, terms)

    def test_signed_cancellation_still_pays_thirty(self):
        terms = baseline() + [
            (Fraction(-1, 2), vector((0, 1), (4, 1))),
            (Fraction(-1, 2), vector((0, 1), (4, -1))),
            (Fraction(1), vector((0, 1))),
            (Fraction(1), vector((4, 1))),
        ]
        for i in range(10):
            for j in range(10):
                self.assertEqual(sum(weight * row[i] * row[j] for weight, row in terms),
                                 sum(weight * row[i] * row[j] for weight, row in baseline()))
        self.assertEqual(verify.check_gram(self.core, terms), 30)

    def test_missing_payload_and_wrong_normalization_are_rejected(self):
        for terms in (baseline()[:-1], [(weight / 2, row) for weight, row in baseline()]):
            with self.subTest(terms=terms), self.assertRaises(ValueError):
                verify.check_gram(self.core, terms)

    def test_asymmetric_spans_do_not_obey_the_cover_tariff(self):
        left, right = self.core[2], self.core[0] + self.core[4]
        self.assertEqual(dense_pairing(left, right), 1)
        self.assertEqual(verify.pairing(left, right), 1)
        pairs = [(i, j) for i in range(5) for j in range(i + 1, 5)
                 if any(bit_dot(a, b) for a in self.core[i] for b in self.core[j])]
        touched = sum(2 in pair and any(i in pair for i in (0, 4)) for pair in pairs)
        self.assertEqual(touched, 2)
        self.assertLess(verify.pairing(left, right), touched)

    def test_changed_input_bytes_are_rejected(self):
        sources = json.loads(Path(__file__).with_name("SOURCES.json").read_bytes())
        paths = [pin["path"] for pin in sources["files"] if pin["usage"] == "input"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in paths:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / name).read_bytes())
            self.assertEqual(verify.load_geometry(root=root), (self.matching, self.planes))
            for name in paths:
                with self.subTest(path=name):
                    target = root / name
                    original = target.read_bytes()
                    changed = (gzip.compress(gzip.decompress(original) + b"\n", mtime=0)
                               if target.suffix == ".gz" else original + b"\n")
                    target.write_bytes(changed)
                    try:
                        with self.assertRaises(ValueError):
                            verify.load_geometry(root=root)
                    finally:
                        target.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
