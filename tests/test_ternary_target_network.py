"""Exact direct-producer rank arithmetic and complete assembly controls."""
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import ternary_target_network as target
from prime_field_network import bit_counts, witness as original_witness


class DirectWitness(unittest.TestCase):
    def test_only_width_and_absolute_rank_sum_change(self):
        old, new = original_witness(), target.witness()
        for name in ('D', 'L', 'N', 'm'):
            self.assertEqual(old['bit'][name], new['bit'][name])
        removed = 11840940-10365877
        self.assertEqual(removed, 1475063)
        delta = 2*98280**2*removed
        self.assertEqual(old['bit']['W']-new['bit']['W'], delta)
        self.assertEqual(old['bit']['s']-new['bit']['s'], delta*21952)
        self.assertEqual(new['bit']['eta'], Q(351, 4101949544))
        self.assertEqual(old['complex'], new['complex'])
        self.assertEqual(old['guard'], new['guard'])

    def test_assembly_and_predecessor_width_negative_control(self):
        new = target.witness()
        self.assertEqual(new['minimum_margin'], Q(42776443, 10**16))
        self.assertEqual(new['absorption_gap'], Q(6443, 10**16))
        self.assertTrue(all(x > 0 for x in new['constraints'].values()))
        self.assertTrue(all(x > 0 for x in new['deficit_slacks'].values()))
        with self.assertRaises(ValueError):
            original_witness(p=target.parameters(), bn=bit_counts())
        with self.assertRaises(ValueError):
            original_witness(p=replace(target.parameters(), kappa=new['minimum_margin']),
                             bn=bit_counts(target.ROLES))


if __name__ == '__main__':
    unittest.main()
