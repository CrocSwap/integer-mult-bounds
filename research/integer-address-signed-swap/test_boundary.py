"""Failure-sensitive export and evidence checks, including optimized execution."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class Boundary(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="integer-signed-swap-")
        self.root = Path(self.temp.name)
        self.pkg = self.root / "research/integer-address-signed-swap"
        shutil.copytree(HERE, self.pkg, ignore=shutil.ignore_patterns("__pycache__"))
        manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
        for item in manifest["files"]:
            if item["usage"] != "input" or item["path"].startswith("research/integer-address-signed-swap/"):
                continue
            dest = self.root / item["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / item["path"], dest)

    def tearDown(self):
        self.temp.cleanup()

    def invoke(self, *args):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(self.pkg / "verify.py"), *args],
                              cwd=self.root, capture_output=True, text=True, encoding="utf-8", timeout=60)

    def hashes(self):
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob("*") if p.is_file()}

    def test_git_free_readonly_replay(self):
        before = self.hashes()
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, self.hashes())

    def test_source_drift_rejected(self):
        source = self.pkg / "predecessor-2544.md"
        source.write_bytes(source.read_bytes()+b"\nChanged premise\n")
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source SHA mismatch", result.stderr)

    def test_missing_source_rejected(self):
        (self.root / "research/symmetric-adjacent-cut-bound/PROOF.md").unlink()
        self.assertNotEqual(self.invoke().returncode, 0)

    def test_typed_receipt_drift_rejected(self):
        path = self.pkg / "RESULT.json"
        receipt = json.loads(path.read_text(encoding="utf-8"))
        receipt["new_selected_exponent"] = 0  # Python equality alone would accept False == 0.
        path.write_text(json.dumps(receipt), encoding="utf-8")
        result = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("receipt mismatch", result.stderr)

    def test_missing_receipt_rejected(self):
        (self.pkg / "RESULT.json").unlink()
        self.assertNotEqual(self.invoke().returncode, 0)

    def test_exclusive_regeneration(self):
        destination = self.root / "fresh-result.json"
        result = self.invoke("--write-result", str(destination))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(destination.read_text()), json.loads((self.pkg / "RESULT.json").read_text()))
        old = destination.read_bytes()
        self.assertNotEqual(self.invoke("--write-result", str(destination)).returncode, 0)
        self.assertEqual(destination.read_bytes(), old)


if __name__ == "__main__":
    unittest.main()
