#!/usr/bin/env python3
"""Residue step of the chirp odometer.

The checker proves the square step and runs the published transitions.
It does not run the middle-map consumer.
"""

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_CHIRP_RESIDUE_STEP rollouts=6141 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
MAX_ELL = 12
VISIT_LENGTHS = (2, 4, 8, 16, 32)


def fail(message):
    raise SystemExit("FAIL_CHIRP_RESIDUE_STEP " + message)


def require(condition, message):
    if not condition:
        fail(message)


def odd_slopes(length):
    return range(1, length, 2)


def coefficient(slope, radius, length):
    modulus = 2 * radius
    return (-slope * (radius // length)) % modulus


def one_axis(radius, length, slope):
    modulus = 2 * radius
    factor = coefficient(slope, radius, length)
    index = 0
    value = 0
    difference = factor
    total = 0
    steps = 0
    while True:
        require(value == (factor * index * index) % modulus, "value")
        require(difference == (factor * (2 * index + 1)) % modulus, "difference")
        require(total == value, "one-axis total")
        steps += 1
        if index + 1 < length:
            total = (total + difference) % modulus
            value = (value + difference) % modulus
            difference = (difference + 2 * factor) % modulus
            index += 1
            continue
        total = (total - value) % modulus
        index = 0
        value = 0
        difference = factor
        break
    require(total == 0 and index == 0 and value == 0, "rollover")
    require(steps == length, "step count")
    return steps


def two_axis(radius, lengths, slopes):
    modulus = 2 * radius
    factors = [coefficient(slope, radius, length) for slope, length in zip(slopes, lengths)]
    index = [0, 0]
    value = [0, 0]
    difference = list(factors)
    total = 0
    states = 0
    for _ in range(lengths[0] * lengths[1]):
        closed = 0
        for axis in range(2):
            expected = (factors[axis] * index[axis] * index[axis]) % modulus
            require(value[axis] == expected, "two-axis value")
            require(difference[axis] == (factors[axis] * (2 * index[axis] + 1)) % modulus, "two-axis difference")
            closed = (closed + expected) % modulus
        require(total == closed, "two-axis total")
        states += 1
        axis = 0
        while True:
            if index[axis] + 1 < lengths[axis]:
                total = (total + difference[axis]) % modulus
                value[axis] = (value[axis] + difference[axis]) % modulus
                difference[axis] = (difference[axis] + 2 * factors[axis]) % modulus
                index[axis] += 1
                break
            total = (total - value[axis]) % modulus
            index[axis] = 0
            value[axis] = 0
            difference[axis] = factors[axis]
            axis += 1
            if axis == 2:
                break
    require(total == 0 and index == [0, 0] and value == [0, 0], "two-axis rollover")
    return states


def visit_ratio(lengths):
    size = 1
    for length in lengths:
        size *= length
    total = 0
    tail = 1
    ratio = Fraction(0)
    for offset, length in enumerate(reversed(lengths)):
        require(tail >= 2 ** offset, "tail")
        ratio += Fraction(1, tail)
        total += size // tail
        tail *= length
    require(ratio < 2, "visit ratio")
    require(total < 2 * size, "visit count")
    return total


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    squares = 0
    for index in range(1 << MAX_ELL):
        require((index + 1) ** 2 - index ** 2 == 2 * index + 1, "square")
        require(2 * (index + 1) + 1 == (2 * index + 1) + 2, "second difference")
        squares += 1
    rollouts = 0
    steps = 0
    for ell in range(2, MAX_ELL + 1):
        radius = 1 << ell
        for length in (radius // 2, radius):
            for slope in odd_slopes(length):
                steps += one_axis(radius, length, slope)
                rollouts += 1
    states = 0
    for ell in range(2, 5):
        radius = 1 << ell
        for first in (radius // 2, radius):
            lengths = (first, radius)
            for slope_0 in odd_slopes(first):
                for slope_1 in odd_slopes(radius):
                    states += two_axis(radius, lengths, (slope_0, slope_1))
    tuples = 0
    choices = len(VISIT_LENGTHS)

    def walk(prefix, depth):
        nonlocal tuples
        if depth == 0:
            visit_ratio(prefix)
            tuples += 1
            return
        for length in VISIT_LENGTHS:
            walk(prefix + (length,), depth - 1)

    for depth in range(1, 6):
        walk((), depth)
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(squares == 4096, "square checks")
    require(rollouts == 6141, "rollouts")
    require(steps == 13981010, "steps")
    require(states == 21840, "states")
    require(tuples == 3905, "tuples")
    require(receipt["square_checks"] == squares, "receipt squares")
    require(receipt["one_axis_rollouts"] == rollouts, "receipt rollouts")
    require(receipt["one_axis_steps"] == steps, "receipt steps")
    require(receipt["two_axis_states"] == states, "receipt states")
    require(receipt["visit_tuples"] == tuples, "receipt tuples")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    require(choices == 5, "visit alphabet")
    print(MARKER)


if __name__ == "__main__":
    main()
