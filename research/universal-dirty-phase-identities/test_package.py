#!/usr/bin/env python3
"""Real file faults and standalone optimized replay; standard library only."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def invoke(folder, script="verify.py", *extra):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(folder / script), *map(str, extra)],
                          cwd=folder, text=True, capture_output=True)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="phase identities ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "isolated package"
        shutil.copytree(HERE, self.root, ignore=shutil.ignore_patterns("__pycache__"))

    def test_optimized_relocation_and_dense_oracle(self):
        for path in self.root.rglob("*"):
            if path.is_file():
                path.chmod(0o444)
        for script in ["verify.py", "check_dense.py"]:
            result = invoke(self.root, script)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_source_drift(self):
        source = self.root / "vendor/PR1278-PROOF.md"
        source.write_text(source.read_text().replace("P_a", "P_wrong", 1))
        result = invoke(self.root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source hash mismatch", result.stderr)

    def test_receipt_fault(self):
        path = self.root / "CERTIFICATE.json"
        data = json.loads(path.read_text())
        data["identities"]["completed_parent"]["normal_form"][0]["terms"][0]["coefficient"] += 1
        path.write_text(json.dumps(data))
        self.assertNotEqual(invoke(self.root).returncode, 0)
        self.assertNotEqual(invoke(self.root, "check_dense.py").returncode, 0)

    def test_noncommutative_order_fault(self):
        path = self.root / "CERTIFICATE.json"
        data = json.loads(path.read_text())
        changed = 0
        for entry in data["identities"]["completed_parent"]["normal_form"]:
            for term in entry["terms"]:
                if term["word"] == ["A", "B"]:
                    term["word"] = ["B", "A"]
                    changed += 1
        self.assertEqual(changed, 1)
        path.write_text(json.dumps(data))
        self.assertNotEqual(invoke(self.root).returncode, 0)
        self.assertNotEqual(invoke(self.root, "check_dense.py").returncode, 0)

    def test_regeneration_and_no_overwrite(self):
        out = self.root / "new receipt.json"
        result = invoke(self.root, "verify.py", "--write", out)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(out.read_bytes(), (self.root / "CERTIFICATE.json").read_bytes())
        before = out.read_bytes()
        self.assertNotEqual(invoke(self.root, "verify.py", "--write", out).returncode, 0)
        self.assertEqual(out.read_bytes(), before)

    def test_dense_receipt_fault(self):
        path = self.root / "DENSE-CHECK.json"
        data = json.loads(path.read_text())
        data["counterexamples"]["P_does_not_fix_y"]["residual"][3][0] = 0
        path.write_text(json.dumps(data))
        self.assertNotEqual(invoke(self.root, "check_dense.py").returncode, 0)


if __name__ == "__main__":
    unittest.main()
