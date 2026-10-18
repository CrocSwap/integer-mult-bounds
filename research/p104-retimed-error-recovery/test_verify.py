"""Behavioral failures, grid boundaries and a relocated source-bound replay."""
import copy
from fractions import Fraction as Q
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

P = Path(__file__).resolve().parent
V = types.ModuleType('recovery_test_verify')
V.__file__ = str(P / 'verify.py')
exec(compile((P / 'verify.py').read_bytes(), V.__file__, 'exec'), V.__dict__)


class RecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = V.load()
        cls.result = json.loads((P / 'RESULT.json').read_text())

    def test_grid_recovery_and_strict_radius(self):
        for spacing in (Q(1, 128), Q(1, 2 ** 30), Q(3, 8)):
            for k in range(-5, 6):
                exact = k * spacing
                for e in (Q(-49, 100), Q(0), Q(49, 100)):
                    self.assertEqual(V.M.nearest(exact + e * spacing, spacing), exact)
                with self.assertRaisesRegex(ValueError, 'ambiguity'):
                    V.M.nearest(exact + spacing / 2, spacing)
                self.assertNotEqual(V.M.nearest(exact + Q(51, 100) * spacing, spacing), exact)

    def test_exact_feedback_and_private_threshold(self):
        J, K = Q(5534), Q(6047, 4)
        self.assertLess(J + K, 2 ** 13)
        self.assertGreater(J, 2 ** 12)  # Sufficient formula only, not a precision floor.
        for f in (0, 1, 10):
            for h in (0, 1, 20):
                for depth in (1, 2, 3, 100):
                    F = f + (9 * depth + 1) // 2 + 2
                    u = Q(1, 2 ** (F + h + 9))
                    B = 2 ** h
                    E = u * B * J / (1 - u * K)
                    private = u * (Q(317, 2) * B + 22 * E)
                    self.assertLess(private, Q(1, 2 ** (F + 1)))
                    u = Q(1, 2 ** (F + h + 14))
                    self.assertLess(u * B * J / (1 - u * K), Q(1, 2 ** (F + 1)))

    def test_cleanup_and_chart_mutants(self):
        # Removing a cleanup ADD leaves an ideally nonzero private erasure.
        first_erase = next(i for i, e in enumerate(self.word['program']) if e[0] == 'erase')
        cleanup = max(i for i, e in enumerate(self.word['program'][:first_erase])
                      if e[0] == 'add' and e[1] == 'C')
        mutant = copy.deepcopy(self.word)
        del mutant['program'][cleanup]
        with self.assertRaisesRegex(ValueError, 'nonzero ideal erase'):
            V.M.replay(mutant)
        mutant = copy.deepcopy(self.word)
        first_add = next(e for e in mutant['program'] if e[0] == 'add')
        first_add[-1] = [1]
        with self.assertRaisesRegex(ValueError, 'ADD chart'):
            V.M.replay(mutant)

    def test_endpoint_coefficient_mutant(self):
        mutant = copy.deepcopy(self.word)
        last = next(e for e in reversed(mutant['program']) if e[0] == 'add')
        last[3] = str(Q(last[3]) + 1)
        with self.assertRaisesRegex(ValueError, 'source complete ideal map'):
            V.certificate(mutant)

    def test_private_residuals_and_escaped_errors(self):
        response = V.M.replay(self.word)
        controls = V.recovery_controls(self.word, response)
        self.assertEqual(controls['private_residuals'], 8)
        self.assertEqual(controls['half_grid_rejections'], 2)
        self.assertNotEqual(Q(controls['escaped_private'][2]), 0)

    def test_relocated_replay_and_corruption(self):
        with tempfile.TemporaryDirectory(prefix='p104-recovery-export-') as directory:
            root = Path(directory)
            package = root / 'research' / P.name
            shutil.copytree(P, package, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            pins = json.loads((P / 'SOURCES.json').read_text())
            for pin in pins['files']:
                if pin['usage'] == 'input':
                    target = root / pin['path']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(V.ROOT / pin['path'], target)
            command = [sys.executable, '-I', '-O', '-B', str(package / 'verify.py')]
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            good = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120)
            self.assertEqual(good.returncode, 0, good.stderr)
            after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            receipt = package / 'RESULT.json'
            original = receipt.read_bytes()
            bad = json.loads(original)
            bad['peaks']['J']['value'] = '5533'
            receipt.write_text(json.dumps(bad))
            failed = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('complete receipt mismatch', failed.stderr)
            receipt.write_bytes(original)
            source = root / 'research/p104-dual-add-retiming/WORD.json'
            source.write_bytes(source.read_bytes() + b' ')
            failed = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('source SHA256', failed.stderr)


if __name__ == '__main__':
    unittest.main()
