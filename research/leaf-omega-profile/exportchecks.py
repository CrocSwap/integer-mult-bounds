"""Real CLI relocation and failure controls. ywz65/Codex; Apache-2.0."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PASS = "PASS_OMEGA_PROFILE:"


class ExportChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="omega-export-")
        self.root = Path(self.tmp.name) / "standalone"
        self.package = self.root / "research" / HERE.name
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns("__pycache__"))
        manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
        self.inputs = [item for item in manifest["files"] if item.get("usage") == "input"]
        self.assertEqual(len(self.inputs), 5)
        for item in self.inputs:
            destination = self.root / item["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / item["path"], destination)

    def tearDown(self):
        for path in self.root.rglob("*"):
            if path.is_file():
                path.chmod(stat.S_IREAD | stat.S_IWRITE)
        self.tmp.cleanup()

    def cli(self, *args, program="verify.py"):
        env = os.environ.copy()
        env["PATH"] = ""
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, "-I", "-O", "-B", str(self.package / program), *args],
            cwd=self.root, env=env, capture_output=True, text=True, timeout=120)

    def rejected(self, result, reason):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(reason, result.stderr)
        self.assertNotIn(PASS, result.stdout)

    def inventory(self):
        return {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in self.root.rglob("*") if path.is_file()}

    def test_read_only_git_free_both_engines(self):
        self.assertFalse((self.root / ".git").exists())
        before = self.inventory()
        for path in self.root.rglob("*"):
            if path.is_file():
                path.chmod(stat.S_IREAD)
        for program, marker in (("verify.py", PASS), ("independent.py", "PASS_FORWARD_COLUMNS:")):
            with self.subTest(program=program):
                result = self.cli(program=program)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(marker, result.stdout)
        self.assertEqual(self.inventory(), before)

    def test_each_source_corruption(self):
        for item in self.inputs:
            path = self.root / item["path"]
            original = path.read_bytes()
            with self.subTest(source=item["path"]):
                try:
                    path.write_bytes(original + b"\n")
                    self.rejected(self.cli(), "source SHA256")
                finally:
                    path.write_bytes(original)

    def test_authentication_precedes_source_execution(self):
        path = self.root / "research/leaf-destination-transport-bound/check2.py"
        source = path.read_text(encoding="utf-8")
        original = "def gen(n, sign=1,"
        self.assertEqual(source.count(original), 1)
        replacement = ("def gen(n=__import__('pathlib').Path('SOURCE_EXECUTED').touch(), "
                       "sign=1,")
        path.write_text(source.replace(original, replacement), encoding="utf-8")
        self.rejected(self.cli(), "source SHA256")
        self.assertFalse((self.root / "SOURCE_EXECUTED").exists())

    def test_typed_receipt(self):
        path = self.package / "RESULT.json"
        original = path.read_bytes()
        for field, value in (("schema_version", True), ("literal_profiles", 23.0)):
            with self.subTest(field=field):
                changed = json.loads(original)
                changed[field] = value
                path.write_text(json.dumps(changed), encoding="utf-8")
                self.rejected(self.cli(), "typed receipt mismatch")
        path.write_bytes(original)

    def test_existing_output_is_preserved(self):
        path = self.package / "RESULT.json"
        original = path.read_bytes()
        self.rejected(self.cli("--output", str(path)), "output already exists")
        self.assertEqual(path.read_bytes(), original)

    def test_fresh_output_matches_receipt(self):
        path = self.root / "fresh.json"
        result = self.cli("--output", str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        canonical = lambda obj: json.dumps(obj, sort_keys=True, separators=(",", ":"))
        self.assertEqual(canonical(json.loads(path.read_text(encoding="utf-8"))),
                         canonical(json.loads((self.package / "RESULT.json").read_text(encoding="utf-8"))))

    def test_unknown_option(self):
        self.rejected(self.cli("--not-an-option"), "unrecognized arguments")


if __name__ == "__main__":
    unittest.main()
