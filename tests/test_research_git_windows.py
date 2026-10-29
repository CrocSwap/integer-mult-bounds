"""Native Windows ownership at the shared Git reader, before fixture teardown.

Fixtures build on Mihir Srivastava's PR5524 and ywz65's native handle observer.
Integration regressions for josecarlosgonzalezroque-design with substantial
OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import closing
import ctypes
from ctypes import wintypes
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('windows_blob_package', ROOT / 'scripts/research_package.py')
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)

# Retain a native handle: PID reuse and later teardown cannot manufacture PASS.
PRODUCER = r'''
import os, subprocess, sys, time
from pathlib import Path
root, mode = Path(sys.argv[1]), sys.argv[2]
child = subprocess.Popen([sys.executable, '-I', '-S', '-c', 'import time; time.sleep(60)'],
                         stdin=sys.stdin, stdout=sys.stdout, stderr=subprocess.DEVNULL)
(root/'child.pending').write_text(str(child.pid))
(root/'child.pending').replace(root/'child.pid')
while not (root/'observed').exists(): time.sleep(.01)
while sys.stdin.buffer.read(1) not in (bytes([0]), bytes([10]), b''): pass
reply = b'a'*40+b' blob 4\n\x00\xff\r\n\n'
prefix = {'header': b'', 'payload': reply[:-3], 'terminator': reply[:-1]}.get(mode, reply)
sys.stdout.buffer.write(prefix)
sys.stdout.buffer.flush()
os._exit(0)
'''


class ProcessHandle:
    def __init__(self, pid):
        self.api = ctypes.WinDLL('kernel32', use_last_error=True)
        for name, result, args in (
            ('OpenProcess', wintypes.HANDLE, [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]),
            ('WaitForSingleObject', wintypes.DWORD, [wintypes.HANDLE, wintypes.DWORD]),
            ('TerminateProcess', wintypes.BOOL, [wintypes.HANDLE, wintypes.UINT]),
            ('CloseHandle', wintypes.BOOL, [wintypes.HANDLE]),
        ):
            fn = getattr(self.api, name)
            fn.restype, fn.argtypes = result, args
        self.handle = self.api.OpenProcess(0x00100001, False, pid)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())

    def exited(self, timeout=0):
        result = self.api.WaitForSingleObject(self.handle, timeout)
        if result not in (0, 258):
            raise ctypes.WinError(ctypes.get_last_error())
        return result == 0

    def terminate(self):
        if not self.exited():
            if not self.api.TerminateProcess(self.handle, 1):
                raise ctypes.WinError(ctypes.get_last_error())
            if not self.exited(5000):
                raise RuntimeError('fixture descendant did not terminate')

    def close(self):
        self.terminate()
        if not self.api.CloseHandle(self.handle):
            raise ctypes.WinError(ctypes.get_last_error())


@unittest.skipUnless(os.name == 'nt', 'native Windows Job Objects required')
class WindowsGitReaderTests(unittest.TestCase):
    def test_direct_child_mutation_is_rejected(self):
        # Replacing the job owner with direct Popen must fail all six boundaries.
        # The inner fixture still cleans its children after recording failures.
        case = WindowsGitReaderTests('test_descendants_and_consumer_pause_at_the_shared_reader')
        result = unittest.TestResult()
        with patch.object(PACKAGE, '_git_blob_popen', subprocess.Popen):
            case.run(result)
        self.assertEqual(len(result.failures), 6)
        self.assertEqual(result.errors, [])

    def test_descendants_and_consumer_pause_at_the_shared_reader(self):
        for mode in ('success', 'header', 'payload', 'terminator', 'early-close', 'consumer-error'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                real_factory = PACKAGE._git_blob_popen
                handles, gates, guards = [], [], []
                guard_fired = threading.Event()

                def start(argv, **kwargs):
                    process = real_factory(
                        [sys.executable, '-I', '-S', '-c', PRODUCER, str(root), mode], **kwargs)
                    gates.append(process)
                    deadline = time.monotonic() + 5
                    while not (root / 'child.pid').exists():
                        if time.monotonic() >= deadline:
                            process.__exit__(None, None, None)
                            self.fail('descendant readiness timed out')
                        time.sleep(.01)
                    handle = ProcessHandle(int((root / 'child.pid').read_text()))
                    handles.append(handle)
                    self.assertFalse(handle.exited())

                    def guard():
                        guard_fired.set()
                        handle.terminate()
                    timer = threading.Timer(4, guard)
                    guards.append(timer)
                    timer.start()
                    (root / 'observed').touch()
                    return process

                try:
                    with (patch.object(PACKAGE, '_git_blob_popen', side_effect=start),
                          patch.object(PACKAGE, 'GIT_BLOB_RESPONSE_TIMEOUT', .25),
                          closing(PACKAGE.git_blobs(root, ['HEAD:x'])) as rows):
                        if mode in ('header', 'payload', 'terminator'):
                            with self.assertRaises(subprocess.TimeoutExpired):
                                list(rows)
                        elif mode == 'success':
                            self.assertEqual(list(rows), [('a' * 40, b'\0\xff\r\n')])
                        else:
                            self.assertEqual(next(rows), ('a' * 40, b'\0\xff\r\n'))
                            time.sleep(.4)  # Consumer time is outside the response deadline.
                            self.assertFalse(handles[0].exited())
                            if mode == 'consumer-error':
                                with self.assertRaisesRegex(ValueError, 'validation failed'):
                                    with closing(rows):
                                        raise ValueError('validation failed')
                            else:
                                rows.close()
                    self.assertFalse(guard_fired.is_set(), 'fallback teardown rescued the reader')
                    self.assertEqual(len(handles), 1)
                    self.assertTrue(handles[0].exited(1000), 'live descendant before teardown')
                    self.assertTrue(all(g.poll() is not None for g in gates))
                    self.assertTrue(all(g.stdin.closed and g.stdout.closed for g in gates))
                finally:
                    for timer in guards:
                        timer.cancel()
                        timer.join()
                    for handle in handles:
                        handle.close()
                    for gate in gates:
                        gate.__exit__(None, None, None)

    def test_native_launch_errors_do_not_become_blob_errors_or_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            invalid = root / 'invalid.exe'
            invalid.write_bytes(b'not an executable')
            for executable in (root / 'missing.exe', invalid, root):
                with self.subTest(executable=executable.name):
                    argv = [str(executable)]
                    with self.assertRaises(OSError) as direct:
                        subprocess.Popen(argv)
                    real_factory = PACKAGE._git_blob_popen
                    with (patch.object(PACKAGE, '_git_blob_popen',
                                       side_effect=lambda ignored, **kw: real_factory(argv, **kw)) as launch,
                          self.assertRaises(OSError) as wrapped):
                        list(PACKAGE.git_blobs(root, ['HEAD:missing']))
                    fields = ('errno', 'winerror', 'strerror', 'filename', 'filename2')
                    self.assertEqual(type(wrapped.exception), type(direct.exception))
                    self.assertEqual([getattr(wrapped.exception, f) for f in fields],
                                     [getattr(direct.exception, f) for f in fields])
                    self.assertEqual(launch.call_count, 1)

    def test_unicode_argv_environment_cwd_and_binary_output(self):
        with tempfile.TemporaryDirectory(prefix='git-\u03ba-') as temporary:
            root = Path(temporary)
            payload = b'\0\xff\r\n' * 20000
            code = ('import os,sys; from pathlib import Path; '
                    'assert sys.argv[1] == "\u03ba"; assert os.environ["GIT_TEST_VALUE"] == "\u03ba"; '
                    'assert Path.cwd() == Path(sys.argv[2]); '
                    'sys.stdin.buffer.read(1); sys.stdout.buffer.write(b"\\0\\xff\\r\\n"*20000)')
            with PACKAGE._git_blob_popen(
                    [sys.executable, '-I', '-S', '-c', code, '\u03ba', str(root)], cwd=root,
                    env=dict(os.environ, GIT_TEST_VALUE='\u03ba'), stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
                process.stdin.write(b'x')
                process.stdin.close()
                self.assertEqual(process.stdout.read(), payload)
                self.assertEqual(process.wait(timeout=5), 0)

    def test_launched_exit_129_retries_once_with_native_owner(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(['git', 'init', '-q', str(root)], check=True, capture_output=True)
            payload = b'\0\xff\r\n' * 20000
            oid = subprocess.run(['git', 'hash-object', '-w', '--stdin'], cwd=root,
                                 input=payload, capture_output=True, check=True).stdout.decode().strip()
            for status in (0, 1, 7, 129):
                with self.subTest(status=status):
                    real_factory = PACKAGE._git_blob_popen
                    calls = []

                    def start(argv, **kwargs):
                        calls.append(argv)
                        command = ([sys.executable, '-I', '-S', '-c', f'raise SystemExit({status})']
                                   if len(calls) == 1 else argv)
                        return real_factory(command, **kwargs)

                    with patch.object(PACKAGE, '_git_blob_popen', side_effect=start):
                        if status == 129:
                            self.assertEqual(list(PACKAGE.git_blobs(root, [oid, oid])),
                                             [(oid, payload), (oid, payload)])
                        else:
                            with self.assertRaisesRegex(ValueError, 'missing or non-blob'):
                                list(PACKAGE.git_blobs(root, [oid]))
                    expected = [['git', 'cat-file', '--batch', '-z']]
                    if status == 129:
                        expected.append(['git', 'cat-file', '--batch'])
                    self.assertEqual(calls, expected)


if __name__ == '__main__':
    unittest.main()
