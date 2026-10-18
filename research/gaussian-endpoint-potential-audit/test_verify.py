"""Boundary, arithmetic and packaging controls for the scoped audit."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from itertools import product
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

import verify


class AuditTests(unittest.TestCase):
    def test_signed_phase_and_periodicity(self):
        for s in range(2, 15):
            for t in range(s + 1, 2 * s):
                for j in range(-3 * s, 3 * s):
                    quotient, remainder = divmod(t * j, s)
                    nearest = quotient + int(2 * remainder >= s)
                    expected = Fraction(t * j, s) - nearest
                    self.assertEqual(verify.phase(s, t, j), expected)
                    self.assertEqual(verify.phase(s, t, j + s), expected)

    def test_formal_matrix_powers_preserve_wrapped_steps(self):
        # Represent truncated E entries as exact polynomials in z=exp(-A/s^2).
        # Matrix multiplication groups paths by destination, unlike verify.py.
        # Nonzero h = +/-s must contribute to diagonal entries.
        for s, t in ((2, 3), (3, 4), (4, 5)):
            moves = tuple(h for h in range(-s, s + 1) if h)
            def beta_num(j):
                return t * j - s * ((2 * t * j + s) // (2 * s))

            matrix = [[Counter() for _ in range(s)] for _ in range(s)]
            for j in range(s):
                for h in moves:
                    exponent = (t * h + beta_num(j)) ** 2 - beta_num(j + h) ** 2
                    matrix[j][(j + h) % s][exponent] += 1
                self.assertEqual(sum(matrix[j][j].values()), 2)
            square = [[Counter() for _ in range(s)] for _ in range(s)]
            for j, k, middle in product(range(s), repeat=3):
                for a, na in matrix[j][middle].items():
                    for b, nb in matrix[middle][k].items():
                        square[j][k][a + b] += na * nb
            for j in range(s):
                direct = [Counter() for _ in range(s)]
                for h1, h2 in product(moves, repeat=2):
                    x1 = verify.step(s, t, j, h1)[0]
                    x2 = verify.step(s, t, j + h1, h2)[0]
                    exponent = (x1 + x2) * s * s
                    self.assertEqual(exponent.denominator, 1)
                    direct[(j + h1 + h2) % s][int(exponent)] += 1
                self.assertEqual(square[j], direct)
                self.assertEqual(sum(sum(entry.values()) for entry in square[j]), len(moves) ** 2)

    def test_counterexamples_and_domain_controls(self):
        self.assertEqual(verify.rejection_controls(), 10)
        # This admitted tuple isolates an actual integer count improvement.
        example = verify.counts(128, 4, 15, 16)
        self.assertEqual(example["residual_count"], 5)
        self.assertEqual(example["old_endpoint_same_decay_count"], 6)
        self.assertEqual(example["original_corollary_count"], 18)

    def test_constants_are_certified(self):
        verify.constant_checks()

    def test_independent_oracle_detects_corruption(self):
        original = verify.integer_path
        def wrong_exponent(*args):
            total, slack = original(*args)
            return total + 1, slack
        with patch.object(verify, "integer_path", wrong_exponent):
            with self.assertRaisesRegex(ValueError, "independent exponent"):
                verify.audit_path(4, 5, 2, (1, -1, 4))

    def test_source_drift_and_missing_source(self):
        rows = json.loads((verify.HERE / "SOURCES.json").read_text())["files"]
        with tempfile.TemporaryDirectory(prefix="gaussian audit ") as folder:
            root = Path(folder)
            for row in rows:
                target = root / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((verify.ROOT / row["path"]).read_bytes())
            self.assertEqual(verify.source_check(root), len(rows))
            target = root / rows[0]["path"]
            original = target.read_bytes()
            target.write_bytes(original + b"\n% control\n")
            with self.assertRaisesRegex(ValueError, "source drift"):
                verify.source_check(root)
            target.unlink()
            with self.assertRaises(FileNotFoundError):
                verify.source_check(root)

    def test_receipt_corruption_including_numeric_types(self):
        expected = json.loads((verify.HERE / "RESULT.json").read_text())
        verify.check_receipt(expected, deepcopy(expected))
        for field, replacement in (("assignment_seed", 63), ("controls", True),
                                   ("controls", 10.0), ("exact_paths", 0)):
            bad = deepcopy(expected)
            bad[field] = replacement
            with self.assertRaisesRegex(ValueError, "receipt mismatch"):
                verify.check_receipt(expected, bad)
        bad = deepcopy(expected)
        del bad["examples"]
        with self.assertRaisesRegex(ValueError, "receipt mismatch"):
            verify.check_receipt(expected, bad)

    def test_existing_output_preserved(self):
        # Check the CLI output policy without repeating the full enumeration.
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "receipt.json"
            output.write_bytes(b"retained\n")
            with patch.object(verify, "certificate", return_value={}), \
                 patch("sys.argv", ["verify.py", "--write", str(output)]):
                with self.assertRaises(FileExistsError):
                    verify.main()
            self.assertEqual(output.read_bytes(), b"retained\n")


if __name__ == "__main__":
    unittest.main()
