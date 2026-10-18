#!/usr/bin/env python3
"""Selected source-closure regressions on synthetic records. Apache-2.0."""
import errno
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('selected_inventory_candidate', HERE / 'check.py')
c = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(c)


def fixture(root, modern):
    package = root / 'supplier'
    (package / 'nested').mkdir(parents=True)
    proof = package / 'nested/proof.txt'
    proof.write_bytes(b'frozen synthetic proof\n')
    certificate = root / 'certificate.json'
    certificate.write_bytes(b'{"kappa":"1/1000"}')
    manifest = root / 'manifest.json' if modern else package / 'MANIFEST.json'
    key = 'supplier/nested/proof.txt' if modern else 'nested/proof.txt'
    inventory = {'files': {key: sha256(proof.read_bytes()).hexdigest()}}
    if modern:
        inventory.update(format='repository-packages-sha256-v1', package_roots=['supplier'])
    manifest.write_text(json.dumps(inventory), encoding='utf-8')
    return {'kappa': '1/1000', 'decimal': '0.001', 'certificate': 'certificate.json',
            'certificate_sha256': sha256(certificate.read_bytes()).hexdigest(),
            'source_manifest': manifest.relative_to(root).as_posix(),
            'proof': 'supplier/nested/proof.txt', 'review': 'supplier/nested/proof.txt',
            'validation': 'certificate.json',
            'proof_supplements': {'supplier/nested/proof.txt': sha256(proof.read_bytes()).hexdigest()}}


@contextmanager
def unreadable(directory, test):
    if os.name != 'posix':
        test.skipTest('POSIX permissions unavailable; injected I/O controls remain mandatory')
    directory.chmod(0)
    try:
        try:
            with os.scandir(directory) as entries:
                list(entries)
        except PermissionError:
            pass
        else:
            test.skipTest('account bypasses directory permissions')
        yield
    finally:
        directory.chmod(0o700)


def cli_tree(root, record):
    """Minimal checkout for the actual retained and successor command lines."""
    target = root / c.PREDECESSOR
    target.parent.mkdir(parents=True)
    target.write_bytes(c.source(c.PREDECESSOR))
    package = root / 'research' / HERE.name
    package.mkdir(parents=True)
    for name in ('check.py', 'SOURCES.json'):
        (package / name).write_bytes((HERE / name).read_bytes())
    selected = root / 'certificates/selected-result.json'
    selected.parent.mkdir()
    selected.write_text(json.dumps(record), encoding='utf-8')
    return target, package / 'check.py'


