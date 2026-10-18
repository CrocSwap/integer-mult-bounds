# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the public certificate and its source interpretation."""

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from inverse import ONE, certify, quotient, variable
from paths import MAX_PATHS, collect, combine, expand, parity_polynomial
from source import MAX_GATES, PATHS, Gate, gates_from_inputs, load_inputs, project_rows
from verify import expected_export


def rotate(value: tuple[int, int], exponent: int) -> tuple[int, int]:
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent % 4]


def dense(gates: list[Gate], z: list[int], character: int) -> list:
    matrix = [[(int(i == j), 0) for j in range(8)] for i in range(8)]
    for gate in gates:
        row, source = gate.row, gate.source
        if gate.kind == "phase":
            exponent = sum(c * ((a & character).bit_count() % 2) for a, c in gate.phases)
            scale = 1 if gate.site < 0 else z[gate.site]
            matrix[row] = [rotate((a * scale, b * scale), exponent) for a, b in matrix[row]]
        elif gate.kind == "add":
            matrix[row] = [(a + gate.coefficient * c, b + gate.coefficient * d)
                           for (a, b), (c, d) in zip(matrix[row], matrix[source], strict=True)]
        elif gate.kind == "exchange":
            x, y = matrix[row], matrix[source]
            matrix[row], matrix[source] = y, [(-a, -b) for a, b in x]
        else:
            raise ValueError("invalid primitive")
    return matrix


