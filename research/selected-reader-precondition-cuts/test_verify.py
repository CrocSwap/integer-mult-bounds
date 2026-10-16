#!/usr/bin/env python3
"""Behavioral and semantic failure tests for the fixed cut certificate.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import ast
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cut_verifier_under_test", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


@contextmanager
def exported():
    parent = os.environ.get("RESEARCH_CUT_TEST_SCRATCH")
    if parent:
        Path(parent).mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="selected-cut-test-", dir=parent) as name:
        root = Path(name)
        package = root / "research/selected-reader-precondition-cuts"
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        archive = root / v.ARCHIVE
        archive.parent.mkdir(parents=True)
        shutil.copyfile(v.ROOT / v.ARCHIVE, archive)
        try:
            yield root, package
        finally:
            # Only the test-owned export is made writable for TemporaryDirectory.
            for path in root.rglob("*"):
                path.chmod(0o700 if path.is_dir() else 0o600)
            root.chmod(0o700)
    if Path(name).exists():
        raise RuntimeError("test export not removed")


def invoke(package, *args):
    return subprocess.run([sys.executable, "-I", "-B", "-O", str(package / "verify.py"), *args],
                          cwd=package.parents[1], text=True, capture_output=True, timeout=120)


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, previous = v.load()
        gates, _ = previous.typed_segment(cls.data)
        cls.rows = v.reconstruct(gates)
        cls.prefix = [e[1] for e in cls.data["LOCAL-PROGRAMS.json.gz"]["forward"][:7401]
                      if e[0] == "scalar"]

    def test_actual_write_guard_and_guard_removal(self):
        bad = deepcopy(self.prefix)
        index = next(i for i, g in enumerate(bad) if g[0] == "add" and g[2][1] != 92)
        bad[index][1][1] = 92
        with self.assertRaisesRegex(ValueError, "reader-visible prefix write"):
            v.invisible_writes(self.rows, bad)
        tree = ast.parse((HERE / "verify.py").read_text())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "invisible_writes")
        function.body = [ast.Pass()]
        isolated = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
        namespace = dict(v.__dict__)
        exec(compile(isolated, "<removed write-subspace guard>", "exec"), namespace)
        with self.assertRaisesRegex(ValueError, "mutation accepted"):
            v.expect_reject(lambda: namespace["invisible_writes"](self.rows, bad), "reader-visible prefix write")

    def test_equivalent_prefix_and_genuine_semantic_controls(self):
        result = v.controls(self.rows, self.prefix)
        self.assertEqual(result["rejected_semantic_faults"], 6)
        self.assertTrue(result["equivalent_prefix_sign_and_order"])

    def test_complete_receipt_missing_and_typed_corruption(self):
        with exported() as (_, package):
            receipt = package / "RESULT.json"
            saved = receipt.read_bytes()
            content = json.loads(saved)
            content["excluded_cut_cycle_pairs"] = True
            receipt.write_text(json.dumps(content, sort_keys=True, indent=2) + "\n")
            bad = invoke(package)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("complete committed receipt mismatch", bad.stderr)
            self.assertEqual(json.loads(receipt.read_text())["excluded_cut_cycle_pairs"], True)
            receipt.unlink()
            absent = invoke(package)
            self.assertNotEqual(absent.returncode, 0)
            self.assertIn("FileNotFoundError", absent.stderr)
            self.assertFalse(receipt.exists())

    def test_corrupted_source_rejected_before_executable_import(self):
        with exported() as (_, package):
            borrowed = package / "inputs/PR2491-verify.py"
            borrowed.write_text("raise RuntimeError('EXECUTED_CORRUPTED_SOURCE')\n")
            result = invoke(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("immutable predecessor bytes", result.stderr)
            self.assertNotIn("EXECUTED_CORRUPTED_SOURCE", result.stderr)
        with exported() as (root, package):
            archive = root / v.ARCHIVE
            archive.write_bytes(archive.read_bytes() + b"changed")
            result = invoke(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("immutable selected archive", result.stderr)

    def test_git_free_read_only_and_exclusive_regeneration(self):
        with exported() as (root, package):
            paths = sorted(p for p in root.rglob("*") if p.is_file())
            before = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
            for p in paths:
                p.chmod(0o444)
            for p in sorted((p for p in root.rglob("*") if p.is_dir()), reverse=True):
                p.chmod(0o555)
            root.chmod(0o555)
            result = invoke(package)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_SELECTED_READER_PRECONDITION_CUTS", result.stdout)
            after = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            self.assertFalse((root / ".git").exists())
        with exported() as (_, package):
            result = invoke(package, "--write-result")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FileExistsError", result.stderr)
            receipt = package / "RESULT.json"
            saved = receipt.read_bytes()
            receipt.unlink()
            result = invoke(package, "--write-result")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(saved, receipt.read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
