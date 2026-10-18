"""PR154 integration: worker validation, failure propagation and true snapshots."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_parallel
import verify_parallel


class ParallelChecks(unittest.TestCase):
    def test_invalid_environment_does_not_silently_clamp(self):
        for value in ('0', '-1', '', 'no', '1.5'):
            with self.subTest(value=value), patch.dict(os.environ, {'JOBS': value}):
                with self.assertRaises(ValueError):
                    run_parallel.jobs()
        with patch.dict(os.environ, {'JOBS': '2'}):
            self.assertEqual(run_parallel.jobs(), 2)
            self.assertEqual(verify_parallel.default_jobs(), 2)

    def test_worker_failure_is_not_lost(self):
        commands = [('good', [sys.executable, '-c', 'print("good payload")']),
                    ('bad', [sys.executable, '-c', 'print("bad payload"); raise SystemExit(7)'])]
        out = io.StringIO()
        with patch.dict(os.environ, {'JOBS': '2'}), contextlib.redirect_stdout(out):
            self.assertEqual(run_parallel.run_all(commands), ['bad'])
        self.assertIn('good payload', out.getvalue())
        self.assertIn('bad payload', out.getvalue())

    def synthetic(self, directory):
        root = Path(directory) / 'source'; root.mkdir()
        (root / '.gitignore').write_text('*.dat\nbuild/\n')
        (root / 'tracked.dat').write_text('baseline')
        (root / 'deleted').write_text('remove me')
        (root / 'Makefile').write_text(
            'verify:\n\t$(MAKE) verify-good\n\t$(MAKE) verify-other\n'
            'verify-good:\n\t@cat tracked.dat\n'
            'verify-other:\n\t@cat tracked.dat\n'
            'verify-bad:\n\t@false\n'
            'verify-drift:\n\t@echo changed > tracked.dat\n')
        verify_parallel.git('init', '-q', cwd=root)
        verify_parallel.git('add', '-f', '.', cwd=root)
        verify_parallel.git('commit', '-q', '--no-verify', '-m', 'test fixture', cwd=root)
        (root / 'tracked.dat').write_text('uncommitted edit')
        (root / 'deleted').unlink()
        (root / 'new-input').write_text('untracked input')
        (root / 'ignored.dat').write_text('ignored output')
        return root

    def test_snapshot_preserves_ignored_tracked_edits_and_untracked_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.synthetic(directory); dest = Path(directory) / 'snapshot'
            with patch.object(verify_parallel, 'ROOT', root):
                verify_parallel.snapshot(dest)
            names = verify_parallel.git('ls-files', cwd=dest).splitlines()
            self.assertIn('tracked.dat', names)
            self.assertIn('new-input', names)
            self.assertNotIn('ignored.dat', names)
            self.assertNotIn('deleted', names)
            self.assertEqual((dest / 'tracked.dat').read_text(), 'uncommitted edit')

    def invoke(self, root, args, work):
        def mkdir(**kwargs):
            work.mkdir()
            return str(work)
        with patch.object(verify_parallel, 'ROOT', root), patch.object(
            verify_parallel, 'LOGS', root / 'build/verify-parallel'), patch(
            'sys.argv', ['verify_parallel.py', *args]), patch.dict(
            os.environ, {'JOBS': '1'}), patch.object(
            verify_parallel.tempfile, 'mkdtemp', side_effect=mkdir), contextlib.redirect_stdout(io.StringIO()):
            verify_parallel.main()

    def test_two_groups_are_isolated_and_preserve_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.synthetic(directory)
            self.invoke(root, ['--jobs', '2'], Path(directory) / 'work')
            self.assertEqual((root / 'tracked.dat').read_text(), 'uncommitted edit')
            self.assertFalse((Path(directory) / 'work').exists())
            for group in ('good', 'other'):
                self.assertIn('uncommitted edit', (root / f'build/verify-parallel/{group}.log').read_text())

    def test_failure_and_tracked_drift_both_reject(self):
        for group in ('bad', 'drift'):
            with self.subTest(group=group), tempfile.TemporaryDirectory() as directory:
                root = self.synthetic(directory)
                makefile = root / 'Makefile'
                makefile.write_text(makefile.read_text().replace('$(MAKE) verify-other', f'$(MAKE) verify-{group}'))
                with self.assertRaisesRegex(SystemExit, 'FAILED'):
                    self.invoke(root, [group, '--jobs', '1'], Path(directory) / 'work')
                self.assertEqual((root / 'tracked.dat').read_text(), 'uncommitted edit')

    def test_invalid_cli_and_groups_fail_before_creating_snapshots(self):
        cases = [['--jobs', '0'], ['--jobs', '-2'], ['good', 'good'], ['../escape'], ['missing']]
        with tempfile.TemporaryDirectory() as directory:
            root = self.synthetic(directory)
            for args in cases:
                with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        self.invoke(root, args, Path(directory) / 'must-not-exist')
                    self.assertFalse((Path(directory) / 'must-not-exist').exists())


if __name__ == '__main__':
    unittest.main()
