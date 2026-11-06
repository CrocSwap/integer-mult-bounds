#!/usr/bin/env python3
"""Exact finite corroboration for the capped corank-one spectral theorem.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Standalone Python 3.12 standard library; no predecessor code or runtime inputs.
"""

import itertools
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_matrix(rows, r):
    require(isinstance(rows, tuple) and len(rows) == r, "matrix dimension")
    require(all(type(v) is int and 0 <= v < (1 << r) for v in rows),
            "binary matrix row encoding")
    return rows


def identity(r):
    return tuple(1 << j for j in range(r))


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b, strict=True))


def multiply(a, b):
    result = []
    for row in a:
        value = 0
        while row:
            bit = row & -row
            value ^= b[bit.bit_length() - 1]
            row ^= bit
        result.append(value)
    return tuple(result)


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)


def inverse(rows):
    r = len(rows)
    work = [row | (1 << (r + j)) for j, row in enumerate(rows)]
    for column in range(r):
        pivot = next((j for j in range(column, r)
                      if (work[j] >> column) & 1), None)
        require(pivot is not None, "singular basis map")
        work[column], work[pivot] = work[pivot], work[column]
        for j in range(r):
            if j != column and ((work[j] >> column) & 1):
                work[j] ^= work[column]
    result = tuple(row >> r for row in work)
    require(multiply(rows, result) == identity(r), "basis inverse")
    return result


def profile(rows):
    """Return zero multiplicity, zero-primary cap, and all power nullities."""
    r = len(rows)
    power = identity(r)
    nullities = [0]
    for _ in range(r):
        power = multiply(power, rows)
        nullities.append(r - rank(power))
    z = nullities[-1]
    cap = nullities.index(z)
    increments = [nullities[j + 1] - nullities[j] for j in range(r)]
    require(all(x >= y for x, y in zip(increments, increments[1:])),
            "power nullities are not a nilpotent partition")
    return z, cap, tuple(nullities)


def polynomial_multiply(a, b):
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        b >>= 1
    return result


def characteristic_polynomial(rows):
    """Independent Leibniz determinant of tI+X over F2; no power or rank calls."""
    r = len(rows)
    determinant = 0
    for permutation in itertools.permutations(range(r)):
        term = 1
        for i, j in enumerate(permutation):
            factor = ((rows[i] >> j) & 1) | (2 if i == j else 0)
            term = polynomial_multiply(term, factor)
            if not term:
                break
        determinant ^= term
    require(determinant.bit_length() == r + 1, "characteristic degree")
    return determinant


def domain(r, cap):
    require(type(r) is int and 1 <= r <= 33, "dimension outside finite verifier")
    require(type(cap) is int and 1 <= cap <= r, "cap outside domain")


def sharp_bound(r, cap):
    domain(r, cap)
    return r + cap - (1 if cap % 2 == 0 else 0)


def witness(r, cap):
    domain(r, cap)
    ell = cap - (1 if cap % 2 == 0 else 0)
    upper = tuple(((1 << ell) - 1) ^ ((1 << (j + 1)) - 1)
                  for j in range(ell))
    lower = tuple((1 << j) - 1 for j in range(ell))
    basis = tuple((1 << j) | (1 << (ell - 1)) for j in range(ell - 1))
    basis += ((1 << ell) - 1,)
    # Transpose the displayed basis columns to this verifier's row encoding.
    basis = tuple(sum(((basis[j] >> i) & 1) << j for j in range(ell))
                  for i in range(ell))
    inv = inverse(basis)
    core_a = multiply(multiply(inv, upper), basis)
    core_b = multiply(multiply(inv, lower), basis)
    positions = tuple(range(ell - 1)) + (r - 1,)
    a, b = [0] * r, [0] * r
    for i, target in enumerate(positions):
        a[target] = sum(((core_a[i] >> j) & 1) << positions[j]
                        for j in range(ell))
        b[target] = sum(((core_b[i] >> j) & 1) << positions[j]
                        for j in range(ell))
    for j in range(ell - 1, r - 1):
        b[j] = 1 << j
    return tuple(a), tuple(b)


