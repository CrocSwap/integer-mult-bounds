#!/usr/bin/env python3
"""Independent finite PR6717 section 7 audit; imports no predecessor code.

Literal word multiplication in Z[S,A,B,C]/(S^2-1). Standard library only.
All-size scope comes from PROOF.md, not this finite grid. Apache-2.0.
Prepared for ferdy252 with substantial OpenAI Codex assistance.
"""
from fractions import Fraction
from pathlib import Path
import hashlib
import json


class AuditFailure(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AuditFailure(message)


PINS = {
    "PR6717-PROOF.md": ("9e108fdf827ffe92215be5e782f763a18968ce7613b66dfdd25a38f94958ce18", "7e3b89f085f1fe1f15098b75e22e370efc6ce4ce"),
    "PR6717-NOTICE": ("317d1abe22f6cb12239548139d632e0a59798b119c00692104c278776a548526", "57c81a73802b9166b5f72547938439ff1110e661"),
    "PR6717-LICENSE": ("c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4", "261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64"),
}


def authenticate():
    root = Path(__file__).resolve().parent
    for name, (sha256, blob) in PINS.items():
        data = (root / "inputs" / name).read_bytes()
        require(hashlib.sha256(data).hexdigest() == sha256, "source SHA256 mismatch: " + name)
        raw = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(raw).hexdigest() == blob, "source Git blob mismatch: " + name)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def basis(n):
    require(n >= 4 and n % 2 == 0, "even dimension >=4 required")
    columns = [[1, 1, 0, 0], [1, 2, 1, 0], [1, 2, 2, 0]]
    columns += [[0, 1, 1, 1] for _ in range(n - 3)]
    columns = [c + [0] * (n - 4) for c in columns]
    for j in range(3, n - 1):
        columns[j][j + 1] = 1
        columns[-1][j + 1] = -((-1) ** (j + 1))
    return [list(row) for row in zip(*columns)]


def inverse_and_determinant(matrix):
    n = len(matrix)
    rows = [[Fraction(x) for x in row] + list(map(Fraction, eye))
            for row, eye in zip(matrix, identity(n))]
    det = Fraction(1)
    for col in range(n):
        pivot = next((r for r in range(col, n) if rows[r][col]), None)
        require(pivot is not None, "singular basis")
        if pivot != col:
            rows[pivot], rows[col] = rows[col], rows[pivot]
            det = -det
        value = rows[col][col]
        det *= value
        rows[col] = [x / value for x in rows[col]]
        for r in range(n):
            if r != col:
                value = rows[r][col]
                rows[r] = [x - value * y for x, y in zip(rows[r], rows[col])]
    return [r[n:] for r in rows], det


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def construct(n, mutation=None):
    h = basis(n)
    if mutation == "sign":
        h[4][-1] *= -1
    elif mutation == "omit-tail":
        for j in range(4, n):
            h[j][-1] = 0
    inv, det = inverse_and_determinant(h)
    require(det == 1, "determinant is not one")
    require(all(x.denominator == 1 for row in inv for x in row), "nonintegral inverse")
    inv = [[int(x) for x in row] for row in inv]
    require([[dot(r, c) for c in zip(*inv)] for r in h] == identity(n), "inverse residual")
    factors = []
    for i in range(n + 1):
        u = [int(j == i) for j in range(n)] if i < n else [(-1) ** (j + 1) for j in range(n)]
        v = [int(i > j) - int(i < j) for j in range(n)]
        left = [dot(row, u) for row in h]
        right = [dot(v, col) for col in zip(*inv)]
        require(any(left) and any(right) and dot(left, right) == 0,
                "query rank-one/square-zero contract")
        factors.append((left, right))
    return factors


def masks(n):
    return {0: (0, (0, 1)), 1: (1, (0, 1, 2)), n: (2, (0, 3))}


def check_compatibility(factors):
    n = len(factors) - 1
    # Diagonal coordinate selectors are idempotent and commute pairwise.
    for site, (_, support) in masks(n).items():
        u, v = factors[site]
        require(all((not u[k] and not v[k]) or k in support for k in range(n)),
                f"selected compatibility at site {site}")


def check_factors(factors):
    n = len(factors) - 1
    expected = {0: ([1, 1, 0, 0], [1, -1, 0, 0]),
                1: ([1, 2, 1, 0], [1, 0, -1, 0]),
                n: ([-1, 0, 0, 1], [1, 0, 0, 1])}
    for site, (u, v) in expected.items():
        require(factors[site] == (u + [0] * (n - 4), v + [0] * (n - 4)),
                "selected factor mismatch")
    check_compatibility(factors)
    # P1 supports R0 and R1, hence the actual prefix T1*T0; P0 supports R0.
    # The final prefix -I is checked by the complete symbolic endpoint below.
    require(all((not u[k] and not v[k]) or k in (0, 1, 2)
                for u, v in factors[:2] for k in range(n)), "middle prefix support")


