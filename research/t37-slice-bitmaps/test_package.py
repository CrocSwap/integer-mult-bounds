#!/usr/bin/env python3
"""Meaningful source, receipt, patch and inherited-assertion controls."""
import ast
import copy
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))
A = runpy.run_path(str(C["HERE"] / "adapter.py"))
K = runpy.run_path(str(C["HERE"] / "kernel.py"))


class PackageControls(unittest.TestCase):
    def test_missing_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                C["pins"](Path(tmp))

    def test_changed_source(self):
        manifest = C["load"](C["HERE"] / "SOURCES.json")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in manifest["files"]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(C["ROOT"] / name, target)
            path = root / "research/complex-t21-owners/independent_check.py"
            path.write_bytes(path.read_bytes() + b"\n# changed source\n")
            with self.assertRaisesRegex(ValueError, "source hash mismatch"):
                C["pins"](root)

    def test_duplicate_json_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text('{"width":9,"width":8}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                C["load"](path)

    def test_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text('{"width":NaN}')
            with self.assertRaisesRegex(ValueError, "nonfinite JSON"):
                C["load"](path)

    def test_typed_receipts(self):
        with self.assertRaisesRegex(ValueError, "typed receipt"):
            C["same"]({"count": 1}, {"count": True}, "typed receipt")

    def test_complete_receipt_field_required(self):
        receipt = C["load"](C["HERE"] / "EXPECTED.json")["complete_receipt"]
        altered = copy.deepcopy(receipt)
        del altered["checked_busy_family_windows"]
        with self.assertRaisesRegex(ValueError, "full receipt"):
            C["same"](receipt, altered, "full receipt")

    def test_input_inventory_required(self):
        manifest = C["load"](C["HERE"] / "SOURCES.json")
        receipt = C["load"](C["ROOT"] / manifest["frozen_receipt"])
        receipt["input_sha256"].pop(next(iter(receipt["input_sha256"])))
        with self.assertRaisesRegex(ValueError, "receipt input inventory"):
            C["normalize"](receipt, manifest)

    def test_patch_fails_on_changed_predicate(self):
        source = (C["ROOT"] / "research/complex-t21-owners/independent_check.py").read_text()
        node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "check_roles")
        function = "\n".join(source.splitlines()[node.lineno-1:node.end_lineno]) + "\n"
        with self.assertRaisesRegex(ValueError, "pinned occupied-cell block changed"):
            K["patch"](function.replace("not used[bin_key] & cells", "True"))

    def test_changed_archive_member_hash(self):
        manifest = copy.deepcopy(C["load"](C["HERE"] / "SOURCES.json"))
        manifest["members"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "archive member hash"):
                C["materialize"](C["ROOT"], Path(tmp) / "inputs", manifest)

    def test_optimized_wrapper_still_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run"
            result = subprocess.run([sys.executable, "-I", "-O", "-B", C["HERE"] / "adapter.py",
                                     "--output", out], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Assertions must remain enabled", result.stderr)
            self.assertFalse((out / "receipt.json").exists())

    def test_existing_output_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "new output path"):
                A["run"](None, Path(tmp))


if __name__ == "__main__":
    unittest.main()
