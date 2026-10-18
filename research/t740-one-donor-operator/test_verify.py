#!/usr/bin/env python3
"""Small independent controls for the source-bound one-donor operator."""

from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v


def identity():
    return [[(int(row == column), 0) for column in range(8)] for row in range(8)]


def normalize_numeric(matrix, character):
    """Remove i^popcount(character) without using either replay's phase code."""
    exponent = -character.bit_count() % 4
    rotations = (
        lambda real, imag: (real, imag),
        lambda real, imag: (-imag, real),
        lambda real, imag: (-real, -imag),
        lambda real, imag: (imag, -real),
    )
    return [[rotations[exponent](*entry) for entry in row] for row in matrix]


class OperatorControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.context, cls.blocks = v.load_context()
        matrix, _ = v.symbolic_replay(cls.context, cls.blocks)
        cls.rows = v.normalized_rows(matrix)

    def test_quadratic_parity_and_same_phase_distinct_bases(self):
        separate = v.phase_add(v.phase_axis(1), v.phase_axis(2))
        difference = v.phase_add(v.phase_axis(3), v.phase_scale(separate, -1))
        self.assertEqual(v.phase_value(difference, 0), 0)
        for bit in range(73):
            self.assertEqual(v.phase_value(difference, 1 << bit), 0)
        # All coordinate characters miss this nonzero quadratic term.
        self.assertEqual(v.phase_value(difference, 3), 2)
        high_pair = v.phase_axis((1 << 72) | 1)
        self.assertEqual(v.phase_value(high_pair, (1 << 72) | 1), 0)
        self.assertEqual(v.phase_value(high_pair, 1 << 72), 1)

        coordinate = [1 << bit for bit in range(6)]
        complement = [63 ^ axis for axis in coordinate]
        self.assertNotEqual(coordinate, complement)
        for i, left in enumerate(complement):
            for j, right in enumerate(complement):
                self.assertEqual((left & right).bit_count() % 2, int(i == j))
        self.assertEqual(v.sum_axes(coordinate), v.sum_axes(complement))
        # Independence is essential to the rank consequence: repetition is free mod 4.
        self.assertEqual(v.sum_axes([1, 1, 1, 1]), v.ZERO_PHASE)

    def test_exact_nontrivial_specialization_and_identity(self):
        receipt = v.certify(self.context, self.blocks)
        self.assertEqual(receipt["residual_ranks"],
                         [[8, 48], [10, 48], [12, 48], [13, 48], [14, 1]])
        self.assertEqual(v.specialize(self.rows, (0, 0, 0, 0, 0)), identity())
        expected = [[(0, 0) for _ in range(8)] for _ in range(8)]
        diagonal = [(0, 1), (0, -1), (1, 0), (-1, 0),
                    (1, 0), (1, 0), (0, 1), (-1, 0)]
        for index, entry in enumerate(diagonal):
            expected[index][index] = entry
        expected[0][2] = (-1, 1)
        expected[3][1] = (1, -1)
        expected[5][1] = (2, 0)
        expected[5][3] = (-2, 0)
        self.assertEqual(v.specialize(self.rows, (1, 2, 3, 1, 2)), expected)

    def test_actual_donor_axis_removal_matches_formal_phase(self):
        donor_axes = self.context["residual"][14]
        self.assertEqual(donor_axes, [1 << 72])
        character = donor_axes[0]
        before = self.source.replay(self.context, self.context["residual"],
                                    character, self.blocks)
        self.assertEqual(normalize_numeric(before, character), identity())
        changed = deepcopy(self.context["residual"])
        changed[14].pop()
        after = self.source.replay(self.context, changed, character, self.blocks)
        actual = normalize_numeric(after, character)
        self.assertNotEqual(actual, identity())
        self.assertEqual(actual, v.specialize(self.rows, (0, 0, 0, 0, 3)))

    def test_omitted_hosted_prefix_is_detected(self):
        changed = deepcopy(self.context)
        time = next(time for time, events in changed["hosts"].items() if events)
        removed = changed["hosts"][time].pop(0)
        self.assertTrue(removed[1])
        # Keep hosted_axes metadata intact: replay must detect the missing action.
        with self.assertRaisesRegex(ValueError, "uncancelled ambient character phase"):
            v.certify(changed, self.blocks)

    def test_omitted_bridge_is_detected(self):
        changed = deepcopy(self.blocks)
        stage, index = next(
            (stage, index)
            for stage, events in changed.items()
            for index, event in enumerate(events)
            if event["kind"] == "bridge" and event["coefficient"] != 0
        )
        changed[stage].pop(index)
        with self.assertRaisesRegex(
                ValueError, "uncancelled ambient character phase|source-bound five-site matrix"):
            v.certify(self.context, changed)

    def test_changed_source_bytes_are_rejected(self):
        target = v.ROOT / v.SOURCE / "verify.py"
        original_read = Path.read_bytes
        intercepted = []

        def changed_read(path):
            data = original_read(path)
            if path == target:
                intercepted.append(path)
                return data + b"\n# synthetic source-pin fault\n"
            return data

        with patch.object(Path, "read_bytes", changed_read):
            with self.assertRaisesRegex(ValueError, "source hash: .*verify[.]py"):
                v.authenticate()
        self.assertEqual(intercepted, [target])


if __name__ == "__main__":
    unittest.main()
