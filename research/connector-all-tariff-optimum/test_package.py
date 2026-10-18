#!/usr/bin/env python3
"""Focused package behavior controls. Apache-2.0; substantial Codex assistance."""
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("tariff_verifier", HERE / "verify.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


def export(target):
    package = target / "research" / HERE.name
    package.mkdir(parents=True)
    for name in ("verify.py", "SOURCES.json", "SELECTION.json", "RESULT.json"):
        shutil.copyfile(HERE / name, package / name)
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for source in manifest["files"]:
        if source["usage"] == "input":
            destination = target / source["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / source["path"], destination)
    return package


def run(package, cwd, *arguments):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"),
                           *map(str, arguments)], cwd=cwd, capture_output=True, text=True,
                          timeout=90)


def tree_hashes(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*") if path.is_file()}


class PackageBehavior(unittest.TestCase):
    def test_exact_tariff_api_and_every_region(self):
        receipt = json.loads((HERE / "RESULT.json").read_text())
        cases = [([1] * 36, 74), ([10] * 7 + [1] + [10] * 28, 722)]
        last_cheap = [10] * 35 + [1]
        cases.append((last_cheap, 704))
        for prices, expected in cases:
            self.assertEqual(verifier.optimum(prices)[0], expected)
        for witness in receipt["witnesses"]:
            kind, port = witness["extra"]
            index = port if kind == "B" else port + 4
            prices = [Fraction(7, 3)] * 36
            prices[index] = Fraction(1, 5)
            value, chosen = verifier.optimum(prices)
            self.assertEqual(chosen, index)
            self.assertEqual(value, sum(count * price for count, price in
                                       zip(verifier.profile(witness["events"]), prices)))
        for invalid in ([1] * 35, [0] + [1] * 35, [1.0] * 36):
            with self.assertRaises(ValueError):
                verifier.optimum(invalid)

    def test_live_source_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "export"
            package = export(root)
            source = root / "research/universal-connector-boundary/CERTIFICATE.json"
            source.write_bytes(source.read_bytes() + b"\n")
            result = run(package, temp)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source SHA256 mismatch", result.stderr)

    def test_receipt_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            package = export(Path(temp) / "export")
            receipt_path = package / "RESULT.json"
            receipt = json.loads(receipt_path.read_text())
            receipt["eligible_extra_readout_masks"].append(3)
            receipt_path.write_text(json.dumps(receipt))
            result = run(package, temp)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("committed receipt mismatch", result.stderr)

    def test_readonly_relocation_and_exclusive_receipts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "export"
            package = export(root)
            before = tree_hashes(root)
            files = [path for path in root.rglob("*") if path.is_file()]
            directories = [path for path in root.rglob("*") if path.is_dir()]
            try:
                for path in files:
                    path.chmod(0o444)
                for path in reversed(directories):
                    path.chmod(0o555)
                root.chmod(0o555)
                result = run(package, temp)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("PASS_CONNECTOR_ALL_TARIFF_OPTIMUM", result.stdout)
                output = Path(temp) / "new-result.json"
                created = run(package, temp, "--write-result", output)
                self.assertEqual(created.returncode, 0, created.stderr)
                self.assertEqual(json.loads(output.read_text()),
                                 json.loads((package / "RESULT.json").read_text()))
                old = output.read_bytes()
                duplicate = run(package, temp, "--write-result", output)
                self.assertNotEqual(duplicate.returncode, 0)
                self.assertEqual(output.read_bytes(), old)
                self.assertEqual(tree_hashes(root), before)
            finally:
                root.chmod(0o755)
                for path in directories:
                    path.chmod(0o755)
                for path in files:
                    path.chmod(0o644)


if __name__ == "__main__":
    unittest.main(verbosity=2)
