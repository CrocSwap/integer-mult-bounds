#!/usr/bin/env python3
"""Exact finite corroboration of the dyadic cyclic balancing theorem.

No predecessor executable is imported. Default execution writes nothing.
The all-length assertion is proved in PROOF.md, not inferred from these cases.
"""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys


MAX_LENGTH = 64
MAX_BITS = 1024
MAX_DEMAND = 4096


def require(condition, message):
    if not condition:
        raise ValueError(message)


def power_two(exponent):
    require(type(exponent) is int and abs(exponent) <= 2 * MAX_DEMAND,
            "power capacity")
    return Fraction(1 << exponent) if exponent >= 0 else Fraction(1, 1 << -exponent)


def ceil_log_two(value):
    require(type(value) is Fraction and value > 0, "positive rational required")
    require(max(value.numerator.bit_length(), value.denominator.bit_length())
            <= MAX_BITS, "rational capacity")
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    return exponent + (power_two(exponent) < value)


def minimum_span(demands):
    require(type(demands) is tuple and 1 <= len(demands) <= MAX_LENGTH,
            "cycle capacity")
    require(all(type(d) is int and abs(d) <= MAX_DEMAND for d in demands),
            "integer edge demand required")
    if sum(demands) > 0:
        return None
    size = len(demands)
    scales = []
    for end in range(size):
        best = total = 0
        for length in range(size - 1):
            total += demands[(end - length) % size]
            best = max(best, total)
        scales.append(best)
    height = max(scales)
    require(min(scales) == 0, "normalization invariant")
    require(all(scales[i] - scales[i - 1] >= demands[i] for i in range(size)),
            "constructed edge invariant")
    return height, tuple(scales)


def balance(magnitudes, cap):
    require(type(magnitudes) is tuple and 1 <= len(magnitudes) <= MAX_LENGTH,
            "coefficient capacity")
    require(type(cap) is Fraction and cap > 0, "positive cap required")
    require(all(type(a) is Fraction and a > 0 for a in magnitudes),
            "positive coefficient magnitudes required")
    demands = tuple(ceil_log_two(a / cap) for a in magnitudes)
    return demands, minimum_span(demands)


def literal_feasible(demands, scales):
    """Check integer differences directly, with no interval-sum formula."""
    return all(scales[i] - scales[i - 1] >= demands[i]
               for i in range(len(demands)))


def finite_optimization():
    cases = feasible = optimum_cases = trial_vectors = 0
    for size in range(1, 7):
        for demands in product(range(-2, 3), repeat=size):
            cases += 1
            result = minimum_span(demands)
            if result is None:
                require(sum(demands) > 0, "false infeasibility")
                continue
            feasible += 1
            height, scales = result
            require(literal_feasible(demands, scales), "attainer failed")
            if size > 4:
                continue
            optimum_cases += 1
            # Every smaller-span vector translates into this finite box.
            # If height is zero there is no smaller nonnegative span.
            for candidate in product(range(height), repeat=size):
                trial_vectors += 1
                require(not literal_feasible(demands, candidate),
                        "a strictly smaller span exists")
    return dict(edge_cases=cases, feasible_cases=feasible,
                exhaustive_optimum_cases=optimum_cases,
                strictly_smaller_vectors=trial_vectors)


def apply_cycle(coefficients, vector):
    return tuple(vector[i] - coefficients[i] * vector[i - 1]
                 for i in range(len(vector)))


def conjugacy_checks():
    alphabet = tuple(map(Fraction, ("1/4", "1/2", "3/5", "3/4", "1", "3/2", "2")))
    cases = feasible = columns = entries = 0
    for size in range(1, 5):
        for magnitudes in product(alphabet, repeat=size):
            for cap in (Fraction(1), Fraction(1, 2)):
                cases += 1
                _, result = balance(magnitudes, cap)
                if result is None:
                    continue
                feasible += 1
                height, scales = result
                # Alternating signs retain nontrivial real phases.
                original = tuple((-1) ** i * a for i, a in enumerate(magnitudes))
                diagonal = tuple(power_two(s) for s in scales)
                balanced = tuple(original[i] * diagonal[i - 1] / diagonal[i]
                                 for i in range(size))
                require(max(map(abs, balanced)) <= cap, "coefficient cap failed")
                require(max(diagonal) / min(diagonal) == power_two(height),
                        "condition number failed")
                for column in range(size):
                    basis = tuple(Fraction(i == column) for i in range(size))
                    scaled = tuple(x * s for x, s in zip(basis, diagonal))
                    left = apply_cycle(original, scaled)
                    right = apply_cycle(balanced, basis)
                    require(left == tuple(x * s for x, s in zip(right, diagonal)),
                            "literal conjugacy failed")
                    columns += 1
                    entries += size
    return dict(rational_cap_cases=cases, balanced_cases=feasible,
                conjugacy_columns=columns, conjugacy_entries=entries)


