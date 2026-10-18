"""Receipt, source-corruption and relocation controls for the scoped audit.

Brody Arbon, with substantial OpenAI Codex assistance. Apache-2.0.
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


class PackageControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="replica-prefix-", dir=ROOT.parent)
        cls.root = Path(cls.tmp.name) / "minimal checkout with spaces"
        cls.package = cls.root / "research" / HERE.name
        cls.package.mkdir(parents=True)
        for path in HERE.iterdir():
            if path.is_file():
                shutil.copy2(path, cls.package / path.name)
        manifest = json.loads((HERE / "SOURCES.json").read_bytes())
        cls.inputs = manifest["inputs"]
        for entry in cls.inputs.values():
            destination = cls.root / entry["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / entry["path"], destination)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_audit(self, *extra):
        return subprocess.run([sys.executable, "-I", "-O", "-B",
                               str(self.package / "verify.py"), *map(str, extra)],
                              cwd=ROOT.parent, capture_output=True, text=True, timeout=120)

    def test_1_relocated_isolated_optimized(self):
        result = self.run_audit()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("prefix_bits=286->160", result.stdout)

    def test_2_source_corruption(self):
        source = self.root / self.inputs["plan"]["path"]
        original = source.read_bytes()
        try:
            source.write_bytes(original + b"\n")
            result = self.run_audit()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source pin: plan", result.stderr)
        finally:
            source.write_bytes(original)

    def test_3_changed_expected_receipt(self):
        source = self.package / "EXPECTED.json"
        original = source.read_bytes()
        try:
            modified = json.loads(original)
            modified["prefix_bits"]["replica_bound"] = 159
            source.write_text(json.dumps(modified), encoding="utf-8")
            result = self.run_audit()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("expected receipt mismatch", result.stderr)
        finally:
            source.write_bytes(original)

    def test_4_gzip_repackaging(self):
        source = self.root / self.inputs["owners"]["path"]
        original = source.read_bytes()
        try:
            source.write_bytes(gzip.compress(gzip.decompress(original), compresslevel=1, mtime=1234))
            self.assertNotEqual(source.read_bytes(), original)
            result = self.run_audit()
            self.assertEqual(result.returncode, 0, result.stderr)
        finally:
            source.write_bytes(original)

    def test_5_no_receipt_overwrite(self):
        target = self.root / "existing receipt.json"
        target.write_bytes(b"keep this exact content\n")
        result = self.run_audit("--record", target)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FileExistsError", result.stderr)
        self.assertEqual(target.read_bytes(), b"keep this exact content\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
