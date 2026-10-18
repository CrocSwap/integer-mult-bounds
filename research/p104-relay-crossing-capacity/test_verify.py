"""Exercise the public verifier in an isolated, Git-free source export."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


class PublicReplay(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / "research" / PACKAGE.name
        self.package.mkdir(parents=True)
        for name in ["verify.py", "EXPECTED.json"]:
            shutil.copyfile(PACKAGE / name, self.package / name)
        self.inputs = self.root / "research/p104-native-channel/inputs"
        self.inputs.mkdir(parents=True)
        for name in ["LOWRANK-WITNESS.json", "P104-FIXTURE.json"]:
            shutil.copyfile(ROOT / "research/p104-native-channel/inputs" / name,
                            self.inputs / name)

    def run_verifier(self, *args):
        return subprocess.run(
            [sys.executable, "-I", "-O", "-Werror", "-B", str(self.package / "verify.py"), *args],
            cwd=self.root, capture_output=True, text=True, timeout=30, check=False)

    def test_readonly_export_and_literal_result(self):
        files = sorted(p for p in self.root.rglob("*") if p.is_file())
        before = {p: p.read_bytes() for p in files}
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(),
                         "PASS_P104_RELAY_CROSSING_CAPACITY forced=4680 "
                         "cheap_floor=4680 other_at_482=67")
        self.assertEqual(before, {p: p.read_bytes() for p in files})
        self.assertEqual(files, sorted(p for p in self.root.rglob("*") if p.is_file()))

    def test_changed_source_fails_before_analysis(self):
        path = self.inputs / "LOWRANK-WITNESS.json"
        path.write_text("{}")
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source hash LOWRANK-WITNESS.json", result.stderr)

    def test_missing_source_rejects(self):
        (self.inputs / "P104-FIXTURE.json").unlink()
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FileNotFoundError", result.stderr)

    def test_wrong_receipt_rejects(self):
        path = self.package / "EXPECTED.json"
        receipt = json.loads(path.read_text())
        receipt["cuts"][3]["forced"] = 4681
        path.write_text(json.dumps(receipt))
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("complete expected receipt", result.stderr)

    def test_duplicate_receipt_keys_reject(self):
        (self.package / "EXPECTED.json").write_text('{"cuts": [], "cuts": []}')
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate JSON key", result.stderr)

    def test_exclusive_output(self):
        output = self.root / "receipt.json"
        first = self.run_verifier("--out", str(output))
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(json.loads(output.read_text())["homogeneous_shape_lifetime_floor"], 4680)
        saved = output.read_bytes()
        second = self.run_verifier("--out", str(output))
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("FileExistsError", second.stderr)
        self.assertEqual(output.read_bytes(), saved)

    def test_input_capacity_rejects(self):
        (self.inputs / "P104-FIXTURE.json").write_bytes(b" " * 2_000_001)
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source capacity before hashing", result.stderr)


if __name__ == "__main__":
    unittest.main()