def grid_checks():
    cases = coordinates = witnesses = 0
    for size in range(1, 6):
        for demands in product(range(-1, 2), repeat=size):
            result = minimum_span(demands)
            if result is None:
                continue
            height, scales = result
            for width in range(5):
                common_grid = power_two(-width - height)
                for numerator in (-3, -1, 0, 1, 3):
                    original = numerator * power_two(-width)
                    for scale in scales:
                        value = original * power_two(-scale)
                        require((value / common_grid).denominator == 1,
                                "scaled input left sufficient grid")
                        coordinates += 1
                at_max = scales.index(height)
                value = power_two(-width - scales[at_max])
                require(value.denominator == 1 << (width + height),
                        "sharp denominator failed")
                if width + height > 0:
                    require((value / (2 * common_grid)).denominator == 2,
                            "coarser grid incorrectly accepted")
                # A unit error in this balanced coordinate attains the gain.
                require(power_two(scales[at_max]) == power_two(height),
                        "sharp reverse error gain failed")
                cases += 1
                witnesses += 1
    return dict(grid_contexts=cases, grid_coordinates=coordinates,
                sharp_grid_and_error_witnesses=witnesses)


def rejects(function, *arguments):
    try:
        function(*arguments)
    except ValueError:
        return 1
    raise ValueError("a rejection control was accepted")


def controls():
    count = 0
    for bad in ((), (True,), (Fraction(1),), (MAX_DEMAND + 1,), (0,) * 65):
        count += rejects(minimum_span, bad)
    for bad in (Fraction(0), Fraction(-1), 1.0, Fraction(1 << MAX_BITS)):
        count += rejects(ceil_log_two, bad)
    for magnitudes, cap in (((Fraction(0),), Fraction(1)),
                            ((Fraction(1),), Fraction(0))):
        count += rejects(balance, magnitudes, cap)
    require(minimum_span((1,)) is None, "positive one-cycle accepted")
    require(minimum_span((-1,)) == (0, (0,)), "one-cycle mishandled")
    require(minimum_span((2, -3, 2, -1))[0] == 3,
            "wraparound interval omitted")
    require(minimum_span((0, 0)) == (0, (0, 0)), "zero cycle rejected")
    require(not literal_feasible((2, -2), (1, 0)), "understated span accepted")
    count += 5
    for exponent in range(-100, 101):
        require(ceil_log_two(power_two(exponent)) == exponent, "dyadic boundary")
        require(ceil_log_two(3 * power_two(exponent - 1)) == exponent + 1,
                "nondyadic ceiling")
    # A strict continuous product margin does not imply dyadic feasibility.
    magnitudes = (Fraction(3, 5), Fraction(2, 5))
    cap = Fraction(1, 2)
    demands, result = balance(magnitudes, cap)
    require(magnitudes[0] * magnitudes[1] < cap * cap, "margin fixture")
    require(demands == (1, 0) and result is None, "quantization obstruction")
    real_scales = (Fraction(6, 5), Fraction(1))
    require(all(magnitudes[i] * real_scales[i - 1] / real_scales[i] <= cap
                for i in range(2)), "continuous positive control")
    count += 1
    for exponent in range(1, 65):
        magnitudes = (power_two(exponent), power_two(-exponent - 2))
        demands, result = balance(magnitudes, cap)
        require(demands == (exponent + 1, -exponent - 1), "family demands")
        require(result == (exponent + 1, (exponent + 1, 0)), "family optimum")
    large = (MAX_DEMAND,) * 32 + (-MAX_DEMAND,) * 32
    require(minimum_span(large)[0] == 32 * MAX_DEMAND, "capacity attainer")
    return dict(rejection_and_semantic_controls=count,
                logarithm_boundary_values=402, expansive_family_cases=64,
                maximum_length_cases=1)


def main():
    require(len(sys.argv) == 1, "this fixed verifier accepts no arguments")
    report = {}
    report.update(finite_optimization())
    report.update(conjugacy_checks())
    report.update(grid_checks())
    report.update(controls())
    package = Path(__file__).resolve().parent
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in files:
        data = (package / name).read_bytes()
        require(len(data) <= 1024 * 1024, "package file capacity")
        hashes[name] = sha256(data).hexdigest()
    print(json.dumps(dict(status="PASS_DYADIC_CYCLE_BALANCING",
                          counts=report, sha256=hashes), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
