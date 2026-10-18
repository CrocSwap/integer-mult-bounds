#!/usr/bin/env python3
"""Packaging and failure-detection checks in a minimal offline source closure.

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


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="gauge38 package with spaces ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "minimal closure"
        self.package = self.root / HERE.relative_to(ROOT)
        pins = json.loads((HERE / "SOURCE-PINS.json").read_text())
        for rel in pins["files"]:
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, target)
        self.package.mkdir(parents=True, exist_ok=True)
        for name in ("verify.py", "SOURCE-PINS.json", "CERTIFICATE.json", "EXPECTED.json"):
            shutil.copyfile(HERE / name, self.package / name)

    def run_check(self, *args, optimize=False, local_only=True):
        flags = ["-I", "-B", "-S"] + (["-O"] if optimize else [])
        scope = ["--local-only"] if local_only else []
        return subprocess.run([sys.executable, *flags, str(self.package / "verify.py"),
                               *scope, *args], cwd=self.tmp.name,
                              text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def rejected(self, reason, *args):
        result = self.run_check(*args)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(reason, result.stdout)

    def test_optimized_minimal_relocation(self):
        result = self.run_check(optimize=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("controls=46 local_only=True", result.stdout)

    def test_gzip_repackaging(self):
        pins = json.loads((self.package / "SOURCE-PINS.json").read_text())
        count = 0
        for rel, pin in pins["files"].items():
            if pin["representation"] == "gzip-payload":
                path = self.root / rel
                path.write_bytes(gzip.compress(gzip.decompress(path.read_bytes()), compresslevel=1, mtime=1234))
                count += 1
        self.assertGreater(count, 0)
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_full_replay_without_git_or_unpinned_files(self):
        pins = json.loads((self.package / "SOURCE-PINS.json").read_text())
        for rel, pin in pins["files"].items():
            if pin["representation"] == "gzip-payload":
                path = self.root / rel
                path.write_bytes(gzip.compress(gzip.decompress(path.read_bytes()), compresslevel=1, mtime=4321))
        result = self.run_check(optimize=True, local_only=False)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("blocks=14 saved=224,224 local_bill_delta=-224", result.stdout)

    def test_source_corruption(self):
        path = self.root / "research/complex-factory5-resynthesis/CIRCUIT.json"
        path.write_text(path.read_text() + " ")
        self.rejected("source pin: research/complex-factory5-resynthesis/CIRCUIT.json")

    def test_missing_source(self):
        (self.root / "research/complex-dyadic-lowering/lower.py").unlink()
        self.rejected("FileNotFoundError")

    def test_invalid_dual(self):
        path = self.package / "CERTIFICATE.json"
        data = json.loads(path.read_text())
        data["dual"][0] = 2
        path.write_text(json.dumps(data))
        self.rejected("dual capacity")

    def test_boolean_gauge(self):
        path = self.package / "CERTIFICATE.json"
        data = json.loads(path.read_text())
        data["potentials"][0] = False
        path.write_text(json.dumps(data))
        self.rejected("certificate integers required")

    def test_altered_receipt(self):
        path = self.package / "EXPECTED.json"
        data = json.loads(path.read_text())
        data["budget_local"]["main"]["after"]["fractional_bits"] = 0
        path.write_text(json.dumps(data))
        self.rejected("frozen receipt differs")

    def test_output_preserved(self):
        out = Path(self.tmp.name) / "existing output"
        out.mkdir()
        sentinel = out / "keep.txt"
        sentinel.write_text("unchanged")
        self.rejected("FileExistsError", "--out", str(out))
        self.assertEqual(sentinel.read_text(), "unchanged")
        self.assertEqual(list(out.iterdir()), [sentinel])


if __name__ == "__main__":
    unittest.main(verbosity=2)
