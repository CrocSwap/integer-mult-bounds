"""Behavioral controls and separate finite oracles for the scoped theorem."""

import os
import tempfile
import unittest
from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path

from beta import (
    CAP,
    PROFILES,
    application,
    beta_receipt,
    prefixes,
    support_budget,
    survives,
)
from geometry import canonical, dot, primitive, root_data
from verify import (
    DATA,
    ROOT,
    bind_data,
    matching_receipt,
    quotient_control,
    simplex_control,
)


def rational_rank(vectors):
    """Separate small fixture oracle, bounded by eight rows/columns."""
    if not vectors:
        return 0
    rows = [list(map(Fraction, row)) for row in vectors]
    if len(rows) > 8 or any(len(row) != len(rows[0]) or len(row) > 8 for row in rows):
        raise ValueError("fixture rank domain")
    rank = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][col]
        rows[rank] = [x / scale for x in rows[rank]]
        for i in range(len(rows)):
            if i != rank:
                scale = rows[i][col]
                rows[i] = [x - scale * y
                           for x, y in zip(rows[i], rows[rank], strict=True)]
        rank += 1
    return rank


def original_filter_oracle(weights):
    """Independent prefix selection and subset packing, following PR3154."""
    if sum(weights) >= 30 + 2 * len(weights):
        return False
    caps = (0, 0, 2, 4, 8, 12, 20, 36)
    for level in range(1, 6):
        kept = sorted(weights, reverse=True)[5 - level:]
        total = sum(caps[w] for w in kept)
        target = total - 4 * kept.count(7)
        threshold = (0, 53, 78, 92, 100, 106)[level]
        if level == 1 and target < 53 and total < 73:
            return False
        if level == 2 and target < 78 and total < 82:
            return False
        if level >= 3 and total < threshold:
            return False
    small = sorted(weights)[:len(weights) - 5]
    if sum(caps[w] for w in small) >= 53:
        return True
    if sum(small) <= 7:
        return False
    for count in range(len(small) + 1):
        for subset in combinations(range(len(small)), count):
            left = sum(small[i] for i in subset)
            if left <= 6 and sum(small) - left <= 6:
                return False
    return True


class QuotientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots, cls.points, cls.labels, _ = root_data()

    def test_three_actual_profiles(self):
        for weights in PROFILES:
            row = application(weights)
            self.assertEqual(row["prefix_caps"], (68, 80, 92, 104, 116))
            self.assertEqual(row["deficit"], 1)
            self.assertEqual(row["contradiction_margin"], 39)

    def test_independent_filter_all_multisets(self):
        survivors = []
        for size in range(5, 12):
            for weights in combinations_with_replacement(range(2, 8), size):
                decision = original_filter_oracle(weights)
                self.assertEqual(survives(weights), decision, weights)
                if decision:
                    survivors.append(weights)
        self.assertEqual(survivors, beta_receipt()["original_survivors"])

    def test_support_only_basis_cannot_certify(self):
        for weights in PROFILES:
            caps = sorted(CAP[w] for w in weights)
            self.assertEqual(sum(caps[:6]), 56)
            row = application(weights)
            self.assertEqual(row["old_support_basis_subsets"], 462)
            self.assertEqual(row["support_certified_bases"], 0)

    def test_strict_root_cutoff(self):
        self.assertEqual(support_budget(32, 12), (44, 72, 756))
        self.assertEqual(support_budget(33, 12), (45, 72, 765))
        with self.assertRaisesRegex(ValueError, "strict quotient"):
            support_budget(34, 12)

    def test_invalid_capacity_contract(self):
        for small, endpoint in ((0, 12), (32, -1), (113, 12), (True, 12)):
            with self.assertRaises(ValueError):
                support_budget(small, endpoint)

    def test_invalid_profiles(self):
        for weights in ((), (3,) * 12, (1,) * 11, (8,) * 11, (5, 4) + (5,) * 9):
            with self.assertRaises(ValueError):
                survives(weights)
        with self.assertRaises(ValueError):
            application((5,) * 11)

    def test_odd_classes_and_independent_count(self):
        counts = [1, 1]
        for size in range(2, 9):
            counts.append(counts[-1] + (size - 1) * counts[-2])
        for size in range(1, 9):
            row = matching_receipt(size)
            self.assertEqual(row["partitions"], counts[size])
            if size % 2:
                self.assertEqual(row["singleton_histogram"][0], 0)
        self.assertEqual(matching_receipt(7)["partitions"], 232)

    def test_even_classes_are_a_failure_control(self):
        self.assertEqual(matching_receipt(8)["singleton_histogram"][0], 105)

    def test_matching_domain(self):
        for size in (0, 9, True):
            with self.assertRaises(ValueError):
                matching_receipt(size)

    def test_abstract_quotient_rank_oracle(self):
        vectors = quotient_control()["vectors"]
        basis = [tuple(int(i == j) for i in range(6)) for j in range(4)]
        lifted = [(0, 0, 0, 0, a, b) for a, b in vectors]
        self.assertEqual(rational_rank([*basis, lifted[-1]]), 5)
        for vertex in lifted[:-1]:
            self.assertEqual(rational_rank([*basis, lifted[-1], vertex]), 6)
        self.assertEqual(rational_rank(lifted), 2)

    def test_two_dimensional_space_has_more_than_120_lines(self):
        a, b = self.roots[:2]
        self.assertEqual(rational_rank([a, b]), 2)
        directions = {primitive(tuple(Fraction(x + t * y)
                                      for x, y in zip(a, b, strict=True)))
                      for t in range(121)}
        root_directions = {primitive(tuple(map(Fraction, row))) for row in self.roots}
        self.assertEqual(len(directions), 121)
        self.assertTrue(directions - root_directions)

    def test_source_binding_and_mutation(self):
        path = ROOT / DATA
        self.assertEqual(len(bind_data(path, self.points, self.labels)), 64)
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as directory:
            mutant = Path(directory) / "mutant.txt"
            mutant.write_bytes(path.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "changed P112"):
                bind_data(mutant, self.points, self.labels)

    def test_ordered_source_binding(self):
        with self.assertRaisesRegex(ValueError, "root binding"):
            bind_data(ROOT / DATA, tuple(reversed(self.points)), self.labels)
        with self.assertRaisesRegex(ValueError, "label binding"):
            bind_data(ROOT / DATA, self.points, tuple(reversed(self.labels)))

    def test_simplex_literal_incidence(self):
        row = simplex_control(self.roots, self.points)
        histogram = [0] * 16
        for point in self.points:
            levels = [sum(x * y for x, y in zip(point, vertex, strict=True))
                      for vertex in row["vertices"]]
            count = sum(levels[i] != levels[j] for i in range(6) for j in range(i))
            histogram[count] += 1
        self.assertEqual(row["histogram"], histogram)
        self.assertEqual(max(i for i, count in enumerate(histogram) if count), 9)

    def test_outside_endpoint_incidence(self):
        for values in product(range(-2, 3), repeat=6):
            nonzero = sum(value != 0 for value in values)
            unequal = sum(a != b for a, b in combinations(values, 2))
            self.assertLessEqual(unequal, 5 * nonzero)

    def test_code_evaluation_is_injective(self):
        gram = [[sum(dot(point, a) * dot(point, b) for point in self.points)
                 for b in self.roots[:8]] for a in self.roots[:8]]
        self.assertEqual(rational_rank(gram), rational_rank(self.roots[:8]))
        coordinate_gram = [[sum(point[i] * point[j] for point in self.points)
                            for j in range(8)] for i in range(8)]
        self.assertEqual(coordinate_gram, [[112 * (i == j) for j in range(8)]
                                          for i in range(8)])
        self.assertEqual(rational_rank(coordinate_gram), 8)

    def test_small_weight_support_caps(self):
        self.assertEqual([CAP[w] for w in (2, 3, 4)], [2 ** (w - 1) for w in (2, 3, 4)])
        self.assertEqual(prefixes(PROFILES[0])[0], 68)
        self.assertEqual(len({canonical(row) for row in self.roots}), 120)


if __name__ == "__main__":
    unittest.main()
