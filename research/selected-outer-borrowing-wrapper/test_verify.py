"""CLI, immutable-source and typed-receipt tests; no network or Git required."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from hashlib import sha1, sha256
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def cli(package=PACKAGE, *arguments, optimized=False):
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(
        [
            sys.executable,
            *(["-O"] if optimized else []),
            "-Werror",
            "-B",
            str(package / "verify.py"),
            "--core-only",
            *arguments,
        ],
        capture_output=True,
        text=True,
        timeout=120,
        env=environment,
        check=False,
    )


class WrapperTests(unittest.TestCase):
    def copied(self):
        temporary = tempfile.TemporaryDirectory(prefix="outer-wrapper-test-")
        self.addCleanup(temporary.cleanup)
        target = Path(temporary.name) / "package"
        shutil.copytree(PACKAGE, target)
        return target

    def require_failure(self, result, message):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(message, result.stderr)
        self.assertNotIn("PASS_OUTER_BORROWING_WRAPPER", result.stdout)

    def test_normal_core(self):
        result = cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("core cases 9 controls 9 no_new_kappa", result.stdout)

    def test_optimized_git_free_read_only_core(self):
        package = self.copied()
        before = {
            str(path.relative_to(package)): sha256(path.read_bytes()).hexdigest()
            for path in package.rglob("*")
            if path.is_file()
        }
        result = cli(package, optimized=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        after = {
            str(path.relative_to(package)): sha256(path.read_bytes()).hexdigest()
            for path in package.rglob("*")
            if path.is_file()
        }
        self.assertEqual(after, before)

    def test_source_corruption_rejects_before_execution(self):
        package = self.copied()
        marker = package / "SHOULD_NOT_EXIST"
        source = package / "vendor/pr2786/padding.py"
        source.write_text(
            source.read_text() + f"\nopen({str(marker)!r}, 'w').write('bad')\n"
        )
        manifest = json.loads((package / "VENDOR.json").read_text())
        # Preserve the declared size so SHA256, not only the size gate, rejects.
        manifest["files"]["padding.py"]["size"] = source.stat().st_size
        (package / "VENDOR.json").write_text(json.dumps(manifest))
        self.require_failure(cli(package), "predecessor SHA256")
        self.assertFalse(marker.exists())

    def test_inner_archive_authentication_is_not_bypassed(self):
        package = self.copied()
        path = package / "vendor/pr2786/predecessor.tar.gz"
        data = path.read_bytes() + b"changed"
        path.write_bytes(data)
        manifest = json.loads((package / "VENDOR.json").read_text())
        pin = manifest["files"][path.name]
        pin.update(
            size=len(data),
            sha256=sha256(data).hexdigest(),
            git_blob=sha1(
                b"blob " + str(len(data)).encode() + b"\0" + data, usedforsecurity=False
            ).hexdigest(),
        )
        (package / "VENDOR.json").write_text(json.dumps(manifest))
        self.require_failure(cli(package), "immutable source archive SHA256")

    def test_undeclared_bytecode_rejects(self):
        package = self.copied()
        cache = package / "vendor/pr2786/__pycache__"
        cache.mkdir()
        (cache / "padding.pyc").write_bytes(b"untrusted cache")
        self.require_failure(
            cli(package, optimized=True), "no undeclared source or bytecode cache"
        )

    def test_preloaded_source_rejects(self):
        code = (
            f"import sys, types; sys.path.insert(0, {str(PACKAGE)!r}); "
            "sys.modules['padding']=types.ModuleType('padding'); "
            "from predecessor import installed; "
            "installed().__enter__()"
        )
        result = subprocess.run(
            [sys.executable, "-B", "-c", code],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.require_failure(result, "no preloaded padding source")

    def test_boolean_receipt_corruption_rejects(self):
        package = self.copied()
        path = package / "RESULT.json"
        expected = json.loads(path.read_text())
        self.assertEqual(expected["cases"][0]["k"], 1)
        expected["cases"][0]["k"] = True
        path.write_text(json.dumps(expected))
        self.require_failure(
            cli(package, optimized=True), "complete typed receipt matches"
        )

    def test_emit_does_not_overwrite(self):
        package = self.copied()
        target = package.parent / "existing.json"
        target.write_text("untouched\n")
        self.require_failure(cli(package, "--emit-to", str(target)), "FileExistsError")
        self.assertEqual(target.read_text(), "untouched\n")

    def test_emit_refuses_package_mutation(self):
        package = self.copied()
        self.require_failure(
            cli(package, "--emit-to", str(package / "new.json")),
            "receipt output must be external",
        )
        self.assertFalse((package / "new.json").exists())


if __name__ == "__main__":
    unittest.main()
