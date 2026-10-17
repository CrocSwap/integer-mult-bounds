"""Behavioral controls for the scoped shortening certificate."""

import copy
import json
import shutil
import tempfile
import unittest
from collections import Counter
from itertools import product
from pathlib import Path

import verify
from bound import after_cuts, shortening_contract, support_costs
from independent import integer_rank
from mixed import projective, rational_rank
from vendor.geometry import dot, root_data


class ShorteningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = verify.receipt()
        cls.roots, cls.points, _, _ = root_data()

    def test_01_committed_certificate_and_strict_contradiction(self):
        verify.check_receipt(
            self.result, json.loads(verify.read_bytes(verify.PACKAGE / "RESULT.json"))
        )
        self.assertEqual(self.result["mixed"]["minimum_after_30_cuts"], 121)
        self.assertEqual(self.result["root"]["minimum_after_30_cuts"], 122)
        self.assertEqual(self.result["contract"]["endpoint_allowance"], 120)

    def test_02_mixed_witness_full_edges_and_independence(self):
        rows = tuple(map(tuple, self.result["mixed"]["witness"]["vertices_doubled"]))
        self.assertEqual(integer_rank(rows), 5)
        allowed = {projective(r) for r in self.roots}
        self.assertTrue(any(projective(r) not in allowed for r in rows))
        vertices = ((0,) * 8,) + rows
        for i in range(6):
            for j in range(i):
                edge = tuple(
                    x - y for x, y in zip(vertices[i], vertices[j], strict=True)
                )
                self.assertLessEqual(sum(dot(p, edge) != 0 for p in self.points), 70)

    def test_03_mixed_witness_deletion_and_common_shifts(self):
        witness = self.result["mixed"]["witness"]
        rows = tuple(map(tuple, witness["vertices_doubled"]))
        cuts = set(witness["cuts"])
        self.assertEqual(len(cuts), 30)
        total = 0
        for i, p in enumerate(self.points):
            if i in cuts:
                continue
            values = (0,) + tuple(dot(p, row) for row in rows)
            best = min(
                sum(x + shift != 0 for x in values) for shift in {-x for x in values}
            )
            total += best
        self.assertEqual(total, 121)

    def test_04_root_witness_frame_and_exact_cost(self):
        star = tuple(map(tuple, self.result["root"]["star"]))
        frame = self.result["root"]["witness_frame"]
        self.assertEqual(len(frame), 8)
        for i in frame:
            for j in frame:
                self.assertEqual(dot(self.roots[i], self.roots[j]), 8 * (i == j))
        costs = support_costs(self.roots, star)
        self.assertEqual(
            after_cuts(tuple(c for i, c in enumerate(costs) if i not in frame), 30), 122
        )
        self.assertEqual(after_cuts(costs, 38), 120)

    def test_05_losing_controls_do_not_extend_the_theorem(self):
        self.assertEqual(self.result["root"]["minimum_after_31_cuts"], 120)
        self.assertLessEqual(self.result["mixed"]["minimum_after_31_cuts"], 120)
        for small, endpoints, dimension in (
            (31, (20,) * 6, 5),
            (30, (20,) * 6, 4),
            (30, (21,) * 6, 5),
        ):
            with self.assertRaises(ValueError):
                shortening_contract(small, endpoints, dimension)

    def test_06_support_contract_boundaries(self):
        for small in (0, 29, 30):
            result = shortening_contract(small, (20,) * 6, 5)
            self.assertGreater(result["minimum_contradiction_margin"], 0)
        for endpoints in ((20,) * 5, (False,) * 6, (-1,) * 6):
            with self.assertRaises(ValueError):
                shortening_contract(30, endpoints, 5)

    def test_07_coordinate_shift_formula_exhaustive(self):
        for values in product(range(3), repeat=6):
            expected = min(sum(x + s != 0 for x in values) for s in (0, -1, -2, 7))
            self.assertEqual(6 - max(Counter(values).values()), expected)

    def test_08_integer_rank_against_rational_rank(self):
        rows = tuple(map(tuple, self.result["mixed"]["witness"]["vertices_doubled"]))
        for length in range(1, 6):
            for sample in (rows[:length], (rows[0],) * length):
                self.assertEqual(integer_rank(sample), rational_rank(sample))
        self.assertEqual(integer_rank(rows), 5)
        self.assertEqual(integer_rank((rows[0],) * 5), 1)

    def test_09_incomplete_affine_vertices_reject(self):
        star = tuple(map(tuple, self.result["root"]["star"]))
        with self.assertRaises(ValueError):
            support_costs(self.points, star[:-1])
        for cuts in (-1, 113, True):
            with self.assertRaises(ValueError):
                after_cuts((1,) * 112, cuts)

    def test_10_source_binding_rejects_changed_missing_and_linked_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in verify.LIVE:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.ROOT / relative, target)
            self.assertEqual(verify.bind_sources(root), verify.INPUT_HASHES)
            path = root / verify.DATA
            original = path.read_bytes()
            path.write_bytes(original + b"\n")
            with self.assertRaises(ValueError):
                verify.bind_sources(root)
            path.unlink()
            with self.assertRaises(ValueError):
                verify.bind_sources(root)
            path.symlink_to(verify.ROOT / verify.DATA)
            with self.assertRaises(ValueError):
                verify.bind_sources(root)

    def test_11_semantic_receipt_mutations_reject(self):
        for section, field, value in (
            ("mixed", "minimum_after_30_cuts", 120),
            ("root", "frames", 2024),
            ("contract", "endpoint_allowance", 121),
            ("alphabet", "directions", 120),
        ):
            bad = copy.deepcopy(self.result)
            bad[section][field] = value
            with self.assertRaises(ValueError):
                verify.check_receipt(self.result, bad)

    def test_12_rank_and_cost_inputs_reject(self):
        with self.assertRaises(ValueError):
            integer_rank(((1, 2),))
        with self.assertRaises(ValueError):
            after_cuts((6,) * 112, 30)


if __name__ == "__main__":
    unittest.main(verbosity=2)
