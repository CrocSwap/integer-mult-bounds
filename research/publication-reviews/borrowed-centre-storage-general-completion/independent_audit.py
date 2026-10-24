#!/usr/bin/env python3
"""Check the actual residue matrices without a source checker import."""

import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path


def need(condition, label):
    if not condition:
        raise ValueError(label)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def add(a, b, sign=1, p=13):
    return [[(x + sign*y) % p for x, y in zip(row, other)]
            for row, other in zip(a, b)]


def product(a, b, p=13):
    out = [[0]*len(b[0]) for _ in a]
    for i, row in enumerate(a):
        for k, value in enumerate(row):
            if value:
                for j, other in enumerate(b[k]):
                    out[i][j] += value*other
    return [[x % p for x in row] for row in out]


def rank(a, p=13):
    rows = [[x % p for x in row] for row in a]
    pivot = 0
    for column in range(len(rows[0])):
        found = next((i for i in range(pivot, len(rows)) if rows[i][column]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        scale = pow(rows[pivot][column], -1, p)
        rows[pivot] = [(x*scale) % p for x in rows[pivot]]
        for i in range(pivot + 1, len(rows)):
            scale = rows[i][column]
            if scale:
                rows[i] = [(x-scale*y) % p for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def inverse(a, p=13):
    n = len(a)
    rows = [[x % p for x in row] + eye for row, eye in zip(a, identity(n))]
    for column in range(n):
        found = next((i for i in range(column, n) if rows[i][column]), None)
        need(found is not None, "Selected minor must be a unit in the residue field")
        rows[column], rows[found] = rows[found], rows[column]
        scale = pow(rows[column][column], -1, p)
        rows[column] = [(x*scale) % p for x in rows[column]]
        for i in range(n):
            scale = rows[i][column] if i != column else 0
            if scale:
                rows[i] = [(x-scale*y) % p for x, y in zip(rows[i], rows[column])]
    return [row[n:] for row in rows]


def double_real(a):
    """Realify a matrix whose entries are real."""
    width = len(a[0])
    return [row + [0]*width for row in a] + [[0]*width + row for row in a]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--annex", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    annex = args.annex.resolve()
    need(not args.out.exists(), "Output file must be new")
    source = annex / "frozen/work/centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json"
    raw = source.read_bytes()
    need(sha256(raw).hexdigest() == "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3",
         "Actual interface source pin")
    rows = json.loads(raw)["R"]
    r = []
    for row in rows:
        values = [Fraction(row.get(str(j), 0)) for j in range(112)]
        r.append([(q.numerator*pow(q.denominator, -1, 13)) % 13 for q in values])
    selected = [0, 7, 20, 27, 36, 46, 57, 111]
    other = [j for j in range(112) if j not in selected]
    rs = [[row[j] for j in selected] for row in r]
    rsi = inverse(rs)
    k = [[(r[j][i]*10) % 13 for j in range(8)] for i in range(112)]
    need(product(r, k) == identity(8), "Actual RK is I modulo 13")
    l = [[row[j] if j in selected else 0 for j in range(112)] for row in r]
    g = [[0]*8 for _ in range(112)]
    for i, port in enumerate(selected):
        g[port] = rsi[i]
    d = [[0]*8 if i in selected else row[:] for i, row in enumerate(k)]
    b = add(r, l, -1)
    eye = identity(112)
    gb = product(g, b)
    dl = product(d, l)
    upper, lower = add(eye, gb), add(eye, dl, -1)
    t = product(lower, upper)
    ti = product(add(eye, gb, -1), add(eye, dl))
    j = add(eye, product(k, r), -1)
    repair = add(t, j, -1)
    need(product(t, ti) == product(ti, t) == eye, "Both actual inverse orders")
    need(product(l, t) == r, "Actual complete query")
    need([t[i] for i in other] == [j[i] for i in other], "All retained actual rows")
    changed = [i for i, row in enumerate(repair) if any(row)]
    need(changed == selected, "Exactly the eight selected output fields change")
    actual_ranks = {"R": rank(r), "K": rank(k), "J": rank(j), "T": rank(t),
                    "T_minus_J": rank(repair)}
    need(actual_ranks == {"R": 8, "K": 8, "J": 104, "T": 112, "T_minus_J": 8},
         "Actual rank and nullity counts")
    need(product(j, k) == [[0]*8 for _ in range(112)], "K image is in the J kernel")
    need(rank(product(repair, k)) == 8, "Repair is injective on the J kernel")
    need(product(repair, repair) == repair, "Actual compatible repair is a projection")

    # These changes must fail the source output contract.
    reversed_t = product(upper, lower)
    need([reversed_t[i] for i in other] != [j[i] for i in other], "Reversed shears fail retained rows")
    wrong_d_t = product(add(eye, product(k, l), -1), upper)
    need(rank(wrong_d_t) == 104, "Using all of K in D destroys invertibility")
    need(product(l, wrong_d_t) != r, "Using all of K in D destroys the query")
    wrong_sign_t = product(add(eye, dl), upper)
    need([wrong_sign_t[i] for i in other] != [j[i] for i in other], "Wrong shear sign fails retained rows")

    # Set the selected part of K to zero. The same T still completes J.
    incompatible_j = add(eye, product(d, r), -1)
    incompatible_repair = add(t, incompatible_j, -1)
    need([t[i] for i in other] == [incompatible_j[i] for i in other], "Arbitrary selected K retains U")
    need(product(incompatible_repair, incompatible_repair) != incompatible_repair,
         "The general repair is not necessarily a projection")
    need(rank(incompatible_j) == 112, "The unit branch can need zero changed fields")

    # The actual source matrix is real, so realification is a block diagonal sum.
    real_ranks = {"J": rank(double_real(j)), "T": rank(double_real(t)),
                  "T_minus_J": rank(double_real(repair))}
    need(real_ranks == {"J": 208, "T": 224, "T_minus_J": 16}, "Full realified ranks")
    need(5*5 % 13 == 8*8 % 13 == 12, "Both Gaussian residue maps")
    result = {
        "status": "PASS_INDEPENDENT_GENERAL_COMPLETION_ANNEX_AUDIT",
        "interface_sha256": sha256(raw).hexdigest(),
        "method": "Direct finite-field matrix arithmetic with no source checker imports",
        "prime": 13,
        "selected_fields": selected,
        "actual_ranks": actual_ranks,
        "realified_ranks": real_ranks,
        "inverse_orders": 2,
        "retained_rows": 104,
        "kernel_injection_rank": 8,
        "negative_controls": ["Reversed factor order breaks retained rows",
                              "Unprojected K in D gives rank 104 and breaks query",
                              "Wrong shear sign breaks retained rows",
                              "Incompatible selected K gives a nonprojection repair"],
        "unit_branch_control_rank": 112,
        "scope": "Actual residue matrices and contract controls; the general ring claim uses the reviewed proof",
        "checks_not_run": ["New native implementation or native cost optimum",
                           "Global supplier or kappa calculation", "Nonlinear program or finite-precision implementation"],
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])


if __name__ == "__main__":
    main()