# Keys are (S exponent modulo 2, A exponent, B exponent, C exponent).
ONE = (0, 0, 0, 0)


def add_scaled(target, source, scalar, modulus):
    for key, value in source.items():
        result = target.get(key, 0) + scalar * value
        if modulus:
            result %= modulus
        if result:
            target[key] = result
        else:
            target.pop(key, None)


def query_delta(poly):
    out = {}
    for (s, a, b, c), value in poly.items():
        key = (s ^ 1, a, b, c)
        out[key] = out.get(key, 0) + value
        key = (s, a, b, c)
        out[key] = out.get(key, 0) - value
    return {key: value for key, value in out.items() if value}


def multiply_stage(poly, variable):
    out = {}
    for key, value in poly.items():
        exponents = list(key)
        exponents[variable + 1] += 1
        out[tuple(exponents)] = value
    return out


def word(factors, q, modulus=0, swapped_queries=False, drop_extra_input=False):
    n = len(factors) - 1
    stages = masks(n)
    order = list(range(n + 1))
    if swapped_queries:
        order[1], order[2] = order[2], order[1]
    columns = []
    for source in range(n * q):
        state = [{} for _ in range(n * q)]
        if not (drop_extra_input and source == 4 * q):
            state[source] = {ONE: 1}
        for site, query in enumerate(order):
            u, v = factors[query]
            # Propagate every independent coupled input through the actual word.
            for port in range(q):
                contraction = {}
                for j, value in enumerate(v):
                    add_scaled(contraction, state[j * q + port], value, modulus)
                delta = query_delta(contraction)
                for j, value in enumerate(u):
                    add_scaled(state[j * q + port], delta, value, modulus)
            if site in stages:
                variable, support = stages[site]
                for j in support:
                    for port in range(q):
                        index = j * q + port
                        state[index] = multiply_stage(state[index], variable)
        columns.append(state)
    return columns


def check_endpoint(columns, n, q):
    # Target specified independently of stage masks; all entries are compared.
    stage_exponents = [(1, 1, 1), (1, 1, 0), (0, 1, 0), (0, 0, 1)]
    require(len(columns) == n*q and all(len(c) == n*q for c in columns), "endpoint shape")
    for source, column in enumerate(columns):
        field = source // q
        abc = stage_exponents[field] if field < 4 else (0, 0, 0)
        for output, poly in enumerate(column):
            expected = {(1,) + abc: 1} if output == source else {}
            require(poly == expected, f"endpoint mismatch: input {source}, output {output}, n={n}, q={q}")


def expect_rejection(name, function, message):
    try:
        function()
    except AuditFailure as error:
        require(message in str(error), f"wrong rejection for {name}: {error}")
        return name
    raise AuditFailure("mutation accepted: " + name)


def main():
    authenticate()
    rows = []
    cases = [(n, 1, 0) for n in (4, 6, 8, 10, 12)]
    cases += [(4, 2, 0), (6, 2, 0), (4, 3, 0)]
    cases += [(n, 1, prime) for prime in (3, 5) for n in (4, 6, 8, 10, 12)]
    for n, q, modulus in cases:
        factors = construct(n)
        check_factors(factors)
        check_endpoint(word(factors, q, modulus), n, q)
        rows.append({"n": n, "q": q, "coefficient_modulus": modulus,
                     "independent_inputs": n*q, "stage_ranks": [2*q, 3*q, 2*q]})
    factors = construct(6)
    controls = [expect_rejection("last-column sign", lambda: construct(6, "sign"), "determinant"),
                expect_rejection("lost extra input", lambda: check_endpoint(
                    word(factors, 1, drop_extra_input=True), 6, 1), "endpoint mismatch"),
                expect_rejection("swapped chronology", lambda: check_endpoint(
                    word(factors, 1, swapped_queries=True), 6, 1), "endpoint mismatch")]
    # This altered word has the CORRECT complete endpoint but violates final
    # query compatibility. It prevents endpoint-only acceptance of this model.
    malformed = construct(6, "omit-tail")
    require(malformed[-1] == ([-1, 0, 0, 1, 1, -1], [1, 0, 0, 1, 0, 0]),
            "endpoint-preserving control factors")
    check_endpoint(word(malformed, 1), 6, 1)
    controls.append(expect_rejection("endpoint-preserving incompatible query",
                                     lambda: check_compatibility(malformed), "compatibility at site 6"))
    print(json.dumps({"status": "PASS_FINITE_ATTAINMENT_AUDIT", "cases": rows,
                      "rejected_controls": controls,
                      "scope": "Finite exact word checks; all-size proof is PROOF.md. No lower-bound or physical-supplier admission."},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
