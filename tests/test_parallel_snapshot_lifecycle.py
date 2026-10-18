"""Portable real-process checks for owned snapshot cleanup and cancellation."""
import contextlib
import io
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import verify_parallel as runner


class SnapshotLifecycleChecks(unittest.TestCase):
    def invoke(self, directory, source, interrupt=False):
        root = Path(directory) / 'source'
        root.mkdir()
        (root / 'Makefile').write_text('verify:\n\t$(MAKE) verify-check\n')
        (root / 'verify-check').write_text(source)
        runner.git('init', '-q', cwd=root)
        runner.git('add', '.', cwd=root)
        runner.git('commit', '-q', '--no-verify', '-m', 'fixture', cwd=root)
        work = Path(directory) / 'work'
        def mkdir(**kwargs):
            work.mkdir()
            return str(work)
        out = io.StringIO()
        real_popen = subprocess.Popen
        launched = []
        def launch(argv, **kwargs):
            p = real_popen(argv, **kwargs)
            if argv[-1] == 'verify-check':
                launched.append(p)
            return p
        with patch.object(runner, 'ROOT', root), patch.object(runner, 'LOGS', Path(directory) / 'logs'), patch.object(
                runner.tempfile, 'mkdtemp', side_effect=mkdir), patch.dict(os.environ, {'MAKE': sys.executable, 'JOBS': '1'}), patch(
                'sys.argv', ['verify_parallel.py', '--jobs', '1']), patch.object(
                runner.subprocess, 'Popen', side_effect=launch), contextlib.redirect_stdout(out):
            if interrupt:
                # Interrupt the scheduler once; subprocess.wait(timeout=...) also
                # uses the same time module and must be allowed to reap the child.
                real_sleep = runner.time.sleep
                interrupted = False
                def interrupt_once(seconds):
                    nonlocal interrupted
                    if not interrupted:
                        interrupted = True
                        raise KeyboardInterrupt
                    return real_sleep(seconds)
                with patch.object(runner.time, 'sleep', side_effect=interrupt_once), self.assertRaises(KeyboardInterrupt):
                    runner.main()
            else:
                runner.main()
        return work, out.getvalue(), launched

    def test_success_removes_real_git_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            work, out, _ = self.invoke(directory, 'print("fixture passed")\n')
            self.assertFalse(work.exists())
            self.assertIn('PASS all 1 groups', out)

    def test_cancellation_preserves_original_exception_and_reaps_child(self):
        with tempfile.TemporaryDirectory() as directory:
            work, _, launched = self.invoke(directory, 'import time; time.sleep(600)\n', interrupt=True)
            self.assertEqual(len(launched), 1)
            self.assertIsNotNone(launched[0].poll())
            self.assertFalse(work.exists())

    def test_readonly_file_removed_but_outside_sibling_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = root / 'owned'; snapshot.mkdir()
            inside = snapshot / 'object'; inside.write_text('git object')
            outside = root / 'keep'; outside.write_text('unrelated')
            inside.chmod(stat.S_IREAD)
            runner.remove_snapshot(snapshot)
            self.assertFalse(snapshot.exists())
            self.assertEqual(outside.read_text(), 'unrelated')


if __name__ == '__main__':
    unittest.main()
