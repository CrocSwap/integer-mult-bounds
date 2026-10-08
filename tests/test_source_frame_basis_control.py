"""Common-basis and physical endpoint controls for source-frame batching."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from experiments.source_frame_basis_control import (
    common_coordinate_control, five_subset_control, identity, shifted_exit)


class SourceFrameBasis(unittest.TestCase):
    def test_same_basis_covers_all_old_and_new_projectors(self):
        result=common_coordinate_control()
        self.assertEqual(result['old_projectors_checked'],57)
        self.assertEqual(result['new_projectors_checked'],9)
        self.assertEqual(result['total_projectors_checked'],66)
        self.assertTrue(result['one_common_integer_parameter_tuple'])
        self.assertTrue(result['rational_corner_nonsingularity_certified'])
        self.assertEqual(result['new_profile'],dict(
            nullity=3,rank=24,middle_width=21,corner_width=0,singleton_corner_pivots=3))

    def test_actual_five_subset_preserves_total_rank(self):
        result=five_subset_control()
        self.assertEqual(result['exact_line_norm'],'3')
        self.assertEqual(result['ranks'],dict(source=20,final=25,internal=5,old_exit=100,new_exit=120))
        self.assertEqual(result['old_total_rank'],result['new_total_rank'])
        self.assertEqual(result['pivot_profile']['middle_width'],115)
        self.assertEqual(result['pivot_profile']['singleton_corner_pivots'],5)

    def test_changing_source_without_sink_is_rejected(self):
        source=[[1,0],[0,0]]
        with self.assertRaisesRegex(ValueError,'endpoint difference'):
            shifted_exit(source,identity(2),sink=identity(2))
        self.assertEqual(shifted_exit(source,identity(2)),source)


if __name__=='__main__': unittest.main()
