"""Independent arithmetic evaluations and fail-closed audit-harness tests.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import product
from math import gcd
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify
from laurent import Ring


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.compiler = verify.sources()

    def test_exact_algebra_against_all_unit_pairs(self):
        cases = 0
        for modulus in (9, 25):
            r = Ring(modulus)
            x, y = r.variable(0), r.variable(1)
            p = r.add(r.mul(3, r.mul(r.inv(x), y)), r.mul(5, r.mul(x, x)))
            q = r.add(r.mul(-1, y), r.scalar(2))
            for a, b in product((i for i in range(modulus) if gcd(i, modulus) == 1), repeat=2):
                expected_p = (3*pow(a, -1, modulus)*b + 5*a*a) % modulus
                expected_q = (2-b) % modulus
                self.assertEqual(r.evaluate(p, (a, b)), expected_p)
                self.assertEqual(r.evaluate(r.add(p, q), (a, b)), (expected_p+expected_q) % modulus)
                self.assertEqual(r.evaluate(r.mul(p, q), (a, b)), expected_p*expected_q % modulus)
                cases += 1
        self.assertEqual(cases, 436)

    def test_zero_divisors_and_canonical_cancellation(self):
        r = Ring(9)
        x = r.variable(0)
        self.assertEqual(r.mul(r.mul(3, x), r.mul(3, r.inv(x))), {})
        self.assertEqual(r.mul(x, r.inv(x)), r.scalar(1))
        self.assertEqual(r.add(x, r.mul(-1, x)), {})
        with self.assertRaisesRegex(ValueError, "nonunit coefficient"):
            r.inv(r.mul(3, x))
        with self.assertRaisesRegex(ValueError, "one unit monomial"):
            r.inv(r.add(x, r.scalar(1)))
        with self.assertRaisesRegex(ValueError, "unit weights"):
            r.evaluate(x, (3,))

    def test_actual_bank_read_boundary(self):
        m, f, modulus = 64, 3, 25
        calls = []
        units = [i for i in range(modulus) if gcd(i, modulus) == 1]
        def value(index):
            calls.append(index)
            return units[index % len(units)]
        prepared = SimpleNamespace(dimension=m, columns=f, modulus=modulus,
                                   weights=SimpleNamespace(value=value),
                                   arithmetic=SimpleNamespace(counts=verify.Counter()))
        for row in range(2*m):
            for col in range(f):
                got = self.compiler.bank_weight(prepared, row, col)
                self.assertEqual(got, units[(row*f+col) % len(units)] if row < m else 1)
        self.assertEqual(calls, list(range(m*f)))

    def test_instrumented_coefficients_match_numeric_evaluator(self):
        compiler = self.compiler
        matrix = [[3, 2, 0, 0], [1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        plan = compiler.elimination(matrix, 9)
        operations = compiler.compile_program(plan)
        units = (1, 2, 4, 5, 7, 8)
        r = Ring(9)
        symbolic = SimpleNamespace(plan=plan, arithmetic=r, modulus=9)
        expressions = []
        with verify.symbolic_reads(compiler, 2, 1, r):
            for op in operations:
                expressions.append(r.coerce(compiler.coefficient(symbolic, op.coefficient, 0)))
        arithmetic = compiler.Arithmetic(9)
        for assignment in product(units, repeat=2):
            numeric = SimpleNamespace(plan=plan, arithmetic=arithmetic, dimension=2, columns=1,
                                      modulus=9, weights=SimpleNamespace(value=assignment.__getitem__))
            for op, expression in zip(operations, expressions):
                self.assertEqual(compiler.coefficient(numeric, op.coefficient, 0),
                                 r.evaluate(expression, assignment))

    def test_bank_instrumentation_restored_after_exception(self):
        original = self.compiler.bank_weight
        with self.assertRaisesRegex(ValueError, "sentinel"):
            with verify.symbolic_reads(self.compiler, 2, 1, Ring(9)):
                raise ValueError("sentinel")
        self.assertIs(self.compiler.bank_weight, original)

    def test_selected_binding_rejects_wrong_copy(self):
        import gzip
        import json
        from hashlib import sha256
        data = dict(self.data)
        base = "research/community-hyperplane599-audit/pr589/bit589/v9/hosted/"
        template = json.loads(gzip.decompress(data[base+"GLOBAL-TEMPLATE.json.gz"]))
        template["hosting"]["slots"].append([6, 213])
        decoded = json.dumps(template).encode()
        data[base+"GLOBAL-TEMPLATE.json.gz"] = gzip.compress(decoded)
        receipt = json.loads(data[base+"GLOBAL.json"])
        receipt["template_sha256"] = sha256(decoded).hexdigest()
        data[base+"GLOBAL.json"] = json.dumps(receipt).encode()
        with self.assertRaisesRegex(ValueError, "unhosted copy"):
            verify.selected_binding(data)

    def test_rejection_must_have_the_expected_cause(self):
        def unrelated():
            raise ValueError("unrelated fixture failure")
        with self.assertRaisesRegex(ValueError, "wrong rejection"):
            verify.reject(unrelated, "test", "symbolic endpoint mismatch")
        with self.assertRaisesRegex(ValueError, "negative control passed"):
            verify.reject(lambda: None, "test", "symbolic endpoint mismatch")

    def test_weight_fault_invisible_at_unit_assignment(self):
        r = Ring(25)
        weight = r.mul(7, r.mul(r.variable(0), r.inv(r.variable(1))))
        lost_weight = r.scalar(7)
        self.assertNotEqual(weight, lost_weight)
        self.assertEqual(r.evaluate(weight, (1, 1)), r.evaluate(lost_weight, (1, 1)))
        self.assertNotEqual(r.evaluate(weight, (2, 1)), r.evaluate(lost_weight, (2, 1)))


if __name__ == "__main__":
    unittest.main()
