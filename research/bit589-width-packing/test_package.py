# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the PR589 width-packing note.

Run: python3 -B -m unittest discover -s research/bit589-width-packing -p test_package.py -v
"""
import itertools
import json
import sys
import unittest
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import packing  # noqa: E402


class SlotModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = packing.slot_model(packing.pinned_json('bit_record'), packing.pinned_json('selection'))

    def test_capacities(self):
        self.assertEqual(self.model['caps'], {0: 14, 1: 7, 2: 28, 3: 7, 4: 42, 5: 7, 6: 42, 7: 28, 8: 14})
        self.assertEqual(self.model['slots'], Counter({7: 666, 14: 444, 28: 444, 42: 444}))
        self.assertEqual(self.model['deficit'], 28416 - 63 * 288)

    def test_width8_optimality_and_refusal(self):
        c_star = Q(1733427039589844234750, 10 ** 24)
        out = packing.width8_optimality(self.model, c_star)
        self.assertEqual(out['slack_units_per_replica'], 45)
        bad = dict(self.model)
        bad['slots'] = Counter(self.model['slots']) + Counter({40: 1})
        with self.assertRaisesRegex(ValueError, 'divisible by 8'):
            packing.width8_optimality(bad, c_star)

    def test_width7_placements(self):
        units, idle = packing.width7_idle(self.model)
        self.assertEqual((units, idle), (2043, Counter({42: 340, 21: 1})))
        idle1 = packing.width7_partial_idle(self.model, 1)
        self.assertEqual(idle1, Counter({7: 657, 6: 444, 4: 444, 42: 10, 2: 433, 34: 1}))
        mass = lambda c: sum(r * n for r, n in c.items())
        self.assertEqual(mass(idle1), mass(self.model['idle_rep']) + 9)

    def test_local_bracket(self):
        opt, pes = packing.local_bracket(Counter({1: 3, 2: 2, 7: 1}), 2)
        self.assertEqual(opt, Counter({1: 1, 2: 2, 7: 1}))
        self.assertEqual(pes, Counter({1: 4, 6: 1, 2: 1}))


class MajorizationTests(unittest.TestCase):
    def test_greedy_fill_is_optimal_for_concave_children(self):
        """Exhaustive check of the slot-exact width-7 placement rule on small instances."""
        g = lambda r: r * (64 / r) ** 0.002 if r else 0.0
        for caps in ([1, 2, 2, 4], [6, 6, 4, 2, 1], [6, 4, 4, 1, 1]):
            for units in range(1, sum(caps)):
                best = min(sum(g(7 * u) for u in us)
                           for us in itertools.product(*[range(c + 1) for c in caps]) if sum(us) == units)
                bigs = sorted(caps, reverse=True)
                greedy, left = [], units
                for c in bigs:
                    take = min(c, left)
                    greedy.append(take)
                    left -= take
                self.assertAlmostEqual(best, sum(g(7 * u) for u in greedy), places=12)


class ResultTests(unittest.TestCase):
    def test_committed_baseline(self):
        res = json.loads((HERE / 'RESULT.json').read_text())
        rec = packing.pinned_json('bit_record')
        self.assertEqual(res['scenarios']['selected']['bit_lower'], rec['nine']['bit_lower'])
        self.assertEqual(res['scenarios']['selected']['bit_bound_kappa_cap_decimal'], '0.001730427469823602')


if __name__ == '__main__':
    unittest.main()
