#!/usr/bin/env python3
"""Separate LCM and Cartesian-coordinate checks; does not import verify.py."""
import itertools
import math


def need(condition, message):
    if not condition:
        raise ValueError(message)


def check_lcm():
    cases = 0
    for packet, compatibility, levels in itertools.product(range(1, 8), range(1, 10), range(5)):
        constraints = [compatibility * packet**i for i in range(1, levels + 1)]
        minimum = math.lcm(*constraints)
        expected = compatibility * packet**levels if levels else 1
        need(minimum == expected, "LCM of every local guard")
        # Recover divisibility constraints from an actual chain without
        # assuming coprimality of the packet and compatibility constants.
        for multiplier in range(1, 4):
            rows = multiplier * minimum
            for _ in range(levels):
                need(rows % packet == 0, "complete packet")
                rows //= packet
                need(rows > 0 and rows % compatibility == 0, "local compatibility")
        cases += 1
    return cases


def check_codec():
    family_count, low_count, high_count, compatibility, levels = 2, 3, 2, 5, 3
    layers = list(itertools.product(range(family_count), range(low_count), range(high_count)))
    packet = len(layers)
    total = compatibility * packet**levels
    images = set()
    for coordinates in itertools.product(layers, repeat=levels):
        for terminal in range(compatibility):
            ordinal = terminal
            extent = compatibility
            for family, low, high in reversed(coordinates):
                digit = (family * low_count + low) * high_count + high
                ordinal += digit * extent
                extent *= packet
            need(0 <= ordinal < total and ordinal not in images, "one restored row ordinal")
            images.add(ordinal)
            row, remaining = ordinal, total
            recovered = []
            for _ in range(levels):
                remaining //= packet
                digit, row = divmod(row, remaining)
                family, suffix = divmod(digit, low_count * high_count)
                low, high = divmod(suffix, high_count)
                recovered.append((family, low, high))
                need(remaining % compatibility == 0, "complete compatible child extent")
            need(tuple(recovered) == coordinates and row == terminal, "pointwise inverse")
    need(len(images) == total, "complete fresh range")
    return total


def check_two_format_boundary():
    live, physical = 28416, 28425
    compatibility = physical // math.gcd(live, physical)
    need(compatibility == 9475, "selected compatibility")
    for levels in range(1, 9):
        # N and H cancel from the old physical/live depth-format comparison.
        candidate = compatibility * live**levels
        old_common = math.lcm(live, physical)**levels
        need(old_common // candidate == compatibility**(levels - 1), "reserve reduction")
        need((candidate % physical**levels == 0) == (levels == 1),
             "old dual-format boundary remains false at depth two and higher")
        required = compatibility**(levels - 1)
        for multiplicity in (1, required, required + 1):
            need((multiplicity * candidate % physical**levels == 0)
                 == (multiplicity % required == 0), "exact old-format multiplicity gate")
    return 8


def main():
    lcm_cases = check_lcm()
    rows = check_codec()
    formats = check_two_format_boundary()
    print(f"PASS_INDEPENDENT_GUARD_STOCK lcm_cases={lcm_cases} "
          f"pointwise_rows={rows} old_format_depths={formats}")


if __name__ == "__main__":
    main()
