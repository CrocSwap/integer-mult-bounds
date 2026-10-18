"""Adjoint, independent small determinant oracle, and exported-CLI controls.

Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('stream_readout_audit', HERE/'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class Algebra(unittest.TestCase):
    def test_singular_and_invertible_adjoint_rules(self):
        operations = [
            ['clear', ['L', 1]],
            ['copy', ['L', 1], ['L', 0]],
            ['scale', ['L', 1], -3, 4],
            ['add', ['L', 1], ['L', 0], 5, 8],
        ]
        # All input/output basis columns, including arbitrary destination dirt.
        for op in operations:
            for input_column, output_column in itertools.product(range(3), repeat=2):
                state = [F(i == input_column) for i in range(3)]
                if op[0] == 'clear': state[1] = F(0)
                elif op[0] == 'copy': state[1] = state[0]
                elif op[0] == 'scale': state[1] *= F(-3, 4)
                else: state[1] += F(5, 8)*state[0]
                dual = {('L', i): ({0: F(1)} if i == output_column else {})
                        for i in range(3)}
                V.reverse_scalar(dual, op)
                self.assertEqual(state[output_column], dual['L', input_column].get(0, 0))
        with self.assertRaisesRegex(ValueError, 'distinct COPY'):
            V.reverse_scalar({('L', 0): {0: F(1)}}, ['copy', ['L', 0], ['L', 0]])

    def test_minor_determinant_against_leibniz_oracle(self):
        rng = random.Random(20261015)
        cases = 0
        for n in range(1, 5):
            for _ in range(24):
                matrix = [[F(rng.randrange(-3, 4), 2**rng.randrange(3))
                           for _ in range(n)] for _ in range(n)]
                determinant = F(0)
                for permutation in itertools.permutations(range(n)):
                    product = F(1)
                    for i, j in enumerate(permutation): product *= matrix[i][j]
                    parity = sum(permutation[i] > permutation[j]
                                 for i in range(n) for j in range(i+1, n))
                    determinant += (-1 if parity % 2 else 1)*product
                # The rows of this oracle matrix are the API's error columns.
                columns = [{i: q for i, q in enumerate(row) if q} for row in matrix]
                expected = determinant.numerator*pow(determinant.denominator, -1, V.PRIME) % V.PRIME
                self.assertEqual(expected, V.minor_determinant(columns, list(range(n)), list(range(n))))
                cases += 1
        self.assertEqual(cases, 96)


class Export(unittest.TestCase):
    def test_git_free_optimized_cli_and_integrity_controls(self):
        with tempfile.TemporaryDirectory(prefix='centre-stream-readout-') as directory:
            root = Path(directory).resolve()
            package = root/'research/selected-centre-stream-readouts'
            package.mkdir(parents=True)
            for name in ('verify.py', 'SOURCES.json', 'RESULT.json', 'pr2622-result.json'):
                shutil.copyfile(HERE/name, package/name)
            archive = root/'research/community-frontier1094-audit/selected-replay.tar.gz'
            archive.parent.mkdir(parents=True)
            shutil.copyfile(V.ROOT/'research/community-frontier1094-audit/selected-replay.tar.gz', archive)
            self.assertFalse((root/'.git').exists())

            def invoke(*extra):
                return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py'), *extra],
                                      cwd=root, text=True, capture_output=True, timeout=240)

            hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in root.rglob('*') if p.is_file()}
            clean = invoke()
            self.assertEqual(clean.returncode, 0, clean.stdout+clean.stderr)
            self.assertIn('X_rank=1024 Y_rank=1003 full_rank=1152', clean.stdout)
            self.assertEqual(hashes, {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in root.rglob('*') if p.is_file()})

            occupied = package/'occupied.json'
            occupied.write_text('keep me', encoding='utf-8')
            result = invoke('--out', str(occupied))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('FileExistsError', result.stderr)
            self.assertEqual(occupied.read_text(), 'keep me')

            original = (package/'RESULT.json').read_bytes()
            wrong = json.loads(original)
            # bool == 1 in Python; the typed canonical comparison must reject it.
            wrong['schedule_counts']['bank_padding_cover_sweep'] = True
            (package/'RESULT.json').write_text(json.dumps(wrong), encoding='utf-8')
            typed = invoke()
            self.assertNotEqual(typed.returncode, 0)
            self.assertIn('typed result receipt mismatch', typed.stderr)
            (package/'RESULT.json').write_bytes(original)

            with archive.open('r+b') as stream:
                first = stream.read(1)
                stream.seek(0)
                stream.write(bytes([first[0] ^ 1]))
            corrupt = invoke()
            self.assertNotEqual(corrupt.returncode, 0)
            self.assertIn('source SHA256', corrupt.stderr)
            with archive.open('r+b') as stream:
                stream.write(first)

            reference = package/'pr2622-result.json'
            reference.write_bytes(reference.read_bytes()+b' ')
            corrupt = invoke()
            self.assertNotEqual(corrupt.returncode, 0)
            self.assertIn('reference receipt bytes', corrupt.stderr)


if __name__ == '__main__':
    unittest.main()
