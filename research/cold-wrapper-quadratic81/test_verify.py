"""Check the symbolic compiler against direct finite phase arithmetic."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('quadratic81', HERE / 'verify.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def affine_value(form, assignment):
    return ((form & assignment).bit_count() + int(bool(form & check.CONSTANT))) % 2


def polynomial_value(polynomial, assignment):
    return sum(coefficient for mask, coefficient in polynomial.items()
               if assignment & mask == mask) % 4


def direct_map(rows, x, offset=0):
    return sum(((row & x).bit_count() % 2) * (2 ** i) for i, row in enumerate(rows)) ^ offset


def direct_phase(q, alpha, x, constant=0):
    value = constant
    for i in range(9):
        if x & (2 ** i):
            value += alpha[i]
            for j in range(i + 1, 9):
                if x & (2 ** j) and q[i] & (2 ** j):
                    value += 2
    return value % 4


class SymbolicChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.instance, _ = check.load_instance()
        cls.recipe = cls.instance['recipe']
        cls.certificate = check.derive(cls.recipe)

    def test_xor_lift_on_all_used_forms_and_assignments(self):
        right = self.recipe['right']
        z = check.linear_map(right['matrix_rows'], check.X, right['offset'])
        z = [f ^ (check.DELTA[i] if i < 4 else 0) for i, f in enumerate(z)]
        forms = set(check.X + check.DELTA + z + self.certificate['output_forms']
                    + self.certificate['kernel_difference_forms'])
        # Also exercise the constant and its interaction with every coordinate.
        forms |= {0, check.CONSTANT, (2 ** 13) - 1, (2 ** 14) - 1}
        forms |= {f ^ check.CONSTANT for f in list(forms)}
        for form in forms:
            polynomial = check.lift(form)
            for assignment in range(2 ** 13):
                self.assertEqual(polynomial_value(polynomial, assignment),
                                 affine_value(form, assignment), (form, assignment))

    def test_all_six_phase_components_by_direct_arithmetic(self):
        left, right = self.recipe['left'], self.recipe['right']
        _, inverse, q, alpha = check.canonical_geometry(self.recipe['terminal_vectors'])
        for assignment in range(2 ** 13):
            x, delta = assignment & 511, assignment >> 9
            z = direct_map(right['matrix_rows'], x, right['offset']) ^ delta
            y = direct_map(left['matrix_rows'], z, left['offset'])
            c = direct_map(inverse, x ^ y)
            self.assertEqual(c >> 4, 0)
            self.assertEqual(y, sum(affine_value(f, assignment) * (2 ** i)
                                    for i, f in enumerate(self.certificate['output_forms'])))
            expected = {
                'right_phase_x': direct_phase(right['quadratic_rows'], right['linear_Z4'], x, right['phase']),
                'left_phase_z': direct_phase(left['quadratic_rows'], left['linear_Z4'], z, left['phase']),
                'minus_delta_weight': -delta.bit_count() % 4,
                'minus_canonical_phase_y': -direct_phase(q, alpha, y) % 4,
                'canonical_phase_x': direct_phase(q, alpha, x),
                'canonical_difference_weight': c.bit_count() % 4,
            }
            for name, value in expected.items():
                self.assertEqual(polynomial_value(self.certificate['components'][name], assignment),
                                 value, (name, assignment))
            self.assertEqual(sum(expected.values()) % 4, 0)

    def test_corrupt_symbolic_coefficient_has_concrete_witness(self):
        for mask in [0] + [2 ** i for i in range(13)] + [(2 ** i) | (2 ** j) for i in range(13) for j in range(i + 1, 13)]:
            for coefficient in (1, 2, 3):
                witness = check.witness({mask: coefficient})
                self.assertEqual(polynomial_value({mask: coefficient}, witness['assignment_mask']), coefficient)

    def test_each_recorded_phase_counterexample_is_nonzero(self):
        controls = check.controls(self.recipe)
        self.assertEqual(len(controls), 13)
        for control in controls:
            if 'counterexample' in control:
                self.assertIn(control['counterexample']['phase_error_mod4'], (1, 2, 3))

    def test_optimized_fresh_process(self):
        completed = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE / 'verify.py')],
                                   cwd='/tmp', capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn('PASS_COLD_WRAPPER_QUADRATIC_CERTIFICATE', completed.stdout)


if __name__ == '__main__':
    unittest.main()
