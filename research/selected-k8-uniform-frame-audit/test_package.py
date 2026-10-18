#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Mathematical failure controls and source/receipt/relocation checks."""
import copy
from fractions import Fraction as Q
import importlib.util
import json
from math import comb
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('uniform_audit', HERE / 'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class MathematicalChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module, cls.word, cls.dual = V.source_inputs()
        cls.model = cls.module.Model(cls.word)
        cls.histogram, _, _, _ = V.audit_lp(cls.module, cls.model, cls.dual)

    def test_power_prices_by_independent_integer_roots(self):
        # No logarithms, Taylor coefficients or Bernstein basis in this oracle.
        scale = 1 << 96
        for denominator in (32, 64, 128):
            prices = {}
            for d in V.RANKS:
                radicand = d**(denominator-1) * scale**denominator
                root = V.root_floor(radicand, denominator)
                self.assertLessEqual(root**denominator, radicand)
                self.assertGreater((root+1)**denominator, radicand)
                prices[d] = (Q(root, scale)-d, Q(root+1, scale)-d)
            for vector in self.histogram:
                if vector == V.ZERO:
                    continue
                lower = sum(v*prices[d][0 if v > 0 else 1]
                            for d, v in zip(V.RANKS, vector))
                self.assertGreater(lower, 0, (denominator, vector))
                V.uniform_certificate(vector)
        # The exact square is positive, but reversing it must be rejected.
        with self.assertRaisesRegex(ValueError, 'Bernstein positivity'):
            V.uniform_certificate(tuple(-x for x in V.SQUARE))
        # The first-order slope of this square is zero, not a strict margin.
        self.assertEqual(V.uniform_certificate(V.SQUARE)['proof'], '4*(1-2^-a)^2')
        with self.assertRaisesRegex(ValueError, 'alternating-series range'):
            V.uniform_certificate(V.SQUARE, Q(1))

    def test_bernstein_change_of_basis(self):
        # Check exact polynomial identity for every nonspecial source vector.
        for vector in self.histogram:
            if vector in (V.ZERO, V.SQUARE):
                continue
            polynomial = V.slope_lower_polynomial(vector)
            coefficients = V.bernstein(polynomial, V.A_MAX)
            for t in (Q(0), Q(2, 7), Q(1)):
                a = t*V.A_MAX
                direct = sum(c*a**i for i, c in enumerate(polynomial))
                bernstein = sum(c*comb(8, i)*t**i*(1-t)**(8-i)
                                for i, c in enumerate(coefficients))
                self.assertEqual(direct, bernstein)
        # Deliberately omit the interval scaling: the identity must detect it.
        polynomial = [Q(1), Q(-2), Q(3)]
        wrong = V.bernstein(polynomial, Q(1))
        t = Q(2, 7)
        expected = sum(c*(t*V.A_MAX)**i for i, c in enumerate(polynomial))
        self.assertNotEqual(expected, sum(c*comb(2, i)*t**i*(1-t)**(2-i)
                                         for i, c in enumerate(wrong)))

    def test_claim_boundaries(self):
        vector = tuple(map(Q, (0, 8, 1, -4, 0, 0, 0, 0)))
        self.assertIn(vector, self.histogram)
        lo, hi = map(Q, V.power_boundary(vector))
        self.assertLess(lo, hi)
        self.assertLess(hi, 0)
        with self.assertRaisesRegex(ValueError, 'Bernstein positivity'):
            V.uniform_certificate(vector, Q(1, 20))
        vector = tuple(map(Q, (-3, 1, 0, 0, 0, 0, 0, 0)))
        f = [min(d, 2) for d in range(10)]
        self.assertTrue(all(2*f[d] >= f[d-1]+f[d+1] for d in range(1, 9)))
        self.assertEqual(sum(v*(f[d]-d*f[1]) for d, v in zip(V.RANKS, vector)), -1)
        fixture = V.alternative_optimum(self.model)
        self.assertNotEqual(fixture['before'], fixture['after'])
        self.assertEqual(fixture['profile'], {str(r): n for r, n in V.PROFILE.items()})

    def test_dual_objective_and_coverage_mutations(self):
        corrupted = copy.deepcopy(self.dual)
        normalization = json.dumps(('N', self.model.components()[0][0]))
        values = corrupted['components'][0]['duals'].setdefault(normalization, {})
        values['2'] = str(Q(values.get('2', '0')) + 1)
        with self.assertRaisesRegex(ValueError, 'symbolic objective mismatch'):
            V.audit_lp(self.module, self.model, corrupted)
        missing = copy.deepcopy(self.dual)
        missing['components'].pop()
        with self.assertRaisesRegex(ValueError, 'component coverage'):
            V.audit_lp(self.module, self.model, missing)
        unknown = copy.deepcopy(self.dual)
        unknown['components'][0]['duals']['unknown-row'] = {'2': '1'}
        with self.assertRaisesRegex(ValueError, 'unknown dual row'):
            V.audit_lp(self.module, self.model, unknown)

    def test_second_column_assembly_and_graph_mutations(self):
        original = self.module.lp
        def missing_column(*args):
            rows, rhs, columns = original(*args)
            return rows, rhs, columns[:-1]
        with patch.object(self.module, 'lp', missing_column):
            with self.assertRaisesRegex(ValueError, 'two column assemblies disagree'):
                V.audit_lp(self.module, self.model, self.dual)
        model = copy.copy(self.model)
        model.edges = dict(model.edges)
        model.edges.pop(next(iter(model.edges)))
        with self.assertRaisesRegex(ValueError, 'complete graph binding'):
            V.graph_checks(model)
        model = copy.copy(self.model)
        model.domain = dict(model.domain)
        node = next(iter(model.domain))
        model.domain[node] = model.domain[node][:-1]
        with self.assertRaisesRegex(ValueError, 'complete graph binding'):
            V.graph_checks(model)
        self.assertEqual(V.graph_checks(self.model), 5586)


class PackageChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='k8-uniform-audit-')
        self.root = Path(self.temp.name)
        self.package = self.root / 'research' / HERE.name
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns('__pycache__'))
        for path in V.INPUTS:
            dest = self.root / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(V.ROOT / path, dest)

    def tearDown(self):
        for path in self.root.rglob('*'):
            path.chmod(0o755 if path.is_dir() else 0o644)
        self.root.chmod(0o755)
        self.temp.cleanup()

    def invoke(self, *args):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(self.package / 'verify.py'), *args],
                              cwd=self.root, text=True, capture_output=True, timeout=90)

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in self.root.rglob('*') if p.is_file()}

    def test_optimized_readonly_relocation_and_regeneration(self):
        before = self.snapshot()
        regenerated = self.invoke('--write')
        self.assertEqual(regenerated.returncode, 0, regenerated.stderr)
        self.assertEqual(before, self.snapshot())
        for path in self.root.rglob('*'):
            path.chmod(0o555 if path.is_dir() else 0o444)
        self.root.chmod(0o555)
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASS_SELECTED_K8_UNIFORM_FRAME_AUDIT', result.stdout)
        self.assertEqual(before, self.snapshot())

    def test_receipt_mutations_and_missing_receipt(self):
        path = self.package / 'RESULT.json'
        original = path.read_bytes()
        for change in ('missing_vector', 'false_interval', 'bool_for_int'):
            result = V.parse(original)
            if change == 'missing_vector':
                result['residual_proofs'].pop()
            elif change == 'false_interval':
                result['a_interval'][1] = '1/20'
            else:
                result['residual_proofs'][0]['columns'] = True
            path.write_text(json.dumps(result))
            run = self.invoke()
            self.assertNotEqual(run.returncode, 0, change)
            self.assertIn('result receipt mismatch', run.stderr)
        path.unlink()
        self.assertNotEqual(self.invoke().returncode, 0)
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            V.parse('{"x":1,"x":2}')
        with self.assertRaisesRegex(ValueError, 'noninteger JSON number'):
            V.parse('{"x":NaN}')

    def test_source_pin_and_dual_corruption(self):
        model = self.root / V.MODEL
        original = model.read_bytes()
        model.write_bytes(original + b'\n# drift\n')
        run = self.invoke()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('live source SHA256', run.stderr)
        model.write_bytes(original)
        path = self.package / 'SOURCES.json'
        original = path.read_bytes()
        source = V.parse(original)
        source['files'].pop()
        path.write_text(json.dumps(source))
        run = self.invoke()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('source inventory', run.stderr)
        path.write_bytes(original)
        dual = self.package / 'DUALS.json.gz'
        dual.write_bytes(dual.read_bytes()[:-1])
        run = self.invoke()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('dual source SHA256', run.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
