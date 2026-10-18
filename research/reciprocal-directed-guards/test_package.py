#!/usr/bin/env python3
"""Mathematical and actual package-fault controls. Apache-2.0.

Prepared for @ToikY with substantial OpenAI Codex assistance.
"""
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("reciprocal_rational_checker", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def run(path, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(path), *map(str, args)],
                          capture_output=True, text=True, timeout=90)


class PackageTests(unittest.TestCase):
    def test_nondyadic_cell_interiors(self):
        count = 0
        for p in range(1, 13):
            T = max(6, p + 5)
            scale = 1 << T
            for offset in (0, 1, scale // 3, scale // 2, scale - 1):
                left = F(scale + offset, scale)
                middle = left + F(2, 3 * scale)
                for guards in (3, 5):
                    x, trace = v.reciprocal(middle, p, guards)
                    left_x, left_trace = v.reciprocal(left, p, guards)
                    self.assertEqual((x, trace), (left_x, left_trace))
                    self.assertLess(abs(1 - middle * x), F(1, 1 << (p + 1)))
                    count += 1
        self.assertEqual(count, 120)

    def test_general_quantified_step_fixtures(self):
        count = 0
        for m in range(1, 10):
            for next_m in range(m + 1, 2 * m + 1):
                for j in range(37):
                    c = 1 + F(j, 37)
                    for signed in (-1, 0, 1):
                        e = F(signed, 1 << (m + 1))
                        x = (1 - e) / c
                        out = v.step(c, x, next_m + 3)[2]
                        self.assertLess(abs(1 - c * out), F(1, 1 << (next_m + 1)))
                        count += 1
        self.assertEqual(count, 4995)

    def test_signed_identity_and_lower_guard_failures(self):
        self.assertEqual(v.symbolic_checks()["three_guard_lower_slack"], "1/32")
        rows = v.sharp_invariant_witness()["steps"]
        self.assertEqual([r["passes"] for r in rows], [False, False, False, True])
        for row in rows[:3]:
            self.assertNotEqual(row["x"], row["actual_warmup"])
        c, x, t = F(4, 3), F(5, 8), 6
        ct, u, out = v.step(c, x, t)
        eta1, eta2 = u - ct * x, out - x * (2 - u)
        wrong = (1 - c * x) ** 2 + c * (c - ct) * x * x + c * x * eta1 - c * eta2
        self.assertNotEqual(1 - c * out, wrong)

    def test_missing_warmup_stale_prefix_and_invalid_domain(self):
        self.assertEqual(v.mathematical_controls()["stale_prefix"]["p"], 12)
        for c, p, g in ((F(1, 2), 2, 3), (F(2), 2, 3), (F(1), 0, 3),
                         (F(1), True, 3), (F(1), 2, -1)):
            with self.assertRaises(ValueError):
                v.reciprocal(c, p, g)

    def test_source_corruption_rejects(self):
        with tempfile.TemporaryDirectory(prefix="reciprocal-source-") as raw:
            root = Path(raw)
            package = root / "research" / HERE.name
            shutil.copytree(HERE, package)
            source = root / v.SOURCE
            source.parent.mkdir(parents=True)
            source.write_bytes((ROOT / v.SOURCE).read_bytes() + b"\n% changed\n")
            result = run(package / "verify.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("pinned Section09 source bytes changed", result.stderr)

    def test_certificate_corruption_and_occupied_output_reject(self):
        with tempfile.TemporaryDirectory(prefix="reciprocal-receipt-") as raw:
            root = Path(raw)
            package = root / "research" / HERE.name
            shutil.copytree(HERE, package)
            source = root / v.SOURCE
            source.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / v.SOURCE, source)
            expected = json.loads((package / "CERTIFICATE.json").read_text())
            expected["census"]["cells"] -= 1
            (package / "CERTIFICATE.json").write_text(json.dumps(expected))
            result = run(package / "verify.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("certificate content changed", result.stderr)
            occupied = root / "occupied.json"
            occupied.write_text("keep")
            result = run(package / "verify.py", "--write-receipt", occupied)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(occupied.read_text(), "keep")

    def test_independent_receipt_corruption_rejects(self):
        with tempfile.TemporaryDirectory(prefix="reciprocal-independent-") as raw:
            path = Path(raw) / "bad.json"
            receipt = json.loads((HERE / "INDEPENDENT.json").read_text())
            receipt["endpoint_checks"] -= 1
            path.write_text(json.dumps(receipt))
            result = run(HERE / "independent.py", "--check", path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("independent receipt differs", result.stderr)

    def test_readonly_optimized_relocation(self):
        with tempfile.TemporaryDirectory(prefix="reciprocal relocated ") as raw:
            root = Path(raw)
            package = root / "research" / HERE.name
            shutil.copytree(HERE, package)
            source = root / v.SOURCE
            source.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / v.SOURCE, source)
            files = [p for p in root.rglob("*") if p.is_file()]
            before = {str(p.relative_to(root)): p.read_bytes() for p in files}
            for path in files:
                path.chmod(0o444)
            for path in sorted((p for p in root.rglob("*") if p.is_dir()), reverse=True):
                path.chmod(0o555)
            root.chmod(0o555)
            try:
                for name in ("verify.py", "independent.py"):
                    result = run(package / name)
                    self.assertEqual(result.returncode, 0, result.stderr)
                after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
                self.assertEqual(before, after)
            finally:
                root.chmod(0o755)
                for path in root.rglob("*"):
                    path.chmod(0o755 if path.is_dir() else 0o644)


if __name__ == "__main__":
    unittest.main(verbosity=2)
