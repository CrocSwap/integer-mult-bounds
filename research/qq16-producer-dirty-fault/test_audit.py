#!/usr/bin/env python3
"""Behavioral controls for the source-bound F0 scalar fault audit.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class AuditBehavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # run_path reads the primary's current source without importing its .pyc.
        cls.api = runpy.run_path(str(HERE / 'verify.py'))
        cls.word = cls.api['expand'](cls.api['load'](ROOT))

    def cli(self, path, *args, optimized=False, success=True):
        command = [sys.executable, '-I', '-B']
        if optimized:
            command.append('-O')
        result = subprocess.run(command + [str(path), *args], capture_output=True,
                                text=True, timeout=30)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def export(self, directory):
        root = Path(directory)
        package = root / 'research' / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        sources = json.loads((HERE / 'SOURCES.json').read_text())
        for entry in sources['files']:
            if entry['usage'] == 'input':
                target = root / entry['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / entry['path'], target)
        return root, package

    def test_public_cli_and_optimized(self):
        for optimized in (False, True):
            result = self.cli(HERE / 'verify.py', optimized=optimized)
            self.assertIn('PASS_QQ16_PRODUCER_DIRTY_FAULT', result.stdout)
            result = self.cli(HERE / 'independent.py', optimized=optimized)
            self.assertIn('PASS_QQ16_DIRTY_FAULT_ADJOINT', result.stdout)

    def test_git_free_read_only_relocation(self):
        with tempfile.TemporaryDirectory(prefix='qq16-dirty-export-') as directory:
            root, package = self.export(directory)
            self.assertFalse((root / '.git').exists())
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.cli(package / 'verify.py', optimized=True)
            self.cli(package / 'independent.py', optimized=True)
            after = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)

    def test_receipt_change_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='qq16-dirty-receipt-') as directory:
            _, package = self.export(directory)
            self.cli(package / 'verify.py', '--write', success=False)
            receipt_path = package / 'RESULT.json'
            receipt = json.loads(receipt_path.read_text())
            receipt['all_480_helpers_exact_after_fault'] = 1
            receipt_path.write_text(json.dumps(receipt))
            result = self.cli(package / 'verify.py', optimized=True, success=False)
            self.assertIn('result receipt changed', result.stderr)
            receipt['unit_fault_final_response'][0][1] = '1/3'
            receipt_path.write_text(json.dumps(receipt))
            self.cli(package / 'independent.py', success=False)

    def test_input_changes_rejected_before_replay(self):
        for name in ('research/joint-query/certificate.json.gz',
                     'research/qq16-producer-defect-transfer/README.md'):
            with self.subTest(name=name), tempfile.TemporaryDirectory(prefix='qq16-dirty-source-') as directory:
                root, package = self.export(directory)
                target = root / name
                target.write_bytes(target.read_bytes() + b'changed')
                result = self.cli(package / 'verify.py', success=False)
                self.assertIn('source changed:', result.stderr)

    def test_cancellation_sign_and_fault_binding(self):
        word = copy.deepcopy(self.word)
        word[24438][1][3] = -4
        with self.assertRaisesRegex(ValueError, 'dirty restoration'):
            self.api['audit'](word)
        packet = self.api['load'](ROOT)
        packet['core_words']['forward'][24438][1][1] = ['L', 40]
        with self.assertRaisesRegex(ValueError, 'fault event binding'):
            self.api['expand'](packet)

    def test_small_fault_scaling_and_absolute_escape(self):
        Q = self.api['Q']
        run, unit, word = self.api['run'], self.api['unit'], self.word
        for magnitude in (Q(1, 4), Q(3, 2), Q(1024)):
            initial = unit(112)
            initial[359] = magnitude
            ideal = run(word, initial)
            for u in (Q(1, 2**120), Q(1, 2**200)):
                delta = 8 * u * magnitude
                actual = run(word, initial, (24438, delta))
                self.assertEqual(max(abs(a-b) for a,b in zip(actual[:224], ideal[:224])),
                                 4*u*magnitude)
                self.assertEqual(actual[224:], initial[224:])
            # Exact ADDs (eta=0), and fixed absolute errors, escape the T scaling.
            self.assertEqual(run(word, initial, (24438, Q(0))), ideal)
            actual = run(word, initial, (24438, Q(1, 16)))
            self.assertEqual(max(abs(a-b) for a,b in zip(actual[:224], ideal[:224])), Q(1, 32))


if __name__ == '__main__':
    unittest.main()
