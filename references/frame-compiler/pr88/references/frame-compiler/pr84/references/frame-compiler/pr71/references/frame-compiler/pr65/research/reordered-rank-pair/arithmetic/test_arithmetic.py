"""Meaningful certificate verification and deliberate-failure controls."""
import sys
sys.dont_write_bytecode = True
from copy import deepcopy
from fractions import Fraction as Q
import json
from pathlib import Path
import subprocess
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import refine
import audit


class ExactArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = json.loads((HERE/'certificate.json').read_text())
        cls.profile = json.loads((refine.ROOT/cls.certificate['profile_path']).read_text())['bit']

    def test_complete_reproduction(self):
        actual = refine.arithmetic.js(refine.build_certificate(refine.ROOT/self.certificate['profile_path']))
        self.assertEqual(actual, self.certificate)

    def test_independent_enclosures_and_controls(self):
        actual = refine.arithmetic.js(audit.audit(self.certificate))
        self.assertEqual(actual, json.loads((HERE/'audit-receipt.json').read_text()))
        self.assertEqual(len(actual['controls']), 10)

    def test_next_bit_grid_is_rejected(self):
        p = self.profile
        result = refine.exact_moment(p['m'], p['W'], {int(t):n for t,n in p['child_multiplicities'].items()}, Q(self.certificate['next_bit_saving']))
        self.assertGreater(result['lower'], 1)

    def test_forged_accepted_bit_is_rejected(self):
        forged = deepcopy(self.certificate)
        forged['bit_saving'] = forged['next_bit_saving']
        with self.assertRaises(AssertionError):
            audit.audit(forged)

    def test_forged_source_digest_is_rejected(self):
        forged = deepcopy(self.certificate)
        forged['profile_sha256'] = '0'*64
        with self.assertRaises(AssertionError):
            audit.audit(forged)

    def test_omitted_constraint_is_rejected(self):
        forged = deepcopy(self.certificate)
        del forged['preferred']['assembly']['constraints']['K_geometry']
        with self.assertRaises(AssertionError):
            audit.audit(forged)

    def test_float_saving_refused(self):
        with self.assertRaises(AssertionError):
            refine.exact_moment(2, 1, {1:1}, 0.01)

    def test_python_optimization_is_rejected(self):
        for script in ('refine.py', 'audit.py'):
            result = subprocess.run([sys.executable, '-B', '-O', str(HERE/script)],
                                    cwd=refine.ROOT, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Assertions must remain enabled', result.stderr)


if __name__ == '__main__':
    unittest.main()
