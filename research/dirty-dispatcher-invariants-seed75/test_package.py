#!/usr/bin/env python3
"""Source/receipt rejection and relocation checks. Hanson Sun / Codex, Apache-2.0."""
import contextlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("dispatcher_verifier", P/"verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


@contextlib.contextmanager
def relocated():
    with tempfile.TemporaryDirectory(prefix="dispatcher package with spaces ") as temp:
        root = Path(temp)
        package = root/"research"/P.name
        shutil.copytree(P, package, ignore=shutil.ignore_patterns("__pycache__", "*.olean", "*.ilean"))
        for row in json.loads((P/"SOURCES.json").read_text())["files"]:
            if row["usage"] == "input":
                target = root/row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(v.REPO/row["path"], target)
        try:
            yield root, package
        finally:
            # Permit cleanup after the read-only relocation case.
            for path in root.rglob("*"):
                path.chmod(0o755 if path.is_dir() else 0o644)


def replay(package, *extra):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(package/"verify.py"),
                           "--python-only", *map(str, extra)], cwd=package.parent,
                          capture_output=True, text=True, timeout=60)


class PackageTests(unittest.TestCase):
    def test_actual_source_corruption(self):
        with relocated() as (root, package):
            source = root/v.SOURCE
            source.write_bytes(source.read_bytes()+b"\n# corrupt source\n")
            result = replay(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source SHA256", result.stderr)

    def test_actual_receipt_corruption(self):
        with relocated() as (_, package):
            path = package/"EXPECTED.json"
            receipt = json.loads(path.read_text())
            receipt["distinct_signed_traces"] += 1
            path.write_text(json.dumps(receipt))
            result = replay(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Python receipt mismatch", result.stderr)

    def test_formal_source_binding(self):
        with relocated() as (_, package):
            path = package/"Dispatcher.lean"
            path.write_text(path.read_text().replace("g.src", "g.dst", 1))
            result = replay(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Python receipt mismatch", result.stderr)

    def test_readonly_relocation(self):
        with relocated() as (root, package):
            paths = [p for p in root.rglob("*") if p.is_file()]
            before = {p.relative_to(root).as_posix(): v.sha(p.read_bytes()) for p in paths}
            for path in root.rglob("*"):
                path.chmod(0o555 if path.is_dir() else 0o444)
            result = replay(package)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            self.assertIn("Lean=NOT_RUN", result.stdout)
            after = {p.relative_to(root).as_posix(): v.sha(p.read_bytes())
                     for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_regeneration_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)/"receipt.json"
            result = replay(P, "--write", target)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            self.assertEqual(target.read_bytes(), (P/"EXPECTED.json").read_bytes())
            before = target.read_bytes()
            refused = replay(P, "--write", target)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("refuse receipt overwrite", refused.stderr)
            self.assertEqual(before, target.read_bytes())

    def test_theorem_inventory_and_forbidden_axioms(self):
        for output in ("", "'a' depends on axioms: [sorryAx]",
                       "'a' depends on axioms: [Lean.ofReduceBool]",
                       "'a' does not depend on any axioms\n'a' does not depend on any axioms",
                       "'different' does not depend on any axioms"):
            with self.subTest(output=output), self.assertRaises(ValueError):
                v.audit_axioms(output, ["a"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
