"""Exercise the published verifier through its standalone command."""

import gzip
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class ArtifactChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.package = Path(self.temporary.name) / "package"
        shutil.copytree(
            HERE, self.package, ignore=shutil.ignore_patterns("__pycache__")
        )

    def tearDown(self):
        for path in self.package.iterdir():
            path.chmod(0o644)
        self.package.chmod(0o755)
        self.temporary.cleanup()

    def replay(self):
        return subprocess.run(
            [
                sys.executable,
                "-I",
                "-B",
                "-W",
                "error",
                str(self.package / "verify.py"),
            ],
            cwd=self.temporary.name,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    def test_git_free_read_only_replay(self):
        before = {p.name: p.read_bytes() for p in self.package.iterdir() if p.is_file()}
        for path in self.package.iterdir():
            path.chmod(0o444)
        self.package.chmod(0o555)
        result = self.replay()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_QQ16_SCRATCH_TRAVEL", result.stdout)
        self.assertEqual(
            before, {p.name: p.read_bytes() for p in self.package.iterdir()}
        )

    def test_source_corruption_rejects(self):
        path = self.package / "source-word.json.gz"
        raw = gzip.decompress(path.read_bytes()).replace(b'"W0"', b'"W1"', 1)
        path.write_bytes(gzip.compress(raw, mtime=0))
        result = self.replay()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source SHA256", result.stderr)

    def test_typed_receipt_corruption_rejects(self):
        path = self.package / "RESULT.json"
        result = json.loads(path.read_text())
        result["literal_site_cases"][0] = True
        path.write_text(json.dumps(result))
        run = self.replay()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("typed result receipt", run.stderr)

    def test_compression_metadata_is_not_mathematical_evidence(self):
        path = self.package / "source-word.json.gz"
        raw = gzip.decompress(path.read_bytes())
        path.write_bytes(gzip.compress(raw, compresslevel=1, mtime=1))
        result = self.replay()
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
