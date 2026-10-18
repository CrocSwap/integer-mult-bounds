"""Focused portability and adversarial artifact tests, with assertions off."""

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
        scratch = tempfile.TemporaryDirectory(prefix="jp8-transpose-qa-")
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name).resolve()
        self.package = self.root / PACKAGE
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns("__pycache__"))
        for name in json.loads((HERE / "SOURCES.json").read_text())["payload_sha256"]:
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

    def snapshot(self):
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob("*") if p.is_file()}

    def test_relocated_recompressed_read_only(self):
        for path in self.root.rglob("*.gz"):
            path.write_bytes(gzip.compress(gzip.decompress(path.read_bytes()),
                                           compresslevel=1, mtime=123456789))
        before = self.snapshot()
        self.run_script("verify.py")
        self.run_script("independent.py")
        self.assertEqual(before, self.snapshot())

    def test_pinned_source_corruption(self):
        path = next(self.root.rglob("CANONICAL-WORD.json.gz"))
        obj = json.loads(gzip.decompress(path.read_bytes()))
        obj["R"] -= 1
        path.write_bytes(gzip.compress(json.dumps(obj).encode(), mtime=0))
        self.assertIn("source payload changed", self.run_script("verify.py", False))
        self.assertIn("independent source pin", self.run_script("independent.py", False))

    def test_vendored_dependency_corruption(self):
        path = self.package / "vendor/construct_seed31.py"
        path.write_bytes(path.read_bytes() + b"\n# deliberate pin mutation\n")
        self.assertIn("vendored forward constructor changed", self.run_script("verify.py", False))
        # The independent circuit replay does not execute or depend on this code.
        self.run_script("independent.py")

    def test_companion_sign_corruption(self):
        path = self.package / "CERTIFICATE.json"
        obj = json.loads(path.read_text())
        block = obj["blocks"][0]
        op = next(op for op in block["backward_primitives"]
                  if op[0] in ("add", "sub") and op[1] == block["common_backward_target"])
        op[0] = "sub" if op[0] == "add" else "add"
        path.write_text(json.dumps(obj))
        self.assertIn("CERTIFICATE.json mismatch", self.run_script("verify.py", False))
        self.assertIn("backward primitive hash", self.run_script("independent.py", False))

    def test_undercharged_receipt(self):
        path = self.package / "EXPECTED.json"
        obj = json.loads(path.read_text())
        obj["orientations"]["backward"]["real_primitives"] -= 2
        path.write_text(json.dumps(obj))
        self.assertIn("EXPECTED.json mismatch", self.run_script("verify.py", False))


if __name__ == "__main__":
    unittest.main()