def evaluate(rows: list, z: list[int], character: int, q: int = 11) -> list:
    matrix = [[(0, 0) for _ in range(8)] for _ in range(8)]
    for row, column, mask, ambient, coefficient in rows:
        value = coefficient
        for i in range(20):
            if mask >> i & 1:
                value *= z[i]
        real, imag = rotate((value, 0), ambient * ((q & character).bit_count() % 2))
        a, b = matrix[row][column]
        matrix[row][column] = a + real, b + imag
    return matrix


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = load_inputs()
        cls.gates, cls.ranks = gates_from_inputs(cls.data)
        cls.expected = expected_export()["polynomial_matrix"]

    def test_complete_source_and_unit_denominators(self) -> None:
        streams, peak, count = expand(self.gates)
        rows = collect(streams, 11)
        self.assertEqual(rows, self.expected)
        self.assertEqual((peak, count, len(rows)), (1174, 1174, 72))
        certificate = certify(rows)
        self.assertEqual(certificate["coordinates"], 20)
        self.assertEqual(len(certificate["unit_divisions"]), 21)
        self.assertTrue(all(coefficient == 1 for _, coefficient in certificate["unit_divisions"]))

    def test_all_small_parity_functions(self) -> None:
        for axis in range(64):
            lifted = parity_polynomial(axis)
            for character in range(64):
                observed = sum(c for mask, c in lifted if character & mask == mask) % 4
                self.assertEqual(observed, (axis & character).bit_count() % 2)
        mixed = (1 << 72) | (1 << 35) | 11
        for character in (0, 11, mixed, (1 << 73) - 1):
            polynomial = combine(parity_polynomial(mixed), parity_polynomial(11), -3)
            value = sum(c for mask, c in polynomial if character & mask == mask) % 4
            self.assertEqual(value, ((mixed & character).bit_count() % 2
                                     - 3 * ((11 & character).bit_count() % 2)) % 4)

    def test_direct_gaussian_integer_oracle(self) -> None:
        characters = (0, 1, 11, (1 << 72) | 16, (1 << 73) - 1)
        fixtures = ([1] * 20, [-1 if i % 3 else 2 for i in range(20)],
                    [i % 4 + 1 for i in range(20)])
        for character in characters:
            for phases in fixtures:
                self.assertEqual(dense(self.gates, phases, character),
                                 evaluate(self.expected, phases, character))

    def test_each_formal_site_is_observable(self) -> None:
        baseline = evaluate(self.expected, [1] * 20, 0)
        for site in range(20):
            phases = [1] * 20
            phases[site] = -1
            self.assertNotEqual(evaluate(self.expected, phases, 0), baseline)

    def test_source_semantic_mutants(self) -> None:
        bridge = next(i for i, gate in enumerate(self.gates)
                      if gate.kind == "add" and gate.row // 2 != gate.source // 2)
        empty = next(i for i, gate in enumerate(self.gates) if gate.site == 0)
        terminal = next(i for i, gate in enumerate(self.gates) if gate.kind == "exchange")
        translation = next(i for i, gate in enumerate(self.gates)
                           if gate.kind == "phase" and any(c == 2 and a != 0 for a, c in gate.phases))
        mutants = {
            "missing first hosted phase": self.gates[1:],
            "wrong bridge sign": [replace(gate, coefficient=-gate.coefficient) if i == bridge else gate
                                  for i, gate in enumerate(self.gates)],
            "unrepresented empty site": [replace(gate, site=-1) if i == empty else gate
                                        for i, gate in enumerate(self.gates)],
            "missing signed terminal exchange": self.gates[:terminal] + self.gates[terminal + 1:],
            "missing dirty translation": self.gates[:translation] + self.gates[translation + 1:],
        }
        for name, gates in mutants.items():
            with self.subTest(name=name):
                try:
                    paths, _, _ = expand(gates)
                    rows = collect(paths, 11)
                except ValueError:
                    continue  # A changed character factor also rejects the source certificate.
                self.assertNotEqual(rows, self.expected)

    def test_corrupt_coefficient_fails_inverse(self) -> None:
        rows = [row[:] for row in self.expected]
        diagonal = next(i for i, row in enumerate(rows) if row[:2] == [0, 0])
        rows[diagonal][-1] *= -1
        with self.assertRaises(ValueError):
            certify(rows)

    def test_nonmonomial_zero_and_nonunit_divisors_reject(self) -> None:
        for denominator in ({}, {**variable(0), **variable(1)}, {(0,) * 20: 2}):
            with self.subTest(denominator=denominator), self.assertRaises(ValueError):
                quotient(ONE, denominator, [])
        # Nonzero variables may be negative, and Laurent monomials are still units.
        self.assertEqual(quotient(variable(0), variable(1), []),
                         {(1, -1) + (0,) * 18: 1})

    def test_export_and_raw_source_corruption_reject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            exported = root / "export.json"
            exported.write_text("{}")
            with self.assertRaises(ValueError):
                expected_export(exported)
            source = root / PATHS["fill"]
            source.parent.mkdir(parents=True)
            source.write_bytes(b"corrupt source")
            with self.assertRaises(ValueError):
                load_inputs(root)

    def test_journal_preimage_and_duplicate_reject(self) -> None:
        data = dict(self.data)
        journal = json.loads(json.dumps(data["edits"]))
        journal["edits"][0][1][0] += 1
        data["edits"] = journal
        with self.assertRaises(ValueError):
            project_rows(data)
        journal = json.loads(json.dumps(self.data["edits"]))
        journal["edits"][1] = journal["edits"][0]
        data["edits"] = journal
        with self.assertRaises(ValueError):
            project_rows(data)

    def test_bounds_and_unknown_operations_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            expand([Gate("phase", 0)] * (MAX_GATES + 1))
        with self.assertRaises(ValueError):
            expand([Gate("unknown", 0)])
        with self.assertRaises(ValueError):
            expand([Gate("add", 0, 0)])
        # Alternating shears grow Fibonacci-many uncancelled paths before cancellation.
        gates = [Gate("add", i % 2, 1 - i % 2) for i in range(40)]
        with self.assertRaisesRegex(ValueError, "path capacity"):
            expand(gates)
        self.assertGreater(MAX_PATHS, 1174)


if __name__ == "__main__":
    unittest.main()
