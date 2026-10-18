#!/usr/bin/env python3
"""Package-boundary controls; mathematical controls live in verify.py.
Gareth Davidson, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V


class PackageTests(unittest.TestCase):
    def test_expected_type_and_value(self):
        value = V.quick()
        V.check_expected("quick", value)
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            data = {"quick": value}
            data["quick"]["censuses"][0]["histogram"][0] = True
            (p / "EXPECTED.json").write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "expected quick"):
                V.check_expected("quick", V.quick(), p)

    def test_native_distance_corruption(self):
        distances = bytearray([255] * 4)
        distances[V.A.encode((1,))] = 0
        distances[V.A.encode((3,))] = 1
        V.census(1, distances)
        distances[V.A.encode((3,))] = 0
        with self.assertRaisesRegex(ValueError, "Cayley distance"):
            V.census(1, distances)

    def test_missing_source_and_json_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            pins = V.load(V.HERE / "SOURCES.json")
            pins["files"] = [r for r in pins["files"] if r["path"] != sorted(V.INPUTS)[0]]
            (p / "SOURCES.json").write_text(json.dumps(pins))
            with self.assertRaisesRegex(ValueError, "source inventory"):
                V.source_check(V.ROOT, p)
            for invalid in ['{"x":1,"x":2}', '{"x":NaN}']:
                (p / "bad.json").write_text(invalid)
                with self.assertRaises(ValueError):
                    V.load(p / "bad.json")

    def test_readonly_relocation_and_live_corruption(self):
        with tempfile.TemporaryDirectory(prefix="binary affine export ") as temp:
            root = Path(temp)
            package = root / "research" / V.HERE.name
            shutil.copytree(V.HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            for name in V.INPUTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(V.ROOT / name, target)
            files = [p for p in root.rglob("*") if p.is_file()]
            before = {str(p.relative_to(root)): V.sha(p.read_bytes()) for p in files}
            try:
                for p in files:
                    p.chmod(0o444)
                process = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"),
                                          "--quick"], cwd="/tmp", capture_output=True, text=True, timeout=60)
                self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                self.assertIn("not_full_dimension4_census", process.stdout)
                self.assertEqual(before, {str(p.relative_to(root)): V.sha(p.read_bytes())
                                          for p in root.rglob("*") if p.is_file()})
            finally:
                for p in files:
                    p.chmod(0o644)
            source = root / sorted(V.INPUTS)[0]
            source.write_text(source.read_text() + "\ncorruption\n")
            with self.assertRaisesRegex(ValueError, "source hash"):
                V.source_check(root, package)

    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            keep = p / "keep"
            keep.write_text("untouched")
            process = subprocess.run([sys.executable, "-I", "-B", str(V.HERE / "verify.py"),
                                      "--full", "--work", str(p)], capture_output=True,
                                     text=True, timeout=60)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("output directory already exists", process.stdout + process.stderr)
            self.assertEqual(keep.read_text(), "untouched")
            self.assertEqual([p.name for p in p.iterdir()], ["keep"])


if __name__ == "__main__":
    unittest.main()
