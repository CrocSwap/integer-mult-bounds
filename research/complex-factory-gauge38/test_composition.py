#!/usr/bin/env python3
"""Offline closure, rejection and output-preservation checks for composition.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class CompositionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="composition minimal with spaces ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "offline closure"
        self.package = self.root / HERE.relative_to(ROOT)
        self.pins = json.loads((HERE / "SOURCE-PINS.json").read_text())
        for rel in self.pins["files"]:
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, path)
        self.package.mkdir(parents=True, exist_ok=True)
        cert = json.loads((HERE / "COMPOSITION.json").read_text())
        for name in [*cert["pins"], "COMPOSITION.json", "COMPOSITION-RESULT.json", "compose_pr922.py"]:
            shutil.copyfile(HERE / name, self.package / name)

    def run_check(self, *args, full=False):
        scope = [] if full else ["--local-only"]
        return subprocess.run([sys.executable, "-I", "-O", "-B", "-S",
                               str(self.package / "compose_pr922.py"), *scope, *args],
                              cwd=self.tmp.name, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def reject(self, reason, *args):
        result = self.run_check(*args)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(reason, result.stdout)

    def test_full_optimized_repacked_minimal_closure(self):
        for rel, pin in self.pins["files"].items():
            if pin["representation"] == "gzip-payload":
                path = self.root / rel
                path.write_bytes(gzip.compress(gzip.decompress(path.read_bytes()), compresslevel=1, mtime=1234))
        result = self.run_check(full=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("blocks=14 saved=448,448 extra_vs_each=224,224 controls=38", result.stdout)

    def test_pr922_source_corruption(self):
        path = self.package / "PR922-CIRCUIT.json"
        path.write_text(path.read_text() + " ")
        self.reject("composition source pin: PR922-CIRCUIT.json")

    def test_missing_lowering_source(self):
        (self.root / "research/complex-dyadic-lowering/lower.py").unlink()
        self.reject("FileNotFoundError")

    def test_boolean_coefficient(self):
        path = self.package / "COMPOSITION.json"
        cert = json.loads(path.read_text())
        cert["replacement"][0][3] = True
        path.write_text(json.dumps(cert))
        self.reject("combined witness differs")

    def test_receipt_underprices_combination(self):
        path = self.package / "COMPOSITION-RESULT.json"
        receipt = json.loads(path.read_text())
        receipt["local"]["combined"]["pr696"] -= 1
        path.write_text(json.dumps(receipt))
        self.reject("composition receipt differs")

    def test_existing_output_preserved(self):
        path = Path(self.tmp.name) / "existing directory"
        path.mkdir()
        sentinel = path / "keep"
        sentinel.write_text("unchanged")
        self.reject("FileExistsError", "--out", str(path))
        self.assertEqual(sentinel.read_text(), "unchanged")
        self.assertEqual(list(path.iterdir()), [sentinel])

    def test_existing_receipt_preserved(self):
        path = Path(self.tmp.name) / "existing receipt.json"
        path.write_text("unchanged")
        self.reject("receipt output already exists", "--write", str(path))
        self.assertEqual(path.read_text(), "unchanged")


if __name__ == "__main__":
    unittest.main(verbosity=2)
