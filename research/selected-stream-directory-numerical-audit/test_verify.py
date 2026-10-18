#!/usr/bin/env python3
"""External integrity and defect-sensitive controls. Apache-2.0."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

ROOT = Path(__file__).resolve().parent


def check(value, message):
    if not value:
        raise ValueError(message)


def load_verifier():
    module = types.ModuleType('audit_under_test')
    module.__file__ = str(ROOT / 'verify.py')
    exec(compile((ROOT / 'verify.py').read_bytes(), module.__file__, 'exec'), module.__dict__)
    return module


class Controls(unittest.TestCase):
    def export(self):
        temp = tempfile.TemporaryDirectory(prefix='stream-directory-controls-')
        self.addCleanup(temp.cleanup)
        target = Path(temp.name) / 'package'
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('__pycache__'))
        return target

    def run_package(self, target, success, expected=''):
        run = subprocess.run([sys.executable, '-I', '-O', '-B', str(target / 'verify.py')],
                             capture_output=True, text=True, timeout=60)
        self.assertEqual(run.returncode == 0, success, run.stdout + run.stderr)
        self.assertIn(expected, run.stdout + run.stderr)

    def test_source_corruption(self):
        target = self.export()
        with (target / 'vendor/stream.py').open('ab') as f:
            f.write(b'\n# source corruption\n')
        self.run_package(target, False, 'source hash: vendor/stream.py')

    def test_deleted_manifest_record(self):
        target = self.export()
        path = target / 'SNAPSHOT.json'
        data = json.loads(path.read_text())
        data['files'].pop()
        path.write_text(json.dumps(data))
        self.run_package(target, False, 'snapshot identity')

    def test_changed_source_provenance(self):
        target = self.export()
        path = target / 'SNAPSHOT.json'
        data = json.loads(path.read_text())
        data['files'][0]['source_path'] = 'unrelated.py'
        path.write_text(json.dumps(data))
        self.run_package(target, False, 'snapshot identity')

    def test_typed_receipt(self):
        target = self.export()
        path = target / 'RESULT.json'
        data = json.loads(path.read_text())
        data['schema_version'] = True
        path.write_text(json.dumps(data))
        self.run_package(target, False, 'complete typed receipt equality')

    def test_extra_restored_scratch_and_guard_deletion(self):
        verifier = load_verifier()
        m = verifier.load()
        original_multiply = m.words.Ring.multiply
        original_require = verifier.require

        def changed_multiply(ring, a, b):
            extra = ring.arena.zero()
            try:
                return original_multiply(ring, a, b)
            finally:
                ring.arena.free(extra)

        def run():
            return verifier.stream_case(m, 5, 2, (1, 1, 1), [i % 2 for i in range(25)])

        m.words.Ring.multiply = changed_multiply
        try:
            with self.assertRaisesRegex(ValueError, 'max-composed residue bound'):
                run()

            def omitted_guard(value, message):
                if message != 'max-composed residue bound':
                    original_require(value, message)

            verifier.require = omitted_guard
            result = run()
            self.assertEqual(result['residue_peak'], 7)
        finally:
            m.words.Ring.multiply = original_multiply
            verifier.require = original_require

    def test_effective_stale_bytecode_is_ignored_and_files_unchanged(self):
        # This private helper creates timestamp-valid caches for a real loader
        # positive control. The source checker must bypass both cache variants.
        from importlib._bootstrap_external import _code_to_timestamp_pyc
        target = self.export()
        source = target / 'vendor/words.py'
        code = compile("raise RuntimeError('EFFECTIVE_BYTECODE_SENTINEL')", str(source), 'exec')
        data = _code_to_timestamp_pyc(code, int(source.stat().st_mtime), source.stat().st_size)
        for optimization in ('', '1'):
            cache = Path(importlib.util.cache_from_source(str(source), optimization=optimization))
            cache.parent.mkdir(exist_ok=True)
            cache.write_bytes(data)
        probe = subprocess.run([sys.executable, '-I', '-O', '-B', '-c',
                                'import sys;sys.path.insert(0,sys.argv[1]);import words',
                                str(source.parent)], capture_output=True, text=True, timeout=10)
        self.assertNotEqual(probe.returncode, 0)
        self.assertIn('EFFECTIVE_BYTECODE_SENTINEL', probe.stderr)
        before = {str(p.relative_to(target)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in target.rglob('*') if p.is_file()}
        self.run_package(target, True, 'PASS_STREAM_DIRECTORY_NUMERICAL_AUDIT')
        after = {str(p.relative_to(target)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in target.rglob('*') if p.is_file()}
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
