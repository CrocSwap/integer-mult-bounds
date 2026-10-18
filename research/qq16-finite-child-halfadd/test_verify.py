#!/usr/bin/env python3
"""Behavioral controls and a separate finite binary64 execution. Apache-2.0."""

import unittest
from fractions import Fraction as Q

import verify as V


def oracle(n, p):
    if abs(n) < 1 << p:
        return n
    magnitude = abs(n)
    candidates = [
        (abs(m * (1 << e) - magnitude), m % 2, m * (1 << e))
        for e in range(12)
        for m in range(1 << (p - 1), 1 << p)
    ]
    out = min(candidates)[2]
    return -out if n < 0 else out


def binary64(source, destination, recipe):
    right, left = V.table(recipe["right"]), V.table(recipe["left"])
    a, b, out = [(0.0, 0.0)] * 512, [(0.0, 0.0)] * 512, [(0.0, 0.0)] * 512
    for i, (dest, phase) in enumerate(right):
        a[dest] = V.rotate(float(source[i][0]), float(source[i][1]), phase)
    for i in range(0, 512, 2):
        ar, ai = a[i]
        br, bi = a[i + 1]
        sr, si, dr, di = ar + br, ai + bi, ar - br, ai - bi
        b[i] = ((sr - di) * 0.5, (si + dr) * 0.5)
        b[i + 1] = ((sr + di) * 0.5, (si - dr) * 0.5)
    for i, (dest, phase) in enumerate(left):
        out[dest] = V.rotate(*b[i], phase)
    added = [
        (float(a) - c * 0.5, float(b) - d * 0.5)
        for (a, b), (c, d) in zip(destination, out, strict=True)
    ]
    return out, added


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events, cls.recipes = V.load()

    def test_rounding_separate_enumeration(self):
        for p in range(2, 7):
            for n in range(-512, 513):
                self.assertEqual(V.nearest(n, p), oracle(n, p))

    def test_binary64_actual_rounding(self):
        top = 1 << 52
        source = [(4 * (top + i * 37), -4 * (top + i * 19)) for i in range(512)]
        destination = list(reversed(source))
        for recipe in self.recipes:
            native, added = binary64(source, destination, recipe)
            actual = V.run(source.copy(), destination.copy(), recipe, 53, 56)
            self.assertEqual(actual[:2], (native, added))
            self.assertGreater(actual[2]["native_nonzero_rounds"], 0)

    def test_zero_and_cancellation(self):
        zero = [(0, 0)] * 512
        source = [(4, -4)] * 512
        for recipe in self.recipes:
            out, added, counts = V.run(zero.copy(), zero.copy(), recipe, 2, 1)
            self.assertEqual((out, added), (zero, zero))
            self.assertEqual(counts["nonzero_rounds"], 0)
            ideal, _ = V.exact(source, zero, recipe)
            self.assertEqual(V.norm2(ideal), V.norm2(source))

    def test_complete_small_pair_domain(self):
        # The native butterfly is the only mixing arithmetic; exhaust a complex pair.
        for a in range(-2, 3):
            for b in range(-2, 3):
                for c in range(-2, 3):
                    for d in range(-2, 3):
                        pair = [V.nearest(n, 2) for n in (a + c, b + d, a - c, b - d)]
                        sr, si, dr, di = pair
                        out = [
                            Q(V.nearest(n, 2), 2)
                            for n in (sr - di, si + dr, sr + di, si - dr)
                        ]
                        exact = [
                            Q(n, 2)
                            for n in (
                                a - b + c + d,
                                b + a + d - c,
                                c - d + a + b,
                                d + c + b - a,
                            )
                        ]
                        error = sum(
                            (x - y) ** 2 for x, y in zip(out, exact, strict=True)
                        )
                        self.assertLessEqual(
                            error, Q(9, 16) ** 2 * (a * a + b * b + c * c + d * d)
                        )

    def test_entry_rejections(self):
        zero = [(0, 0)] * 512
        for precision, span, value in (
            (1, 1, zero),
            (4097, 1, zero),
            (2, 0, zero),
            (2, 2049, zero),
            (2, 1, [(1, 0)] * 512),
            (2, 1, [(8, 0)] * 512),
            (2, 8, [(28, 0)] * 512),
        ):
            with self.assertRaises(ValueError):
                V.run(value, zero, self.recipes[0], precision, span)
        with self.assertRaises(ValueError):
            V.run(zero, zero, self.recipes[0], 2, 1)

    def test_phase_and_half_coefficient_controls(self):
        source, dest = [(0, 0)] * 512, [(0, 0)] * 512
        source[7] = (4, 0)
        correct, added, _ = V.run(source.copy(), dest.copy(), self.recipes[0], 53, 3)
        mutated = dict(self.recipes[0])
        mutated["left"] = dict(
            mutated["left"], phase=(mutated["left"]["phase"] + 1) % 4
        )
        wrong, _, _ = V.run(source.copy(), dest.copy(), mutated, 53, 3)
        self.assertNotEqual(correct, wrong)
        unit_add = [(-a, -b) for a, b in correct]
        self.assertNotEqual(added, unit_add)
        self.assertEqual(self.events[13491][1][-2:], [-1, 1])
        self.assertEqual(self.events[11796][1][-2:], [-1, 2])


if __name__ == "__main__":
    unittest.main()
