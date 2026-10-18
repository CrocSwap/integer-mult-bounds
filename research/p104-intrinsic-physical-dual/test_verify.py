"""Behavioral source-export and integrity checks for the finite bridge."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


class ExportChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.package = cls.root / "research" / P.name
        shutil.copytree(P, cls.package, ignore=shutil.ignore_patterns("__pycache__"))
        for entry in json.loads((P / "SOURCES.json").read_text())["files"]:
            if entry["usage"] == "input":
                target = cls.root / entry["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / entry["path"], target)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_export(self, *args):
        env = os.environ.copy()
        env["PYTHONOPTIMIZE"] = "2"
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package / "verify.py"), *args],
                              cwd=self.root, env=env, text=True, capture_output=True, timeout=90)

    @contextmanager
    def replace(self, path, value):
        original = path.read_bytes()
        path.write_bytes(value)
        try:
            yield
        finally:
            path.write_bytes(original)

    def test_git_free_optimized_replay(self):
        self.assertFalse((self.root / ".git").exists())
        result = self.run_export()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["basis_columns"], 106496)

    def test_retained_source_tampering_rejected(self):
        path = self.root / "research/p104-native-channel/inputs/P104-FIXTURE.json"
        with self.replace(path, b"not JSON and must fail before parsing"):
            result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source SHA256", result.stderr)

    def test_predecessor_tampering_rejected(self):
        path = self.package / "inputs/PR2586-WORD.json"
        with self.replace(path, b"not JSON and must fail before parsing"):
            result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("predecessor SHA256", result.stderr)

    def test_adapter_payload_drift_rejected(self):
        path = self.package / "ADAPTERS.json"
        value = json.loads(path.read_text())
        value["adapters"][0]["recipe"]["left"]["phase"] ^= 1
        with self.replace(path, json.dumps(value).encode()):
            result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("regenerated adapter payload", result.stderr)

    def test_receipt_drift_rejected(self):
        path = self.package / "RESULT.json"
        value = json.loads(path.read_text())
        value["retained_rank_mass"] -= 1
        with self.replace(path, json.dumps(value).encode()):
            result = self.run_export()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("complete saved receipt", result.stderr)

    def test_regeneration_and_exclusive_output(self):
        path = self.root / "regenerated.json"
        result = self.run_export("--emit", str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(path.read_text()), json.loads((self.package / "ADAPTERS.json").read_text()))
        original = path.read_bytes()
        result = self.run_export("--emit", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FileExistsError", result.stderr)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
