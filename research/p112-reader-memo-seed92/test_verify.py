#!/usr/bin/env python3
"""Failure-detection, fallback, relocation and optimized-execution controls.

Charan (@theon199), with substantial OpenAI Codex assistance. Apache-2.0.
"""

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
spec = importlib.util.spec_from_file_location('reader_memo_package', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def export(root):
    package = root / 'research/p112-reader-memo-seed92'
    package.mkdir(parents=True)
    for name in ('verify.py', 'SOURCES.json'):
        shutil.copyfile(HERE / name, package / name)
    for name in v.LIVE_INPUTS:
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(v.ROOT / name, destination)
    return package


class ReaderMemoTests(unittest.TestCase):
    def test_mathematical_fault_and_mutation_controls(self):
        controls = v.controls(v.ROOT)
        self.assertEqual(len(controls), 13)
        self.assertEqual(len(set(controls)), 13)

    def test_outside_envelope_retains_source_behavior(self):
        module = v.subject(v.ROOT)
        memo = v.ConstraintMemo(module.constraint_rows, module.evaluate)
        # A small arbitrary state uses the exact original builder, including
        # duplicated readers, signed labels and coefficient magnitudes != 1.
        data = {'X': [[1, -1], [0, 1], [-1, 0]], 'labels': [1, 2, -3]}
        for coefficients in ((1, 1), (2, -1), (0, 0)):
            spaces = [[1, 1], [2, 3]]
            self.assertEqual(memo(coefficients, data, spaces),
                             module.constraint_rows(coefficients, data, spaces))
        spaces = [[1, 1], [2, 3]]
        expected = module.constraint_rows((1, 1), data, spaces)
        lazy = {**data, 'labels': iter(data['labels'])}
        self.assertEqual(memo((1, 1), lazy, spaces), expected)
        # A malformed form is irrelevant when no reader is active; caching
        # must not turn the source's successful zero map into a type failure.
        data = module.build()
        spaces = [[1.0] * 8 for _ in range(8)]
        self.assertEqual(memo((0,) * 8, data, spaces), [0] * 224)

    def test_every_proof_section_is_compared(self):
        expected = v.read_json(v.ROOT / v.SUBJECT / 'RESULTS.json')
        mutations = []
        for field, value in (('geometry_sha256', '0' * 64),
                             ('reader_spaces', expected['reader_spaces'][::-1])):
            wrong = copy.deepcopy(expected)
            wrong[field] = value
            mutations.append(wrong)
        wrong = copy.deepcopy(expected)
        wrong['support_certificates'][0]['basis_ports'][0] = -1
        mutations.append(wrong)
        wrong = copy.deepcopy(expected)
        wrong['cases'][0]['rows_sha256'] = '0' * 64
        mutations.append(wrong)
        wrong = copy.deepcopy(expected)
        full = next(case for case in wrong['cases'] if 'kernel' in case)
        full['kernel'] = '0x0'
        mutations.append(wrong)
        wrong = copy.deepcopy(expected)
        full = next(case for case in wrong['cases'] if 'conflict_ports' in case)
        full['conflict_ports'].pop()
        mutations.append(wrong)
        wrong = copy.deepcopy(expected)
        wrong['controls']['rejected'].pop()
        mutations.append(wrong)
        for wrong in mutations:
            with self.assertRaisesRegex(ValueError, 'complete certificate mismatch'):
                v.compare(wrong, expected, 'mutated proof section')

    def test_source_drift_inventory_and_duplicate_json(self):
        manifest = v.read_json(HERE / 'SOURCES.json')
        with tempfile.TemporaryDirectory(prefix='reader source controls ') as temporary:
            root = Path(temporary)
            export(root)
            v.source_admission(root)
            source = root / v.SUBJECT / 'geometry.py'
            source.write_bytes(source.read_bytes() + b'\n# deliberate source mutation\n')
            with self.assertRaisesRegex(ValueError, 'source drift'):
                v.source_admission(root)
            duplicate = copy.deepcopy(manifest)
            duplicate['files'].append(next(p for p in duplicate['files']
                                           if p['usage'] == 'input'))
            with self.assertRaisesRegex(ValueError, 'complete live input inventory'):
                v.source_admission(root, duplicate)
            path = root / 'duplicate.json'
            path.write_text('{"rank":63,"rank":64}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                v.read_json(path)

    def test_optimized_read_only_relocation_and_preserved_output(self):
        with tempfile.TemporaryDirectory(prefix='reader relocation with spaces ') as temporary:
            outside = Path(temporary)
            root = outside / 'read only checkout'
            package = export(root)
            paths = list(root.rglob('*')) + [root]
            for path in paths:
                path.chmod(0o555 if path.is_dir() else 0o444)
            try:
                report = outside / 'report.json'
                completed = subprocess.run(
                    [sys.executable, '-I', '-O', '-B', str(package / 'verify.py'),
                     '--report', str(report)], text=True, capture_output=True, timeout=120)
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
                self.assertIn('PASS_P112_READER_MEMO', completed.stdout)
                result = v.read_json(report)
                self.assertEqual(result['sign_cases'], 3272)
                self.assertEqual(len(result['package_controls']), 13)
                # An actually optimized candidate worker executes the full
                # predecessor replay, not just an optimized parent driver.
                worker = outside / 'optimized-worker.json'
                completed = subprocess.run(
                    [sys.executable, '-I', '-O', '-B', str(package / 'verify.py'),
                     '--engine', 'memo', '--output', str(worker)],
                    text=True, capture_output=True, timeout=120)
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
                v.compare(v.read_json(worker)['certificate'],
                          v.read_json(root / v.SUBJECT / 'RESULTS.json'), 'optimized worker')
                saved = report.read_bytes()
                source = root / v.SUBJECT / 'geometry.py'
                source.chmod(0o644)
                source.write_bytes(source.read_bytes() + b'\n# deliberate failure\n')
                source.chmod(0o444)
                failed = subprocess.run(
                    [sys.executable, '-I', '-O', '-B', str(package / 'verify.py'),
                     '--report', str(report)], text=True, capture_output=True, timeout=120)
                self.assertNotEqual(failed.returncode, 0)
                self.assertIn('source drift', failed.stderr)
                self.assertEqual(report.read_bytes(), saved)
            finally:
                for path in paths:
                    path.chmod(0o755 if path.is_dir() else 0o644)


if __name__ == '__main__':
    unittest.main(verbosity=2)
