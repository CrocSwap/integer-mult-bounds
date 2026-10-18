"""Bounded controls for source relabelling and incorrect caller inference."""

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from binding import ROOT, SOURCE_ROWS, authenticate
from model import classify, partition_receipt, validate


class BoundaryControls(unittest.TestCase):
    def copy_sources(self, root):
        shutil.copyfile(ROOT / "SOURCES.json", root / "SOURCES.json")
        for row in SOURCE_ROWS:
            target = root / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row["path"], target)
        shutil.copyfile(ROOT / "vendor/__init__.py", root / "vendor/__init__.py")

    def reject_manifest(self, change):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = json.loads((ROOT / "SOURCES.json").read_text())
            change(manifest)
            (root / "SOURCES.json").write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                authenticate(root)

    def test_live_input_cannot_be_relabelled(self):
        def change(manifest):
            manifest["retained_files"][0]["usage"] = "proof-contract"

        self.reject_manifest(change)

    def test_unknown_inventory_entry(self):
        def change(manifest):
            manifest["retained_files"].append(
                copy.deepcopy(manifest["retained_files"][0])
            )

        self.reject_manifest(change)

    def test_missing_inventory_entry(self):
        def change(manifest):
            manifest["retained_files"].pop()

        self.reject_manifest(change)

    def test_source_commit_cannot_change(self):
        def change(manifest):
            manifest["retained_files"][0]["commit"] = "0" * 40

        self.reject_manifest(change)

    def test_float_pr_number_is_not_an_integer_inventory(self):
        def change(manifest):
            manifest["retained_files"][0]["pr"] = 3154.0

        self.reject_manifest(change)

    def test_duplicate_json_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SOURCES.json").write_text(
                '{"schema_version":1,"schema_version":1}'
            )
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                authenticate(root)

    def test_source_bytes_cannot_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "package"
            root.mkdir()
            self.copy_sources(root)
            with (root / "vendor/bk2b.py").open("a") as handle:
                handle.write("\n# changed source\n")
            with self.assertRaisesRegex(ValueError, "source bytes"):
                authenticate(root)

    def test_nonprefix_partition_is_retained(self):
        # The rank-seven piece is the common support, not an endpoint.
        weights = (5, 5, 6, 7, 7, 7, 7, 7)
        result = classify(weights)["certificates"]["PR3260-ranks556-cut37"]
        self.assertEqual(result["valid_partitions"], 5)
        self.assertEqual(result["witness"]["common_support_cap"], 36)

    def test_six_cuts_are_not_five(self):
        result = classify((2, 2, 2) + (7,) * 7)
        self.assertIsNone(result["primary"])
        self.assertNotIn("PR3253-seven-flat-common5", result["certificates"])

    def test_deletion_does_not_preserve_six_dimensions(self):
        with self.assertRaisesRegex(ValueError, "lost code dimensions"):
            partition_receipt((2, 2) + (6,) * 7, (0, 1), (2, 3, 4), 6)

    def test_invalid_weights_are_rejected(self):
        for weights in ((True,) * 6, (2,) * 11, (2,) * 5 + (8,), (6, 5, 4, 3, 2, 2)):
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                validate(weights)

    def test_changed_receipt_fails_actual_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (
                "binding.py",
                "model.py",
                "verify.py",
                "RESULT.json",
                "SOURCES.json",
            ):
                shutil.copyfile(ROOT / name, root / name)
            self.copy_sources(root)
            receipt = json.loads((root / "RESULT.json").read_text())
            receipt["rows"][0]["primary"] = "unproved rule"
            (root / "RESULT.json").write_text(json.dumps(receipt))
            child = subprocess.run(
                [sys.executable, "-O", "-W", "error", "-B", str(root / "verify.py")],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            self.assertNotEqual(child.returncode, 0)
            self.assertIn("committed receipt disagrees", child.stderr)


if __name__ == "__main__":
    unittest.main()
