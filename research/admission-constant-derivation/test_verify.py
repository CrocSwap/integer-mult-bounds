#!/usr/bin/env python3
"""Rejecting controls for verify.py."""
import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v  # noqa: E402

S = v.bind_sources()


class Controls(unittest.TestCase):
    def test_atom_at_or_below_left_endpoint_fails(self):
        lo, _ = v.atom_interval(S['C1'], S['old'])
        for d in (lo, lo-Q(1, 10**9), Q('.0034')):
            self.assertFalse(v.admissible(S['C1'], S['old'], d))

    def test_atom_at_or_above_right_endpoint_fails(self):
        _, hi = v.atom_interval(S['C1'], S['old'])
        self.assertFalse(v.admissible(S['C1'], S['old'], hi))
        self.assertFalse(v.admissible(S['C1'], S['old'], Q(1)))

    def test_admitted_above_sup_impossible(self):
        lo, hi = v.atom_interval(S['C1'], S['old'])
        target = lo+Q(1, 10**9)
        for d in (lo+Q(1, 10**12), Q('.004'), (lo+hi)/2):
            self.assertLess(v.ordinary(S['C1'], S['old'], d), target)

    def test_dropping_lost_helper_term_fails(self):
        helpers, children, ports, block = S['sides']['complex']
        lit = v.literal_surplus(helpers, children, [block]*ports, 17, 5)[0]
        H = sum(r*n for r, n in helpers.items()); C = sum(r*n for r, n in children.items())
        self.assertNotEqual(lit, 19*(H-C+(2*block+1)*ports))

    def test_width_only_reading_fails(self):
        # 48 is the local balance, not a width-8 constant: change one helper count
        helpers, children, ports, block = S['sides']['bit']
        changed = dict(helpers); changed[8] += 1
        lit = v.literal_surplus(changed, children, [block]*ports, 16, 3)[0]
        self.assertNotEqual(lit, 48*18-ports)
        self.assertEqual(lit, v.closed_surplus(changed, children, [block]*ports, 16))

    def test_mixed_widths_break_uniform_formula(self):
        helpers, children, ports, block = S['sides']['complex']
        widths = [block]*(ports-1)+[7]
        lit = v.literal_surplus(helpers, children, widths, 16, 4)[0]
        self.assertNotEqual(lit, 48*18-ports)
        self.assertEqual(lit, v.closed_surplus(helpers, children, widths, 16))


if __name__ == '__main__':
    unittest.main(verbosity=2)
