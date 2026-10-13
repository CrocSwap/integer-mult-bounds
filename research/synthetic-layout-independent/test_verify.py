"""Failure-detection checks for the independent synthetic-layout package."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('layout_verifier', HERE / 'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class LayoutVerificationTests(unittest.TestCase):
    def test_signed_rotation_against_formal_monomials(self):
        # Direct exponent reduction, independent of the two-piece rotation.
        for r in (2, 4, 8, 16, 32, 64):
            row = [2 * j - r for j in range(r)]
            for exponent in range(-6 * r, 6 * r + 1):
                expected = [0] * r
                for j, value in enumerate(row):
                    reduced = (j + exponent) % (2 * r)
                    expected[reduced % r] += value if reduced < r else -value
                self.assertEqual(V.physical.monomial(row, exponent), expected)

    def test_noninvolutive_layout_is_required_for_direction_control(self):
        p = V.physical.plan(2, 1, (False, False, True))
        moved = [V.physical.layout_address(i, p) for i in range(16)]
        inverse = [V.physical.layout_address(i, p, True) for i in range(16)]
        self.assertNotEqual(moved, inverse)
        self.assertEqual(sorted(moved), list(range(16)))
        for i in range(16):
            self.assertEqual(inverse[moved[i]], i)

    def test_all_controls_have_actual_coefficient_witnesses(self):
        controls = V.controls()
        self.assertEqual(len(controls), 11)
        self.assertEqual(controls, json.loads((HERE / 'EXPECTED.json').read_text())['negative_controls'])
        for control in controls:
            witness = control['witness']
            self.assertNotEqual(witness['actual_numerator'], witness['expected_numerator'])

    def test_changed_or_incomplete_receipt_rejected(self):
        expected = json.loads((HERE / 'EXPECTED.json').read_text())
        mutants = []
        changed = copy.deepcopy(expected)
        changed['arithmetic']['cases'].pop()
        mutants.append(changed)
        changed = copy.deepcopy(expected)
        changed['negative_controls'][0]['witness']['actual_numerator'] += 1
        mutants.append(changed)
        changed = copy.deepcopy(expected)
        changed['layouts']['complete_addresses'] -= 1
        mutants.append(changed)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'receipt.json'
            for mutant in mutants:
                path.write_text(json.dumps(mutant))
                with self.assertRaisesRegex(ValueError, 'receipt mismatch'):
                    V.check_receipt(expected, path)

    def test_source_changes_fail_before_arithmetic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pins = json.loads((HERE / 'SOURCES.json').read_text())
            for relative in pins['sources']:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(HERE.parents[1] / relative, target)
            V.source_check(root)
            changed = root / 'upstream/build/sections/06-transforms.tex'
            changed.write_bytes(changed.read_bytes() + b'\nmutated source\n')
            with self.assertRaisesRegex(ValueError, 'source drift'):
                V.source_check(root)
            changed.unlink()
            with self.assertRaises(FileNotFoundError):
                V.source_check(root)

    def test_optimized_relocated_replay_and_corrupt_source(self):
        # This is a genuinely isolated package/source closure, not a repo import.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / 'research/synthetic-layout-independent'
            shutil.copytree(HERE, target, ignore=shutil.ignore_patterns('__pycache__'))
            pins = json.loads((HERE / 'SOURCES.json').read_text())
            for relative in pins['sources']:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(HERE.parents[1] / relative, destination)
            command = [sys.executable, '-B', '-I', '-O', str(target / 'verify.py')]
            result = subprocess.run(command, cwd=root, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('PASS_SYNTHETIC_LAYOUT', result.stdout)
            source = root / 'upstream/build/sections/06-transforms.tex'
            source.write_bytes(source.read_bytes() + b'\nchanged\n')
            result = subprocess.run(command, cwd=root, text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source drift', result.stderr)
            self.assertNotIn('PASS_SYNTHETIC_LAYOUT', result.stdout)


if __name__ == '__main__':
    unittest.main()
