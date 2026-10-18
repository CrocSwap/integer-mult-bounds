"""Unit tests and semantic controls for the T74 k554 root enclosure.

Aaron Wang, with help from opencode. Apache-2.0.
"""
from fractions import Fraction as Q
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402

BITS = 400


class Arithmetic(unittest.TestCase):
    def test_log_identities(self):
        V.check_log_identities()

    def test_logs_enclose_float(self):
        logs = V.log_table(73, (1, 2, 3, 4, 5, 8, 48), BITS)
        for r, (lo, hi) in logs.items():
            self.assertLess(lo, hi)
            self.assertLess(hi - lo, 2 ** 16)   # well inside the verifier's 128 guard bits
            self.assertAlmostEqual(lo / 2 ** BITS, math.log(73 / r), places=14)

    def test_exp_encloses_float(self):
        y = (Q(1, 137) * 2 ** BITS).__floor__()
        lo, hi = V.exp_interval(y, y + 1, BITS)
        self.assertLess(hi - lo, 2 ** 12)
        self.assertAlmostEqual(lo / 2 ** BITS, math.exp(1 / 137), places=14)

    def test_fail_closed_on_low_precision(self):
        src = V.load_inputs()['sources']['pr1672']
        self.assertEqual(V.side(src, Q(src['complex_lower']), False, 64), 0)


class Brackets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = V.load_inputs()['sources']['pr1672']

    def test_native_bracket(self):
        self.assertTrue(V.bracket(self.src, False)['pass'])

    def test_conservative_bracket(self):
        self.assertTrue(V.bracket(self.src, True)['pass'])

    def test_controls_rejected(self):
        controls = V.controls(self.src)
        self.assertEqual(len(controls), 7)
        for name, rejected in controls.items():
            self.assertTrue(rejected, name)


class Ledger(unittest.TestCase):
    def test_composition(self):
        for src in V.load_inputs()['sources'].values():
            self.assertEqual(V.ledger(src)['deficit'], 23680)

    def test_composition_control(self):
        src = dict(V.load_inputs()['sources']['pr1672'])
        src['provider_counts'] = dict(src['provider_counts'], extra=416)
        with self.assertRaises(ValueError):
            V.ledger(src)

    def test_inputs_pinned(self):
        V.check_inputs_pin()


if __name__ == '__main__':
    unittest.main()
