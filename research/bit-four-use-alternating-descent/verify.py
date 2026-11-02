#!/usr/bin/env python3
"""Exact finite corroboration of alternating four-call lattice descent."""

import hashlib
import itertools
import json
from pathlib import Path
import platform
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def field_table(q):
    require(q in (2, 4, 8), "field must be F2, F4 or F8")
    modulus = {2: 3, 4: 7, 8: 11}[q]
    degree = q.bit_length() - 1
    rows = []
    for a in range(q):
        row = []
        for b in range(q):
            value, x = 0, a
            for bit in range(degree):
                if (b >> bit) & 1:
                    value ^= x
                x <<= 1
                if x & q:
                    x ^= modulus
            row.append(value)
        rows.append(tuple(row))
    table = tuple(rows)
    for a, b, c in itertools.product(range(q), repeat=3):
        require(table[a][b] == table[b][a], "field commutativity")
        require(table[a][table[b][c]] == table[table[a][b]][c], "associativity")
        require(table[a][b ^ c] == table[a][b] ^ table[a][c], "distributivity")
    for a in range(1, q):
        require(table[a][1] == a and 1 in table[a], "field unit/inverse")
    return table


def identity(n):
    return tuple(int(i == j) for i in range(n) for j in range(n))


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b, strict=True))


def scale(a, coefficient, table):
    return tuple(table[coefficient][x] for x in a)


def multiply(a, b, n, table):
    out = [0] * (n * n)
    for i, j, k in itertools.product(range(n), repeat=3):
        out[n * i + j] ^= table[a[n * i + k]][b[n * k + j]]
    return tuple(out)


def trace(a, n):
    value = 0
    for i in range(n):
        value ^= a[n * i + i]
    return value


def rank(a, n, table):
    rows = [list(a[i * n:(i + 1) * n]) for i in range(n)]
    pivot = 0
    for column in range(n):
        candidates = [i for i in range(pivot, n) if rows[i][column]]
        if not candidates:
            continue
        selected = candidates[0]
        rows[pivot], rows[selected] = rows[selected], rows[pivot]
        inverse = table[rows[pivot][column]].index(1)
        rows[pivot] = [table[inverse][x] for x in rows[pivot]]
        for i in range(n):
            if i != pivot and rows[i][column]:
                coefficient = rows[i][column]
                rows[i] = [x ^ table[coefficient][y]
                           for x, y in zip(rows[i], rows[pivot], strict=True)]
        pivot += 1
    return pivot


def validate_projector(p, n, table):
    require(1 <= n <= 4 and len(p) == n * n, "projector shape")
    require(all(isinstance(x, int) and 0 <= x < len(table) for x in p),
            "projector field entries")
    require(multiply(p, p, n, table) == p, "projector idempotence")
    require(rank(p, n, table) == 1, "projector rank one")


def projectors(n, table):
    q = len(table)
    require(1 <= n <= 4 and q ** n <= 256, "projector enumeration capacity")
    vectors = tuple(itertools.product(range(q), repeat=n))
    out = []
    for u in vectors:
        nonzero = [x for x in u if x]
        if not nonzero or nonzero[0] != 1:
            continue
        for v in vectors:
            pairing = 0
            for x, y in zip(u, v, strict=True):
                pairing ^= table[x][y]
            if pairing == 1:
                p = tuple(table[x][y] for x in u for y in v)
                validate_projector(p, n, table)
                out.append(p)
    expected = (q ** n - 1) * q ** (n - 1) // (q - 1)
    require(len(out) == len(set(out)) == expected, "complete projector list")
    return tuple(out)


def polynomial_product(a, b, n, table):
    require(len(a) + len(b) <= 6, "polynomial degree capacity")
    zero = (0,) * (n * n)
    out = [zero] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = add(out[i + j], multiply(x, y, n, table))
    return tuple(out)


def word(ps, n, table):
    require(len(ps) <= 4, "word length capacity")
    result = (identity(n),)
    for p in ps:
        result = polynomial_product(result, (add(identity(n), p), p), n, table)
    return result


def column_interpreter(ps, n, table):
    """Act on basis columns without polynomial matrix multiplication."""
    require(len(ps) <= 4, "column interpreter length capacity")
    matrices = [[0] * (n * n) for _ in range(len(ps) + 1)]
    for column in range(n):
        coefficients = [tuple(int(i == column) for i in range(n))]
        for p in reversed(ps):
            following = [[0] * n for _ in range(len(coefficients) + 1)]
            for degree, vector in enumerate(coefficients):
                projected = [0] * n
                for i, j in itertools.product(range(n), repeat=2):
                    projected[i] ^= table[p[n * i + j]][vector[j]]
                for i in range(n):
                    following[degree][i] ^= vector[i] ^ projected[i]
                    following[degree + 1][i] ^= projected[i]
            coefficients = [tuple(v) for v in following]
        for degree, vector in enumerate(coefficients):
            for row, value in enumerate(vector):
                matrices[degree][n * row + column] = value
    return tuple(tuple(m) for m in matrices)


