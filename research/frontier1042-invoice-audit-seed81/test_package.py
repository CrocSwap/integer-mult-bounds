"""Unit tests for the seed-81 PR1042 invoice/outer audit. Apache-2.0."""
import json
import subprocess
import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as V  # noqa: E402


class GroupOrder(unittest.TestCase):
    def test_formulas_agree(self):
        for n in range(1, 40):
            self.assertEqual(V.sp_order_product(n), V.sp_order_orbit(n))

    def test_brute_force_small_odd_orthogonal(self):
        self.assertEqual(V.orthogonal_odd_brute(1), 6)
        self.assertEqual(V.orthogonal_odd_brute(2), 720)


class Replay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = V.load_inputs(V.ROOT)

    def test_committed_result_regenerates(self):
        r = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'verify.py')], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('PASS_FRONTIER1042_INVOICE_OUTER_INDEPENDENT', r.stdout)

    def test_every_control_rejected(self):
        res = V.controls(self.data)
        self.assertEqual(len(res), 15)
        self.assertEqual(res['max_rank'], 'halving guard m^2 > 2 max^2')
        self.assertEqual(res['group_Sp70'], 'stock bits')

    def test_kappa_is_last_grid_point(self):
        out = V.run_all(self.data)
        k = Q(self.data['asm']['kappa'])
        self.assertEqual(out['native']['kappa'], str(k))
        self.assertEqual(k, Q(1672188119205421, 10 ** 18))

    def test_result_fields(self):
        res = json.loads((HERE / 'RESULT.json').read_text())
        self.assertEqual(res['guards']['row'], [16469, 20161])
        self.assertTrue(res['native']['all_quadratic'] and res['conservative']['all_quadratic'])


if __name__ == '__main__':
    unittest.main()
