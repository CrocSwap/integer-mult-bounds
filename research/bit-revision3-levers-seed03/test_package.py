# SPDX-License-Identifier: Apache-2.0
"""Controls for the bit-side lever budgets (< 2 s; one instance of each relaxation step, fractional counts hold by superset).

Run: python3 -I -B -m unittest discover -s research/bit-revision3-levers-seed03 -p test_package.py -v
"""
import copy
import json
import math
import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import levers as L  # noqa: E402
import verify as V  # noqa: E402

BINDING, ASM, EXP, WORD = V.bind()
PROFILE = {int(r): n for r, n in EXP['nine']['profile'].items()}
W = EXP['nine']['bit']['live']
C0 = V.frac(EXP['nine']['bit_lower'])
M, w = 64, Q(296, 3)


class Engine(unittest.TestCase):
    def test_intervals_contain_floats(self):
        for k in (2, 7, 45, 64, 73):
            lo, hi = L.ln(k)
            self.assertTrue(lo <= Q(math.log(k)) + Q(1, 10 ** 12) and Q(math.log(k)) - Q(1, 10 ** 12) <= hi and hi - lo < Q(1, 10 ** 50))
        lo, hi = L.child(7, 64, Q(1, 99))
        self.assertTrue(lo < hi and abs(float(lo) - (7 / 64) ** (1 - 1 / 99)) < 1e-12)

    def test_selected_endpoint_and_its_neighbours(self):
        self.assertEqual(L.verdict(PROFILE, M, W, C0, surcharge=True), 'pass')
        self.assertEqual(L.verdict(PROFILE, M, W, C0 + Q(1, 10 ** 24), surcharge=True), 'fail')
        # omitting the inherited surcharge would also accept the next grid point
        self.assertEqual(L.verdict(PROFILE, M, W, C0 + Q(1, 10 ** 24), surcharge=False), 'pass')


class Relaxation(unittest.TestCase):
    """The relaxation is favorable: each step it takes can only lower the bill."""

    def bill_hi(self, H):
        return L.bill(H, M, w, Q(1, 99))[1]

    def bill_lo(self, H):
        return L.bill(H, M, w, Q(1, 99))[0]

    def test_merging_climbs_lowers_the_bill(self):
        # one rank-7 climb is cheaper than a 3 + 4 split of the same register (concavity of r^(1-a))
        self.assertLess(self.bill_hi({7: 1}), self.bill_lo({3: 1, 4: 1}))

    def test_idle_mass_at_the_largest_rank_is_cheapest(self):
        self.assertLess(self.bill_hi({45: 1}), self.bill_lo({42: Q(45, 42)}))
        self.assertLess(self.bill_hi({63: 1}), self.bill_lo({45: Q(63, 45)}))

    def test_surcharge_only_raises_the_bill(self):
        H = L.relaxed(dict(EXPECTED_LOCAL), M, w, 63, 45)
        self.assertLess(L.bill(H, M, w, Q(1, 99))[1], L.bill(H, M, w, Q(1, 99), surcharge=True)[0])

    def test_coverage_law_and_rank_guards(self):
        with self.assertRaises(L.Reject):
            L.relaxed({7: 10 ** 6}, M, w, 63, 45)            # more local mass than the coverage law allows
        with self.assertRaises(L.Reject):
            L.relaxed(dict(EXPECTED_LOCAL), M, w, 63, 64)    # an idle child of rank m makes the bill vacuous
        self.assertEqual(max(r for r in range(1, M) if M * M > 2 * r * r), 45)
        self.assertFalse(M * M > 2 * 46 * 46)

    def test_halving_depth_caps_follow_the_row_bounds(self):
        result = json.loads((HERE / 'RESULT.json').read_text())
        rows = {d['halving_depth']: d for d in result['replay']['halving_depths']}
        self.assertEqual({k: r['idle_cap'] for k, r in rows.items()}, {2: 45, 3: 50, 4: 53, 5: 55})
        self.assertEqual([k for k, r in rows.items() if r['pr510_admissible']], [2])
        self.assertEqual([k for k, r in rows.items() if r['elementary_cover_admissible']], [2, 3, 4])

    def test_o2_flips_at_halving_depth_four(self):
        base = {7: Q(222) + Q(63, 14)}
        for R, k in ((50, 131), (53, 145)):
            loc = dict(base)
            loc[8] = k
            self.assertEqual(L.verdict(L.relaxed(loc, M, w, Q(63, 2), R), M, w, Q(1, 99)), 'pass')
            loc[8] = k + 1
            self.assertEqual(L.verdict(L.relaxed(loc, M, w, Q(63, 2), R), M, w, Q(1, 99)), 'fail')

    def test_centre_free_fits_in_window_with_fewer_helpers(self):
        # the joint surface, not the window, is what the centre-free lever must meet
        self.assertEqual(L.verdict(L.relaxed({7: 222, 8: 332}, M, w, 0, 45), M, w, Q(1, 99)), 'pass')
        self.assertEqual(L.verdict(L.relaxed({7: 222, 8: 333}, M, w, 0, 45), M, w, Q(1, 99)), 'fail')

    def test_o2_boundary_is_certified(self):
        base = {7: Q(222) + Q(63, 14)}
        k, _, nxt = L.max_count(base, 8, M, w, Q(63, 2), 45, Q(1, 99), 600)
        self.assertEqual((k, nxt), (104, 'fail'))
        loc = dict(base)
        loc[8] = 104
        self.assertEqual(L.verdict(L.relaxed(loc, M, w, Q(63, 2), 45), M, w, Q(1, 99)), 'pass')
        loc[8] = 105
        self.assertEqual(L.verdict(L.relaxed(loc, M, w, Q(63, 2), 45), M, w, Q(1, 99)), 'fail')

    def test_o1_has_no_room_at_any_admissible_cap(self):
        base = {7: Q(222) + 9}
        for R in (42, 45, 50, 53, 63):
            self.assertEqual(L.verdict(L.relaxed(base, M, w, 63, R), M, w, Q(1, 99)), 'fail')


class Replay(unittest.TestCase):
    def test_replay_matches_the_record(self):
        local, split, copies = V.replay(WORD, EXP)
        self.assertEqual(sum(r * c for r, c in local.items()), 5129)
        self.assertEqual(sum(r * c for r, c in (split['sources']).items()), 777)
        self.assertEqual(dict(copies), {7: 9})

    def test_tampered_gate_is_rejected(self):
        word = copy.deepcopy(WORD)
        gate = next(g for g in word['A'] if g[0] != word['start'][g[1]])
        gate[0] = 0                                       # a gate moved to the empty frame
        with self.assertRaises(L.Reject):
            V.replay(word, EXP)

    def test_tampered_record_histogram_is_rejected(self):
        exp = copy.deepcopy(EXP)
        exp['word']['local_histogram']['2'] += 1
        with self.assertRaises(L.Reject):
            V.replay(WORD, exp)

    def test_receipt_is_reproduced(self):
        result = json.loads((HERE / 'RESULT.json').read_text())
        self.assertEqual(result['status'], 'PASS_BIT_REVISION3_LEVERS')
        self.assertEqual(result['levers'][0]['root'], '0.001955918756')
        self.assertEqual(result['O2']['by_cap']['45']['max_width8_helpers'], 104)
        self.assertEqual(result['O2']['by_cap']['53']['max_width8_helpers'], 145)


EXPECTED_LOCAL = {int(r): n for r, n in EXP['word']['local_histogram'].items()}

if __name__ == '__main__':
    unittest.main()
