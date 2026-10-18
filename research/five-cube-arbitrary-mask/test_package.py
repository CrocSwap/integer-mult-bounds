#!/usr/bin/env python3
"""CLI corruption and relocation controls, without modifying original inputs."""
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


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="five cube package ")
        self.root = Path(self.temporary.name)
        self.package = self.root / "research" / HERE.name
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns("__pycache__"))
        records = json.loads((HERE / "SOURCES.json").read_text())["files"]
        self.inputs = [r["path"] for r in records if r["usage"] == "input"]
        for relative in self.inputs:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)

    def tearDown(self):
        for path in self.root.rglob("*"):
            path.chmod(0o755 if path.is_dir() else 0o644)
        self.temporary.cleanup()

    def command(self, script, *args, ok=True):
        result = subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package / script), *args],
                                cwd=self.root, capture_output=True, text=True, timeout=120)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS_", result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, "mutation unexpectedly accepted")
            self.assertIn("FAIL_", result.stderr)
        return result

    def mutate_receipt(self, change):
        path = self.package / "CERTIFICATE.json"
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def test_changed_rank_rejected_by_both(self):
        self.mutate_receipt(lambda x: x["fixtures"][0]["ranks"].__setitem__(0, 15))
        self.command("verify.py", ok=False)
        self.command("independent.py", ok=False)

    def test_missing_fixture_and_forged_potential_rejected(self):
        original = (self.package / "CERTIFICATE.json").read_bytes()
        self.mutate_receipt(lambda x: x["fixtures"].pop())
        self.command("independent.py", ok=False)
        (self.package / "CERTIFICATE.json").write_bytes(original)
        self.mutate_receipt(lambda x: x["primitives"]["potentials"][0].__setitem__(17, 3))
        self.command("independent.py", ok=False)

    def test_changed_source_rejected_by_both(self):
        path = self.root / self.inputs[0]
        path.write_bytes(path.read_bytes() + b"\nchanged source\n")
        self.command("verify.py", ok=False)
        self.command("independent.py", ok=False)

    def test_existing_output_preserved(self):
        target = self.root / "occupied.json"
        target.write_bytes(b"keep this output\n")
        self.command("verify.py", "--write-certificate", str(target), ok=False)
        self.assertEqual(target.read_bytes(), b"keep this output\n")

    def test_read_only_optimized_relocation(self):
        files = [p for p in self.root.rglob("*") if p.is_file()]
        before = {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        for path in files:
            path.chmod(0o444)
        for path in sorted((p for p in self.root.rglob("*") if p.is_dir()), reverse=True):
            path.chmod(0o555)
        self.command("verify.py")
        self.command("independent.py")
        after_files = [p for p in self.root.rglob("*") if p.is_file()]
        after = {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in after_files}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main(verbosity=2)
