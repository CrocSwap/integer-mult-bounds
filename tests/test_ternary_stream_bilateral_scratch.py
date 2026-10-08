"""Positive strict dual-frame continuation with the actual frame-cut rule."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/experiments'))
from ternary_stream_bilateral_scratch import strict_dual_control


class BilateralStream(unittest.TestCase):
    def test_strict_dual_frame_growth_and_every_dirty_basis(self):
        result = strict_dual_control()
        self.assertEqual(result['source_nodes'], [1, 2, 3])
        self.assertEqual(result['dual_nodes'], [9, 10])
        self.assertEqual(result['dual_frame_dimensions'], [24, 27])
        self.assertEqual(result['new_roles'], 6)
        self.assertEqual(result['matched_links'], 1)
        self.assertTrue(result['coefficients']['every_dirty_basis_restored_by_inverse'])
        for frame in result['frames']:
            self.assertEqual((frame['total_rank'], frame['loss']), (600, 0))
        wrapper = result['dirty_wrapper']
        self.assertEqual(wrapper['all_basis_symbols'], 22)
        self.assertFalse(wrapper['intended_map_is_identity'])
        self.assertTrue(wrapper['dirty_wrapper_restores_every_scratch'])
        self.assertTrue(wrapper['forward_inverse_exact'])


if __name__ == '__main__':
    unittest.main()
