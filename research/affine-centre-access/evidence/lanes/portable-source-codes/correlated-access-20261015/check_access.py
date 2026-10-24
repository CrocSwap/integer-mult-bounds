#!/usr/bin/env python3
"""Check the finite examples for the CSS access note."""

import argparse
import hashlib
import json
from fractions import Fraction
from math import comb
from pathlib import Path


def require(test, message):
    if not test:
        raise ValueError(message)


def span(generators):
    values = {0}
    for g in generators:
        values |= {x ^ g for x in values}
    return tuple(sorted(values))


def dot(x, y):
    return (x & y).bit_count() & 1


def dual(code, length):
    return tuple(x for x in range(1 << length)
                 if all(not dot(x, c) for c in code))


def cosets(code, support):
    remaining = set(support)
    result = []
    while remaining:
        first = min(remaining)
        group = tuple(sorted(first ^ c for c in code))
        require(set(group) <= remaining, "coset partition")
        result.append(group)
        remaining.difference_update(group)
    return result


def projection(vector, groups, character=0):
    out = [Fraction(0)] * len(vector)
    for group in groups:
        value = sum((-1) ** dot(character, j) * vector[j] for j in group) / len(group)
        for j in group:
            out[j] = (-1) ** dot(character, j) * value
    return out


def shear(source, target, groups, sign=1, character=0):
    for group in groups:
        pivot = group[-1]
        for j in group[:-1]:
            source[pivot] += (-1) ** dot(character, j ^ pivot) * source[j]
        source[pivot] /= len(group)
        for j in group:
            target[j] += sign * (-1) ** dot(character, j ^ pivot) * source[pivot]
        source[pivot] *= len(group)
        for j in reversed(group[:-1]):
            source[pivot] -= (-1) ** dot(character, j ^ pivot) * source[j]


def gaussian_add(x, y):
    return x[0] + y[0], x[1] + y[1]


def gaussian_mul(x, y):
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def gaussian_scale(x, a):
    return a * x[0], a * x[1]


def gaussian_i(x):
    return -x[1], x[0]


def c_numerator(vector, length):
    """The result has the additional denominator 2**length."""
    out = list(vector)
    for bit in range(length):
        step = 1 << bit
        for first in range(len(out)):
            if first & step:
                continue
            second = first ^ step
            a, b = out[first], out[second]
            out[first] = gaussian_add(gaussian_mul((1, 1), a),
                                      gaussian_mul((1, -1), b))
            out[second] = gaussian_add(gaussian_mul((1, -1), a),
                                       gaussian_mul((1, 1), b))
    return out


def walsh_numerator(vector, length):
    out = list(vector)
    for bit in range(length):
        step = 1 << bit
        for first in range(len(out)):
            if first & step:
                continue
            second = first ^ step
            a, b = out[first], out[second]
            out[first] = gaussian_add(a, b)
            out[second] = gaussian_add(a, gaussian_scale(b, -1))
    return out


def projection_numerator(vector, groups, character=0):
    """The result has the additional denominator equal to a coset size."""
    out = [(0, 0)] * len(vector)
    for group in groups:
        total = (0, 0)
        for j in group:
            total = gaussian_add(total, gaussian_scale(vector[j], (-1) ** dot(character, j)))
        for j in group:
            out[j] = gaussian_scale(total, (-1) ** dot(character, j))
    return out


def check_css(length, generators):
    code = span(generators)
    require(all(c.bit_count() % 4 == 0 for c in code), "doubly even")
    support = dual(code, length)
    require(set(code) <= set(support), "self orthogonal")
    groups = cosets(code, support)
    size = 1 << length
    scalar = len({x.bit_count() % 4 for x in support}) == 1
    for col in range(size):
        vector = [(0, 0)] * size
        vector[col] = (1, 0)
        p = projection_numerator(vector, groups)
        require(c_numerator(p, length) ==
                projection_numerator(c_numerator(vector, length), groups),
                "CSS and C commute")
        require(walsh_numerator(p, length) ==
                projection_numerator(walsh_numerator(vector, length), groups),
                "CSS and Walsh commute")
    for col in range(2 * size):
        x = [Fraction(int(j == col)) for j in range(size)]
        y = [Fraction(int(j + size == col)) for j in range(size)]
        old_x, old_y = x[:], y[:]
        expected = [a + b for a, b in zip(y, projection(x, groups))]
        shear(x, y, groups)
        require(x == old_x and y == expected, "all-input projector shear")
        shear(x, y, groups, -1)
        require(x == old_x and y == old_y, "inverse projector shear")
        for _ in range(4):
            shear(y, x, groups)
            shear(x, y, groups, -1)
            shear(y, x, groups)
        require(x == old_x and y == old_y, "projected quarter turn order")
    r = len(code).bit_length() - 1
    allowed, count = len(support), len(groups)
    return {
        "length": length, "dimension": r, "generators": generators,
        "projector_rank": count, "ambient_dimension": size,
        "native_C_is_scalar": scalar,
        "native_phase_residues": sorted({x.bit_count() % 4 for x in support}),
        "all_input_columns": 2 * size, "complex_unit_adds": 3 * allowed - 2 * count,
        "real_primitive_bound": 24 * allowed + (4 * r - 16) * count,
        "extra_native_children": 0, "maximum_source_pivot_growth": len(code),
        "stream_admission": "not checked",
    }


