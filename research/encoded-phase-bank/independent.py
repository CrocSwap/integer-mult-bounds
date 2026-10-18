#!/usr/bin/env python3
"""Exact rational matrix replay, independent of the symbolic crossing checker.

Tekalign, substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def mul(a, b):
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), F(0))
             for j in range(len(b[0]))] for i in range(len(a))]


def inverse(a):
    n = len(a)
    rows = [list(row) + unit for row, unit in zip(a, eye(n))]
    for k in range(n):
        pivot = next((j for j in range(k, n) if rows[j][k]), None)
        require(pivot is not None, "singular conjugating matrix")
        rows[k], rows[pivot] = rows[pivot], rows[k]
        scale = rows[k][k]
        rows[k] = [x / scale for x in rows[k]]
        for j in range(n):
            if j != k:
                scale = rows[j][k]
                rows[j] = [x - scale * y for x, y in zip(rows[j], rows[k])]
    return [r[n:] for r in rows]


def coordinate(q, bit):
    n = 1 << q
    z = [[F((-1) ** ((i >> bit) & 1) if i == j else 0)
          for j in range(n)] for i in range(n)]
    x = [[F(i == (j ^ (1 << bit))) for j in range(n)] for i in range(n)]
    return z, x


def conjugate(a, s):
    return mul(mul(s, a), inverse(s))


def dense_basis(n):
    s = eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            s[i][j] = F((i + j) % 3 + 1, j - i + 1)
    return s


def sparse(a):
    return [[(j, x) for j, x in enumerate(row) if x] for row in a]


def execute(word, generators, labels, column):
    d = len(generators[0][0][0])
    vector = [F(k == column) for k in range(d)]
    for j in word:
        for k, pair in enumerate(generators[j]):
            for side in range(2):
                if labels[j][k][side]:
                    vector = [sum((a * vector[t] for t, a in row), F(0))
                              for row in pair[side]]
    return vector


def fixture(name, word, matrices, expect=True):
    widths = [len(x) for x in matrices]
    d = len(matrices[0][0][0])
    encoded = [[tuple(sparse(a) for a in pair) for pair in column] for column in matrices]
    total = 0
    witness = None
    for flat in product((0, 1), repeat=2 * sum(widths)):
        labels, offset = [], 0
        for w in widths:
            labels.append([flat[offset + 2 * k:offset + 2 * k + 2] for k in range(w)])
            offset += 2 * w
        sign = (-1) ** sum(u * v for column in labels for u, v in column)
        for b in range(d):
            actual = execute(word, encoded, labels, b)
            wanted = [F(sign * (i == b)) for i in range(d)]
            total += 1
            if actual != wanted and witness is None:
                witness = {"labels": flat, "bank_column": b,
                           "actual": [str(x) for x in actual],
                           "expected": [str(x) for x in wanted]}
                if not expect:
                    return {"name": name, "rejected": True, "witness": witness}
    require((witness is None) == expect, "matrix fixture failed: " + name)
    return {"name": name, "bank_dimension": d, "widths": widths,
            "complete_columns": total, "coefficients": total * d}


def run():
    # No simultaneous coordinate basis is required for nested columns.
    a, b = coordinate(1, 0)
    s = [[F(1), F(1, 2)], [F(1), F(3, 2)]]
    other = (conjugate(a, s), conjugate(b, s))
    require(mul(a, other[0]) != mul(other[0], a), "noncommuting nonedge fixture")
    require(any(sum(bool(x) for x in row) > 1 for m in other for row in m),
            "fixture did not leave monomial coordinates")
    nested = [[(a, b)], [other]]
    results = [fixture("non-Pauli nested columns", (0, 1, 1, 0), nested)]

    # Full rational conjugation mixes all four lanes, preserving exact endpoint.
    s4 = dense_basis(4)
    base = [coordinate(2, c) for c in (0, 1, 0)]
    dense = [[tuple(conjugate(m, s4) for m in pair)] for pair in base]
    results.append(fixture("dense producer-prefix", (0, 1, 2, 2, 0, 1), dense))
    results.append(fixture("interleaved path", (0, 1, 0, 2, 1, 2), dense))

    # Weighted blocks: ranks 1,2,1; maximum weighted increasing chain has weight 3.
    s8 = dense_basis(8)
    weighted = [[tuple(conjugate(m, s8) for m in coordinate(3, bit)) for bit in bits]
                for bits in [(0,), (1, 2), (0,)]]
    results.append(fixture("dense weighted blocks", (0, 1, 2, 2, 0, 1), weighted))
    cycle = [[coordinate(3, c)] for c in (0, 1, 0, 1, 2)]
    results.append(fixture("C5 attained dimension eight", (0, 1, 4, 0, 3, 4, 2, 3, 1, 2), cycle))

    negative = [fixture("crossed noncommuting dense columns", (0, 1, 0, 1), nested, False),
                fixture("missing consumer", (0, 1, 1), nested, False),
                fixture("wrong same-column square", (0, 0), [[(a, a)]], False),
                fixture("permutation destroys sharing", (0, 1, 2, 0, 1, 2), dense, False)]
    z0, x0 = coordinate(2, 0)
    z1, x1 = coordinate(2, 1)
    # All mixed A/B cross conditions hold; A/A alone fails. The old
    # coordinate-only cross-term formula would miss this encoded obstruction.
    aa_only = [[(z0, x0)], [(mul(x0, z1), x1)]]
    negative.append(fixture("same-family commutation is necessary", (0, 1, 0, 1), aa_only, False))

    # Without separated u/v dependence, scalar i^(uv) implements the phase.
    scalar_cases = 0
    for bits in product((0, 1), repeat=10):
        phase_mod4 = sum(2 * bits[2 * j] * bits[2 * j + 1] for j in range(5)) % 4
        require(phase_mod4 == 2 * (sum(bits[2*j] * bits[2*j+1] for j in range(5)) % 2),
                "joint-label scalar escape")
        scalar_cases += 1
    return {"status": "PASS_INDEPENDENT_ENCODED_BANK_MATRICES", "no_new_kappa": True,
            "positive_fixtures": results, "negative_controls": negative,
            "joint_label_dimension_one_escape": scalar_cases,
            "complete_columns": sum(r["complete_columns"] for r in results),
            "coefficients": sum(r["coefficients"] for r in results)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    receipt = run()
    if args.emit:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        expected = json.loads((HERE / "MATRICES.json").read_text())
        require(json.dumps(expected, sort_keys=True) == json.dumps(receipt, sort_keys=True),
                "independent receipt mismatch")
        print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
