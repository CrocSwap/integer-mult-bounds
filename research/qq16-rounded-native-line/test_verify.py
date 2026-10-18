"""Exercise the published CLI and its artifact failure paths. Apache-2.0."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class ArtifactTests(unittest.TestCase):
    def invoke(self, package, *args):
        return subprocess.run(
            [
                sys.executable,
                "-Werror",
                "-I",
                "-O",
                "-B",
                str(package / "verify.py"),
                *args,
            ],
            cwd=package,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

    def copy_package(self, directory):
        target = Path(directory) / "export"
        shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__"))
        return target

    def test_git_free_read_only_export(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.copy_package(directory)
            paths = list(package.rglob("*"))
            before = {
                p.relative_to(package): p.read_bytes() for p in paths if p.is_file()
            }
            for path in paths:
                if path.is_file():
                    path.chmod(0o444)
            try:
                run = self.invoke(package)
                self.assertEqual(run.returncode, 0, run.stderr)
                prefix = "PASS_QQ16_ROUNDED_NATIVE_LINE "
                self.assertTrue(run.stdout.startswith(prefix), run.stdout)
                record = json.loads(run.stdout[len(prefix) :])
                self.assertEqual(record["basis_columns"], 1240)
                self.assertEqual(record["rounded_tensor_cases"], 72)
                self.assertEqual(record["relative_tensor_cases"], 72)
                self.assertEqual(record["relative_cases_with_nonzero_error"], 72)
                self.assertEqual(
                    record["source"],
                    {
                        "events": 3823,
                        "signed_lines": 336,
                        "positive": 224,
                        "negative": 112,
                    },
                )
                after = {
                    p.relative_to(package): p.read_bytes()
                    for p in package.rglob("*")
                    if p.is_file()
                }
                self.assertEqual(after, before)
            finally:
                for path in paths:
                    if path.is_file():
                        path.chmod(0o644)

    def test_source_corruption_rejects_before_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.copy_package(directory)
            for name in ("WORD.json", "LINE-PROOF.md", "DEFECT-PROOF.md"):
                with self.subTest(name=name):
                    path = package / "source" / name
                    original = path.read_bytes()
                    path.write_bytes(original + b" ")
                    run = self.invoke(package)
                    self.assertNotEqual(run.returncode, 0)
                    self.assertIn("source SHA256", run.stderr)
                    self.assertNotIn("PASS_", run.stdout)
                    path.write_bytes(original)

    def test_receipt_types_are_not_coerced(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.copy_package(directory)
            path = package / "RESULT.json"
            record = json.loads(path.read_text())
            record["guard_bits"] = 22.0
            path.write_text(json.dumps(record))
            run = self.invoke(package)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("complete typed receipt", run.stderr)

    def test_overwrite_refused_and_cli_rejects_unknown_argument(self):
        with tempfile.TemporaryDirectory() as directory:
            package = self.copy_package(directory)
            original = (package / "RESULT.json").read_bytes()
            run = self.invoke(package, "--write-result")
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("FileExistsError", run.stderr)
            self.assertEqual((package / "RESULT.json").read_bytes(), original)
            invalid = self.invoke(package, "--unknown")
            self.assertEqual(invalid.returncode, 2)
            self.assertIn("unrecognized arguments", invalid.stderr)


if __name__ == "__main__":
    # No environment-dependent assertion disabling is used by the subprocesses.
    os.environ.pop("PYTHONOPTIMIZE", None)
    unittest.main()
