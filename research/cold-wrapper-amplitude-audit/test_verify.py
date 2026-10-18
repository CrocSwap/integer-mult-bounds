#!/usr/bin/env python3
"""Failure-detection checks for the standalone finite audit (Apache-2.0)."""

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


class AdmissionTests(unittest.TestCase):
    def run_checker(self, package=HERE, root=ROOT, extra=()):
        return subprocess.run(
            [sys.executable, "-I", "-O", "-B", str(package / "verify.py"),
             "--root", str(root), *map(str, extra)],
            cwd=package, text=True, capture_output=True, timeout=30,
        )

    def source_fixture(self, destination):
        sources = json.loads((HERE / "SOURCES.json").read_text())
        paths = list(sources["files"])
        paths += [p["path"] for artifacts in sources["artifacts"].values()
                  for p in artifacts.values()]
        for path in paths:
            target = destination / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)
        return sources

    def test_isolated_optimized_replay(self):
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("70 rejected mutations", result.stdout)

    def test_relocated_minimal_checkout_and_container_independence(self):
        with tempfile.TemporaryDirectory(prefix="cold wrapper audit ") as directory:
            root = Path(directory)
            sources = self.source_fixture(root)
            for artifacts in sources["artifacts"].values():
                path = root / artifacts["CANONICAL-WORD.json.gz"]["path"]
                payload = gzip.decompress(path.read_bytes())
                path.write_bytes(gzip.compress(payload, compresslevel=1, mtime=123))
            result = self.run_checker(root=root)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_changed_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = self.source_fixture(root)
            target = root / next(iter(sources["files"]))
            with target.open("ab") as stream:
                stream.write(b"\n")
            result = self.run_checker(root=root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Source hash mismatch", result.stderr)

    def test_changed_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = self.source_fixture(root)
            path = root / sources["artifacts"]["ck"]["RESIDUAL-ADAPTERS.json"]["path"]
            value = json.loads(path.read_text())
            recipe = value["recipes"]["0:52"]
            recipe["right"]["phase"] = (recipe["right"]["phase"] + 1) % 4
            path.write_text(json.dumps(value))
            result = self.run_checker(root=root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Artifact semantic hash mismatch", result.stderr)

    def test_changed_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            for name in ("verify.py", "SOURCES.json"):
                shutil.copyfile(HERE / name, package / name)
            receipt = json.loads((HERE / "EXPECTED.json").read_text())
            receipt["negative_controls"][0]["different_columns"] = 0
            (package / "EXPECTED.json").write_text(json.dumps(receipt))
            result = self.run_checker(package=package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Receipt differs", result.stderr)

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "receipt.json"
            target.write_text("keep this output\n")
            result = self.run_checker(extra=("--write", target))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FileExistsError", result.stderr)
            self.assertEqual(target.read_text(), "keep this output\n")


if __name__ == "__main__":
    unittest.main()
