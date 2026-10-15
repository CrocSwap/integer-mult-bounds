#!/usr/bin/env python3
"""Behavioral checks for the independently runnable mathematical artifact.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Apache-2.0. Temporary copies never modify the frozen input packages.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # TMPDIR may be supplied by the caller; there is no fixed external path.
        cls.temp = tempfile.TemporaryDirectory(prefix="qq16-transcript-")
        cls.export = Path(cls.temp.name) / "source export"
        cls.package = cls.export / "research/qq16-transcript-capacity"
        cls.package.parent.mkdir(parents=True)
        shutil.copytree(HERE, cls.package)
        manifest = json.loads((HERE / "SOURCES.json").read_text())
        for entry in manifest["files"]:
            if entry["usage"] == "input":
                target = cls.export / entry["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / entry["path"], target)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_export(self, *args):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package / "verify.py"), *args],
                              cwd=self.export, capture_output=True, text=True, timeout=90)

    def test_read_only_export_without_git(self):
        files = [p for p in self.export.rglob("*") if p.is_file()]
        directories = [self.export] + [p for p in self.export.rglob("*") if p.is_dir()]
        try:
            for p in files:
                p.chmod(0o444)
            for p in directories:
                p.chmod(0o555)
            result = self.run_export()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_QQ16_TRANSCRIPT_CAPACITY", result.stdout)
            self.assertFalse((self.export / ".git").exists())
        finally:
            for p in directories:
                p.chmod(0o755)
            for p in files:
                p.chmod(0o644)

    def test_mutated_mathematical_receipt(self):
        receipt = json.loads((HERE / "RESULT.json").read_text())
        receipt["source_rank"]["first_width_not_excluded"] = 12
        target = Path(self.temp.name) / "wrong-capacity.json"
        target.write_text(json.dumps(receipt))
        result = self.run_export("--certificate", str(target))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("complete receipt mismatch", result.stderr)

    def test_mutated_source_is_rejected_before_algebra(self):
        target = self.export / "research/joint-query/evidence/QQ16-SELECTED-WITNESS.json"
        original = target.read_bytes()
        try:
            witness = json.loads(original)
            witness["trajectory_after_B1"][0]["coefficient"] = -1
            target.write_text(json.dumps(witness))
            result = self.run_export()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source digest:", result.stderr)
        finally:
            target.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
