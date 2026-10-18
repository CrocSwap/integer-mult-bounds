#!/usr/bin/env python3
"""Behavior checks on a Git-free source export; no scientific input is rewritten."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from hashlib import sha256

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


class ExportChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="p104-live-helper-")
        cls.root = Path(cls.temp.name)
        cls.package = cls.root / "research/p104-live-helper-reads"
        shutil.copytree(HERE, cls.package, ignore=shutil.ignore_patterns("__pycache__"))
        cls.inputs = [x["path"] for x in json.loads((HERE/"SOURCES.json").read_text())['files']
                      if x['usage'] == 'input']
        for name in cls.inputs:
            target = cls.root/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, target)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_export(self):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package/"verify.py")],
                              cwd=self.root, capture_output=True, text=True, timeout=120)

    def test_read_only_export(self):
        def snapshot():
            return {str(p.relative_to(self.root)): sha256(p.read_bytes()).hexdigest()
                    for p in self.root.rglob("*") if p.is_file()}
        before = snapshot()
        proc = self.run_export()
        self.assertEqual(proc.returncode, 0, proc.stdout+proc.stderr)
        self.assertIn("PASS_P104_LIVE_HELPER_READS", proc.stdout)
        self.assertEqual(before, snapshot())

    def test_source_drift(self):
        p = self.root/self.inputs[0]
        raw = p.read_bytes()
        try:
            p.write_bytes(raw+b"\n")
            proc = self.run_export()
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("source hash", proc.stderr)
        finally:
            p.write_bytes(raw)

    def test_missing_source(self):
        p = self.root/self.inputs[0]
        raw = p.read_bytes()
        try:
            p.unlink()
            proc = self.run_export()
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("FileNotFoundError", proc.stderr)
        finally:
            p.write_bytes(raw)

    def test_receipt_and_duplicate_keys(self):
        p = self.package/"RESULT.json"
        raw = p.read_bytes()
        try:
            result = json.loads(raw)
            result["trace"]["target_endpoint_contacts"] = 1
            p.write_text(json.dumps(result), encoding="utf8")
            proc = self.run_export()
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("receipt mismatch", proc.stderr)
            p.write_text('{"x":1,"x":2}', encoding="utf8")
            proc = self.run_export()
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("duplicate JSON key", proc.stderr)
        finally:
            p.write_bytes(raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)
