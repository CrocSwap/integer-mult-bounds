"""Behavioral controls for the adaptive collision; Apache-2.0."""
from copy import deepcopy
from fractions import Fraction
import gzip
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
v = types.ModuleType('collision_verifier')
v.__file__ = str(HERE / 'verify.py')
exec(compile((HERE / 'verify.py').read_bytes(), v.__file__, 'exec'), v.__dict__)


class CollisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module, cls.local, cls.recipes = v.inputs()

    def test_fraction_first_stage_collision(self):
        """A separate Fraction/ties-even calculation, rather than kernel reuse."""
        for b in (0, 1, 8, 64, 256):
            A = 1 << (b+7)
            for sign in (-1, 1):
                low = tuple(round(Fraction(sign*x*A, 2)) for x in (1, 1, 1, -1))
                high = tuple(round(Fraction(sign*x*(A+1), 2)) for x in (1, 1, 1, -1))
                self.assertEqual(low, high)
                vector = [v.ZERO]*512
                vector[0] = sign*(A+1), 0
                self.assertEqual(self.module.rounded_stage(vector, 0), 4)
                self.assertEqual(tuple(vector[0]+vector[1]), high)

    def test_actual_strict_erase_rejects_and_finer_policy_restores(self):
        b, f = 64, 19
        basis = v.inverse_basis(self.module, self.recipes[0])
        A = 1 << (b+7)
        dirty = ([(a*(A+1), c*(A+1)) for a, c in basis], f)
        with self.assertRaisesRegex(ValueError, 'strict private zero'):
            v.collector(self.module, self.local, self.recipes, dirty, b, strict=True)
        residue, _, _ = v.collector(self.module, self.local, self.recipes, dirty, b+7, strict=True)
        self.assertTrue(v.equal(residue, ([v.ZERO]*512, 0)))

    def test_full_fixture_and_wrong_cleanup(self):
        v.fixture(self.module, self.local, self.recipes, 8, 300)
        changed = deepcopy(self.local)
        changed[13][3] = '1'
        with self.assertRaisesRegex(ValueError, 'strict private zero'):
            v.fixture(self.module, changed, self.recipes, 8, 300)

    def test_native_phase_and_occurrence_controls(self):
        recipes = deepcopy(self.recipes)
        recipes[1]['left']['phase'] = (recipes[1]['left']['phase']+1) % 4
        with self.assertRaisesRegex(ValueError, 'complete native inverse column'):
            v.check_inverse(self.module, recipes)
        word = v.read_json((v.ROOT / 'research/p104-rounded-collector/inputs/WORD.json').read_bytes())
        native = v.read_json(gzip.decompress(
            (v.ROOT / 'research/p104-rounded-collector/inputs/NATIVE.json.gz').read_bytes()))
        word['program'][2031][4] = 6
        with self.assertRaisesRegex(ValueError, 'literal native event'):
            v.bind(word, native)
        word['program'][2031][4] = 7
        word['program'][0][2] = [387]
        with self.assertRaisesRegex(ValueError, 'prefix transport frame'):
            v.bind(word, native)

    def test_relative_defect_rejects_zero_input_error(self):
        zero = ([v.ZERO]*512, 0)
        wrong = [(1, 0)]+[v.ZERO]*511, 0
        self.assertFalse(v.relative_ok(wrong, zero, zero, 0))
        self.assertTrue(v.relative_ok(zero, zero, zero, 256))

    def test_diagnostic_preserving_collision_cube(self):
        result = v.check_cube(self.module, self.local, self.recipes)
        self.assertEqual(result['minimum_history_bits'], 256)
        self.assertEqual(result['minimum_extra_bits_given_diagnostics'], 252)
        for j in range(256):
            A = 128
            low = [v.ZERO]*512
            low[2*j] = A, 0
            high = low.copy()
            high[2*j] = A+1, 0
            self.module.rounded_stage(low, 0)
            self.module.rounded_stage(high, 0)
            self.assertEqual(low, high)

    def test_typed_complete_receipt_and_duplicate_keys(self):
        receipt = v.read_json((HERE / 'RESULT.json').read_bytes())
        altered = deepcopy(receipt)
        altered['fixtures'][0]['residual_norm2_numerator'] = True
        with self.assertRaisesRegex(ValueError, 'typed receipt'):
            v.compare(receipt, altered)
        altered = deepcopy(receipt)
        altered['fixtures'][-1]['return_grid'] += 1
        with self.assertRaisesRegex(ValueError, 'receipt value'):
            v.compare(receipt, altered)
        with self.assertRaisesRegex(ValueError, 'duplicate JSON'):
            v.read_json('{"x":1,"x":2}')

    def test_executable_pin_before_execution(self):
        pins = v.read_json((HERE / 'SOURCES.json').read_bytes())
        with tempfile.TemporaryDirectory(prefix='.source-control-', dir=HERE) as folder:
            root = Path(folder)
            for pin in pins['files']:
                if pin['usage'] == 'input':
                    target = root / pin['path']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(v.ROOT / pin['path'], target)
            target = root / 'research/p104-rounded-native-child/arithmetic.py'
            target.write_text('raise RuntimeError("MUTANT EXECUTED")\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'source SHA256'):
                v.inputs(root)

    def test_git_free_optimized_read_only_export_and_occupied_output(self):
        pins = v.read_json((HERE / 'SOURCES.json').read_bytes())
        with tempfile.TemporaryDirectory(prefix='.export-control-', dir=HERE) as folder:
            root = Path(folder)
            package = root / 'research/p104-adaptive-rounding-collision'
            package.mkdir(parents=True)
            for name in ('verify.py', 'SOURCES.json', 'RESULT.json'):
                shutil.copyfile(HERE / name, package / name)
            for pin in pins['files']:
                if pin['usage'] == 'input':
                    target = root / pin['path']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(v.ROOT / pin['path'], target)
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            result = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py')],
                                    cwd=root, capture_output=True, text=True, timeout=180)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            self.assertIn('PASS_P104_ADAPTIVE_ROUNDING_COLLISION', result.stdout)
            after = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
        with mock.patch.object(v, 'calculate', return_value={'result': 1}):
            with mock.patch.object(sys, 'argv', ['verify.py', '--write-result', str(HERE/'RESULT.json')]):
                with self.assertRaises(FileExistsError):
                    v.main()


if __name__ == '__main__':
    unittest.main()
