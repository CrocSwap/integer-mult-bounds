#!/usr/bin/env python3
"""Artifact-integrity checks in an isolated source-bound export. Apache-2.0."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        # An explicitly local temp root also works when system temp is remote.
        self.temporary = tempfile.TemporaryDirectory(prefix=".qq16-check-", dir=ROOT)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / "research" / PACKAGE.name
        shutil.copytree(PACKAGE, self.package, ignore=shutil.ignore_patterns("__pycache__"))
        manifest = json.loads((PACKAGE / "VERIFY.json").read_text())
        for name in manifest["inputs"]:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(ROOT / name)

    def run_check(self, *extra):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package / "verify.py"), *extra],
                              cwd=self.root, capture_output=True, text=True, timeout=90)

    def test_relocated_replay_and_exclusive_emission(self):
        before = {str(p.relative_to(self.package)): p.read_bytes()
                  for p in self.package.rglob("*") if p.is_file()}
        replay = self.run_check()
        self.assertEqual(replay.returncode, 0, replay.stderr)
        self.assertIn("single_taps=768 A_defect=8 ports<=8_excluded", replay.stdout)
        after = {str(p.relative_to(self.package)): p.read_bytes()
                 for p in self.package.rglob("*") if p.is_file()}
        self.assertEqual(before, after, "default replay modified the package")
        destination = self.root / "must-not-overwrite.json"
        destination.write_text("existing content\n")
        blocked = self.run_check("--emit-result", str(destination))
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("FileExistsError", blocked.stderr)
        self.assertEqual(destination.read_text(), "existing content\n")

    def test_full_receipt_corruption_rejected(self):
        path = self.package / "RESULT.json"
        result = json.loads(path.read_text())
        result["rank_certificate"]["single_source_cases"][1]["even_basis"][0] = 2
        path.write_text(json.dumps(result))
        replay = self.run_check()
        self.assertNotEqual(replay.returncode, 0)
        self.assertIn("complete canonical receipt mismatch", replay.stderr)

    def test_reference_source_corruption_rejected(self):
        reference = self.package / "references/pr2093/verify.py"
        reference.write_bytes(reference.read_bytes() + b"\n# mutated input\n")
        replay = self.run_check()
        self.assertNotEqual(replay.returncode, 0)
        self.assertIn("source hash: PR2093 verifier", replay.stderr)


if __name__ == "__main__":
    unittest.main()