def check_pair(p, q, n, table):
    endpoint = word((p, q, p, q), n, table)
    require(endpoint == column_interpreter((p, q, p, q), n, table),
            "independent literal polynomial endpoints")
    pq = multiply(p, q, n, table)
    qp = multiply(q, p, n, table)
    tau = trace(pq, n)
    expected_odd = scale(add(p, q), tau, table)
    require(endpoint[1] == endpoint[3] == expected_odd, "odd coefficient formula")
    even = not any(endpoint[1]) and not any(endpoint[3])
    require(even == (p == q or tau == 0), "exact even-subalgebra criterion")
    if not even:
        return "not_even", endpoint
    first, second = (p, p) if p == q else (add(p, pq), add(q, qp))
    validate_projector(first, n, table)
    validate_projector(second, n, table)
    coarse = word((first, second), n, table)
    zero = (0,) * (n * n)
    require(endpoint == (coarse[0], zero, coarse[1], zero, coarse[2]),
            "two coarse-label calls reproduce every coefficient")
    if p == q:
        return "equal", endpoint
    require(not any(multiply(first, second, n, table)), "coarse orthogonality")
    require(not any(multiply(second, first, n, table)), "reverse orthogonality")
    require(rank(add(first, second), n, table) == 2, "coarse rank two")
    return "orthogonal" if pq == qp else "noncommuting", endpoint


def rejected_projector(p, n, table, expected):
    try:
        validate_projector(p, n, table)
    except ValueError as error:
        require(str(error) == expected, "wrong projector rejection reason")
        return
    raise ValueError("invalid projector accepted")


def controls():
    table, n = field_table(2), 2
    p, q = (1, 0, 0, 0), (0, 1, 0, 1)
    zero = (0,) * 4
    endpoint = word((p, q, p, q), n, table)
    require(endpoint == (zero, zero, identity(n), zero, zero),
            "noncommuting even witness")
    require(multiply(p, q, n, table) != multiply(q, p, n, table),
            "commuting-only mutation rejected")
    require(p != q, "equal-projector-only mutation rejected")
    proper = 0
    for length in (1, 2, 3):
        for start in range(5 - length):
            subword = (p, q, p, q)[start:start + length]
            result = word(subword, n, table)
            require(any(any(result[i]) for i in range(1, len(result), 2)),
                    "proper consecutive block must not be even")
            proper += 1
    bare = word((p, q), n, table)
    require(endpoint != (bare[0], zero, bare[1], zero, bare[2]),
            "omitting cross-term correction rejected")
    require(endpoint != word((p, q, p, p), n, table), "changed fourth call rejected")
    rejected_projector((0, 1, 0, 0), n, table, "projector idempotence")
    rejected_projector(identity(n), n, table, "projector rank one")
    rejected_projector((0, 0, 0, 0), n, table, "projector rank one")
    rejected_projector((1,), n, table, "projector shape")
    rejected_projector((2, 0, 0, 0), n, table, "projector field entries")
    try:
        field_table(3)
    except ValueError as error:
        require(str(error) == "field must be F2, F4 or F8", "wrong field error")
    else:
        raise ValueError("odd characteristic accepted")
    require(proper == 9, "proper subword inventory")
    return {"proper_noneven_blocks": proper, "semantic_checks": 5,
            "invalid_inputs": 6}


def main():
    require(len(sys.argv) == 1, "no command-line arguments are supported")
    rows, digest = [], hashlib.sha256()
    for field_size, n in ((2, 1), (2, 2), (2, 3), (2, 4),
                          (4, 1), (4, 2), (8, 1), (8, 2)):
        table = field_table(field_size)
        ps = projectors(n, table)
        counts = dict.fromkeys(("equal", "orthogonal", "noncommuting", "not_even"), 0)
        for p, q in itertools.product(ps, repeat=2):
            category, endpoint = check_pair(p, q, n, table)
            counts[category] += 1
            digest.update(bytes(x for matrix in endpoint for x in matrix))
        require(sum(counts.values()) == len(ps) ** 2, "pair enumeration accounting")
        rows.append({"field": field_size, "width": n, "projectors": len(ps),
                     "pairs": len(ps) ** 2, **counts})
    folder = Path(__file__).resolve().parent
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(folder.iterdir()) if p.is_file()}
    receipt = {"status": "PASS_BIT_FOUR_USE_ALTERNATING_DESCENT", "rows": rows,
               "controls": controls(), "endpoint_sha256": digest.hexdigest(),
               "package_sha256": hashes, "python": platform.python_version(),
               "claim_type": "scoped written proof with finite corroboration",
               "no_new_kappa": True}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
