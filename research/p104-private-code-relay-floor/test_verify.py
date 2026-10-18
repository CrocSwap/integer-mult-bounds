#!/usr/bin/env python3
"""Public CLI controls for source binding, typed receipts and portable replay.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
Only temporary exports are changed; no source input is modified in place.
"""
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PACKAGE = HERE.relative_to(ROOT)
INPUTS = ["research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
          "research/p104-native-channel/inputs/P104-FIXTURE.json"]


def hashes(root):
    return {p.relative_to(root).as_posix(): sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class ExportControls(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="p104-private-code-")
        self.root = Path(self.temporary.name)
        for relative in [*(str(PACKAGE / name) for name in ("verify.py", "SOURCES.json", "RESULT.json")),
                         *INPUTS]:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)

    def tearDown(self):
        # Restore permissions after the read-only export control.
        for path in [self.root, *self.root.rglob("*")]:
            path.chmod(0o755 if path.is_dir() else 0o644)
        self.temporary.cleanup()

    def run_cli(self, *arguments):
        return subprocess.run([sys.executable, "-I", "-O", "-B",
                               str(self.root / PACKAGE / "verify.py"), *map(str, arguments)],
                              cwd=self.root, text=True, capture_output=True,
                              timeout=30, env=dict(os.environ))

    def test_readonly_export(self):
        before = hashes(self.root)
        for path in self.root.rglob("*"):
            path.chmod(0o555 if path.is_dir() else 0o444)
        self.root.chmod(0o555)
        run = self.run_cli()
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("lifetimes=208 controls=12 no_new_kappa", run.stdout)
        self.assertEqual(hashes(self.root), before)

    def test_source_drift(self):
        path = self.root / INPUTS[0]
        path.write_bytes(path.read_bytes() + b"\n")
        run = self.run_cli()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("source hash mismatch", run.stderr)

    def test_changed_mathematical_receipt(self):
        path = self.root / PACKAGE / "RESULT.json"
        receipt = json.loads(path.read_text())
        receipt["helper_lifetime_floor"] = 207
        path.write_text(json.dumps(receipt))
        run = self.run_cli()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("receipt mismatch", run.stderr)

    def test_bool_is_not_integer(self):
        path = self.root / PACKAGE / "RESULT.json"
        receipt = json.loads(path.read_text())
        # Python equality alone equates True and 1; this comparison must not.
        receipt["schema_version"] = True
        path.write_text(json.dumps(receipt))
        run = self.run_cli()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("receipt mismatch", run.stderr)

    def test_duplicate_receipt_key(self):
        path = self.root / PACKAGE / "RESULT.json"
        text = path.read_text()
        path.write_text(text.replace('"schema_version": 1',
                                     '"schema_version": 1, "schema_version": 1'))
        run = self.run_cli()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("duplicate JSON key", run.stderr)

    def test_exclusive_verified_output(self):
        path = self.root / "verified.json"
        run = self.run_cli("--out", path)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(path.read_text()),
                         json.loads((self.root / PACKAGE / "RESULT.json").read_text()))
        before = path.read_bytes()
        run = self.run_cli("--out", path)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("FileExistsError", run.stderr)
        self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
