#!/usr/bin/env python3
"""Exact positive fixtures and failure controls, including optimized execution."""
from fractions import Fraction as F
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import route as R
import verify as V


class CarryTests(unittest.TestCase):
    def test_literal_signed_carries(self):
        self.assertEqual(R.carry_update(0, 0, 1, 0, F(1, 2), 5, 2, False), (3, 2))
        self.assertEqual(R.carry_update(0, 0, 1, 0, F(-1, 2), 5, 2, False), (2, 2))
        self.assertEqual(R.carry_update(4, 0, 4, 0, F(1), 5, 2, False), (3, 1))
        self.assertEqual(R.carry_update(1, 0, 0, 0, F(1, 2), 5, 2, True), (3, 2))
        self.assertEqual(R.carry_update(1, 0, 0, 0, F(1, 2), 5, 1, True), (3, 0))

    def test_exhaustive_elementary_ring_maps(self):
        count = 0
        for q, width, coefficients in ((3, 2, (F(1, 2), F(-3, 2), F(2))),
                                        (5, 2, (F(-7, 3), F(1, 2)))):
            modulus = q**width
            for c in coefficients:
                cm = c.numerator * pow(c.denominator, -1, modulus) % modulus
                for x in range(modulus):
                    for y in range(modulus):
                        low, high = R.carry_update(y % q, y // q, x % q, x // q,
                                                   c, q, width, False)
                        self.assertEqual(low + q * high, (y + cm * x) % modulus)
                        count += 1
                if c.numerator % q:
                    image = set()
                    for y in range(modulus):
                        low, high = R.carry_update(y % q, y // q, 0, 0, c, q, width, True)
                        self.assertEqual(low + q * high, cm * y % modulus)
                        image.add(low + q * high)
                    self.assertEqual(len(image), modulus)
        self.assertEqual(count, 1493)

    def test_bad_boundaries(self):
        base = [0, 0, 0, 0, F(1), 5, 2, False]
        for index, value in ((0, 5), (1, 5), (2, -1), (3, 5), (5, 1), (5, 2**127), (6, 0), (6, 17)):
            args = base[:]
            args[index] = value
            with self.assertRaises(ValueError):
                R.carry_update(*args)
        with self.assertRaisesRegex(ValueError, "nonunit"):
            R.carry_update(0, 0, 0, 0, F(1, 5), 5, 2, False)
        with self.assertRaisesRegex(ValueError, "nonunit"):
            R.carry_update(0, 0, 0, 0, F(0), 5, 2, True)
        with self.assertRaisesRegex(ValueError, "coefficient capacity"):
            R.carry_update(0, 0, 0, 0, F(2**16), 5, 2, False)
        with self.assertRaisesRegex(ValueError, "rational coefficient"):
            R.carry_update(0, 0, 0, 0, 0.5, 5, 2, False)
        q = 2**127 - 1
        modulus = q**16
        x, y = modulus - 2, modulus - 1
        low, high = R.carry_update(y % q, y // q, x % q, x // q, F(1, 2), q, 16, False)
        self.assertEqual(low + q * high, (y + pow(2, -1, modulus) * x) % modulus)

    def test_noncommuting_column_orientation(self):
        program = [("add", 0, 1, F(1, 2)), ("add", 1, 2, F(-2))]
        axes = list(range(15))
        matrix = V.program_matrix(program)
        self.assertEqual(matrix[1][0], F(1, 2))
        self.assertEqual(matrix[2][1], F(-2))
        self.assertEqual(matrix[2][0], 0)
        self.assertNotEqual(V.program_matrix(list(reversed(program))), matrix)
        V.check_case(matrix, program, 5, 3, axes)


class RouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = V.authenticated_inputs()
        cls.matrix, cls.program = V.selected_route(cls.data)

    def test_fixed_route_and_receipt(self):
        actual = V.receipt(self.data)
        self.assertEqual(actual, json.loads((HERE / "RESULT.json").read_text()))
        self.assertEqual(actual["elementary_column_factors"], 77)
        self.assertEqual(actual["row_field_steps_per_route"], 4928)
        self.assertEqual(actual["omitted_factor_controls"], 77)
        self.assertEqual(len(actual["cases"]), 24)

    def test_low_and_restoration_checks_can_miss_carry_fault(self):
        witness = V.carry_omission_control(self.matrix)
        self.assertEqual((witness["q"], witness["width"], witness["stage"]), (5, 2, 8))
        self.assertEqual(witness["active_input_row"], [1, 17, 6, 20, 9, 23, 12, 1, 1, 15, 4, 18, 7, 21, 10])
        self.assertEqual((witness["row"], witness["column"], witness["uncarried_entry"],
                          witness["correct_entry"]), (0, 6, 19, 14))
        self.assertTrue(witness["low_residues_correct"])
        self.assertTrue(witness["two_applications_restore"])
        self.assertFalse(witness["full_right_product_correct"])

    def test_arbitrary_spectators_and_inactive_columns(self):
        axes = list(range(8)) + list(range(57, 64))
        fields = V.split_fields(V.fixture(5, 3), 5)
        first = R.route_fields(fields, self.program, axes, 5, 3)
        for name in ("ancestors", "role_type", "unused_child_stock", "head_data", "spectators"):
            changed = copy.deepcopy(fields)
            changed[name] = ("different arbitrary dirt", 1234567)
            second = R.route_fields(changed, self.program, axes, 5, 3)
            self.assertEqual(second["current_low"], first["current_low"])
            self.assertEqual(second["current_high"], first["current_high"])
            self.assertEqual(second[name], changed[name])
        for i in range(64):
            for j in range(8, 57):
                self.assertEqual(first["current_low"][i][j], fields["current_low"][i][j])
                self.assertEqual(first["current_high"][i][j], fields["current_high"][i][j])

    def test_invalid_route_contracts(self):
        fields = V.split_fields(V.fixture(5, 2), 5)
        for program, axes in ((self.program, [0] * 15),
                               ([("read_child_stock", 0, 1, F(1))], list(range(15))),
                               ([("add", 0, 0, F(1))], list(range(15))),
                               ([("add", 15, 0, F(1))], list(range(15)))):
            with self.assertRaises(ValueError):
                R.route_fields(fields, program, axes, 5, 2)
        bad = copy.deepcopy(fields)
        bad["current_high"][0][0] = 5
        with self.assertRaisesRegex(ValueError, "high matrix range"):
            R.route_fields(bad, self.program, list(range(15)), 5, 2)
        with self.assertRaisesRegex(ValueError, "singular"):
            R.column_program([[F(0)]])
        with self.assertRaisesRegex(ValueError, "program/field capacity"):
            R.route_fields(fields, [("swap", 0, 1, F(1))] * 241, list(range(15)), 5, 2)
        bad = {**fields, "current_low": [[]] * 65}
        with self.assertRaisesRegex(ValueError, "ambient rows"):
            R.route_fields(bad, self.program, list(range(15)), 5, 2)

    def test_detached_selected_binding(self):
        for key, value in (("pr", 555), ("git_blob_sha1", "0" * 40)):
            data = dict(self.data)
            assembly = json.loads(data[V.ASSEMBLY])
            assembly["bit_supplier"][key] = value
            data[V.ASSEMBLY] = json.dumps(assembly).encode()
            with self.assertRaises(ValueError):
                V.selected_route(data)

    def test_each_source_corruption_rejected(self):
        manifest = json.loads((HERE / "SOURCES.json").read_text())
        for item in manifest["files"]:
            if item["usage"] != "input":
                continue
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for name, payload in self.data.items():
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(payload + b"corrupt" if name == item["path"] else payload)
                with self.assertRaisesRegex(ValueError, "source hash"):
                    V.authenticated_inputs(root)

    def test_optimized_cli_receipt_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory)
            root = checkout / "research" / HERE.name
            root.mkdir(parents=True)
            for path in HERE.glob("*.py"):
                (root / path.name).write_bytes(path.read_bytes())
            for name, payload in self.data.items():
                path = checkout / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            (root / "SOURCES.json").write_bytes((HERE / "SOURCES.json").read_bytes())
            command = [sys.executable, "-I", "-O", "-B", str(root / "verify.py")]
            missing = subprocess.run(command, capture_output=True, timeout=15)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn(b"RESULT.json", missing.stderr)
            (root / "RESULT.json").write_text("{}")
            wrong = subprocess.run(command, capture_output=True, timeout=15)
            self.assertNotEqual(wrong.returncode, 0)
            self.assertIn(b"required result mismatch", wrong.stderr)
            target = root / "existing.json"
            target.write_text("preserve me")
            overwrite = subprocess.run(command + ["--write-result", str(target)], capture_output=True, timeout=15)
            self.assertNotEqual(overwrite.returncode, 0)
            self.assertEqual(target.read_text(), "preserve me")


if __name__ == "__main__":
    unittest.main()
