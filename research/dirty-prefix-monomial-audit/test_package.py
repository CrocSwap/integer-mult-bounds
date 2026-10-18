#!/usr/bin/env python3
"""Source, mathematical and relocated-receipt controls; Apache-2.0."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("monomial_audit", HERE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class PackageTests(unittest.TestCase):
    def export(self, folder):
        root = Path(folder)
        package = root / "research" / HERE.name
        package.mkdir(parents=True)
        for path in HERE.iterdir():
            if path.is_file():
                shutil.copyfile(path, package / path.name)
        sources = json.loads((HERE / "SOURCES.json").read_text())
        for item in sources["files"]:
            destination = root / item["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / item["path"], destination)
        return root, package

    def run_export(self, root, package):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                              cwd=root.parent, capture_output=True, text=True, timeout=300)

    def test_mathematical_controls(self):
        self.assertEqual(len(audit.negative_controls()), 10)

    def test_induction_cases(self):
        self.assertEqual(audit.schema_checks()["abstract_cases"], 32)

    def test_odd_sign_negation_is_not_a_counterexample(self):
        # For odd n, negating every ideal factor gives the negative product.
        # It must not be advertised as a rejected wrong-order counterexample.
        instructions = [(s, t, a, -v) for s, t, a, v in audit.word(3)]
        result = audit.trace(3, -1, instructions)
        self.assertEqual(result["maximum"], [4, 4])
        self.assertNotEqual(instructions, audit.word(3, -1))

    def test_source_drift(self):
        with tempfile.TemporaryDirectory(prefix="prefix72-drift-") as temporary:
            root, _ = self.export(temporary)
            source = json.loads((HERE / "SOURCES.json").read_text())["roles"]["dispatcher"]
            with (root / source).open("a") as stream:
                stream.write("\n# deliberate source drift\n")
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                audit.bound_sources(root)

    def test_missing_source(self):
        with tempfile.TemporaryDirectory(prefix="prefix72-missing-") as temporary:
            root, _ = self.export(temporary)
            source = json.loads((HERE / "SOURCES.json").read_text())["roles"]["budget"]
            (root / source).unlink()
            with self.assertRaises(FileNotFoundError):
                audit.bound_sources(root)

    def test_receipt_types_are_distinct(self):
        self.assertNotEqual(audit.canonical({"sign": 1}), audit.canonical({"sign": True}))

    def test_relocated_readonly_replay(self):
        with tempfile.TemporaryDirectory(prefix="prefix72-readonly-") as temporary:
            root, package = self.export(temporary)
            paths = list(root.rglob("*"))
            try:
                for path in paths:
                    path.chmod(0o500 if path.is_dir() else 0o400)
                root.chmod(0o500)
                result = self.run_export(root, package)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("PASS_DIRTY_PREFIX_MONOMIAL", result.stdout)
                self.assertEqual(set(root.rglob("*")), set(paths))
            finally:
                root.chmod(0o700)
                for path in paths:
                    path.chmod(0o700 if path.is_dir() else 0o600)

    def test_tampered_receipt_rejected(self):
        with tempfile.TemporaryDirectory(prefix="prefix72-receipt-") as temporary:
            root, package = self.export(temporary)
            path = package / "EXPECTED.json"
            receipt = json.loads(path.read_text())
            receipt["seed_witness"]["sign"] = True
            path.write_text(json.dumps(receipt))
            result = self.run_export(root, package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("complete deterministic receipt", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
