"""Behavioral and independent-arithmetic checks for the joint prefix grid."""
import copy
from fractions import Fraction as Q
import importlib.util
import json
import marshal
import os
from pathlib import Path
import shutil
import subprocess
import struct
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('joint_grid', HERE / 'verify.py')
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


class JointGridTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word, cls.archive, cls.arithmetic = v.load_inputs()

    def test_noncommuting_gaussian_factor_lemma(self):
        # Four Gaussian basis columns, arbitrary interspersed permutations/phases.
        columns = [[(Q(int(i == j)), Q(0)) for i in range(4)] for j in range(4)]
        for gates in range(1, 19):
            direction = 1 + gates % 3
            for j, column in enumerate(columns):
                before = list(column)
                for i in range(4):
                    a, b = before[i]
                    c, d = before[i ^ direction]
                    sign = 1 if gates % 2 else -1
                    column[i] = ((a-sign*b+c+sign*d)/2,
                                 (b+sign*a+d-sign*c)/2)
                # Z phases and address permutations need not commute with C.
                phased = [(-b, a) if (i+gates) % 3 == 0 else (a, b)
                          for i, (a, b) in enumerate(column)]
                columns[j] = [phased[(i+gates) % 4] for i in range(4)]
            scale = 2**((gates+1)//2)
            self.assertTrue(all((x*scale).denominator == 1
                                for column in columns for pair in column for x in pair))
        self.assertEqual(v.gaussian_lemma(), [(n+1)//2 for n in range(19)])
        self.assertNotEqual((Q(1, 2) * 2**(1//2)).denominator, 1)

    def test_tensor_envelope(self):
        _, evidence = v.census(self.word)
        forms = [(int(n), d) for n, d in evidence['gate_counts'].items()]
        for depth in list(range(1, 65)) + [1000, 10**20, 10**20+1]:
            self.assertEqual(max((n*depth+1)//2+d for n, d in forms),
                             (15*depth+1)//2+2)

    def test_semantic_faults(self):
        word = copy.deepcopy(self.word)
        index = next(i for i, event in enumerate(word['program']) if event[0] == 'add')
        word['program'][index][3] = '1/3'
        with self.assertRaisesRegex(ValueError, 'dyadic'):
            v.census(word)
        word = copy.deepcopy(self.word)
        index = next(i for i, event in enumerate(word['program']) if event[0] == 'transport')
        word['program'][index][4] += 1
        with self.assertRaisesRegex(ValueError, 'transport rank'):
            v.census(word)
        word = copy.deepcopy(self.word)
        # Remove a real private cleanup ADD, preserving the event count/schema.
        index = max(i for i, event in enumerate(word['program'][:2040])
                    if event[0] == 'add' and event[1] == 'C')
        word['program'][index][3] = str(Q(word['program'][index][3]) * 2)
        with self.assertRaisesRegex(ValueError, 'private erasure'):
            v.census(word)
        word = copy.deepcopy(self.word)
        word['initial_frames']['X0'][0] = True
        with self.assertRaisesRegex(ValueError, 'binary frame'):
            v.census(word)

    def test_source_integrity_before_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            export = Path(tmp) / 'export'
            shutil.copytree(HERE, export, ignore=shutil.ignore_patterns('__pycache__'))
            for name in ('WORD.json', 'predecessor_arithmetic.py', 'clifford_exact.py'):
                path = export / 'inputs' / name
                original = path.read_bytes()
                path.write_bytes(original + b'\nraise RuntimeError("executed corrupt source")\n')
                with self.assertRaisesRegex(ValueError, 'source SHA256'):
                    v.load_inputs(export)
                path.write_bytes(original)
            # A source-matching timestamp cache must not replace pinned source.
            path = export / 'inputs/predecessor_arithmetic.py'
            cache = Path(importlib.util.cache_from_source(str(path)))
            cache.parent.mkdir(exist_ok=True)
            stat = path.stat()
            header = importlib.util.MAGIC_NUMBER + struct.pack(
                '<III', 0, int(stat.st_mtime) & 0xffffffff, stat.st_size)
            sentinel = compile('raise RuntimeError("forged cache executed")', str(path), 'exec')
            cache.write_bytes(header + marshal.dumps(sentinel))
            _, _, arithmetic = v.load_inputs(export)
            self.assertEqual(arithmetic.N, 512)

    def test_strict_receipts_and_output_refusal(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON'):
            v.decode('{"x":1,"x":2}')
        result = v.decode((HERE / 'RESULT.json').read_bytes())
        altered = copy.deepcopy(result)
        altered['schema_version'] = True
        self.assertNotEqual(v.canonical(result), v.canonical(altered))
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'occupied.json'
            output.write_text('preserve me')
            process = subprocess.run([sys.executable, '-I', '-O', '-B',
                                      str(HERE / 'verify.py'), '--out', str(output)],
                                     capture_output=True, text=True, timeout=120)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn('FileExistsError', process.stderr)
            self.assertEqual(output.read_text(), 'preserve me')

    def test_optimized_git_free_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            export = Path(tmp) / 'export'
            shutil.copytree(HERE, export, ignore=shutil.ignore_patterns('__pycache__'))
            env = dict(os.environ, PYTHONOPTIMIZE='2')
            process = subprocess.run([sys.executable, '-I', '-O', '-B',
                                      str(export / 'verify.py')], cwd=tmp,
                                     capture_output=True, text=True, timeout=120, env=env)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(json.loads(process.stdout)['status'],
                             'PASS_P104_JOINT_PREFIX_GRID')


if __name__ == '__main__':
    unittest.main()
