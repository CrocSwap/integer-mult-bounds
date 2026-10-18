#!/usr/bin/env python3
"""Behavioral and independent rational checks for the local collector. Apache-2.0."""

from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('collector', HERE / 'verify.py')
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def fraction_monomial(vector, record):
    result = [(Fraction(0), Fraction(0))] * 512
    for address in range(512):
        bits = [j for j in range(9) if address & (1 << j)]
        target = record['offset'] ^ sum((bin(mask & address).count('1') % 2) << j
                                         for j, mask in enumerate(record['matrix_rows']))
        phase = record['phase'] + sum(record['linear_Z4'][j] for j in bits)
        phase += 2 * sum((record['quadratic_rows'][j] >> k) & 1
                         for j in bits for k in bits if j < k)
        real, imag = vector[address]
        for _ in range(phase % 4):
            real, imag = -imag, real
        result[target] = real, imag
    return result


def fraction_trace(vector, recipe):
    stages = [fraction_monomial(vector, recipe['right'])]
    for bit in range(7):
        result = [(Fraction(0), Fraction(0))] * 512
        for address in range(512):
            other = address ^ (1 << bit)
            if other < address:
                continue
            a, b = stages[-1][address]
            c, d = stages[-1][other]
            real_sum, imag_sum = a + c, b + d
            real_difference, imag_difference = a - c, b - d
            result[address] = ((real_sum - imag_difference) / 2,
                               (imag_sum + real_difference) / 2)
            result[other] = ((real_sum + imag_difference) / 2,
                             (imag_sum - real_difference) / 2)
        stages.append(result)
    stages.append(fraction_monomial(stages[-1], recipe['left']))
    return stages


class CollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recipes = CHECK.load_inputs()
        cls.mappings = [(CHECK.plan(r['right']), CHECK.plan(r['left'])) for r in cls.recipes]

    def run_cli(self, package, *args):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py'), *args],
                              capture_output=True, text=True, timeout=120)

    def test_independent_fraction_prefixes(self):
        fixtures = [CHECK.basis(0), [(b, a) for a, b in CHECK.basis(173)],
                    [(16 * (x % 17 - 8), 16 * (x % 23 - 11)) for x in range(512)]]
        for integers in fixtures:
            initial = list(integers)
            rational = [(Fraction(a, 16), Fraction(b, 16)) for a, b in integers]
            for recipe, mapping in zip(self.recipes, self.mappings):
                exact = fraction_trace(rational, recipe)
                actual = CHECK.trace(integers, mapping)
                self.assertEqual(len(exact), 9)
                for expected, got in zip(exact, actual):
                    self.assertEqual(expected, [(Fraction(a, 16), Fraction(b, 16)) for a, b in got])
                rational, integers = exact[-1], actual[-1]
            self.assertEqual(integers, initial)

    def test_kernel_argument_and_lattice_failures(self):
        with self.assertRaisesRegex(ValueError, 'integer payload shape'):
            CHECK.inplace_native([0] * 1023, self.mappings[0])
        with self.assertRaisesRegex(ValueError, 'guard domain'):
            CHECK.inplace_native([0] * 1024, self.mappings[0], -1)
        with self.assertRaisesRegex(ValueError, 'inexact internal division'):
            CHECK.native(CHECK.basis(0, 1), self.mappings[1])

    def test_git_free_optimized_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / 'package'
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            result = self.run_cli(package)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('prefixes=9216 guard=4', result.stdout)

    def test_source_corruption_precedes_parsing(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / 'package'
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            (package / 'inputs/WORD.json').write_text('invalid JSON')
            result = self.run_cli(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source SHA256', result.stderr)
            self.assertNotIn('JSONDecodeError', result.stderr)

    def test_receipt_type_and_duplicate_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / 'package'
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            receipt = json.loads((package / 'RESULT.json').read_text())
            receipt['prefix_extra_fractional_bits'][0] = False
            (package / 'RESULT.json').write_text(json.dumps(receipt))
            result = self.run_cli(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('complete receipt mismatch', result.stderr)
            raw = (HERE / 'RESULT.json').read_text()
            (package / 'RESULT.json').write_text('{"status":"duplicate",' + raw[1:])
            result = self.run_cli(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('duplicate JSON key', result.stderr)

    def test_cli_refuses_overwrite_and_unknown_options(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'receipt.json'
            output.write_text('keep this')
            result = self.run_cli(HERE, '--out', str(output))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('output already exists', result.stderr)
            self.assertEqual(output.read_text(), 'keep this')
            result = self.run_cli(HERE, '--unknown-option')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('unrecognized arguments', result.stderr)


if __name__ == '__main__':
    unittest.main()
