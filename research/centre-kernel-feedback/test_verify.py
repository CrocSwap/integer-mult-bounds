#!/usr/bin/env python3
"""Behavioral controls for causal kernel transport. Apache-2.0."""
import contextlib
from fractions import Fraction as F
import gzip
import io
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_module(name):
    # Read source directly; -B alone does not disable reads of stale bytecode.
    path = HERE/(name+'.py')
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', optimize=0), module.__dict__)
    return module


class Tests(unittest.TestCase):
    def test_assignment_rules_and_minor(self):
        primary = load_module('verify')
        for op in [('add', ['L', 0], ['L', 1], 3, 2),
                   ('copy', ['L', 0], ['L', 1]),
                   ('clear', ['L', 0]), ('scale', ['L', 0], -2, 3)]:
            state = {('L', 0): {0: F(1)}, ('L', 1): {1: F(1)}}
            primary.scalar(state, op)
            for a, b in ((0, 0), (2, -3), (-7, 5)):
                actual = sum(q*(a if k == 0 else b) for k, q in state['L', 0].items())
                expected = {'add': F(a)+F(3, 2)*b, 'copy': F(b),
                            'clear': F(0), 'scale': F(-2, 3)*a}[op[0]]
                self.assertEqual(actual, expected)
        for size in range(1, 6):
            for shift in range(5):
                matrix = [[F((3*i+5*j+shift+2)**2 % 17-8, 2**((i+j)%3))
                           for j in range(size)] for i in range(size)]
                determinant = F(0)
                for perm in itertools.permutations(range(size)):
                    sign = (-1)**sum(perm[i] > perm[j] for i in range(size) for j in range(i+1, size))
                    term = F(sign)
                    for i in range(size): term *= matrix[i][perm[i]]
                    determinant += term
                expected = determinant.numerator*pow(determinant.denominator, -1, primary.PRIME)%primary.PRIME
                rows = [dict(enumerate(row)) for row in matrix]
                self.assertEqual(primary.determinant_mod(rows, list(range(size)), list(range(size))), expected)

    def test_repair_and_noncommutation_controls(self):
        repair = load_module('repair')
        with contextlib.redirect_stdout(io.StringIO()): repair.verify()
        for mutation in ('omit-cleanup', 'wrong-oracle'):
            with self.assertRaises(ValueError): repair.verify(mutation)
        literal = load_module('independent')
        vector = [{0: F(1)}, {1: F(1)}]
        a, b = literal.operator(0), literal.operator(1)
        self.assertNotEqual(literal.apply_matrix(a, literal.apply_matrix(b, vector)),
                            literal.apply_matrix(b, literal.apply_matrix(a, vector)))
        self.assertTrue(literal.repair_check({0: F(2)}, {1: F(1)}, {0: F(2)}, a))
        self.assertFalse(literal.repair_check({0: F(2)}, {1: F(1)}, {0: F(2)}, a, wrong_sign=True))

    def test_git_free_optimized_and_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);package = root/'research/centre-kernel-feedback'
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            relative = 'research/community-frontier1094-audit/selected-replay.tar.gz'
            archive = root/relative;archive.parent.mkdir(parents=True)
            shutil.copy2(ROOT/relative, archive)
            def run(name='verify', *args):
                return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/(name+'.py')), *args],
                                      cwd=root, text=True, capture_output=True, timeout=180)
            good = run();self.assertEqual(good.returncode, 0, good.stderr)
            good = run('repair');self.assertEqual(good.returncode, 0, good.stderr)
            result = package/'RESULT.json';saved = result.read_bytes()
            changed = json.loads(saved);changed['expanded_repair_invoice']['source_written_at_any_prefix'] = 0
            result.write_text(json.dumps(changed))
            bad = run();self.assertNotEqual(bad.returncode, 0);self.assertIn('typed result receipt', bad.stderr)
            result.write_bytes(saved)
            correction = package/'CORRECTION.json';saved = correction.read_bytes()
            changed = json.loads(saved);first = next(iter(changed));key = next(iter(changed[first]));changed[first][key] = '999'
            correction.write_text(json.dumps(changed))
            bad = run();self.assertNotEqual(bad.returncode, 0);self.assertIn('typed correction receipt', bad.stderr)
            correction.write_bytes(saved)
            reference = package/'pr2799-result.json.gz';saved = reference.read_bytes()
            reference.write_bytes(gzip.compress(gzip.decompress(saved)+b' '))
            bad = run();self.assertNotEqual(bad.returncode, 0);self.assertIn('source SHA256', bad.stderr)
            reference.write_bytes(saved)
            with archive.open('r+b') as stream: byte = stream.read(1);stream.seek(0);stream.write(bytes([byte[0]^1]))
            bad = run();self.assertNotEqual(bad.returncode, 0);self.assertIn('source SHA256', bad.stderr)
            bad = run('verify', '--out', str(package))
            self.assertNotEqual(bad.returncode, 0);self.assertIn('FileExistsError', bad.stderr)


if __name__ == '__main__': unittest.main()
