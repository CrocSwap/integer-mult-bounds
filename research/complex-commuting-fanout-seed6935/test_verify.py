import unittest
from fractions import Fraction as Q

from verify import (
    gap_commutes_with_fanout,
    identity,
    matmul,
    operation_matrix,
    verify_fanout_map,
)


class CommutatorTests(unittest.TestCase):
    def assert_exactly_commutes(self, operation, source, destinations):
        for destination in destinations:
            selected = ["add", destination, source, 2, 3]
            left = matmul(operation_matrix(operation, 6), operation_matrix(selected, 6))
            right = matmul(operation_matrix(selected, 6), operation_matrix(operation, 6))
            self.assertEqual(left, right)

    def assert_does_not_commute(self, operation, source, destinations):
        found_witness = False
        for destination in destinations:
            selected = ["add", destination, source, 2, 3]
            left = matmul(operation_matrix(operation, 6), operation_matrix(selected, 6))
            right = matmul(operation_matrix(selected, 6), operation_matrix(operation, 6))
            found_witness |= left != right
        self.assertTrue(found_witness)

    def test_positive_target_write_and_common_source_read(self):
        source, destinations = 0, [2, 3, 4]
        writes_target = ["add", 2, 1, 5, 7]
        reads_source = ["add", 1, 0, -3, 5]
        zero_add = ["add", 0, 2, 0, 1]
        for operation in (writes_target, reads_source, zero_add):
            self.assertTrue(gap_commutes_with_fanout(operation, source, destinations))
            self.assert_exactly_commutes(operation, source, destinations)

    def test_negative_source_write_and_target_read(self):
        source, destinations = 0, [2, 3, 4]
        writes_source = ["add", 0, 1, 5, 7]
        reads_target = ["add", 1, 3, -3, 5]
        for operation in (writes_source, reads_target):
            self.assertFalse(gap_commutes_with_fanout(operation, source, destinations))
            self.assert_does_not_commute(operation, source, destinations)

    def test_scale_positive_and_negative_controls(self):
        source, destinations = 0, [2, 3, 4]
        unrelated_scale = ["scale", 5, -2, 1, []]
        unit_scale = ["scale", 2, 1, 1, []]
        source_scale = ["scale", 0, -1, 1, []]
        destination_scale = ["scale", 3, -1, 1, []]
        for operation in (unrelated_scale, unit_scale):
            self.assertTrue(gap_commutes_with_fanout(operation, source, destinations))
            self.assert_exactly_commutes(operation, source, destinations)
        for operation in (source_scale, destination_scale):
            self.assertFalse(gap_commutes_with_fanout(operation, source, destinations))
            self.assert_does_not_commute(operation, source, destinations)

    def test_exact_fanout_inverse_positive_and_negative(self):
        coefficients = [Q(2, 3), Q(-5, 4), Q(7, 9)]
        verify_fanout_map(coefficients)
        forward, wrong_inverse = identity(4), identity(4)
        for row, coefficient in enumerate(coefficients, start=1):
            forward[row][0] += coefficient
            wrong_inverse[row][0] += coefficient
        self.assertNotEqual(matmul(forward, wrong_inverse), identity(4))


if __name__ == "__main__":
    unittest.main()
