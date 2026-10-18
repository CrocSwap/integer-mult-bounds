#!/usr/bin/env python3
"""Filesystem coverage regressions for strict payload comparison. Apache-2.0."""
import errno
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('inventory_comparator', HERE / 'compare.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class InventoryControls(unittest.TestCase):
    def test_unreadable_subtree_cli_fails_without_report(self):
        if os.name != 'posix':
            self.skipTest('POSIX permission fixture; injected controls are portable')
        with tempfile.TemporaryDirectory(prefix='strict inventory ') as temporary:
            root = Path(temporary)
            left, right = root / 'reference', root / 'run'
            for side, value in ((left, b'{"proof":1}'), (right, b'{"proof":2}')):
                (side / 'private').mkdir(parents=True)
                (side / 'private' / 'certificate.json').write_bytes(value)
            command = [sys.executable, '-I', '-O', '-B', str(HERE / 'compare.py'),
                       str(left), str(right)]
            readable = subprocess.run(command, check=False, capture_output=True, text=True, timeout=10)
            self.assertEqual(readable.returncode, 1, readable.stderr)
            for hidden in ((left,), (right,), (left, right)):
                with self.subTest(hidden=[p.name for p in hidden]):
                    report = root / ('comparison-' + '-'.join(p.name for p in hidden) + '.json')
                    try:
                        for side in hidden:
                            (side / 'private').chmod(0)
                        try:
                            with os.scandir(hidden[0] / 'private') as entries:
                                list(entries)
                        except PermissionError:
                            pass
                        else:
                            self.skipTest('current account bypasses directory permissions')
                        result = subprocess.run(command + ['--out', str(report)],
                                                check=False, capture_output=True, text=True, timeout=10)
                        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                        self.assertIn('INVALID_COMPARISON:', result.stderr)
                        self.assertNotIn('"equivalent": true', result.stdout)
                        self.assertFalse(report.exists())
                    finally:
                        for side in hidden:
                            (side / 'private').chmod(0o700)
            (right / 'private' / 'certificate.json').write_bytes(b'{ "proof": 1 }')
            restored = subprocess.run(command, check=False, capture_output=True, text=True, timeout=10)
            self.assertEqual(restored.returncode, 0, restored.stderr)
            self.assertEqual(json.loads(restored.stdout),
                             {'equivalent': True, 'counts': {'json-format': 1}})

    def test_open_iteration_and_stat_errors_reach_cli_without_partial_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            left, right = root / 'reference', root / 'run'
            for side in (left, right):
                (side / 'nested').mkdir(parents=True)
                (side / 'nested' / 'proof.json').write_bytes(b'{}')
            real_scandir = os.scandir
            for side in (left, right):
                for phase in ('open', 'iterate', 'stat'):
                    for code in (errno.EACCES, errno.EIO):
                        with self.subTest(side=side.name, phase=phase, errno=code):
                            failure = OSError(code, 'injected inventory failure')
                            with real_scandir(side / 'nested') as entries:
                                entry = next(entries)
                            if phase == 'stat':
                                entry = mock.Mock()
                                entry.name = 'proof.json'
                                entry.stat.side_effect = failure
                            scan = FaultyScan(entry, failure if phase == 'iterate' else None)

                            def scandir(path, side=side, phase=phase, failure=failure, scan=scan):
                                if Path(path) != side / 'nested':
                                    return real_scandir(path)
                                if phase == 'open':
                                    raise failure
                                return scan

                            out, err = io.StringIO(), io.StringIO()
                            report = root / 'never-created.json'
                            argv = ['compare.py', str(left), str(right), '--out', str(report)]
                            with mock.patch.object(c.os, 'scandir', side_effect=scandir), \
                                    mock.patch.object(sys, 'argv', argv), \
                                    redirect_stdout(out), redirect_stderr(err):
                                self.assertEqual(c.strict.main(), 2)
                            self.assertIn('injected inventory failure', err.getvalue())
                            self.assertEqual(out.getvalue(), '')
                            self.assertFalse(report.exists())
                            if phase != 'open':
                                self.assertTrue(scan.closed)

    def test_complete_inventory_and_entry_budget(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'nested').mkdir()
            (root / 'nested' / 'proof.json').write_bytes(b'{}')
            (root / 'raw.bin').write_bytes(b'\xff')
            self.assertEqual(set(c.inventory(root, max_entries=3)),
                             {'nested/proof.json', 'raw.bin'})
            with self.assertRaisesRegex(c.InvalidPayload, 'entry budget exceeded'):
                c.inventory(root, max_entries=2)
            for bad in (-1, True, 1.0):
                with self.subTest(bad=bad), self.assertRaises(c.InvalidPayload):
                    c.inventory(root, max_entries=bad)
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual(c.inventory(Path(temporary), max_entries=0), {})

    def test_missing_extra_and_changed_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            left, right = root / 'reference', root / 'run'
            left.mkdir()
            right.mkdir()
            (left / 'missing.json').write_bytes(b'{}')
            (right / 'extra.json').write_bytes(b'{}')
            (left / 'proof.json').write_bytes(b'{"checked":true}')
            (right / 'proof.json').write_bytes(b'{"checked":1}')
            result = c.compare(left, right)
            self.assertEqual(set(result), {'missing.json', 'extra.json', 'proof.json'})
            self.assertEqual(result['missing.json'], {'cls': 'missing'})
            self.assertEqual(result['extra.json'], {'cls': 'extra'})
            self.assertEqual(result['proof.json']['verdict'], 'proof-relevant-candidate')

    def test_invalid_roots_links_and_special_entries(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            file = root / 'proof.json'
            file.write_bytes(b'{}')
            with self.assertRaises(c.InvalidPayload):
                c.inventory(file)
            with self.assertRaises(OSError):
                c.inventory(root / 'missing')
            if os.name == 'posix':
                for target in (file, root, root / 'missing'):
                    link = root / 'link'
                    link.symlink_to(target)
                    try:
                        with self.assertRaises(c.InvalidPayload):
                            c.inventory(root)
                        with self.assertRaises(c.InvalidPayload):
                            c.inventory(link)
                    finally:
                        link.unlink()
                os.mkfifo(root / 'fifo')
                with self.assertRaisesRegex(c.InvalidPayload, 'nonregular entry'):
                    c.inventory(root)

    def test_changed_source_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / c.PREDECESSOR
            target.parent.mkdir(parents=True)
            raw = c.source(c.PREDECESSOR)
            target.write_bytes(raw + b'\nraise RuntimeError("must not execute")\n')
            with mock.patch.object(c, 'ROOT', root), \
                    self.assertRaisesRegex(ValueError, 'source bytes differ'):
                c.predecessor()


class FaultyScan:
    """One real entry, followed by an optional iteration failure."""
    def __init__(self, entry, failure):
        self.entry = entry
        self.failure = failure
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.closed = True

    def __iter__(self):
        yield self.entry
        if self.failure is not None:
            raise self.failure


if __name__ == '__main__':
    unittest.main(verbosity=2)
