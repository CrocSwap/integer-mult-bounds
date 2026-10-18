#!/usr/bin/env python3
"""Artifact and rewrite-boundary rejection tests, without importing the checker.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
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
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="qq16-output-retention-")
        self.root = Path(self.temp.name)
        self.pkg = self.root / "research" / HERE.name
        shutil.copytree(HERE, self.pkg)
        inputs = json.loads((HERE / "VERIFY.json").read_text())["inputs"]
        for name in inputs:
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)

    def tearDown(self):
        for path in self.root.rglob("*"):
            path.chmod(0o755 if path.is_dir() else 0o644)
        self.root.chmod(0o755)
        self.temp.cleanup()

    def run_checker(self, *args):
        return subprocess.run([sys.executable, "-I", "-B", "-O", str(self.pkg / "verify.py"), *args],
                              cwd=self.root, capture_output=True, text=True, timeout=30)

    def reject(self, message):
        run = self.run_checker()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn(message, run.stdout + run.stderr)

    def test_read_only_git_free_export(self):
        paths = [p for p in self.root.rglob("*") if p.is_file()]
        before = {p.relative_to(self.root): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        for p in self.root.rglob("*"):
            p.chmod(0o555 if p.is_dir() else 0o444)
        self.root.chmod(0o555)
        run = self.run_checker()
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("PASS_QQ16_OUTPUT_BANK_RETENTION", run.stdout)
        after = {p.relative_to(self.root): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_predecessor_corruption(self):
        p = self.pkg / "predecessor" / "WORD.json"
        p.write_bytes(p.read_bytes() + b" ")
        self.reject("predecessor source hash")

    def test_live_scalar_price_corruption(self):
        p = self.root / "research/joint-query/verify_scalar.py"
        p.write_bytes(p.read_bytes() + b"\n# changed\n")
        self.reject("live source hash")

    def test_candidate_word_corruption(self):
        p = self.pkg / "WORD.json"
        word = json.loads(p.read_text()); word[1]["coefficient"] = "-1"
        p.write_text(json.dumps(word))
        self.reject("candidate WORD differs")

    def test_typed_receipt_corruption(self):
        p = self.pkg / "RESULT.json"
        receipt = json.loads(p.read_text()); receipt["selected_ports"][0] = False
        p.write_text(json.dumps(receipt))
        self.reject("complete typed RESULT differs")

    def test_write_refuses_overwrite(self):
        p = self.pkg / "RESULT.json"; before = p.read_bytes()
        run = self.run_checker("--write")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("FileExistsError", run.stderr)
        self.assertEqual(before, p.read_bytes())


if __name__ == "__main__":
    unittest.main()
