#!/usr/bin/env python3
"""Check the exact Newton Fourier identity and its precision bill."""

from fractions import Fraction as F
from math import isqrt
from pathlib import Path
import hashlib
import json
import os
import platform
import resource
import time


class Cyclotomic:
    def __init__(self, q, a=1):
        self.q = q
        self.a = a
        self.zero = (F(),)*q
        self.one = self.root(0)

    def reduce(self, a):
        last = a[-1]
        return tuple(x-last for x in a)

    def root(self, exponent):
        a = [F()]*self.q
        a[self.a*exponent % self.q] = F(1)
        return self.reduce(a)

    def add(self, a, b):
        return tuple(x+y for x, y in zip(a, b))

    def scale(self, a, c):
        return tuple(c*x for x in a)

    def multiply(self, a, b):
        out = [F()]*self.q
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                out[(i+j) % self.q] += x*y
        return self.reduce(out)

    def inverse_one_minus_root(self, j):
        assert j % self.q
        out = [F()]*self.q
        for k in range(self.q):
            out[self.a*j*k % self.q] += F(self.q-1-k, self.q)
        result = self.reduce(out)
        value = self.add(self.one, self.scale(self.root(j), -1))
        assert self.multiply(value, result) == self.one
        return result


def check_identity(q, a=1):
    field = Cyclotomic(q, a)
    n = [[field.zero for j in range(q)] for i in range(q)]
    diagonal_inverse = []
    for i in range(q):
        inverse = field.one
        for j in range(i):
            factor_inverse = field.multiply(field.root(-j), field.inverse_one_minus_root(i-j))
            inverse = field.multiply(inverse, field.scale(factor_inverse, -1))
        diagonal_inverse.append(inverse)
        for k in range(i+1):
            value = field.one
            for j in range(k):
                difference = field.add(field.root(i), field.scale(field.root(j), -1))
                value = field.multiply(value, difference)
            n[i][k] = value
        assert field.multiply(n[i][i], inverse) == field.one
    omitted_diagonal_failures = 0
    for i in range(q):
        for j in range(q):
            actual = field.zero
            wrong = field.zero
            for k in range(min(i, j)+1):
                term = field.multiply(n[i][k], n[j][k])
                wrong = field.add(wrong, term)
                actual = field.add(actual, field.multiply(term, diagonal_inverse[k]))
            assert actual == field.root(i*j)
            omitted_diagonal_failures += wrong != field.root(i*j)
    assert omitted_diagonal_failures > 0
    inverse_a = pow(a, -1, q)
    standard = Cyclotomic(q)
    for k in range(q):
        for j in range(q):
            assert field.root((inverse_a*k % q)*j) == standard.root(k*j)
    h = [field.one]
    for j in range(1, q):
        h.append(field.multiply(h[-1], field.inverse_one_minus_root(j)))
    g = [field.scale(field.multiply(field.root(j*(j-1)//2), h[j]), (-1)**j) for j in range(q)]
    for j in range(q):
        total = field.zero
        for k in range(j+1):
            total = field.add(total, field.multiply(g[k], h[j-k]))
        assert total == (field.one if j == 0 else field.zero)
    full_product = []
    for j in range(2*q-1):
        total = field.zero
        for k in range(q):
            if 0 <= j-k < q:
                total = field.add(total, field.multiply(g[k], h[j-k]))
        full_product.append(total)
    assert full_product[-1] == field.scale(field.root(1), F(1, q*q))
    assert full_product[q] == field.scale(field.one, -F(q-1, 2*q))
    if q == 3:
        assert full_product == [field.one, field.zero, field.zero,
                                field.scale(field.one, -F(1, 3)),
                                field.scale(field.root(1), F(1, 9))]
    return {"prime": q, "primitive_power": a, "exact_matrix_entries": q*q,
            "omitted_diagonal_failures": omitted_diagonal_failures,
            "nonzero_full_product_degrees": [j for j, v in enumerate(full_product) if v != field.zero],
            "degree_q_coefficient": str(-F(q-1, 2*q)),
            "highest_degree": 2*q-2, "highest_coefficient": "u/q^2"}


def good_rotation(q, a, b):
    return all(b*j*min(a*j % q, q-a*j % q) >= q for j in range(1, q))


def select_rotation(q):
    assert all(q % j for j in range(2, 1+isqrt(q)))
    h = (q-1).bit_length()
    b = 16*h
    a = next(a for a in range(1, q) if good_rotation(q, a, b))
    assert a < q//2+1
    numerator, denominator = q, a
    partials = []
    while denominator:
        term, remainder = divmod(numerator, denominator)
        partials.append(term)
        numerator, denominator = denominator, remainder
    assert len(partials) <= 2*h+1
    assert max(partials) <= b
    previous, current = 0, 1
    for term in partials:
        nxt = term*current+previous
        assert nxt <= b*current
        previous, current = current, nxt
    assert current == q
    harmonic = sum((F(1, j) for j in range(1, q)), F())
    assert F(2*q, b)*harmonic < q-1
    discrepancies = []
    for length in sorted({q//3, q//2, q-1}):
        points = sorted(a*j % q for j in range(1, length+1))
        numerator_bound = max(max(abs(q*i-length*x), abs(q*(i+1)-length*x)) for i, x in enumerate(points))
        value = F(numerator_bound, q)
        assert value <= 480*h*h
        discrepancies.append({"prefix": length, "interval_discrepancy": str(value)})
    return {"prime": q, "primitive_power": a, "h": h, "B": b,
            "partial_quotients": partials, "sample_discrepancies": discrepancies,
            "H_log2_magnitude_bound": 1000*h**3}


def first_odd_primes(count):
    result = []
    candidate = 3
    while len(result) < count:
        if all(candidate % j for j in range(2, 1+isqrt(candidate))):
            result.append(candidate)
        candidate += 2
    return result


def check_peak(q):
    i, k = (q-1)//2, q//6
    assert q >= 7 and k >= 1
    for j in range(k):
        angle = F(i-j, q)
        assert F(1, 3) <= angle <= F(1, 2)
    assert 3**k > 2**k
    return k


def main():
    directory = Path(__file__).resolve().parent
    stat = os.statvfs(directory)
    assert stat.f_bavail*stat.f_frsize >= 3*1024**3
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    started = time.perf_counter()
    identities = [check_identity(q, a) for q in (3, 5, 7, 11) for a in (1, 2)]
    primes = first_odd_primes(256)
    for q in primes:
        if q >= 7:
            check_peak(q)
    bills = []
    for count in (8, 16, 32, 64, 128, 256):
        working_length = 1
        gamma = F()
        for q in primes[:count]:
            working_length *= q
            if q >= 7:
                gamma += F(q//6, 2)
        p = working_length.bit_length()
        bills.append({"prime_axes": count, "working_length_bits": p,
                      "growth_bits_lower_bound": str(gamma),
                      "growth_after_one_over_working_length": str(gamma-p)})
    assert F(bills[-1]["growth_after_one_over_working_length"]) > bills[-1]["working_length_bits"]
    rotations = [select_rotation(q) for q in (101, 257, 509, 1009, 2017, 4099, 8191)]
    assert not good_rotation(257, 1, 16*(257-1).bit_length())
    raw_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss = raw_rss if platform.system() == "Darwin" else raw_rss*1024
    assert rss < 512*1024**2
    result = {"status": "PASS", "scope": "Exact Newton identity, scoped canonical-root bill, and a uniform root choice; no full cyclic supplier gain",
              "identities": identities, "exact_entries": sum(a["exact_matrix_entries"] for a in identities),
              "angle_cases": sum(q >= 7 for q in primes), "precision_bills": bills,
              "selected_rotations": rotations,
              "elapsed_seconds": round(time.perf_counter()-started, 6), "max_rss_bytes": rss,
              "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
