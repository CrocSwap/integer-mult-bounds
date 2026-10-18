"""Behavioral controls for the reusable certificate, including source-before-code checks."""

from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
RELATIVE = PACKAGE.relative_to(ROOT)


class CertificateBehavior(unittest.TestCase):
    def setUp(self):
        # Keep temporary exports within the invoking checkout.
        self.temporary = tempfile.TemporaryDirectory(prefix="p104-fusion-check-", dir=ROOT)
        self.root = Path(self.temporary.name)
        self.package = self.root / RELATIVE
        shutil.copytree(PACKAGE, self.package, ignore=shutil.ignore_patterns("__pycache__"))
        sources = json.loads((PACKAGE / "SOURCES.json").read_text())
        for entry in sources["files"]:
            if entry["usage"] == "input":
                path = Path(entry["path"])
                (self.root / path).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / path, self.root / path)

    def tearDown(self):
        for path in self.root.rglob("*"):
            path.chmod(0o755 if path.is_dir() else 0o644)
        self.root.chmod(0o755)
        self.temporary.cleanup()

    def run_verifier(self, *args):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package / "verify.py"), *args],
                              cwd=self.root, text=True, capture_output=True, timeout=120)

    def test_optimized_read_only_git_free_export(self):
        before = {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in self.root.rglob("*") if p.is_file()}
        for path in self.root.rglob("*"):
            path.chmod(0o555 if path.is_dir() else 0o444)
        self.root.chmod(0o555)
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_P104_DUAL_ENDPOINT_FUSION", result.stdout)
        after = {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_complete_word_and_native_regeneration(self):
        result = self.run_verifier("--regenerate")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_source_drift_rejected_before_execution(self):
        path = self.root / "research/p104-native-channel/vendor/native_verify.py"
        path.write_text("raise RuntimeError('UNAUTHENTICATED_EXECUTION')\n" + path.read_text())
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source SHA256", result.stderr)
        self.assertNotIn("UNAUTHENTICATED_EXECUTION", result.stderr)

    def test_predecessor_word_pin(self):
        path = self.package / "inputs/PR2586-WORD.json"
        path.write_text(path.read_text() + "\n")
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source SHA256", result.stderr)

    def test_typed_receipt_mutation(self):
        path = self.package / "RESULT.json"
        receipt = json.loads(path.read_text())
        receipt["candidate"]["zero_erasures"] = 8.0
        path.write_text(json.dumps(receipt))
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("complete typed result receipt", result.stderr)

    def test_exclusive_output(self):
        output = self.root / "receipt.json"
        output.write_text("existing data\n")
        result = self.run_verifier("--out", str(output))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FileExistsError", result.stderr)
        self.assertEqual(output.read_text(), "existing data\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
