"""Independent arithmetic/decoder checks and artifact failure controls."""

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import verify as v


def fraction_rank(matrix):
    """Column-space basis insertion, independent of the integer row engine."""
    basis = {}
    for column in zip(*matrix):
        column = list(map(Fraction, column))
        for pivot in sorted(basis):
            factor = column[pivot]
            column = [x - factor * y for x, y in zip(column, basis[pivot])]
        pivot = next((i for i, value in enumerate(column) if value), None)
        if pivot is not None:
            factor = column[pivot]
            basis[pivot] = [value / factor for value in column]
    return len(basis)


class IndependentChecks(unittest.TestCase):
    def test_fraction_column_engine_checks_all_geometric_obligations(self):
        _, data = v.geometry(v.e8_roots())
        bases = data["basis_rows"]
        checked = 0
        for a in bases:
            for b in bases:
                matrix = [[sum(x * y for x, y in zip(row, col)) for col in b]
                          for row in a]
                self.assertEqual(v.rank(matrix), fraction_rank(matrix))
                checked += 1
        for a, b in combinations(bases, 2):
            self.assertEqual(fraction_rank(a + b), 8)
            checked += 1
        self.assertEqual(checked, 145)

    def test_explicit_inverse_decodes_nonlinear_examples(self):
        checked = 0
        for n, width in ((10, 1), (4, 2)):
            code = v.broadcast_code(n, width)
            for x, transmitted in zip(v.states(code.widths), code.messages[0].outputs):
                bits = [(transmitted >> i) & 1 for i in range(n // 2 * width)]
                if bits[0] and bits[1]:
                    bits[2] = 1 - bits[2]
                for pair_index, (a, b) in enumerate(code.pairs):
                    parity = sum(bits[pair_index * width + k] * 2 ** k
                                 for k in range(width))
                    self.assertEqual(parity ^ x[b], x[a])
                    self.assertEqual(parity ^ x[a], x[b])
                checked += 1
        self.assertEqual(checked, 1280)

    def test_all_four_port_one_bit_encoders_fail(self):
        # Exhaust all 2^16 truth tables, including nonlinear encoders, for
        # four independent one-bit inputs. Everyone receives the one bit.
        # A receiver knows just its mate; its two desired values must have
        # disjoint sets of observed outputs at each fixed side-information bit.
        masks = {}
        for t in range(4):
            mate = 3 - t
            masks[t] = [[sum(1 << x for x in range(16)
                             if (x >> t) & 1 == target and (x >> mate) & 1 == side)
                         for target in range(2)] for side in range(2)]

        def can_decode(table, t):
            for zero, one in masks[t]:
                a, b = table & zero, table & one
                if not ((a == 0 and b == one) or (a == zero and b == 0)):
                    return False
            return True

        first_receiver = [table for table in range(1 << 16) if can_decode(table, 0)]
        self.assertEqual(len(first_receiver), 4)
        self.assertEqual([table for table in first_receiver
                          if all(can_decode(table, t) for t in range(4))], [])

    def test_relocated_receipt_and_tamper_rejection_in_optimized_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("verify.py", "SOURCES.json", "RESULTS.json"):
                shutil.copyfile(v.HERE / name, root / name)
            command = [sys.executable, "-I", "-O", "-B", str(root / "verify.py")]
            clean = subprocess.run(command, cwd=root.parent, text=True, capture_output=True)
            self.assertEqual(clean.returncode, 0, clean.stderr)
            self.assertIn("PASS_HURWITZ_NONLINEAR_COPY", clean.stdout)
            original = (root / "RESULTS.json").read_bytes()
            (root / "RESULTS.json").write_bytes(original.replace(b'"cost": 10', b'"cost": 9', 1))
            bad_receipt = subprocess.run(command, cwd=root.parent, text=True, capture_output=True)
            self.assertNotEqual(bad_receipt.returncode, 0)
            self.assertIn("committed receipt differs", bad_receipt.stderr)
            (root / "RESULTS.json").write_bytes(original)
            with (root / "SOURCES.json").open("a") as stream:
                stream.write("\n")
            bad_sources = subprocess.run(command, cwd=root.parent, text=True, capture_output=True)
            self.assertNotEqual(bad_sources.returncode, 0)
            self.assertIn("committed receipt differs", bad_sources.stderr)


if __name__ == "__main__":
    unittest.main()
