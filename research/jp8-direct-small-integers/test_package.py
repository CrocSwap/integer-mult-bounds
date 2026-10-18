#!/usr/bin/env python3
"""Mathematical and packaging failure controls; Apache-2.0.

Michał Ciemięga (@zewelor), with substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import controls
import verify as v


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.source_check()
        cls.baseline = staticmethod(v.load_reference())

    def test_dense_contract_controls(self):
        result = controls.run(self.baseline)
        self.assertEqual(len(result["rejections"]), 13)

    def test_integer_rows_against_fraction(self):
        rng = random.Random(29)
        for _ in range(1000):
            a = v.row({i: rng.randrange(-32, 33) for i in range(4)}, rng.randrange(9))
            b = v.row({i: rng.randrange(-32, 33) for i in range(4)}, rng.randrange(9))
            q = Q(rng.randrange(-32, 33), 1 << rng.randrange(9))
            for actual, expected in (
                (v.add(a, b), {i: Q(a[1].get(i, 0), 1 << a[0])+Q(b[1].get(i, 0), 1 << b[0]) for i in range(4)}),
                (v.add(a, b, -1), {i: Q(a[1].get(i, 0), 1 << a[0])-Q(b[1].get(i, 0), 1 << b[0]) for i in range(4)}),
                (v.scale(a, q), {i: q*Q(a[1].get(i, 0), 1 << a[0]) for i in range(4)}),
            ):
                self.assertEqual({i: Q(n, 1 << actual[0]) for i, n in actual[1].items()},
                                 {i: n for i, n in expected.items() if n})

    def test_exact_replacement_domain(self):
        for n in range(-25, 26):
            if n == 0:
                continue
            for d in (1, 2, 4, 8, 16):
                op = ["add", ["T", 0], ["S", 0], n, d]
                original, candidate = self.baseline(op), v.lower(op, self.baseline)
                self.assertEqual(candidate != original, abs(Q(n, d)) in (2, 3))
                self.assertLessEqual(len(candidate), len(original))
        for op in (["clear", ["T", 0]], ["copy", ["T", 0], ["S", 0]],
                   ["scale", ["T", 0], -1, 8], ["scale", ["T", 0], 8, 1]):
            self.assertEqual(v.lower(op, self.baseline), self.baseline(op))

    def test_source_binding_and_semantic_recompression(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in v.FILES:
                dst = root / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(v.ROOT / name, dst)
            compressed = root / (v.PROVIDER + "LOCAL-PROGRAMS.json.gz")
            payload = gzip.decompress(compressed.read_bytes())
            compressed.write_bytes(gzip.compress(payload, compresslevel=1, mtime=29))
            v.source_check(root)  # Changed container bytes preserve all input fields.
            bad = root / v.REFERENCE
            bad.write_bytes(bad.read_bytes() + b"\n# changed\n")
            with self.assertRaisesRegex(ValueError, "source pin mismatch"):
                v.source_check(root)

    def test_optimized_minimal_relocation_and_receipt_corruption(self):
        with tempfile.TemporaryDirectory(prefix="jp8 direct test ") as directory:
            root = Path(directory)
            for name in v.FILES:
                dst = root / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(v.ROOT / name, dst)
            package = root / "research/jp8-direct-small-integers"
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
            run = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=90)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("PASS_JP8_DIRECT_SMALL_INTEGERS", run.stdout)
            receipt = package / "EXPECTED.json"
            value = json.loads(receipt.read_text(encoding="utf-8"))
            value["programs"]["forward"]["changed_macros"] = 1424.0
            receipt.write_text(json.dumps(value), encoding="utf-8")
            run = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=90)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("expected receipt mismatch", run.stderr)

    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "keep.json"
            output.write_bytes(b"keep\n")
            run = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"),
                                  "--write", str(output)], capture_output=True, text=True, timeout=10)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("output already exists", run.stderr)
            self.assertEqual(output.read_bytes(), b"keep\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
