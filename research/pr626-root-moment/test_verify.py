#!/usr/bin/env python3
"""Disposable-package controls for the independent moment checker.

Prepared for arkfx with substantial OpenAI Codex assistance; Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class PackageControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='root moment ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / 'research/pr626-root-moment'
        self.package.mkdir(parents=True)
        for name in ('verify.py', 'SOURCES.json', 'CERTIFICATE.json'):
            shutil.copyfile(HERE / name, self.package / name)
        self.sources = json.loads((HERE / 'SOURCES.json').read_text())
        for item in self.sources['files'].values():
            target = self.root / item['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / item['path'], target)

    def run_checker(self, optimized=False):
        options = ['-I', '-B'] + (['-O'] if optimized else [])
        return subprocess.run([sys.executable, *options, str(self.package / 'verify.py')],
                              cwd=self.root, capture_output=True, text=True, timeout=30)

    def test_minimal_offline_package_normal_and_optimized(self):
        normal, optimized = self.run_checker(), self.run_checker(True)
        self.assertEqual(normal.returncode, 0, normal.stderr)
        self.assertEqual(optimized.returncode, 0, optimized.stderr)
        self.assertEqual(normal.stdout, optimized.stdout)
        self.assertIn('PASS_PR626_ROOT_MOMENT', normal.stdout)

    def test_five_source_corruptions_are_rejected(self):
        for label, item in self.sources['files'].items():
            with self.subTest(source=label):
                path = self.root / item['path']
                raw = path.read_bytes()
                path.write_bytes(raw + b' ')
                result = self.run_checker()
                path.write_bytes(raw)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('source hash: ' + label, result.stderr)

    def test_certificate_corruption_is_rejected(self):
        path = self.package / 'CERTIFICATE.json'
        certificate = json.loads(path.read_text())
        certificate['endpoints'][0]['accept'] = False
        path.write_text(json.dumps(certificate), encoding='utf-8')
        result = self.run_checker(True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('certificate differs', result.stderr)

    def test_actual_arithmetic_and_accounting_mutants(self):
        path = self.package / 'verify.py'
        original = path.read_text(encoding='utf-8')
        mutants = [
            ('root rounding', 'upper += upper * upper < hi * scale', 'upper += 0',
             'integer-power oracle'),
            ('exponent truncation',
             'upper_n = ceil_div(exponent.numerator * denominator, exponent.denominator)',
             'upper_n = lower_n', 'integer-power oracle'),
            ('no surcharge', 'if surcharge:\n', 'if False:\n', 'strict endpoint: conservative'),
            ('omit idle', "profile = local + Counter(profile_dict(idle['rank_profile']))",
             'profile = local', 'complete profile'),
            ('physical denominator', 'weight = Q(r * count, m * live)',
             'weight = Q(r * count, m * 7670)', 'strict endpoint: native'),
        ]
        for name, old, new, reason in mutants:
            with self.subTest(mutant=name):
                self.assertEqual(original.count(old), 1)
                path.write_text(original.replace(old, new), encoding='utf-8')
                result = self.run_checker(True)
                self.assertNotEqual(result.returncode, 0, name)
                self.assertIn(reason, result.stderr)
        path.write_text(original, encoding='utf-8')


if __name__ == '__main__':
    unittest.main(verbosity=2)
