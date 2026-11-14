#!/usr/bin/env python3
"""Exact bounded controls for PRIME-ORBITS.md; read-only, standard library.

Reuses this package's frozen rational matrix primitives, but checks prime
cycles by direct enumeration, an independent Burnside sum, and the product
formula. No imported main routine is executed and no assertions are used.
"""

from collections import Counter
from fractions import Fraction as F
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from math import gcd, isqrt, lcm, prod
from pathlib import Path
import json

spec = spec_from_file_location("orbit_matrix_primitives", Path(__file__).with_name("verify.py"))
base = module_from_spec(spec)
spec.loader.exec_module(base)
require = base.require


def is_prime(p):
    return p >= 2 and all(p % i for i in range(2, isqrt(p) + 1))


def validate(n, d, primes):
    require(n >= 2, "alphabet must have at least two labels")
    require(len(set(primes)) == len(primes), "repeated prime periods")
    require(all(p >= 3 and p % 2 and is_prime(p) for p in primes),
            "block lengths must be odd primes")
    require(sum(primes) <= d, "blocks exceed coordinate budget")


def rotate(x, primes):
    out = list(x)
    offset = 0
    for p in primes:
        out[offset:offset + p] = x[offset + 1:offset + p] + (x[offset],)
        offset += p
    return tuple(out)


def orbit_order(shape, primes):
    vertices = list(product(*(range(n) for n in shape)))
    ordered, starts, lengths = [], [], []
    seen = set()
    for x in vertices:
        if x in seen:
            continue
        starts.append(len(ordered))
        y = x
        while y not in seen:
            seen.add(y)
            ordered.append(y)
            y = rotate(y, primes)
        require(y == x, "cycle did not return to representative")
        lengths.append(len(ordered) - starts[-1])
    require(len(ordered) == len(vertices) and set(ordered) == set(vertices),
            "cycle order lost or repeated labels")
    return vertices, ordered, starts, lengths


def count_formula(n, d, primes):
    answer = F(n ** (d - sum(primes)))
    for p in primes:
        answer *= F(n ** p + (p - 1) * n, p)
    return answer


def burnside_count(n, d, primes):
    period = lcm(*primes) if primes else 1
    total = sum(n ** (d - sum(primes) + sum(gcd(p, t) for p in primes))
                for t in range(period))
    require(total % period == 0, "Burnside sum is not integral")
    return total // period


def check_cycles(n, primes, spectators=0):
    d = sum(primes) + spectators
    validate(n, d, primes)
    vertices, _, starts, lengths = orbit_order((n,) * d, primes)
    expected = count_formula(n, d, primes)
    require(expected.denominator == 1, "prime count not integral")
    require(len(starts) == expected == burnside_count(n, d, primes),
            "direct/Burnside/product counts differ")
    period = prod(primes)
    require(all(period % length == 0 for length in lengths), "period divisibility")
    require(1 in lengths and period in lengths, "variable periods missing")
    correction = F(len(starts) * period, len(vertices))
    require(F(1) <= correction < F(3), "uniform correction certificate")
    return {"n": n, "primes": primes, "spectators": spectators,
            "vertices": len(vertices), "cycles": len(starts),
            "length_histogram": dict(sorted(Counter(lengths).items())),
            "correction": str(correction)}


