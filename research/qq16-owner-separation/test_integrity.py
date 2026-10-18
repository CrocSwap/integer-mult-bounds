#!/usr/bin/env python3
"""Check fail-closed receipt/pin handling in an isolated package copy.

No frozen input is edited. kyzer1023 with OpenAI Codex assistance, Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BOOTSTRAP = """
import importlib.util
from pathlib import Path
import sys
spec = importlib.util.spec_from_file_location('subject', sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.ROOT = Path(sys.argv[2])
sys.argv = [sys.argv[1]]
module.main()
"""


class IntegrityTests(unittest.TestCase):
    def run_copy(self, change):
        with tempfile.TemporaryDirectory(prefix="qq16-owner-integrity-") as directory:
            copied = Path(directory) / "package"
            shutil.copytree(PACKAGE, copied, ignore=shutil.ignore_patterns("__pycache__"))
            change(copied)
            before = {p.name: p.read_bytes() for p in copied.iterdir() if p.is_file()}
            process = subprocess.run(
                [sys.executable, "-I", "-O", "-B", "-c", BOOTSTRAP,
                 str(copied / "verify.py"), str(ROOT)],
                capture_output=True, text=True, timeout=60)
            after = {p.name: p.read_bytes() for p in copied.iterdir() if p.is_file()}
            self.assertEqual(before, after, "replay must not rewrite evidence")
            return process

    def test_relocated_positive(self):
        process = self.run_copy(lambda _: None)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("PASS_QQ16_OWNER_SEPARATION", process.stdout)

    def test_wrong_recorded_rank(self):
        def corrupt(package):
            path = package / "RESULT.json"
            result = json.loads(path.read_text(encoding="utf-8"))
            result["owner_evaluation_rank"] = 73
            path.write_text(json.dumps(result), encoding="utf-8")
        process = self.run_copy(corrupt)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("complete canonical receipt equality", process.stderr)

    def test_wrong_source_manifest(self):
        def corrupt(package):
            path = package / "SOURCES.json"
            result = json.loads(path.read_text(encoding="utf-8"))
            next(row for row in result["files"] if row["usage"] == "input")["sha256"] = "0" * 64
            path.write_text(json.dumps(result), encoding="utf-8")
        process = self.run_copy(corrupt)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("declared input pins", process.stderr)


if __name__ == "__main__":
    unittest.main()
