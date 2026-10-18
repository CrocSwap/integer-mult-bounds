#!/usr/bin/env python3
"""Behavioral equivalence and fresh-call invalidation for the preflight prototype.

Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_sources():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    for name, expected in sources['live_sources'].items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == expected,
                'Pinned source changed: ' + name)
    return sources


class FreshCallControls(unittest.TestCase):
    def each_layout(self, run):
        for modern in (False, True):
            with self.subTest(modern=modern), tempfile.TemporaryDirectory() as td:
                root = Path(td).resolve()
                record = self.fixtures.fixture(root, modern)
                run(root, record, modern)

    def test_same_size_change_with_restored_mtime(self):
        def run(root, record, modern):
            source = root / record['proof']
            original = source.read_bytes()
            stamp = source.stat()
            self.checker.check(record, root)
            source.write_bytes(bytes([original[0] ^ 1]) + original[1:])
            os.utime(source, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
            self.assertEqual(source.stat().st_size, len(original))
            self.assertEqual(source.stat().st_mtime_ns, stamp.st_mtime_ns)
            with self.assertRaisesRegex(ValueError, 'inventory or bytes changed'):
                self.checker.check(record, root)
            source.write_bytes(original)
            self.assertEqual(self.checker.check(record, root), self.fixtures.Fraction(1, 1000))
        self.each_layout(run)

    def test_alias_retargeted_after_success(self):
        def run(root, record, modern):
            source = root / record['proof']
            alias = root / 'supplier/alias.txt'
            try:
                alias.symlink_to('PROOF.md')
            except (OSError, NotImplementedError) as exc:
                self.skipTest(str(exc))
            manifest_path = root / record['source_manifest']
            manifest = json.loads(manifest_path.read_text())
            manifest['files']['supplier/alias.txt' if modern else 'alias.txt'] = sha256(source.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest))
            self.checker.check(record, root)
            outside = root / 'outside.txt'
            outside.write_bytes(source.read_bytes())
            alias.unlink()
            alias.symlink_to('../outside.txt')
            with self.assertRaisesRegex(ValueError, 'Package symlink escapes root'):
                self.checker.check(record, root)
        self.each_layout(run)

    def test_unhashed_manifest_cannot_be_primary_proof(self):
        def run(root, record, modern):
            record['proof'] = record['source_manifest']
            with self.assertRaisesRegex(ValueError, 'primary proof is not covered'):
                self.checker.check(record, root)
        self.each_layout(run)

    def test_overlapping_nested_roots_still_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            record = self.fixtures.fixture(root, True)
            nested = root / 'supplier/nested'
            nested.mkdir()
            (nested / 'extra.txt').write_bytes(b'covered twice')
            path = root / record['source_manifest']
            manifest = json.loads(path.read_text())
            manifest['package_roots'].append('supplier/nested')
            manifest['files']['supplier/nested/extra.txt'] = sha256((nested / 'extra.txt').read_bytes()).hexdigest()
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'Overlapping package roots'):
                self.checker.check(record, root)


def main():
    require(not sys.flags.optimize, 'Run equivalence tests with assertions enabled')
    check_sources()
    total = 0
    for engine, path in (('baseline', ROOT / 'scripts/verify_selected_result.py'),
                         ('candidate', HERE / 'candidate.py')):
        checker = load('preflight_' + engine, path)
        suite = unittest.TestSuite()
        for name in ('test_selected_result', 'test_selected_inventory_links',
                     'test_selected_proof_binding'):
            tests = load(engine + '_' + name, ROOT / 'tests' / (name + '.py'))
            tests.checker = checker
            suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(tests))
        fixtures = load(engine + '_fixtures', ROOT / 'tests/test_selected_proof_binding.py')
        controls = type(engine + '_FreshCallControls', (FreshCallControls,),
                        {'checker': checker, 'fixtures': fixtures})
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(controls))
        count = suite.countTestCases()
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        require(result.wasSuccessful() and not result.skipped,
                engine + ' equivalence/control suite failed or skipped')
        total += count
        print(engine, count, 'behavioral groups PASS', flush=True)
        optimized = subprocess.run([sys.executable, '-I', '-B', '-O', str(path)],
                                   capture_output=True, text=True, timeout=10)
        require(optimized.returncode != 0 and 'Assertions must remain enabled' in optimized.stderr,
                engine + ' optimized CLI did not fail closed')
    check_sources()
    print('PASS_SELECTED_PREFLIGHT_PATH_REUSE', total, 'behavioral groups; both optimized CLIs refused')


if __name__ == '__main__':
    main()
