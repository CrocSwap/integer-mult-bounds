#!/usr/bin/env python3
"""Failure controls for the fixed mathematical claims, not implementation mirrors."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
INPUTS = [
    'research/community-frontier1094-audit/ASSEMBLY.json',
    'research/e8-bit-p111-tuned/tune/EXPECTED.json',
]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.primary = load('mixed_primary', PKG/'verify.py')
        cls.oracle = load('mixed_oracle', PKG/'oracle.py')
        cls.receipt = json.loads((PKG/'RESULT.json').read_text())

    def command(self, path, optimized=False, args=()):
        argv = [sys.executable, '-I', '-B']
        if optimized:
            argv.append('-O')
        return subprocess.run(argv+[str(path), *args], capture_output=True, text=True, timeout=60)

    def copied_root(self, target):
        package = target/'research'/PKG.name
        package.parent.mkdir(parents=True)
        shutil.copytree(PKG, package, ignore=shutil.ignore_patterns('__pycache__'))
        for item in INPUTS:
            dst = target/item
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/item, dst)
        return package

    def test_complete_positive_and_optimized(self):
        for script in ('verify.py', 'oracle.py'):
            normal = self.command(PKG/script)
            optimized = self.command(PKG/script, optimized=True)
            self.assertEqual(normal.returncode, 0, normal.stderr)
            self.assertEqual(optimized.returncode, 0, optimized.stderr)
            self.assertEqual(normal.stdout, optimized.stdout)

    def test_mathematical_receipt_corruptions(self):
        # Every mutant changes a mathematical or scope claim; both engines reject.
        mutations = [
            ('mass', lambda d: d['mixed_overhead']['bit_endpoint'].__setitem__('mass', 4446)),
            ('minimizer', lambda d: d['mixed_overhead']['bit_endpoint']['partition'].__setitem__('51', 86)),
            ('adjacency', lambda d: d['mixed_overhead']['next_complex_endpoint'].__setitem__('next_mass', 4624)),
            ('exponent', lambda d: d['mixed_overhead']['bit_endpoint'].__setitem__('endpoint', '1/1000')),
            ('strict sign', lambda d: d['mixed_overhead']['bit_endpoint'].__setitem__('pass_residual', ['1/1000', '1/500'])),
            ('pure removal', lambda d: d['bit_pure_removal'].__setitem__('changes', 648)),
            ('bit reblocking', lambda d: d['bit_zero_mass_reblocking'].__setitem__('changes', 2247)),
            ('target', lambda d: d['assembly'].__setitem__('target', '1/100')),
            ('finite grid', lambda d: d['assembly'].__setitem__('full_gain', '1/100')),
            ('quantized improvement', lambda d: d['quantized_improvement'].__setitem__('conditional_recipe_kappa', '1/100')),
            ('scope', lambda d: d.__setitem__('no_new_kappa', False)),
        ]
        with tempfile.TemporaryDirectory(prefix='mixed-receipt-') as folder:
            root = Path(folder)
            package = self.copied_root(root)
            for label, mutate in mutations:
                with self.subTest(label=label):
                    value = copy.deepcopy(self.receipt)
                    mutate(value)
                    (package/'RESULT.json').write_text(json.dumps(value))
                    result = self.command(package/'verify.py')
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('fixed RESULT.json mismatch', result.stderr)
                    with self.assertRaises(ValueError):
                        self.oracle.check_receipt(value)

    def test_source_and_missing_receipt(self):
        with tempfile.TemporaryDirectory(prefix='mixed-inputs-') as folder:
            root = Path(folder)
            package = self.copied_root(root)
            for source in INPUTS:
                path = root/source
                original = path.read_bytes()
                path.write_bytes(original+b' ')
                for script, reason in [('verify.py', 'source SHA256'), ('oracle.py', 'oracle input pin')]:
                    result = self.command(package/script)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(reason, result.stderr)
                path.write_bytes(original)
            (package/'RESULT.json').unlink()
            for script in ('verify.py', 'oracle.py'):
                result = self.command(package/script)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((package/'RESULT.json').exists())
            generated = self.command(package/'verify.py', args=('--write',))
            self.assertEqual(generated.returncode, 0, generated.stderr)
            self.assertEqual((package/'RESULT.json').read_bytes(), (PKG/'RESULT.json').read_bytes())

    def test_arithmetic_defects_reach_algebraic_controls(self):
        source = (PKG/'verify.py').read_text()
        defects = [
            ('upper root rounds down', 'return r + (r*r != n)', 'return r'),
            ('truncate exponent', 'n // a.denominator, ceildiv(n, a.denominator)',
             'n // a.denominator, n // a.denominator'),
        ]
        with tempfile.TemporaryDirectory(prefix='mixed-kernel-') as folder:
            for i, (label, before, after) in enumerate(defects):
                with self.subTest(label=label):
                    self.assertEqual(source.count(before), 1)
                    path = Path(folder)/('bad'+str(i)+'.py')
                    path.write_text(source.replace(before, after))
                    mutant = load('mixed_defect_'+str(i), path)
                    with self.assertRaisesRegex(ValueError, 'integer-power oracle'):
                        mutant.controls()
                    # Isolate the algebraic-fixture stage, then actually remove
                    # its named detector. The defective implementation now passes
                    # that stage: rejection above depends on the intended check.
                    isolated = path.read_text().replace('    x=Q(73)\n',
                                                        '    return count\n    x=Q(73)\n')
                    predicate = "need(lo**den <= x**num <= hi**den, 'integer-power oracle')"
                    self.assertEqual(isolated.count(predicate), 1)
                    unchecked_path = Path(folder)/('unchecked'+str(i)+'.py')
                    unchecked_path.write_text(isolated.replace(predicate, 'pass'))
                    unchecked = load('mixed_unchecked_'+str(i), unchecked_path)
                    self.assertEqual(unchecked.controls(), 728)
                    sample = mutant.power(mutant.Q(2), mutant.Q(1, 2), bits=4, depth=3) if i == 0 else \
                             mutant.power(mutant.Q(73), mutant.Q(1, 3), bits=20, depth=3)
                    self.assertTrue(sample[1]**(2 if i == 0 else 3) < (2 if i == 0 else 73))

    def test_contract_premises(self):
        v = self.primary
        for call in (
            lambda: v.power(v.Q(1, 2), v.Q(1, 3)),
            lambda: v.power(2, -v.Q(1, 3)),
            lambda: v.residual({0: 1}, 73, 14336, v.Q(1, 1000)),
            lambda: v.residual({73: 1}, 73, 14336, v.Q(1, 1000)),
            lambda: v.residual({1: -1}, 73, 14336, v.Q(1, 1000)),
            lambda: v.partition(5, 0),
        ):
            with self.assertRaises(ValueError):
                call()
        # Equivalent unordered histogram and harmless zero multiplicity.
        a = v.Q(1, 1000)
        self.assertEqual(v.residual({1: 3, 8: 2}, 73, 14336, a),
                         v.residual({8: 2, 51: 0, 1: 3}, 73, 14336, a))
        asm, _ = v.check_sources()
        h = {int(r): n for r, n in asm['complex_profile'].items()}
        h[8] -= 576
        # A mass below the maximum does NOT admit every partition.
        self.assertLess(sum(r*n for r, n in {1: 4444}.items()), 4445)
        self.assertGreater(v.residual(v.combined(h, {1: 4444}), 73, 14336,
                                      v.Q(asm['bit_lower']))[0], 0)

    def test_read_only_relocation(self):
        with tempfile.TemporaryDirectory(prefix='mixed read only ') as folder:
            root = Path(folder)
            package = self.copied_root(root)
            files = [p for p in root.rglob('*') if p.is_file()]
            directories = [p for p in root.rglob('*') if p.is_dir()]
            before = {p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            try:
                for path in files:
                    path.chmod(0o444)
                for path in sorted(directories, key=lambda p: len(p.parts), reverse=True):
                    path.chmod(0o555)
                for script in ('verify.py', 'oracle.py'):
                    result = self.command(package/script, optimized=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                after = {p.relative_to(root): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in root.rglob('*') if p.is_file()}
                self.assertEqual(before, after)
            finally:
                for path in directories:
                    path.chmod(0o755)
                for path in files:
                    path.chmod(0o644)


if __name__ == '__main__':
    unittest.main()
