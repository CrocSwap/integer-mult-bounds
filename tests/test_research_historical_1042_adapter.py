"""Historical replay must retain old bytes without freezing live documentation."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "historical_1042_adapter", ROOT / "research/historical-1042-link/historical_replay.py")
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)


class Historical1042AdapterTests(unittest.TestCase):
    def test_publication_manifest_is_available_in_head_history(self):
        # A locally cached fork commit can satisfy cat-file while remaining
        # absent from upstream CI's full checkout. Require reachable history.
        subprocess.run(["git", "--no-replace-objects", "merge-base",
                        "--is-ancestor", A.PUBLICATION, "HEAD"],
                       cwd=ROOT, check=True, capture_output=True)
        raw = A.git_bytes(ROOT, A.PUBLICATION + ":" + A.PACKAGE + "/SOURCES.json")
        self.assertEqual(A.blob_id(raw), A.ORIGINAL["SOURCES.json"])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.data = b"historical input\n"
        (self.root / "fixture.txt").write_bytes(self.data)
        self.git("add", "fixture.txt")
        self.git("commit", "-qm", "Frozen fixture")
        self.base = self.git("rev-parse", "HEAD").decode().strip()
        self.row = {"path": "fixture.txt", "git_blob": A.blob_id(self.data),
                    "sha256": hashlib.sha256(self.data).hexdigest()}

    def git(self, *args, input=None, env=None):
        return subprocess.run(["git", *args], cwd=self.root, input=input, env=env,
                              check=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).stdout

    def test_exact_historical_bytes_ignore_live_edits(self):
        (self.root / "fixture.txt").write_bytes(b"new current text\n")
        self.assertEqual(A.authenticated_input(self.root, self.base, self.row), self.data)
        self.assertEqual((self.root / "fixture.txt").read_bytes(), b"new current text\n")

    def test_wrong_hash_and_wrong_blob_reject(self):
        for field in ("git_blob", "sha256"):
            row = dict(self.row)
            row[field] = "0" * len(row[field])
            with self.assertRaises(ValueError):
                A.authenticated_input(self.root, self.base, row)

    def test_missing_history_fails_closed(self):
        with self.assertRaises(subprocess.CalledProcessError):
            A.authenticated_input(self.root, "0" * 40, self.row)

    def test_git_replacement_cannot_substitute_evidence(self):
        replacement = self.git("hash-object", "-w", "--stdin", input=b"forged\n").decode().strip()
        self.git("replace", self.row["git_blob"], replacement)
        self.assertEqual(A.authenticated_input(self.root, self.base, self.row), self.data)
        env = dict(os.environ, GIT_REPLACE_REF_BASE="refs/alternate-replacements/")
        self.git("update-ref", env["GIT_REPLACE_REF_BASE"] + self.row["git_blob"], replacement)
        with patch.dict(os.environ, env):
            self.assertEqual(A.authenticated_input(self.root, self.base, self.row), self.data)

    def test_noncanonical_paths_and_bases_reject(self):
        for path in ("../escape", "/absolute", "a/../b", "a//b", "a\\b", "a\0b"):
            with self.assertRaises(ValueError):
                A.checked_path(path)
        with self.assertRaises(ValueError):
            A.authenticated_input(self.root, "HEAD", self.row)

    def test_frozen_manifest_guard_is_not_only_json_parsing(self):
        with patch.object(A, "git_bytes", return_value=b'{"files": []}'):
            with self.assertRaisesRegex(ValueError, "Original manifest changed"):
                A.collect(self.root, self.root)


if __name__ == "__main__":
    unittest.main()
