#!/usr/bin/env python3
"""Package admission controls, using fresh temporary copies and subprocesses.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
"""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RELATIVE = HERE.relative_to(ROOT)


class PackageControls(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="xor-affine-audit-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / RELATIVE
        shutil.copytree(HERE, self.package)
        self.sources = json.loads((HERE / "SOURCE.json").read_text(encoding="utf-8"))["sha256"]
        for name in self.sources:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)

    def execute(self, script, successful, expected_text):
        result = subprocess.run(
            [sys.executable, "-I", "-O", "-B", str(self.package / script)],
            cwd=self.root, capture_output=True, text=True, timeout=60,
        )
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode == 0, successful, output)
        self.assertIn(expected_text, output)
        return output

    def mutate_json(self, name, change):
        path = self.package / name
        data = json.loads(path.read_text(encoding="utf-8"))
        change(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_relocated_optimized_read_only_replay(self):
        before = {p.relative_to(self.root): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        output = self.execute("verify.py", True, "PASS_XOR_AFFINE_AGREEMENT")
        self.assertIn("PASS_XOR_AFFINE_INDEPENDENT", output)
        after = {p.relative_to(self.root): p.read_bytes()
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after, "Replay mutated or added source files")

    def test_source_drift_is_rejected_before_any_success(self):
        name = next(iter(self.sources))
        path = self.root / name
        path.write_bytes(path.read_bytes() + b"\nsource drift control\n")
        output = self.execute("verify.py", False, "Source pin mismatch")
        self.assertNotIn("PASS_XOR_AFFINE", output)

    def test_missing_source_is_rejected(self):
        (self.root / next(iter(self.sources))).unlink()
        self.execute("verify.py", False, "FileNotFoundError")

    def test_false_coverage_receipt_is_rejected(self):
        self.mutate_json("CERTIFICATE.json",
                         lambda r: r["coverage"].update(mask_count=509))
        output = self.execute("verify.py", False, "Certificate differs")
        self.assertNotIn("PASS_XOR_AFFINE", output)

    def test_independent_histogram_binding_rejects_drift(self):
        self.mutate_json("CERTIFICATE.json",
                         lambda r: r["census"][0].update(all_histograms_sha256="0" * 64))
        self.execute("independent.py", False, "Independent histogram differs")

    def test_independent_receipt_rejects_wrong_boundary_count(self):
        self.mutate_json("INDEPENDENT.json",
                         lambda r: r["negative_control"].update(modular_solutions=31))
        self.execute("independent.py", False, "Independent receipt differs")


if __name__ == "__main__":
    unittest.main(verbosity=2)
