"""Behavioral controls for the numerical contract; standard-library only."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arithmetic
import verify


class NumericalTests(unittest.TestCase):
    def test_signed_nearest_even(self):
        for value in range(-1001, 1002):
            self.assertEqual(arithmetic.nearest_half(value), round(Fraction(value, 2)))

    def test_stage_unitarity_and_local_defects(self):
        # Exhaust every Gaussian pair over {-1,0,1} at the first C stage.
        import itertools
        for a, b, c, d in itertools.product((-1, 0, 1), repeat=4):
            vector = [(a * 2, b * 2), (c * 2, d * 2)]
            before = verify.norm2(vector)
            self.assertEqual(arithmetic.rounded_stage(vector, 0), 0)
            self.assertEqual(verify.norm2(vector), before)
            vector = [(a, b), (c, d)]
            self.assertLessEqual(arithmetic.rounded_stage(vector, 0), 4)

    def test_precision_and_arithmetic_mutants(self):
        native, _ = verify.inputs()
        recipe = native['transports'][0]['recipe']
        plans = arithmetic.wrapper_plan(recipe['left']), arithmetic.wrapper_plan(recipe['right'])
        basis = verify.inverse_wrapper_basis(plans[1])
        exact = verify.oracle(basis, recipe)
        with patch.object(arithmetic, 'working_precision', return_value=0):
            value, F, _ = arithmetic.execute(basis, 0, 8, recipe, plans)
        err, ef = verify.error_squared(value, F, exact, recipe['rank'])
        self.assertFalse(verify.relative_ok(err, ef, basis, 0, 8))
        # Execute a real alternate kernel with one numerator sign corrupted.
        source = (HERE / 'arithmetic.py').read_text(encoding='utf-8')
        old = 'a - b + c + d, b + a + d - c'
        self.assertEqual(source.count(old), 1)
        namespace = {}
        exec(compile(source.replace(old, 'a + b + c + d, b + a + d - c'), '<mutated kernel>', 'exec'), namespace)
        vector = [(1, 1)] + [(0, 0)] * 511
        value, F, _ = namespace['execute'](vector, 0, 8, recipe, plans)
        exact = verify.oracle(vector, recipe)
        err, ef = verify.error_squared(value, F, exact, recipe['rank'])
        self.assertFalse(verify.relative_ok(err, ef, vector, 0, 8))

    def test_export_integrity_and_read_only_replay(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / 'research' / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            pins = json.loads((HERE / 'SOURCES.json').read_text())
            for pin in pins['files']:
                if pin['usage'] == 'input':
                    dest = root / pin['path']
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(HERE.parents[1] / pin['path'], dest)
            def run(*args):
                return subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py'), *args],
                                      cwd=root, text=True, capture_output=True, timeout=180)
            def hashes():
                return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in root.rglob('*') if p.is_file()}
            before = hashes()
            result = run()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(hashes(), before)
            receipt = package / 'RESULT.json'
            data = json.loads(receipt.read_text())
            data['exact_columns'] = True
            receipt.write_text(json.dumps(data))
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('complete typed receipt', result.stderr)
            source = root / 'research/p104-dual-add-retiming/NATIVE.json'
            source.write_bytes(source.read_bytes() + b' ')
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source SHA256', result.stderr)

    def test_exclusive_output(self):
        # Exercise the actual writer while avoiding another complete oracle run.
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'receipt.json'
            path.write_text('occupied')
            with patch.object(sys, 'argv', ['verify.py', '--write-result', str(path)]):
                with patch.object(verify, 'calculate', return_value={}):
                    with self.assertRaises(FileExistsError):
                        verify.main()
            self.assertEqual(path.read_text(), 'occupied')


if __name__ == '__main__':
    unittest.main()
