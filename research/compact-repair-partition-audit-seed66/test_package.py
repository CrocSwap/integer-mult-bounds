#!/usr/bin/env python3
"""Semantic controls and actual CLI source/receipt/export failure detection."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("partition_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = verify
spec.loader.exec_module(verify)


class AuditControls(unittest.TestCase):
    def cli(self, root, *args):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(root / "verify.py"), *args],
                              cwd=root.parent, text=True, capture_output=True, timeout=180)

    def test_repair_sign_fault(self):
        verify.authenticate()
        _, compact, oracle = verify.load_sources()
        original = verify.repair_formula
        try:
            def wrong(y, t, z, K, G, rho):
                active = z == 1 and t == (1 << G)-1 and not ((y >> rho) & 1)
                return (y + ((1 << (rho+G+1)) if active else 0)) % (1 << (2*K))
            verify.repair_formula = wrong
            with self.assertRaisesRegex(ValueError, "inverse-source formula"):
                verify.primary_orbits(compact, oracle)
        finally:
            verify.repair_formula = original

    def test_boolean_information_witness(self):
        # A cell cannot distinguish these two local inputs, but must emit
        # different remote bits. Equal cell sizes do not repair this failure.
        destination = 65408
        left = range(32768)
        first = {0: 0}
        second = {0: 1}
        self.assertEqual([first.get(i, 0) for i in range(32768, 65536)],
                         [second.get(i, 0) for i in range(32768, 65536)])
        self.assertIn(0, left)
        self.assertNotIn(destination, left)
        self.assertNotEqual(first[0], second[0])

    def test_typed_receipt_equality(self):
        result = json.loads((HERE / "RESULT.json").read_text())
        altered = copy.deepcopy(result)
        altered["primary_orbits"]["raw_invariance_not_required"] = 1
        self.assertEqual(result, altered)  # Python otherwise treats True == 1.
        self.assertNotEqual(verify.canonical(result), verify.canonical(altered))

    def test_source_rejected_before_import(self):
        with tempfile.TemporaryDirectory(prefix="repair-source-fault-") as directory:
            root = Path(directory) / "package"
            shutil.copytree(HERE, root)
            source = root / "sources/compact.py"
            source.write_text(source.read_text() + "\nraise RuntimeError('MUST_NOT_IMPORT')\n")
            result = self.cli(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source SHA256: sources/compact.py", result.stderr)
            self.assertNotIn("MUST_NOT_IMPORT", result.stderr)

    def test_blob_pin_rejected(self):
        with tempfile.TemporaryDirectory(prefix="repair-blob-fault-") as directory:
            root = Path(directory) / "package"
            shutil.copytree(HERE, root)
            path = root / "SOURCES.json"
            manifest = json.loads(path.read_text())
            manifest["vendored"][0]["git_blob"] = "0"*40
            path.write_text(json.dumps(manifest))
            result = self.cli(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source Git blob", result.stderr)

    def test_optimized_git_free_export_and_receipt_fault(self):
        with tempfile.TemporaryDirectory(prefix="repair-clean-export-") as directory:
            root = Path(directory) / "package"
            shutil.copytree(HERE, root)
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            result = self.cli(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS_COMPACT_REPAIR_PARTITION_AUDIT", result.stdout)
            after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            path = root / "RESULT.json"
            receipt = json.loads(path.read_text())
            receipt["primary_orbits"]["cycle_histogram"]["512"] += 1
            path.write_text(json.dumps(receipt))
            damaged = path.read_bytes()
            result = self.cli(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("complete typed receipt mismatch", result.stderr)
            self.assertEqual(path.read_bytes(), damaged)
            result = self.cli(root, "--write", str(path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to overwrite receipt", result.stderr)
            self.assertEqual(path.read_bytes(), damaged)


if __name__ == "__main__":
    unittest.main()
