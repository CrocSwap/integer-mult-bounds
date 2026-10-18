#!/usr/bin/env python3
"""Artifact acceptance controls, independent of another full native compilation.

Hanson Sun with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
V = runpy.run_path(str(HERE / "verify.py"))


class PackageTests(unittest.TestCase):
    def test_native_receipt_mutations(self):
        result = V["load"](HERE / "RESULT.json")
        count = 0
        for name, word in result["words"].items():
            for k in (2, 4, 5):
                receipt = word["native"][str(2*k+1)]
                V["check_columns"](receipt, k, word["prices"])
                changes = {
                    "status": "PASS", "formal_columns_checked": 1,
                    "independent_dirty_registers": 0, "local_scalar_additions": 0,
                    "bridge_additions": 0, "fresh_center_copies": 9,
                    "reverse_fresh_center_copies": 0, "local_raw_H": [],
                    "stages": receipt["stages"][:-1], "payload_prefix_upper": "1",
                    "payload_prefix_bits": 1, "negative_controls": [],
                    "copied_center_original_source_immutable": False,
                    "signed_lift_prefix": list(reversed(receipt["signed_lift_prefix"])),
                }
                for field, value in changes.items():
                    mutated = deepcopy(receipt)
                    mutated[field] = value
                    with self.subTest(word=name, stages=2*k+1, field=field):
                        with self.assertRaises(ValueError):
                            V["check_columns"](mutated, k, word["prices"])
                    count += 1
        self.assertEqual(count, 168)

    def test_candidate_binding(self):
        for tag, parent_path in V["PARENTS"].items():
            parent = V["load"](V["ROOT"] / parent_path)
            actual = V["load"](HERE / "vendor/pr1868" / ("absorbed-" + tag + ".json.gz"))
            derived = V["rebuild"](parent)
            V["equal"](derived, actual, "candidate")
            for section in ("A", "D", "C"):
                bad = deepcopy(actual)
                bad[section] = bad[section][1:]
                with self.assertRaises(ValueError):
                    V["equal"](derived, bad, "candidate")

    def test_source_corruption(self):
        manifest = V["load"](HERE / "PREDECESSOR.json")
        for row in manifest["files"]:
            data = (HERE / row["path"]).read_bytes()
            V["check_blob"](data, row)
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                V["check_blob"](data + b"\n", row)
            bad = dict(row, git_blob="0" * 40)
            with self.assertRaisesRegex(ValueError, "source Git blob"):
                V["check_blob"](data, bad)

    def test_strict_receipt_comparison(self):
        with self.assertRaises(ValueError):
            V["equal"]({"rejected": True}, {"rejected": 1}, "typed result")
        for raw in ('{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                json.loads(raw, object_pairs_hook=V["pairs"], parse_constant=V["invalid"])

    def test_minimal_relocation_and_precompile_failure(self):
        # Full Git provenance is an explicit package dependency. The temporary
        # clone shares only immutable Git objects, with a minimal copied worktree.
        with tempfile.TemporaryDirectory(prefix="twisted-package-test-") as tmp:
            root = Path(tmp) / "minimal"
            subprocess.run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(V["ROOT"]), str(root)],
                           check=True, capture_output=True, timeout=30)
            package = root / "research" / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            manifest = V["load"](HERE / "SOURCES.json")
            for row in manifest["files"]:
                if row["usage"] == "input":
                    dest = root / row["path"]
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(V["ROOT"] / row["path"], dest)
            probe = "import runpy,sys; runpy.run_path(sys.argv[1])['sources'](); print('PINS_PASS')"
            command = [sys.executable, "-I", "-O", "-B", "-c", probe, str(package / "verify.py")]
            result = subprocess.run(command, text=True, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PINS_PASS", result.stdout)
            # A dependency and the copied predecessor are each rejected before
            # the deliberately nonexistent compiler could be started.
            source = root / V["PARENTS"]["pr1062"]
            vendor = package / "vendor/pr1868/absorbed-pr1188.json.gz"
            env = dict(os.environ, CXX="compiler-must-not-be-invoked")
            for path in (source, vendor):
                original = path.read_bytes()
                try:
                    path.write_bytes(original + b"broken")
                    result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                                            env=env, text=True, capture_output=True, timeout=30)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("source SHA256", result.stderr)
                    self.assertNotIn("Compiling pinned", result.stdout)
                finally:
                    path.write_bytes(original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
