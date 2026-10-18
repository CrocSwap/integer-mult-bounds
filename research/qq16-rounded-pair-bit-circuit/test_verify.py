"""Behavioral artifact tests, including a read-only Git-free replay."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def fingerprint(package):
    return {
        p.relative_to(package).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in package.rglob("*")
        if p.is_file()
    }


class Artifacts(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.package = Path(self.directory.name) / "package"
        shutil.copytree(
            PACKAGE, self.package, ignore=shutil.ignore_patterns("__pycache__")
        )

    def replay(self, *arguments):
        return subprocess.run(
            [
                sys.executable,
                "-Werror",
                "-I",
                "-O",
                "-B",
                str(self.package / "verify.py"),
                *arguments,
            ],
            cwd=self.directory.name,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )

    def test_git_free_read_only(self):
        before = fingerprint(self.package)
        result = self.replay()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_QQ16_ROUNDED_PAIR_BIT_CIRCUIT", result.stdout)
        self.assertEqual(fingerprint(self.package), before)

    def test_source_corruption(self):
        path = self.package / "source/format-verify.py"
        path.write_bytes(path.read_bytes() + b"\n# changed source\n")
        result = self.replay()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source hash mismatch", result.stderr)

    def test_typed_receipt_corruption(self):
        path = self.package / "RESULT.json"
        data = json.loads(path.read_text())
        data["invoice"]["runtime_examples"][0]["input_bits"] = True
        path.write_text(json.dumps(data))
        result = self.replay()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("receipt mismatch", result.stderr)

    def test_missing_receipt(self):
        (self.package / "RESULT.json").unlink()
        result = self.replay()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing regular artifact", result.stderr)

    def test_exclusive_regeneration(self):
        path = self.package / "RESULT.json"
        original = path.read_bytes()
        rejected = self.replay("--write")
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("FileExistsError", rejected.stderr)
        self.assertEqual(path.read_bytes(), original)
        path.unlink()
        accepted = self.replay("--write")
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
