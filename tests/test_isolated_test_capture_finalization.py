"""Observe real capture ownership before independent fixture cleanup.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('capture_runner', ROOT / 'scripts/run_isolated_tests.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class CaptureFinalizationTests(unittest.TestCase):
    def exercise(self, *, close_failure=False, stop_failure=False, retained_reader=False, timeout=False):
        children, original_closes = [], []
        reader, writer, timer = None, None, None
        released = threading.Event()
        real_popen, real_stop = subprocess.Popen, runner.stop_module
        marker = OSError('communication failed after capture started')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            module = root / 'test_wait.py'
            module.write_text('import time,unittest\nclass T(unittest.TestCase):\n'
                              ' def test_wait(self): time.sleep(30)\n', encoding='utf-8')

            def launch(*args, **kwargs):
                process = real_popen(*args, **kwargs)
                children.append(process)
                communicate = process.communicate
                original_closes.extend((process.stdout.close, process.stderr.close))

                def fail_after_capture(*args, **kwargs):
                    if timeout:
                        raise subprocess.TimeoutExpired(process.args, .05,
                                                        output=b'captured', stderr=b'diagnostic')
                    # Start actual capture (including Windows reader threads), then fail.
                    try:
                        communicate(timeout=.05)
                    except subprocess.TimeoutExpired:
                        raise marker from None
                    self.fail('blocking fixture unexpectedly completed')

                process.communicate = fail_after_capture
                return process

            def stop(process):
                nonlocal reader, writer, timer
                real_stop(process)
                if close_failure or retained_reader:
                    self.assertEqual(runner.close_captures(process), [])
                if close_failure:
                    def denied_close():
                        raise OSError('capture close denied')
                    process.stdout.close = denied_close
                if retained_reader:
                    read_fd, writer = os.pipe()
                    process.stdout = os.fdopen(read_fd, 'rb')
                    original_closes.append(process.stdout.close)
                    started = threading.Event()
                    def read():
                        started.set()
                        process.stdout.read()
                    reader = threading.Thread(target=read)
                    process.stdout_thread = reader
                    reader.start()
                    self.assertTrue(started.wait(1))
                    def release():
                        released.set()
                        os.close(writer)
                    # A broken unbounded close must fail without hanging the suite.
                    timer = threading.Timer(4, release)
                    timer.start()

            try:
                with patch.object(runner.subprocess, 'Popen', side_effect=launch), \
                        patch.object(runner, 'stop_module',
                                     side_effect=PermissionError('process stop denied')
                                     if stop_failure else stop):
                    if timeout:
                        rows = runner.run_modules([module], tests_dir=root, cwd=root,
                                                  workers=1, module_timeout=.01)
                        self.assertEqual(rows[0][1:3], (124, b'captured'))
                        notes = rows[0][3].decode('utf-8')
                        self.assertIn('diagnostic', notes)
                        self.assertIn('Module timeout', notes)
                    else:
                        with self.assertRaises(OSError) as caught:
                            runner.run_modules([module], tests_dir=root, cwd=root, workers=1)
                        self.assertIs(caught.exception, marker)
                        notes = '\n'.join(getattr(marker, '__notes__', []))
                self.assertEqual(len(children), 1)
                child = children[0]
                if stop_failure:
                    self.assertIn('process stop denied', notes)
                    self.assertIsNone(child.poll(), 'failed cleanup must remain observable')
                    self.assertFalse(child.stdout.closed)
                    self.assertFalse(child.stderr.closed)
                else:
                    self.assertIsNotNone(child.poll(), 'owner must be reaped before returning')
                    self.assertTrue(child.stderr.closed, 'continue closing after one close fails')
                    if retained_reader:
                        self.assertIn('stdout capture reader did not stop', notes)
                        self.assertFalse(released.is_set(), 'close blocked on a retained reader')
                        self.assertTrue(reader.is_alive())
                        self.assertFalse(child.stdout.closed)
                    elif close_failure:
                        self.assertIn('capture close denied', notes)
                    else:
                        self.assertTrue(child.stdout.closed, 'capture still owned at API return')
                        self.assertEqual(notes, '')
            finally:
                # Never credit this independent teardown as runner cleanup.
                for child in children:
                    real_stop(child)
                if timer is not None:
                    timer.cancel()
                    timer.join()
                    if not released.is_set():
                        os.close(writer)
                    reader.join(2)
                    self.assertFalse(reader.is_alive(), 'fixture reader cleanup failed')
                for close in original_closes:
                    close()

    def test_timeout_with_retained_reader_keeps_status_bytes_and_cleanup_diagnostic(self):
        self.exercise(retained_reader=True, timeout=True)

    def test_unbounded_close_mutant_is_rejected(self):
        def unbounded(process):
            process.stdout.close()
            process.stderr.close()
            return []
        with patch.object(runner, 'close_captures', side_effect=unbounded):
            with self.assertRaisesRegex(AssertionError, 'stdout capture reader did not stop'):
                self.exercise(retained_reader=True)

    def test_stopped_owner_with_retained_reader_does_not_block_capture_close(self):
        self.exercise(retained_reader=True)

    def test_started_capture_is_closed_after_worker_failure(self):
        self.exercise()

    def test_close_failure_preserves_worker_error_and_closes_other_capture(self):
        self.exercise(close_failure=True)

    def test_stop_failure_does_not_block_on_an_active_capture_reader(self):
        self.exercise(stop_failure=True)


if __name__ == '__main__':
    unittest.main()
