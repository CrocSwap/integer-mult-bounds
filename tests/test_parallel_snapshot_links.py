"""Snapshot inputs cannot leave writable aliases to the donor checkout."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import verify_parallel


class SnapshotLinks(unittest.TestCase):
    def fixture(self, directory):
        root = Path(directory) / 'source'
        root.mkdir()
        (root / 'input.txt').write_text('original')
        verify_parallel.git('init', '-q', cwd=root)
        return root

    def link(self, target, alias):
        try:
            alias.symlink_to(target)
        except OSError as exc:
            self.skipTest(f'symlink creation unavailable: {exc}')

    def test_external_and_absolute_links_fail_before_copying(self):
        for kind in ('external-absolute', 'external-relative', 'internal-absolute'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root = self.fixture(directory)
                outside = Path(directory) / 'outside.txt'
                outside.write_text('outside')
                target = {'external-absolute': str(outside),
                          'external-relative': '../outside.txt',
                          'internal-absolute': str(root / 'input.txt')}[kind]
                self.link(target, root / 'z-alias')
                dest = Path(directory) / 'snapshot'
                with patch.object(verify_parallel, 'ROOT', root):
                    with self.assertRaisesRegex(ValueError, 'snapshot symlink'):
                        verify_parallel.snapshot(dest)
                self.assertFalse(dest.exists())
                self.assertEqual(outside.read_text(), 'outside')
                self.assertEqual((root / 'input.txt').read_text(), 'original')

    def test_relative_internal_link_moves_with_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            self.link('input.txt', root / 'alias')
            dest = Path(directory) / 'snapshot'
            with patch.object(verify_parallel, 'ROOT', root):
                self.assertEqual(verify_parallel.snapshot(dest), 2)
            self.assertTrue((dest / 'alias').is_symlink())
            self.assertEqual(os.readlink(dest / 'alias'), 'input.txt')
            (dest / 'alias').write_text('worker edit')
            self.assertEqual((dest / 'input.txt').read_text(), 'worker edit')
            self.assertEqual((root / 'input.txt').read_text(), 'original')

    def test_indirect_escape_and_link_cycle_fail_closed(self):
        for kind in ('chain', 'cycle'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root = self.fixture(directory)
                (Path(directory) / 'outside.txt').write_text('outside')
                self.link('second', root / 'first')
                self.link('../outside.txt' if kind == 'chain' else 'first', root / 'second')
                with patch.object(verify_parallel, 'ROOT', root):
                    with self.assertRaisesRegex(ValueError, 'snapshot symlink'):
                        verify_parallel.snapshot(Path(directory) / 'snapshot')


if __name__ == '__main__':
    unittest.main()
