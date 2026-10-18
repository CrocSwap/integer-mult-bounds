#!/usr/bin/env python3
"""Public-CLI source, receipt and actual guard-removal controls. Apache-2.0."""
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


@contextmanager
def exported():
    with tempfile.TemporaryDirectory(prefix='live-row-divisor-test-') as temporary:
        destination = Path(temporary)/'standalone'
        shutil.copytree(HERE, destination, ignore=shutil.ignore_patterns('__pycache__'))
        try:
            yield destination
        finally:
            for path in [destination, *destination.rglob('*')]:
                path.chmod(0o755 if path.is_dir() else 0o644)


def run(directory, optimized=False, extra=()):
    command = [sys.executable, '-I', '-B']
    if optimized:
        command.append('-O')
    command.extend([str(directory/'verify.py'), *map(str, extra)])
    return subprocess.run(command, cwd=directory.parent, text=True,
                          capture_output=True, timeout=30)


class PublicContract(unittest.TestCase):
    def check_failure(self, mutate, expected):
        for optimized in (False, True):
            with self.subTest(optimized=optimized), exported() as directory:
                mutate(directory)
                result = run(directory, optimized)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout+result.stderr)
                self.assertNotIn('PASS_SELECTED_LIVE_ROW_DIVISOR factor=', result.stdout)

    def test_read_only_git_free_positive(self):
        with exported() as directory:
            for path in [*directory.rglob('*'), directory]:
                path.chmod(0o555 if path.is_dir() else 0o444)
            for optimized in (False, True):
                result = run(directory, optimized)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('PASS_SELECTED_LIVE_ROW_DIVISOR factor=9475^D', result.stdout)
            self.assertFalse(list(directory.rglob('__pycache__')))

    def test_changed_source(self):
        def mutate(d):
            p=d/'sources/pr2234/PROOF.md'
            p.write_text(p.read_text()+'\nchanged source\n')
        self.check_failure(mutate, 'source size mismatch')

    def test_changed_source_identity(self):
        def mutate(d):
            p=d/'PREDECESSORS.json'; data=json.loads(p.read_text())
            data[0]['commit']='0'*40
            p.write_text(json.dumps(data))
        self.check_failure(mutate, 'predecessor manifest changed')

    def test_missing_receipt(self):
        self.check_failure(lambda d: (d/'RESULT.json').unlink(), 'FileNotFoundError')

    def test_changed_coefficient(self):
        def mutate(d):
            p=d/'RESULT.json'; data=json.loads(p.read_text())
            data['selected']['removed_factor_per_depth']=9474
            p.write_text(json.dumps(data))
        self.check_failure(mutate, 'stored receipt differs')

    def test_boolean_receipt_drift(self):
        def mutate(d):
            p=d/'RESULT.json'; data=json.loads(p.read_text())
            data['selected']['private_inventory']=True
            p.write_text(json.dumps(data))
        self.check_failure(mutate, 'stored receipt differs')

    def test_guard_removal_is_detected(self):
        def mutate(d):
            p=d/'verify.py'; text=p.read_text()
            before='need(path_join(packet, *fields, t) == row, "ancestor/row coordinate changed")'
            self.assertEqual(text.count(before), 1)
            p.write_text(text.replace(before, 'need(True, "ancestor/row coordinate changed")'))
        self.check_failure(mutate, 'accepted defect: multiset_only_row_restoration')

    def test_equivalent_receipt_serialization(self):
        with exported() as directory:
            path=directory/'RESULT.json'
            path.write_text(json.dumps(json.loads(path.read_text()), sort_keys=True))
            self.assertEqual(run(directory, True).returncode, 0)

    def test_explicit_generation_never_overwrites(self):
        with exported() as directory:
            output=directory.parent/'new-result.json'
            self.assertEqual(run(directory, True, ['--write-receipt', output]).returncode, 0)
            content=output.read_bytes()
            second=run(directory, True, ['--write-receipt', output])
            self.assertNotEqual(second.returncode, 0)
            self.assertIn('FileExistsError', second.stderr)
            self.assertEqual(content, output.read_bytes())


if __name__ == '__main__':
    unittest.main()
