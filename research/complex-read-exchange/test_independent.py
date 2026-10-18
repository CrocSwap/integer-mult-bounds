#!/usr/bin/env python3
"""Focused positive and failure-path checks; no broad search is repeated."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('read_exchange_independent', HERE / 'independent_check.py')
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original, cls.sha = CHECK.read(HERE / 'inputs/P6K4-WORD.json.gz')
        cls.recipe, _ = CHECK.read(HERE / 'inputs/SW4-RECIPE.json')
        cls.baseline, cls.profile, cls.widths = CHECK.rewrite(cls.original, cls.recipe['moves'])

    def test_known_positive_exact_bytes_and_scalar_map(self):
        self.assertEqual(self.sha, self.recipe['input_sha256'])
        self.assertEqual(hashlib.sha256(CHECK.encoded(self.baseline)).hexdigest(), self.recipe['output_sha256'])
        self.assertEqual(CHECK.scalar_compare(self.original, self.baseline), 728)
        self.assertEqual(CHECK.recount(self.baseline)[0], self.recipe['profile_out'])
        self.assertEqual(sum(self.widths), 3778)
        self.assertEqual(CHECK.boundary_check(self.original, self.baseline)['helper_count'], 504)

    def test_exact_scalar_corruption_can_leave_frames_legal(self):
        mutant = deepcopy(self.baseline)
        gate = next(g for g in mutant['B'] if g[0] == 'add')
        gate[3] += gate[4]
        self.assertEqual(CHECK.recount(mutant)[0], self.profile)
        with self.assertRaisesRegex(ValueError, 'Exact B map changed'):
            CHECK.scalar_compare(self.original, mutant)

    def test_kept_compensation_preread_is_rejected_exactly(self):
        mutant = deepcopy(self.baseline)
        move = next(m for m in self.recipe['moves'] if m['kind'] == 'h2r')
        preread = deepcopy(self.original['B'][move['delete_preread_index']])
        mutant['B'].insert(0, preread)
        with self.assertRaisesRegex(ValueError, 'Exact B map changed'):
            CHECK.scalar_compare(self.original, mutant)

    def test_frame_corruption_preserves_scalars_but_fails_caps(self):
        mutant = deepcopy(self.baseline)
        gate = next(g for g in mutant['B'] if g[0] == 'add' and 112 <= g[1] < 224)
        gate[-1] = CHECK.frame(CHECK.FULL)
        self.assertEqual(CHECK.scalar_compare(self.original, mutant), 728)
        with self.assertRaisesRegex(ValueError, 'Target hyperplane violation'):
            CHECK.recount(mutant)

    def test_fixed_boundary_change_rejected(self):
        mutant = deepcopy(self.baseline)
        helper = next(iter(mutant['start_extra']))
        mutant['start_extra'][helper] = []
        with self.assertRaisesRegex(ValueError, 'Changed fixed boundary'):
            CHECK.boundary_check(self.original, mutant)

    def test_wrong_recipe_coefficient_and_duplicate_edit_rejected(self):
        move = deepcopy(self.recipe['moves'][0])
        move['coef'][0] *= -1
        with self.assertRaisesRegex(ValueError, 'Read/recipe mismatch'):
            CHECK.rewrite(self.original, [move])
        with self.assertRaisesRegex(ValueError, 'Duplicate read edit'):
            CHECK.rewrite(self.original, [self.recipe['moves'][0]] * 2)

    def test_partial_refusal_has_explicit_nonorthogonal_vector(self):
        probe = CHECK.RefusalProbe(self.original)
        self.assertEqual(probe.run([]), (None, None))
        self.assertEqual(probe.run(self.recipe['moves']), (None, None))
        move = next(m for m in self.recipe['moves'] if m['kind'] == 'h2r')
        failure, vector = probe.run([move])
        self.assertEqual(failure[0], 'cap')
        port = self.original['ports'][failure[2] - 112]
        self.assertEqual(bin(vector & port).count('1') % 2, 1)
        with self.assertRaisesRegex(ValueError, 'Target hyperplane violation'):
            CHECK.rewrite(self.original, [move])

    def test_eligible_pair_domain_reconstructed(self):
        pairs = CHECK.enumerate_pairs(self.original)
        self.assertEqual(len(pairs), 54)
        self.assertEqual(sum((1 << len(p['moves'])) - 1 for p in pairs), 602)

    def test_completed_domain_group_counts(self):
        pairs = CHECK.enumerate_pairs(self.original)
        groups = CHECK.finite_groups(pairs, 2, 'all')
        self.assertEqual((len(groups), sum(n for _, n in groups)), (1431, 175456))
        triples = CHECK.finite_groups(pairs, 3, 'shared-targets')
        self.assertEqual((len(triples), sum(n for _, n in triples)), (16, 27344))

    def test_incomplete_report_and_candidate_list_rejected_before_replay(self):
        pairs = CHECK.enumerate_pairs(self.original)
        declaration = {'input_sha256': self.sha, 'pairs': pairs}
        search = {'status': 'TIME_LIMIT'}
        with self.assertRaisesRegex(ValueError, 'completed domain'):
            CHECK.replay_refusals(self.original, self.recipe, search, declaration)
        search = {'status': 'COMPLETE_FINITE_DOMAIN', 'at_least_one_partial': True,
                  'unchanged_other_sw4_pairs': True, 'arity': 2, 'domain': 'all',
                  'pairs_tested': [], 'counts': {'coupled_total': 175456}}
        with self.assertRaisesRegex(ValueError, 'eligible-pair enumeration differs'):
            CHECK.replay_refusals(self.original, self.recipe, search,
                                 {'input_sha256': self.sha, 'pairs': pairs[:-1]})
        with self.assertRaisesRegex(ValueError, 'group/mask declaration'):
            CHECK.replay_refusals(self.original, self.recipe, search, declaration)
        search['pairs_tested'] = [[*[p['h'] for p in g], n]
                                  for g, n in CHECK.finite_groups(pairs, 2, 'all')]
        search['pairs_tested'][0][-1] -= 1
        with self.assertRaisesRegex(ValueError, 'group/mask declaration'):
            CHECK.replay_refusals(self.original, self.recipe, search, declaration)

    def test_dyadic_normalization_and_nondyadic_rejection(self):
        self.assertEqual(CHECK.coefficient(['scale', 235, 1, -1, []]), Fraction(-1))
        self.assertEqual(CHECK.coefficient(['add', 1, 2, 2, 4, []]), Fraction(1, 2))
        with self.assertRaisesRegex(ValueError, 'not dyadic'):
            CHECK.coefficient(['add', 1, 2, 1, 3, []])

    def test_exact_pricing_has_both_signs_and_mass_guard(self):
        cheaper = dict(self.profile)
        cheaper['1'] -= 2
        cheaper['2'] += 1
        self.assertEqual(CHECK.price(cheaper, self.profile)['relation'], 'strictly_cheaper')
        self.assertEqual(CHECK.price(self.profile, cheaper)['relation'], 'strictly_more_expensive')
        self.assertEqual(CHECK.price(self.profile, self.profile)['relation'], 'identical_profile')
        expensive_mass = dict(self.profile)
        expensive_mass['1'] += 1
        with self.assertRaisesRegex(ValueError, 'Changed local rank mass'):
            CHECK.price(expensive_mass, self.profile)

    def test_external_corrupted_recipe_rejected_with_optimization(self):
        with tempfile.TemporaryDirectory(prefix='read-exchange-test-') as tmp:
            recipe = deepcopy(self.recipe)
            recipe['moves'][0]['coef'][0] *= -1
            path = Path(tmp) / 'bad-recipe.json'
            path.write_text(json.dumps(recipe))
            run = subprocess.run([sys.executable, '-B', '-I', '-O', str(HERE / 'independent_check.py'),
                                  str(HERE / 'inputs/P6K4-WORD.json.gz'), '--baseline-recipe',
                                  str(HERE / 'inputs/SW4-RECIPE.json'), '--recipe', str(path)],
                                 capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('Read/recipe mismatch', run.stderr)


if __name__ == '__main__':
    unittest.main()