def check_pair(r, cap, a, b, expected=None):
    domain(r, cap)
    checked_matrix(a, r)
    checked_matrix(b, r)
    endpoint = identity(r - 1) + (0,)
    require(add(a, b) == endpoint, "wrong coordinate endpoint")
    require(multiply(endpoint, endpoint) == endpoint, "nonidempotent endpoint")
    require(rank(endpoint) == r - 1, "wrong endpoint corank")
    pa, pb = profile(a), profile(b)
    require(pa[1] <= cap and pb[1] <= cap, "zero-primary chain cap violated")
    value = pa[0] + pb[0]
    require(value <= sharp_bound(r, cap), "sharp upper bound violated")
    if expected is not None:
        require(type(expected) is int and value == expected, "wrong claimed value")
    return {"z": [pa[0], pb[0]], "nu0": [pa[1], pb[1]], "value": value}


def check_cap_two_pair(r, k, a, b, expected=None):
    domain(r, 1)
    require(type(k) is int and 0 <= k <= r, "endpoint rank outside domain")
    checked_matrix(a, r)
    checked_matrix(b, r)
    d = identity(k) + (0,) * (r - k)
    require(add(a, b) == d, "wrong general-rank endpoint")
    pa, pb = profile(a), profile(b)
    require(pa[1] <= 2 and pb[1] <= 2, "cap-two hypothesis violated")
    squares = add(multiply(a, a), multiply(b, b))
    require(multiply(multiply(d, squares), d) == d, "compression identity")
    value = pa[0] + pb[0]
    require(value <= 2*r-k, "general-rank cap-two bound")
    if expected is not None:
        require(type(expected) is int and value == expected, "wrong cap-two value")
    return value


def complete_census():
    records, general_records, matrix_count, cap_pair_count = [], [], 0, 0
    general_pair_count = 0
    for r in range(1, 5):
        mask = (1 << r) - 1
        profiles, squares = [], []
        for encoded in range(1 << (r * r)):
            rows = tuple((encoded >> (j * r)) & mask for j in range(r))
            p = profile(rows)
            polynomial = characteristic_polynomial(rows)
            zero_order = (polynomial & -polynomial).bit_length() - 1
            require(p[0] == zero_order, "rank/characteristic-polynomial disagreement")
            profiles.append(p[:2])
            squares.append(multiply(rows, rows))
        diagonal = sum(1 << (j * r + j) for j in range(r - 1))
        for cap in range(1, r + 1):
            maximum, maximizers, admissible = -1, 0, 0
            for encoded, (za, ca) in enumerate(profiles):
                zb, cb = profiles[encoded ^ diagonal]
                if ca > cap or cb > cap:
                    continue
                admissible += 1
                value = za + zb
                if value > maximum:
                    maximum, maximizers = value, 1
                elif value == maximum:
                    maximizers += 1
            require(maximum == sharp_bound(r, cap), "census does not attain theorem")
            records.append({"r": r, "cap": cap, "maximum": maximum,
                            "maximizers": maximizers, "admissible_pairs": admissible})
            cap_pair_count += len(profiles)
        for k in range(r + 1):
            delta = sum(1 << (j*r+j) for j in range(k))
            maximum, maximizers, admissible = -1, 0, 0
            for encoded, (za, ca) in enumerate(profiles):
                compressed = tuple((x ^ y) & ((1 << k)-1) if j < k else 0
                                   for j, (x, y) in enumerate(zip(
                                       squares[encoded], squares[encoded ^ delta], strict=True)))
                require(compressed == identity(k)+(0,)*(r-k),
                        "all-pair square compression identity")
                zb, cb = profiles[encoded ^ delta]
                if ca > 2 or cb > 2:
                    continue
                admissible += 1
                value = za + zb
                if value > maximum:
                    maximum, maximizers = value, 1
                elif value == maximum:
                    maximizers += 1
            require(maximum == 2*r-k, "general-rank cap-two census")
            general_records.append({"r": r, "k": k, "maximum": maximum,
                                    "maximizers": maximizers, "admissible_pairs": admissible})
            general_pair_count += len(profiles)
        matrix_count += len(profiles)
    return {"matrices_and_polynomial_checks": matrix_count,
            "ordered_pairs": matrix_count, "pair_cap_checks": cap_pair_count,
            "records": records, "cap_two_all_rank_pairs": general_pair_count,
            "all_pair_compression_identity_checks": general_pair_count,
            "cap_two_all_rank_records": general_records}


