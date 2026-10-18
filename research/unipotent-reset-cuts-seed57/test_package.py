#!/usr/bin/env python3
"""Portable replay and actual on-disk corruption controls. Apache-2.0."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def inventory(directory):
    return {str(p.relative_to(directory)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


class PackageChecks(unittest.TestCase):
    def run_copy(self, modify=None, readonly=False, full=False):
        with tempfile.TemporaryDirectory(prefix="reset cuts test ") as temporary:
            target = Path(temporary)/"standalone package"
            shutil.copytree(HERE,target,ignore=shutil.ignore_patterns("__pycache__"))
            if modify:
                modify(target)
            before = inventory(target)
            if readonly:
                for p in target.rglob("*"):
                    os.chmod(p,0o555 if p.is_dir() else 0o444)
                os.chmod(target,0o555)
            try:
                command = [sys.executable,"-I","-O","-B",str(target/"verify.py")]
                if not full:
                    command.append("--certificate-only")
                result = subprocess.run(command,cwd=temporary,capture_output=True,text=True,timeout=240)
                self.assertEqual(before,inventory(target),"replay changed runtime files")
            finally:
                os.chmod(target,0o755)
                for p in target.rglob("*"):
                    os.chmod(p,0o755 if p.is_dir() else 0o644)
            return result

    def test_readonly_relocated_full_replay(self):
        result = self.run_copy(readonly=True,full=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("PASS_UNIPOTENT_RESET_CUTS",result.stdout)

    def test_source_corruption(self):
        def change(root):
            p = root/"references/pr1537_model.py"
            p.write_bytes(p.read_bytes()+b"\n# changed source\n")
        result = self.run_copy(change)
        self.assertNotEqual(result.returncode,0)
        self.assertIn("source SHA256",result.stderr)

    def test_certificate_cost_corruption(self):
        def change(root):
            p = root/"CERTIFICATE.json"
            data = json.loads(p.read_text())
            data["frontier"][-1]["cost"] -= 1
            p.write_text(json.dumps(data))
        result = self.run_copy(change)
        self.assertNotEqual(result.returncode,0)
        self.assertIn("certificate differs",result.stderr)

    def test_certificate_growth_corruption(self):
        def change(root):
            p = root/"CERTIFICATE.json"
            data = json.loads(p.read_text())
            data["edges"][0]["peak"] -= 1
            p.write_text(json.dumps(data))
        result = self.run_copy(change)
        self.assertNotEqual(result.returncode,0)
        self.assertIn("certificate differs",result.stderr)


if __name__ == "__main__":
    unittest.main()
