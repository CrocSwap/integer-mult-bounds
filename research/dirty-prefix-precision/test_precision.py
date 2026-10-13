"""Boundary budgets and nonlinear perturbations; Apache-2.0.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance.
"""
import importlib.util
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('core', HERE/'core.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class PrecisionTests(unittest.TestCase):
    def test_exact_logarithm_boundaries(self):
        for exponent in range(-100, 101):
            power = Q(2)**exponent
            self.assertEqual(c.ceil_log2(power), exponent)
            self.assertEqual(c.ceil_log2(power*(1-Q(1, 2**20))), exponent)
            self.assertEqual(c.ceil_log2(power*(1+Q(1, 2**20))), exponent+1)

    def test_finer_input_grid_is_preserved(self):
        coarse = c.working_bits(2, Q(1), Q(1), Q(2), 8)
        self.assertLess(coarse, 1000)
        self.assertEqual(c.working_bits(2, Q(1), Q(1), Q(2), 8, 1000), 1000)

    def test_feedback_boundary(self):
        self.assertEqual(c.execution_parameters(1, 1, 1, 0, 3)['feedback'], Q(1, 2))
        with self.assertRaisesRegex(ValueError, 'feedback smallness'):
            c.execution_parameters(1, 1, 1, 0, 2)

    def test_nonlinear_leaf_errors_and_exact_dirty_inverse(self):
        cases = 0
        for n in (2, 3, 5, 8):
            h, _, _ = c.resources(n)
            factors = [Q(2) if i%2 == 0 else Q(-1, 2) for i in range(n)]
            for dirt in (-7, 11):
                original = [Q(1, 2), Q(3, 8)]+[Q(dirt+j, 4) for j in range(h)]
                D = max(map(abs, original))
                bits = c.working_bits(n, 2, 1, D, 8, 3)
                u = Q(1, 2**bits)
                bound = c.execution_parameters(n, 2, 1, D, bits)
                values = original[:]

                def run(sign):
                    peak = max(map(abs, values))
                    for source, target, index, q in c.word(n, sign):
                        z = values[source]
                        error = (-1)**index*u*(abs(z)+1)
                        values[target] += q*(factors[index]*z+error)
                        peak = max(peak, max(map(abs, values)))
                    return peak

                peak = run(1)
                expected = original[0]
                for factor in factors:
                    expected *= factor
                actual_error = abs(values[1]-original[1]-expected)
                self.assertLessEqual(actual_error, bound['error_bound'])
                self.assertLessEqual(peak, bound['magnitude_bound'])
                self.assertEqual(values[:1]+values[2:], original[:1]+original[2:])
                run(-1)
                self.assertEqual(values, original)
                cases += 1
        self.assertEqual(cases, 8)


if __name__ == '__main__':
    unittest.main()
