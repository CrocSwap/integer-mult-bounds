#!/usr/bin/env python3
"""Check the reciprocal rank-two response and its actual pair code."""

from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = (HERE.parent / "lanes/independent-review-20261017/"
          "cyclic-pair-flags-20261018/CYCLIC-FLAGS.json")
SOURCE_SHA = "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def product(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)]
            for row in a]


def subtract(a, b):
    return [[x - y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def rank(a):
    a = [list(map(F, row)) for row in a]
    pivot = 0
    for col in range(len(a[0])):
        row = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if row is None:
            continue
        a[pivot], a[row] = a[row], a[pivot]
        scale = a[pivot][col]
        a[pivot] = [x / scale for x in a[pivot]]
        for i in range(len(a)):
            if i != pivot and a[i][col]:
                scale = a[i][col]
                a[i] = [x - scale * y for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def response(n):
    m = n - 2
    e = identity(n)
    for i in range(m):
        for j in range(m):
            e[i][j] -= 1
        e[i][m] = F(1)
    e[m] = [F(0)] * n
    e[m][m + 1] = F(1)
    e[m + 1] = [F(-(m - 2))] * m + [F(m - 1), F(0)]
    p = identity(n)
    p[m], p[m + 1] = p[m + 1], p[m]
    inverse = product(product(p, e), p)
    return e, inverse, p


def main():
    dimensions = []
    for n in range(3, 17):
        m = n - 2
        e, inverse, p = response(n)
        unit = identity(n)
        u = [[F(1), F(0)] for _ in range(m)]
        u += [[F(0), F(1)], [F(m - 2), F(-1)]]
        v = [[F(-1)] * m + [F(1), F(0)],
             [F(0)] * m + [F(-1), F(1)]]
        correction = subtract(e, unit)
        need(product(u, v) == correction, "Exact rank-two correction")
        need(rank(correction) == rank(subtract(inverse, unit)) == 2,
             "Both correction ranks are two")
        need(product(e, inverse) == product(inverse, e) == unit,
             "Both inverse orders")
        need(all(e[i][i] == inverse[i][i] == 0 for i in range(n)),
             "Both diagonals are zero")
        r = product(p, e)
        need(product(r, r) == unit and rank(subtract(r, unit)) == 1,
             "The reflection has rank one")
        small = product(v, u)
        small = [[small[i][j] + (i == j) for j in range(2)]
                 for i in range(2)]
        need(small == [[F(1 - m), F(1)], [F(m - 2), F(-1)]],
             "The two-coordinate action")
        need(small[0][0] * small[1][1] -
             small[0][1] * small[1][0] == 1, "Determinant one")
        for j in range(m):
            fixed = [[F(i == j)] for i in range(m)] + [[F(1)], [F(1)]]
            need(product(e, fixed) == fixed, "An explicit fixed-space basis")
        dimensions.append({"n": n, "correction_rank": 2,
                           "fixed_dimension": n - 2, "determinant": 1})

    raw = SOURCE.read_bytes()
    need(sha256(raw).hexdigest() == SOURCE_SHA, "Cyclic family source pin")
    source = json.loads(raw)
    ports = source["affected_ports"]
    need(len(ports) == len(set(ports)) == 48, "48 distinct physical ports")
    position = {p: i for i, p in enumerate(ports)}
    pair_code = [[F(0)] * 48 for _ in range(48)]
    for pair in source["pair_codes"]:
        for i, p in enumerate(pair["ports"]):
            for j, q in enumerate(pair["ports"]):
                pair_code[position[p]][position[q]] = F(pair["matrix"][i][j])
    pair_inverse = [[x / 2 for x in row] for row in zip(*pair_code)]
    need(product(pair_code, pair_inverse) == identity(48), "Actual pair inverse")
    block = [[F(0)] * 48 for _ in range(48)]
    block_inverse = [[F(0)] * 48 for _ in range(48)]
    e, inverse, _ = response(6)
    for carriers in source["cyclic_carriers"]:
        need(len(carriers) == 6, "Six modes at each vertex")
        for i, p in enumerate(carriers):
            for j, q in enumerate(carriers):
                block[position[p]][position[q]] = e[i][j]
                block_inverse[position[p]][position[q]] = inverse[i][j]
    physical = product(product(pair_inverse, block), pair_code)
    physical_inverse = product(product(pair_inverse, block_inverse), pair_code)
    need(product(physical, physical_inverse) == identity(48), "Physical right inverse")
    need(product(physical_inverse, physical) == identity(48), "Physical left inverse")
    need(rank(subtract(physical, identity(48))) == 16, "Physical correction rank")
    need(rank(subtract(physical_inverse, identity(48))) == 16, "Inverse correction rank")
    need(all(physical[i][i] == physical_inverse[i][i] == 0 for i in range(48)),
         "Physical diagonals")
    receipt = {
        "status": "PASS_RECIPROCAL_RANK_TWO",
        "source": str(SOURCE.relative_to(HERE.parent)),
        "source_sha256": SOURCE_SHA,
        "dimensions": dimensions,
        "six_mode_response": [[str(x) for x in row] for row in e],
        "six_mode_inverse": [[str(x) for x in row] for row in inverse],
        "physical_ports": ports,
        "physical_response": [[str(x) for x in row] for row in physical],
        "physical_inverse": [[str(x) for x in row] for row in physical_inverse],
        "physical_correction_rank": 16,
        "scope": "Exact response algebra; no native phase or terminal price claim",
    }
    output = HERE / "RECIPROCAL-RANK-TWO-20261020.json"
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])
    print("receipt_sha256=" + sha256(output.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
