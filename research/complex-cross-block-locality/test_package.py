"""Corruption and minimal read-only relocation checks for the public replay.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = HERE.relative_to(ROOT)
ARCHIVE = Path("research/community-frontier1042-audit/selected-replay.tar.gz")


def run(root, script, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(root / PACKAGE / script), *map(str, args)],
                          cwd=root.parent, capture_output=True, text=True, timeout=60)


def export(root):
    shutil.copytree(HERE, root / PACKAGE, ignore=shutil.ignore_patterns("__pycache__"))
    (root / ARCHIVE).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / ARCHIVE, root / ARCHIVE)


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class PackageTests(unittest.TestCase):
    def test_changed_primary_certificate_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            receipt = json.loads((HERE / "CERTIFICATE.json").read_text())
            receipt["profile"]["1"] -= 1
            bad = Path(d) / "wrong.json"
            bad.write_text(json.dumps(receipt))
            result = run(ROOT, "verify.py", "--certificate", bad)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("saved certificate mismatch", result.stderr)

    def test_source_drift_is_rejected_before_replay(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "source export"
            export(root)
            with (root / ARCHIVE).open("ab") as f:
                f.write(b"changed source")
            for script, message in (("verify.py", "source hash mismatch"),
                                    ("independent.py", "input source mismatch")):
                result = run(root, script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

    def test_changed_independent_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "source export"
            export(root)
            path = root / PACKAGE / "INDEPENDENT.json"
            receipt = json.loads(path.read_text())
            receipt["boundary_witnesses"][0]["rank"] = 191
            path.write_text(json.dumps(receipt))
            result = run(root, "independent.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("independent saved receipt mismatch", result.stderr)

    def test_minimal_read_only_export_is_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "read only export with spaces"
            export(root)
            before = hashes(root)
            paths = [root, *root.rglob("*")]
            try:
                for p in paths:
                    p.chmod(0o555 if p.is_dir() else 0o444)
                for script in ("verify.py", "independent.py"):
                    result = run(root, script)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("PASS_", result.stdout)
                self.assertEqual(hashes(root), before)
            finally:
                for p in paths:
                    p.chmod(0o755 if p.is_dir() else 0o644)


if __name__ == "__main__":
    unittest.main()
