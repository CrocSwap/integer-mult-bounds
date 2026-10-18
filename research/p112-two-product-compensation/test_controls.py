#!/usr/bin/env python3
"""CLI corruption and relocated-export controls for the research evidence.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = HERE.relative_to(ROOT)


class EvidenceControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="p112-compensation-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.package = self.root / PACKAGE
        self.package.mkdir(parents=True)
        for name in ("verify.py", "independent_check.py", "SOURCES.json", "CERTIFICATE.json"):
            shutil.copyfile(HERE / name, self.package / name)
        self.pins = json.loads((HERE / "SOURCES.json").read_text())
        for pin in self.pins["files"]:
            if pin["usage"] == "input":
                target = self.root / pin["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / pin["path"], target)

    def run_checker(self, name, expected_error=None, *extra):
        result = subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package / name), *extra],
                                cwd=self.root, capture_output=True, text=True, timeout=120)
        if expected_error is None:
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_P112", result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn(expected_error, result.stderr)

    def test_relocated_optimized_export(self):
        # No .git, imported predecessor code, third-party packages, or package directory on sys.path.
        self.run_checker("verify.py")
        self.run_checker("independent_check.py")

    def test_complete_receipt_binding(self):
        path = self.package / "CERTIFICATE.json"
        original = json.loads(path.read_text())
        changed = copy.deepcopy(original)
        changed["finite"]["one_sided_records"] -= 1
        path.write_text(json.dumps(changed))
        self.run_checker("verify.py", "complete certificate mismatch")
        self.run_checker("independent_check.py", "complete finite-premise receipt mismatch")
        changed = copy.deepcopy(original)
        changed["fixtures"]["omission_invoice"]["complete"] = 63
        path.write_text(json.dumps(changed))
        self.run_checker("verify.py", "complete certificate mismatch")

    def test_source_bytes_and_blob_binding(self):
        pin = next(p for p in self.pins["files"] if p["path"].endswith("reference-geometry.json"))
        path = self.root / pin["path"]
        original = path.read_bytes()
        path.write_bytes(original + b"\n")
        self.run_checker("verify.py", "source SHA256 drift")
        self.run_checker("independent_check.py", "source hash")
        path.write_bytes(original)
        pin["git_blob"] = "0" * 40
        (self.package / "SOURCES.json").write_text(json.dumps(self.pins))
        self.run_checker("verify.py", "source Git blob drift")
        self.run_checker("independent_check.py", "source blob")


if __name__ == "__main__":
    unittest.main(verbosity=2)
