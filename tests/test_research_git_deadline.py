"""Real-process deadline boundaries for streaming Git source blobs."""
from contextlib import closing, contextmanager
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("git_deadline_package", ROOT / "scripts/research_package.py")
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)
OID = b"a" * 40


class GitBlobDeadlineTests(unittest.TestCase):
    @contextmanager
    def child(self, body, timeout=0.5):
        real_popen = subprocess.Popen
        children, calls, guards = [], [], []

        def start(argv, **kwargs):
            calls.append(argv)
            code = "from pathlib import Path\nREADY = Path(" + repr(str(ready)) + ")\n" + body
            process = real_popen([sys.executable, "-c", code], **kwargs)
            children.append(process)
            # Bound this regression even when run against the unfixed reader.
            guard = threading.Timer(3, lambda: process.kill() if process.poll() is None else None)
            guard.start()
            guards.append(guard)
            return process

        with tempfile.TemporaryDirectory() as directory:
            ready = Path(directory) / "response-ready"
            try:
                with (patch.object(PACKAGE.subprocess, "Popen", side_effect=start),
                      patch.object(PACKAGE, "GIT_BLOB_RESPONSE_TIMEOUT", timeout, create=True)):
                    yield Path(directory), children, calls
            finally:
                for guard in guards:
                    guard.cancel()
                    guard.join()
                for process in children:
                    if process.poll() is None:
                        process.kill()
                    process.wait(timeout=3)
                    for stream in (process.stdin, process.stdout):
                        if stream is not None and not stream.closed:
                            stream.close()

    def test_header_payload_and_terminator_stalls_timeout_without_fallback(self):
        header = OID + b" blob 4\n"
        for boundary, prefix in (("header", b""), ("payload", header + b"ab"),
                                 ("terminator", header + b"abcd")):
            body = ("import sys,time\n"
                    "while sys.stdin.buffer.read(1) not in (bytes([0]), b''): pass\n"
                    f"sys.stdout.buffer.write({prefix!r}); sys.stdout.buffer.flush()\n"
                    "READY.write_text('response boundary reached')\n"
                    "time.sleep(60)\n")
            with self.subTest(boundary=boundary), self.child(body) as (root, children, calls):
                consumed = []
                def specs():
                    consumed.append("first")
                    yield "HEAD:first"
                    consumed.append("later")
                    yield "HEAD:later"
                started = time.monotonic()
                with self.assertRaises(subprocess.TimeoutExpired):
                    list(PACKAGE.git_blobs(root, specs()))
                self.assertLess(time.monotonic() - started, 2)
                self.assertEqual(consumed, ["first"])
                self.assertEqual(len(calls), 1)
                self.assertIsNotNone(children[0].poll())
                self.assertEqual((root / "response-ready").read_text(), "response boundary reached")

    def test_blocked_request_write_times_out_and_reaps_child(self):
        with self.child("import time; time.sleep(60)") as (root, children, calls):
            with self.assertRaises(subprocess.TimeoutExpired):
                list(PACKAGE.git_blobs(root, ["a" * 2_000_000]))
            self.assertEqual(len(calls), 1)
            self.assertIsNotNone(children[0].poll())

    def test_legacy_batch_payload_stall_also_times_out(self):
        body = ("import sys,time\n"
                "sys.stdin.buffer.readline()\n"
                f"sys.stdout.buffer.write({OID + b' blob 4' + bytes([10]) + b'ab'!r}); sys.stdout.buffer.flush()\n"
                "READY.write_text('response boundary reached')\n"
                "time.sleep(60)\n")
        with self.child(body) as (root, children, calls):
            with self.assertRaises(subprocess.TimeoutExpired):
                list(PACKAGE._git_blob_batch(root, ["HEAD:first"], nul=False))
            self.assertEqual(len(calls), 1)
            self.assertIsNotNone(children[0].poll())
            self.assertEqual((root / "response-ready").read_text(), "response boundary reached")

    def test_delayed_binary_replies_and_suspended_consumer_remain_exact(self):
        payload = b"\0\xffa\n\rZ"
        reply = OID + b" blob 6\n" + payload + b"\n"
        body = ("import sys,time\n"
                "for _ in range(2):\n"
                " while sys.stdin.buffer.read(1) not in (bytes([0]), b''): pass\n"
                " time.sleep(.01)\n"
                f" sys.stdout.buffer.write({reply!r}); sys.stdout.buffer.flush()\n")
        with self.child(body, timeout=0.3) as (root, children, calls):
            with closing(PACKAGE.git_blobs(root, ["HEAD:first", "HEAD:second"])) as rows:
                self.assertEqual(next(rows), (OID.decode(), payload))
                time.sleep(0.45)
                self.assertIsNone(children[0].poll())
                self.assertEqual(next(rows), (OID.decode(), payload))
                with self.assertRaises(StopIteration):
                    next(rows)
            self.assertEqual(len(calls), 1)
            self.assertEqual(children[0].poll(), 0)

    def test_many_real_git_blobs_leave_no_watchdog_threads(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            PACKAGE.git(root, "init", "-q")
            (root / "data").write_bytes(b"binary\0\xff\r\n")
            oid = PACKAGE.git(root, "hash-object", "-w", "--", "data").decode().strip()
            before = set(threading.enumerate())
            with closing(PACKAGE.git_blobs(root, [oid] * 128)) as rows:
                for item in rows:
                    self.assertEqual(item, (oid, b"binary\0\xff\r\n"))
                    self.assertEqual(set(threading.enumerate()), before)
            self.assertEqual(set(threading.enumerate()), before)


if __name__ == "__main__":
    unittest.main()
