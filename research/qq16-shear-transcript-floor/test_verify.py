"""Integration controls for source-export replay. Apache-2.0; Codex assisted."""

import hashlib
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
SPEC = importlib.util.spec_from_file_location("qq16_shear_driver", HERE / "verify.py")
DRIVER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DRIVER)


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class ReplayControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="qq16-shear-control-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / HERE.relative_to(ROOT)
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns("__pycache__"))
        sources = json.loads((HERE / "SOURCES.json").read_text())
        for record in sources["files"]:
            if record["usage"] != "input":
                continue
            target = self.root / record["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / record["path"], target)

    def replay(self, *extra):
        return subprocess.run([sys.executable, "-I", "-B", str(self.package / "verify.py"),
                               *extra], cwd=self.root, text=True, capture_output=True,
                              timeout=60)

    def test_export_passes_read_only(self):
        before = snapshot(self.root)
        result = self.replay()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_SCOPED_QQ16_SHEAR_TRANSCRIPT_FLOOR", result.stdout)
        self.assertEqual(before, snapshot(self.root))

    def test_external_source_drift_rejected(self):
        source = self.root / "research/joint-query/evidence/QQ16-SELECTED-WITNESS.json"
        source.write_bytes(source.read_bytes() + b"\n")
        result = self.replay()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source SHA256 mismatch", result.stderr)

    def test_receipt_numeric_type_corruption_rejected(self):
        receipt = self.package / "RESULT.json"
        data = json.loads(receipt.read_text())
        data["schema_version"] = True  # Python's ordinary dict equality misses 1 == True.
        receipt.write_text(json.dumps(data))
        result = self.replay()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RESULT.json differs", result.stderr)

    def test_emit_refuses_existing_file(self):
        receipt = self.package / "RESULT.json"
        before = receipt.read_bytes()
        result = self.replay("--emit-result", str(receipt))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before, receipt.read_bytes())
        self.assertIn("File exists", result.stderr)

    def test_duplicate_json_field_rejected(self):
        bad = self.root / "duplicate.json"
        bad.write_text('{"status":"PASS","status":"FAIL"}')
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            DRIVER.read_json(bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)
