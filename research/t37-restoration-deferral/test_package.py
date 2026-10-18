# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the T37 restoration-deferral note.

Run: python3 -B -m unittest discover -s research/t37-restoration-deferral -p test_package.py -v
"""
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from common import (Span, concentrated, coverage_census, hyperplane, load_construction, rank_mass,
                    restoration_census, window_deferral)

FULL3 = [0b100, 0b010, 0b001]


def toy_word():
    """h=3, one source (port 001), one target, two helpers; helper 3 is a low end."""
    return dict(report=dict(h=3, v=1, R=2), ports=[0b001], start_extra={},
                A=[['add', 0, 2, 1, 1, [0b001, 0b010]]], centers=[], center_frames=[], cut=[],
                B=[['add', 3, 1, 1, 1, [0b010]]], early_cleanup=[],
                cleanup=[['add', 0, 2, -1, 1, FULL3]], helper_final={'3': [0b010]}, target_levels={})


def toy_template():
    """Two calls; helper 0 is hosted twice in one window, helper 1 in two windows,
    helper 2 in a window that already has an idle remainder of rank 3."""
    slots = [dict(helper=0, family=2, child=0, width=2), dict(helper=0, family=2, child=0, width=2),
             dict(helper=1, family=3, child=1, width=1), dict(helper=1, family=4, child=2, width=1),
             dict(helper=2, family=5, child=3, width=2), dict(helper=2, family=5, child=3, width=2)]
    return dict(calls=[{}, {}], hosting=dict(pooled_slots=slots),
                idle_children=[dict(family=5, child=3, rank=3, replicas=1)])


class SpanTests(unittest.TestCase):
    def test_rank_and_containment(self):
        U = Span([0b011, 0b001, 0b011])
        self.assertEqual(U.rank, 2)
        self.assertTrue(Span([0b010]).within(U))
        self.assertFalse(Span([0b100]).within(U))
        self.assertTrue(Span([0b001, 0b010]).same(U))

    def test_hyperplane_is_orthogonal_complement(self):
        for p in range(1, 1 << 5):
            U = hyperplane(p, 5)
            self.assertEqual(U.rank, 4)
            self.assertTrue(all(bin(b & p).count('1') % 2 == 0 for b in U.basis))


class RestorationTests(unittest.TestCase):
    def test_toy_word(self):
        r = restoration_census(toy_word())
        self.assertEqual(r['paid'], Counter({1: 6, 2: 1}))
        regs = r['registers']
        self.assertEqual([x['restoration'] for x in regs], [1, 1, 1, 0])
        self.assertEqual([x['full_cleanup_gates'] for x in regs], [1, 0, 1, 0])
        self.assertTrue(regs[3]['low_end'])
        self.assertEqual(r['widths'], Counter({3: 1, 1: 1}))

    def test_non_monotone_frame_rejected(self):
        w = toy_word()
        w['B'].append(['add', 2, 3, 1, 1, [0b100]])   # helper 2 sits at rank 2 and cannot drop to <100>
        with self.assertRaisesRegex(ValueError, 'non-monotone'):
            restoration_census(w)

    def test_target_levels_rejected(self):
        w = toy_word()
        w['target_levels'] = {'1': 1}
        with self.assertRaisesRegex(ValueError, 'target levels'):
            restoration_census(w)

    def test_full_cleanup_on_low_end_rejected(self):
        w = toy_word()
        w['cleanup'].append(['add', 3, 0, 1, 1, FULL3])
        with self.assertRaisesRegex(ValueError, 'low end'):
            restoration_census(w)


class DeferralTests(unittest.TestCase):
    local = Counter({1: 2, 2: 1, 4: 1})
    restoration = {0: 1, 1: 1, 2: 2}

    def run_case(self, chosen):
        H, removed, _ = window_deferral(toy_template(), self.local, self.restoration, chosen)
        base, _, _ = window_deferral(toy_template(), self.local, self.restoration, set())
        self.assertEqual(rank_mass(H), rank_mass(base))
        return H, base

    def test_isolated_deferral_is_shape_neutral(self):
        H, base = self.run_case({1})
        self.assertEqual(H, base)

    def test_same_window_deferrals_merge(self):
        H, base = self.run_case({0})
        self.assertEqual(base - H, Counter({1: 2}))
        self.assertEqual(H - base, Counter({2: 1}))

    def test_existing_remainder_absorbs(self):
        H, base = self.run_case({2})
        self.assertEqual(base - H, Counter({2: 2, 3: 1}))
        self.assertEqual(H - base, Counter({7: 1}))

    def test_concentration_preserves_mass(self):
        H = Counter({1: 5, 48: 2})
        out = concentrated(H, Counter({1: 3}), Counter({48: 2}), 48)
        self.assertEqual(rank_mass(out), rank_mass(H))
        self.assertEqual(out, Counter({1: 2, 48: 2, 3: 1}))


class CoverageTests(unittest.TestCase):
    def template(self):
        prov = dict(v=1, R=2, widths=[2, 1])
        call = dict(provider_id='p', owners=[[0, [1, 0, 0]], [1, [1, 1, 0]], [2, [3, 0, 0]], [3, [4, 0, 0]]])
        return dict(live=4, m=5, local_providers={'p': prov}, calls=[call],
                    hosting=dict(pooled_slots=[dict(helper=0, family=2, width=2), dict(helper=1, family=3, width=1)]),
                    idle_children=[dict(family=0, rank=2, replicas=1), dict(family=1, rank=2, replicas=1),
                                   dict(family=2, rank=2, replicas=1), dict(family=3, rank=3, replicas=1)],
                    private_namespace=dict(centers=[4, 5]))

    def test_identity_and_failure(self):
        cov = coverage_census(self.template(), local_mass=7, data_step=2)
        self.assertEqual(cov['coverage_values'], {'5': 4})
        t = self.template()
        t['idle_children'][3]['rank'] = 2
        self.assertEqual(coverage_census(t, 7, 2)['coverage_values'], {'4': 1, '5': 3})


class SelectedDataTests(unittest.TestCase):
    def test_t37_census_claims(self):
        template, word = load_construction('T37')
        local = restoration_census(word)
        pos = [r for r in local['registers'] if r['restoration'] > 0]
        self.assertEqual(sum(r['restoration'] for r in pos if r['role'] == 'helper'), 636)
        self.assertEqual(sum(r['restoration'] for r in pos if r['role'] == 'source'), 230)
        self.assertTrue(all(r['full_cleanup_gates'] > 0 for r in pos))
        cov = coverage_census(template, rank_mass(local['paid']), 8)
        self.assertEqual(cov['coverage_values'], {'73': 33152})
        self.assertEqual(cov['deficit'], 33152 - 64 * 333)

    def test_committed_baseline_is_selected(self):
        prices = json.loads((HERE / 'PRICES.json').read_text())
        selected = json.loads((HERE.parents[1] / 'certificates/selected-result.json').read_text())
        self.assertEqual(prices['scenarios']['baseline']['kappa'], selected['kappa'])


if __name__ == '__main__':
    unittest.main()
