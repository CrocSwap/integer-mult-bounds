"""Arithmetic, dirt, failure and binding controls for the opt-in kernels.

Sricharan Vagvala, substantial OpenAI Codex assistance. Apache-2.0.
"""

from copy import deepcopy
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import random
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fast_rows import accelerated, normal_row, sum_rows
from support import HERE, PREDECESSOR, ROOT, check_pins, load_module, module_aliases


class FastRowsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = load_module("ck917_test_reference", PREDECESSOR / "independent.py")

    def test_exhaustive_signed_normalization(self):
        for a, b, exponent in product(range(-4, 5), range(-4, 5), range(9)):
            terms = {0: a, 1: b}
            original = terms.copy()
            self.assertEqual(normal_row(terms, exponent), self.reference._normal_row(terms, exponent))
            self.assertEqual(terms, original)
        self.assertEqual(normal_row({0: -(1 << 200), 1: 1 << 225}, 240),
                         ({0: -1, 1: 1 << 25}, 40))

    def test_exhaustive_addition_and_immutability(self):
        rows = [self.reference._normal_row({0: a, 1: b}, exponent)
                for a, b, exponent in product(range(-4, 5), range(-4, 5), range(5))]
        for left, right, sign in product(rows, rows, (-1, 1)):
            snapshot = deepcopy((left, right))
            self.assertEqual(sum_rows(left, right, sign), self.reference._sum_rows(left, right, sign))
            self.assertEqual((left, right), snapshot)
        for exponent in (0, 1, 8, 64, 256):
            left, right = ({0: -3, 2: 5}, exponent), ({0: 7, 1: -1}, 0)
            for sign in (-1, 1):
                result, power = sum_rows(left, right, sign)
                expected = {column: Fraction(left[0].get(column, 0), 1 << exponent)
                            + sign * Fraction(right[0].get(column, 0)) for column in range(3)}
                self.assertEqual({column: Fraction(result.get(column, 0), 1 << power)
                                  for column in range(3)}, expected)
            self.assertEqual(sum_rows(left, left, -1), ({}, 0))

    def test_seed89_fraction_primitive_oracle(self):
        rng = random.Random(89)
        refs = [("L", i) for i in range(12)] + [("C", i) for i in range(3)] + [("W", 0)]
        rows = {ref: {i: Fraction(1)} for i, ref in enumerate(refs)}
        envelope = {ref: Fraction(1) for ref in refs}
        peak, first_peak, maximum_power = Fraction(1), -1, 0
        program = []
        for index in range(3000):
            operation = rng.choice(("clear", "copy", "add", "double", "halve", "negate"))
            target, source = rng.sample(refs, 2)
            instruction = [operation, list(target)]
            if operation == "clear":
                rows[target], envelope[target] = {}, Fraction(0)
            elif operation == "copy":
                instruction.append(list(source))
                rows[target], envelope[target] = rows[source].copy(), envelope[source]
            elif operation == "add":
                sign = rng.choice((-1, 1))
                instruction.extend((list(source), sign))
                result = rows[target].copy()
                for column, value in rows[source].items():
                    result[column] = result.get(column, 0) + sign * value
                rows[target] = {column: value for column, value in result.items() if value}
                envelope[target] += envelope[source]
            else:
                factor = {"double": Fraction(2), "halve": Fraction(1, 2), "negate": Fraction(-1)}[operation]
                rows[target] = {column: value * factor for column, value in rows[target].items()}
                envelope[target] *= abs(factor)
            if envelope[target] > peak:
                peak, first_peak = envelope[target], index
            maximum_power = max(maximum_power, max((value.denominator.bit_length() - 1
                                for value in rows[target].values()), default=0))
            program.append(instruction)
        module = load_module("ck917_test_fast", PREDECESSOR / "independent.py")
        with accelerated(module):
            result = module.replay(program, n=12, centers=3)
        for ref, expected in rows.items():
            row = result["endpoint"][ref[0]][ref[1]]
            self.assertEqual({column: Fraction(value, 1 << row["denominator_power"])
                              for column, value in row["terms"]}, expected)
        actual_peak = result["positive_prefix"]
        self.assertEqual(Fraction(actual_peak["numerator"], 1 << actual_peak["denominator_power"]), peak)
        self.assertEqual(actual_peak["first_maximum_instruction"], first_peak)
        self.assertEqual(result["maximum_denominator_power"], maximum_power)

    def test_inherited_arithmetic_and_fault_controls(self):
        module = load_module("ck917_inherited_fast", PREDECESSOR / "independent.py")
        with module_aliases(independent=module), accelerated(module):
            inherited = load_module("ck917_inherited_tests", PREDECESSOR / "test_independent.py")
            result = unittest.TestResult()
            unittest.defaultTestLoader.loadTestsFromModule(inherited).run(result)
        self.assertEqual(result.testsRun, 6)
        self.assertEqual(result.errors + result.failures, [])

    def test_context_restores_after_exception(self):
        module = load_module("ck917_restore", PREDECESSOR / "independent.py")
        original = module._normal_row, module._sum_rows
        with self.assertRaisesRegex(RuntimeError, "deliberate"):
            with accelerated(module):
                self.assertIs(module._sum_rows, sum_rows)
                raise RuntimeError("deliberate")
        self.assertEqual((module._normal_row, module._sum_rows), original)

    def test_copy_aliasing_cancellation_and_transient_precision(self):
        module = load_module("ck917_copy", PREDECESSOR / "independent.py")
        program = [["copy", ["W", 0], ["L", 0]], ["halve", ["L", 0]],
                   ["add", ["L", 0], ["L", 1], 1], ["double", ["W", 0]],
                   ["halve", ["W", 0]], ["add", ["L", 1], ["W", 0], -1]]
        expected = module.replay(program, n=2, centers=0)
        with accelerated(module):
            self.assertEqual(module.replay(program, n=2, centers=0), expected)
        self.assertEqual(expected["maximum_denominator_power"], 1)
        self.assertEqual(expected["endpoint"]["W"][0]["terms"], [[0, 1]])

    def test_every_live_source_drift_is_rejected(self):
        sources = json.loads((HERE / "SOURCES.json").read_text())["files"]
        inputs = [row["path"] for row in sources if row["usage"] == "input"]
        with tempfile.TemporaryDirectory(prefix="ck-dyadic-pins-") as directory:
            root = Path(directory)
            for name in inputs:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, path)
            self.assertEqual(check_pins(root), inputs)
            for name in inputs:
                path = root / name
                original = path.read_bytes()
                path.write_bytes(original + b" ")
                with self.subTest(source=name), self.assertRaisesRegex(ValueError, "source pin mismatch"):
                    check_pins(root)
                path.write_bytes(original)
            (root / inputs[0]).unlink()
            with self.assertRaisesRegex(ValueError, "missing or symlinked input"):
                check_pins(root)


if __name__ == "__main__":
    unittest.main()
