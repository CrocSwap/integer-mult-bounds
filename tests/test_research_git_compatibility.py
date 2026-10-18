"""Exact pin reads on Git versions without cat-file --batch -z."""
import hashlib
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing, contextmanager
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("git_compat_package", ROOT / "scripts/research_package.py")
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)


def blob_id(payload):
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()


class GitCompatibilityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        PACKAGE.git(self.root, "init", "-q", "--object-format=sha1")
        self.payloads = {"empty": b"", "space name": b"alpha\n", "unicode-κ": b"omega",
                         "binary": b"\0\n\xff" * 65537}
        (self.root / "dir").mkdir()
        (self.root / "dir/file").write_bytes(b"nested")
        for name, payload in self.payloads.items():
            (self.root / name).write_bytes(payload)
        self.commit()

    def commit(self):
        PACKAGE.git(self.root, "-c", "core.autocrlf=false", "add", ".")
        PACKAGE.git(self.root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                    "-c", "maintenance.auto=false", "-c", "gc.auto=0", "commit", "-qm", "fixture")

    @contextmanager
    def older_git(self, status=129, exited_before_write=False):
        """Only model option rejection; actual Git serves every fallback byte."""
        real_popen = subprocess.Popen
        calls, children = [], []

        def start(argv, **kwargs):
            calls.append(argv)
            unsupported = argv == ["git", "cat-file", "--batch", "-z"]
            if unsupported:
                argv = [sys.executable, "-c", f"import sys; sys.exit({status})"]
            child = real_popen(argv, **kwargs)
            if unsupported and exited_before_write:
                child.wait(timeout=10)
            children.append(child)
            return child

        with patch.object(PACKAGE.subprocess, "Popen", side_effect=start):
            yield calls, children
        self.assertTrue(all(child.poll() is not None for child in children))

    def test_unsupported_option_keeps_exact_empty_binary_unicode_and_duplicate_blobs(self):
        names = [*self.payloads, "empty"]
        with self.older_git() as (calls, _):
            actual = list(PACKAGE.git_blobs(self.root, ["HEAD:" + name for name in names]))
        self.assertEqual(actual, [(blob_id(self.payloads[name]), self.payloads[name]) for name in names])
        self.assertEqual(calls, [["git", "cat-file", "--batch", "-z"], ["git", "cat-file", "--batch"]])

    @unittest.skipIf(os.name == "nt", "Windows filenames cannot contain CR or LF")
    def test_line_separators_are_resolved_as_one_object_before_legacy_batching(self):
        names = ["line\nname", "carriage\rname"]
        for name in names:
            (self.root / name).write_bytes(b"literal " + name.encode())
        self.commit()
        with self.older_git() as (calls, _):
            actual = list(PACKAGE.git_blobs(self.root, ["HEAD:" + name for name in names]))
        payloads = [b"literal " + name.encode() for name in names]
        self.assertEqual(actual, [(blob_id(payload), payload) for payload in payloads])
        resolutions = [call for call in calls if call[:2] == ["git", "rev-parse"]]
        self.assertEqual(resolutions, [["git", "rev-parse", "--verify", "--end-of-options", "HEAD:" + name]
                                       for name in names])

    def test_sha256_repository_keeps_64_character_object_ids(self):
        root = self.root / "sha256"
        root.mkdir()
        PACKAGE.git(root, "init", "-q", "--object-format=sha256")
        (root / "data").write_bytes(b"payload")
        oid = PACKAGE.git(root, "hash-object", "-w", "--", "data").decode().strip()
        self.assertEqual(oid, hashlib.sha256(b"blob 7\0payload").hexdigest())
        with self.older_git():
            self.assertEqual(list(PACKAGE.git_blobs(root, [oid])), [(oid, b"payload")])

    def test_option_rejection_before_first_write_handles_broken_pipe(self):
        with self.older_git(exited_before_write=True):
            actual = list(PACKAGE.git_blobs(self.root, ["HEAD:empty"]))
        self.assertEqual(actual, [(blob_id(b""), b"")])

    def test_empty_inventory_starts_no_process(self):
        with patch.object(PACKAGE.subprocess, "Popen", side_effect=AssertionError("unexpected Git process")):
            self.assertEqual(list(PACKAGE.git_blobs(self.root, [])), [])

    def test_missing_blob_tree_and_nul_request_still_reject(self):
        for spec in ("HEAD:absent", "HEAD:dir", "HEAD:empty\0HEAD:binary"):
            with (self.subTest(spec=spec), self.older_git(),
                  self.assertRaisesRegex(ValueError, "missing or non-blob|invalid Git object")):
                list(PACKAGE.git_blobs(self.root, [spec]))

    def test_non_usage_exit_does_not_retry(self):
        with (self.older_git(status=7) as (calls, _),
              self.assertRaisesRegex(ValueError, "missing or non-blob")):
            list(PACKAGE.git_blobs(self.root, ["HEAD:empty"]))
        self.assertEqual(len(calls), 1)

    def test_usage_exit_after_a_valid_blob_does_not_retry(self):
        reply = blob_id(b"").encode() + b" blob 0\n\n"
        code = ("import sys\n"
                "if sys.stdin.buffer.read(11) != b'HEAD:empty\\0': sys.exit(8)\n"
                f"sys.stdout.buffer.write({reply!r}); sys.stdout.buffer.flush()\n"
                "if sys.stdin.buffer.read(12) != b'HEAD:binary\\0': sys.exit(8)\n"
                "sys.exit(129)\n")
        real_popen = subprocess.Popen
        children = []

        def start(argv, **kwargs):
            child = real_popen([sys.executable, "-c", code], **kwargs)
            children.append(child)
            return child

        with (patch.object(PACKAGE.subprocess, "Popen", side_effect=start),
              closing(PACKAGE.git_blobs(self.root, ["HEAD:empty", "HEAD:binary"])) as rows):
            self.assertEqual(next(rows), (blob_id(b""), b""))
            with self.assertRaisesRegex(ValueError, "missing or non-blob"):
                next(rows)
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].poll(), 129)

    def test_early_close_reaps_both_processes_without_reading_later_specs(self):
        with (self.older_git() as (calls, _),
              closing(PACKAGE.git_blobs(self.root, iter(["HEAD:empty", "HEAD:absent"]))) as rows):
            self.assertEqual(next(rows), (blob_id(b""), b""))
        self.assertEqual(len(calls), 2)

    def test_each_invocation_rechecks_the_current_commit(self):
        with self.older_git():
            before = list(PACKAGE.git_blobs(self.root, ["HEAD:empty"]))
            (self.root / "empty").write_bytes(b"changed")
            self.commit()
            after = list(PACKAGE.git_blobs(self.root, ["HEAD:empty"]))
        self.assertEqual(before, [(blob_id(b""), b"")])
        self.assertEqual(after, [(blob_id(b"changed"), b"changed")])


if __name__ == "__main__":
    unittest.main()
