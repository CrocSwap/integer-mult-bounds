#!/usr/bin/env python3
"""Scoped mathematical and real package-fault controls. Apache-2.0.

Prepared for @ToikY with substantial OpenAI Codex assistance.
"""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("ut4_formal_checker", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def run(path, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(path), *map(str, args)],
                          capture_output=True, text=True, timeout=60)


def export(root):
    package = root / "research" / HERE.name
    shutil.copytree(HERE, package)
    source = "research/bit-three-register-lower-bound/README.md"
    destination = root / source
    destination.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / source, destination)
    return package, destination


class PackageTests(unittest.TestCase):
    def test_rectangular_quotient_rank_inequality(self):
        cases, nonzero = 0, 0
        for n in range(3):
            Xs = list(itertools.product(range(1 << n), repeat=2))
            Ys = list(itertools.product(range(4), repeat=n))
            for X in Xs:
                for Y in Ys:
                    if any(v.multiply(X, Y)):
                        continue
                    Us = [U for U in Xs if not any(v.multiply(U, Y))]
                    Vs = [V for V in Ys if not any(v.multiply(X, V))]
                    for U in Us:
                        for V in Vs:
                            H = v.multiply(U, V)
                            self.assertLessEqual(v.rank(H), n - v.rank(X) - v.rank(Y))
                            cases += 1
                            nonzero += bool(v.rank(H))
        self.assertGreater(cases, 100)
        self.assertGreater(nonzero, 0)

    def test_binary_sharp_relaxation_and_field_boundary(self):
        for w in range(1, 65):
            for r in (w, w + 2):
                result = v.middle_relaxation(w, r)
                self.assertEqual(result["middle_calls"], 3 * w + (w == 1))
                self.assertEqual(result["rank_H"], w)
                self.assertEqual(result["rank_X"], w)
                self.assertEqual(result["rank_Y"], w)
        X, Y, U, V = [1, 1, 1], [1, 1, 1], [1, 2, 0], [1, 0, 2]
        dot = lambda a, b: sum(x * y for x, y in zip(a, b)) % 3
        self.assertEqual((dot(X, Y), dot(U, Y), dot(X, V), dot(U, V)), (0, 0, 0, 1))

    def test_actual_trial_and_nonfaithful_dirty_leak(self):
        controls = v.semantic_controls()
        trial = controls["twelve_call_trial"]["word"]
        formal = v.paid_product(trial, 2)
        self.assertEqual(v.proof_image(formal, 2), v.proof_image(v.target(2, 2), 2))
        self.assertNotEqual(v.proof_image(formal, 2, True), v.proof_image(v.target(2, 2), 2, True))
        self.assertNotEqual(formal, v.target(2, 2))
        self.assertEqual(controls["common_kernel_changed_columns"], 64)

    def test_alphabet_domain_and_order_failures(self):
        for word, r in (([("z", 1, 1)], 2), ([("a", 0, 1)], 2),
                         ([("a", 4, 1)], 2), ([("a", True, 1)], 2), ([], 0)):
            with self.assertRaises(ValueError):
                v.paid_product(word, r)
        self.assertNotEqual(v.paid_product([("a", 1, 1), ("b", 1, 1)], 1),
                            v.paid_product([("b", 1, 1), ("a", 1, 1)], 1))
        for w in (0, 3):
            with self.assertRaises(ValueError):
                v.target(2, w)

    def test_real_source_corruption_rejects(self):
        with tempfile.TemporaryDirectory(prefix="ut4-source-") as raw:
            package, source = export(Path(raw))
            source.write_bytes(source.read_bytes() + b"\nchanged\n")
            result = run(package / "verify.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("pinned model source changed", result.stderr)

    def test_receipt_corruption_and_occupied_output_reject(self):
        with tempfile.TemporaryDirectory(prefix="ut4-receipt-") as raw:
            package, _ = export(Path(raw))
            receipt = json.loads((package / "CERTIFICATE.json").read_text())
            receipt["expanded_two_factor_pairs"] -= 1
            (package / "CERTIFICATE.json").write_text(json.dumps(receipt))
            result = run(package / "verify.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("certificate differs", result.stderr)
            occupied = Path(raw) / "occupied.json"
            occupied.write_text("keep")
            result = run(package / "verify.py", "--write-receipt", occupied)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(occupied.read_text(), "keep")

    def test_independent_receipt_corruption_rejects(self):
        with tempfile.TemporaryDirectory(prefix="ut4-independent-") as raw:
            path = Path(raw) / "bad.json"
            receipt = json.loads((HERE / "INDEPENDENT.json").read_text())
            receipt["fixture_count"] -= 1
            path.write_text(json.dumps(receipt))
            result = run(HERE / "independent.py", "--check", path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("independent receipt differs", result.stderr)

    def test_readonly_optimized_relocation(self):
        with tempfile.TemporaryDirectory(prefix="ut4 relocated ") as raw:
            root = Path(raw)
            package, _ = export(root)
            before = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in root.rglob("*") if p.is_file()}
            for path in root.rglob("*"):
                if path.is_file():
                    path.chmod(0o444)
            for path in sorted((p for p in root.rglob("*") if p.is_dir()), reverse=True):
                path.chmod(0o555)
            root.chmod(0o555)
            try:
                self.assertEqual(run(package / "verify.py").returncode, 0)
                independent = run(package / "independent.py", "--check", package / "INDEPENDENT.json")
                self.assertEqual(independent.returncode, 0, independent.stderr)
                after = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in root.rglob("*") if p.is_file()}
                self.assertEqual(before, after)
            finally:
                root.chmod(0o755)
                for path in root.rglob("*"):
                    path.chmod(0o755 if path.is_dir() else 0o644)


if __name__ == "__main__":
    unittest.main(verbosity=2)
