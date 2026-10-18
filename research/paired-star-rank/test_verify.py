#!/usr/bin/env python3
"""End-to-end failure detection and portable replay checks (Apache-2.0)."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="paired-star-rank-")
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.package = self.root / "research" / "paired-star-rank"
        self.package.mkdir(parents=True)
        for name in ("verify.py", "build_certificate.py", "SOURCES.json",
                     "CERTIFICATE.json", "RESULTS.json"):
            shutil.copyfile(HERE / name, self.package / name)
        self.sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
        for name in self.sources["local_context_sha256"]:
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)

    def run_check(self, *args):
        return subprocess.run(
            [sys.executable, "-I", "-O", "-B", str(self.package / "verify.py"), *args],
            cwd=self.workspace.name, capture_output=True, text=True, check=False,
        )

    def assert_rejected(self, result, output):
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("PASS_PAIRED_STAR_RANK:", result.stdout)
        self.assertEqual(output.read_bytes(), b"previous evidence\n")

    def export_target(self):
        output = self.root / "export.json"
        output.write_bytes(b"previous evidence\n")
        return output

    def test_relocated_optimized_replay_and_regeneration(self):
        exported = self.root / "export.json"
        result = self.run_check("--write", str(exported))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(exported.read_bytes(), (HERE / "RESULTS.json").read_bytes())
        regenerated = self.root / "rebuilt.json"
        build = subprocess.run(
            [sys.executable, "-I", "-B", str(self.package / "build_certificate.py"),
             "--output", str(regenerated)], capture_output=True, text=True, check=False,
        )
        self.assertEqual(build.returncode, 0, build.stderr)
        self.assertEqual(regenerated.read_bytes(), (HERE / "CERTIFICATE.json").read_bytes())

    def test_corrupted_certificate_preserves_output(self):
        certificate = self.package / "CERTIFICATE.json"
        data = json.loads(certificate.read_text(encoding="utf-8"))
        data["cases"][-2]["decoders_hex"][0] = "0x0"
        certificate.write_text(json.dumps(data), encoding="utf-8")
        output = self.export_target()
        self.assert_rejected(self.run_check("--write", str(output)), output)

    def test_incomplete_receipt_preserves_output(self):
        receipt = self.package / "RESULTS.json"
        data = json.loads(receipt.read_text(encoding="utf-8"))
        data["cases"].pop()
        receipt.write_text(json.dumps(data), encoding="utf-8")
        output = self.export_target()
        self.assert_rejected(self.run_check("--write", str(output)), output)

    def test_context_source_and_pin_changes_are_rejected(self):
        name = next(iter(self.sources["local_context_sha256"]))
        source = self.root / name
        original = source.read_bytes()
        source.write_bytes(original + b"\nchanged\n")
        output = self.export_target()
        self.assert_rejected(self.run_check("--write", str(output)), output)
        source.write_bytes(original)
        self.sources["local_context_sha256"][name] = "0" * 64
        (self.package / "SOURCES.json").write_text(json.dumps(self.sources), encoding="utf-8")
        self.assert_rejected(self.run_check("--write", str(output)), output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
