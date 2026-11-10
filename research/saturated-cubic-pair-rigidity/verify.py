#!/usr/bin/env python3
"""Exact finite checks of the new cubic equality normal form.

Produced by Nick Petalas. Apache-2.0.
The all-dimension theorem is the written proof, not a finite extrapolation.
"""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def field(q):
    require(q in (2, 4), "unsupported field order")
    modulus = {2: 3, 4: 7}[q]
    table = [[0] * q for _ in range(q)]
    for a in range(q):
        for b in range(q):
            x, y, value = a, b, 0
            for _ in range(q.bit_length() - 1):
                if y & 1:
                    value ^= x
                y >>= 1
                x <<= 1
                if x & q:
                    x ^= modulus
            table[a][b] = value
    return tuple(tuple(row) for row in table)


def identity(n):
    require(1 <= n <= 24, "matrix dimension outside finite verifier domain")
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def zero(n):
    return tuple((0,) * n for _ in range(n))


def add(a, b):
    return tuple(tuple(x ^ y for x, y in zip(u, v, strict=True))
                 for u, v in zip(a, b, strict=True))


def multiply(a, b, table):
    n = len(a)
    out = [[0] * n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if a[i][k]:
                products = table[a[i][k]]
                for j in range(n):
                    out[i][j] ^= products[b[k][j]]
    return tuple(tuple(row) for row in out)


def cube(a, table):
    return multiply(multiply(a, a, table), a, table)


def inverse(a, table):
    n, q = len(a), len(table)
    rows = [list(row) + list(unit) for row, unit in
            zip(a, identity(n), strict=True)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        require(pivot is not None, "singular matrix")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = next(x for x in range(1, q) if table[rows[j][j]][x] == 1)
        rows[j] = [table[scale][x] for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                products = table[rows[i][j]]
                rows[i] = [x ^ products[y] for x, y in
                           zip(rows[i], rows[j], strict=True)]
    result = tuple(tuple(row[n:]) for row in rows)
    require(multiply(a, result, table) == identity(n), "inverse residual")
    return result


def block_matrix(blocks):
    s = len(blocks[0][0])
    return tuple(tuple(x for block in block_row for x in block[i])
                 for block_row in blocks for i in range(s))


def normal_forms(s):
    require(1 <= s <= 8, "corank outside finite verifier domain")
    i, z = identity(s), zero(s)
    a = block_matrix(((z, i, z), (z, z, i), (z, z, z)))
    b = block_matrix(((z, i, z), (i, i, i), (i, z, i)))
    return a, b


def endpoint_forms(s):
    i, z = identity(s), zero(s)
    a = block_matrix(((i, i, z), (i, z, i), (i, z, i)))
    d = block_matrix(((i, z, z), (z, i, z), (z, z, z)))
    return a, add(a, d), d


def check_pair(a, b, s, table):
    n = 3 * s
    require(1 <= s <= 8 and len(a) == len(b) == n, "dimension hypothesis")
    q = len(table)
    require(all(len(row) == n and all(0 <= x < q for x in row)
                for row in (*a, *b)), "matrix representation")
    _, _, d = endpoint_forms(s)
    require(add(a, b) == d, "endpoint hypothesis")
    require(cube(a, table) == zero(n), "A cubic hypothesis")
    require(cube(b, table) == zero(n), "B cubic hypothesis")
    a2 = multiply(a, a, table)
    # Coordinates on im(E) are its last s standard coordinates.
    observation = identity(n)[2*s:] + a[2*s:] + a2[2*s:]
    backward = inverse(observation, table)
    expected_a, expected_b = normal_forms(s)
    require(multiply(multiply(observation, a, table), backward, table)
            == expected_a, "A observation normal form")
    require(multiply(multiply(observation, b, table), backward, table)
            == expected_b, "B observation normal form")


def matrices(n, q):
    require((n, q) in ((1, 2), (1, 4), (2, 2), (3, 2), (3, 4), (4, 2)),
            "exhaustive domain outside declared limits")
    for values in product(range(q), repeat=n*n):
        yield tuple(tuple(values[i*n:(i+1)*n]) for i in range(n))


def literal_three_space(q):
    table = field(q)
    _, _, d = endpoint_forms(1)
    candidates = accepted = 0
    for a in matrices(3, q):
        candidates += 1
        if cube(a, table) != zero(3):
            continue
        b = add(a, d)
        if cube(b, table) != zero(3):
            continue
        check_pair(a, b, 1, table)
        accepted += 1
    expected = (q*q - 1) * (q*q - q)
    require(candidates == q**9 and accepted == expected, "literal count")
    return {"q": q, "candidate_matrices": candidates, "pairs": accepted}


def block_identity_checks():
    checked = 0
    for s, q in ((1, 2), (1, 4), (2, 2)):
        table = field(q)
        i, z = identity(s), zero(s)
        domain = tuple(matrices(s, q))
        for m in domain:
            for n in domain:
                b = block_matrix(((z, i, z), (m, i, i), (n, z, i)))
                b3 = cube(b, table)
                first = tuple(tuple((*u, *v, *w)) for u, v, w in
                              zip(add(m, n), add(m, i), z, strict=True))
                require(b3[:s] == first, "noncommuting first-row identity")
                require((b3 == zero(3*s)) == (m == n == i), "cubic rigidity")
                checked += 1
    return checked


def fixed_endpoint_orbit():
    table = field(2)
    a, b, _ = endpoint_forms(2)
    i = identity(2)
    seen = set()
    candidates = 0
    for p in matrices(4, 2):
        candidates += 1
        try:
            p_inv = inverse(p, table)
        except ValueError as exc:
            require(str(exc) == "singular matrix", "unexpected orbit failure")
            continue
        c = tuple(tuple((*row, 0, 0)) for row in p)
        c += tuple((0,) * 4 + row for row in i)
        c_inv = tuple(tuple((*row, 0, 0)) for row in p_inv)
        c_inv += tuple((0,) * 4 + row for row in i)
        conjugate_a = multiply(multiply(c, a, table), c_inv, table)
        conjugate_b = multiply(multiply(c, b, table), c_inv, table)
        check_pair(conjugate_a, conjugate_b, 2, table)
        require(conjugate_a not in seen, "duplicate fixed-endpoint representative")
        seen.add(conjugate_a)
    require(candidates == 65536 and len(seen) == 20160, "six-space orbit count")
    payload = json.dumps(sorted(seen), separators=(",", ":")).encode()
    return {"candidate_four_matrices": candidates, "distinct_pairs": len(seen),
            "sorted_A_sha256": sha256(payload).hexdigest()}


def rank(rows, q, table):
    work = [list(row) for row in rows]
    width, pivot = len(work[0]), 0
    for j in range(width):
        selected = next((i for i in range(pivot, len(work)) if work[i][j]), None)
        if selected is None:
            continue
        work[pivot], work[selected] = work[selected], work[pivot]
        scale = next(x for x in range(1, q) if table[work[pivot][j]][x] == 1)
        work[pivot] = [table[scale][x] for x in work[pivot]]
        for i in range(pivot + 1, len(work)):
            products = table[work[i][j]]
            work[i] = [x ^ products[y] for x, y in
                       zip(work[i], work[pivot], strict=True)]
        pivot += 1
        if pivot == len(work):
            break
    return pivot


def commutant_checks():
    cases = []
    for s, q in ((1, 2), (1, 4), (2, 2), (2, 4)):
        table, n = field(q), 3*s
        a, b = normal_forms(s)
        images = []
        for u in range(n):
            for v in range(n):
                unit = tuple(tuple(int(i == u and j == v) for j in range(n))
                             for i in range(n))
                ca = add(multiply(unit, a, table), multiply(a, unit, table))
                cb = add(multiply(unit, b, table), multiply(b, unit, table))
                images.append(tuple(x for matrix in (ca, cb) for row in matrix
                                    for x in row))
        dimension = n*n - rank(images, q, table)
        require(dimension == s*s, "joint commutant dimension")
        cases.append({"s": s, "q": q, "dimension": dimension})
    return cases


def larger_checks():
    checked = 0
    for s in range(3, 9):
        for q in (2, 4):
            table, n = field(q), 3*s
            a, b, _ = endpoint_forms(s)
            c = [list(row) for row in identity(n)]
            # An invertible unit-upper-triangular change within im(D).
            for j in range(2*s - 1):
                c[j][j+1] = 1 if q == 2 else 2
            c = tuple(tuple(row) for row in c)
            backward = inverse(c, table)
            a = multiply(multiply(c, a, table), backward, table)
            b = multiply(multiply(c, b, table), backward, table)
            check_pair(a, b, s, table)
            checked += 1
    return checked


def rejection_checks():
    table = field(2)
    a, b, d = endpoint_forms(1)
    cases = ((zero(3), d, 1, "B cubic hypothesis"),
             (d, zero(3), 1, "A cubic hypothesis"),
             (a, zero(3), 1, "endpoint hypothesis"),
             (a, b, 2, "dimension hypothesis"))
    rejected = []
    for x, y, s, expected in cases:
        try:
            check_pair(x, y, s, table)
        except ValueError as exc:
            require(str(exc) == expected, "wrong rejection reason")
            rejected.append(expected)
        else:
            raise ValueError("invalid pair accepted")
    try:
        inverse(zero(3), table)
    except ValueError as exc:
        require(str(exc) == "singular matrix", "singular control reason")
        rejected.append("singular matrix")
    else:
        raise ValueError("singular observation accepted")
    try:
        field(3)
    except ValueError as exc:
        require(str(exc) == "unsupported field order", "field control reason")
        rejected.append("unsupported field order")
    else:
        raise ValueError("characteristic-three field accepted")
    return rejected


def main():
    result = {
        "status": "PASS_SATURATED_CUBIC_PAIR_RIGIDITY",
        "claim_type": "scoped written proof with exact finite corroboration",
        "literal_counts": [literal_three_space(q) for q in (2, 4)],
        "noncommuting_block_forms": block_identity_checks(),
        "six_dimensional_binary_orbit": fixed_endpoint_orbit(),
        "commutants": commutant_checks(),
        "larger_conjugates": larger_checks(),
        "rejections": rejection_checks(),
        "failed_checks": 0,
    }
    package = Path(__file__).resolve().parent
    source_files = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json",
                    "VERIFY.json", "verify.py")
    result["file_sha256"] = {
        name: sha256((package / name).read_bytes()).hexdigest()
        for name in source_files
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
