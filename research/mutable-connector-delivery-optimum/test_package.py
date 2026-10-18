#!/usr/bin/env python3
"""Defect-sensitive controls and source-export replay. Apache-2.0."""
import copy
from fractions import Fraction
import hashlib
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
spec = importlib.util.spec_from_file_location("mutable_delivery", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class PackageTests(unittest.TestCase):
    def test_exact_domain_rejects_aliases(self):
        for value in [True, 1.0, float("nan"), "1", 0, -1]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                v.optimum([value], [], [1])
        for args in [([], [], []), ([1, 1], [], [1, 1]), ([1], [], [])]:
            with self.assertRaises(ValueError):
                v.optimum(*args)
        self.assertEqual(v.optimum([Fraction(1, 7)], [], [Fraction(2, 7)])[0], Fraction(6, 7))

    def test_prices_can_favor_nonadjacent_pair(self):
        # A greedy adjacent-pair rule is wrong for nonuniform source prices.
        self.assertEqual(v.optimum([10, 1, 10], [2, 2], [1, 1, 1]), (32, (1, 1, 0)))
        adjacent_best = 48 - (10 + 1 - 2)
        self.assertGreater(adjacent_best, 32)
        self.assertEqual(v.optimum([7] * 3, [15, 15], [3, 4, 3]), (62, (0, 0, 0)))

    def test_output_only_check_misses_adapter_leak(self):
        word = v.construct((0, 1, 0))
        without = [x for x in word if x[0] != "D"]
        # All three delivery checks succeed; only final arbitrary dirt fails.
        with self.assertRaisesRegex(ValueError, "source/connector endpoint"):
            v.replay(without, 3)
        v.replay(word, 3)

    def test_endpoint_neutral_writes_violate_delivery_contract(self):
        word = v.construct((0, 1, 0))
        for illegal in [ [["A", 1], ["A", 1]] + word,
                         word + [["A", 0], ["A", 0]] ]:
            with self.assertRaisesRegex(ValueError, "outside request"):
                v.replay(illegal, 3)
        with self.assertRaisesRegex(ValueError, "matrix alias"):
            v.matrix_gates([1], [0], [0])
        p = v.pilot((0, 1, 0))
        corrupted = copy.deepcopy(p)
        # Removing one source bit from a B query changes an actual delivered value.
        corrupted["gates"][4] = [2, 5]
        with self.assertRaises(ValueError):
            v.check_pilot(corrupted)

    def export(self, root):
        package = root / "research" / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        source_rows = v.load_json(HERE / "SOURCES.json")["files"]
        for row in source_rows:
            if row["usage"] == "input":
                dst = root / row["path"]
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row["path"], dst)
        return package

    def execute(self, package, file="verify.py"):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / file)],
                              cwd=package.parents[1], capture_output=True, text=True, timeout=120)

    def test_read_only_relocated_export(self):
        with tempfile.TemporaryDirectory(prefix="mutable-delivery-readonly-") as tmp:
            root = Path(tmp)
            package = self.export(root)
            files = [p for p in root.rglob("*") if p.is_file()]
            before = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            dirs = [p for p in root.rglob("*") if p.is_dir()] + [root]
            try:
                for p in files:
                    p.chmod(0o444)
                for p in dirs:
                    p.chmod(0o555)
                for checker, marker in [("verify.py", "PASS_MUTABLE_CONNECTOR_DELIVERY_OPTIMUM"),
                                        ("independent.py", "PASS_INDEPENDENT_MUTABLE_DELIVERY")]:
                    result = self.execute(package, checker)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn(marker, result.stdout)
                after = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in root.rglob("*") if p.is_file()}
                self.assertEqual(before, after)
            finally:
                for p in dirs:
                    p.chmod(0o755)
                for p in files:
                    p.chmod(0o644)

    def test_on_disk_corruptions_fail_under_optimized_python(self):
        with tempfile.TemporaryDirectory(prefix="mutable-delivery-controls-") as tmp:
            package = self.export(Path(tmp))
            receipt = package / "RESULT.json"
            original = receipt.read_bytes()
            payload = json.loads(original)
            changes = []
            changed = copy.deepcopy(payload)
            changed["pilots"][2]["candidate_xors"] = 52.0
            changes.append((json.dumps(changed), "receipt drift"))
            changed = copy.deepcopy(payload)
            changed["tariff_cases"] = True
            changes.append((json.dumps(changed), "receipt drift"))
            changed = copy.deepcopy(payload)
            changed["three_output_pilot"]["gates"].pop()
            changes.append((json.dumps(changed), "receipt drift"))
            changes += [('{"status":1,"status":2}', "duplicate JSON key"),
                        ('{"status":NaN}', "non-finite JSON")]
            for text, error in changes:
                with self.subTest(error=error):
                    receipt.write_text(text)
                    result = self.execute(package)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(error, result.stderr)
            receipt.write_bytes(original)
            source = Path(tmp) / "research/mutable-source-persistent-connector/README.md"
            saved = source.read_bytes()
            source.write_bytes(saved + b"\ncorruption\n")
            result = self.execute(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source drift", result.stderr)
            source.unlink()
            result = self.execute(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing source", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
