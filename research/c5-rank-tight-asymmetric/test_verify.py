#!/usr/bin/env python3
"""Independent finite methods and scope controls, standard library only."""

import json
import unittest
from copy import deepcopy
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from unittest.mock import patch

import verify as v


def dense_rank(rows, modulus=None):
    if not rows:
        return 0
    work = [
        [Fraction(x) if modulus is None else x % modulus for x in row] for row in rows
    ]
    rank = 0
    for column in range(len(work[0])):
        pivot = next((i for i in range(rank, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        scale = 1 / scale if modulus is None else pow(scale, -1, modulus)
        work[rank] = [x * scale for x in work[rank]]
        if modulus:
            work[rank] = [x % modulus for x in work[rank]]
        for i in range(rank + 1, len(work)):
            scale = work[i][column]
            work[i] = [x - scale * y for x, y in zip(work[i], work[rank], strict=True)]
            if modulus:
                work[i] = [x % modulus for x in work[i]]
        rank += 1
        if rank == len(work):
            break
    return rank


def walk_cycles(planes):
    edges = [
        [
            j
            for j in range(56)
            if i != j
            and not any((a & b).bit_count() % 2 for a in planes[i] for b in planes[j])
        ]
        for i in range(56)
    ]
    found = set()
    for a in range(56):
        for b in edges[a]:
            for c in edges[b]:
                for d in edges[c]:
                    for e in edges[d]:
                        group = {a, b, c, d, e}
                        if (
                            len(group) == 5
                            and a in edges[e]
                            and all(
                                len(group.intersection(edges[i])) == 2 for i in group
                            )
                        ):
                            found.add(tuple(sorted(group)))
    return found


class ExactControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.planes = v.load_planes()
        cls.orders = v.cycles(cls.planes)
        cls.local = [cls.planes[i] for i in cls.orders[0]]

    def test_independent_cycle_census(self):
        self.assertEqual(
            walk_cycles(self.planes), {tuple(sorted(x)) for x in self.orders}
        )

    def test_all_rectangular_tariffs_against_dense_elimination(self):
        for cycle in self.orders:
            local = [self.planes[i] for i in cycle]
            for left in range(32):
                for right in range(32):
                    sources = [q for i in range(5) if left >> i & 1 for q in local[i]]
                    targets = [q for i in range(5) if right >> i & 1 for q in local[i]]
                    rows = [[(q & r).bit_count() % 2 for r in targets] for q in sources]
                    self.assertEqual(v.tariff(local, left, right), dense_rank(rows, 2))

    def test_baseline_rank_and_forced_blocks(self):
        a = v.baseline()
        matrix = v.multiply(a, v.transpose(a))
        self.assertEqual(dense_rank(matrix), 5)
        for i, j in combinations(range(5), 2):
            if (i - j) % 5 in (2, 3):
                ports = [2 * i, 2 * i + 1, 2 * j, 2 * j + 1]
                self.assertEqual(
                    [[matrix[p][q] for q in ports] for p in ports], v.identity(4)
                )

    def test_rational_unequal_factor_family_and_edge_dimensions(self):
        base = v.baseline()
        for i in range(5):
            for j in range(5):
                if i == j:
                    continue
                basis = v.identity(5)
                basis[i][j] = Fraction((-1) ** (i + j) * (i + 1), j + 2)
                a = v.multiply(base, basis)
                b = v.multiply(base, v.transpose(v.inverse(basis)))
                self.assertEqual(
                    v.multiply(a, v.transpose(b)), v.multiply(base, v.transpose(base))
                )
                self.assertEqual(dense_rank(a), 5)
                for k in range(5):
                    first, second = (
                        a[2 * k : 2 * k + 2],
                        a[2 * ((k + 1) % 5) : 2 * ((k + 1) % 5) + 2],
                    )
                    self.assertEqual(4 - dense_rank(first + second), 1)
                fit = v.inspect_fit(self.local, a, b)
                self.assertTrue(
                    all(t["tariff"] >= 4 and t["shared_edges"] for t in fit["terms"])
                )
                self.assertTrue(any(t["left"] != t["right"] for t in fit["terms"]))

    def test_dual_basis_coordinate_identity(self):
        h = v.identity(5)
        h[0][1], h[1][2], h[3][4] = Fraction(1, 2), Fraction(-2, 3), Fraction(4, 5)
        g = v.transpose(v.inverse(h))
        self.assertEqual(v.multiply(h, v.transpose(g)), v.identity(5))
        self.assertEqual(v.multiply(v.transpose(h), g), v.identity(5))
        for t in range(5):
            self.assertEqual(sum(h[i][t] * g[i][t] for i in range(5)), 1)
            self.assertTrue(any(h[i][t] and g[i][t] for i in range(5)))

    def test_six_terms_really_break_individual_charge_four(self):
        a, b = v.six_term_fixture()
        fit = v.inspect_fit(self.local, a, b)
        self.assertEqual([t["tariff"] for t in fit["terms"]], [2, 4, 4, 4, 4, 2])
        self.assertEqual(fit["cost"], 20)
        self.assertEqual(dense_rank(v.multiply(a, v.transpose(b))), 5)
        self.assertTrue(any(not t["shared_edges"] for t in fit["terms"]))

    def test_wrong_diagonal_and_forced_zero_rejected(self):
        bad = v.baseline()
        bad[0][4] = 0
        with self.assertRaisesRegex(ValueError, "strict scalar fit"):
            v.inspect_fit(self.local, bad, v.baseline())
        bad = v.baseline()
        bad[0][1] = 1
        with self.assertRaisesRegex(ValueError, "strict scalar fit"):
            v.inspect_fit(self.local, bad, v.baseline())

    def test_singular_change_and_zero_terms_rejected(self):
        bad = v.identity(5)
        bad[0] = bad[1][:]
        with self.assertRaisesRegex(ValueError, "invertible"):
            v.inverse(bad)
        a = [row + [0] for row in v.baseline()]
        with self.assertRaisesRegex(ValueError, "nonzero"):
            v.inspect_fit(self.local, a, a)

    def test_same_span_underpricing_mutant_is_detected(self):
        original = v.tariff
        with (
            patch.object(
                v, "tariff", side_effect=lambda p, a, b: original(p, a, b) - 1
            ),
            self.assertRaisesRegex(ValueError, "sharp and split"),
        ):
            v.build()

    def test_input_tampering_rejected(self):
        original = Path.read_bytes
        target = v.ROOT / v.INPUT / "MATCHING.json"

        def read_bytes(path):
            raw = original(path)
            return raw + b" " if path == target else raw

        with (
            patch.object(Path, "read_bytes", read_bytes),
            self.assertRaisesRegex(ValueError, "input hash"),
        ):
            v.load_planes()

    def test_receipt_equality(self):
        actual = v.build()
        self.assertEqual(actual, json.loads((v.HERE / "RESULT.json").read_bytes()))
        wrong = deepcopy(actual)
        wrong["five_term_cost_floor"] = 19
        self.assertNotEqual(actual, wrong)


if __name__ == "__main__":
    unittest.main()
