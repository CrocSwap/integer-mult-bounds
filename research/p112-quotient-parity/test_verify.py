"""Behavioral and failure controls, including separate rational circuit checks."""

import tempfile
import unittest
from fractions import Fraction
from itertools import combinations, product
from math import comb
from pathlib import Path

from geometry import (
    canonical,
    dot,
    flat_capacity,
    require,
    root_data,
    root_plane_receipt,
)
from quotient import (
    application,
    good_extension,
    matching_receipt,
    original_filter_control,
    partial_matchings,
)
from verify import DATA, ROOT, bind_data, simplex_control


def rational_rank(matrix):
    """Small independent oracle; fixed bounds cover only the fixtures below."""
    require(len(matrix) <= 8 and all(len(row) <= 10 for row in matrix), "rank bounds")
    rows = [list(map(Fraction, row)) for row in matrix]
    require(bool(rows) and len({len(row) for row in rows}) == 1, "rank shape")
    rank = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][col]
        rows[rank] = [x / scale for x in rows[rank]]
        for i in range(rank + 1, len(rows)):
            factor = rows[i][col]
            rows[i] = [x - factor * y
                       for x, y in zip(rows[i], rows[rank], strict=True)]
        rank += 1
        if rank == len(rows):
            break
    return rank


class QuotientControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots, cls.points, cls.labels, _ = root_data()

    def test_all_odd_matchings(self):
        self.assertEqual(matching_receipt()["matchings"], 232)
        # Independent telephone-number recurrence.
        counts = [1, 1]
        for n in range(2, 8):
            counts.append(counts[-1] + (n - 1) * counts[-2])
        self.assertEqual(counts[7], len(partial_matchings(7)))

    def test_even_parity_is_required(self):
        with self.assertRaisesRegex(ValueError, "perfect matching"):
            good_extension((1, 0, 3, 2, 5, 4))
        self.assertTrue(any(len(edges) == 3 for edges in partial_matchings(6)))

    def test_bad_partner_contracts(self):
        for partners in ((0,), (1, None), (2, 0), (True, 0), [None] * 7):
            with self.subTest(partners=partners), self.assertRaises(ValueError):
                good_extension(partners)

    def test_matching_capacity(self):
        for size in (-1, 9, True):
            with self.assertRaises(ValueError):
                partial_matchings(size)

    def test_six_distinct_five_piece_circuit_lines(self):
        # Six rational moment-curve columns in dimension four. This realizes
        # the forbidden abstract restriction before imposing E8 root geometry.
        columns = [tuple(t ** k for k in range(4)) for t in range(6)]
        for indices in combinations(range(6), 4):
            self.assertEqual(rational_rank([columns[i] for i in indices]), 4)
        w = [(-1) ** i * comb(5, i) for i in range(6)]
        circuits = [[w[i] * (i - j) for i in range(6)] for j in range(6)]
        for j, circuit in enumerate(circuits):
            self.assertEqual([i for i, x in enumerate(circuit) if not x], [j])
            self.assertEqual([sum(circuit[i] * columns[i][k] for i in range(6))
                              for k in range(4)], [0] * 4)
        self.assertEqual(rational_rank(circuits), 2)
        self.assertEqual(len({canonical(row) for row in circuits}), 6)

    def test_generic_quotient_has_good_extension(self):
        columns = [tuple(t ** k for k in range(5)) for t in range(10)]
        chosen = columns[:4]
        self.assertEqual(rational_rank(chosen), 4)
        for column in columns[4:]:
            self.assertEqual(rational_rank([*chosen, column]), 5)

    def test_root_plane_inventory(self):
        self.assertEqual(root_plane_receipt(self.roots), {"2": 3780, "3": 3360})

    def test_mutated_root_plane_input(self):
        with self.assertRaisesRegex(ValueError, "root-plane input"):
            root_plane_receipt(self.roots[:-1])

    def test_root_supports_and_injective_gram(self):
        self.assertEqual({sum(dot(r, p) != 0 for p in self.points)
                          for r in self.roots}, {53, 56})
        gram = [[sum(p[i] * p[j] for p in self.points) for j in range(8)]
                for i in range(8)]
        self.assertEqual(rational_rank(gram), 8)

    def test_simplex_and_endpoint_counts(self):
        control = simplex_control(self.roots, self.points)
        maximum = max(i for i, n in enumerate(control["incidence_histogram"]) if n)
        self.assertEqual(maximum, 9)
        # Exhaust all six endpoint assignments from a four-level alphabet.
        for values in product(range(4), repeat=6):
            k = sum(x != 0 for x in values)
            self.assertLessEqual(sum(a != b for a, b in combinations(values, 2)), 5 * k)

    def test_input_binding_and_mutation(self):
        bind_data(ROOT / DATA, self.points, self.labels)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.txt"
            path.write_bytes((ROOT / DATA).read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "changed P112 input"):
                bind_data(path, self.points, self.labels)
        with self.assertRaisesRegex(ValueError, "label binding"):
            bind_data(ROOT / DATA, self.points, tuple(reversed(self.labels)))

    def test_unused_capacity_and_label_mutants(self):
        with self.assertRaises(ValueError):
            flat_capacity(self.labels, 6)
        with self.assertRaisesRegex(ValueError, "invalid P112 labels"):
            flat_capacity((0, *self.labels[1:]), 5)

    def test_exact_application_and_old_failure(self):
        row = application()
        self.assertEqual(row["contradiction_margin"], 39)
        self.assertEqual(row["edge_support_cap"], 68)
        self.assertGreaterEqual(row["failed_old_quotient_support_cap"], 53)
        # Losing the cap-eight piece makes the root-edge test fail.
        self.assertGreaterEqual(4 * 12 + 2 * 12, 70)

    def test_original_filter_binding(self):
        self.assertTrue(original_filter_control()["original_BK_BK7_survivor"])


if __name__ == "__main__":
    unittest.main()
