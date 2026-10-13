"""Portable replay and corruption controls for the standalone research package."""

import gzip
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


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="ck signed routes ")
        cls.root = Path(cls.temp.name) / "isolated source"
        shutil.copytree(HERE, cls.root / RELATIVE,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        pins = json.loads((HERE / "SOURCES.json").read_text())
        for name in pins["files"]:
            target = cls.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_command(self, script="verify.py"):
        return subprocess.run(
            [sys.executable, "-I", "-O", "-S", "-B", str(self.root / RELATIVE / script)],
            cwd=Path(self.temp.name), capture_output=True, text=True, timeout=90)

    def with_mutation(self, path, replacement, expected_error, script="verify.py"):
        original = path.read_bytes()
        try:
            path.write_bytes(replacement)
            result = self.run_command(script)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn(expected_error, result.stderr)
        finally:
            path.write_bytes(original)

    def test_optimized_relocated_recompression(self):
        """Only declared inputs are present; gzip container identity is irrelevant."""
        ck = self.root / "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/LOCAL-PROGRAMS.json.gz"
        original = ck.read_bytes()
        try:
            ck.write_bytes(gzip.compress(gzip.decompress(original), compresslevel=1, mtime=1))
            before = {str(p.relative_to(self.root)): p.read_bytes()
                      for p in self.root.rglob("*") if p.is_file()}
            result = self.run_command()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("extra_saved=926,0", result.stdout)
            after = {str(p.relative_to(self.root)): p.read_bytes()
                     for p in self.root.rglob("*") if p.is_file()}
            self.assertEqual(before, after, "read-only replay modified its inputs")
        finally:
            ck.write_bytes(original)

    def test_source_corruption_rejected(self):
        path = self.root / "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/LOCAL-PROGRAMS.json.gz"
        modified = gzip.decompress(path.read_bytes()) + b" "
        self.with_mutation(path, gzip.compress(modified), "source pin")

    def test_route_cost_forgery_rejected_by_independent_engine(self):
        path = self.root / RELATIVE / "ROUTES.json"
        obj = json.loads(path.read_text())
        obj[20]["signed"][0] -= 1
        self.with_mutation(path, json.dumps(obj).encode(), "nonminimal or wrong route",
                           "independent_check.py")

    def test_truncated_coverage_rejected(self):
        path = self.root / RELATIVE / "ROUTES.json"
        obj = json.loads(path.read_text())[:-1]
        self.with_mutation(path, json.dumps(obj).encode(), "route certificate mismatch")

    def test_invoice_forgery_rejected(self):
        path = self.root / RELATIVE / "EXPECTED.json"
        obj = json.loads(path.read_text())
        obj["local_substitution_budget"]["saving"] += 1
        self.with_mutation(path, json.dumps(obj).encode(), "receipt mismatch")

    def test_signed_instruction_corruption_rejected(self):
        path = self.root / RELATIVE / "circuit.py"
        old = path.read_text()
        new = old.replace('("add" if sign == 1 else "subtract", WORK, source)',
                          '("add", WORK, source)')
        self.assertNotEqual(new, old)
        self.with_mutation(path, new.encode(), "primitive/direct boundary disagreement")


if __name__ == "__main__":
    unittest.main(verbosity=2)
