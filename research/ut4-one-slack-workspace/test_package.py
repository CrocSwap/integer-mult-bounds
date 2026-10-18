#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Boundary/fault controls; prepared for @ToikY with substantial OpenAI Codex assistance."""
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
spec = importlib.util.spec_from_file_location("workspace_primary", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

def run(path, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(path), *map(str, args)],
                          capture_output=True, text=True, timeout=120)

def relocate(root):
    package = root / "research" / HERE.name
    shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
    inputs = [row["path"] for row in json.loads((HERE / "SOURCES.json").read_text())["files"]
              if row["usage"] == "input"]
    for name in inputs:
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    return package, inputs

class PackageTests(unittest.TestCase):
    def test_one_slack_and_threshold(self):
        for exception in range(-1, 6):
            spans = [2] * 6
            counts = [4, 6, 4]
            if exception >= 0:
                spans[exception] = 3
                counts[exception // 2] += 1
            answer = v.one_slack_orientation(2, counts, spans)
            self.assertEqual(answer, {"columns": exception < 0 or exception % 2 == 1,
                                      "rows": exception < 0 or exception % 2 == 0})
        for spans, counts in (([3, 2, 2, 3, 2, 2], [5, 7, 4]),
                              ([2, 2, 3, 2, 2, 3], [4, 7, 5])):
            with self.assertRaisesRegex(ValueError, "outside one-slack length threshold"):
                v.one_slack_orientation(2, counts, spans)
        with self.assertRaisesRegex(ValueError, "requires w>=2"):
            v.one_slack_orientation(1, [2, 4, 2], [1] * 6)

    def test_mixed_orientation_has_actual_feedback(self):
        word = [("a", 1, 4), ("b", 4, 1)]
        with self.assertRaisesRegex(ValueError, "no common triangular orientation"):
            v.compress(word, 3, 2)
        corner = v.active_corner(v.formal_product(word, 3), 2)
        self.assertNotEqual(corner, v.formal_product([], 2))
        self.assertNotEqual(v.regular_columns(corner, 2), v.regular_columns({0: [1, 2]}, 2))

    def test_invalid_paid_alphabet_and_domain(self):
        for word, roles in (([("d", 1, 1)], 3), ([("a", True, 1)], 3),
                            ([("a", 1, 8)], 3), ([("a", 0, 1)], 3), ([], True)):
            with self.assertRaises(ValueError):
                v.formal_product(word, roles)
        for width in (0, 4, True):
            with self.assertRaises(ValueError):
                v.compress([], 3, width)

    def test_real_source_and_vendor_faults_reject_before_import(self):
        with tempfile.TemporaryDirectory(prefix="ut4-input-fault-") as raw:
            root = Path(raw)
            package, inputs = relocate(root)
            source = root / inputs[0]
            honest = source.read_bytes()
            source.write_bytes(honest + b"\nchanged\n")
            result = run(package / "verify.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("pinned model source changed", result.stderr)
            source.write_bytes(honest)
            (package / "quotient.py").write_text('raise RuntimeError("VENDOR_IMPORTED")\n')
            result = run(package / "verify.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("pinned quotient source changed", result.stderr)
            self.assertNotIn("VENDOR_IMPORTED", result.stderr)

    def test_actual_receipt_fault_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="ut4-receipt-fault-") as raw:
            package, _ = relocate(Path(raw))
            path = package / "CERTIFICATE.json"
            receipt = json.loads(path.read_text())
            receipt["ordered_triangular_pairs"] -= 1
            path.write_text(json.dumps(receipt))
            result = run(package / "verify.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("certificate differs", result.stderr)
            occupied = Path(raw) / "occupied.json"
            occupied.write_text("keep")
            result = run(package / "verify.py", "--write-receipt", occupied)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(occupied.read_text(), "keep")

    def test_optimized_readonly_relocation(self):
        with tempfile.TemporaryDirectory(prefix="ut4 readonly path ") as raw:
            root = Path(raw)
            package, _ = relocate(root)
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            for path in root.rglob("*"):
                path.chmod(0o555 if path.is_dir() else 0o444)
            root.chmod(0o555)
            try:
                for name in ("verify.py", "independent.py"):
                    result = run(package / name)
                    self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(before, {str(p.relative_to(root)): p.read_bytes()
                                         for p in root.rglob("*") if p.is_file()})
            finally:
                root.chmod(0o755)
                for path in root.rglob("*"):
                    path.chmod(0o755 if path.is_dir() else 0o644)
if __name__ == "__main__":
    unittest.main(verbosity=2)
