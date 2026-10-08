"""Full rank accounting, exact assembly."""
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import ternary_reuse_network as tr
from prime_field_network import witness as previous_witness, bit_counts


class TernaryReuseWitness(unittest.TestCase):
    def test_role_change_preserves_absolute_deficit_and_loss(self):
        old, new = previous_witness(), tr.witness()
        for key in ('D', 'L', 'N', 'm'):
            self.assertEqual(old['bit'][key], new['bit'][key])
        width_drop = old['bit']['W']-new['bit']['W']
        self.assertEqual(width_drop, 2*98280**2*65772)
        self.assertEqual(old['bit']['s']-new['bit']['s'], width_drop*21952)
        self.assertEqual(new['bit']['eta'], Q(39, 517154624))
        self.assertEqual(old['complex'], new['complex'])
        self.assertEqual(old['guard'], new['guard'])

    def test_complete_assembly_and_old_width_negative_control(self):
        new = tr.witness()
        self.assertEqual(new['parameters']['kappa'], Q(3769, 10**12))
        self.assertEqual(new['minimum_margin'], Q(37697459, 10**16))
        self.assertEqual(new['absorption_gap'], Q(7459, 10**16))
        self.assertTrue(all(x > 0 for x in new['constraints'].values()))
        self.assertTrue(all(x > 0 for x in new['deficit_slacks'].values()))
        with self.assertRaises(ValueError):
            previous_witness(p=tr.parameters(), bn=bit_counts())
        with self.assertRaises(ValueError):
            previous_witness(p=replace(tr.parameters(), kappa=new['minimum_margin']),
                             bn=bit_counts(tr.ROLES))


if __name__ == '__main__':
    unittest.main()
