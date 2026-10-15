"""Artifact rejection tests for the scoped QQ16 verifier. Apache-2.0."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_kernel_verify", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class Artifacts(unittest.TestCase):
    def test_source_corruption(self):
        with tempfile.TemporaryDirectory(prefix="qq16-source-", dir=Path.cwd()) as tmp:
            root = Path(tmp)
            manifest = json.loads((HERE / "SOURCES.json").read_text())
            for entry in manifest["files"]:
                if entry["usage"] == "input":
                    target = root / entry["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(v.ROOT / entry["path"], target)
            self.assertEqual(set(v.load_sources(root)), set(v.load_sources(v.ROOT)))
            with (root / v.TAIL).open("ab") as stream:
                stream.write(b"\n")
            with self.assertRaisesRegex(v.Failure, "source digest"):
                v.load_sources(root)

    def test_receipt_type_change_rejected(self):
        with tempfile.TemporaryDirectory(prefix="qq16-receipt-", dir=Path.cwd()) as tmp:
            receipt = json.loads((HERE / "RESULT.json").read_text())
            receipt["ordered_identity"]["residual_term_counts"][0] = False
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps(receipt))
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"),
                                     "--receipt", str(path)], text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt mismatch", result.stderr)

    def test_ambiguous_json_rejected(self):
        for raw in ('{"a":0,"a":1}', '{"a":NaN}', '{"a":Infinity}'):
            with self.assertRaises(v.Failure):
                v.read_json(raw)


if __name__ == "__main__":
    unittest.main()
