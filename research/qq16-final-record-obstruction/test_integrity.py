#!/usr/bin/env python3
"""Relocated read-only replay and tampering controls; standard library only.

Apache-2.0. Substantial OpenAI Codex assistance.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


class ExportIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="qq16-final-record-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        cls.package = cls.root / "research" / PACKAGE.name
        shutil.copytree(PACKAGE, cls.package, ignore=shutil.ignore_patterns("__pycache__"))
        sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
        for row in sources["files"]:
            if row["usage"] == "input":
                source = ROOT / row["path"]
                destination = cls.root / row["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)

    def run_export(self):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package / "verify.py")],
                              cwd=self.root, text=True, capture_output=True, timeout=120)

    def snapshot(self):
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob("*") if p.is_file()}

    def test_01_git_free_read_only_replay(self):
        self.assertFalse((self.root / ".git").exists())
        before = self.snapshot()
        result = self.run_export()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_QQ16_FINAL_RECORD_OBSTRUCTION", result.stdout)
        self.assertEqual(before, self.snapshot())

    def test_02_complete_receipt_rejects_changed_bound(self):
        path = self.package / "RESULT.json"
        original = path.read_bytes()
        try:
            altered = json.loads(original)
            altered["primary"]["sources"]["selected_defect_lower_per_owner"] = "9/7"
            path.write_text(json.dumps(altered), encoding="utf-8")
            result = self.run_export()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("complete canonical RESULT.json differs", result.stderr)
        finally:
            path.write_bytes(original)

    def test_03_source_pin_rejects_changed_packet(self):
        path = self.root / "research/joint-query/certificate.json.gz"
        original = path.read_bytes()
        try:
            path.write_bytes(original + b"changed")
            result = self.run_export()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("input hash: research/joint-query/certificate.json.gz", result.stderr)
        finally:
            path.write_bytes(original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
