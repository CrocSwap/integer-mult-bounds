#!/usr/bin/env python3
"""On-disk controls and relocation for the source-shear certificate."""
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
        self.temp = tempfile.TemporaryDirectory(prefix="source shear replay ")
        self.root = Path(self.temp.name)
        self.package = self.root / "research" / HERE.name
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns("__pycache__"))
        manifest = json.loads((HERE / "SOURCES.json").read_text())
        for row in manifest["files"]:
            if row["usage"] == "input":
                target = self.root / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row["path"], target)

    def tearDown(self):
        for path in self.root.rglob("*"):
            path.chmod(0o755 if path.is_dir() else 0o644)
        self.temp.cleanup()

    def run_check(self, name="verify.py", *args, passes=True):
        result = subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package / name), *map(str, args)],
                                cwd=self.root, capture_output=True, text=True, timeout=30)
        if passes:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, "corruption accepted")
        return result

    def mutate_receipt(self, field, value):
        path = self.package / "CERTIFICATE.json"
        data = json.loads(path.read_text())
        data[field] = value
        path.write_text(json.dumps(data))

    def test_read_only_relocation(self):
        for path in self.root.rglob("*"):
            path.chmod(0o555 if path.is_dir() else 0o444)
        self.run_check()
        self.run_check("independent.py")

    def test_deterministic_export_and_output_preservation(self):
        output = self.root / "fresh.json"
        self.run_check("verify.py", "--write", output)
        self.assertEqual(output.read_bytes(), (HERE / "CERTIFICATE.json").read_bytes())
        self.run_check("verify.py", "--write", output, passes=False)
        self.assertEqual(output.read_bytes(), (HERE / "CERTIFICATE.json").read_bytes())

    def test_unpaid_shear_and_false_minimum(self):
        for field, value in (("identity_row_xors", 0), ("minimum_shears_at_ten_queries", 2),
                             ("unit_tariff", {"candidate": 2740, "predecessor": 2760, "read_only_repair": 2812})):
            with self.subTest(field=field):
                self.mutate_receipt(field, value)
                self.run_check(passes=False)
                shutil.copyfile(HERE / "CERTIFICATE.json", self.package / "CERTIFICATE.json")

    def test_live_and_frozen_source_drift(self):
        for name in (self.root / "research/universal-connector-boundary/README.md",
                     self.package / "sources/PROOF.md"):
            with self.subTest(path=name):
                original = name.read_bytes()
                name.write_bytes(original + b"\ncorrupted contract\n")
                self.run_check(passes=False)
                name.write_bytes(original)

    def test_bad_readout_and_bad_path(self):
        data = json.loads((HERE / "CERTIFICATE.json").read_text())
        pairs = data["readout_pairs"]
        pairs[0] = [0, 0]
        self.mutate_receipt("readout_pairs", pairs)
        self.run_check(passes=False)
        self.run_check("independent.py", passes=False)
        shutil.copyfile(HERE / "CERTIFICATE.json", self.package / "CERTIFICATE.json")
        self.mutate_receipt("points", [0] * 11)
        self.run_check(passes=False)
        self.run_check("independent.py", passes=False)

    def test_wrong_predecessor_head(self):
        path = self.package / "PREDECESSOR.json"
        data = json.loads(path.read_text())
        data["head"] = "0" * 40
        path.write_text(json.dumps(data))
        self.run_check(passes=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
