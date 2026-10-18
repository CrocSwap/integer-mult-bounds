# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for alignment, range, ownership and literal bit gates."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import verify
from bitadder import adder, apply, circuit, execute, rational, terms, validate
from check_bits import check_truth


class BitTests(unittest.TestCase):
    def test_signed_coefficient_identity(self):
        self.assertEqual(terms(7, 4), [(-1, -2), (1, 1)])
        self.assertEqual(terms(-7, 8), [(1, -3), (-1, 0)])
        self.assertEqual(len(terms(7, 4, False)), 3)
        self.assertEqual(len(terms(7, 4)), 2)

    def test_dirty_signed_endpoints(self):
        for width in (4, 8, 64, 256):
            for a, b, source, target, expected in (
                (1, 2, -4, 3, 1),
                (-1, 4, -4, -2, -1),
                (7, 4, 4, -3, 4),
                (-7, 8, -8, -3, 4),
                (2, 1, 2, -3, 1),
                (0, 1, -4, 3, 3),
            ):
                self.assertEqual(execute(width, a, b, source, target), expected)

    def test_alignment_and_endpoint_are_separate(self):
        with self.assertRaisesRegex(ValueError, "alignment"):
            execute(8, 1, 2, 3, 0)
        with self.assertRaisesRegex(ValueError, "endpoint"):
            execute(8, 1, 1, 127, 1)
        self.assertEqual(execute(8, 1, 1, 127, 1, exact=False), -128)
        self.assertEqual(execute(8, 1, 2, -128, 1), -63)

    def test_modular_prefix_needs_no_arithmetic_guard(self):
        # 7/4 = -1/4 + 2: the first signed partial sum underflows.
        self.assertEqual(execute(8, 7, 4, 4, -128), -121)

    def test_gate_counts_and_positive_shift_pruning(self):
        for width in range(2, 257):
            gates = adder(width, 0)
            self.assertEqual(sum(g[0] == "ccx" for g in gates), 4 * width - 6)
            self.assertEqual(sum(g[0] == "cx" for g in gates), 4 * width - 5)
            self.assertEqual(
                adder(width, 1),
                [
                    (
                        g[0],
                        *[
                            (kind, index + 1 if kind == "t" else index)
                            for kind, index in g[1:]
                        ],
                    )
                    for g in adder(width - 1, 0)
                ],
            )
        self.assertEqual(adder(1, 0), [("cx", ("s", 0), ("t", 0))])
        self.assertEqual(adder(2, 3), [])

    def test_independent_integer_interpreter(self):
        # Separate scalar-bit execution, not the bit-packed apply interpreter.
        for width in range(1, 6):
            modulus = 1 << width
            for source in range(modulus):
                for target in range(modulus):
                    for sign in (-1, 1):
                        gates = adder(width, 0)
                        gates = gates if sign > 0 else list(reversed(gates))
                        wires = {("s", i): (source >> i) & 1 for i in range(width)}
                        wires.update(
                            {("t", i): (target >> i) & 1 for i in range(width)}
                        )
                        wires.update({("c", i): 0 for i in range(width - 1)})
                        for gate in gates:
                            enabled = all(wires[wire] == 1 for wire in gate[1:-1])
                            if enabled:
                                wires[gate[-1]] = 1 - wires[gate[-1]]
                        got = sum(wires["t", i] << i for i in range(width))
                        self.assertEqual(got, (target + sign * source) % modulus)
                        self.assertEqual(
                            sum(wires["s", i] << i for i in range(width)), source
                        )
                        self.assertFalse(any(wires["c", i] for i in range(width - 1)))

    def test_semantic_mutations_reject(self):
        gates = circuit(5, 1, 2)
        for mutant in (list(reversed(gates)), gates[:-2], gates[1:]):
            with self.assertRaises(ValueError):
                check_truth(mutant, 5, 1, 2)

    def test_source_and_carry_ownership(self):
        bad = [("cx", ("t", 0), ("s", 0))]
        with self.assertRaisesRegex(ValueError, "read-only"):
            validate(bad, 4)
        with self.assertRaisesRegex(ValueError, "distinct"):
            validate([("ccx", ("s", 0), ("s", 0), ("t", 0))], 4)
        with self.assertRaisesRegex(ValueError, "index"):
            validate([("cx", ("s", 4), ("t", 0))], 4)
        wires = {(kind, i): 0 for kind in ("s", "t") for i in range(4)}
        wires.update({("c", i): 0 for i in range(3)})
        wires["c", 0] = 1
        after = apply(adder(4, 0), wires, 4)
        self.assertNotEqual([after["t", i] for i in range(4)], [0] * 4)

    def test_boundary_rejections(self):
        for a, b in ((1, 3), (256, 1), (1, 8192), (1, 0), (True, 1)):
            with self.assertRaises(ValueError):
                rational(a, b)
        for width in (0, 257, True):
            with self.assertRaises(ValueError):
                adder(width, 0)
        with self.assertRaises(ValueError):
            adder(8, -13)

    def test_frozen_source_mutation(self):
        with tempfile.TemporaryDirectory(prefix="rank7-bits-control-") as directory:
            from shutil import copytree

            package = Path(directory) / "package"
            copytree(verify.PACKAGE, package)
            path = package / "vendor/parent/EDITS.json"
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "source bytes"):
                verify.authenticate(package)

    def test_occupied_workspace_is_preserved(self):
        with tempfile.TemporaryDirectory(prefix="rank7-bits-occupied-") as directory:
            marker = Path(directory) / "marker"
            marker.write_text("preserve")
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(verify.PACKAGE / "verify.py"),
                    "--work",
                    directory,
                ],
                capture_output=True,
                check=False,
                timeout=10,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"fresh output directory", result.stderr)
            self.assertEqual(marker.read_text(), "preserve")
            self.assertEqual(list(Path(directory).iterdir()), [marker])


if __name__ == "__main__":
    unittest.main()
