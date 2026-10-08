"""Focused controls for the extra contiguous stage-two pivot block."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/experiments'))
from controlled_basis_control import PRIME, SingularMatrix, certificate, check_projector, identity


def paired_projector(m,pairs):
    """Exact half-projection on each pair; identity on untouched coordinates."""
    matrix = identity(m)
    half = pow(2,PRIME-2,PRIME)
    for i,j in pairs:
        matrix[i][i] = matrix[i][j] = matrix[j][i] = matrix[j][j] = half
    return matrix


class ControlledBasisControl(unittest.TestCase):
    def test_one_basis_handles_all_57_projectors(self):
        result = certificate()
        self.assertEqual(result['projectors_checked'],57)
        self.assertEqual(result['class_counts'],{'A1':27,'A3':27,'A2':3})
        self.assertTrue(result['one_common_integer_parameter_tuple'])
        self.assertTrue(result['rational_corner_nonsingularity_certified'])
        self.assertEqual(result['profiles']['A2'],dict(
            nullity=9,rank=18,middle_width=9,corner_width=9,singleton_corner_pivots=0))
        self.assertEqual(result['profiles']['A1']['singleton_corner_pivots'],6)
        self.assertEqual(result['profiles']['A3']['middle_width'],5)

    def test_invertible_corner_alone_does_not_allow_corner_batching(self):
        # An anti-diagonal corner is valid for the ordinary large-projector
        # lemma, but its two reversed fields cannot be one aligned chunk.
        matrix = paired_projector(6,[(0,5),(1,4)])
        profile = check_projector(matrix,2)
        self.assertEqual(profile['middle_width'],2)
        self.assertEqual(profile['singleton_corner_pivots'],2)
        with self.assertRaisesRegex(ValueError,'not diagonal'):
            check_projector(matrix,2,aligned_corner=True)
        aligned = paired_projector(6,[(0,4),(1,5)])
        self.assertEqual(check_projector(aligned,2,aligned_corner=True)['corner_width'],2)

    def test_singular_corner_is_rejected(self):
        matrix = identity(6)
        matrix[4][4] = matrix[5][5] = 0
        with self.assertRaises(SingularMatrix):
            check_projector(matrix,2,aligned_corner=True)


if __name__ == '__main__':
    unittest.main()
