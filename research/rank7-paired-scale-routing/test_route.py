# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with OpenAI Codex.
"""Arithmetic, ownership and reversible-cleanup controls for local routing."""
from itertools import product
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import route
from source_events import authenticate, load_pairscale


def signed(value, width):
    return value - (1 << width) if value >> (width - 1) else value


def tapes(width, real, imag):
    return [route.Tape((value >> i) & 1 for i in range(width))
            for value in (real, imag)] + [route.Tape((0,))]


class RouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paired = load_pairscale()

    def gates(self, width, control=False):
        return self.paired.circuit(width, 1, -1, [("neg", 0)], control=control)

    def check_boundary(self, result, expected):
        self.assertEqual(result["components"], expected)
        self.assertEqual(result["carry"], 0)
        self.assertEqual(result["heads"], (0, 0, 0))
        self.assertEqual(result["scratch"], (0, 0))

    def test_exhaustive_four_bit_arithmetic_and_comparator(self):
        for control in (False, True):
            gates = self.gates(4, control)
            for real, imag in product(range(-8, 8), repeat=2):
                with self.subTest(control=control, real=real, imag=imag):
                    result = route.execute(4, gates, real, imag)
                    self.check_boundary(result, ((-real) % 16, (-imag) % 16))

    def test_width84_extremes_and_separate_signed_guard(self):
        width, limit = 84, 1 << 83
        cases = [(0, 0), (1, -1), (limit - 1, 1 - limit), (-limit, 0),
                 (0, -limit), (-limit, -limit), (1 << 61, -(1 << 62))]
        for control in (False, True):
            gates = self.gates(width, control)
            for real, imag in cases:
                with self.subTest(control=control, real=real, imag=imag):
                    result = route.execute(width, gates, real, imag)
                    self.check_boundary(result, ((-real) % (1 << width),
                                                 (-imag) % (1 << width)))
        with self.assertRaises(ValueError):
            self.paired.endpoint(width, 1, -1, -limit)
        self.assertEqual(self.paired.endpoint(width, 1, -1, 1 - limit), limit - 1)

    def test_independent_gate_truth_and_inverse(self):
        width = 4
        gates = ((0, 8), (8, 4, 1), (0, 8), (5, 3), (2, 6, 7))
        for real, imag in product((-8, -1, 0, 1, 7), repeat=2):
            bits = [(value >> i) & 1 for value in (real, imag)
                    for i in range(width)] + [0]
            for gate in gates:
                if all(bits[wire] for wire in gate[:-1]):
                    bits[gate[-1]] = 1 - bits[gate[-1]]
            expected = tuple(sum(bits[bank * width + i] << i for i in range(width))
                             for bank in (0, 1))
            result = route.execute(width, gates, real, imag)
            self.check_boundary(result, expected)
            inverse = route.execute(width, tuple(reversed(gates)),
                                    *(signed(value, width) for value in expected))
            self.check_boundary(inverse, (real % 16, imag % 16))

    def test_independent_gate_access_counts(self):
        for width, control in product((4, 8, 84), (False, True)):
            gates = self.gates(width, control)
            expected = {
                "moves": 104 * width - 176 if control else 64 * width - 140,
                "reads": sum(2 * (len(gate) - 1) + 1 for gate in gates),
                "writes": len(gates),
            }
            self.assertEqual(expected["reads"],
                             150 * width - 96 if control else 88 * width - 108)
            self.assertEqual(expected["writes"],
                             42 * width - 24 if control else 24 * width - 28)
            result = route.execute(width, gates, -3, 5)
            self.assertEqual(result["counters"], expected)
            self.assertEqual(route.counters(route.compile_route(width, gates)), expected)

    def test_local_trace_is_data_independent(self):
        traces = []
        for value in (0, -1):
            trace = []

            class ObservedTape(route.Tape):
                def __init__(self, bank, bits):
                    super().__init__(bits)
                    self.bank = bank

                def move(self, direction):
                    before = self.head
                    super().move(direction)
                    trace.append(("moves", self.bank, before, self.head))

                def read(self):
                    trace.append(("reads", self.bank, self.head))
                    return super().read()

                def write(self, bit):
                    trace.append(("writes", self.bank, self.head))
                    super().write(bit)

            owned = [ObservedTape(bank, ((value >> i) & 1 for i in range(4)))
                     for bank in (0, 1)] + [ObservedTape(2, (0,))]
            program = route.compile_route(4, self.gates(4))
            result = route.run_route(4, program, owned)
            for entry in trace:
                self.assertTrue(0 <= entry[2] < (1 if entry[1] == 2 else 4))
                if entry[0] == "moves":
                    self.assertEqual(abs(entry[3] - entry[2]), 1)
                if entry[0] == "writes":
                    self.assertIn(entry[1], (0, 1, 2))
            self.assertEqual(result["counters"],
                             {name: sum(entry[0] == name for entry in trace)
                              for name in ("moves", "reads", "writes")})
            traces.append(trace)
        self.assertEqual(*traces)

    def test_malformed_wires_and_ownership_entrance(self):
        for gate in ((0,), (0, 1, 2, 3), (-1, 1), (0, 9), (0, 0),
                     (0, 0, 1), (0, 1, 0), (True, 1), "01"):
            with self.subTest(gate=gate), self.assertRaises(ValueError):
                route.compile_route(4, (gate,))
        for width in (3, 257, True):
            with self.assertRaises(ValueError):
                route.compile_route(width, ())
        with self.assertRaises(ValueError):
            route.execute(4, (), 0, 0, carry=1)
        with self.assertRaises(ValueError):
            route.execute(4, (), 8, 0)
        owned = tapes(4, 0, 0)
        with self.assertRaises(ValueError):
            route.run_route(4, (), (owned[0], owned[0], owned[2]))
        owned[0].move(1)
        with self.assertRaises(ValueError):
            route.run_route(4, (), owned)
        with self.assertRaises(ValueError):
            route.run_route(4, (("move", 0, 2),), tapes(4, 0, 0))

    def test_missing_control_uncompute_is_rejected(self):
        program = route.compile_route(4, ((0, 4),))
        self.assertEqual(program[-1], ("xor", 0, 0))
        with self.assertRaisesRegex(ValueError, "scratch"):
            route.run_route(4, program[:-1], tapes(4, 1, 0))

    def test_missing_final_head_movement_is_rejected(self):
        program = route.compile_route(4, self.gates(4))
        self.assertEqual(program[-1][0], "move")
        with self.assertRaisesRegex(ValueError, "heads"):
            route.run_route(4, program[:-1], tapes(4, 3, -2))

    def test_changed_paired_source_is_rejected_before_reuse(self):
        target = Path(__file__).resolve().parents[2] / "research/rank7-paired-scale/pairscale.py"
        original_read, touched = Path.read_bytes, []

        def changed_read(path):
            value = original_read(path)
            if path == target:
                touched.append(path)
                return value + b"\n# source corruption control\n"
            return value

        with patch.object(Path, "read_bytes", changed_read):
            with self.assertRaisesRegex(ValueError, "source hash: .*pairscale.py"):
                authenticate()
        self.assertEqual(touched, [target])


if __name__ == "__main__":
    unittest.main()
