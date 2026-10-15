#!/usr/bin/env python3
"""Behavioral and rejection controls for the conditional stock checker.

Nick Petalas. Apache-2.0.
"""
import copy
import io
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
V = runpy.run_path(str(PACKAGE / "verify.py"))


class StockTests(unittest.TestCase):
    def test_literal_depths(self):
        fixtures = {0: 0, 1: 0, 63: 0, 64: 1, 95: 1, 96: 1, 127: 1,
                    128: 2, 191: 2, 192: 2, 256: 3, 384: 3}
        self.assertEqual({n: V["forward_depth"](n) for n in fixtures}, fixtures)

    def test_contraction_and_terminal_controls(self):
        V["depth_certificate"](64, 42, 28, 17, 64)
        self.assertEqual(V["forward_depth"](128), 2)
        for args, message in (((64, 42, 28, 18, 64), "strict contraction"),
                              ((64, 43, 28, 17, 64), "strict contraction"),
                              ((64, 42, 28, 17, 1), "terminal slack"),
                              ((64, 42, 65, 17, 64), "bounded contraction")):
            with self.subTest(args=args), self.assertRaisesRegex(V["Rejected"], message):
                V["depth_certificate"](*args)

    def test_capacity_and_wrong_producer(self):
        self.assertEqual(V["forward_depth"](64), 1)
        for n, m, r in ((-1, 64, 42), (1 << 4097, 64, 42),
                        (73, 73, 48), (True, 64, 42)):
            with self.subTest(n=n), self.assertRaises(V["Rejected"]):
                V["forward_depth"](n, m, r)

    def test_all_child_oracle_must_include_largest_rank(self):
        with self.assertRaisesRegex(V["Rejected"], "selected child domain"):
            V["finite_checks"]((1, 2, 3, 4))
        self.assertEqual(V["forward_depth"](256), 3)

    def test_floor_is_required(self):
        # The weakened ceil recurrence can loop forever at 84. This is a
        # countermodel to changing the premise, not a selected compiler bug.
        self.assertEqual(V["forward_depth"](84), 1)
        self.assertEqual(42 * ((84 + 63) // 64), 84)
        self.assertEqual(42 * (84 // 64), 42)

    def test_archive_member_corruption_and_type(self):
        data = (ROOT / V["ARCHIVE"]).read_bytes()
        tree = V["assembler"](data)
        self.assertEqual(V["ast"].literal_eval(V["assignment"](tree, "BIT_BLOB")),
                         "e293ddc557742637f9f679f083a1a282d87b1b13")
        for symlink in (False, True):
            stream = io.BytesIO()
            with tarfile.open(fileobj=stream, mode="w:gz") as archive:
                member = tarfile.TarInfo("code/assemble.py")
                if symlink:
                    member.type = tarfile.SYMTYPE
                    member.linkname = "elsewhere"
                    archive.addfile(member)
                else:
                    member.size = 1
                    archive.addfile(member, io.BytesIO(b"x"))
            with self.subTest(symlink=symlink), self.assertRaises(V["Rejected"]):
                V["assembler"](stream.getvalue())

    def test_cutoff_control(self):
        inputs = V["read_inputs"]()
        assembly = json.loads(inputs[V["ASSEMBLY"]])
        self.assertEqual(V["first_cutoff"](assembly, 6748)["ell"], 16)
        with self.assertRaisesRegex(V["Rejected"], "stock coefficient"):
            V["first_cutoff"](assembly, 6747)
        bad = copy.deepcopy(assembly)
        bad["bootstrap"][0]["cutoff_log2"] = "3"
        with self.assertRaisesRegex(V["Rejected"], "stock-fit guard"):
            V["first_cutoff"](bad, 6748)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.package = self.root / "research" / PACKAGE.name
        self.package.mkdir(parents=True)
        for name in ("verify.py", "SOURCES.json", "RESULT.json"):
            shutil.copyfile(PACKAGE / name, self.package / name)
        pins = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]
        self.inputs = [pin["path"] for pin in pins if pin["usage"] == "input"]
        for name in self.inputs:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def cli(self):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package / "verify.py")],
                              cwd=self.root, capture_output=True, text=True, encoding="utf-8",
                              timeout=120, check=False)

    def test_optimized_public_cli(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout,
                         "PASS_SELECTED_BIT_CEILING_FREE_STOCK sigma=6748 predecessor=8194 "
                         "ratio=14/17 widths=100001 ell=16 no_new_kappa\n")
        self.assertEqual(result.stderr, "")

    def test_every_live_source_mutation_rejects(self):
        for name in self.inputs:
            path = self.root / name
            original = path.read_bytes()
            path.write_bytes(original + b"\n")
            try:
                result = self.cli()
                with self.subTest(source=name):
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("source SHA256: " + name, result.stderr)
                    self.assertEqual(result.stdout, "")
            finally:
                path.write_bytes(original)

    def test_required_receipt_is_read_only(self):
        path = self.package / "RESULT.json"
        original = path.read_bytes()
        altered = json.loads(original)
        altered["sigma"] = 6747
        path.write_text(json.dumps(altered), encoding="utf-8")
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical RESULT.json mismatch", result.stderr)
        self.assertEqual(json.loads(path.read_bytes())["sigma"], 6747)
        path.unlink()
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FileNotFoundError", result.stderr)
        self.assertFalse(path.exists())
        path.write_bytes(original)
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("sigma=6748", result.stdout)


if __name__ == "__main__":
    unittest.main()
