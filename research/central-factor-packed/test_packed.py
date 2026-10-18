#!/usr/bin/env python3
"""Differential, malformed-input and defect-sensitive packing controls."""
from copy import deepcopy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(HERE))
import packed
import verify
from experiments.complex_centers import factor, verify_factor as reference


def outcome(fn, value):
    try:
        return ('accepted', fn(value))
    except ValueError as error:
        return ('rejected', str(error))


class PackedFactorTests(unittest.TestCase):
    def compare(self, value, accepted=False):
        old = deepcopy(value)
        expected = outcome(reference, value)
        self.assertEqual(outcome(packed.verify_factor, value), expected)
        self.assertEqual(value, old, 'Verifier mutated its input')
        self.assertEqual(expected[0], 'accepted' if accepted else 'rejected')
        return expected

    def test_full_published_factor_and_parameter_cases(self):
        for h in (8, 10, 12, 18, 26):
            with self.subTest(h=h):
                self.compare(factor(h), accepted=True)
        # Match the original verifier even on its vacuous small domains.
        for h in (0, 1, 2):
            self.compare(dict(h=h, triples=[], gather=[], scatter=[]), accepted=True)

    def test_equivalent_factors_and_sparse_order_are_accepted(self):
        for h in (8, 12):
            f = factor(h)
            permutation = list(range(h))
            random.Random(93 + h).shuffle(permutation)
            f['gather'] = [tuple(reversed([(permutation[i], x) for i, x in v]))
                           for v in f['gather']]
            f['scatter'] = [tuple(u[permutation.index(i)] for i in range(h))
                            for u in f['scatter']]
            self.compare(f, accepted=True)
            f = factor(h)
            f['gather'] = [tuple((i, -x if i == 1 else x) for i, x in v)
                           for v in f['gather']]
            f['scatter'] = [tuple(-x if i == 1 else x for i, x in enumerate(u))
                            for u in f['scatter']]
            self.compare(f, accepted=True)

    def test_every_small_scatter_entry_and_gather_sign(self):
        base = factor(8)
        counts = {'scatter_replacements': 0, 'gather_signs': 0, 'gather_deletions': 0}
        for row, u in enumerate(base['scatter']):
            for col, before in enumerate(u):
                for after in (-1, 0, 1, 2):
                    if before == after:
                        continue
                    f = deepcopy(base)
                    replacement = list(u)
                    replacement[col] = after
                    f['scatter'][row] = tuple(replacement)
                    self.compare(f)
                    counts['scatter_replacements'] += 1
        for col, v in enumerate(base['gather']):
            for term, (i, x) in enumerate(v):
                f = deepcopy(base)
                replacement = list(v)
                replacement[term] = (i, -x)
                f['gather'][col] = tuple(replacement)
                self.compare(f)
                counts['gather_signs'] += 1
                f['gather'][col] = v[:term] + v[term+1:]
                self.compare(f)
                counts['gather_deletions'] += 1
        print('EXHAUSTIVE_CONTROLS ' + json.dumps(counts, sort_keys=True), flush=True)

    def test_structure_types_and_charge_checks(self):
        cases = []
        for key in ('triples', 'gather', 'scatter'):
            f = factor(8)
            f[key] = f[key][:-1]
            cases.append(f)
        for value in (True, Fraction(1, 2), 0.0):
            f = factor(8)
            f['scatter'][0] = (value,) + f['scatter'][0][1:]
            cases.append(f)
        for v in (((0, 1), (0, -1)), ((-1, 1),), ((8, 1),),
                  ((True, 1),), ((0, True),), ((0, 0),), ((0, 2),)):
            f = factor(8)
            f['gather'][0] = v
            cases.append(f)
        f = factor(8)
        f['scatter'][0] = f['scatter'][0][:-1]
        cases.append(f)
        f = factor(8)
        f['triples'][0], f['triples'][1] = f['triples'][1], f['triples'][0]
        cases.append(f)
        for f in cases:
            self.compare(f)
        # Product is correct, but a -2 scatter weight must still be rejected.
        f = factor(8)
        f['gather'] = [tuple((i, -x if i == 0 else x) for i, x in v) for v in f['gather']]
        f['scatter'] = [(-u[0],) + u[1:] for u in f['scatter']]
        self.assertEqual(self.compare(f)[1], 'Scalar charge requires these dyadic weights')

    def test_seed93_large_signed_entries_and_end_positions(self):
        rng = random.Random(93)
        for trial in range(64):
            h = rng.choice((8, 10, 12, 14))
            f = factor(h)
            row = rng.choice((0, len(f['scatter']) - 1, rng.randrange(len(f['scatter']))))
            col = rng.randrange(h)
            u = list(f['scatter'][row])
            u[col] = rng.choice((-1, 1)) * (1 << rng.randrange(2, 200))
            f['scatter'][row] = tuple(u)
            self.compare(f)
        for where in (0, -1):
            f = factor(26)
            f['gather'][where] = ()
            self.compare(f)

    def test_column_swap_exposes_an_underpriced_radix(self):
        f = factor(8)
        f['gather'][0], f['gather'][1] = f['gather'][1], f['gather'][0]
        self.compare(f)
        # Deliberately faulty B=1 compares only row sums, losing columns.
        # This control would pass that faulty implementation, but fails above.
        with patch.object(packed, '_radix_bits', return_value=0):
            self.assertEqual(outcome(packed.verify_factor, f)[0], 'accepted')
        self.assertEqual(outcome(packed.verify_factor, f)[0], 'rejected')

    def test_no_stale_acceptance_after_in_place_mutation(self):
        f = factor(8)
        self.compare(f, accepted=True)
        f['gather'][-1] = ()
        self.compare(f)

    def test_pins_detect_source_fixture_and_upstream_changes(self):
        pins = verify.admit_sources()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in pins['files']:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            verify.admit_sources(root)
            for name in ('scripts/experiments/complex_centers.py', verify.FIXTURE,
                         'upstream/manifest.json'):
                path = root / name
                before = path.read_bytes()
                path.write_bytes(before + b' ')
                with self.assertRaisesRegex(ValueError, 'Source pin mismatch'):
                    verify.admit_sources(root)
                path.write_bytes(before)
            (root / 'scripts/audit_complex_centers.py').unlink()
            with self.assertRaisesRegex(ValueError, 'Source pin mismatch'):
                verify.admit_sources(root)

    def test_adapter_changes_and_incomplete_receipts_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            here = Path(directory)
            for name in ('SOURCES.json', 'packed.py', 'verify.py'):
                shutil.copyfile(HERE / name, here / name)
            (here / 'packed.py').write_bytes((here / 'packed.py').read_bytes() + b'\n')
            with patch.object(verify, 'HERE', here):
                with self.assertRaisesRegex(ValueError, 'Adapter pin mismatch'):
                    verify.admit_sources()
        # The inherited side audit contains assertions and its wrapper forbids -O.
        if __debug__:
            import audit_complex_centers as audit
            expected = json.loads((ROOT / verify.FIXTURE).read_text())
            for field in ('central_factor', 'scalar_charge', 'side_phase_frames'):
                broken = deepcopy(expected)
                del broken[field]
                with patch.object(audit, 'certificate', return_value=broken):
                    with self.assertRaisesRegex(ValueError, 'Complete historical certificate mismatch'):
                        verify.replay()
            broken = deepcopy(expected)
            broken['central_factor']['coefficients_checked'] -= 1
            with patch.object(audit, 'certificate', return_value=broken):
                with self.assertRaisesRegex(ValueError, 'Complete historical certificate mismatch'):
                    verify.replay()

    def test_optimized_full_audit_and_existing_output_are_rejected(self):
        result = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE / 'verify.py')],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('requires Python assertions', result.stderr)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'existing.json'
            path.write_text('preserve me')
            result = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'verify.py'),
                                     '--output', str(path)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Output already exists', result.stderr)
            self.assertEqual(path.read_text(), 'preserve me')

    def test_original_dirty_interface_tests_in_both_modes(self):
        sys.path.insert(0, str(ROOT / 'tests'))
        import experiments.complex_centers as centers
        for engine in (reference, packed.verify_factor):
            with patch.object(centers, 'verify_factor', engine):
                spec = importlib.util.spec_from_file_location('original_center_tests',
                                                ROOT / 'tests/test_complex_centers.py')
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                result = unittest.TestResult()
                unittest.defaultTestLoader.loadTestsFromModule(module).run(result)
                self.assertEqual(result.testsRun, 4)
                self.assertTrue(result.wasSuccessful(), result.errors + result.failures)


if __name__ == '__main__':
    unittest.main(verbosity=2)