def check_affine_criterion():
    result = []
    for length in range(1, 7):
        codes = {(0,)}
        frontier = {(0,)}
        while frontier:
            next_frontier = set()
            for code in frontier:
                for v in range(1, 1 << length):
                    if v in code or v.bit_count() & 1 or any(dot(v, c) for c in code):
                        continue
                    enlarged = tuple(sorted(set(code) | {c ^ v for c in code}))
                    if enlarged not in codes:
                        next_frontier.add(enlarged)
            codes |= next_frontier
            frontier = next_frontier
        constant = 0
        tested = 0
        for code in codes:
            support = dual(code, length)
            for a in range(1 << length):
                tested += 1
                if len({(a ^ v).bit_count() % 4 for v in support}) == 1:
                    require(code == support, "affine scalar criterion")
                    constant += 1
        result.append({"length": length, "self_orthogonal_codes": len(codes),
                       "affine_cases": tested, "constant_weight_cases": constant})
    return result


def bell_column(n, b, a):
    factor = (1, 0)
    for _ in range(n):
        factor = gaussian_mul(factor, (1, 1))
    return {(x << n) | (x ^ a): gaussian_scale(factor, (-1) ** dot(x, b))
            for x in range(1 << n)}


def check_bell():
    count = 0
    controls = {"omit_i": False, "always_translate": False, "inverse_phase": False}
    for n in range(1, 5):
        for q in range(1, 1 << n):
            for b in range(1 << n):
                parity = dot(b, q)
                for a in range(1 << n):
                    original = bell_column(n, b, a)
                    actual = {}
                    for address, coefficient in original.items():
                        for left, right in ((0, 0), (0, 1), (1, 0), (1, 1)):
                            destination = address ^ ((q << n) if left else 0) ^ (q if right else 0)
                            factor = gaussian_mul((1, -1) if left else (1, 1),
                                                  (1, -1) if right else (1, 1))
                            value = gaussian_mul(factor, coefficient)
                            actual[destination] = gaussian_add(actual.get(destination, (0, 0)), value)
                    actual = {k: v for k, v in actual.items() if v != (0, 0)}
                    expected = bell_column(n, b, a if parity else a ^ q)
                    expected = {k: gaussian_scale(gaussian_i(v) if parity else v, 4)
                                for k, v in expected.items()}
                    require(actual == expected, "original complex Bell phase")
                    if parity:
                        omit = {k: gaussian_scale(v, 4) for k, v in original.items()}
                        inverse = {k: gaussian_scale(gaussian_i(v), -4) for k, v in original.items()}
                        move = {k: gaussian_scale(gaussian_i(v), 4)
                                for k, v in bell_column(n, b, a ^ q).items()}
                        controls["omit_i"] |= actual != omit
                        controls["inverse_phase"] |= actual != inverse
                        controls["always_translate"] |= actual != move
                    count += 1
    require(all(controls.values()), "Bell negative controls")
    return {"complete_basis_columns": count, "native_coordinates": [1, 2, 3, 4],
            "negative_controls_rejected": controls}


