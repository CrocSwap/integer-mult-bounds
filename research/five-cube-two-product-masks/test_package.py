#!/usr/bin/env python3
"""Package boundary and reproducibility checks. Apache-2.0; Codex-assisted."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def call(script, *args, cwd=None):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(script), *map(str, args)],
                          cwd=cwd, capture_output=True, text=True, timeout=240)


class PackageChecks(unittest.TestCase):
    def test_deterministic_certificate(self):
        with tempfile.TemporaryDirectory(prefix="two-product-regeneration-") as directory:
            output = Path(directory) / "regenerated.json"
            result = call(PACKAGE / "generate.py", "--output", output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_bytes(), (PACKAGE / "CERTIFICATE.json").read_bytes())

    def test_optimized_standalone_replay_and_source_drift(self):
        with tempfile.TemporaryDirectory(prefix="two product relocated ") as directory:
            root = Path(directory)
            relocated = root / "research" / PACKAGE.name
            shutil.copytree(PACKAGE, relocated)
            sources = json.loads((PACKAGE / "SOURCES.json").read_text())
            inputs = [r for r in sources["files"] if r["usage"] == "input"]
            for row in inputs:
                destination = root / row["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row["path"], destination)
            receipt = root / "receipt.json"
            result = call(relocated / "verify.py", "--receipt", receipt, cwd=root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(receipt.read_text()), json.loads((PACKAGE / "RECEIPT.json").read_text()))
            source = root / inputs[0]["path"]
            source.write_bytes(source.read_bytes() + b"\nchanged source\n")
            result = call(relocated / "verify.py", cwd=root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source hash mismatch", result.stderr)

    def test_corrupt_certificate_rejects(self):
        original = json.loads((PACKAGE / "CERTIFICATE.json").read_text())
        with tempfile.TemporaryDirectory(prefix="two-product-corrupt-") as directory:
            path = Path(directory) / "corrupt.json"
            for defect in ("target", "rank", "domain"):
                data = json.loads(json.dumps(original))
                if defect == "target":
                    data["target_state"] ^= 1
                    message = "incorrect state space or target"
                elif defect == "rank":
                    data["orbits"][0]["term_ranks"][0] += 1
                    message = "incorrect rational term rank"
                else:
                    data["domain"].pop()
                    message = "domain must contain 720 codes"
                path.write_text(json.dumps(data))
                with self.subTest(defect=defect):
                    result = call(PACKAGE / "verify.py", "--certificate", path)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(message, result.stderr)

    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory(prefix="two-product-existing-") as directory:
            path = Path(directory) / "keep.txt"
            original = b"preserve these bytes\n"
            path.write_bytes(original)
            for script, argument in (("generate.py", "--output"), ("verify.py", "--receipt")):
                with self.subTest(script=script):
                    result = call(PACKAGE / script, argument, path)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