def check_matrix(name, factors, primes):
    shape = tuple(len(b) for b in factors)
    validate(shape[0], len(shape), primes)
    vertices, ordered, starts, lengths = orbit_order(shape, primes)
    index = {x: i for i, x in enumerate(ordered)}
    successor = [index[rotate(x, primes)] for x in ordered]
    targets = [factors, [base.inverse(b) for b in factors]]
    ranks = []
    matrices = []
    for target in targets:
        h = base.permuted_matrix(target, vertices, ordered)
        require(all(h[successor[i]][successor[j]] == h[i][j]
                    for i in range(len(h)) for j in range(len(h))),
                "matrix is not invariant")
        e = base.stein(h)
        require(e == base.literal_stein(h), "literal shift product differs")
        require(base.supported(e, starts), "prime-orbit support failed")
        r = base.rank(e)
        require(r <= 2 * len(starts), "prime rank bound failed")
        terms = base.generators(e, starts)
        require(base.toeplitz_reconstruct(terms) == h,
                "prime ordinary-generator reconstruction failed")
        ranks.append(r)
        matrices.append(h)
    require(base.inverse(matrices[0]) == matrices[1], "full inverse differs")
    return {"case": name, "dimension": len(ordered), "cycles": len(starts),
            "periods": sorted(set(lengths)), "forward_rank": ranks[0],
            "inverse_rank": ranks[1], "literal_reconstructions": 2}


def rank_mod(a, modulus):
    work = [row[:] for row in a]
    r = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if work[i][j] % modulus), None)
        if pivot is None:
            continue
        work[r], work[pivot] = work[pivot], work[r]
        inverse = pow(work[r][j], -1, modulus)
        work[r] = [value * inverse % modulus for value in work[r]]
        for i in range(r + 1, len(a)):
            if work[i][j]:
                value = work[i][j]
                work[i] = [(x - value * y) % modulus for x, y in zip(work[i], work[r])]
        r += 1
        if r == len(a):
            break
    return r


def modular_pair():
    modulus = 1000003
    q = pow(2, -1, modulus)
    _, order, starts, lengths = orbit_order((2,) * 8, [3, 5])
    integers = [sum(bit << i for i, bit in enumerate(x)) for x in order]
    h = [[pow(q, (x ^ y).bit_count(), modulus) for y in integers] for x in integers]
    denom_inverse = pow(pow((1 - q * q) % modulus, 8, modulus), -1, modulus)
    hi = [[pow(-q % modulus, (x ^ y).bit_count(), modulus) * denom_inverse % modulus
           for y in integers] for x in integers]
    # Direct dense product verifies the full inverse at this finite field point.
    columns = list(zip(*hi))
    for i, row in enumerate(h):
        for j, col in enumerate(columns):
            require(sum(x * y for x, y in zip(row, col)) % modulus == int(i == j),
                    "modular full inverse residual")
    ranks = []
    for matrix in (h, hi):
        e = [[(matrix[i][j] - (matrix[i - 1][j - 1] if i and j else 0)) % modulus
              for j in range(len(matrix))] for i in range(len(matrix))]
        require(base.supported(e, starts), "modular support failed")
        r = rank_mod(e, modulus)
        require(r <= 2 * len(starts), "modular rank bound failed")
        ranks.append(r)
    return {"field": modulus, "q_rational": "1/2", "dimension": 256,
            "cycles": len(starts), "periods": sorted(set(lengths)),
            "forward_rank_mod": ranks[0], "inverse_rank_mod": ranks[1],
            "scope": "one finite-field point; not a real-q universal rank"}


