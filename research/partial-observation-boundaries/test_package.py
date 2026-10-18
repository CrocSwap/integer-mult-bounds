"""Integrity and portable-replay tests, using only isolated temporary copies.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


@contextmanager
def export():
    with tempfile.TemporaryDirectory(prefix="partial-observation-test-") as name:
        root = Path(name)
        package = root / "research" / PACKAGE.name
        shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
        for item in json.loads((PACKAGE / "SOURCES.json").read_text())["files"]:
            if item["usage"] == "input":
                target = root / item["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / item["path"], target)
        yield root, package


def run(package, *args, cwd=None):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"), *map(str, args)],
                          cwd=cwd, capture_output=True, text=True, timeout=120, check=False)


def hashes(root):
    return {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class PackageIntegrity(unittest.TestCase):
    def test_source_corruption_rejects(self):
        with export() as (root, package):
            item = next(x for x in json.loads((package / "SOURCES.json").read_text())["files"] if x["usage"] == "input")
            target = root / item["path"]
            target.write_bytes(target.read_bytes() + b"\ncorrupt source control\n")
            result = run(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source drift", result.stderr)

    def test_receipt_corruption_rejects(self):
        with export() as (_, package):
            target = package / "RESULT.json"
            data = json.loads(target.read_text())
            data["partial_observation_improvements"] += 1
            target.write_text(json.dumps(data))
            result = run(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt mismatch", result.stderr)

    def test_existing_result_is_preserved(self):
        with export() as (_, package):
            target = package / "RESULT.json"
            before = target.read_bytes()
            result = run(package, "--write-result", target)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to overwrite", result.stderr)
            self.assertEqual(target.read_bytes(), before)

    def test_readonly_relocation_from_empty_cwd(self):
        with export() as (root, package):
            empty = root / "empty"
            empty.mkdir()
            before = hashes(root)
            paths = list(root.rglob("*"))
            try:
                for path in paths:
                    path.chmod(0o555 if path.is_dir() else 0o444)
                result = run(package, cwd=empty)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("PASS_PARTIAL_OBSERVATION_BOUNDARIES", result.stdout)
                self.assertEqual(hashes(root), before)
            finally:
                for path in paths:
                    path.chmod(0o755 if path.is_dir() else 0o644)


if __name__ == "__main__":
    unittest.main()
