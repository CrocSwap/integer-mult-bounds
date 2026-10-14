#!/usr/bin/env python3
"""Relocation and failure-detection tests for the exact research receipt.

Copyright 2026 Luke Mansoor. Apache-2.0. Substantial OpenAI Codex assistance.
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


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="global-star-puncture-",dir=ROOT)
        self.root = Path(self.scratch.name).resolve()
        self.package = self.root / "research/global-star-puncture"
        self.package.mkdir(parents=True)
        for name in ("verify.py","independent.py","SOURCES.json","RESULTS.json"):
            shutil.copyfile(HERE / name, self.package / name)
        for item in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["context"]:
            target = self.root / item["path"]
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT / item["path"],target)

    def tearDown(self):
        # The cleanup target is exactly the temporary directory created above.
        self.assertEqual(self.root, Path(self.scratch.name).resolve())
        self.assertEqual(self.root.parent, ROOT.resolve())
        self.scratch.cleanup()

    def run_checker(self, *arguments):
        return subprocess.run([sys.executable,"-I","-O","-B",
                               str(self.package / "verify.py"),*arguments],
                              cwd=self.root.parent,capture_output=True,text=True,timeout=30)

    def test_relocated_export(self):
        exported = self.root / "export.json"
        result = self.run_checker("--write",str(exported))
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("PASS_GLOBAL_STAR_PUNCTURE",result.stdout)
        self.assertEqual(json.loads(exported.read_text()),
                         json.loads((HERE / "RESULTS.json").read_text()))

    def test_receipt_corruption_preserves_output(self):
        receipt = self.package / "RESULTS.json"
        changed = json.loads(receipt.read_text())
        changed["bitset_quotient"][0]["minimum_weight"] = 3
        receipt.write_text(json.dumps(changed),encoding="utf-8")
        exported = self.root / "existing.json"
        exported.write_text("preserve me",encoding="utf-8")
        result = self.run_checker("--write",str(exported))
        self.assertNotEqual(result.returncode,0)
        self.assertIn("committed receipt differs",result.stderr)
        self.assertEqual(exported.read_text(),"preserve me")

    def test_context_corruption(self):
        with (self.root / "CONTRIBUTING.md").open("a",encoding="utf-8") as handle:
            handle.write("\nchanged provenance\n")
        result = self.run_checker()
        self.assertNotEqual(result.returncode,0)
        self.assertIn("pinned context bytes changed",result.stderr)

    def test_source_pin_corruption(self):
        source = self.package / "SOURCES.json"
        changed = json.loads(source.read_text())
        changed["context"][0]["sha256"] = "0" * 64
        source.write_text(json.dumps(changed),encoding="utf-8")
        result = self.run_checker()
        self.assertNotEqual(result.returncode,0)
        self.assertIn("pinned context bytes changed",result.stderr)


if __name__ == "__main__":
    unittest.main()
