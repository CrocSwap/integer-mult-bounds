#!/usr/bin/env python3
"""Exact finite corroboration of the native C prefix-scale theorem.

Produced by Nick Petalas. Apache-2.0. Standard library only.
No predecessor executable is imported or run. All checks survive -O.
"""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import permutations, product
from pathlib import Path
import json
import random
import sys


def need(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(z, w):
    return z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0]


def axis_numerator(values, axis):
    """Apply 2C using real integer rows, without any division."""
    out = list(values)
    for a in range(len(values)):
        if a & (1 << axis):
            continue
        b = a | (1 << axis)
        ar, ai = values[a]
        br, bi = values[b]
        out[a] = ar - ai + br + bi, ar + ai - br + bi
        out[b] = ar + ai + br - bi, ai - ar + br + bi
    return out


def prefixes(values, order):
    result = [list(values)]
    for axis in order:
        result.append(axis_numerator(result[-1], axis))
    return result


def is_integral(numerators, denominator):
    return all(a % denominator == b % denominator == 0 for a, b in numerators)


def divide(numerators, denominator):
    need(is_integral(numerators, denominator), "nonintegral Gaussian value")
    return [(a // denominator, b // denominator) for a, b in numerators]


def scaled_program(values, order, scale):
    current = [(scale * a, scale * b) for a, b in values]
    for axis in order:
        current = divide(axis_numerator(current, axis), 2)
    return divide(current, scale)


def rational_axis(values, axis):
    """Independent complex multiplication with rational coefficients."""
    diagonal = Fraction(1, 2), Fraction(1, 2)
    off = Fraction(1, 2), Fraction(-1, 2)
    out = list(values)
    for a in range(len(values)):
        if a & (1 << axis):
            continue
        b = a | (1 << axis)
        u, v = multiply(diagonal, values[a]), multiply(off, values[b])
        out[a] = u[0] + v[0], u[1] + v[1]
        u, v = multiply(off, values[a]), multiply(diagonal, values[b])
        out[b] = u[0] + v[0], u[1] + v[1]
    return out


def dense_tensor(values, f, selected):
    """Direct tensor entries i^(d-HammingDistance)/pi^d on selected bits."""
    mask = sum(1 << a for a in selected)
    d = len(selected)
    denominator = (1, 0)
    for _ in range(d):
        denominator = multiply(denominator, (1, 1))
    norm = denominator[0] ** 2 + denominator[1] ** 2
    inverse = Fraction(denominator[0], norm), Fraction(-denominator[1], norm)
    units = ((1, 0), (0, 1), (-1, 0), (0, -1))
    result = []
    for a in range(1 << f):
        total = (0, 0)
        for b in range(1 << f):
            if (a ^ b) & ~mask:
                continue
            exponent = d - ((a ^ b) & mask).bit_count()
            term = multiply(units[exponent % 4], values[b])
            total = total[0] + term[0], total[1] + term[1]
        result.append(multiply(total, inverse))
    return result


def witness(f, selected):
    selected = tuple(sorted(selected))
    other = tuple(a for a in range(f) if a not in selected)
    pairs = tuple(zip(selected, other))
    values, endpoint = [], []
    for address in range(1 << f):
        equal = all(((address >> a) ^ (address >> b)) & 1 == 0 for a, b in pairs)
        opposite = all(((address >> a) ^ (address >> b)) & 1 == 1 for a, b in pairs)
        values.append((int(equal), 0))
        endpoint.append((int(opposite), 0))
    return values, endpoint


def check_cut(f, selected):
    x, expected = witness(f, selected)
    order = tuple(selected) + tuple(a for a in range(f) if a not in selected)
    history = prefixes(x, order)
    need(divide(history[-1], 1 << f) == expected, "witness endpoint")
    common = 1 << (((f // 2) + 1) // 2)
    need(scaled_program(x, order, common) == expected, "scaled arithmetic program")
    j = len(selected)
    d = min(j, f - j)
    pi_power = (1, 0)
    for _ in range(d):
        pi_power = multiply(pi_power, (1, 1))
    cut = [multiply(v, pi_power) for v in history[j]]
    integral = divide(cut, 1 << j)
    need(all(abs(a) + abs(b) == 1 for a, b in integral), "sharp Gaussian denominator")
    binary = 1 << ((d + 1) // 2)
    divide([(binary * a, binary * b) for a, b in history[j]], 1 << j)
    if binary > 1:
        need(not is_integral([(binary // 2 * a, binary // 2 * b)
                              for a, b in history[j]], 1 << j), "binary lower bound")
    if f <= 4:
        need(dense_tensor(x, f, selected) ==
             [(Fraction(a, 1 << j), Fraction(b, 1 << j)) for a, b in history[j]],
             "direct tensor oracle")
    return {"f": f, "cut": j, "gaussian_exponent": d, "binary_scale": binary}


def exhaustive_box():
    """Every Gaussian 0/1-component array through three axes."""
    counts = Counter()
    for f in range(1, 4):
        n = 1 << f
        scale = 1 << (((f // 2) + 1) // 2)
        for flat in product((0, 1), repeat=2 * n):
            x = list(zip(flat[::2], flat[1::2]))
            history = prefixes(x, range(f))
            counts["inputs"] += 1
            if not is_integral(history[-1], 1 << f):
                counts["outside_endpoint_domain"] += 1
                continue
            counts["endpoint_integral"] += 1
            for j, row in enumerate(history):
                d = min(j, f - j)
                pi = (1, 0)
                for _ in range(d):
                    pi = multiply(pi, (1, 1))
                divide([multiply(z, pi) for z in row], 1 << j)
                divide([(scale * a, scale * b) for a, b in row], 1 << j)
                counts["prefixes"] += 1
    return dict(counts)


def independent_oracles():
    rng = random.Random(8527429)
    count = 0
    for f in range(1, 6):
        for _ in range(12):
            x = [(rng.randrange(-7, 8), rng.randrange(-7, 8)) for _ in range(1 << f)]
            order = tuple(rng.sample(range(f), f))
            integer = prefixes(x, order)
            rational = [(Fraction(a), Fraction(b)) for a, b in x]
            for j, axis in enumerate(order, 1):
                rational = rational_axis(rational, axis)
                need(rational == [(Fraction(a, 1 << j), Fraction(b, 1 << j))
                                   for a, b in integer[j]], "independent rational prefix")
                if f <= 4:
                    need(rational == dense_tensor(x, f, order[:j]), "dense tensor prefix")
                count += 1
    return count


def permutation_checks():
    count = 0
    for f in range(1, 6):
        x, endpoint = witness(f, range(f // 2))
        scale = 1 << (((f // 2) + 1) // 2)
        for order in permutations(range(f)):
            history = prefixes(x, order)
            need(divide(history[-1], 1 << f) == endpoint, "axis order endpoint")
            for j, row in enumerate(history):
                divide([(scale * a, scale * b) for a, b in row], 1 << j)
            count += 1
    return count


def controls():
    checked = []
    x, endpoint = witness(6, range(3))
    h = prefixes(x, range(6))
    need(divide(h[-1], 64) == endpoint, "six-axis promise")
    checked.append("six_axis_integral_endpoint")
    need(not is_integral([(2*a, 2*b) for a, b in h[3]], 8), "one bit too little")
    checked.append("one_bit_below_sharp_scale")
    impulse = [(1, 0)] + [(0, 0)] * 7
    bad = prefixes(impulse, range(3))
    need(not is_integral(bad[-1], 8), "missing endpoint hypothesis")
    checked.append("unpromised_endpoint")
    need(not is_integral([(2*a, 2*b) for a, b in bad[-1]], 8), "unpromised scale")
    checked.append("scale_without_endpoint_promise_fails")
    for bad_denominator in (2, 4):
        rejected = False
        try:
            divide([(1, 0)], bad_denominator)
        except ValueError as error:
            rejected = str(error) == "nonintegral Gaussian value"
        need(rejected, "inexact division must reject")
        checked.append("inexact_division_" + str(bad_denominator))
    minus = rational_axis([(Fraction(1), Fraction(0)), (Fraction(0), Fraction(0))], 0)
    need(minus != [(Fraction(1,2), Fraction(-1,2)),
                   (Fraction(1,2), Fraction(1,2))], "inverse/phase confusion")
    checked.append("forward_not_inverse_phase")
    shifted = [(a - 8, b + 8) for a, b in x]
    need(divide(prefixes(shifted, range(6))[-1], 64) ==
         [(a - 8, b + 8) for a, b in endpoint], "arbitrary signed dirty offset")
    checked.append("signed_complex_dirty_offset")
    return checked


def run():
    cuts = []
    for f in range(1, 7):
        for mask in range(1 << f):
            cuts.append(check_cut(f, tuple(a for a in range(f) if mask & (1 << a))))
    for f in range(7, 11):
        for j in range(f + 1):
            cuts.append(check_cut(f, tuple(range(j))))
    summary = {
        "claim_type": "scoped written proof with exact finite corroboration",
        "cut_witnesses": len(cuts),
        "cut_profile_sha256": sha256(json.dumps(cuts, sort_keys=True).encode()).hexdigest(),
        "exhaustive_box": exhaustive_box(),
        "independent_prefixes": independent_oracles(),
        "axis_permutations": permutation_checks(),
        "controls": controls(),
        "binary_scales_f1_to_f10": [1 << (((f // 2) + 1) // 2) for f in range(1, 11)],
    }
    here = Path(__file__).resolve().parent
    files = sorted(p for p in here.iterdir() if p.is_file())
    need(len(files) <= 12, "package inventory cap")
    need(all(p.stat().st_size <= 2**20 for p in files), "package byte cap")
    receipt = {"result": summary,
               "files": {p.name: sha256(p.read_bytes()).hexdigest() for p in files},
               "python": sys.version.split()[0]}
    print(json.dumps(receipt, sort_keys=True, indent=2))
    print("PASS_NATIVE_C_ENDPOINT_PREFIX_SCALE")


if __name__ == "__main__":
    run()
