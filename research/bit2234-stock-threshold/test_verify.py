#!/usr/bin/env python3
"""Independent finite oracles and rejection tests; no predecessor execution."""
from array import array
import importlib.util
import json
from math import lcm
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("stock_threshold_verifier", PACKAGE / "verify.py")
verify = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = verify
SPEC.loader.exec_module(verify)


def all_child_depths(limit):
    """Bottom-up maximum over every rank 1..42, independently of max-rank descent.

    All n in [64*f, 64*f+63] have the same child list. Filling one such
    block at a time makes the exhaustive oracle small enough for CI.
    """
    result = array("H", [0]) * (limit + 1)
    for first in range(64, limit + 1, 64):
        f = first // 64
        value = 1 + max(result[rank * f] for rank in range(1, 43))
        stop = min(first + 64, limit + 1)
        result[first:stop] = array("H", [value]) * (stop - first)
    return result


def cli(package, optimized):
    command = [sys.executable, "-I", "-B"]
    if optimized:
        command.append("-O")
    command.append(str(package / "verify.py"))
    return subprocess.run(command, cwd=package.parent, capture_output=True,
                          text=True, timeout=60, check=False)


def replace_threshold(value):
    """Change the claimed first universal width without depending on JSON keys."""
    if type(value) is int and value == 311311:
        return 311310, 1
    if value == "311311":
        return "311310", 1
    if isinstance(value, list):
        pairs = [replace_threshold(item) for item in value]
        return [item for item, _ in pairs], sum(count for _, count in pairs)
    if isinstance(value, dict):
        pairs = {key: replace_threshold(item) for key, item in value.items()}
        return {key: item for key, (item, _) in pairs.items()}, sum(
            count for _, count in pairs.values())
    return value, 0


