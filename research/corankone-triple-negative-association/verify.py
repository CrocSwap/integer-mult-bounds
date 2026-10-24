#!/usr/bin/env python3
"""Exact corroboration of the written three-guard negative-association proof.

lee-phys, with substantial OpenAI Codex assistance. Apache-2.0.
Counting formulas: Nick Petalas, PR4227/4261/4275/4777 (see README).
No predecessor code, external data, numerical tolerance, or assertions.
"""

from collections import Counter
from fractions import Fraction as F
from itertools import product
from math import prod
import json


SPECTRA = {
    1: {3: 1},
    2: {9: 1, 7: -2, 5: 1},
    3: {27: 1, 21: -6, 19: 6, 17: -6, 15: 16, 13: -18, 11: 9, 9: -2},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def probability(k, m):
    require(type(k) is int and k in SPECTRA, "kernel domain")
    require(type(m) is int and m >= max(2, k), "dimension domain")
    n, x = m - 1, 2**m
    numerator = sum(c * a**n for a, c in SPECTRA[k].items())
    denominator = prod(x - 2**i for i in range(k)) * 2 ** (k * n)
    return F(numerator, denominator)


def atoms(m):
    p, p2, p3 = (probability(k, m) for k in (1, 2, 3))
    by_weight = (1 - 3*p + 3*p2 - p3, p - 2*p2 + p3, p2 - p3, p3)
    return tuple(by_weight[x.bit_count()] for x in range(8))


def validate_atoms(weights):
    require(len(weights) == 8, "eight atoms required")
    require(all(w >= 0 for w in weights), "negative atom")
    require(sum(weights) == 1, "atom normalization")


def upsets():
    # Generate the monotone Boolean functions, not a hand-selected test list.
    return tuple(mask for mask in range(16) if all(
        not ((x & y) == x and (mask >> x) & 1) or (mask >> y) & 1
        for x in range(4) for y in range(4)
    ))


def covariances(weights):
    validate_atoms(weights)
    answer = []
    for singleton in range(3):
        j, k = (i for i in range(3) if i != singleton)
        ey = sum(w for x, w in enumerate(weights) if (x >> singleton) & 1)
        for mask in upsets():
            if mask in (0, 15):
                continue
            ef, efy = F(0), F(0)
            for x, w in enumerate(weights):
                pair = ((x >> j) & 1) | (((x >> k) & 1) << 1)
                if (mask >> pair) & 1:
                    ef += w
                    if (x >> singleton) & 1:
                        efy += w
            answer.append((singleton, mask, efy - ef*ey))
    return answer


def check_strict_na(weights):
    values = covariances(weights)
    require(len(values) == 12, "increasing-event coverage")
    require(all(c < 0 for _, _, c in values), "nonnegative increasing covariance")


def inverse(rows, m):
    augmented = [row | (1 << (m+i)) for i, row in enumerate(rows)]
    for col in range(m):
        pivot = next((i for i in range(col, m) if (augmented[i] >> col) & 1), None)
        if pivot is None:
            return None
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        for i in range(m):
            if i != col and (augmented[i] >> col) & 1:
                augmented[i] ^= augmented[col]
    return tuple(row >> m for row in augmented)


def multiply(a, b):
    result = []
    for row in a:
        out = 0
        while row:
            bit = row & -row
            out ^= b[bit.bit_length() - 1]
            row ^= bit
        result.append(out)
    return tuple(result)


def rank(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)


def full_guard(rows, m):
    for size in range(1, m):
        mask = (1 << size) - 1
        if rank(tuple(row & mask for row in rows[:size])) != size:
            return False
    return True


def literal_headers(m):
    ident = tuple(1 << i for i in range(m))
    requests = [tuple(v if j != i else 0 for j, v in enumerate(ident))
                for i in range(3)]
    histogram = [0] * 8
    for g in product(range(1 << m), repeat=m):
        inv = inverse(g, m)
        if inv is None:
            continue
        require(multiply(g, inv) == ident, "literal inverse")
        mask = 0
        for i, request in enumerate(requests):
            conjugate = multiply(multiply(g, request), inv)
            mask |= int(full_guard(conjugate, m)) << i
        histogram[mask] += 1
    total = prod(2**m - 2**i for i in range(m))
    require(sum(histogram) == total, "complete GL enumeration")
    observed = tuple(F(c, total) for c in histogram)
    require(observed == atoms(m), "literal header atom law")
    check_strict_na(observed)
    return histogram


def safe_steps(k):
    positions = [(i, j) for i in range(k) for j in range(k) if i != j]
    weights = [0] * (1 << len(positions))
    # Each actual pair (y,x) is counted, including all zero factorizations.
    for y, x in product(range(1 << k), repeat=2):
        if y & x:
            continue
        mask = sum((((y >> i) & 1) * ((x >> j) & 1)) << bit
                   for bit, (i, j) in enumerate(positions))
        weights[mask] += 1
    require(sum(weights) == 3**k, "safe factor count")
    return weights


def character_spectrum(weights):
    result = Counter()
    for character in range(len(weights)):
        eigenvalue = sum(w * (-1)**((character & step).bit_count())
                         for step, w in enumerate(weights))
        result[eigenvalue] += (-1)**character.bit_count()
    return {a: c for a, c in result.items() if c}


def check_spectrum(actual, expected):
    require(actual == expected, "signed character spectrum")


def check_walks():
    checks = 0
    spectra = {}
    for k in (1, 2, 3):
        weights = safe_steps(k)
        spectrum = character_spectrum(weights)
        check_spectrum(spectrum, SPECTRA[k])
        spectra[k] = spectrum
        states = [1] + [0] * (len(weights) - 1)
        nonzero = [(s, w) for s, w in enumerate(weights) if w]
        for n in range(1, 25):
            states = [sum(states[x ^ step] * w for step, w in nonzero)
                      for x in range(len(weights))]
            m = n + 1
            if m < k:
                continue
            denominator = prod(2**m - 2**i for i in range(k)) * 2**(k*(m-k))
            require(F(states[-1], denominator) == probability(k, m), "Gram walk law")
            require(sum(states) == 3**(k*n), "Gram walk total")
            checks += 1
    return checks, spectra


def check_dimensions():
    require(upsets() == (0, 8, 10, 12, 14, 15), "complete Boolean upsets")
    count = 0
    for m in range(3, 257):
        n, x = m - 1, 2**m
        p, p2, p3 = (probability(k, m) for k in (1, 2, 3))
        r, s = F(7, 9)**n, F(5, 9)**n
        delta = 1 - p2/p**2
        require(delta == F((x-1)*(2*r-s)-1, x-2), "pair deficit identity")
        require(delta > r/2 and 0 < p < r, "analytic comparison")
        gap = p*(2*p-p2) - (2*p2-p3)
        require(gap == p**2*((2+p)*delta-p) + p3, "union gap identity")
        require(gap > p**2*(r-p) > 0, "quantitative union bound")
        require(p3 < p*p2, "cited conjunction inequality")
        check_strict_na(atoms(m))
        count += 1
    require(probability(3, 3) == 0, "zero-triple boundary")
    for m, expected in ((3, F(421, 2352)), (4, F(199, 2688))):
        p, p2, p3 = (probability(k, m) for k in (1, 2, 3))
        require(p*(2*p-p2)-(2*p2-p3) == expected, "exact gap fixture")
    return count


def check_cited_tail():
    require(57 * 19**42 < 21**42, "conjunction remainder constant")
    require(3 * 7**42 < 9**42, "positive conjunction upper bound")
    require(14**2 > 2 * 9**2, "finite-GL comparison constant")
    checked = 0
    for m in range(3, 43):
        n, x = m - 1, 2**m
        b = 27**n - 2*21**n + 15**n
        t = sum(c * a**n for a, c in SPECTRA[3].items())
        integer_gap = (x-4)*b - (x-1)*t
        require(b > 0 and integer_gap > 0, "finite conjunction proof case")
        p, p2, p3 = (probability(k, m) for k in (1, 2, 3))
        require(p3/(p*p2) == F(t*(x-1), b*(x-4)), "conjunction ratio normalization")
        checked += 1
    return checked


def expect_rejection(operation, name):
    try:
        operation()
    except ValueError:
        return name
    raise ValueError("control accepted: " + name)


def controls(header4, spectra):
    by_weight = (F(13, 100), F(8, 100), F(21, 100), F(0))
    deceptive = tuple(by_weight[x.bit_count()] for x in range(8))
    values = {(i, mask): c for i, mask, c in covariances(deceptive)}
    require(values[0, 8] == -F(21, 200), "control AND covariance")
    require(values[0, 10] == -F(1, 25), "control pair covariance")
    require(values[0, 14] == F(1, 40), "control OR covariance")
    broken_spectrum = dict(SPECTRA[3])
    broken_spectrum[19] += 1
    wrong_pair = F(9**3 - 2*7**3 + 5**3, 15**2 * 2**6)
    observed_pair = F(sum(c for x, c in enumerate(header4) if x & 3 == 3), sum(header4))
    tests = [
        (lambda: check_strict_na(deceptive), "pair-AND-only false positive"),
        (lambda: check_strict_na((F(1, 2),) + (F(0),)*6 + (F(1, 2),)), "identical events"),
        (lambda: check_strict_na((F(1, 8),)*8), "independence is not strict"),
        (lambda: validate_atoms((F(-1), F(2)) + (F(0),)*6), "negative atom"),
        (lambda: validate_atoms((F(1, 9),)*8), "unnormalized law"),
        (lambda: require(wrong_pair == observed_pair, "finite-GL factor"), "missing GL normalization"),
        (lambda: check_spectrum(spectra[3], broken_spectrum), "changed triple coefficient"),
        (lambda: probability(3, 2), "insufficient dimension"),
        (lambda: probability(3, True), "Boolean dimension"),
    ]
    return [expect_rejection(f, name) for f, name in tests]


def main():
    histograms = {m: literal_headers(m) for m in (3, 4)}
    walk_checks, spectra = check_walks()
    dimensions = check_dimensions()
    finite_cases = check_cited_tail()
    rejected = controls(histograms[4], spectra)
    summary = {
        "literal_header_atoms": histograms,
        "literal_headers": sum(map(sum, histograms.values())),
        "walk_comparisons": walk_checks,
        "three_kernel_signed_spectrum": spectra[3],
        "dimensions_checked": dimensions,
        "strict_covariances_checked": 12 * dimensions,
        "cited_finite_conjunction_cases": finite_cases,
        "rejected_controls": rejected,
    }
    print(json.dumps(summary, sort_keys=True))
    print("PASS_CORANKONE_TRIPLE_NEGATIVE_ASSOCIATION")


if __name__ == "__main__":
    main()
