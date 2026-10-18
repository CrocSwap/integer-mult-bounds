"""Independent finite oracles and failure controls for A4 shortening."""

import itertools
import json
import shutil
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import model
import verify
from a4_geometry import canonical, dot, root_lines


def independent_roots():
    """Describe doubled E8 roots by their support rather than the primary loops."""
    rows = set()
    for support in itertools.combinations(range(8), 2):
        for signs in itertools.product((-1, 1), repeat=2):
            row = tuple(
                2 * signs[support.index(i)] if i in support else 0 for i in range(8)
            )
            rows.add(max(row, tuple(-x for x in row)))
    for negative in range(0, 9, 2):
        for support in itertools.combinations(range(8), negative):
            row = tuple(-1 if i in support else 1 for i in range(8))
            rows.add(max(row, tuple(-x for x in row)))
    return tuple(sorted(rows))


def literal_costs(roots):
    vertices = [(0,) * 8] + [
        tuple(2 * int(i in (0, j)) for i in range(8)) for j in range(1, 5)
    ]
    result = []
    for root in roots:
        values = [sum(root[i] * vertex[i] for i in range(8)) for vertex in vertices]
        result.append(min(sum(value != shift for value in values) for shift in values))
    return result


def deletion_oracle(values, removed):
    """0/1 dynamic program, independent of sorted-cost deletion."""
    best = [None] * (removed + 1)
    best[0] = 0
    for index, value in enumerate(values):
        for count in range(min(index + 1, removed), 0, -1):
            prior = best[count - 1]
            if prior is not None:
                candidate = prior + value
                best[count] = (
                    candidate if best[count] is None else max(best[count], candidate)
                )
    if best[removed] is None:
        raise ValueError("deletion budget exceeds coordinate count")
    return sum(values) - best[removed]


class ShorteningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots = root_lines()
        cls.values = literal_costs(independent_roots())

    def test_independent_inventory_and_spectrum(self):
        self.assertEqual(independent_roots(), self.roots)
        self.assertEqual(dict(Counter(self.values)), model.SPECTRUM)
        self.assertEqual(sum(self.values), 170)

    def test_all_stabilizer_extensions(self):
        prefix = ()
        for expected in (240, 56, 27, 16):
            classes, _ = model.extensions(prefix, self.roots)
            self.assertEqual([n for _, n in classes], [expected])
            prefix += (classes[0][0],)
        self.assertEqual(dict(Counter(model.costs(prefix, self.roots))), model.SPECTRUM)

    def test_independent_cut_oracle_and_boundary(self):
        for small in (0, 20, 24, 26, 27):
            self.assertEqual(
                deletion_oracle(self.values, small + 8), model.support_lower(small)
            )
        self.assertEqual(model.support_lower(26), 102)
        self.assertEqual(
            model.support_lower(27), 100
        )  # A failed proof bound, not a counterexample.

    def test_each_coordinate_cost_is_attainable(self):
        self.assertTrue(all(cost in (0, 1, 2) for cost in self.values))
        for r in self.roots:
            values = [0] + [2 * (r[0] + r[j]) for j in range(1, 5)]
            direct = min(sum(v + shift != 0 for v in values) for shift in range(-8, 9))
            self.assertEqual(direct, 5 - max(Counter(values).values()))

    def test_applications_and_original_membership(self):
        survivors = model.original_survivors()
        self.assertEqual(len(survivors), 17)
        for weights, small, lower in zip(
            model.PROFILES, (24, 20), (106, 114), strict=True
        ):
            self.assertIn(weights, survivors)
            row = model.application(weights)
            self.assertEqual(
                (row["retained_code_dimension_lower"], row["common_support_cap"]),
                (4, small),
            )
            self.assertEqual((row["endpoint_lower"], row["endpoint_cap"]), (lower, 100))

    def test_dimension_drop_is_not_free(self):
        for weights in model.PROFILES:
            with self.assertRaisesRegex(ValueError, "four code dimensions"):
                model.application(weights, required_dimension=5)
            with self.assertRaisesRegex(ValueError, "hypotheses"):
                model.application(weights, deleted=1)

    def test_malformed_inputs_rejected(self):
        for small in (-1, 53, 26.0, True):
            with self.assertRaises(ValueError):
                model.support_lower(small)
        with self.assertRaises(ValueError):
            model.application((6,) * 9)
        with self.assertRaises(ValueError):
            model.extensions((), self.roots[:-1])
        with self.assertRaises(ValueError):
            model.extensions((self.roots[0], self.roots[0]), self.roots)
        with self.assertRaises(ValueError):
            model.costs(((0,) * 8,) * 4, self.roots)

    def test_weight_cover_with_independent_subset_oracle(self):
        for weights in model.PROFILES:
            for row in model.cover_audit(weights):
                basis = row["basis"]
                best = sum(model.CAP[w] for w in basis)
                subsets = tuple(
                    itertools.chain.from_iterable(
                        itertools.combinations(range(3), n) for n in range(4)
                    )
                )
                for first in subsets:
                    for second in subsets:
                        if set(first) & set(second):
                            continue
                        if (
                            max(
                                sum(basis[i] for i in first),
                                sum(basis[i] for i in second),
                            )
                            <= 6
                        ):
                            paid = sum(
                                model.CAP[basis[i]]
                                for i in range(3)
                                if i not in first and i not in second
                            )
                            best = min(best, paid)
                self.assertEqual(row["minimum_paid_cuts"], best)

    def test_source_and_receipt_corruption_rejected(self):
        with tempfile.TemporaryDirectory(prefix="a4-controls-") as directory:
            package = Path(directory)
            for name in ("SOURCES.json", "a4_geometry.py"):
                shutil.copyfile(verify.PACKAGE / name, package / name)
            verify.bind_sources(package=package)
            with (package / "a4_geometry.py").open("ab") as stream:
                stream.write(b"\n# altered source\n")
            with self.assertRaisesRegex(ValueError, "changed source"):
                verify.bind_sources(package=package)
        with self.assertRaisesRegex(ValueError, "receipt"):
            verify.check_receipt({"lower": 102}, {"lower": 100})

    def test_receipt_and_puncture_controls(self):
        expected = json.loads(verify.read_bytes(verify.PACKAGE / "RESULT.json"))
        self.assertEqual([row["margin"] for row in expected["applications"]], [6, 14])
        self.assertEqual(deletion_oracle(self.values, 34), 102)
        # Omitting the eight punctures would claim the wrong lower bound 118.
        self.assertEqual(deletion_oracle(self.values, 26), 118)
        self.assertEqual(len({canonical(r) for r in self.roots}), 120)
        self.assertTrue(all(dot(r, r) == 8 for r in self.roots))


if __name__ == "__main__":
    unittest.main()
