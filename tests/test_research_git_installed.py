"""Exercise the installed Git's actual protocol, including Git-only path names.

Complements Nick Petalas's simulated option-rejection tests and the Windows
pipe/deadline work by Mihir Srivastava and Brian / JoyboyBrian. Object-tree
fixtures follow the existing exporter tests. Prepared for Mihir Srivastava
with substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import closing, contextmanager
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "installed_git_package", ROOT / "scripts/research_package.py")
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)


class InstalledGitTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.payloads = {
            "empty": b"",
            "binary": b"\x00\xff\r\n" * 65537,
            "space name": b"spaces\n",
            "unicode-\u03ba": b"unicode path\n",
            "line\nname": b"literal LF\x00\xff",
            "carriage\rname": b"literal CR\x00\xff",
            "pair\r\nname": b"literal CRLF\x00\xff",
        }

    def git(self, *args, data=None):
        return subprocess.run(["git", *args], cwd=self.root, input=data,
                              capture_output=True, check=True, timeout=15,
                              env=PACKAGE.git_source_env()).stdout

    def fixture(self, algorithm="sha1"):
        self.git("init", "-q", "--object-format=" + algorithm)
        objects, entries = {}, []
        for name, data in sorted(self.payloads.items()):
            oid = self.git("hash-object", "-w", "--stdin", data=data).decode().strip()
            expected = hashlib.new(algorithm, b"blob " + str(len(data)).encode()
                                   + b"\0" + data).hexdigest()
            self.assertEqual(oid, expected)
            objects[name] = oid
            entries.append(f"100644 blob {oid}\t{name}\0".encode("utf-8"))
        nested = self.git("mktree", "-z", data=(
            f"100644 blob {objects['empty']}\tleaf\0".encode())).decode().strip()
        entries.append(f"040000 tree {nested}\tdir\0".encode())
        tree = self.git("mktree", "-z", data=b"".join(entries)).decode().strip()
        commit = self.git("-c", "user.name=Fixture", "-c",
                          "user.email=fixture@example.invalid", "commit-tree",
                          tree, "-m", "Git-only names").decode().strip()
        self.git("update-ref", "HEAD", commit)
        # No checkout or OS filename translation participates in this fixture.
        self.assertEqual({path.name for path in self.root.iterdir()}, {".git"})
        names = sorted([*self.payloads, "dir/leaf"])
        self.assertEqual(self.git("ls-tree", "-r", "-z", "--name-only", "HEAD"),
                         "".join(name + "\0" for name in names).encode("utf-8"))
        return objects

    def installed_protocol(self):
        probe = subprocess.run(["git", "cat-file", "--batch", "-z"],
                               cwd=self.root, input=b"", capture_output=True,
                               timeout=15, env=PACKAGE.git_source_env())
        self.assertIn(probe.returncode, (0, 129), probe.stderr)
        self.assertEqual(probe.stdout, b"")
        return probe.returncode == 0

    @contextmanager
    def observe(self, wait_for_probe_exit=False):
        """Record launches without replacing an executable, reply or pipe."""
        real_popen = subprocess.Popen
        calls, children = [], []

        def start(argv, **kwargs):
            calls.append(list(argv))
            child = real_popen(argv, **kwargs)
            children.append(child)
            if wait_for_probe_exit and argv == ["git", "cat-file", "--batch", "-z"]:
                # The actual old binary rejects the option. Delay returning its
                # handle until it exits to exercise the native closed pipe too.
                self.assertEqual(child.wait(timeout=15), 129)
            return child

        try:
            with patch.object(PACKAGE.subprocess, "Popen", side_effect=start):
                yield calls
        finally:
            try:
                self.assertTrue(all(child.poll() is not None for child in children))
                self.assertTrue(all(stream is None or stream.closed for child in children
                                    for stream in (child.stdin, child.stdout, child.stderr)))
            finally:
                # Check ownership before fallback teardown: teardown must not
                # manufacture a pass, but a regression must not leak children.
                for child in children:
                    if child.poll() is None:
                        child.kill()
                        child.wait(timeout=5)
                    for stream in (child.stdin, child.stdout, child.stderr):
                        if stream is not None and not stream.closed:
                            try:
                                stream.close()
                            except OSError:
                                pass

    def assert_protocol(self, calls, supports_nul):
        batches = [args for args in calls if args[:3] == ["git", "cat-file", "--batch"]]
        expected = [["git", "cat-file", "--batch", "-z"]]
        if not supports_nul:
            expected.append(["git", "cat-file", "--batch"])
        self.assertEqual(batches, expected)

    def check_exact_objects(self, algorithm):
        objects = self.fixture(algorithm)
        supports_nul = self.installed_protocol()
        names = [*self.payloads, "empty"]
        expected = [(objects[name], self.payloads[name]) for name in names]
        before = set(threading.enumerate())
        with self.observe(wait_for_probe_exit=not supports_nul) as calls, closing(PACKAGE.git_blobs(
                self.root, ("HEAD:" + name for name in names))) as rows:
            actual = []
            for row in rows:
                actual.append(row)
                self.assertEqual(set(threading.enumerate()), before)
        self.assertEqual(actual, expected)
        self.assert_protocol(calls, supports_nul)
        resolutions = [args for args in calls if args[:2] == ["git", "rev-parse"]]
        expected_resolutions = [] if supports_nul else [
            ["git", "rev-parse", "--verify", "--end-of-options", "HEAD:" + name]
            for name in names if "\r" in name or "\n" in name]
        self.assertEqual(resolutions, expected_resolutions)
        self.assertEqual(set(threading.enumerate()), before)

    def test_installed_git_exact_sha1_objects_and_literal_line_separators(self):
        self.check_exact_objects("sha1")

    def test_installed_git_exact_sha256_objects_and_literal_line_separators(self):
        self.check_exact_objects("sha256")

    def test_installed_git_early_close_does_not_consume_later_requests(self):
        objects = self.fixture()
        supports_nul = self.installed_protocol()
        consumed = []

        def requests():
            for name in ("empty", "absent"):
                consumed.append(name)
                yield "HEAD:" + name

        with self.observe() as calls, closing(PACKAGE.git_blobs(self.root, requests())) as rows:
            self.assertEqual(next(rows), (objects["empty"], b""))
        self.assertEqual(consumed, ["empty"])
        self.assert_protocol(calls, supports_nul)

    def test_installed_git_rejects_missing_tree_and_nul_requests(self):
        self.fixture()
        supports_nul = self.installed_protocol()
        for spec in ("HEAD:absent", "HEAD:dir", "HEAD:empty\0HEAD:binary"):
            with self.subTest(spec=spec), self.observe() as calls:
                with self.assertRaisesRegex(ValueError, "missing or non-blob|invalid Git object"):
                    list(PACKAGE.git_blobs(self.root, [spec]))
            if "\0" in spec:
                self.assertEqual(calls, [["git", "cat-file", "--batch", "-z"]])
            else:
                self.assert_protocol(calls, supports_nul)


if __name__ == "__main__":
    unittest.main()
