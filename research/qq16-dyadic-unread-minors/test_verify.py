#!/usr/bin/env python3
"""Exercise the public checker commands, including deliberate corruptions."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/joint-query/certificate.json.gz"


def run(script, *arguments, optimized=False):
    command = [sys.executable, "-I", "-B"]
    if optimized:
        command.append("-O")
    return subprocess.run(command + [str(HERE / script), *map(str, arguments)],
                          capture_output=True, text=True, timeout=30, check=False)


class EntryPointTests(unittest.TestCase):
    def test_optimized_and_git_free_source_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / SOURCE
            source.parent.mkdir(parents=True)
            source.write_bytes((ROOT / SOURCE).read_bytes())
            before = source.read_bytes()
            result = run("verify.py", "--repo", root, optimized=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("sets=107889 dyadic=59023 odd_factor=2501", result.stdout)
            self.assertEqual(source.read_bytes(), before)
            self.assertFalse((root / ".git").exists())

    def test_source_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / SOURCE
            source.parent.mkdir(parents=True)
            raw = (ROOT / SOURCE).read_bytes()
            source.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
            result = run("verify.py", "--repo", root, "--emit", optimized=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("packet source pin differs", result.stderr)

    def test_receipt_type_corruption_rejected(self):
        receipt = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        receipt["schema_version"] = True
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "RESULT.json"
            path.write_text(json.dumps(receipt), encoding="utf-8")
            result = run("verify.py", "--receipt", path, optimized=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt differs from complete recomputation", result.stderr)

    def test_missing_receipt_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = run("verify.py", "--receipt", Path(temporary) / "absent.json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FileNotFoundError", result.stderr)

    def test_direct_oracle_rejects_histogram_corruption(self):
        receipt = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        receipt["absolute_determinant_histograms_by_distance"][1]["48"] += 1
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "RESULT.json"
            path.write_text(json.dumps(receipt), encoding="utf-8")
            result = run("oracle.py", "--receipt", path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("direct census and determinant lemma disagree", result.stderr)


if __name__ == "__main__":
    unittest.main()
