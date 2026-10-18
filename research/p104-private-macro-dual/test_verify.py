#!/usr/bin/env python3
"""Source-before-import and complete-word controls on an isolated source export."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


class ExportChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="p104-private-dual-")
        cls.root = Path(cls.temp.name)
        cls.package = cls.root/"research/p104-private-macro-dual"
        shutil.copytree(HERE, cls.package, ignore=shutil.ignore_patterns("__pycache__"))
        sources = json.loads((HERE/"SOURCES.json").read_text())
        for pin in sources["files"]:
            if pin["usage"] == "input":
                target = cls.root/pin["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/pin["path"], target)

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
        p = self.run_export()
        self.assertEqual(p.returncode, 0, p.stdout+p.stderr)
        self.assertIn("PASS_P104_PRIVATE_MACRO_DUAL", p.stdout)
        self.assertEqual(before, snapshot())

    def test_changed_interpreter_rejected_before_import(self):
        p = self.root/"research/p104-native-channel/vendor/native_verify.py"
        raw = p.read_bytes()
        try:
            p.write_bytes(raw+b"\nraise RuntimeError('UNTRUSTED_NATIVE_EXECUTED')\n")
            proc = self.run_export()
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("source hash:", proc.stderr)
            self.assertNotIn("UNTRUSTED_NATIVE_EXECUTED", proc.stderr)
        finally:
            p.write_bytes(raw)

    def test_complete_dual_word_not_just_summary(self):
        p = self.package/"WORD.json"
        raw = p.read_bytes()
        try:
            data = json.loads(raw)
            # Same operation/profile counters, changed mathematically relevant sign.
            next(e for e in data["program"] if e[0] == "add")[3] = "999"
            p.write_text(json.dumps(data), encoding="utf8")
            proc = self.run_export()
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("complete dual word mismatch", proc.stderr)
        finally:
            p.write_bytes(raw)

    def test_missing_native_evidence(self):
        p = self.root/"research/p104-native-channel/NATIVE-RECIPES.json.gz"
        raw = p.read_bytes()
        try:
            p.unlink()
            proc = self.run_export()
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("FileNotFoundError", proc.stderr)
        finally:
            p.write_bytes(raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)
