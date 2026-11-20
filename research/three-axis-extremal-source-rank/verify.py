#!/usr/bin/env python3
"""Complete finite polynomial certificate and exact source checks.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
SPDX-License-Identifier: Apache-2.0
"""
from fractions import Fraction
from hashlib import sha256
from itertools import permutations, product
from math import factorial, isqrt
from pathlib import Path
import json

MODULUS = 1000000007
POINT = ((2, 3), (5, 7), (11, 13))
BAD_ORDER = (0, 1, 2, 4, 6, 5, 3, 7)


class CheckFailure(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise CheckFailure(message)


def prime_by_trial_division(n):
    return n >= 2 and all(n % d for d in range(2, isqrt(n) + 1))


def tensor_entry(row, col, factors, modulus=None):
    result = 1
    for axis, (upper, lower) in enumerate(factors):
        r, c = (row >> (2-axis)) & 1, (col >> (2-axis)) & 1
        result *= 1 if r == c else (upper if r == 0 else lower)
    return result if modulus is None else result % modulus


def displacement(order, factors, modulus):
    require(sorted(order) == list(range(8)), "order must be a permutation")
    return [
        [
            (tensor_entry(order[i], order[j], factors)
             - (tensor_entry(order[i-1], order[j-1], factors) if i and j else 0))
            % modulus
            for j in range(8)
        ]
        for i in range(8)
    ]


def determinant_mod(matrix, modulus):
    a = [row[:] for row in matrix]
    n = len(a)
    result = 1
    for k in range(n):
        pivot_row = next((r for r in range(k, n) if a[r][k]), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            a[k], a[pivot_row] = a[pivot_row], a[k]
            result = -result
        pivot = a[k][k]
        result = result * pivot % modulus
        inverse = pow(pivot, modulus-2, modulus)
        for i in range(k+1, n):
            multiple = a[i][k] * inverse % modulus
            a[i][k] = 0
            for j in range(k+1, n):
                a[i][j] = (a[i][j] - multiple * a[k][j]) % modulus
    return result % modulus


def rank_mod(matrix, modulus):
    a = [row[:] for row in matrix]
    row = 0
    for col in range(len(a[0])):
        pivot = next((r for r in range(row, len(a)) if a[r][col]), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        inv = pow(a[row][col], modulus-2, modulus)
        for i in range(row+1, len(a)):
            scale = a[i][col] * inv % modulus
            for j in range(col, len(a[0])):
                a[i][j] = (a[i][j] - scale*a[row][j]) % modulus
        row += 1
    return row


def complete_order_certificate():
    require(prime_by_trial_division(MODULUS), "field modulus must be prime")
    digest = sha256()
    count = 0
    residues = set()
    for order in permutations(range(8)):
        det = determinant_mod(displacement(order, POINT, MODULUS), MODULUS)
        require(det != 0, "zero generic determinant at order " + str(order))
        digest.update(bytes(order) + det.to_bytes(4, "big"))
        residues.add(det)
        count += 1
    require(count == factorial(8), "complete permutation coverage")
    return {
        "orders": count, "zero_determinants": 0, "modulus": MODULUS,
        "point": POINT, "distinct_residues": len(residues),
        "ordered_residue_sha256": digest.hexdigest(),
        "meaning": "Every formal determinant is a nonzero integer polynomial."
    }


def repeated_monomial(row, col):
    upper = ((~row) & col & 7).bit_count()
    lower = (row & (~col) & 7).bit_count()
    return upper, lower


def repeated_entry(order, i, j):
    out = {repeated_monomial(order[i], order[j]): 1}
    if i and j:
        key = repeated_monomial(order[i-1], order[j-1])
        out[key] = out.get(key, 0)-1
    return {key: value for key, value in out.items() if value}


def strict_box_counterexample():
    for left, right in ((2, 3), (5, 6)):
        require(
            all(repeated_entry(BAD_ORDER, i, left) ==
                repeated_entry(BAD_ORDER, i, right) for i in range(8)),
            "symbolic equal columns"
        )
    u, w = Fraction(2047, 2048), Fraction(1, 4096)
    v = 3*w/2
    require(Fraction(1023, 1024) < u < 1 and 0 < w <= Fraction(1, 2048),
            "strict box fixture")
    require(w < v < 2*w, "strict lower-entry box fixture")
    fu = 2047*pow(2048, MODULUS-2, MODULUS) % MODULUS
    fv = 3*pow(8192, MODULUS-2, MODULUS) % MODULUS
    e = displacement(BAD_ORDER, ((fu, fv),)*3, MODULUS)
    require(rank_mod(e, MODULUS) == 6, "strict rational fixture has rank six")
    return {
        "order": BAD_ORDER, "equal_column_pairs": [[2, 3], [5, 6]],
        "identity": "Bivariate polynomial identities, all u and v.",
        "strict_fixture": {"u": str(u), "v": str(v), "w": str(w), "rank": 6}
    }


def nearest(s, t, j):
    return (2*t*j+s)//(2*s)


def literal_exponent(s, t, j, k):
    return Fraction(
        (t*k-s*nearest(s,t,j))**2 - (t*k-s*nearest(s,t,k))**2,
        s*s
    )


def source_checks():
    # Proth-style certificates: k odd, k < 2^m, s=k*2^m+1,
    # and witness^((s-1)/2)=-1 mod s imply every prime divisor > sqrt(s).
    fixtures = [
        {"m": 32, "k": 4294967221, "witness": 3},
        {"m": 32, "k": 4294967203, "witness": 3},
        {"m": 32, "k": 4294967187, "witness": 5}
    ]
    p, t = 4096, 1 << 64
    rows = []
    for fixture in fixtures:
        m, k, witness = (fixture[x] for x in ("m", "k", "witness"))
        s = k*(1 << m)+1
        require(k % 2 == 1 and 0 < k < 1 << m, "exact prime structure")
        require(pow(witness, (s-1)//2, s) == s-1, "exact primality certificate")
        require(s >= p**4, "source lower size")
        require((1-Fraction(1,2*p*p))*t < s <=
                (1-Fraction(1,4*p*p))*t, "fine-prime interval")
        delta = t-s
        A, B = 2*delta+1, 2*s-1
        i = (-(s-1)//2)*pow(delta, -1, s) % s
        require(0 <= i < s-1, "selected pair stays in finite source")
        require(t*i-s*nearest(s,t,i) == -(s-1)//2, "extremal source phase")
        require(nearest(s,t,i+1) == nearest(s,t,i)+1, "same-cell pair")
        require(literal_exponent(s,t,i,i+1) == Fraction(A,s), "upper coefficient")
        require(literal_exponent(s,t,i+1,i) == Fraction(B,s), "lower coefficient")
        require(A > 8 and 8*A+8 < s, "degree-eight uniform guard")
        require(len({(u*A+v*B) % s for u,v in product(range(9), repeat=2)}) == 81,
                "degree-eight source injection")
        rows.append({**fixture, "p":p, "t":t, "s":s, "A":A, "B":B, "index":i})
    require(len({row["s"] for row in rows}) == 3, "three distinct source primes")
    # Elementary bounds 0.69 < ln 2 < 0.70 and 3 < pi < 22/7
    # give 9 < (4/pi) ln(16p) < 16 here, certifying alpha=4.
    require(9 < Fraction(4*16*69,100)/Fraction(22,7), "alpha lower bound")
    require(Fraction(4*16*70,100)/3 < 16, "alpha upper bound")
    return {"fixtures":rows, "degree_box_values_per_axis":81, "alpha":4,
            "scope":"Exact source-grid and prime guards, not transcendence numerics."}


def negative_controls():
    out = []
    require(not prime_by_trial_division(1000000005), "composite modulus rejected")
    out.append("composite field modulus")
    try:
        displacement((0,1,2,3,4,5,6,6), POINT, MODULUS)
    except CheckFailure:
        out.append("nonpermutation order")
    else:
        raise CheckFailure("invalid order unexpectedly accepted")
    require(determinant_mod(displacement(BAD_ORDER, ((2,3),)*3, MODULUS),
                            MODULUS) == 0, "equal-factor mutant")
    out.append("equal-factor all-order full-rank claim")
    # Degree guard cannot be discarded: 81 formal exponent pairs collide
    # on this 17-residue source even though s is prime and t is dyadic.
    s, t = 17, 32
    A, B = 2*(t-s)+1, 2*s-1
    require(len({(u*A+v*B)%s for u,v in product(range(9),repeat=2)}) < 81,
            "degree-box collision control")
    out.append("unqualified source-prime exponent injection")
    # Reusing a denominator makes swapping the first two axis exponents
    # an exact collision; distinct primes are essential to this proof.
    s, A, B = 17, 31, 33
    monomials = ((1,0,0,0),(0,0,1,0))
    weights = (A*s,B*s,A*s,B*s)
    images = {sum(e*w for e,w in zip(m,weights)) for m in monomials}
    require(len(set(monomials)) == 2 and len(images) == 1,
            "repeated denominator collision")
    out.append("repeated-axis denominator loses CRT isolation")
    # Removing the Stein subtraction changes a defining diagonal entry.
    h = [[tensor_entry(i,j,POINT) for j in range(8)] for i in range(8)]
    e = displacement(tuple(range(8)), POINT, MODULUS)
    require(h[1][1] == 1 and e[1][1] == 0,
            "source matrix is not its displacement")
    out.append("omitted predecessor subtraction")
    return out


def authenticate():
    root = Path(__file__).resolve().parent
    pins = json.loads((root/"DEPENDENCIES.json").read_text())
    for item in pins["files"]:
        data = (root/item["local"]).read_bytes()
        require(len(data) == item["bytes"] and sha256(data).hexdigest() == item["sha256"],
                "source authentication " + item["local"])
    return len(pins["files"])


def main():
    result = {
        "status":"PASS_THREE_AXIS_EXTREMAL_SOURCE_RANK",
        "authenticated_inputs":authenticate(),
        "all_orders":complete_order_certificate(),
        "strict_box":strict_box_counterexample(),
        "source":source_checks(),
        "negative_controls":negative_controls(),
        "scope":"Exact three-axis source rank only; no quantitative, alias, rounded or kappa claim."
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