class StockThresholdTests(unittest.TestCase):
    def test_all_child_depth_oracle(self):
        oracle = all_child_depths(10000)
        for width, expected in enumerate(oracle):
            self.assertEqual(verify.depth(width), expected, width)
        self.assertEqual(oracle[63], 0)
        self.assertEqual(oracle[64], 1)
        self.assertEqual(oracle[127], 1)
        self.assertEqual(oracle[128], 2)

    def test_inverse_thresholds_against_forward_oracle(self):
        limit = 2 ** 20
        oracle = all_child_depths(2 * limit)
        expected = []
        previous = 0
        for width in range(64, len(oracle), 64):
            if oracle[width] > previous:
                expected.append(width)
                previous = oracle[width]
                if width > limit:
                    break
        actual = verify.thresholds(limit)
        self.assertEqual(actual, expected)
        self.assertGreater(expected[-1], limit)
        for level, boundary in enumerate(expected, 1):
            self.assertEqual(oracle[boundary - 1], level - 1)
            self.assertEqual(oracle[boundary], level)
        self.assertEqual(expected[18:23],
                         [265984, 405312, 617664, 941248, 1434304])

    def test_exact_atom_ceilings(self):
        cases = [(1, 1), (2, 2), (311310, 2), (2 ** 20, 2),
                 (2 ** 588, 2), (2 ** 589, 3),
                 (2 ** 10000 - 1, 2 ** 17),
                 (2 ** 10000, 2 ** 17),
                 (2 ** 10000 + 1, 2 ** 17 + 1)]
        for width, expected in cases:
            self.assertEqual(verify.atom_width(width), expected)
            self.assertLess((expected - 1) ** 10000, width ** 17)
            self.assertLessEqual(width ** 17, expected ** 10000)

    def test_strict_fit_and_rounding_controls(self):
        width = 311310
        self.assertEqual(verify.depth(width), 19)
        self.assertEqual(verify.guard(width), 155655)
        self.assertEqual(verify.guard(width + 1), 155655)
        self.assertEqual(2 * verify.guard(width), width)
        self.assertFalse(2 * verify.guard(width) < width)
        self.assertTrue(2 * verify.guard(width) <= width)  # Incorrect weak fit.
        self.assertTrue(2 * verify.guard(width + 1) < width + 1)
        # Flooring the atom width, or omitting the high-lift contribution,
        # removes 4096*19 digits. It incorrectly announces a fit here.
        self.assertEqual(verify.guard(width, w=1), 77831)
        self.assertTrue(2 * verify.guard(width, w=1) < width)
        # The actual logarithm is strictly between 155654 and 155655;
        # replacing its ceiling with its floor also gives a false fit.
        self.assertTrue(2 * (verify.guard(width) - 1) < width)

    def test_finite_guard_intervals(self):
        first = verify.thresholds(2 ** 20)
        last_failure = 0
        for level, (lo, end) in enumerate(zip(first, first[1:]), 1):
            hi = min(end - 1, 2 ** 20 - 1)
            if lo > hi:
                break
            # Fraction-free rational ceiling, independent of guard().
            stock = (80 * 8192 * level + 29 * level + 79) // 80
            self.assertEqual(verify.guard(lo), stock)
            self.assertEqual(verify.guard(hi), stock)
            failing = min(hi, 2 * stock)
            if failing >= lo:
                last_failure = max(last_failure, failing)
        self.assertEqual(last_failure, 311310)

    def test_prime_and_actual_stock_sharpness(self):
        q = 213 * 2 ** 80 + 1
        self.assertEqual(q, 257501199577916014212415489)
        self.assertEqual(pow(7, (q - 1) // 2, q), q - 1)
        self.assertGreater((2 ** 80 + 1) ** 2, q)
        m = lcm(28416, 28425)
        self.assertEqual(m, 269241600)
        self.assertGreater(m ** 19, 2 * q ** 6)
        self.assertLess(m ** 19, q ** 7)
        self.assertGreater(q - 1, 2 * 19)  # P^19 > 1-19/(q-1) > 1/2.
        self.assertIsInstance(verify.verify_proth(q), dict)
        self.assertIsInstance(verify.sharpness_certificate(), dict)
        for candidate, base in [(q, 1), (q + 2, 7)]:
            with self.assertRaises(verify.VerificationError):
                verify.verify_proth(candidate, base=base)
        with self.assertRaises(verify.VerificationError):
            verify.sharpness_certificate(base=1)

    def test_receipt_is_deterministic(self):
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        self.assertEqual(verify.build_receipt(), expected)
        self.assertEqual(verify.build_receipt(), expected)

    def test_public_cli_and_copy_corruptions(self):
        with tempfile.TemporaryDirectory(prefix="stock audit ") as temporary:
            copied = Path(temporary) / "package with spaces"
            shutil.copytree(PACKAGE, copied, ignore=shutil.ignore_patterns("__pycache__"))
            result_path = copied / "RESULT.json"
            source_path = copied / "sources" / "pr2234" / "PROOF.md"
            original_result = result_path.read_bytes()
            original_source = source_path.read_bytes()
            verify.verify_sources(copied)
            for optimized in (False, True):
                with self.subTest(optimized=optimized, mutation="none"):
                    completed = cli(copied, optimized)
                    self.assertEqual(completed.returncode, 0,
                                     completed.stdout + completed.stderr)
                    self.assertEqual(result_path.read_bytes(), original_result)
                with self.subTest(optimized=optimized, mutation="missing receipt"):
                    result_path.unlink()
                    completed = cli(copied, optimized)
                    self.assertNotEqual(completed.returncode, 0)
                    self.assertFalse(result_path.exists())
                    result_path.write_bytes(original_result)
                with self.subTest(optimized=optimized, mutation="wrong threshold"):
                    changed, count = replace_threshold(json.loads(original_result))
                    self.assertGreater(count, 0, "receipt must state its threshold")
                    damaged = (json.dumps(changed, sort_keys=True) + "\n").encode()
                    result_path.write_bytes(damaged)
                    completed = cli(copied, optimized)
                    self.assertNotEqual(completed.returncode, 0)
                    self.assertEqual(result_path.read_bytes(), damaged)
                    result_path.write_bytes(original_result)
                for key, replacement in (("schema_version", True), ("cutoff", 311311.0)):
                    with self.subTest(optimized=optimized, mutation="JSON type", field=key):
                        changed = json.loads(original_result)
                        self.assertIs(type(changed[key]), int)
                        changed[key] = replacement
                        damaged = (json.dumps(changed, sort_keys=True) + "\n").encode()
                        result_path.write_bytes(damaged)
                        completed = cli(copied, optimized)
                        self.assertNotEqual(completed.returncode, 0)
                        self.assertEqual(result_path.read_bytes(), damaged)
                        result_path.write_bytes(original_result)
                with self.subTest(optimized=optimized, mutation="source coefficient"):
                    self.assertIn(b"269241600", original_source)
                    damaged = original_source.replace(b"269241600", b"269241601")
                    source_path.write_bytes(damaged)
                    with self.assertRaises(verify.VerificationError):
                        verify.verify_sources(copied)
                    completed = cli(copied, optimized)
                    self.assertNotEqual(completed.returncode, 0)
                    self.assertEqual(source_path.read_bytes(), damaged)
                    self.assertEqual(result_path.read_bytes(), original_result)
                    source_path.write_bytes(original_source)


if __name__ == "__main__":
    unittest.main()