class SelectedInventoryControls(unittest.TestCase):
    def test_unreadable_unlisted_source_is_not_absence(self):
        for modern in (False, True):
            with self.subTest(modern=modern), tempfile.TemporaryDirectory() as td:
                root = Path(td).resolve()
                record = fixture(root, modern)
                self.assertEqual(c.checker.check(record, root), Fraction(1, 1000))
                hidden = root / 'supplier/unlisted'
                hidden.mkdir()
                (hidden / 'extra.py').write_bytes(b'UNREVIEWED = True\n')
                with unreadable(hidden, self):
                    self.assertEqual(c.predecessor().check(record, root), Fraction(1, 1000))
                    with self.assertRaises(PermissionError):
                        c.checker.check(record, root)
                with self.assertRaisesRegex(ValueError, 'inventory or bytes changed'):
                    c.checker.check(record, root)

    def test_actual_cli_rejects_unreadable_source_and_recovers(self):
        for modern in (False, True):
            with self.subTest(modern=modern), tempfile.TemporaryDirectory() as td:
                root = Path(td).resolve()
                record = fixture(root, modern)
                retained, candidate = cli_tree(root, record)
                command = [sys.executable, '-I', '-B', str(candidate)]
                clean = subprocess.run(command, check=False, capture_output=True, text=True, timeout=10)
                self.assertEqual(clean.returncode, 0, clean.stderr)
                self.assertIn('PASS selected record', clean.stdout)
                hidden = root / 'supplier/unlisted'
                hidden.mkdir()
                extra = hidden / 'extra.py'
                extra.write_bytes(b'UNREVIEWED = True\n')
                with unreadable(hidden, self):
                    old = subprocess.run([*command[:-1], str(retained)],
                                         check=False, capture_output=True, text=True, timeout=10)
                    self.assertEqual(old.returncode, 0, old.stderr)
                    failed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=10)
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertIn('PermissionError', failed.stderr)
                    self.assertNotIn('PASS selected record', failed.stdout)
                visible = subprocess.run(command, check=False, capture_output=True, text=True, timeout=10)
                self.assertNotEqual(visible.returncode, 0)
                self.assertIn('inventory or bytes changed', visible.stderr)
                extra.unlink()
                restored = subprocess.run(command, check=False, capture_output=True, text=True, timeout=10)
                self.assertEqual(restored.returncode, 0, restored.stderr)
                self.assertIn('PASS selected record', restored.stdout)
                optimized = subprocess.run([sys.executable, '-I', '-O', '-B', str(candidate)],
                                           check=False, capture_output=True, text=True, timeout=10)
                self.assertNotEqual(optimized.returncode, 0)
                self.assertIn('Assertions must remain enabled', optimized.stderr)

    def test_open_iteration_and_metadata_errors_propagate(self):
        for modern in (False, True):
            with tempfile.TemporaryDirectory() as td:
                root = Path(td).resolve()
                record = fixture(root, modern)
                directory = root / 'supplier/nested'
                real_scandir = os.scandir
                for phase in ('open', 'iterate', 'stat'):
                    for code in (errno.EACCES, errno.EIO):
                        with self.subTest(modern=modern, phase=phase, errno=code):
                            failure = OSError(code, 'injected inventory failure')
                            with real_scandir(directory) as entries:
                                entry = next(entries)
                            if phase == 'stat':
                                entry = mock.Mock(name='proof entry')
                                entry.name = 'proof.txt'
                                entry.stat.side_effect = failure
                            scan = FaultyScan(entry, failure if phase == 'iterate' else None)

                            def scandir(path, directory=directory, real_scandir=real_scandir,
                                        phase=phase, failure=failure, scan=scan):
                                if Path(path) != directory:
                                    return real_scandir(path)
                                if phase == 'open':
                                    raise failure
                                return scan

                            with mock.patch.object(c.os, 'scandir', side_effect=scandir), \
                                    self.assertRaisesRegex(OSError, 'injected inventory failure'):
                                c.checker.check(record, root)
                            if phase != 'open':
                                self.assertTrue(scan.closed)
                self.assertEqual(c.checker.check(record, root), Fraction(1, 1000))

    def test_complete_inventory_and_entry_budget(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'nested').mkdir()
            (root / 'nested/proof.txt').write_bytes(b'proof\n')
            (root / 'data.bin').write_bytes(b'\xff')
            found = {p.relative_to(root).as_posix() for p in c.package_files(root, max_entries=3)}
            self.assertEqual(found, {'nested/proof.txt', 'data.bin'})
            with self.assertRaisesRegex(ValueError, 'entry budget exceeded'):
                list(c.package_files(root, max_entries=2))
            for bad in (-1, True, 1.0):
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    list(c.package_files(root, max_entries=bad))
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(list(c.package_files(Path(td), max_entries=0)), [])

    def test_symlink_target_access_errors_are_not_hidden(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            record = fixture(root, True)
            alias = root / 'supplier/alias.txt'
            try:
                alias.symlink_to('nested/proof.txt')
            except (OSError, NotImplementedError) as exc:
                self.skipTest('symlinks unavailable: ' + str(exc))
            original_scandir = os.scandir
            with original_scandir(alias.parent) as entries:
                link_entry = next(e for e in entries if e.name == 'alias.txt')
            self.assertTrue(link_entry.is_symlink())
            proxy = mock.Mock()
            proxy.name = 'alias.txt'
            for code in (errno.EACCES, errno.EIO):
                def metadata(*, follow_symlinks, code=code):
                    if follow_symlinks:
                        raise OSError(code, 'injected alias metadata failure')
                    return link_entry.stat(follow_symlinks=False)

                proxy.stat.side_effect = metadata
                scan = FaultyScan(proxy, None)
                with mock.patch.object(c.os, 'scandir', return_value=scan), \
                        self.assertRaisesRegex(OSError, 'injected alias metadata failure'):
                    c.checker.check(record, root)
                self.assertTrue(scan.closed)

    def test_nonregular_source_entries_are_rejected(self):
        if not hasattr(os, 'mkfifo'):
            self.skipTest('FIFO unavailable')
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            record = fixture(root, True)
            fifo = root / 'supplier/pipe'
            os.mkfifo(fifo)
            with self.assertRaisesRegex(ValueError, 'not a regular file'):
                c.checker.check(record, root)
            fifo.unlink()
            self.assertEqual(c.checker.check(record, root), Fraction(1, 1000))

    def test_source_change_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / c.PREDECESSOR
            target.parent.mkdir(parents=True)
            target.write_bytes(c.source(c.PREDECESSOR) + b'\nraise RuntimeError("must not execute")\n')
            with mock.patch.object(c, 'ROOT', root), \
                    self.assertRaisesRegex(ValueError, 'source bytes differ'):
                c.predecessor()


class FaultyScan:
    """Yield one real entry, then optionally fail; expose handle cleanup."""
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
