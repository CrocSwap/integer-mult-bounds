#!/usr/bin/env python3
"""Independent arithmetic and CLI failure checks. Apache-2.0."""

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

# -I deliberately excludes the script directory; this is a fixed local import.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify


def count_vector_partitions(total, cap):
    if not (1 <= total <= 11 and 1 <= cap <= 6):
        raise ValueError("count-vector oracle domain")
    answer = set()
    for counts in product(*(range(total // d + 1) for d in range(1, cap + 1))):
        if sum(d * n for d, n in enumerate(counts, 1)) == total:
            answer.add(tuple(d for d in range(cap, 0, -1) for _ in range(counts[d - 1])))
    return answer


class TariffTests(unittest.TestCase):
    def test_group_law_matches_literal_matrices(self):
        for g, h in product(range(8), repeat=2):
            self.assertEqual(verify.literal_product(verify.literal_address(g),
                                                    verify.literal_address(h)),
                             verify.literal_address(verify.group_product(g, h)))
        self.assertNotEqual(verify.group_product(1, 2), verify.group_product(2, 1))
        self.assertEqual(verify.group_product(verify.group_product(1, 2),
                                             verify.group_product(1, 2)), 4)

    def test_all_partitions_against_count_vector_oracle(self):
        for total in range(1, 10):
            for cap in range(1, 6):
                actual = list(verify.partitions(total, cap))
                self.assertEqual(len(actual), len(set(actual)))
                self.assertEqual(set(actual), count_vector_partitions(total, cap))
        self.assertEqual(len(list(verify.partitions(9, 7))), 28)
        with self.assertRaisesRegex(ValueError, "partition domain"):
            list(verify.partitions(15, 7))

    def test_independent_exact_price_minimum(self):
        # Count vectors, not the production partition iterator or cost function.
        for w in range(1, 5):
            for k in range(1, 7):
                bounds = []
                for mass in range(2 * w, 2 * w + 4):
                    for ranks in count_vector_partitions(mass, k):
                        if 2 * max(ranks) <= mass:
                            bounds.append(sum((Fraction(d, d + 1) for d in ranks), Fraction()))
                cap = min(k, w)
                quotient, remainder = divmod(2 * w, cap)
                expected = quotient * Fraction(cap, cap + 1) + Fraction(remainder, remainder + 1)
                self.assertEqual(min(bounds), expected)

    def test_pilot_complete_dirty_operator(self):
        masks = verify.supports(5, 4)
        self.assertEqual(masks, (15, 23, 24))
        word = verify.word_from_supports(masks)
        self.assertEqual(verify.formal_endpoint(word, 7), (4, 4, 4, 4, 4, 0, 0))
        # Literal central action toggles the upper-right address bit.
        expected = tuple((i, g ^ (4 if i < 5 else 0))
                         for i in range(7) for g in range(8))
        self.assertEqual(verify.regular_endpoint(word, 7), expected)
        self.assertEqual(verify.regular_endpoint(tuple(reversed(word)), 7), expected)
        self.assertEqual(verify.check_controls(), 11)
        self.assertEqual(verify.packed_ranks(5, 10000), (5, 5))
        self.assertEqual(verify.packed_ranks(1, 1), (1, 1))
        for w, k in ((0, 1), (33, 1), (1, 0), (True, 1), (1, 1.5)):
            with self.assertRaises(ValueError):
                verify.packed_ranks(w, k)

    def test_full_cli_read_only_export_and_optimized(self):
        with tempfile.TemporaryDirectory() as directory:
            export = Path(directory)
            for name in ("verify.py", "RESULT.json"):
                shutil.copyfile(HERE / name, export / name)
            before = {p.name: p.read_bytes() for p in export.iterdir()}
            for options in ((), ("-O",)):
                result = subprocess.run([sys.executable, "-I", "-X", "dev", "-B",
                                         *options, str(export / "verify.py")],
                                        cwd=directory, capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), json.loads(before["RESULT.json"]))
                self.assertEqual(result.stderr, "")
            self.assertEqual({p.name: p.read_bytes() for p in export.iterdir()}, before)

    def test_cli_rejects_receipt_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            export = Path(directory)
            shutil.copyfile(HERE / "verify.py", export / "verify.py")
            original = json.loads((HERE / "RESULT.json").read_text())
            for field in ("fixtures", "profile_digest", "pilot"):
                changed = dict(original)
                changed[field] = None
                (export / "RESULT.json").write_text(json.dumps(changed))
                result = subprocess.run([sys.executable, "-I", "-O", "-B",
                                         str(export / "verify.py")], cwd=directory,
                                        capture_output=True, text=True, timeout=30)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("receipt differs", result.stderr)
                self.assertEqual(result.stdout, "")
            (export / "RESULT.json").write_bytes(b" " * 4097)
            result = subprocess.run([sys.executable, "-I", "-B", str(export / "verify.py")],
                                    cwd=directory, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt capacity exceeded", result.stderr)


if __name__ == "__main__":
    unittest.main()
