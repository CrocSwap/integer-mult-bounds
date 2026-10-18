"""CLI corruption, optimized replay, source bindings and read-only relocation controls."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


class PackageTests(unittest.TestCase):
    def run_cli(self, package, filename="verify.py", optimized=False):
        return subprocess.run([sys.executable, "-I", *(["-O"] if optimized else []), "-B",
                               str(package / filename)], capture_output=True, text=True, timeout=45)

    def copied(self, directory):
        root = Path(directory)
        package = root / "research" / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        inventory = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
        for row in inventory["files"]:
            if row["usage"] == "input":
                destination = root / row["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(REPO / row["path"], destination)
        return root, package

    def scratch(self):
        return tempfile.TemporaryDirectory(prefix="minimum-query-tests-", dir=REPO.parent)

    def test_normal_and_optimized_read_only(self):
        files = [p for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
        before = {p: sha256(p.read_bytes()).hexdigest() for p in files}
        for optimized in (False, True):
            for filename in ("verify.py", "dense.py"):
                result = self.run_cli(HERE, filename, optimized)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, {p: sha256(p.read_bytes()).hexdigest() for p in files})

    def test_source_export_relocation(self):
        with self.scratch() as directory:
            _, package = self.copied(directory)
            result = self.run_cli(package, optimized=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = self.run_cli(package, "dense.py", True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_corrupted_live_source(self):
        with self.scratch() as directory:
            root, package = self.copied(directory)
            source = root / "research/universal-connector-boundary/CERTIFICATE.json"
            source.write_bytes(source.read_bytes() + b" ")
            result = self.run_cli(package, optimized=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source drift", result.stderr)

    def test_corrupted_receipt(self):
        with self.scratch() as directory:
            _, package = self.copied(directory)
            source = package / "RESULT.json"
            receipt = json.loads(source.read_text(encoding="utf-8"))
            receipt["GL3_prefix_bases"] += 1
            source.write_text(json.dumps(receipt), encoding="utf-8")
            result = self.run_cli(package, optimized=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("stored result drift", result.stderr)

    def test_dense_rejects_unrestored_source(self):
        with self.scratch() as directory:
            _, package = self.copied(directory)
            source = package / "CERTIFICATE.json"
            certificate = json.loads(source.read_text(encoding="utf-8"))
            certificate["schedules"]["minimum_queries"]["word"].pop()
            source.write_text(json.dumps(certificate), encoding="utf-8")
            result = self.run_cli(package, "dense.py", True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("dense root forward failed", result.stderr)

    def test_duplicate_key_rejected(self):
        with self.scratch() as directory:
            _, package = self.copied(directory)
            source = package / "CERTIFICATE.json"
            original = source.read_text(encoding="utf-8")
            source.write_text(original.replace('"n": 5,', '"n": 5, "n": 5,', 1), encoding="utf-8")
            result = self.run_cli(package, optimized=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate JSON key", result.stderr)

    def test_deterministic_regeneration(self):
        with self.scratch() as directory:
            _, package = self.copied(directory)
            before = {name: (package / name).read_bytes() for name in ("CERTIFICATE.json", "RESULT.json")}
            result = subprocess.run([sys.executable, "-I", "-B", str(package / "verify.py"), "--generate"],
                                    capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(before, {name: (package / name).read_bytes() for name in before})


if __name__ == "__main__":
    unittest.main()
