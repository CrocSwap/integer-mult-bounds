#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fault controls for the independent PR3133 local audit, including dual-only faults."""
import copy
from fractions import Fraction as Q
from pathlib import Path
import runpy
import unittest

# Execute authenticated source text rather than importing a cached local module.
A = runpy.run_path(str(Path(__file__).with_name('verify.py')))


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        A['authenticate']()
        cls.parent = A['load']('PARENT-base.json.gz')
        cls.spec = A['load']('EDITS.json')['edits']['base']
        cls.baseline = A['edit'](cls.parent, cls.spec, {'R1_E42', 'R2_E7'})
        cls.word = A['load']('FINAL-base.json.gz')

    def test_full_dirty_and_dual_positive(self):
        self.assertEqual(A['endpoint'](self.word)['independent_inputs'], 632)
        self.assertEqual(A['endpoint'](self.word, True)['zero_buffers'], 91)

    def test_edit_preimage(self):
        parent = copy.deepcopy(self.parent)
        parent['B'][52][3] *= -1
        with self.assertRaisesRegex(ValueError, 'preimage'):
            A['edit'](parent, self.spec, {'B_586_438'})

    def test_coefficient_in_each_fold(self):
        for source_start in (784, 789):
            # The two removed earlier B instructions shift these source positions.
            i = source_start - 2
            mutant = copy.deepcopy(self.word)
            mutant['B'][i][3] *= -1
            mutant['cleanup'] = A['cleanup'](mutant)
            with self.subTest(source_start=source_start):
                with self.assertRaisesRegex(ValueError, 'target|endpoint|dirty'):
                    A['endpoint'](mutant)

    def test_unshifted_warp_positions(self):
        mutant = copy.deepcopy(self.word)
        mutant['warps'] = copy.deepcopy(self.parent['warps'])
        with self.assertRaisesRegex(ValueError, 'warp entry frame|nonmonotone frame'):
            A['frame_bill'](mutant)
        mutant['cleanup'] = A['cleanup'](mutant)
        with self.assertRaisesRegex(ValueError, 'target|dirty|endpoint'):
            A['endpoint'](mutant)

    def test_lower_only_without_changing_program(self):
        for r in ('586', '588'):
            mutant = copy.deepcopy(self.baseline)
            mutant['helper_final'][r] = self.word['helper_final'][r]
            with self.subTest(helper=r):
                with self.assertRaisesRegex(ValueError, 'nonmonotone frame'):
                    A['frame_bill'](mutant)

    def test_fold_only_is_not_inventory_saving(self):
        mutant = copy.deepcopy(self.word)
        for r in ('586', '588'):
            mutant['helper_final'][r] = self.parent['helper_final'][r]
        candidate, inventory, _ = A['frame_bill'](self.word)
        old_ends, old_inventory, _ = A['frame_bill'](mutant)
        self.assertEqual(A['signed_delta'](old_ends, candidate), {'1': 2})
        self.assertEqual(A['signed_delta'](old_inventory, inventory), {'6': -2, '7': 2})

    def test_stale_cleanup(self):
        mutant = copy.deepcopy(self.word)
        mutant['cleanup'] = copy.deepcopy(self.parent['cleanup'])
        with self.assertRaisesRegex(ValueError, 'cleanup not inverse-reverse'):
            A['frame_bill'](mutant)
        with self.assertRaisesRegex(ValueError, 'endpoint|buffer'):
            A['endpoint'](mutant)

    def test_wrong_restore_coefficient(self):
        mutant = copy.deepcopy(self.word)
        mutant['restore'][85][3] *= -1
        mutant['cleanup'] = A['cleanup'](mutant)
        with self.assertRaisesRegex(ValueError, 'dirty helper not restored'):
            A['endpoint'](mutant)

    def test_unrelated_dirty_column_is_checked(self):
        mutant = copy.deepcopy(self.word)
        mutant['B'].append(['add', 140, 224, 1, 1, list(A['FULL'] - {0})])
        mutant['cleanup'] = A['cleanup'](mutant)
        with self.assertRaisesRegex(ValueError, 'target before cleanup'):
            A['endpoint'](mutant)

    def test_restored_helper_column_is_independent(self):
        mutant = copy.deepcopy(self.word)
        mutant['B'].append(['add', 140, 586, 1, 1, list(A['FULL'] - {0})])
        mutant['cleanup'] = A['cleanup'](mutant)
        with self.assertRaisesRegex(ValueError, 'target before cleanup'):
            A['endpoint'](mutant)

    def test_dual_private_buffer_input_is_checked(self):
        # Invisible in the forward map on the promised zero buffer, but the
        # contragredient circuit must also return that buffer to zero.
        mutant = copy.deepcopy(self.word)
        mutant['cleanup'].append(['add', 1, 704 + 586, 1, 1, list(A['FULL'] - {0})])
        A['endpoint'](mutant)
        with self.assertRaisesRegex(ValueError, 'buffer not zero'):
            A['endpoint'](mutant, True)

    def test_binary_span_and_free_word_oracles(self):
        self.assertEqual(A['space']((3, 5)), frozenset((0, 3, 5, 6)))
        row = {(7, (3, -4)): Q(5, 2)}
        self.assertEqual(A['multiply'](row, (9, -3)), {(7, (9, -4)): Q(5, 2)})
        self.assertNotEqual(A['multiply'](row, (9,)), A['multiply'](row, (-9,)))

    def test_singular_and_wrong_warp_map(self):
        record = self.word['warps'][0]
        columns = list(record[2])
        columns[0] = columns[1]
        with self.assertRaisesRegex(ValueError, 'singular warp'):
            A['warp_geometry'](tuple(columns), tuple(record[3]), tuple(record[4]))
        with self.assertRaisesRegex(ValueError, 'warp does not map source frame'):
            A['warp_geometry'](tuple(1 << bit for bit in range(9)), tuple(record[3]), tuple(record[4]))


if __name__ == '__main__':
    unittest.main()
