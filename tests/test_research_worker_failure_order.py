"""Unexpected worker errors must not wait for an earlier module's result.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import importlib.util
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import test_isolated_test_cancellation as cancellation
from test_isolated_test_cancellation import BLOCK, SOLVER, wait_for
from test_research_isolated_test_posix_pipes import ExitObserver

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('failure_order_runner', ROOT / 'scripts/run_isolated_tests.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class ResultOrderTests(unittest.TestCase):
    def test_reverse_completion_preserves_requested_order_and_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first, second = root / 'test_z.py', root / 'test_a.py'
            first.write_text('import pathlib,time,sys,unittest\n'
                'class T(unittest.TestCase):\n'
                ' def test_first(self):\n'
                '  while not pathlib.Path("second-completed").exists(): time.sleep(.01)\n'
                '  sys.stdout.buffer.write(b"first\\0bytes");sys.stdout.flush()\n')
            second.write_text('import pathlib,sys,unittest\n'
                'class T(unittest.TestCase):\n'
                ' def test_second(self):\n'
                '  sys.stdout.buffer.write(b"second\\0bytes");sys.stdout.flush()\n'
                '  pathlib.Path("second-completed").touch()\n')
            rows = runner.run_modules([first, second], tests_dir=root, cwd=root,
                                      workers=2, module_timeout=10)
            self.assertEqual([row[0] for row in rows], [first, second])
            self.assertEqual([row[1] for row in rows], [0, 0])
            self.assertEqual([row[2] for row in rows], [b'first\0bytes', b'second\0bytes'])

    def test_nonzero_test_result_does_not_cancel_other_modules(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first, second = root / 'test_a.py', root / 'test_b.py'
            first.write_text('import pathlib,time,sys,unittest\n'
                'class T(unittest.TestCase):\n'
                ' def test_first(self):\n'
                '  pathlib.Path("first-ready").touch()\n'
                '  while not pathlib.Path("second-failed").exists(): time.sleep(.01)\n'
                '  time.sleep(.2)\n'
                '  sys.stdout.buffer.write(b"earlier module completed\\n");sys.stdout.flush()\n')
            second.write_text('import pathlib,time,unittest\n'
                'class T(unittest.TestCase):\n'
                ' def test_second(self):\n'
                '  while not pathlib.Path("first-ready").exists(): time.sleep(.01)\n'
                '  pathlib.Path("second-failed").touch()\n'
                '  self.fail("ordinary test failure")\n')
            rows = runner.run_modules([first, second], tests_dir=root, cwd=root,
                                      workers=2, module_timeout=10)
            self.assertEqual([row[1] for row in rows], [0, 1])
            self.assertEqual(rows[0][2], b'earlier module completed\n')
            self.assertIn(b'ordinary test failure', rows[1][3])


@unittest.skipUnless((sys.platform == 'linux' and hasattr(os, 'pidfd_open'))
                     or (sys.platform == 'darwin' and hasattr(select, 'kqueue')),
                     'requires retained POSIX native process-exit observations')
class FailureOrderTests(unittest.TestCase):
    def exercise(self, boundary, error_type=OSError):
        real_popen = subprocess.Popen
        children, pids, timer, observer = [], [], None, None
        marker = error_type('later worker ' + boundary + ' failure')
        original_stop = runner.stop_module
        failed = False
        with tempfile.TemporaryDirectory(prefix='worker-failure-order-') as temporary:
            root = Path(temporary)
            tests = root / 'tests'; tests.mkdir()
            first = tests / 'test_a_block.py'; first.write_text(BLOCK)
            second = tests / 'test_b_block.py'
            body = BLOCK.replace('module.pid', 'second-module.pid').replace('solver.py', 'second-solver.py')
            if boundary == 'cleanup':
                body = body.replace('root/\'release\'', 'root/\'second-module-release\'')
                body = body.replace('        child.wait(timeout=5)', '')
            second.write_text(body)
            (root / 'solver.py').write_text(SOLVER)
            (root / 'second-solver.py').write_text(
                SOLVER.replace('solver.pid', 'second-solver.pid').replace('ready', 'second-ready'))
            second_owner = None

            def arm():
                nonlocal observer, timer
                self.assertTrue(wait_for(lambda: (root / 'ready').exists()
                                         and (root / 'second-ready').exists()), 'fixture not ready')
                pids.extend(int((root / (name + '.pid')).read_text())
                            for name in ('module', 'solver', 'second-module', 'second-solver'))
                self.assertEqual(len(set(pids)), 4)
                self.assertEqual([os.getpgid(pid) for pid in pids],
                                 [pids[0], pids[0], pids[2], pids[2]])
                observer = ExitObserver(pids)
                self.assertFalse(observer.stopped(), 'fixture work must be alive before failure')
                timer = threading.Timer(3, (root / 'release').touch)
                timer.start()

            def launch(*args, **kwargs):
                nonlocal second_owner
                process = real_popen(*args, **kwargs)
                children.append(process)
                if second.name in args[0]:
                    second_owner = process
                    real_communicate = process.communicate
                    armed = False
                    def communicate(*args, **kwargs):
                        nonlocal armed
                        if not armed:
                            armed = True
                            arm()
                            if boundary == 'communicate':
                                raise marker
                            (root / 'second-module-release').touch()
                        return real_communicate(*args, **kwargs)
                    process.communicate = communicate
                return process

            def stop(process):
                nonlocal failed
                if boundary == 'cleanup' and process is second_owner and not failed:
                    failed = True
                    raise marker
                return original_stop(process)

            try:
                with patch.object(runner.subprocess, 'Popen', side_effect=launch), \
                        patch.object(runner, 'stop_module', side_effect=stop):
                    with self.assertRaises(error_type) as caught:
                        runner.run_modules([first, second], tests_dir=tests, cwd=root, workers=2)
                self.assertIs(caught.exception, marker, 'preserve the exact worker exception')
                self.assertFalse((root / 'release').exists(),
                                 'worker failure waited for the earlier module forced release')
                self.assertTrue(wait_for(lambda: observer.stopped(.1), timeout=3),
                                'owned module or solver survived failure')
                self.assertTrue(all(stream.closed for child in children
                                    for stream in (child.stdout, child.stderr)),
                                'runner returned with owned capture streams open')
            finally:
                if timer is not None:
                    timer.cancel(); timer.join()
                (root / 'release').touch()
                (root / 'second-module-release').touch()
                try:
                    if observer is not None:
                        observer.stopped()
                    for child in children:
                        members = pids[:2] if pids and child.pid == pids[0] else pids[2:]
                        # Retained exit handles avoid signaling a recycled group ID.
                        if observer is None or not set(members).isdisjoint(observer.pending):
                            try:
                                os.killpg(child.pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                        child.wait(timeout=5)
                    if observer is not None:
                        self.assertTrue(wait_for(lambda: observer.stopped(.1), timeout=5),
                                        'independent fixture cleanup failed')
                finally:
                    for child in children:
                        for stream in (child.stdout, child.stderr):
                            stream.close()
                    if observer is not None:
                        observer.close()

    def test_later_pipe_failure_cancels_an_earlier_blocked_module(self):
        self.exercise('communicate')

    def test_later_cleanup_failure_cancels_an_earlier_blocked_module(self):
        self.exercise('cleanup')

    def test_worker_stop_iteration_is_an_error_not_iterator_completion(self):
        self.exercise('communicate', StopIteration)

    def test_worker_base_exception_cancels_other_owned_work(self):
        self.exercise('communicate', SystemExit)

    def test_controlling_exceptions_still_cancel_active_and_queued_work(self):
        class NativeObserver:
            def __init__(self, pid):
                self.observer = ExitObserver([pid])

            def alive(self):
                return not self.observer.stopped()

            def close(self):
                self.observer.close()

        # Run the retained cancellation fixture with this platform's exit handle.
        with patch.object(cancellation, 'ProcessObserver', NativeObserver):
            for failure in (KeyboardInterrupt, RuntimeError):
                with self.subTest(failure=failure.__name__):
                    cancellation.CancellationTests().exercise(failure)

    def test_input_ordered_wait_mutant_is_rejected(self):
        with patch.object(runner, 'as_completed', side_effect=lambda futures: iter(futures), create=True):
            with self.assertRaisesRegex(AssertionError, 'forced release'):
                self.exercise('communicate')


if __name__ == '__main__':
    unittest.main()
