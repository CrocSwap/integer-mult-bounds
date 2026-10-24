"""Closed-stdin errors must retain the exact Git compatibility retry gate.

Builds on Nick Petalas's PR2752 and Douglas Colkitt's package runner.
Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import contextmanager
import errno
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("git_pipe_package", ROOT / "scripts/research_package.py")
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)


class ErrorPipe(io.BytesIO):
    """Inject one specified OS error per operation, while retaining close state."""
    def __init__(self, operations, number, request=1):
        super().__init__()
        self.operations = set(operations)
        self.number = number
        self.request = request
        self.writes = 0

    def fail(self, operation):
        if operation in self.operations and self.writes >= self.request:
            self.operations.remove(operation)
            raise OSError(self.number, "injected stdin " + operation)

    def write(self, data):
        self.writes += 1
        self.fail("write")
        return super().write(data)

    def flush(self):
        self.fail("flush")
        return super().flush()

    def close(self):
        super().close()
        self.fail("close")


class GitPipeErrorTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        PACKAGE.git(self.root, "init", "-q", "--object-format=sha1")
        self.payloads = [b"", b"\x00\xff\r\n" * 4097, b""]
        self.objects = []
        for index, data in enumerate(self.payloads):
            name = "input-" + str(index)
            (self.root / name).write_bytes(data)
            oid = PACKAGE.git(self.root, "hash-object", "-w", "--", name).decode().strip()
            expected = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            self.assertEqual(oid, expected)
            self.objects.append(oid)

    @contextmanager
    def rejected_probe(self, operations, number=errno.EINVAL, status=129,
                       platform="nt", response=b"", request=1, fail_legacy=False):
        """Model the probe only; real Git supplies every successful fallback blob."""
        real_popen = subprocess.Popen
        calls, children, pipes = [], [], []

        def start(argv, **kwargs):
            calls.append(argv)
            probe = (argv == ["git", "cat-file", "--batch", "-z"]
                     or (fail_legacy and argv == ["git", "cat-file", "--batch"]))
            if probe:
                code = f"import sys; sys.stdout.buffer.write({response!r}); sys.exit({status})"
                child = real_popen([sys.executable, "-c", code], **kwargs)
                child.wait(timeout=10)
                child.stdin.close()
                child.stdin = ErrorPipe(operations, number, request)
                pipes.append(child.stdin)
            else:
                child = real_popen(argv, **kwargs)
            children.append(child)
            return child

        def kill_group(pid, signum):
            # The simulated POSIX branch still runs on native Windows. Group
            # ownership itself is tested separately with actual POSIX processes.
            if hasattr(os, "killpg"):
                os.killpg(pid, signum)
            else:
                next(child for child in children if child.pid == pid).kill()

        try:
            with (patch.object(PACKAGE, "os", SimpleNamespace(
                    name=platform, environ=os.environ, killpg=kill_group)),
                  patch.object(PACKAGE.signal, "SIGKILL",
                               getattr(PACKAGE.signal, "SIGKILL", 9), create=True),
                  patch.object(PACKAGE.subprocess, "Popen", side_effect=start)):
                yield calls, pipes
        finally:
            self.assertTrue(all(child.poll() is not None for child in children))
            self.assertTrue(all(child.stdin.closed and child.stdout.closed for child in children))

    def test_windows_einval_retries_only_the_probe_and_preserves_every_blob(self):
        for operations in (("write",), ("flush",), ("close",), ("flush", "close")):
            with self.subTest(operations=operations):
                consumed = []
                def requests():
                    for oid in self.objects:
                        consumed.append(oid)
                        yield oid
                with self.rejected_probe(operations) as (calls, _):
                    actual = list(PACKAGE.git_blobs(self.root, requests()))
                self.assertEqual(actual, list(zip(self.objects, self.payloads)))
                self.assertEqual(consumed, self.objects)
                self.assertEqual(calls, [["git", "cat-file", "--batch", "-z"],
                                         ["git", "cat-file", "--batch"]])

    def test_broken_pipe_retains_the_same_fallback_on_both_platforms(self):
        for platform in ("nt", "posix"):
            with self.subTest(platform=platform), self.rejected_probe(
                    ("write", "close"), number=errno.EPIPE, platform=platform):
                self.assertEqual(list(PACKAGE.git_blobs(self.root, self.objects)),
                                 list(zip(self.objects, self.payloads)))

    def test_unrelated_errors_and_posix_einval_propagate_without_retry(self):
        for platform, number in (("nt", errno.EIO), ("posix", errno.EINVAL)):
            for operation in ("write", "flush", "close"):
                with self.subTest(platform=platform, operation=operation):
                    with self.rejected_probe((operation,), number=number, platform=platform) as (calls, _):
                        with self.assertRaises(OSError) as caught:
                            list(PACKAGE.git_blobs(self.root, self.objects))
                    self.assertEqual(caught.exception.errno, number)
                    self.assertEqual(len(calls), 1)

    def test_windows_einval_with_non_usage_exit_does_not_retry(self):
        for status in (0, 7):
            with self.subTest(status=status), self.rejected_probe(
                    ("flush", "close"), status=status) as (calls, _):
                with self.assertRaisesRegex(ValueError, "missing or non-blob"):
                    list(PACKAGE.git_blobs(self.root, self.objects))
                self.assertEqual(len(calls), 1)

    def test_windows_einval_after_a_valid_response_does_not_retry(self):
        response = self.objects[0].encode() + b" blob 0\n\n"
        with self.rejected_probe(("write", "close"), response=response, request=2) as (calls, _):
            rows = PACKAGE.git_blobs(self.root, self.objects)
            self.assertEqual(next(rows), (self.objects[0], b""))
            with self.assertRaisesRegex(ValueError, "missing or non-blob"):
                next(rows)
            self.assertEqual(len(calls), 1)

    def test_windows_einval_in_the_legacy_reader_does_not_start_a_third_process(self):
        with self.rejected_probe(("flush", "close"), fail_legacy=True) as (calls, _):
            with self.assertRaisesRegex(ValueError, "missing or non-blob"):
                list(PACKAGE.git_blobs(self.root, self.objects))
            self.assertEqual(calls, [["git", "cat-file", "--batch", "-z"],
                                     ["git", "cat-file", "--batch"]])


if __name__ == "__main__":
    unittest.main()
