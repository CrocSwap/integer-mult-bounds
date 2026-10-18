#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Receipt and read-only CLI controls for the independent full-main replay."""
import contextlib
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('full_replay', HERE / 'full_replay.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


def snapshot(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob('*') if path.is_file()}


@contextlib.contextmanager
def relocated():
    """Copy only declared files; no Git history, network, or parent auditor."""
    with tempfile.TemporaryDirectory(prefix='pr1293-full-replay-test-') as temporary:
        root = Path(temporary) / 'repo'
        package = root / 'research/pr1293-log-enclosure-audit'
        (package / 'vendor').mkdir(parents=True)
        for name in ('full_replay.py', 'FULL-REPLAY.json', 'vendor/pr1293_verify.py'):
            shutil.copyfile(HERE / name, package / name)
        for name in replay.INPUTS:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        yield root, package, Path(temporary) / 'regenerated.json'


def run_export(root, package, output=None):
    command = [sys.executable, '-I', '-O', '-B', str(package / 'full_replay.py')]
    if output is not None:
        command.extend(['--write-receipt', str(output)])
    before = snapshot(root)
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120)
    if snapshot(root) != before:
        raise AssertionError('full replay changed its source/input/receipt tree')
    return result


class FullReplayControls(unittest.TestCase):
    def test_clean_optimized_source_export(self):
        with relocated() as (root, package, _):
            result = run_export(root, package)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('MATCH FULL-REPLAY.json', result.stdout)
            self.assertIn('PASS_PR1293_FULL_REPLAY', result.stdout)

    def test_missing_receipt_rejected(self):
        with relocated() as (root, package, _):
            (package / 'FULL-REPLAY.json').unlink()
            result = run_export(root, package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('FileNotFoundError', result.stderr)
            self.assertIn('FULL-REPLAY.json', result.stderr)

    def test_duplicate_receipt_key_rejected(self):
        with relocated() as (root, package, _):
            path = package / 'FULL-REPLAY.json'
            path.write_text('{"invocations":41,' + path.read_text().lstrip()[1:])
            result = run_export(root, package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('duplicate JSON key', result.stderr)

    def test_receipt_type_changes_rejected(self):
        expected = replay.load_json((HERE / 'FULL-REPLAY.json').read_bytes())
        for key, value in (('invocations', 41.0), ('ambiguity_hits', False),
                           ('stdout_equal', 1), ('result_bytes_equal', 1.0)):
            with self.subTest(key=key):
                mutant = copy.deepcopy(expected)
                mutant[key] = value
                self.assertEqual(mutant, expected)  # Ordinary dict equality is insufficient.
                with self.assertRaisesRegex(ValueError, 'FULL-REPLAY.json differs'):
                    replay.check_receipt(expected, mutant)

    def test_stale_receipt_rejected(self):
        with relocated() as (root, package, _):
            path = package / 'FULL-REPLAY.json'
            data = json.loads(path.read_text())
            data['invocations'] = 40
            path.write_text(json.dumps(data))
            result = run_export(root, package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('FULL-REPLAY.json differs', result.stderr)

    def test_subject_drift_rejected(self):
        with relocated() as (root, package, _):
            path = package / 'vendor/pr1293_verify.py'
            path.write_bytes(path.read_bytes() + b'\n')
            result = run_export(root, package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source pin mismatch', result.stderr)

    def test_each_input_drift_rejected(self):
        for name in replay.INPUTS:
            with self.subTest(input=name), relocated() as (root, package, _):
                path = root / name
                path.write_bytes(path.read_bytes() + b'\n')
                result = run_export(root, package)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('source pin mismatch', result.stderr)

    def test_internal_receipt_output_rejected(self):
        with relocated() as (root, package, _):
            target = package / 'forbidden.json'
            result = run_export(root, package, target)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('receipt must be external JSON', result.stderr)
            self.assertFalse(target.exists())

    def test_explicit_external_regeneration(self):
        with relocated() as (root, package, output):
            expected = (package / 'FULL-REPLAY.json').read_bytes()
            (package / 'FULL-REPLAY.json').unlink()
            result = run_export(root, package, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_bytes(), expected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
