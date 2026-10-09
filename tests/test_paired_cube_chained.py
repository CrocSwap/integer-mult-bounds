"""Fail-closed unit tests for the p=11 chained register reuse research package."""
from fractions import Fraction as Q
from pathlib import Path
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'research/paired-cube-p11-chained'


class PairedCubeChainedTests(unittest.TestCase):
    def test_verify_script_exits_cleanly(self):
        result = subprocess.run(
            [sys.executable, str(PACKAGE / 'verify.py')],
            cwd=ROOT,
            text=True,
            capture_output=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASS KAPPA = 3694531/5000000000 = 7.3890620000e-04', result.stdout)

    def test_expected_values_match_barrier_bounds(self):
        expected = json.loads((PACKAGE / 'expected.json').read_text())
        kappa = Q(expected['kappa'])
        self.assertGreater(kappa, Q(7, 10**4))  # Breaks 7.0 x 10^-4
        self.assertEqual(kappa, Q(7389062, 10**10))
        self.assertTrue(expected['all_47_constraints_positive'])
        self.assertLess(float(Q(expected['complex_moment_upper'])), 1.0)
        self.assertLess(float(Q(expected['bit_moment_upper'])), 1.0)

    def test_deficit_invariants(self):
        row_c = json.loads((PACKAGE / 'row_complex.json').read_text())
        row_b = json.loads((PACKAGE / 'row_bit.json').read_text())
        self.assertEqual(row_c['W_per_vertex'] * row_c['m'] - row_c['rank_per_vertex'], 1320)
        self.assertEqual(row_b['W_per_vertex'] * row_b['m'] - row_b['rank_per_vertex'], 1400)


if __name__ == '__main__':
    unittest.main()
