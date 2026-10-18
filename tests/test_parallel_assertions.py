"""Assertion failures must survive the parallel verifier's process boundary."""
import contextlib
import io
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_parallel
import verify_parallel


class ParallelAssertionChecks(unittest.TestCase):
    def test_direct_replay_guard_survives_optimized_interpreters(self):
        scripts = str(Path(__file__).resolve().parents[1] / 'scripts')
        probe = (
            'import sys\nsys.path.insert(0, ' + repr(scripts) + ')\n'
            'import verify_complex741_parallel as par\n'
            'class SourceTrap:\n'
            ' def read_text(self, **kwargs): raise RuntimeError("SOURCE_REACHED")\n'
            'par.VERIFY=SourceTrap()\n'
            'sys.argv=["replay", "--work", "unused-work"]\npar.main()\n')
        for flags in ([], ['-O'], ['-OO']):
            with self.subTest(flags=flags):
                result = subprocess.run([sys.executable, *flags, '-c', probe], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                if flags:
                    self.assertIn('Assertions are required', result.stderr)
                    self.assertNotIn('SOURCE_REACHED', result.stderr)
                else:
                    self.assertIn('SOURCE_REACHED', result.stderr)

    def test_inherited_optimization_cannot_hide_direct_or_nested_failure(self):
        nested = ('import subprocess,sys; '
                  'sys.exit(subprocess.run([sys.executable,"-c",'
                  '"assert False, \'nested verification failure\'"]).returncode)')
        commands = [('good', [sys.executable, '-c', 'print("positive control")']),
                    ('direct', [sys.executable, '-c', 'assert False, "direct verification failure"']),
                    ('nested', [sys.executable, '-c', nested])]
        for level in ('1', '2'):
            with self.subTest(level=level), patch.dict(os.environ, {'PYTHONOPTIMIZE': level, 'JOBS': '3'}):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    failures = run_parallel.run_all(commands)
                self.assertEqual(set(failures), {'direct', 'nested'})
                self.assertIn('positive control', output.getvalue())
                self.assertIn('nested verification failure', output.getvalue())
                self.assertEqual(os.environ['PYTHONOPTIMIZE'], level)

    def test_explicit_optimized_control_remains_explicit(self):
        command = [sys.executable, '-O', '-c', 'assert False; print("explicit optimized control")']
        with patch.dict(os.environ, {'PYTHONOPTIMIZE': '2', 'JOBS': '1'}):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                failures = run_parallel.run_all([('deliberate-O', command)])
        self.assertEqual(failures, [])
        self.assertIn('explicit optimized control', output.getvalue())

    def test_snapshot_group_retains_assertions_in_make_descendants(self):
        # Python stands in for make and executes the named target file. This
        # exercises the actual snapshot, process and failure path without make.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'source'
            root.mkdir()
            (root / 'Makefile').write_text('verify:\n\t$(MAKE) verify-check\n')
            (root / 'verify-check').write_text('assert False, "group verification failure"\n')
            verify_parallel.git('init', '-q', cwd=root)
            verify_parallel.git('add', '.', cwd=root)
            verify_parallel.git('commit', '-q', '--no-verify', '-m', 'fixture', cwd=root)
            work = Path(directory) / 'work'
            def mkdir(**kwargs):
                work.mkdir()
                return str(work)
            with patch.object(verify_parallel, 'ROOT', root), patch.object(
                    verify_parallel, 'LOGS', Path(directory) / 'logs'), patch.object(
                    verify_parallel.tempfile, 'mkdtemp', side_effect=mkdir), patch.object(
                    # The outer TemporaryDirectory owns fixture cleanup. Keep
                    # this test independent of Git's Windows read-only objects.
                    verify_parallel.shutil, 'rmtree'), patch.dict(
                    os.environ, {'PYTHONOPTIMIZE': '2', 'MAKE': sys.executable, 'JOBS': '1'}), patch(
                    'sys.argv', ['verify_parallel.py', '--jobs', '1']), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(SystemExit, 'FAILED 1 of 1'):
                    verify_parallel.main()
            self.assertIn('group verification failure', (Path(directory) / 'logs/check.log').read_text())


if __name__ == '__main__':
    unittest.main()