def check_phase_projector_support():
    rows = []
    for length in range(3, 21):
        for residue in range(4):
            support = 0
            for weight in range(length + 1):
                value = (1, 0)
                for j in range(length):
                    value = gaussian_mul(value, (1, -1) if j < weight else (1, 1))
                for _ in range((-residue) % 4):
                    value = gaussian_i(value)
                numerator = 2 * value[0]
                if weight == 0:
                    numerator += 1 << length
                if weight == length:
                    numerator += (-1) ** residue * (1 << length)
                if numerator:
                    support += comb(length, weight)
            expected = (1 << length) if length & 1 else (
                (1 << (length - 1)) + (2 if (length // 2 - residue) & 1 else 0))
            require(support == expected, "phase projector row support")
            rows.append([length, residue, support])
    return rows


def all_subspaces(bits):
    spaces = {(0,)}
    frontier = {(0,)}
    while frontier:
        new = set()
        for space in frontier:
            for v in range(1, 1 << bits):
                if v not in space:
                    enlarged = tuple(sorted(set(space) | {x ^ v for x in space}))
                    if enlarged not in spaces:
                        new.add(enlarged)
        spaces |= new
        frontier = new
    return spaces


def signature_phases(address, coordinates, length):
    rows = [(address >> (length * j)) & ((1 << length) - 1)
            for j in range(coordinates)]
    values = set()
    for v in range(1, 1 << coordinates):
        if v.bit_count() & 1:
            total = 0
            for j, row in enumerate(rows):
                if (v >> j) & 1:
                    total ^= row
            values.add(total.bit_count() % 4)
    return values


def check_affine_sector_bound():
    cache = {}
    results = []
    for coordinates, length in ((2, 1), (2, 2), (2, 3), (3, 1), (3, 2)):
        bits = coordinates * length
        if bits not in cache:
            cache[bits] = all_subspaces(bits)
        phases = [signature_phases(a, coordinates, length) for a in range(1 << bits)]
        sector = {a for a, values in enumerate(phases) if len(values) == 1}
        count, maximum, fixed_maximum = 0, 0, 0
        for space in cache[bits]:
            for group in cosets(space, range(1 << bits)):
                if set(group) <= sector:
                    count += 1
                    dimension = len(space).bit_length() - 1
                    maximum = max(maximum, dimension)
                    require(dimension <= coordinates * (length // 2) + (length & 1),
                            "affine full-sector bound")
                    if len(set.union(*(phases[a] for a in group))) == 1:
                        fixed_maximum = max(fixed_maximum, dimension)
                        require(dimension <= coordinates * (length // 2),
                                "affine fixed-phase bound")
        results.append({"coordinates": coordinates, "length": length,
                        "all_linear_spaces": len(cache[bits]),
                        "contained_affine_spaces": count, "sector_size": len(sector),
                        "maximum_affine_dimension": maximum,
                        "maximum_fixed_phase_dimension": fixed_maximum})
    return results


def sharp_affine_space(coordinates, length):
    generators = []
    offset = 0
    for row in range(coordinates):
        for pair in range(length // 2):
            bit = row * length + 2 * pair
            generators.append(3 << bit)
            offset ^= 1 << bit
    if length & 1:
        generators.append(sum(1 << (row * length + length - 1)
                              for row in range(coordinates)))
    return span(generators), offset


def check_sharp_examples():
    rows = []
    for coordinates in (2, 3, 4):
        for length in range(1, 7):
            space, offset = sharp_affine_space(coordinates, length)
            expected = coordinates * (length // 2) + (length & 1)
            require(len(space) == 1 << expected, "sharp affine dimension")
            phases = set()
            for v in space:
                values = signature_phases(v ^ offset, coordinates, length)
                require(len(values) == 1, "sharp affine phase sector")
                phases |= values
            require(phases == ({(length // 2) % 4, (length // 2 + 1) % 4}
                               if length & 1 else {(length // 2) % 4}),
                    "sharp affine phase values")
            rows.append([coordinates, length, expected, sorted(phases)])
    for coordinates, length in ((2, 2), (2, 4), (3, 2)):
        bits = coordinates * length
        size = 1 << bits
        space, offset = sharp_affine_space(coordinates, length)
        translation = dual(space, bits)
        groups = cosets(translation, range(size))
        for col in range(2 * size):
            if col < size:
                basis = [(0, 0)] * size
                basis[col] = (1, 0)
                transformed = walsh_numerator(
                    projection_numerator(basis, groups, offset), bits)
                expected_spectrum = walsh_numerator(basis, bits)
                expected_spectrum = [gaussian_scale(value, len(translation))
                                     if j ^ offset in space else (0, 0)
                                     for j, value in enumerate(expected_spectrum)]
                require(transformed == expected_spectrum, "signed projector Fourier support")
            x = [Fraction(int(j == col)) for j in range(size)]
            y = [Fraction(int(j + size == col)) for j in range(size)]
            old_x, old_y = x[:], y[:]
            increment = projection(x, groups, offset)
            shear(x, y, groups, character=offset)
            require(x == old_x and y == [a + b for a, b in zip(old_y, increment)],
                    "signed affine projector shear")
            shear(x, y, groups, sign=-1, character=offset)
            require(x == old_x and y == old_y, "signed affine inverse shear")
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lanes", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    source = args.lanes / "coherent-port/COVARIANCE.json"
    pin = "6466d082f376bcbd8f7d953d8a2625f5e31eb164ffa61f430b1cdf6e6ef30b38"
    require(hashlib.sha256(source.read_bytes()).hexdigest() == pin, "root source pin")
    data = json.loads(source.read_text())
    labels = data["labels"][:112]
    require(len(set(labels)) == 112 and all(q.bit_count() & 1 for q in labels),
            "actual odd port labels")
    receipt = {
        "status": "PASS_EXACT_CSS_ACCESS_AND_ORIGINAL_BELL_PHASE",
        "source": {"path": "coherent-port/COVARIANCE.json", "sha256": pin},
        "css_cases": [check_css(4, [15]), check_css(8, [15]),
                      check_css(8, [15, 51, 85, 255])],
        "affine_scalar_criterion": check_affine_criterion(),
        "original_complex_bell": check_bell(),
        "single_phase_projector_support": check_phase_projector_support(),
        "affine_correlated_sector_bound": check_affine_sector_bound(),
        "sharp_affine_examples": check_sharp_examples(),
        "scope": "Exact arithmetic graphs and finite algebra checks; no stream, owner, precision, or supplier admission.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
