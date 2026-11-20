#!/usr/bin/env python3
"""Fixed-order polynomial, exact rational margin and source-guard checks.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
SPDX-License-Identifier: Apache-2.0
"""
from collections import defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

ORDER = (0, 1, 2, 4, 6, 5, 3, 7)
REVERSE = tuple(reversed(ORDER))
ZERO = (0,) * 6
MASS_TABLE = {
    2: (16, 16), 3: (165, 224), 4: (580, 1246),
    5: (1029, 3658), 6: (1425, 7104), 7: (1532, 8878),
    8: (1313, 7410), 9: (889, 4070), 10: (437, 1370),
    11: (134, 246), 12: (9, 16),
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def clean(poly):
    return {key: value for key, value in poly.items() if value}


def add(p, q, sign=1):
    out = p.copy()
    for key, value in q.items():
        out[key] = out.get(key, 0) + sign * value
    return clean(out)


def multiply(p, q):
    out = defaultdict(int)
    for first, a in p.items():
        for second, b in q.items():
            out[tuple(x+y for x, y in zip(first, second))] += a*b
    return clean(out)


def variable(index):
    key = [0] * 6
    key[index] = 1
    return {tuple(key): 1}


def tensor_monomial(row, col):
    # High-bit order is physical axis 0, then 1, then 2.
    result = []
    for bit in (2, 1, 0):
        r, c = (row >> bit) & 1, (col >> bit) & 1
        result.extend((int(r == 0 and c == 1), int(r == 1 and c == 0)))
    return tuple(result)


def polynomial_displacement(order):
    require(sorted(order) == list(range(8)), "order is a permutation")
    matrix = []
    for i in range(8):
        row = []
        for j in range(8):
            entry = {tensor_monomial(order[i], order[j]): 1}
            if i and j:
                entry = add(entry, {tensor_monomial(order[i-1], order[j-1]): 1}, -1)
            row.append(entry)
        matrix.append(row)
    return matrix


def polynomial_determinant(matrix):
    # Laplace expansion on the last row of each leading-row submatrix.
    values = {0: {ZERO: 1}}
    for mask in range(1, 1 << 8):
        row = mask.bit_count() - 1
        out = {}
        for col in range(8):
            if mask & (1 << col):
                sign = -1 if (mask >> (col+1)).bit_count() % 2 else 1
                term = multiply(values[mask ^ (1 << col)], matrix[row][col])
                out = add(out, term, sign)
        values[mask] = out
    return values[255]


def polynomial_digest(poly):
    data = [[list(key), poly[key]] for key in sorted(poly)]
    return sha256(json.dumps(data, separators=(",", ":")).encode()).hexdigest()


def polynomial_checks():
    direct = polynomial_determinant(polynomial_displacement(ORDER))
    reverse = polynomial_determinant(polynomial_displacement(REVERSE))
    swapped = {(key[4], key[5], key[2], key[3], key[0], key[1]): value
               for key, value in direct.items()}
    require(reverse == swapped, "complete reverse/outer-axis identity")
    u, v, x, y, r, z = [variable(i) for i in range(6)]
    expected = multiply(
        multiply(add(u, r, -1), add(multiply(u, r), multiply(x, x))),
        multiply(add(multiply(x, y), multiply(u, v), -1),
                 add(multiply(x, y), multiply(r, z), -1)),
    )
    by_degree = defaultdict(dict)
    for key, value in direct.items():
        by_degree[key[1]+key[3]+key[5]][key] = value
    require(0 not in by_degree and 1 not in by_degree, "no degree-zero/one terms")
    require(by_degree[2] == expected, "exact leading factorization")
    table = {d: (len(poly), sum(map(abs, poly.values())))
             for d, poly in by_degree.items()}
    require(table == MASS_TABLE, "complete coefficient mass table")
    require(len(direct) == 7529, "complete nonzero term count")
    weighted = sum((1 << d)*mass for d, (_, mass) in table.items() if d >= 3)
    require(weighted == 7682848 and weighted < 1 << 23, "remainder budget")
    collapsed = defaultdict(int)
    for key, value in direct.items():
        collapsed[(key[0]+key[2]+key[4], key[1]+key[3]+key[5])] += value
    require(not clean(collapsed), "repeated factors give identically zero determinant")
    require(weighted > 1 << 22, "undercharged remainder mutant is rejected")
    return {
        "variables": ["u", "v", "x", "y", "r", "z"],
        "order": ORDER, "reverse_order": REVERSE, "nonzero_terms": len(direct),
        "polynomial_sha256": polynomial_digest(direct),
        "reverse_polynomial_sha256": polynomial_digest(reverse),
        "leading_factorization": "(u-r)(ur+x^2)(xy-uv)(xy-rz)",
        "lower_degree_counts_and_masses": table,
        "weighted_remainder_mass": weighted,
        "meaning": "Complete six-variable integer-polynomial identities, not interpolation."
    }


def kronecker(a, b):
    return [[x*y for x in ra for y in rb] for ra in a for rb in b]


def tensor(factors):
    result = [[Q(1)]]
    for factor in factors:
        result = kronecker(result, factor)
    return result


def displacement(matrix, order):
    permuted = [[matrix[i][j] for j in order] for i in order]
    return [[permuted[i][j] - (permuted[i-1][j-1] if i and j else 0)
             for j in range(len(order))] for i in range(len(order))]


def determinant(matrix):
    a = [list(map(Q, row)) for row in matrix]
    result = Q(1)
    for k in range(len(a)):
        row = next((i for i in range(k, len(a)) if a[i][k]), None)
        if row is None:
            return Q(0)
        if row != k:
            a[k], a[row] = a[row], a[k]
            result = -result
        pivot = a[k][k]
        result *= pivot
        for i in range(k+1, len(a)):
            scale = a[i][k]/pivot
            for j in range(k+1, len(a)):
                a[i][j] -= scale*a[k][j]
    return result


def inverse(matrix):
    n = len(matrix)
    a = [[Q(v) for v in row]+[Q(i == j) for j in range(n)]
         for i, row in enumerate(matrix)]
    for k in range(n):
        row = next(i for i in range(k, n) if a[i][k])
        a[k], a[row] = a[row], a[k]
        pivot = a[k][k]
        a[k] = [v/pivot for v in a[k]]
        for i in range(n):
            if i != k:
                scale = a[i][k]
                a[i] = [v-scale*w for v, w in zip(a[i], a[k])]
    return [row[n:] for row in a]


def positive_definite(matrix):
    # Exact LDL pivots; positive pivots certify a real symmetric matrix.
    a = [row[:] for row in matrix]
    for k in range(len(a)):
        pivot = a[k][k]
        if pivot <= 0:
            return False
        for i in range(k+1, len(a)):
            for j in range(i, len(a)):
                a[i][j] -= a[i][k]*a[j][k]/pivot
                a[j][i] = a[i][j]
    return True


def require_singular_margin(matrix, bound):
    n = len(matrix)
    gram = [[sum(matrix[k][i]*matrix[k][j] for k in range(n))
             - (bound*bound if i == j else 0)
             for j in range(n)] for i in range(n)]
    require(positive_definite(gram), "exact positive Gram margin")


def box_guards(uppers, lowers, w, h):
    return (
        0 < w <= 1 and h > 0
        and all(Q(3, 4) <= u <= 1 for u in uppers)
        and all(w <= v <= 2*w for v in lowers)
        and abs(uppers[0]-uppers[2]) >= h
        and abs(uppers[1]*lowers[1]-uppers[0]*lowers[0]) >= w*h
        and abs(uppers[1]*lowers[1]-uppers[2]*lowers[2]) >= w*h
        and w <= h**3/(1 << 24)
    )


def rational_margin_checks():
    rows = []
    for h_bits, w_bits in ((12, 70), (20, 100)):
        h, w = Q(1, 1 << h_bits), Q(1, 1 << w_bits)
        uppers, lowers = [1-3*h, 1-2*h, 1-h], [w]*3
        require(box_guards(uppers, lowers, w, h), "rational separated-box fixture")
        bound = h**3*w**2/2
        factors = [[[Q(1), u], [v, Q(1)]] for u, v in zip(uppers, lowers)]
        matrix = tensor(factors)
        inv = inverse(matrix)
        matrix_det = determinant(matrix)
        forward_dets = {}
        for order in (ORDER, REVERSE):
            e = displacement(matrix, order)
            einv = displacement(inv, order)
            det = determinant(e)
            reverse_det = determinant(displacement(matrix, tuple(reversed(order))))
            require(abs(det) >= bound, "continuous-box determinant lower bound")
            require(determinant(einv) == reverse_det/matrix_det**2,
                    "inverse determinant requires reversal")
            require_singular_margin(e, bound/(1 << 21))
            require_singular_margin(einv, bound/(1 << 49))
            forward_dets[order] = det
        require(forward_dets[ORDER] != forward_dets[REVERSE],
                "omitting reversal changes the inverse identity")
        zeta = bound/(1 << 71)
        perturbed = tensor([[[1+zeta, u-zeta], [v+zeta, 1-zeta]]
                            for u, v in zip(uppers, lowers)])
        error = max(abs(perturbed[i][j]-matrix[i][j])
                    for i in range(8) for j in range(8))
        require(error <= 7*zeta < bound/(1 << 68), "factor-to-tensor perturbation bill")
        inv_perturbed = inverse(perturbed)
        for order in (ORDER, REVERSE):
            require_singular_margin(displacement(perturbed, order), bound/(1 << 22))
            require_singular_margin(displacement(inv_perturbed, order), bound/(1 << 50))
        require(not box_guards([uppers[0]]*3, lowers, w, h),
                "equal-factor gap control")
        require(not box_guards(uppers, [Q(1, 8)]*3, Q(1, 8), h),
                "remainder-smallness control")
        rows.append({"h": str(h), "w": str(w), "D_box": str(bound),
                     "orders": 2, "stable_gram_checks": 4, "perturbed_gram_checks": 4,
                     "factor_error": str(zeta)})
    coarse = tensor([[[1, 1], [0, 1]]]*3)
    require(determinant(displacement(coarse, ORDER)) == 0,
            "coarse rounding destroys displacement rank")
    return rows


def nearest(s, t, j):
    return (2*t*j+s)//(2*s)


def literal_exponent(s, t, j, k):
    return Q((t*k-s*nearest(s, t, j))**2-(t*k-s*nearest(s, t, k))**2, s*s)


def source_checks():
    p, t = 4096, 1 << 64
    fixtures = [(32, 4294967221, 3), (32, 4294967203, 3), (34, 1073741793, 5)]
    subintervals = [(19, 17), (25, 23), (31, 29)]
    rows = []
    for (m, k, witness), (lo, hi) in zip(fixtures, subintervals):
        s = k*(1 << m)+1
        require(k % 2 == 1 and 0 < k < 1 << m, "Proth structure")
        require(pow(witness, (s-1)//2, s) == s-1, "exact prime certificate")
        require(s >= p**4 and s % 2 == 1, "source size and oddness")
        require((1-Q(1, 2*p*p))*t < s <= (1-Q(1, 4*p*p))*t, "fine-prime interval")
        require((1-Q(lo, 64*p*p))*t < s <= (1-Q(hi, 64*p*p))*t,
                "separated prime subinterval")
        delta = t-s
        i = (-(s-1)//2)*pow(delta, -1, s) % s
        require(0 <= i < s-1, "nonwrapping source pair")
        require(t*i-s*nearest(s, t, i) == -(s-1)//2, "extremal physical phase")
        require(nearest(s, t, i+1) == nearest(s, t, i)+1, "same-cell phase step")
        A, B = 2*delta+1, 2*s-1
        require(literal_exponent(s, t, i, i+1) == Q(A, s), "literal upper exponent")
        require(literal_exponent(s, t, i+1, i) == Q(B, s), "literal lower exponent")
        require(A+B == 2*t, "coupled source exponent identity")
        rows.append({"p": p, "t": t, "s": s, "m": m, "k": k,
                     "prime_witness": witness, "index": i, "A": A, "B": B})
    gaps = [abs(rows[i]["s"]-rows[j]["s"]) for i in range(3) for j in range(i)]
    require(min(gaps) >= Q(t, 32*p*p), "all source separation guards")
    # Rational ln2/pi bounds certify the literal alpha for this finite fixture.
    require(9 < Q(4*16*69, 100)/Q(22, 7), "alpha lower bound")
    require(Q(4*16*70, 100)/3 < 16, "alpha upper bound")
    for exponent in (12, 16, 24, 32, 64):
        pp = 1 << exponent
        require(Q(27, 8*pp) < Q(1, 1024), "upper-entry box endpoint")
        require(pp*pp >= 128, "source w/h remainder relation")
        require(pp**8//8-4 >= pp*pp >= 91+6*pp, "alias polynomial domination")
        require(pp >= 233+42*exponent, "p-bit precision fixture")
    return {"fixtures": rows, "minimum_gap": min(gaps),
            "required_gap": str(Q(t, 32*p*p)), "alpha": 4,
            "parameter_boundary_checks": [12, 16, 24, 32, 64],
            "scope": "Exact finite guards; uniform analytic inequalities are proved in PROOF.md."}


def authenticate():
    root = Path(__file__).resolve().parent
    pins = json.loads((root/"DEPENDENCIES.json").read_text())
    for item in pins["files"]:
        data = (root/item["local"]).read_bytes()
        require(len(data) == item["bytes"] and sha256(data).hexdigest() == item["sha256"],
                "source authentication "+item["local"])
    return len(pins["files"])


def main():
    result = {
        "status": "PASS_SEPARATED_THREE_AXIS_SOURCE_MARGIN",
        "authenticated_inputs": authenticate(),
        "polynomial": polynomial_checks(),
        "rational_margins": rational_margin_checks(),
        "source": source_checks(),
        "negative_controls": [
            "repeated factors have identically zero determinant",
            "2^22 undercharges the exact weighted remainder",
            "equal factors fail the positive separation guard",
            "large lower entries fail the remainder-smallness contract",
            "omitting reversal fails the inverse determinant identity",
            "coarse upper-one lower-zero rounding destroys rank",
        ],
        "scope": "Two orders and separated common-target sources; no all-order margin, producer admission or kappa claim."
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
