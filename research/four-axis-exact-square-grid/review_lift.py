#!/usr/bin/env python3
"""Independent lattice/phase review; does not import the author's search.

This is a separate review of the finite-to-infinite argument. The lead's
direct integer checker owns the complete 4096-class transition replay.
Jerry Chen / @CubeJerry with substantial OpenAI assistance, Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "CERTIFICATE.json"
CERTIFICATE_SHA256 = "44a950a62abec947b4c094c2c1f290bec2f8d7f41d3a108ab4c58b5bdfc46b56"


def need(ok, label):
    if not ok:
        raise ValueError(label)


def multiply(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def inverse(a):
    n = len(a)
    rows = [[Q(x) for x in row] + unit for row, unit in zip(a, eye(n))]
    for j in range(n):
        pivot = next(i for i in range(j, n) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scalar = rows[j][j]
        rows[j] = [x/scalar for x in rows[j]]
        for i in range(n):
            if i != j:
                scalar = rows[i][j]
                rows[i] = [a-scalar*b for a,b in zip(rows[i], rows[j])]
    need([row[:n] for row in rows] == eye(n), "rational inverse left block")
    return [row[n:] for row in rows]


def binary_rank(masks):
    pivots = {}
    for value in masks:
        while value:
            j = value.bit_length()-1
            if j not in pivots:
                pivots[j] = value
                break
            value ^= pivots[j]
    return len(pivots)


def main():
    raw = SOURCE.read_bytes()
    need(sha256(raw).hexdigest() == CERTIFICATE_SHA256, "compressed certificate SHA256")
    data = json.loads(raw)
    need(data["schema_version"] == 1 and len(data["cycles"]) == 568, "compressed certificate shape")
    masks = data["period_rows"]
    need(masks == [0x21, 0x906, 0x6fde, 0x103, 0xa8ec, 0x29e], "period rows")

    # Tensor construction of W, independent of the author's bit-dot formula.
    w = [[1]]
    for _ in range(4):
        w = [row + row for row in w] + [row + [-x for x in row] for row in w]
    s = [(-1)**j.bit_count() for j in range(16)]
    a = [[Q(x, 4) for x in row] for row in w]
    b = [[sign*x for x in row] for sign, row in zip(s, a)]
    jmatrix = [[int(col == (row ^ 15)) for col in range(16)] for row in range(16)]
    kmatrix = [[sign*x for x in row] for sign, row in zip(s, jmatrix)]
    need(multiply(a, a) == eye(16), "Walsh isometry/involution")
    need(multiply(b, b) == kmatrix, "B squared equals signed reversal")
    need(multiply(kmatrix, kmatrix) == eye(16), "signed reversal involution")

    columns = [[4] + [0]*15]
    for bit in range(4):
        column = [0]*16
        column[0], column[1 << bit] = -2, 2
        columns.append(column)
    for vertex in range(16):
        if vertex.bit_count() < 2:
            continue
        column = [0]*16
        column[vertex], column[0] = 1, vertex.bit_count()-1
        for bit in range(4):
            if vertex >> bit & 1:
                column[1 << bit] = -1
        columns.append(column)
    p = list(map(list, zip(*columns)))
    pinv = inverse(p)
    action = multiply(multiply(pinv, b), p)
    need(all(x.denominator == 1 for row in action for x in row), "B preserves integral L")
    action = [[int(x) for x in row] for row in action]
    need(multiply(multiply(action, action), multiply(action, action)) == eye(16), "B automorphism of L")

    dual = []
    for mask in masks:
        dual.append(sum((sum(action[i][j] for i in range(16) if mask >> i & 1) % 2) << j
                        for j in range(16)))
    expected_dual = [masks[0]^masks[1], masks[1]^masks[2], masks[2],
                     masks[3]^masks[4], masks[4]^masks[5], masks[5]]
    need(dual == expected_dual, "Gamma stable by exact dual row action")
    need(binary_rank(masks) == 6, "six independent period constraints")
    need(binary_rank([mask & 31 for mask in masks]) == 5, "no oddness obstruction on even vectors")

    # Independent matrix-rank check of the predecessor's lower-bound premise.
    # E consists of the first five L-coordinate directions. C=K+I on L/2L.
    kaction = multiply(action, action)
    ccolumns = [sum(((kaction[i][j]+int(i == j)) % 2) << i for i in range(16))
                for j in range(16)]
    c_rank = binary_rank(ccolumns)
    joint_rank = binary_rank(ccolumns + [1 << i for i in range(5)])
    intersection = 5+c_rank-joint_rank
    need(ccolumns[:5] == [0, 1, 1, 1, 1], "rank-one C restriction to E")
    need(c_rank == 6 and joint_rank == 9 and intersection == 2,
         "two-dimensional E intersection image C")

    # Exact phase pair: D_v D_{v xor 15}=(-i)^4=1.
    need(all((v.bit_count()+(v^15).bit_count()) % 4 == 0 for v in range(16)), "D J D=J")
    result = {
        "status": "PASS_INDEPENDENT_LATTICE_PHASE_LIFT_REVIEW",
        "certificate_sha256": sha256(raw).hexdigest(),
        "lattice_index": 64,
        "period_constraints_rank": 6,
        "period_index": 4096,
        "low_coordinate_restriction_rank": 5,
        "predecessor_C_rank": c_rank,
        "predecessor_E_plus_image_C_rank": joint_rank,
        "predecessor_E_intersection_image_C_dimension": intersection,
        "dual_action": dual,
        "scope": "Independent lattice and phase derivation; complete finite table identities are checked separately by independent_square.py."
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
