"""Small exact rational algebra for the path-rank audit (Apache-2.0).

Copyright 2026 Curtis Dransfield. Substantial OpenAI Codex assistance.
No floating-point or modular rank heuristics are used.
"""
from fractions import Fraction as F


def require(condition, message):
    if not condition:
        raise ValueError(message)


def matrix(rows):
    rows = tuple(tuple(row) for row in rows)
    require(rows and rows[0] and all(len(row) == len(rows[0]) for row in rows),
            'Nonempty rectangular matrix required')
    require(all(type(x) in (int, str, F) for row in rows for x in row),
            'Use exact integer/rational entries')
    return tuple(tuple(F(x) for x in row) for row in rows)


def eye(n):
    return matrix([[int(i == j) for j in range(n)] for i in range(n)])


def zero(n):
    return matrix([[0] * n for _ in range(n)])


def transpose(A):
    return tuple(zip(*A))


def add(A, B):
    require(len(A) == len(B) and len(A[0]) == len(B[0]), 'Matrix shape mismatch')
    return tuple(tuple(a + b for a, b in zip(ar, br)) for ar, br in zip(A, B))


def scale(A, c):
    return tuple(tuple(c * x for x in row) for row in A)


def sub(A, B):
    return add(A, scale(B, -1))


def mul(A, B):
    require(len(A[0]) == len(B), 'Product shape mismatch')
    return tuple(tuple(sum(a * b for a, b in zip(row, col)) for col in zip(*B)) for row in A)


def rref(A):
    out = [list(row) for row in A]
    pivots = []
    for col in range(len(out[0])):
        row = next((i for i in range(len(pivots), len(out)) if out[i][col]), None)
        if row is None:
            continue
        target = len(pivots)
        out[target], out[row] = out[row], out[target]
        value = out[target][col]
        out[target] = [x / value for x in out[target]]
        for i in range(len(out)):
            if i != target:
                value = out[i][col]
                out[i] = [x - value*y for x, y in zip(out[i], out[target])]
        pivots.append(col)
        if len(pivots) == len(out):
            break
    return tuple(tuple(row) for row in out), tuple(pivots)


def rank(A):
    return len(rref(A)[1])


def nullspace(A):
    reduced, pivots = rref(A)
    basis = []
    for free in range(len(A[0])):
        if free not in pivots:
            v = [F(0)] * len(A[0])
            v[free] = F(1)
            for row, pivot in enumerate(pivots):
                v[pivot] = -reduced[row][free]
            basis.append(tuple(v))
    return tuple(basis)


def inverse(A):
    n = len(A)
    require(len(A[0]) == n, 'Square inverse required')
    augmented = tuple(a + b for a, b in zip(A, eye(n)))
    reduced, pivots = rref(augmented)
    require(pivots == tuple(range(n)), 'Singular inverse')
    return tuple(row[n:] for row in reduced)


def kron(A, B):
    return tuple(tuple(a*b for a in ar for b in br) for ar in A for br in B)


def serializable(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {k: serializable(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serializable(v) for v in value]
    return value


def analyze_pair(P, Q):
    P, Q = matrix(P), matrix(Q)
    d = len(P)
    require(len(P[0]) == d and len(Q) == d and len(Q[0]) == d, 'Equal square dimensions required')
    require(mul(P, P) == P and mul(Q, Q) == Q, 'Idempotence required')
    I = eye(d)
    PQ, QP, R = mul(P, Q), mul(Q, P), sub(sub(I, P), Q)
    p, q, pq, qp, r = map(rank, (P, Q, PQ, QP, R))
    left = nullspace(sub(I, P) + Q)  # im(P) intersect ker(Q), via stacked equations
    right = nullspace(sub(I, Q) + P)
    combined = left + right
    require(len(left) == p - qp and len(right) == q - pq, 'Intersection dimension mismatch')
    require((rank(combined) if combined else 0) == len(combined), 'Kernel summands are not direct')
    for v in combined:
        require(all(x == 0 for row in mul(R, transpose((v,))) for x in row), 'Kernel witness failed')
    require(len(combined) == d - r, 'Kernel witnesses do not span')
    signed = rank(sub(I, Q)) - p
    require(signed == d - q - p, 'Complement rank mismatch')
    require(r == d - p - q + pq + qp, 'Endpoint rank identity failed')
    require(r - signed == pq + qp, 'Exact excess identity failed')
    return dict(d=d, rank_P=p, rank_Q=q, rank_PQ=pq, rank_QP=qp,
                endpoint_difference_rank=r, signed_rank_increment=signed,
                minimum_path_excess=pq + qp,
                kernel_left_basis=left, kernel_right_basis=right)


def path_excess(chain):
    require(len(chain) >= 2, 'Path needs two endpoints')
    charge = sum(rank(sub(B, A)) for A, B in zip(chain, chain[1:]))
    signed = rank(chain[-1]) - rank(chain[0])
    require(charge >= rank(sub(chain[-1], chain[0])), 'Rank triangle inequality failed')
    return dict(charge=charge, signed_rank_increment=signed, excess=charge - signed)