def family_checks():
    result = []
    for d in (8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096):
        k = d.bit_length() - 3
        primes = [next(p for p in range((1 << i) + 1, 1 << (i + 1)) if is_prime(p))
                  for i in range(1, k + 1)]
        validate(2, d, primes)
        p_product = prod(primes)
        require(sum(primes) < (1 << (k + 2)) <= d, "coordinate-budget bound")
        require((1 << (k * (k + 1) // 2)) < p_product <
                (1 << (k * (k + 3) // 2)), "Bertrand product bounds")
        correction = prod(F(1) + F(p - 1, 2 ** (p - 1)) for p in primes)
        require(F(1) < correction < F(3), "finite uniform correction")
        result.append({"d": d, "k": k, "primes": primes,
                       "used_coordinates": sum(primes), "prime_product": p_product,
                       "product_lower_exponent": k * (k + 1) // 2})
    return result


def controls():
    base.must_reject(lambda: validate(2, 6, [3, 3]), "repeated primes accepted")
    _, _, starts, _ = orbit_order((2,) * 6, [3, 3])
    require(len(starts) == burnside_count(2, 6, [3, 3]) == 24,
            "repeated-prime true count changed")
    require(count_formula(2, 6, [3, 3]) == 16, "repeated-prime false count changed")
    base.must_reject(lambda: validate(2, 4, [4]), "composite block accepted")
    _, _, composite_starts, composite_lengths = orbit_order((2,) * 4, [4])
    require(len(composite_starts) == 6 and 2 in composite_lengths,
            "composite intermediate-period witness disappeared")
    require(count_formula(2, 4, [4]) != 6, "prime formula unexpectedly valid")
    base.must_reject(lambda: validate(1, 5, [5]), "one-label alphabet accepted")
    require(count_formula(1, 5, [5]) == 1 > F(3, 5), "one-label bound control")
    vertices, order, starts, lengths = orbit_order((2,) * 3, [3])
    different_q = [base.gaussian(2, q) for q in (F(1, 2), F(1, 3), F(1, 2))]
    matrix = base.permuted_matrix(different_q, vertices, order)
    require(not base.supported(base.stein(matrix), starts), "unequal q not detected")
    different_v = [base.gaussian(2, F(1, 2), v) for v in (F(1), F(2), F(1))]
    matrix = base.permuted_matrix(different_v, vertices, order)
    require(not base.supported(base.stein(matrix), starts), "unequal shift not detected")
    correction = prod(F(1) + F(p - 1, 2 ** (p - 1)) for p in (3, 5, 7))
    require(correction == F(525, 256) > 2, "false-constant witness changed")
    base.must_reject(lambda: require(correction <= 2, "constant two is false"),
                    "forged correction constant survived")
    base.must_reject(lambda: require(all(length == 3 for length in lengths),
                                     "not every orbit has maximum period"),
                    "false equal-period claim survived")
    return {"negative_controls": 7, "repeated_prime_true_count": 24,
            "repeated_prime_false_product": 16, "composite_true_count": 6,
            "constant_two_counterexample": str(correction)}


def main():
    cycles = [check_cycles(n, primes, spectators) for n, primes, spectators in
              ((2, [3], 0), (3, [3], 0), (4, [3], 0), (2, [5], 0),
               (2, [7], 0), (2, [3, 5], 0), (3, [3, 5], 0),
               (2, [3, 5, 7], 0), (2, [3], 2))]
    generic = [[F(2), F(3)], [F(5), F(7)]]
    spectator = [[F(3), F(2)], [F(1), F(5)]]
    rounded = [[F(int(x * 16 + F(1, 2)), 16) for x in row]
               for row in base.gaussian(3, F(1, 2), F(3, 2))]
    matrices = [
        check_matrix("binary-prime3", [base.gaussian(2, F(1, 2))] * 3, [3]),
        check_matrix("shifted-binary-prime5", [base.gaussian(2, F(2, 3), F(5, 4))] * 5, [5]),
        check_matrix("shifted-odd-dimension", [base.gaussian(3, F(1, 2), F(3, 2))] * 3, [3]),
        check_matrix("generic-nonsymmetric", [generic] * 3, [3]),
        check_matrix("arbitrary-spectator", [base.gaussian(2, F(1, 2), F(3, 2))] * 3 +
                     [spectator], [3]),
        check_matrix("common-asymmetric-rounded-table", [rounded] * 3, [3])]
    result = {"status": "PASS", "cycle_fixtures": cycles, "cycle_fixture_count": len(cycles),
              "rational_fixtures": matrices, "rational_fixture_count": len(matrices),
              "rational_targets": 2 * len(matrices), "literal_reconstructions": 2 * len(matrices),
              "modular_pair": modular_pair(), "finite_bertrand_families": family_checks(),
              "controls": controls(), "scope": "bounded exact controls; all-size proof in PRIME-ORBITS.md",
              "new_kappa": False}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
