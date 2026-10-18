"""Packaging/failure-detection tests beyond the algebraic mutation controls."""

import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = HERE.relative_to(ROOT)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="jp8-additive-qa-")
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name).resolve()
        self.package = self.root / PACKAGE
        self.package.mkdir(parents=True)
        for source in HERE.iterdir():
            if source.is_file():
                shutil.copyfile(source, self.package / source.name)
        pins = json.loads((HERE / "SOURCES.json").read_text())
        for name in pins["payload_sha256"]:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def run_script(self, name, success=True):
        result = subprocess.run([sys.executable, "-O", "-I", "-B", str(self.package / name)],
                                check=False, cwd=self.root.parent, text=True, capture_output=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, "corruption accepted")
        return result.stdout + result.stderr

    def hashes(self):
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob("*") if p.is_file()}

    def test_relocated_recompressed_read_only_optimized(self):
        # Both payloads are mathematically unchanged, with different containers.
        for path in self.root.rglob("*.gz"):
            path.write_bytes(gzip.compress(gzip.decompress(path.read_bytes()),
                                           compresslevel=1, mtime=123456789))
        before = self.hashes()
        self.run_script("verify.py")
        self.run_script("independent.py")
        self.assertEqual(before, self.hashes(), "read-only replay changed the tree")

    def test_source_corruption(self):
        path = next(self.root.rglob("CANONICAL-WORD.json.gz"))
        obj = json.loads(gzip.decompress(path.read_bytes()))
        obj["R"] += 1
        path.write_bytes(gzip.compress(json.dumps(obj).encode(), mtime=0))
        self.assertIn("source payload changed", self.run_script("verify.py", False))
        self.assertIn("independent source pin", self.run_script("independent.py", False))

    def test_certificate_corruption(self):
        path = self.package / "CERTIFICATE.json"
        obj = json.loads(path.read_text())
        route = next(r for b in obj["orientations"]["forward"]["blocks"]
                     for r in b["routes"] if r[0] == "read")
        route[1] += 1
        path.write_text(json.dumps(obj))
        self.assertIn("CERTIFICATE.json mismatch", self.run_script("verify.py", False))
        self.assertIn("independent primitive hash", self.run_script("independent.py", False))

    def test_undercharged_receipt(self):
        path = self.package / "EXPECTED.json"
        obj = json.loads(path.read_text())
        obj["orientations"]["forward"]["real_primitives"] -= 2
        path.write_text(json.dumps(obj))
        self.assertIn("EXPECTED.json mismatch", self.run_script("verify.py", False))


if __name__ == "__main__":
    unittest.main()
