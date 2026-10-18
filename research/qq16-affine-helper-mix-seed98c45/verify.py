#!/usr/bin/env python3
"""Exact rational controls for the QQ16 mixed-affine-helper rank corollary."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rank(matrix):
    if not matrix:
        return 0
    a = [[Q(x) for x in row] for row in matrix]
    ncols = len(a[0])
    r = 0
    for col in range(ncols):
        pivot = next((i for i in range(r, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        scale = a[r][col]
        a[r] = [x / scale for x in a[r]]
        for i in range(len(a)):
            if i != r and a[i][col]:
                factor = a[i][col]
                a[i] = [x - factor*y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def stack(*blocks):
    return [list(row) for block in blocks for row in block]


def matmul(a, b):
    need(bool(a) and bool(b) and len(a[0]) == len(b), "matrix dimensions")
    return [[sum((Q(a[i][k])*Q(b[k][j]) for k in range(len(b))), Q(0))
             for j in range(len(b[0]))] for i in range(len(a))]


def add(a, b):
    need(len(a) == len(b) and all(len(x) == len(y) for x, y in zip(a, b)),
         "addition dimensions")
    return [[Q(x)+Q(y) for x, y in zip(rx, ry)] for rx, ry in zip(a, b)]


def matvec(a, x):
    return [sum((Q(v)*Q(t) for v, t in zip(row, x)), Q(0)) for row in a]


def nullspace(a):
    if not a:
        return []
    work = [[Q(x) for x in row] for row in a]
    ncols, r, pivots = len(work[0]), 0, []
    for col in range(ncols):
        pivot = next((i for i in range(r, len(work)) if work[i][col]), None)
        if pivot is None:
            continue
        work[r], work[pivot] = work[pivot], work[r]
        scale = work[r][col]
        work[r] = [x/scale for x in work[r]]
        for i in range(len(work)):
            if i != r and work[i][col]:
                factor = work[i][col]
                work[i] = [x-factor*y for x, y in zip(work[i], work[r])]
        pivots.append(col)
        r += 1
    free = [j for j in range(ncols) if j not in pivots]
    basis = []
    for col in free:
        vector = [Q(0)] * ncols
        vector[col] = Q(1)
        for i, pivot in enumerate(pivots):
            vector[pivot] = -work[i][col]
        basis.append(vector)
    return basis


def authenticate_inputs():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in manifest["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            need(sha256(raw).hexdigest() == row["sha256"], "pinned input drift: " + row["path"])


def main():
    authenticate_inputs()
    # A full-row-rank three-query analogue with a two-coordinate helper.
    # The proof is symbolic; these exact controls exercise the row-space step.
    b0 = [[1,0,0,0,0], [0,1,0,0,0]]
    b1 = [[0,1,1,0,0], [1,0,1,0,0]]
    b2 = [[0,0,0,1,0], [0,0,0,0,1]]
    identity = [[1,0],[0,1]]
    zero = [[0,0],[0,0]]
    mixers = [zero, identity,
              [[2,Q(1,2)],[Q(-1,3),3]],
              [[Q(1,3),2],[-4,Q(5,2)]]]
    full_rank = rank(stack(b0, b1, b2))
    need(full_rank == 5, "positive-control source stack")
    for index, mixer in enumerate(mixers):
        mixed = add(b0, matmul(mixer, b2))
        observed = stack(mixed, b1)
        restored_stack = stack(observed, b2)
        need(rank(restored_stack) == full_rank, f"row-space recovery case {index}")
        need(rank(observed) <= 4, f"two-query row cap case {index}")
        need(rank(restored_stack)-rank(observed) > 0, f"nonzero residual case {index}")
        witness = next((h for h in nullspace(observed) if any(matvec(b2, h))), None)
        need(witness is not None, f"kernel witness case {index}")
        need(not any(matvec(observed, witness)) and any(matvec(b2, witness)),
             f"kernel equations case {index}")
        dirty, offset = [Q(13), Q(-5)], [Q(2), Q(7)]
        response_h = [dirty[i] + matvec(mixed, witness)[i] + offset[i] for i in range(2)]
        response_zero = [dirty[i] + offset[i] for i in range(2)]
        need(response_h == response_zero, f"affine cancellation case {index}")

    # Exact trace arithmetic in the source-pinned predecessor lemma.
    need(Q(1152**2, 64512) == Q(144, 7), "trace ratio")
    need(Q(144, 7)-16 == Q(32, 7) and Q(32, 7) > 0, "residual dimension")

    # Negative controls: omitting B2 breaks reconstruction; a plus sign in the
    # inverse identity is wrong for nonzero M; a corrupted trace fails exactly.
    base_observed = stack(b0, b1)
    need(rank(stack(base_observed, b0)) < full_rank, "omitted-B2 control")
    nonzero_m = mixers[2]
    nonzero_m_b2 = matmul(nonzero_m, b2)
    mixed = add(b0, nonzero_m_b2)
    wrong_reconstruction = add(mixed, nonzero_m_b2)
    need(wrong_reconstruction != b0, "sign-mutation control")
    need(Q(1152**2, 64513) != Q(144, 7), "trace-mutation control")

    print("PASS_QQ16_AFFINE_HELPER_MIX cases=4 positives=4 controls=3 no_new_kappa")


if __name__ == "__main__":
    main()
