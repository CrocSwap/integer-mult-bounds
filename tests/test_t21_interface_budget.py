"""Model-level identities and adverse controls for the T21 interface-budget note."""
from collections import Counter
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT/'research/t21-interface-budget'
spec = importlib.util.spec_from_file_location('t21_interface_budget', PKG/'budget.py')
budget = importlib.util.module_from_spec(spec)
spec.loader.exec_module(budget)
spec = importlib.util.spec_from_file_location('t21_interface_classify', PKG/'classify.py')
classify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classify)


class T21InterfaceBudget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cls = json.loads((PKG/'RESULT-CLASSIFICATION.json').read_text())
        cls.bud = json.loads((PKG/'RESULT-BUDGET.json').read_text())
        cls.claim = json.loads((ROOT/'research/complex-t21-owners/data/CLAIM.json').read_text())

    def test_rows_partition_the_selected_local_profile(self):
        total = Counter()
        for row in self.cls['rows']:
            total.update({int(r): n for r, n in row['profile'].items()})
        self.assertEqual(dict(total), {int(r): n for r, n in self.claim['local_profile'].items()})
        self.assertEqual(sum(self.cls['mass_by_role'].values()), 5634)

    def test_base_reproduces_selected_record(self):
        base = self.bud['base']
        self.assertEqual(Q(base['kappa']), Q(self.claim['kappa']))
        self.assertEqual(Q(base['complex_b']), Q(self.claim['complex_lower']))

    def test_bit_cap_is_independent_of_complex_size(self):
        c = Q(self.claim['bit_lower'])
        thr = Q(self.bud['bit_cap']['complex_b_needed_above'])
        for b in (thr + budget.GRID, thr + Q(1, 1000), Q(1, 40)):
            self.assertEqual(budget.kappa(c, b)['kappa'], self.bud['bit_cap']['kappa'])

    def test_lower_b_is_never_better(self):
        c = Q(self.claim['bit_lower'])
        b = Q(self.claim['complex_lower'])
        self.assertLess(Q(budget.kappa(c, b - Q(1, 10**9))['kappa']), Q(self.bud['base']['kappa']))

    def test_every_relaxation_class_exceeds_headroom(self):
        units = self.bud['headroom']['delete_rank1_children']['units_per_call']
        self.assertEqual(units, 2)
        for name, row in self.bud['complex_relaxations'].items():
            self.assertGreater(row['local_mass_removed_per_call'], units, name)
            self.assertEqual(row['binding'], 'bit', name)

    def test_bit_copy_deletion_alone_misses_one_percent_target(self):
        req = self.bud['kappa_above_one_percent']
        self.assertFalse(req['bit_copy_deletion_reaches_s_star'])
        self.assertLess(Q(req['bit_with_all_nine_copies_deleted']), Q(req['min_common_saving_s_star']))

    def test_selected_t37_has_the_same_two_unit_headroom(self):
        t = self.bud['selected_t37_headroom']
        self.assertEqual([r['binding'] for r in t['rows']], ['complex', 'bit'])
        self.assertEqual(t['rows'][-1]['kappa'], self.bud['bit_cap']['kappa_decimal'])

    def test_annihilator_is_a_hyperplane(self):
        for p in (1, 6, 0b101101101, 511):
            F = classify.annihilator(p, 9)
            self.assertEqual(F.rank, 8)
            self.assertTrue(all(bin(x & p).count('1') % 2 == 0 for x in F.rows.values()))
            if bin(p).count('1') % 2:
                self.assertNotEqual(F.reduce(p), 0)

    def test_frame_containment(self):
        F, G = classify.Frame([1, 2]), classify.Frame([3])
        self.assertTrue(F.contains(G))
        self.assertFalse(G.contains(F))
        self.assertEqual(classify.Frame([1, 2, 3]).rank, 2)


if __name__ == '__main__':
    unittest.main()
