#!/usr/bin/env python3
"""Finite exact corroboration, not a backend, tape model, or kappa certificate."""

from fractions import Fraction
from functools import lru_cache
import random


def need(condition, message):
    if not condition:
        raise ValueError(message)


def floor_root(value, degree):
    need(value >= 0 and degree >= 1, "root domain")
    if value < 2:
        return value
    low = 0
    high = 1 << ((value.bit_length() + degree - 1) // degree)
    while low + 1 < high:
        middle = (low + high) // 2
        if middle**degree <= value:
            low = middle
        else:
            high = middle
    return high if high**degree <= value else low


def ceil_root(value, degree):
    root = floor_root(value, degree)
    return root if root**degree == value else root + 1


@lru_cache(maxsize=None)
def power_interval(value, numerator, denominator):
    """Outward rational bounds for value**(numerator/denominator)."""
    need(value >= 1 and numerator >= 0 and denominator >= 1, "power domain")
    scale = 1 << 80
    radicand = value**numerator * scale**denominator
    root = floor_root(radicand, denominator)
    lower = Fraction(root, scale)
    upper = lower if root**denominator == radicand else Fraction(root + 1, scale)
    return lower, upper


def partition(rank, block):
    quotient, tail = divmod(rank, block)
    return [block] * quotient + ([tail] if tail else [])


def parameter_screen():
    cases = 0
    for p, q in [(1, 4), (1, 3), (1, 2), (2, 3), (3, 4)]:
        for rank in range(1, 257):
            for width in sorted({rank, rank + rank // 2, rank * rank}):
                block = min(rank, ceil_root(width**q, p + q))
                parts = partition(rank, block)
                count = len(parts)
                squares = sum(k * k for k in parts)
                need(sum(parts) == rank, "rank coverage")
                need(squares <= rank * block, "square bound")
                need(count * block < rank + block, "tail count")
                upper_sum = Fraction(0)
                for k in parts:
                    _, high = power_interval(k, q - p, q)
                    upper_sum += high
                _, block_power_high = power_interval(block, p, q)
                need(upper_sum <= Fraction(2 * rank, 1) / block_power_high,
                     "power upper bound")
                # This is the complete normalized logical invoice from the note.
                bill_upper = width * upper_sum + squares + (width + rank) * count
                if width**q <= rank**(p + q):
                    envelope_low, _ = power_interval(width, q, p + q)
                    need(bill_upper <= 8 * rank * envelope_low,
                         "intermediate-width envelope")
                else:
                    envelope_low, _ = power_interval(rank, q - p, q)
                    need(bill_upper <= 4 * width * envelope_low,
                         "wide envelope")
                cases += 1
    return cases


def direct_wrapper(x, rows, offset, linear, quadratic, phase):
    bits = [(x >> j) & 1 for j in range(len(rows))]
    y = offset
    for j, row in enumerate(rows):
        y ^= ((row & x).bit_count() & 1) << j
    phi = phase + sum(l * bit for l, bit in zip(linear, bits))
    for j in range(len(rows)):
        for k in range(j + 1, len(rows)):
            phi += 2 * quadratic[j][k] * bits[j] * bits[k]
    return y, phi % 4


def gray_screen():
    rng = random.Random(303301)
    columns_checked = 0
    omitted_update_faults = 0
    for n in range(1, 9):
        for recipe in range(4):
            rows = [1 << j for j in range(n)]
            if n > 1:
                for _ in range(3 * n):
                    j, k = rng.sample(range(n), 2)
                    rows[j] ^= rows[k]
            columns = [sum(((row >> j) & 1) << k for k, row in enumerate(rows))
                       for j in range(n)]
            offset = rng.randrange(1 << n)
            linear = [rng.randrange(4) for _ in range(n)]
            quadratic = [[0] * n for _ in range(n)]
            for j in range(n):
                for k in range(j + 1, n):
                    quadratic[j][k] = quadratic[k][j] = rng.randrange(2)
            if n > 1 and recipe == 0:
                quadratic[0][1] = quadratic[1][0] = 1
            phase = rng.randrange(4)
            x, y, phi = 0, offset, phase
            derivatives = list(linear)
            bad_phi = phase
            seen = set()
            for t in range(1 << n):
                expected = direct_wrapper(x, rows, offset, linear, quadratic, phase)
                need((y, phi) == expected, "Gray compiler invariant")
                need(x not in seen, "Gray coverage")
                seen.add(x)
                if (y, bad_phi) != expected:
                    omitted_update_faults += 1
                columns_checked += 1
                if t + 1 == 1 << n:
                    break
                next_t = t + 1
                j = (next_t & -next_t).bit_length() - 1
                old_bit = (x >> j) & 1
                phi = (phi + (1 - 2 * old_bit) * derivatives[j]) % 4
                # Negative control: omit the nonlinear derivative changes.
                bad_phi = (bad_phi + (1 - 2 * old_bit) * linear[j]) % 4
                for k in range(n):
                    if k != j:
                        derivatives[k] = (derivatives[k] + 2 * quadratic[j][k]) % 4
                x ^= 1 << j
                y ^= columns[j]
            need(len(seen) == 1 << n, "Gray exhaustive address coverage")
    need(omitted_update_faults > 0, "negative control was not detected")
    return columns_checked, omitted_update_faults


def main():
    cases = parameter_screen()
    columns, faults = gray_screen()
    print("PASS_INDEPENDENT_BLOCK_COST_SCREEN "
          f"parameter_cases={cases} wrapper_columns={columns} "
          f"detected_fault_columns={faults} no_new_kappa")


if __name__ == "__main__":
    main()
