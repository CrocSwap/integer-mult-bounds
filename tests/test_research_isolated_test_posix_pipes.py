"""Observe POSIX module exit before ordinary descendants release capture pipes.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Reuses Nick Petalas's readiness-controlled child/grandchild fixtures.
"""
import importlib.util
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

from test_isolated_test_exit_cleanup import MODULE, SOLVER, await_file

ROOT = Path(__file__).resolve().parents[1]


class ExitObserver:
    """Retain Linux pidfds or macOS process-exit registrations before release."""

    def __init__(self, pids):
        self.pending = set(pids)
        self.handles = {}
        self.queue = None
        if sys.platform == 'linux':
            self.handles = {os.pidfd_open(pid): pid for pid in pids}
        else:
            self.queue = select.kqueue()
            self.queue.control([
                select.kevent(pid, filter=select.KQ_FILTER_PROC,
                              flags=select.KQ_EV_ADD | select.KQ_EV_ONESHOT,
                              fflags=select.KQ_NOTE_EXIT) for pid in pids
            ], 0, 0)

    def stopped(self, timeout=0):
        if self.queue:
            for event in self.queue.control(None, len(self.pending), timeout):
                if event.fflags & select.KQ_NOTE_EXIT:
                    self.pending.discard(event.ident)
        else:
            ready, _, _ = select.select(list(self.handles), [], [], timeout)
            self.pending.difference_update(self.handles[handle] for handle in ready)
        return not self.pending

    def close(self):
        for handle in self.handles:
            os.close(handle)
        if self.queue:
            self.queue.close()


@unittest.skipUnless((sys.platform == 'linux' and hasattr(os, 'pidfd_open'))
                     or (sys.platform == 'darwin' and hasattr(select, 'kqueue')),
                     'Linux pidfd or macOS kqueue process observation required')
