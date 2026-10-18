"""Behavioral controls for the deterministic native collector counterexample."""
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
spec = importlib.util.spec_from_file_location('rounded_collector_audit', HERE / 'verify.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class CollectorControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.local, cls.recipes = audit.load_inputs()

    def test_quantizer_ties_and_gaussian_units(self):
        # Independently specified half-integer ties, including negative values.
        self.assertEqual([audit.nearest_even(n, 2) for n in range(-7, 8)],
                         [-4, -3, -2, -2, -2, -1, 0, 0, 0, 1, 2, 2, 2, 3, 4])
        for real in range(-20, 21):
            for phase in range(4):
                z = (real, 7)
                q = tuple(audit.nearest_even(n, 16) for n in z)
                rotated = audit.rotate(z, phase)
                self.assertEqual(tuple(audit.nearest_even(n, 16) for n in rotated),
                                 audit.rotate(q, phase))

    def test_exact_and_strict_rounded_erase(self):
        dirty = audit.basis(0, 17, 4)
        residue, _, _ = audit.collector(self.local, self.recipes, dirty, strict_erase=True)
        self.assertFalse(any(z != audit.ZERO for z in residue[0]))
        with self.assertRaisesRegex(ValueError, 'strict zero erase'):
            audit.collector(self.local, self.recipes, dirty, 4, strict_erase=True)
        # The same collector and input pass when this output grid is refined.
        audit.collector(self.local, self.recipes, dirty, 8, strict_erase=True)

    def test_wrong_cleanup_fails_exact_control(self):
        broken = copy.deepcopy(self.local)
        broken[-2][3] = '1'
        with self.assertRaisesRegex(ValueError, 'strict zero erase'):
            audit.collector(broken, self.recipes, audit.basis(0), strict_erase=True)

    def test_native_global_phase_is_observable(self):
        broken = copy.deepcopy(self.recipes)
        broken[1]['left']['phase'] = (broken[1]['left']['phase'] + 1) % 4
        with self.assertRaisesRegex(ValueError, 'exact native round trip'):
            audit.verify((self.local, broken))

    def test_subthreshold_grid_is_not_the_symbolic_family(self):
        # b >= 4 matters: U delta_0 itself is not on a coarser output grid.
        image = audit.native(*audit.basis(0), self.recipes[0])
        self.assertNotEqual(audit.quantize(*image, 3), image)

    def test_git_free_cli_pins_receipt_and_output_refusal(self):
        with tempfile.TemporaryDirectory() as folder:
            export = Path(folder) / 'export'
            shutil.copytree(HERE, export, ignore=shutil.ignore_patterns('__pycache__'))
            def run(*args):
                return subprocess.run([sys.executable, '-I', '-O', '-B', str(export / 'verify.py'), *args],
                                      capture_output=True, text=True, timeout=20, cwd=folder)
            output = Path(folder) / 'receipt.json'
            positive = run('--out', str(output))
            self.assertEqual(positive.returncode, 0, positive.stderr)
            self.assertEqual(json.loads(output.read_text()), json.loads((HERE / 'RESULT.json').read_text()))
            self.assertNotEqual(run('--out', str(output)).returncode, 0)
            word = export / 'inputs/WORD.json'
            word.write_bytes(word.read_bytes() + b' ')
            drift = run()
            self.assertNotEqual(drift.returncode, 0)
            self.assertIn('source SHA256', drift.stderr)
            shutil.copyfile(HERE / 'inputs/WORD.json', word)
            result = json.loads((export / 'RESULT.json').read_text())
            result['column_support'] = 127
            (export / 'RESULT.json').write_text(json.dumps(result))
            mismatch = run()
            self.assertNotEqual(mismatch.returncode, 0)
            self.assertIn('receipt equality', mismatch.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
