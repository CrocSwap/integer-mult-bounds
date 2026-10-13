"""Relocation, container portability and fail-closed certificate controls.

faw01, with substantial OpenAI Codex assistance. Apache-2.0.
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
PACKAGE = HERE.relative_to(ROOT)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="jp8-clean-work-test-")
        self.addCleanup(self.directory.cleanup)
        self.outside = Path(self.directory.name)
        self.root = self.outside / "minimal-checkout"
        self.package = self.root / PACKAGE
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns("__pycache__"))
        for name in json.loads((HERE / "SOURCE-PINS.json").read_text())["files"]:
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)

    def run_package(self):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package / "verify.py")],
                              cwd=self.outside, capture_output=True, text=True, timeout=60)

    def reject(self, reason):
        result = self.run_package()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(reason, result.stderr)
        self.assertNotIn("PASS_JP8_CLEAN_WORK", result.stdout)

    def test_minimal_relocation_and_gzip_recompression(self):
        for source in self.root.rglob("*.json.gz"):
            raw = gzip.decompress(source.read_bytes())
            source.write_bytes(gzip.compress(raw, compresslevel=1, mtime=33))
        result = self.run_package()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "PASS_JP8_CLEAN_WORK orientations=2 columns=716+9 extra_saved=9228,9228 controls=15")

    def test_modified_predecessor_rejected_before_import(self):
        source = self.root / "research/complex-dyadic-lowering/lower.py"
        source.write_text("raise RuntimeError('must not execute altered dependency')\n")
        self.reject("source pin: research/complex-dyadic-lowering/lower.py")

    def test_forged_invoice_rejected(self):
        source = self.package / "EXPECTED.json"
        receipt = json.loads(source.read_text())
        receipt["local_invoice"]["new_local_primitive_bound"] -= 1
        source.write_text(json.dumps(receipt))
        self.reject("expected receipt mismatch")

    def test_false_clean_state_rejected_by_independent_census(self):
        source = self.package / "lower.py"
        text = source.read_text()
        self.assertIn("last_add = None", text)
        source.write_text(text.replace("last_add = None", "last_add = 0"))
        self.reject("independent deletion census")


if __name__ == "__main__":
    unittest.main()
