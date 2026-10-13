#!/usr/bin/env python3
"""Focused reproducibility and failure controls. Apache-2.0, ToikY/Codex."""
import copy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


verify = module('verify')
independent = module('crosscheck')


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = verify.run()
        cls.expected = json.loads((HERE / 'EXPECTED.json').read_text())
        cls.independent = independent.run(ROOT)
        cls.rows, _ = verify.load_inputs()
        cls.temporary = tempfile.TemporaryDirectory(prefix='x4 pair closure with spaces ')
        cls.closure = Path(cls.temporary.name)
        shutil.copytree(HERE, cls.closure / 'research/complex-x4-scaled-pairs',
                        ignore=shutil.ignore_patterns('__pycache__'))
        for name in json.loads((HERE / 'SOURCES.json').read_text())['files']:
            destination = cls.closure / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_complete_census_agrees_with_independent_primitive_words(self):
        self.assertTrue(verify.same_json(self.receipt, self.expected))
        self.assertEqual(self.independent['cases'], self.receipt['census']['cases'])
        self.assertEqual(self.independent['records_sha256'],
                         self.receipt['census']['records_sha256'])
        for exponent, primary in self.receipt['census']['by_exponent'].items():
            other = self.independent['by_exponent'][exponent]
            for key in ('cases', 'max_saving_per_component', 'min_saving_per_component'):
                self.assertEqual(other[key], primary[key])
            self.assertEqual(other['profitable_cases'], primary['profitable'])
        self.assertTrue(verify.same_json(self.independent,
                                        json.loads((HERE / 'INDEPENDENT.json').read_text())))

    def test_tail_formula_against_explicit_primitive_words(self):
        for negative in (False, True):
            for a in range(-4, 5):
                for b in range(-4, 5):
                    anchor = len(independent.primitive_word(Fraction(8*a+b, 2**(2+3*negative))))
                    slope = verify.tail_slope(a, b, negative)
                    for k in (3, 4, 9, 29, 128):
                        cost = len(independent.primitive_word(Fraction(a*2**k+b, 2**(2+k*negative))))
                        self.assertEqual(cost, anchor+slope*(k-3))

    def test_scope_positive_controls(self):
        unit = self.receipt['census']['by_exponent']['0']
        self.assertEqual(unit['profitable'], 2978)
        self.assertEqual(unit['ties'], 42)
        self.assertEqual(verify.pair_saving({(2, 1): 10}, -2, 1), 40)
        self.assertLess(self.independent['controls']['unpaid_shears_toy']['paid_saving'], 0)
        self.assertGreater(self.independent['controls']['unpaid_shears_toy']['unpaid_saving'], 0)

    def test_tail_wrong_slope_is_detected(self):
        with patch.object(verify, 'tail_slope', return_value=0):
            with self.assertRaisesRegex(ValueError, 'tail affine identity'):
                verify.tail_checks()

    def test_boundary_bill_changes_closest_case(self):
        best = self.receipt['census']['by_exponent']['1']['first_maximizer']
        saving, i, j, a, b = best
        histogram = verify.pair_histogram(self.rows[i], self.rows[j])
        self.assertEqual(saving, -10)
        self.assertEqual(verify.pair_saving(histogram, a, b), saving)
        # Omitting both paid shears falsely turns the closest loss into a tie.
        unpaid = saving + 2 * verify.horner(a, b)
        self.assertEqual(unpaid, 0)

    def test_source_drift_is_rejected_before_census(self):
        path = self.closure / verify.PINS
        original = path.read_bytes()
        try:
            path.write_bytes(original+b'\n')
            with self.assertRaisesRegex(ValueError, 'source hash mismatch'):
                verify.load_inputs(self.closure)
        finally:
            path.write_bytes(original)

    def test_missing_archive_is_rejected(self):
        path = self.closure / verify.ARCHIVE
        saved = path.with_suffix('.saved')
        path.rename(saved)
        try:
            with self.assertRaises(FileNotFoundError):
                verify.load_inputs(self.closure)
        finally:
            saved.rename(path)

    def test_missing_source_and_member_pins_are_rejected(self):
        manifest = json.loads((HERE / 'SOURCES.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            alternate = Path(directory)
            for field, message in (('files', 'incomplete source file pins'),
                                   ('archive_members', 'incomplete archive member pins')):
                changed = copy.deepcopy(manifest)
                changed[field] = {}
                (alternate / 'SOURCES.json').write_text(json.dumps(changed))
                with patch.object(verify, 'HERE', alternate):
                    with self.assertRaisesRegex(ValueError, message):
                        verify.load_inputs(ROOT)

    def test_typed_receipt_corruption_is_rejected(self):
        for bad in (True, 174048.0, 174049):
            changed = copy.deepcopy(self.expected)
            changed['census']['cases'] = bad
            self.assertFalse(verify.same_json(changed, self.expected))

    def test_optimized_minimal_offline_relocation_and_output_preservation(self):
        package = self.closure / 'research/complex-x4-scaled-pairs'
        before = {str(p.relative_to(self.closure)): p.read_bytes()
                  for p in self.closure.rglob('*') if p.is_file()}
        for script, marker in (('verify.py', 'PASS_X4_NONUNIT_PAIR_EXCLUSION'),
                               ('crosscheck.py', 'PASS_X4_NONUNIT_INDEPENDENT')):
            result = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/script)],
                                    cwd=self.temporary.name, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            self.assertIn(marker, result.stdout)
        after = {str(p.relative_to(self.closure)): p.read_bytes()
                 for p in self.closure.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        expected_path = package/'EXPECTED.json'
        original = expected_path.read_bytes()
        bad = json.loads(original)
        bad['census']['cases'] = True
        expected_path.write_text(json.dumps(bad))
        try:
            result = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py')],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('expected receipt mismatch', result.stderr)
        finally:
            expected_path.write_bytes(original)


if __name__ == '__main__':
    unittest.main(verbosity=2)
