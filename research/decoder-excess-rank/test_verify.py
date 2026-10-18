#!/usr/bin/env python3
"""Focused mathematical and file-corruption regressions. Apache-2.0."""
import copy
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V, INDEPENDENT = load('verify'), load('independent')


class ExactRegressions(unittest.TestCase):
    def test_two_by_two_gaussian_ranks(self):
        # Exhaust all 256 matrices; determinant gives a third exact rank oracle.
        alphabet = (V.G(), V.G(1), V.I, V.G(1, 1))
        for a, b, c, d in itertools.product(alphabet, repeat=4):
            expected = 2 if a * d != b * c else int(any((a, b, c, d)))
            self.assertEqual(V.paired_rank([[a, b], [c, d]]), expected)

    def test_realification_must_include_imaginary_part(self):
        a = [[V.G(), V.I], [V.I, V.G()]]
        self.assertEqual(V.paired_rank(a), 2)
        self.assertEqual(V.integer_rank([[0, 0], [0, 0]]), 0)

    def test_all_ten_term_conditions_are_necessary(self):
        _, _, r, scale, h = V.domains()[1]
        u = V.residual_basis(r, scale, 1)
        d = V.symmetric_fixture(r, h, u, 2, 1, mix=False)
        a, residual = V.project(r, scale, d)
        n, z = V.factor_rank_one(residual)
        V.ten_term_conditions(r, a, a, n, n, z, z)
        # Change each independent summand isolated by the projection proof.
        bad_a = copy.deepcopy(a)
        bad_a[0][0] = bad_a[0][0] + 1
        cases = [((r, bad_a, a, n, n, z, z), 'ten-term core')]
        bad_z = copy.deepcopy(z)
        bad_z[0] = V.G(1)
        cases += [((r, a, a, n, n, bad_z, z), 'Bz'),
                  ((r, a, a, n, n, z, bad_z), 'Aw')]
        bad_z = copy.deepcopy(z)
        bad_z[9] = V.G(1)
        cases.append(((r, a, a, n, n, z, bad_z), 'residual coupling'))
        bad_n = copy.deepcopy(n)
        bad_n[0] = bad_n[0] + 1
        cases.append(((r, a, a, bad_n, n, z, z), 'outside root orthogonality'))
        for args, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                V.ten_term_conditions(*args)

    def test_independent_witness_and_corruptions(self):
        self.assertEqual(INDEPENDENT.run()['cost_before'], 82)
        original = json.loads((HERE / 'RESULT.json').read_text())
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'result.json'
            for kind in ('coefficient', 'charge', 'term', 'encoding'):
                altered = copy.deepcopy(original)
                witness = altered['representatives'][0]
                if kind == 'coefficient':
                    witness['D'][0][8][0] = '999'
                elif kind == 'charge':
                    witness['costs'][8] = 0
                elif kind == 'term':
                    for row in witness['D']:
                        row.pop()
                else:
                    witness['D'][0][0][0] = 0.0
                path.write_text(json.dumps(altered))
                with self.subTest(kind=kind), self.assertRaises(ValueError):
                    INDEPENDENT.run(path)

    def test_source_corruption_rejected_before_import(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            package = root / 'research' / 'decoder-excess-rank'
            package.mkdir(parents=True)
            for name in ('verify.py', 'SOURCES.json'):
                shutil.copy2(HERE / name, package / name)
            for name in V.INPUTS:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(V.ROOT / name, destination)
            source = root / 'research/complex-decoder-field-extension-seed44/exact.py'
            with source.open('a') as out:
                out.write('\nraise RuntimeError("MUTANT EXECUTED")\n')
            result = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py')],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source bytes', result.stderr)
            self.assertNotIn('MUTANT EXECUTED', result.stderr)

    def test_optimized_standalone_read_only_relocation(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            for name in ('independent.py', 'RESULT.json'):
                shutil.copy2(HERE / name, target / name)
                (target / name).chmod(0o444)
            target.chmod(0o555)
            try:
                result = subprocess.run([sys.executable, '-I', '-O', '-B', str(target / 'independent.py')],
                                        capture_output=True, text=True, timeout=30, cwd='/')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('PASS_INDEPENDENT_DECODER_WITNESS', result.stdout)
                self.assertEqual(sorted(p.name for p in target.iterdir()), ['RESULT.json', 'independent.py'])
            finally:
                target.chmod(0o755)


if __name__ == '__main__':
    unittest.main()