def constructed_witnesses():
    count, general_count, sample = 0, 0, []
    require(witness(5, 4) == ((19, 1, 0, 0, 18), (18, 3, 4, 8, 18)),
            "documented cap-four coordinate witness")
    for r in range(1, 34):
        for cap in range(1, r + 1):
            a, b = witness(r, cap)
            result = check_pair(r, cap, a, b, sharp_bound(r, cap))
            count += 1
            if r == 5:
                sample.append({"cap": cap, "A": a, "B": b, **result})
        for k in range(r + 1):
            check_cap_two_pair(r, k, (0,)*r, identity(k)+(0,)*(r-k), 2*r-k)
            general_count += 1
    return {"count": count, "r_max": 33, "r5": sample,
            "cap_two_all_rank_count": general_count}


def expect_rejection(label, function, args):
    try:
        function(*args)
    except ValueError:
        return label
    raise ValueError("accepted rejecting control: " + label)


def rejection_controls():
    a, b = witness(5, 4)
    full_a, full_b = witness(5, 5)
    controls = [
        ("zero cap", sharp_bound, (5, 0)),
        ("cap above dimension", sharp_bound, (5, 6)),
        ("Boolean dimension", sharp_bound, (True, 1)),
        ("noninteger cap", sharp_bound, (5, 2.5)),
        ("wrong row dimension", check_pair, (5, 4, a[:-1], b)),
        ("row outside binary width", check_pair, (5, 4, (32,) + a[1:], b)),
        ("Boolean matrix entry", check_pair, (5, 4, (True,) + a[1:], b)),
        ("corrupted endpoint", check_pair, (5, 4, (a[0] ^ 1,) + a[1:], b)),
        ("geometric nullity is not chain cap", check_pair, (5, 4, full_a, full_b)),
        ("forged cap-four witness value nine", check_pair, (5, 4, a, b, 9)),
        ("forged cap-four witness value ten", check_pair, (5, 4, a, b, 10)),
        ("cap-two cannot import triple witness", check_pair, (5, 2, a, b)),
        ("negative endpoint rank", check_cap_two_pair, (3, -1, (0,)*3, (0,)*3)),
        ("endpoint rank exceeds dimension", check_cap_two_pair, (3, 4, (0,)*3, (0,)*3)),
        ("cap-three defeats all-rank cap-two bound", check_cap_two_pair,
         (3, 2, *witness(3, 3))),
    ]
    result = [expect_rejection(*control) for control in controls]
    require(profile(full_a)[2][1] == profile(full_b)[2][1] == 1,
            "full-chain control must pass the misleading geometric-nullity test")
    require(profile(b)[0] < 5, "attaining cap-four witness must not be globally nilpotent")
    triple_a, triple_b = witness(3, 3)
    require((triple_a, triple_b) == ((7, 1, 6), (6, 3, 6)),
            "documented cap-three counterexample")
    require(profile(triple_a)[:2] == profile(triple_b)[:2] == (3, 3),
            "cap-three counterexample indices and multiplicities")
    require(sum(profile(x)[0] for x in (triple_a, triple_b)) == 6 > 2*3-2,
            "cap-three counterexample must defeat cap-two conclusion")
    return result


def main():
    report = {"claim": "sharp corank-one capped spectrum and all-rank cap-two spectrum",
              "field_of_finite_checks": "F2", "census": complete_census(),
              "construction": constructed_witnesses(),
              "rejection_controls": rejection_controls()}
    report["marker"] = "PASS_CAPPED_SHARED_BLOCK_SPECTRUM"
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
