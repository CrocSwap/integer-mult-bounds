#!/usr/bin/env python3
"""Bounded exact checks for the opt-in exponential interval kernel.

Run from any directory: python3 research/exact-exp-performance/test_exp.py
Stephan Arrington, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from decimal import Decimal
import hashlib
import importlib.util
from math import factorial
from pathlib import Path
import random
import unittest

from fast_exp import D, exp


REFERENCE = (
    Path(__file__).resolve().parents[1]
    / "complex-k492-owner-repair/extras/exact_intervals.py"
)
REFERENCE_SHA256 = "aa3c2327c5d3742248b720a87b2de0bbe2e34ed2af89a578e3c8d5bd2656a9cf"
RANDOM_SEED = 91
RANDOM_CASES = 480


def load_reference():
    actual = hashlib.sha256(REFERENCE.read_bytes()).hexdigest()
    if actual != REFERENCE_SHA256:
        raise ValueError(f"reference source pin mismatch: {actual}")
    spec = importlib.util.spec_from_file_location("pinned_exact_intervals", REFERENCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.exp


def polynomial(x, degree=16):
    """Independent direct power/factorial sum; no homogeneous evaluation."""
    return sum((x ** j / factorial(j) for j in range(degree + 1)), Q(0))


def remainder(x, degree=16, ratio_denominator=None):
    r = degree + 2 if ratio_denominator is None else ratio_denominator
    return x ** (degree + 1) / (factorial(degree + 1) * (1 - x / r))


def floor_grid(x):
    whole, _ = divmod(x.numerator * D, x.denominator)
    return Q(whole, D)


def ceil_grid(x):
    whole, residual = divmod(x.numerator * D, x.denominator)
    return Q(whole + bool(residual), D)


def direct_oracle(a, b):
    return floor_grid(polynomial(a)), ceil_grid(polynomial(b) + remainder(b))


def random_cases():
    rng = random.Random(RANDOM_SEED)
    # Includes denominators far beyond floating point precision and the
    # rounding grid, while keeping this regression suite comfortably bounded.
    widths = (2, 7, 17, 53, 64, 127, 200, 257, 521, 1024)
    for i in range(RANDOM_CASES):
        bits = widths[i % len(widths)]
        denominator_a = rng.randrange(1 << (bits - 1), 1 << bits)
        denominator_b = rng.randrange(1 << (bits - 1), 1 << bits)
        a = Q(rng.randrange(denominator_a), denominator_a)
        b = Q(rng.randrange(denominator_b), denominator_b)
        yield min(a, b), max(a, b)


def boundary_cases():
    points = {
        Q(0), Q(1, 2), Q(1, 3), Q(2, 3), Q(17, 18), Q(18, 19),
        Q(1, D * D), Q(1, D), Q(2, D), Q(D - 1, D),
        Q(D * D - 1, D * D), Q(10 ** 100 - 1, 10 ** 100),
        Q(1, 10 ** 100), Q((1 << 1024) - 1, 1 << 1024),
    }
    for denominator in (3, 7, 17, 19, 101, 65537):
        points.update((Q(1, denominator), Q(denominator - 1, denominator)))
    ordered = sorted(points)
    for i, a in enumerate(ordered):
        for b in ordered[i:]:
            yield a, b


class ExactExpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = staticmethod(load_reference())

    def assert_exact(self, candidate, cases):
        for a, b in cases:
            with self.subTest(a=a, b=b):
                expected = self.reference(a, b)
                self.assertEqual(candidate(a, b), expected)

    def test_reference_pin_and_boundary_differential(self):
        self.assertEqual(D, 1 << 200)
        self.assert_exact(exp, boundary_cases())

    def test_seeded_rational_differential(self):
        self.assert_exact(exp, random_cases())

    def test_independent_direct_power_oracle(self):
        # This second oracle uses powers and factorials, rather than either
        # reference term recurrence or candidate homogeneous integer recurrence.
        cases = [(Q(i, 64), Q(j, 64)) for i in range(0, 64, 7)
                 for j in range(i, 64, 11)]
        cases += list(random_cases())[::12]
        for a, b in cases:
            with self.subTest(a=a, b=b):
                self.assertEqual(exp(a, b), direct_oracle(a, b))

    def test_exact_rounding_obligations(self):
        for a, b in list(boundary_cases())[::7]:
            low, high = exp(a, b)
            unrounded_low = polynomial(a)
            unrounded_high = polynomial(b) + remainder(b)
            self.assertLessEqual(low, unrounded_low)
            self.assertLess(unrounded_low - low, Q(1, D))
            self.assertGreaterEqual(high, unrounded_high)
            self.assertLess(high - unrounded_high, Q(1, D))
            self.assertEqual(D % low.denominator, 0)
            self.assertEqual(D % high.denominator, 0)

    def test_higher_order_certified_enclosures(self):
        # Positive Taylor terms give P_64 <= exp(x); the geometric tail gives
        # exp(x) <= P_64 + R_64. The candidate interval encloses both bounds.
        points = [Q(i, 64) for i in range(64)]
        points += [Q(1, D * D), Q(D * D - 1, D * D)]
        previous = None
        for x in points:
            low, high = exp(x, x)
            tighter_low = polynomial(x, 64)
            tighter_high = tighter_low + remainder(x, 64)
            self.assertLessEqual(low, tighter_low)
            self.assertGreaterEqual(high, tighter_high)
            self.assertLessEqual(low, high)
            # Only the initial sorted grid participates in monotonicity.
            if x.denominator <= 64:
                if previous is not None:
                    self.assertLessEqual(previous[0], low)
                    self.assertLessEqual(previous[1], high)
                previous = low, high

    def test_invalid_domains_rejected(self):
        invalid = [
            (Q(-1), Q(0)), (Q(-1, D * D), Q(0)),
            (Q(0), Q(1)), (Q(1), Q(1)), (Q(0), Q(2)),
            (Q(2, 3), Q(1, 3)), (Q(1, D), Q(1, D * D)),
        ]
        for a, b in invalid:
            with self.subTest(a=a, b=b):
                with self.assertRaises(ValueError):
                    exp(a, b)
                with self.assertRaises(ValueError):
                    self.reference(a, b)

    def test_input_contract(self):
        self.assertEqual(exp(Q(0), Q(0)), (Q(1), Q(1)))
        for a, b in [(0, Q(0)), (Q(0), 0), (False, Q(0)),
                     (0.0, Q(1, 2)), (Q(0), 0.5), ("0", Q(0)),
                     (Decimal(0), Q(0)),
                     (Q(0), None), (complex(0), Q(0))]:
            with self.subTest(a=a, b=b):
                with self.assertRaises(TypeError):
                    exp(a, b)

    def test_negative_control_omitted_polynomial_term(self):
        x = Q(1, 2)
        mutant = floor_grid(polynomial(x, 15)), ceil_grid(polynomial(x) + remainder(x))
        self.assertNotEqual(mutant, self.reference(x, x))
        # The missing term is large enough to remain detectable after rounding.
        self.assertGreater(polynomial(x) - polynomial(x, 15), Q(1, D))

    def test_negative_controls_tail(self):
        x = Q(1, 2)
        certified_lower = polynomial(x, 64)
        correct = self.reference(x, x)
        for bad_tail in (Q(0), remainder(x, ratio_denominator=19)):
            mutant = floor_grid(polynomial(x)), ceil_grid(polynomial(x) + bad_tail)
            self.assertNotEqual(mutant, correct)
            # These are genuine under-enclosures of exp(x), witnessed with
            # exact rationals rather than a floating point exp implementation.
            self.assertLess(mutant[1], certified_lower)

    def test_negative_controls_inward_rounding(self):
        x = Q(1, D * D)
        unrounded_low = polynomial(x)
        unrounded_high = unrounded_low + remainder(x)
        certified_lower = polynomial(x, 64)
        certified_upper = certified_lower + remainder(x, 64)
        correct = self.reference(x, x)
        upward_low = ceil_grid(unrounded_low), ceil_grid(unrounded_high)
        downward_high = floor_grid(unrounded_low), floor_grid(unrounded_high)
        self.assertNotEqual(upward_low, correct)
        self.assertNotEqual(downward_high, correct)
        self.assertGreater(upward_low[0], certified_upper)
        self.assertLess(downward_high[1], certified_lower)


if __name__ == "__main__":
    print(f"reference sha256: {REFERENCE_SHA256}")
    print(f"exact differential cases: {len(list(boundary_cases()))} boundary + "
          f"{RANDOM_CASES} random (seed {RANDOM_SEED})")
    print("negative controls: omitted term; omitted/wrong tail; inward lower/upper rounding")
    unittest.main(verbosity=2)
