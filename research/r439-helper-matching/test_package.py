#!/usr/bin/env python3
"""Fast source/receipt/output controls, separate from mathematical replay. Apache-2.0."""
import gzip
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))
V = runpy.run_path(str(C["HERE"] / "verify.py"))
B = runpy.run_path(str(C["HERE"] / "build.py"))


class PackageControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r439 package controls ")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)

    def closure(self):
        root = self.path / "source closure"
        manifest = C["load"](C["HERE"] / "SOURCES.json")
        for name in manifest["files"]:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(C["ROOT"] / name, target)
        return root

    def rejected_cli(self, *args, reason):
        result = subprocess.run([sys.executable, "-I", "-O", "-B", str(C["HERE"] / "verify.py"),
                                 *map(str, args)], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(reason, result.stderr)

    def test_typed_receipt(self):
        with self.assertRaisesRegex(ValueError, "different"):
            V["same"]({"value": 1}, {"value": True}, "different")

    def test_strict_json(self):
        for i, text in enumerate(('{"x":0,"x":1}', '{"x":NaN}', '{"x":Infinity}')):
            with self.subTest(text=text):
                path = self.path / (str(i) + ".json")
                path.write_text(text)
                with self.assertRaises(ValueError):
                    C["load"](path)

    def test_changed_source(self):
        root = self.closure()
        word = root / C["WORD"]
        word.write_bytes(word.read_bytes() + b"changed")
        with self.assertRaisesRegex(ValueError, "source hash mismatch"):
            C["pins"](root)

    def test_missing_source(self):
        root = self.closure()
        (root / C["CHECKER"]).unlink()
        with self.assertRaises(FileNotFoundError):
            C["pins"](root)

    def test_builder_output_preserved(self):
        output = self.path / "existing output"
        output.mkdir()
        marker = output / "keep"
        marker.write_text("unchanged")
        with self.assertRaises(FileExistsError):
            B["run"](C["ROOT"], output)
        self.assertEqual(marker.read_text(), "unchanged")
        self.assertEqual([p.name for p in output.iterdir()], ["keep"])

    def test_verifier_output_preserved(self):
        output = self.path / "existing output"
        output.mkdir()
        marker = output / "keep"
        marker.write_text("unchanged")
        self.rejected_cli("--output", output, reason="output already exists")
        self.assertEqual(marker.read_text(), "unchanged")

    def test_verifier_receipt_preserved(self):
        receipt = self.path / "existing receipt.json"
        receipt.write_text("unchanged")
        self.rejected_cli("--receipt", receipt, reason="receipt already exists")
        self.assertEqual(receipt.read_text(), "unchanged")

    def test_recompression_preserves_every_field(self):
        original = C["load"](C["HERE"] / "candidate.json.gz")
        encoded = C["canonical"](original)
        containers = [gzip.compress(encoded, compresslevel=level, mtime=mtime)
                      for level, mtime in ((1, 0), (9, 123456789))]
        self.assertNotEqual(*containers)
        for i, data in enumerate(containers):
            path = self.path / (str(i) + ".json.gz")
            path.write_bytes(data)
            V["same"](original, C["load"](path), "payload changed")


if __name__ == "__main__":
    unittest.main()
