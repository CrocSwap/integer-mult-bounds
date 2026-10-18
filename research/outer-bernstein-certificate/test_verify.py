#!/usr/bin/env python3
"""Mathematical and packaging failure tests for the outer certificate.

Gareth Davidson / OpenAI Codex, Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as F
from itertools import product
from math import comb
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import algebra as A
import verify as V


def casteljau(certificate, point):
    """Evaluate the Bernstein tensor by repeated affine interpolation.

    Uses neither power expansion nor the primary Poly arithmetic.
    The two unrestricted positive variables are combined as ordinary powers.
    """
    degrees = certificate['degrees']
    values = dict(zip(product(*(range(d+1) for d in degrees)),
                      (F(c, certificate['scale']) for c in certificate['weights'])))
    reduced = {}
    for index, value in values.items():
        key = index[:5]
        reduced[key] = reduced.get(key, F(0)) + value*point[5]**index[5]*point[6]**index[6]
    for axis in range(4, -1, -1):
        result = {}
        for prefix in product(*(range(degrees[i]+1) for i in range(axis))):
            column = [reduced[prefix+(j,)] for j in range(degrees[axis]+1)]
            while len(column) > 1:
                column = [(1-point[axis])*left+point[axis]*right
                          for left, right in zip(column, column[1:])]
            result[prefix] = column[0]
        reduced = result
    return reduced[()]


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.receipt, cls.pins = V.inputs()
        cls.model, cls.rows = V.obligations(cls.source)
        cls.expected = V.parse_json((HERE/'EXPECTED.json').read_bytes())

    def test_all_rows_by_de_casteljau(self):
        # Asymmetric rational points exercise every coefficient and the two
        # unbounded bridge coordinates, including values far above one.
        points = [(F(1, 7), F(2, 9), F(4, 5), F(3, 8), F(5, 11), F(17), F(101)),
                  (F(5, 6), F(7, 8), F(1, 13), F(12, 13), F(17, 19), F(1, 37), F(10**6))]
        for name, (poly, strict) in self.rows.items():
            for point in points:
                value = casteljau(self.expected['certificates'][name], point)
                self.assertEqual(value, poly.evaluate(point), name)
                self.assertTrue(value > 0 if strict else value == 0, name)

    def test_basis_reconstruction_with_closed_form(self):
        # Check all 64 tensor basis monomials of a cubic by cubic by cubic
        # example, with a nontrivial positive-power bridge coordinate.
        degrees = [3, 3, 3, 0, 0, 1, 0]
        keys = list(product(*(range(d+1) for d in degrees)))
        for a, b, c in product(range(4), repeat=3):
            index = (a, b, c, 0, 0, 1, 0)
            weights = [int(k == index) for k in keys]
            poly = A.reconstruct(dict(degrees=degrees, scale=7, weights=weights))
            point = (F(2, 7), F(3, 5), F(4, 9), F(1, 2), F(1, 3), F(11), F(13))
            target = F(11, 7)
            for x, k in zip(point[:3], (a, b, c)):
                target *= comb(3, k)*x**k*(1-x)**(3-k)
            self.assertEqual(poly.evaluate(point), target)

    def test_positive_sample_does_not_prove_positivity(self):
        x = A.Poly.variable(0)
        p = 1-10*(x-F(1, 2))**2
        self.assertGreater(p.evaluate([F(1, 2)]*7), 0)
        self.assertLess(p.evaluate([F(1, 100)]*7), 0)
        with self.assertRaisesRegex(ValueError, 'negative'):
            A.check_certificate(p, A.nominate(p))

    def test_wrong_gaussian_cap_passes_selected_but_fails_domain(self):
        source = self.source.replace('Q(1,4)-r', 'Q(1,8)-r')
        model, rows = V.obligations(source)
        name = 'slack:alpha_below_one_fourth'
        poly = rows[name][0]
        for witness in self.expected['witnesses'].values():
            point = tuple(map(F, witness['unit_coordinates']+witness['bridge_gaps']))
            self.assertGreater(poly.evaluate(point), 0)
        point = (F(1, 4), F(1, 2), F(1, 2), F(9, 10), F(1, 10), F(1), F(2))
        self.assertLess(poly.evaluate(point), 0)
        with self.assertRaisesRegex(ValueError, 'negative'):
            A.check_certificate(poly, A.nominate(poly))

    def test_zero_requires_nonstrict_obligation(self):
        certificate = A.nominate(A.Poly(0))
        with self.assertRaisesRegex(ValueError, 'strict'):
            A.check_certificate(A.Poly(0), certificate)
        A.check_certificate(A.Poly(0), certificate, strict=False)

    def test_changed_denominator_rejected(self):
        cert = self.expected['certificates']['denominator']
        with self.assertRaisesRegex(ValueError, 'differs'):
            A.check_certificate(self.rows['denominator'][0]+1, cert)

    def test_strict_boundaries(self):
        args = [F(1, 100), F(1, 50), F(1, 4), F(1, 10), F(1, 1000), F(1), F(2)]
        V.admit(*args)
        for index, value in ((0, F(0)), (0, (1-args[2])*args[1]), (4, F(0)),
                             (1, F(1, 32)), (3, F(1, 2)), (2, F(1))):
            changed = list(args)
            changed[index] = value
            with self.assertRaises(ValueError):
                V.admit(*changed)

    def test_closed_bootstrap_equals_recursive_cost(self):
        # Independent comparisons across 72 ordinary-recursion parameter pairs
        # and 12 depths, including small and large finite cutoffs.
        for numerator in range(1, 9):
            s = F(numerator, 10)
            for denominator in range(2, 11):
                initial = s/denominator
                value = initial
                for depth in range(1, 13):
                    value = s*(1-s)+s*value
                    self.assertEqual(value, s-s**depth*(s-initial))

    def test_primary_mutation_controls(self):
        labels = V.controls(self.source, self.expected['certificates'], self.model, self.receipt)
        self.assertEqual(labels, self.expected['controls'])
        self.assertEqual(len(set(labels)), 24)

    def test_unsupported_source_syntax_rejected(self):
        for before, after in (('q=a*(1-2*eta)', 'q=a**(1-2*eta)'),
                              ('q=a*(1-2*eta)', 'q=a*(1-2.0*eta)')):
            with self.assertRaises(ValueError):
                V.obligations(self.source.replace(before, after))

    def test_duplicate_json_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            V.parse_json('{"slack":1,"slack":2}')

    def test_source_integrity_and_relocated_optimized_replay(self):
        with tempfile.TemporaryDirectory(prefix='outer proof with spaces ') as temp:
            root = Path(temp)
            package = root/HERE.relative_to(V.ROOT)
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            for path in V.FILES.values():
                destination = root/path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(V.ROOT/path, destination)
            command = [sys.executable, '-B', '-I', '-O', str(package/'verify.py')]
            passed = subprocess.run(command, cwd='/tmp', capture_output=True, text=True)
            self.assertEqual(passed.returncode, 0, passed.stderr)
            self.assertIn('PASS_OUTER_BERNSTEIN_CERTIFICATE', passed.stdout)
            expected_path = package/'EXPECTED.json'
            original = expected_path.read_bytes()
            corrupted = V.parse_json(original)
            corrupted['certificates']['slack:bit_positive']['weights'][0] = 0.0
            expected_path.write_text(V.json.dumps(corrupted))
            bad_type = subprocess.run(command, cwd='/tmp', capture_output=True, text=True)
            self.assertNotEqual(bad_type.returncode, 0)
            self.assertIn('noninteger weight', bad_type.stderr)
            expected_path.write_bytes(original)
            source = root/V.FILES['engine']
            source.write_bytes(source.read_bytes()+b'\n# changed source\n')
            failed = subprocess.run(command, cwd='/tmp', capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('source hash: engine', failed.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
