#!/usr/bin/env python3
"""Exact finite corroboration of the block Schur theorem. Apache-2.0."""
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def matrix(rows):
    result = tuple(tuple(row) for row in rows)
    require(1 <= len(result) <= 12, "row capacity")
    require(1 <= len(result[0]) <= 12, "column capacity")
    require(all(len(row) == len(result[0]) for row in result), "ragged matrix")
    return result


def mul(a, b, q):
    require(len(a[0]) == len(b), "product shape")
    return matrix([[sum(a[i][k] * b[k][j] for k in range(len(b))) % q
                    for j in range(len(b[0]))] for i in range(len(a))])


def sub(a, b, q):
    require(len(a) == len(b) and len(a[0]) == len(b[0]), "difference shape")
    return matrix([[(x-y) % q for x, y in zip(ar, br)] for ar, br in zip(a, b)])


def rank(a, q):
    rows = [list(row) for row in a]
    r = 0
    for col in range(len(a[0])):
        pivots = [i for i in range(r, len(rows)) if rows[i][col]]
        if not pivots:
            continue
        i = pivots[0]
        rows[r], rows[i] = rows[i], rows[r]
        inv = pow(rows[r][col], -1, q)
        rows[r] = [x*inv % q for x in rows[r]]
        for i in range(r+1, len(rows)):
            scale = rows[i][col]
            rows[i] = [(x-scale*y) % q for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


def inverse(a, q):
    n = len(a)
    require(n == len(a[0]), "inverse shape")
    rows = [list(row) + [int(i == j) for j in range(n)] for i, row in enumerate(a)]
    for col in range(n):
        pivots = [i for i in range(col, n) if rows[i][col]]
        if not pivots:
            return None
        i = pivots[0]
        rows[col], rows[i] = rows[i], rows[col]
        inv = pow(rows[col][col], -1, q)
        rows[col] = [x*inv % q for x in rows[col]]
        for i in range(n):
            if i != col:
                scale = rows[i][col]
                rows[i] = [(x-scale*y) % q for x, y in zip(rows[i], rows[col])]
    return matrix([row[n:] for row in rows])


def blocks(p, d):
    require(len(p) == len(p[0]) and 0 < d < len(p), "pivot shape")
    return (matrix([row[:d] for row in p[:d]]),
            matrix([row[d:] for row in p[:d]]),
            matrix([row[:d] for row in p[d:]]),
            matrix([row[d:] for row in p[d:]]))


def schur(p, d, q):
    a, r, c, z = blocks(p, d)
    ai = inverse(a, q)
    require(ai is not None, "singular pivot")
    return sub(z, mul(mul(c, ai, q), r, q), q)


def factors(p, z, d, q):
    a, r, c, _ = blocks(p, d)
    b, s, e, _ = blocks(z, d)
    h, t, w, _ = blocks(mul(p, z, q), d)
    ai, bi = inverse(a, q), inverse(b, q)
    require(ai is not None and bi is not None, "factor pivots")
    ca, eb = mul(c, ai, q), mul(e, bi, q)
    ar, bs = mul(ai, r, q), mul(bi, s, q)
    u, v = sub(ca, eb, q), sub(ar, bs, q)
    x = sub(w, mul(eb, h, q), q)
    y = sub(t, mul(h, bs, q), q)
    return x, v, u, y


def inspect(p, z, d, q, idempotents=False):
    require(mul(p, z, q) == mul(z, p, q), "commuting input premise")
    s, t = schur(p, d, q), schur(z, d, q)
    actual = sub(mul(s, t, q), mul(t, s, q), q)
    x, v, u, y = factors(p, z, d, q)
    predicted = sub(mul(x, v, q), mul(u, y, q), q)
    require(actual == predicted, "ordered factorization")
    left = matrix([list(xr)+list(ur) for xr, ur in zip(x, u)])
    right = matrix(list(v)+[tuple(-value % q for value in row) for row in y])
    r = rank(actual, q)
    require(actual == mul(left, right, q), "rectangular factorization")
    require(r <= min(2*d, len(p)-d), "block rank bound")
    require((r == 2*d) == (rank(left, q) == rank(right, q) == 2*d),
            "full rank equivalence")
    if idempotents:
        require(mul(p, p, q) == p and mul(z, z, q) == z, "projector inputs")
        require(mul(s, s, q) == s and mul(t, t, q) == t, "Schur idempotents")
        require(rank(s, q) == rank(p, q)-d, "first rank drop")
        require(rank(t, q) == rank(z, q)-d, "second rank drop")
    return r


def polynomial_census(n, d, q):
    counts = Counter()
    noncommuting_pivots = 0
    first = None
    require(q**(n*n) <= 65536, "census capacity")
    for entries in product(range(q), repeat=n*n):
        p = matrix([entries[i*n:(i+1)*n] for i in range(n)])
        z = mul(p, p, q)
        a, _, _, _ = blocks(p, d)
        b, _, _, _ = blocks(z, d)
        if inverse(a, q) is None or inverse(b, q) is None:
            continue
        r = inspect(p, z, d, q)
        counts[r] += 1
        if mul(a, b, q) != mul(b, a, q):
            noncommuting_pivots += 1
            if first is None:
                first = {"P": p, "Q": z, "rank": r}
    return {"n": n, "d": d, "q": q, "candidate_matrices": q**(n*n),
            "ranks": dict(sorted(counts.items())),
            "noncommuting_pivots": noncommuting_pivots, "first_witness": first}


def conjugate(g, gi, mask, q):
    n = len(g)
    return matrix([[sum(g[i][k]*gi[k][j] for k in range(n) if mask >> k & 1) % q
                    for j in range(n)] for i in range(n)])


def projector_orbit():
    counts = Counter()
    headers = 0
    for entries in product(range(2), repeat=16):
        g = matrix([entries[i*4:(i+1)*4] for i in range(4)])
        gi = inverse(g, 2)
        if gi is None:
            continue
        headers += 1
        p, z = conjugate(g, gi, 7, 2), conjugate(g, gi, 11, 2)
        if inverse(blocks(p, 2)[0], 2) is not None and inverse(blocks(z, 2)[0], 2) is not None:
            counts[inspect(p, z, 2, 2, True)] += 1
    require(headers == 20160, "complete GL4(F2) cover")
    return {"headers": headers, "q": 2, "n": 4, "d": 2,
            "projector_masks": [7, 11], "ranks": dict(sorted(counts.items()))}


def tensor_identity(p, d):
    return matrix([[p[i//d][j//d]*int(i % d == j % d)
                    for j in range(len(p)*d)] for i in range(len(p)*d)])


def sharp_examples():
    p = ((4, 3, 3), (3, 4, 3), (3, 3, 4))
    z = ((4, 4, 3), (2, 2, 2), (0, 0, 1))
    result = []
    for d in range(1, 5):
        pp, zz = tensor_identity(p, d), tensor_identity(z, d)
        r = inspect(pp, zz, d, 5, True)
        require(r == 2*d, "sharp tensor rank")
        require(rank(pp, 5) == rank(zz, 5) == 2*d, "sharp input ranks")
        result.append({"q": 5, "n": 3*d, "d": d, "rank": r})
    return result


def boundary_controls():
    zero = ((0, 0), (0, 0))
    rejected = 0
    for operation in ("singular", "shape", "capacity", "premise"):
        try:
            if operation == "singular":
                schur(zero, 1, 2)
            elif operation == "shape":
                blocks(((1, 0),), 1)
            elif operation == "capacity":
                matrix([[0]*13])
            else:
                inspect(((1, 1), (0, 0)), ((1, 0), (1, 0)), 1, 3)
        except ValueError:
            rejected += 1
    require(rejected == 4, "invalid-input controls")
    return rejected


def mutation_controls(domains):
    order = correction = premise = False
    for domain in domains:
        w = domain["first_witness"]
        if w is None:
            continue
        p, z, d, q = w["P"], w["Q"], domain["d"], domain["q"]
        x, v, u, y = factors(p, z, d, q)
        s, t = schur(p, d, q), schur(z, d, q)
        actual = sub(mul(s, t, q), mul(t, s, q), q)
        uy = mul(u, y, q)
        a, _, _, _ = blocks(p, d)
        b, _, e, _ = blocks(z, d)
        h, ht, hw, _ = blocks(mul(p, z, q), d)
        bi = inverse(b, q)
        wrong_x = sub(hw, mul(mul(e, h, q), bi, q), q)
        order |= actual != sub(mul(wrong_x, v, q), uy, q)
        correction |= actual != sub(mul(hw, v, q), mul(u, ht, q), q)
        premise |= mul(a, b, q) != mul(b, a, q)
    require(order, "moving H past B inverse must fail")
    require(premise, "noncommuting pivot blocks must be exercised")
    # Odd characteristic makes the sign control observable in the sharp example.
    p, z = ((4, 3, 3), (3, 4, 3), (3, 3, 4)), ((4, 4, 3), (2, 2, 2), (0, 0, 1))
    x, v, u, y = factors(p, z, 1, 5)
    xv, uy = mul(x, v, 5), mul(u, y, 5)
    plus = matrix([[(a+b) % 5 for a, b in zip(ar, br)] for ar, br in zip(xv, uy)])
    require(sub(xv, uy, 5) != plus, "plus-sign mutation differs")
    _, ht, hw, _ = blocks(mul(p, z, 5), 1)
    s, t = schur(p, 1, 5), schur(z, 1, 5)
    actual = sub(mul(s, t, 5), mul(t, s, 5), 5)
    correction |= actual != sub(mul(hw, v, 5), mul(u, ht, 5), 5)
    require(correction, "omitting H corrections must fail")
    return 4


def main():
    domains = [polynomial_census(n, d, q) for n, d, q in ((4, 2, 2), (3, 2, 3))]
    require(all(domain["noncommuting_pivots"] > 0 for domain in domains),
            "genuine block cases in both fields")
    result = {"polynomial_domains": domains, "projector_orbit": projector_orbit(),
              "sharp_examples": sharp_examples(), "boundary_controls": boundary_controls(),
              "mutation_controls": mutation_controls(domains)}
    package = Path(__file__).resolve().parent
    files = sorted(p for p in package.iterdir() if p.is_file())
    require(len(files) <= 8, "package receipt capacity")
    result["package_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest() for p in files}
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["receipt_sha256"] = sha256(canonical).hexdigest()
    print("PASS_BLOCK_SCHUR_COMMUTATOR")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
