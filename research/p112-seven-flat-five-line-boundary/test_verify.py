"""Behavioral and semantic controls for the literal boundary witness."""

import copy
import json
import unittest
from itertools import combinations
from unittest.mock import patch

import reference
import verify


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = verify.geometry()
        cls.roots, cls.points, cls.labels, _ = cls.g.root_data()
        cls.witness = json.loads((verify.PACKAGE / "WITNESS.json").read_text())

    def check(self, witness):
        return verify.check_witness(witness, self.roots, self.points, self.labels)

    def test_literal_witness(self):
        result = self.check(self.witness)
        self.assertEqual(result["gram_determinant"], 256)
        self.assertEqual(result["common_union_size"], 8)
        self.assertTrue(
            all(row["minimum_deletions"] == 5 for row in result["directions"])
        )

    def test_separate_lattice_reconstruction(self):
        self.assertEqual(reference.root_data(), (self.points, self.labels))

    def test_equivalent_annihilator_bases(self):
        changed = copy.deepcopy(self.witness)
        changed["first_flat_annihilator"] = [2, 67]
        changed["directions"][0]["second_flat_annihilator"] = [3, 130]
        self.assertEqual(self.check(changed), self.check(self.witness))

    def test_four_deletions_rejected(self):
        changed = copy.deepcopy(self.witness)
        changed["directions"][0]["deleted_lines"].pop()
        with self.assertRaisesRegex(ValueError, "five distinct"):
            self.check(changed)

    def test_wrong_fifth_deletion_rejected(self):
        changed = copy.deepcopy(self.witness)
        changed["directions"][0]["deleted_lines"][-1] = 3
        with self.assertRaisesRegex(ValueError, "incorrect deletion"):
            self.check(changed)

    def test_duplicate_deletion_rejected(self):
        changed = copy.deepcopy(self.witness)
        changed["directions"][0]["deleted_lines"][-1] = 0
        with self.assertRaisesRegex(ValueError, "five distinct"):
            self.check(changed)

    def test_out_of_range_deletion_rejected(self):
        changed = copy.deepcopy(self.witness)
        changed["directions"][0]["deleted_lines"][-1] = 112
        with self.assertRaisesRegex(ValueError, "five distinct"):
            self.check(changed)

    def test_dependent_directions_rejected(self):
        changed = copy.deepcopy(self.witness)
        changed["directions"][1] = copy.deepcopy(changed["directions"][0])
        with self.assertRaisesRegex(ValueError, "independent witness"):
            self.check(changed)

    def test_rank_deficient_flat_rejected(self):
        changed = copy.deepcopy(self.witness)
        changed["first_flat_annihilator"] = [2, 2]
        with self.assertRaisesRegex(ValueError, "rank two"):
            self.check(changed)

    def test_nonroot_direction_rejected(self):
        changed = copy.deepcopy(self.witness)
        changed["directions"][0]["h"] = [0] * 8
        with self.assertRaisesRegex(ValueError, "normalized root"):
            self.check(changed)

    def test_common_five_cut_is_not_claimed(self):
        changed = copy.deepcopy(self.witness)
        common = changed["directions"][0]["deleted_lines"]
        for entry in changed["directions"]:
            entry["deleted_lines"] = common.copy()
        with self.assertRaisesRegex(ValueError, "incorrect deletion"):
            self.check(changed)
        masks = [
            sum(1 << i for i in entry["deleted_lines"])
            for entry in self.witness["directions"]
        ]
        self.assertEqual((masks[0] | masks[1] | masks[2]).bit_count(), 8)

    def test_geometry_hash_guard(self):
        with patch.object(verify, "GEOMETRY_SHA", "0" * 64):
            with self.assertRaisesRegex(ValueError, "source changed"):
                verify.geometry()

    def test_binary_rank_two_algorithms_and_closure(self):
        alphabet = (1, 2, 4, 8, 16, 32, 64, 128, 256, 511)
        for size in range(11):
            for columns in combinations(alphabet, size):
                closure = {0}
                for column in columns:
                    closure |= {old ^ column for old in closure}
                expected = len(closure).bit_length() - 1
                self.assertEqual(verify.binary_rank(columns), expected)
                self.assertEqual(reference.rank(columns), expected)

    def test_binary_rank_bounds(self):
        for columns in ((512,), (0,), (True,), (1,) * 113):
            with self.assertRaisesRegex(ValueError, "column bounds"):
                verify.binary_rank(columns)
            with self.assertRaisesRegex(ValueError, "column bounds"):
                reference.rank(columns)

    def test_four_cut_oracle_has_losing_control(self):
        columns = tuple(1 << i for i in range(9))
        self.assertEqual(reference.minimum_four_deletion_rank(columns), (5, 126))


if __name__ == "__main__":
    unittest.main()
