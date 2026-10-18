#!/usr/bin/env python3
"""Behavioral controls for the literal contract and the two algebra interpreters."""

import copy
import sys
import tempfile
import unittest
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backward
import verify as v


def execute(model, dual=False, dirty=True):
    rows = {r: v.identity(r) for r in model.live}
    rows.update({r: v.identity(r) if dirty else {} for r in model.private})
    for gate in model.gates:
        v.apply(v.oriented(gate, dual), rows)
    return rows


class CleanupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        entries = [e for e in v.read_json(v.PACKAGE / "SOURCES.json")["files"]
                   if e["usage"] == "input"]
        cls.entry = entries[0]
        cls.word = v.read_word(v.ROOT, cls.entry)
        cls.model = v.decode(cls.word)

    def test_literal_positive_and_receipts(self):
        self.assertEqual(v.audit(), v.read_json(v.PACKAGE / "RESULT.json"))
        self.assertEqual(backward.audit(), v.read_json(v.PACKAGE / "BACKWARD.json"))

    def test_source_and_duplicate_json_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / self.entry["path"]
            source.parent.mkdir(parents=True)
            source.write_bytes((v.ROOT / self.entry["path"]).read_bytes() + b"x")
            with self.assertRaisesRegex(ValueError, "source hash"):
                v.read_word(root, self.entry)
            duplicate = root / "duplicate.json"
            duplicate.write_text('{"x": 1, "x": 2}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON"):
                v.read_json(duplicate)

    def test_literal_contract_mutations(self):
        for mutation in ("length", "frame", "register", "private", "denominator", "operator"):
            word = copy.deepcopy(self.word)
            if mutation == "length":
                word["cleanup"].pop()
            elif mutation == "frame":
                word["cleanup"][0][-1] = []
            elif mutation == "register":
                word["cleanup"][0][1] = word["removed"][0]
            elif mutation == "private":
                word["helper_final"].pop(next(iter(word["helper_final"])))
            elif mutation == "denominator":
                word["cleanup"][0][4] = 0
            else:
                next(g for g in word["cleanup"] if g[0] == "warp")[2] = 0
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                v.decode(word)

    def test_actual_gate_deletion_and_coefficient(self):
        closing = v.last_touches(self.model)[930]
        mutations = []
        gates = list(self.model.gates)
        gates[closing] = replace(gates[closing], coefficient=-gates[closing].coefficient)
        mutations.append(gates)
        gates = list(self.model.gates)
        gates.pop(closing)
        mutations.append(gates)
        for index, gates in enumerate(mutations):
            with self.subTest(index=index), self.assertRaises(ValueError):
                v.replay(replace(self.model, gates=tuple(gates)), False)

    def test_warp_fault_changes_live_map_not_private_contract(self):
        index = next(i for i, gate in enumerate(self.model.gates) if gate.kind == "warp")
        gates = list(self.model.gates)
        gates[index] = replace(gates[index], operator=-gates[index].operator)
        result = v.replay(replace(self.model, gates=tuple(gates)), False)
        original = v.replay(self.model, False)
        self.assertTrue(result["private_identity"])
        self.assertNotEqual(result["matrix_sha256"], original["matrix_sha256"])

    def test_dirty_only_leak_is_invisible_to_clean_replay(self):
        # The last use of private 1003 reads it into live 302. It is zero for
        # clean entrance, but is exactly its arbitrary entrance for dirty input.
        index = v.last_touches(self.model)[1003]
        self.assertEqual(index, 4844)
        gates = list(self.model.gates)
        self.assertEqual((gates[index].target, gates[index].source), (302, 1003))
        gates[index] = replace(gates[index], coefficient=2 * gates[index].coefficient)
        mutant = replace(self.model, gates=tuple(gates))
        self.assertEqual(execute(mutant, dirty=False), execute(self.model, dirty=False))
        with self.assertRaises(ValueError):
            v.replay(mutant, False)
        original_rows, changed_rows = execute(self.model), execute(mutant)
        differences = {}
        for register in changed_rows:
            keys = set(changed_rows[register]) | set(original_rows[register])
            delta = {key: changed_rows[register].get(key, 0) - original_rows[register].get(key, 0)
                     for key in keys}
            delta = {key: value for key, value in delta.items() if value}
            if delta:
                differences[register] = delta
        self.assertEqual(differences, {302: {(1003, ()): -Q(1, 4)},
                                      930: {(1003, ()): Q(1, 8)},
                                      934: {(1003, ()): Q(1, 8)}})

    def test_early_return_is_not_an_endpoint_identity(self):
        rows = {r: v.identity(r) for r in self.model.live + self.model.private}
        for gate in self.model.gates[:3]:
            v.apply(gate, rows)
        self.assertNotEqual(rows[1099], v.identity(1099))
        self.assertGreater(v.last_touches(self.model)[1099], 2)

    def test_left_and_right_interpreters_on_noncommuting_word(self):
        raw = [["add", 0, 1, 1, 2, v.FULL], ["warp", 0, 1, v.FULL],
               ["warp", 0, 2, v.FULL], ["add", 2, 0, -3, 2, v.FULL],
               ["warp", 0, -1, v.FULL], ["scale", 1, 1, -2, v.FULL]]
        gates = tuple(v.parse_gate(g, {0, 1, 2}, 2) for g in raw)
        for dual in (False, True):
            rows = execute(v.Model(gates, (0, 1, 2), ()), dual)
            for output in range(3):
                covector, _ = backward.reverse_row(raw, output, dual)
                expected = {(source, word): value for source, polynomial in covector.items()
                            for word, value in polynomial.items()}
                self.assertEqual(rows[output], expected)
                column, _ = backward.reverse_row(backward.transposed_program(raw, dual), output, False)
                expected_column = {(target, word[::-1]): value for target, polynomial in column.items()
                                   for word, value in polynomial.items()}
                actual_column = {(target, word): value for target, polynomial in rows.items()
                                 for (source, word), value in polynomial.items() if source == output}
                self.assertEqual(actual_column, expected_column)
        rows = execute(v.Model(gates, (0, 1, 2), ()))
        self.assertIn((0, (-1, 2, 1)), rows[0])
        self.assertNotIn((0, (2,)), rows[0])

    def test_no_inverse_cancellation_and_capacity(self):
        self.assertEqual(v.prepend(-3, (3, 2)), (-3, 3, 2))
        self.assertEqual(backward.append_letter((2, 3), -3), (2, 3, -3))
        self.assertEqual(v.prepend(-3, (2, 3)), (-3, 2, 3))
        with self.assertRaisesRegex(ValueError, "word capacity"):
            v.prepend(1, (1,) * 256)
        with self.assertRaisesRegex(ValueError, "polynomial capacity"):
            v.bounded({(r, ()): Q(1) for r in range(v.MAX_TERMS + 1)})
        with self.assertRaisesRegex(ValueError, "coefficient capacity"):
            v.bounded({(0, ()): Q(1 << 4096)})

    def test_private_input_leak_and_dirty_private_scaling(self):
        live, private = self.model.live[0], self.model.private[0]
        for gate in (v.Gate("add", live, private),
                     v.Gate("scale", private, coefficient=Q(2))):
            mutant = replace(self.model, gates=self.model.gates + (gate,))
            with self.subTest(kind=gate.kind), self.assertRaises(ValueError):
                v.replay(mutant, False)

    def test_receipt_corruption(self):
        result = v.read_json(v.PACKAGE / "RESULT.json")
        result["cases"]["base"][0]["last_touches"]["930"] -= 1
        self.assertNotEqual(v.audit(), result)


if __name__ == "__main__":
    unittest.main()