class PosixPipeTests(unittest.TestCase):
    def exercise(self, mode='pass', deadline=None, joined=False, large=False,
                 following=False, mutant=False):
        with tempfile.TemporaryDirectory(prefix='isolated-posix-pipes-') as temporary:
            root = Path(temporary)
            scripts, tests = root / 'scripts', root / 'tests'
            scripts.mkdir()
            tests.mkdir()
            source = (ROOT / 'scripts/run_isolated_tests.py').read_text(encoding='utf-8')
            if mutant:
                marker = '\ndef run_modules('
                self.assertEqual(source.count(marker), 1)
                source = source.replace(marker, '\ndef stop_module(process):\n'
                                        '    process.wait(timeout=2)\n' + marker)
            script = scripts / 'run_isolated_tests.py'
            script.write_text(source, encoding='utf-8')
            module = MODULE.replace('stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL',
                                    'stdout=None, stderr=None')
            solver = SOLVER.replace('stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL',
                                    'stdout=None, stderr=None')
            # Retain the fixture Popen for the lifetime of the test case.
            module = module.replace('        for _ in range(2000):',
                                    '        self.child = child\n        for _ in range(2000):', 1)
            if mode == 'early':
                module = module.replace('        if (root / "fail").exists():',
                                        '        os._exit(0)\n        if (root / "fail").exists():')
            if large:
                module = module.replace('        print("literal module output", flush=True)',
                    '        sys.stdout.buffer.write(b"L" * 100000); sys.stdout.flush()\n'
                    '        sys.stderr.buffer.write(b"PIPEERR\\0" * 12500); sys.stderr.flush()\n'
                    '        time.sleep(.4)\n'
                    '        sys.stdout.buffer.write(b"R" * 100000); sys.stdout.flush()\n'
                    '        print("literal module output", flush=True)')
            (tests / 'test_fixture.py').write_text(module, encoding='utf-8')
            (root / 'solver.py').write_text(solver, encoding='utf-8')
            if following:
                (tests / 'test_z_follow.py').write_text(
                    'import unittest\nclass T(unittest.TestCase):\n'
                    ' def test_ok(self): print("following module output", flush=True)\n')
            if mode == 'fail':
                (root / 'fail').touch()
            if joined:
                (root / 'join').touch()
            argv = [sys.executable, '-B', str(script), '--workers', '1']
            if deadline is not None:
                argv += ['--module-timeout', str(deadline)]
            process = subprocess.Popen(argv, cwd=root, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, start_new_session=True)
            pids, observer = [], None
            try:
                await_file(root / 'ready.json')
                pids = json.loads((root / 'ready.json').read_bytes())
                self.assertEqual(len(set(pids)), 3)
                self.assertEqual([os.getpgid(pid) for pid in pids], [pids[0]] * 3)
                observer = ExitObserver(pids)
                self.assertFalse(observer.stopped(), 'fixture must still be alive at readiness')
                if mode == 'cancel':
                    process.send_signal(signal.SIGINT)
                elif mode != 'timeout':
                    (root / 'module-release').touch()
                out, err = process.communicate(timeout=8)
                quiet = observer.stopped(1)
                return process.returncode, out, err, quiet
            finally:
                (root / 'module-release').touch()
                (root / 'solver-release').touch()
                # Independent cleanup also contains the deliberately broken runner.
                for group in pids[:1] + [process.pid]:
                    try:
                        os.killpg(group, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                process.communicate(timeout=5)
                if observer:
                    try:
                        end = time.monotonic() + 5
                        while not observer.stopped(.1) and time.monotonic() < end:
                            pass
                        self.assertTrue(observer.stopped(), 'fixture cleanup failed')
                    finally:
                        observer.close()

    def test_success_without_deadline_stops_pipe_holders_and_runs_next_module(self):
        code, out, err, quiet = self.exercise(following=True)
        self.assertEqual(code, 0, err.decode())
        self.assertIn(b'PASS all 2 test modules', out)
        self.assertLess(out.index(b'literal module output'), out.index(b'following module output'))
        self.assertTrue(quiet)

    def test_failed_module_keeps_failure_instead_of_timeout(self):
        code, out, err, quiet = self.exercise(mode='fail', deadline=5)
        self.assertEqual(code, 1, err.decode())
        self.assertIn(b'literal module failure', err)
        self.assertNotIn(b'Module timeout', err)
        self.assertNotIn(b'PASS all', out)
        self.assertTrue(quiet)

    def test_zero_exit_without_completion_receipt_is_rejected(self):
        code, out, err, quiet = self.exercise(mode='early', deadline=5)
        self.assertEqual(code, 1, err.decode())
        self.assertIn(b'Incomplete unittest run', err)
        self.assertNotIn(b'Module timeout', err)
        self.assertNotIn(b'PASS all', out)
        self.assertTrue(quiet)

    def test_joined_completion_retains_success(self):
        code, out, err, quiet = self.exercise(joined=True)
        self.assertEqual(code, 0, err.decode())
        self.assertIn(b'PASS all 1 test modules', out)
        self.assertTrue(quiet)

    def test_full_output_survives_repeated_capture_timeouts(self):
        code, out, err, quiet = self.exercise(large=True, deadline=5)
        self.assertEqual(code, 0, err.decode())
        self.assertEqual(out, b'Checking test_fixture.py\n' + b'L' * 100000
                         + b'R' * 100000 + b'literal module output\n'
                         + b'PASS all 1 test modules in isolated interpreters\n')
        self.assertIn(b'PIPEERR\0' * 12500, err)
        self.assertEqual(err.count(b'\0'), 12500)
        self.assertTrue(quiet)

    def test_live_module_still_times_out_and_stops_tree(self):
        code, out, err, quiet = self.exercise(mode='timeout', deadline=2)
        self.assertEqual(code, 1, err.decode())
        self.assertIn(b'Module timeout after 2s', err)
        self.assertNotIn(b'PASS all', out)
        self.assertTrue(quiet)

    def test_cancellation_still_stops_captured_tree(self):
        code, out, err, quiet = self.exercise(mode='cancel')
        self.assertNotEqual(code, 0)
        self.assertIn(b'KeyboardInterrupt', err)
        self.assertNotIn(b'PASS all', out)
        self.assertTrue(quiet)

    def test_omitted_group_cleanup_cannot_report_success(self):
        code, out, err, quiet = self.exercise(mutant=True)
        self.assertNotEqual(code, 0)
        self.assertIn(b'TimeoutExpired', err)
        self.assertNotIn(b'PASS all', out)
        self.assertFalse(quiet, 'mutation must leave observed descendants alive')


class DeadlinePrecedenceTests(unittest.TestCase):
    def test_elapsed_budget_wins_over_newly_observed_exit(self):
        spec = importlib.util.spec_from_file_location('pipe_deadline_runner',
                                                    ROOT / 'scripts/run_isolated_tests.py')
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        child = Mock(returncode=0)
        child.poll.return_value = 0
        child.communicate.side_effect = [subprocess.TimeoutExpired('fixture', 1),
                                         (b'late output', b'OK')]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch.object(runner.subprocess, 'Popen', return_value=child), \
                    patch.object(runner, 'stop_module') as stop, \
                    patch.object(runner.time, 'monotonic', side_effect=[0, 0, 2]):
                rows = runner.run_modules([root / 'test_late.py'], tests_dir=root,
                                          cwd=root, workers=1, module_timeout=1)
        self.assertEqual(rows[0][1], 124)
        self.assertIn(b'Module timeout after 1s', rows[0][3])
        self.assertEqual(rows[0][2], b'late output')
        stop.assert_called_once_with(child)

    @unittest.skipUnless(os.name == 'posix', 'POSIX leader observation')
    def test_exit_poll_crossing_deadline_cannot_admit_late_completion(self):
        spec = importlib.util.spec_from_file_location('pipe_poll_runner',
                                                    ROOT / 'scripts/run_isolated_tests.py')
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        clock = [0]
        child = Mock(returncode=0)
        def exited_after_budget():
            clock[0] = 2  # A scheduling pause while observing the leader's exit.
            return 0
        child.poll.side_effect = exited_after_budget
        child.communicate.side_effect = [subprocess.TimeoutExpired('fixture', 1),
                                         (b'late output', b'OK')]
        def launch(argv, **kwargs):
            Path(argv[-1]).write_bytes(runner.COMPLETED)
            return child
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch.object(runner.subprocess, 'Popen', side_effect=launch), \
                    patch.object(runner, 'stop_module') as stop, \
                    patch.object(runner.time, 'monotonic', side_effect=lambda: clock[0]):
                rows = runner.run_modules([root / 'test_late.py'], tests_dir=root,
                                          cwd=root, workers=1, module_timeout=1)
        self.assertEqual(rows[0][1], 124)
        self.assertIn(b'Module timeout after 1s', rows[0][3])
        stop.assert_called_once_with(child)


if __name__ == '__main__':
    unittest.main()
