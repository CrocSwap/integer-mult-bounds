#!/usr/bin/env python3
"""Semantic and packaging controls for the scoped Neumann audit. Apache-2.0."""
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('audit', HERE/'verify.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class Mathematics(unittest.TestCase):
    def test_complex_orientation_and_dense_inverse(self):
        matrix = [[(0, 16)]]
        self.assertEqual(audit.GridOracle(matrix)((64, 0)), (0, 16))
        self.assertEqual(audit.GridOracle(matrix)((0, 64)), (-16, 0))
        self.assertEqual(audit.inverse_target(audit.real_matrix(matrix), (1, 0)),
                         (Q(8, 17), Q(-2, 17)))

    def test_inward_half_and_exact_subtractions(self):
        p = 101
        for n in range(-17, 18):
            for m in range(-17, 18):
                u = (n, m)
                y, states = audit.horner(u, 1, lambda _: self.fail('unexpected call'), p)
                self.assertLessEqual(y[0]**2 + y[1]**2, Q(n*n+m*m, 4))
                self.assertTrue(audit.below(audit.sub(y, (Q(n, 2), Q(m, 2))), Q(1), True))
                self.assertEqual(states, [y])

    def test_family_oracle_contract_oddness_and_zero(self):
        p, a = 101, 11
        matrix = [[(0, 0), (16, 0)], [(16, 0), (0, 0)]]
        oracle = audit.GridOracle(matrix, 3*a)
        self.assertEqual(oracle((0, 0, 0, 0)), (0, 0, 0, 0))
        for n in [*range(-12, 13), 1 << p, -(1 << p)]:
            for m in range(-12, 13):
                u = (n, m, -m, n)
                exact = (Q(-m, 4), Q(n, 4), Q(n, 4), Q(m, 4))
                y = oracle(u)
                self.assertTrue(audit.below(audit.sub(y, exact), Q(p, 3), True))
                self.assertEqual(oracle(tuple(-x for x in u)), tuple(-x for x in y))

    def test_oracle_need_not_be_linear_or_zero_preserving(self):
        p, scale = 101, 1 << 101
        # E=0, T(x)=h for all x is a disk-valued absolute-error oracle.
        y, states = audit.horner((scale, 0), 9, lambda _: (1, 0), p)
        self.assertEqual(y, (scale//2-1, 0))
        self.assertTrue(all(audit.disk(x, scale) for x in states))
        self.assertTrue(audit.below(audit.sub(y, (Q(scale, 2), Q(0))), Q(p), True))

    def test_precision_and_term_boundaries(self):
        for k in (0, -1, True, Q(3, 2)):
            with self.assertRaisesRegex(ValueError, 'term count'):
                audit.horner((1, 0), k, lambda x: x, 101)
        for p in (0, 100, True):
            with self.assertRaisesRegex(ValueError, 'precision'):
                audit.horner((1, 0), 1, lambda x: x, p)
        with self.assertRaisesRegex(ValueError, 'input outside'):
            audit.horner(((1 << 101)+1, 0), 1, lambda x: x, 101)
        with self.assertRaisesRegex(ValueError, 'oracle outside'):
            audit.horner((1, 0), 2, lambda _: ((1 << 101)+1, 0), 101)
        for value in ((0,), (0, 0, 0, 0), (Q(1, 2), 0), (True, 0)):
            with self.assertRaisesRegex(ValueError, 'invalid oracle grid vector'):
                audit.horner((1, 0), 2, lambda _, value=value: value, 101)
        with self.assertRaisesRegex(ValueError, 'nonempty complex vector'):
            audit.horner((), 1, lambda x: x, 101)
        for p in (101, 102, 128, 257, 1024, 4096):
            self.assertLess(audit.QMAX + Q(p, 3*(1 << p)), Q(1, 2))
            self.assertLess((Q(p, 3)+Q(3, 2))/(1-audit.QMAX), p)

    def test_disk_margin_is_a_separate_obligation(self):
        p, scale = 101, 1 << 101
        def bad_margin_oracle(x):
            return (-((scale//2-1)*x[0]//scale)-3, 0)
        with self.assertRaisesRegex(ValueError, 'Horner iterate outside'):
            audit.horner((scale, 0), p, bad_margin_oracle, p)
        witness = audit.controls()['weak_margin_witness']
        self.assertEqual(witness['first_exit'], 99)
        self.assertEqual(witness['iterate_numerator'], scale+1)


class Packaging(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='neumann audit ')
        self.root = Path(self.temp.name)/'relocated root'
        self.package = self.root/'research'/HERE.name
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns('__pycache__'))
        sources = json.loads((HERE/'SOURCES.json').read_text())
        self.live_inputs = [row['path'] for row in sources['files'] if row['usage'] == 'input']
        for name in self.live_inputs:
            target = self.root/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(audit.ROOT/name, target)

    def tearDown(self):
        for path in self.root.rglob('*'):
            path.chmod(0o755 if path.is_dir() else 0o644)
        self.root.chmod(0o755)
        self.temp.cleanup()

    def run_verifier(self, *args):
        env = dict(os.environ, PYTHONOPTIMIZE='2')
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(self.package/'verify.py'), *args],
                              cwd=self.temp.name, text=True, capture_output=True, timeout=100, env=env)

    def test_changed_and_missing_source_fail_closed(self):
        path = self.root/self.live_inputs[0]
        content = path.read_bytes()
        path.write_bytes(content+b'\n')
        run = self.run_verifier()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('source drift', run.stderr)
        path.unlink()
        run = self.run_verifier()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('missing source', run.stderr)

    def test_changed_receipt_is_rejected(self):
        path = self.package/'RESULT.json'
        data = json.loads(path.read_text())
        data['fixture_audit']['cases'] = 649
        path.write_text(json.dumps(data, indent=2, sort_keys=True)+'\n')
        run = self.run_verifier()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('receipt mismatch', run.stderr)

    def test_existing_output_is_preserved(self):
        path = Path(self.temp.name)/'existing.json'
        path.write_text('preserve me')
        run = self.run_verifier('--write', str(path))
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('refusing to overwrite', run.stderr)
        self.assertEqual(path.read_text(), 'preserve me')

    def test_read_only_relocation_without_git(self):
        paths = [p for p in self.root.rglob('*') if p.is_file()]
        before = {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in paths}
        for path in self.root.rglob('*'):
            path.chmod(0o555 if path.is_dir() else 0o444)
        self.root.chmod(0o555)
        run = self.run_verifier()
        self.assertEqual(run.returncode, 0, run.stdout+'\n'+run.stderr)
        self.assertIn('PASS_NEUMANN_ROUNDING_AUDIT', run.stdout)
        after = {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main(verbosity=2)
