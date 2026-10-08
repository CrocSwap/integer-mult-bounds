"""Exact fused-producer accounting, strict assembly."""
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import ternary_fused_network as fused
from ternary_target_network import witness as direct_witness
from prime_field_network import bit_counts, witness as general_witness


class FusedWitness(unittest.TestCase):
    def test_role_saving_preserves_absolute_deficit_and_all_other_interfaces(self):
        old, new = direct_witness(), fused.witness()
        for name in ('D', 'L', 'N', 'm'):
            self.assertEqual(old['bit'][name], new['bit'][name])
        removed = old['bit']['roles']-new['bit']['roles']
        self.assertEqual(removed, 9205)
        delta = 2*98280**2*removed
        self.assertEqual(old['bit']['W']-new['bit']['W'], delta)
        self.assertEqual(old['bit']['s']-new['bit']['s'], delta*21952)
        self.assertEqual(new['bit']['W'], 201967892883993600)
        self.assertEqual(new['bit']['s'], 4433598804876454886400)
        self.assertEqual(new['bit']['eta'], Q(117, 1366113728))
        self.assertEqual(old['complex'], new['complex'])
        self.assertEqual(old['guard'], new['guard'])

    def test_strict_assembly_and_negative_controls(self):
        new = fused.witness()
        self.assertEqual(new['parameters']['kappa'], Q(4281, 10**12))
        self.assertEqual(new['minimum_margin'], Q(8563287, 2*10**15))
        self.assertEqual(new['absorption_gap'], Q(1287, 2*10**15))
        self.assertTrue(all(x > 0 for x in new['constraints'].values()))
        self.assertTrue(all(x > 0 for x in new['deficit_slacks'].values()))
        with self.assertRaises(ValueError):
            general_witness(p=fused.parameters(), bn=bit_counts(10365877))
        with self.assertRaises(ValueError):
            general_witness(p=replace(fused.parameters(), kappa=new['minimum_margin']),
                            bn=bit_counts(fused.ROLES))


if __name__ == '__main__':
    unittest.main()
