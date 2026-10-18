"""Exact signed dependent-source connector model. Apache-2.0.

Prepared by Ross Richardson with substantial OpenAI Codex assistance.
Only rational/integer arithmetic is used; no predecessor code is imported.
"""
from fractions import Fraction
from itertools import product
from math import lcm


def need(ok, message):
    if not ok:
        raise ValueError(message)


def phi(t):
    return 2 if t == 0 else abs(t)


def normalize(rows):
    need(bool(rows) and bool(rows[0]), "nonempty source matrix required")
    d = len(rows[0])
    rows = tuple(tuple(Fraction(x) for x in row) for row in rows)
    need(all(len(row) == d and any(row) for row in rows), "nonzero equal-width rows required")
    scales = [lcm(*(row[j].denominator for row in rows)) for j in range(d)]
    return tuple(tuple(int(row[j] * scales[j]) for j in range(d)) for row in rows)


def optimum(rows, readers, sources):
    """Finite exact integer-kernel DP, bounded by the closed source bill.

    This is a mathematical query optimizer, not an efficient uniform controller.
    Its state, coefficient-preparation and instruction costs are not waived.
    """
    rows = normalize(rows)
    a, b = tuple(map(Fraction, readers)), tuple(map(Fraction, sources))
    need(len(rows) == len(a) == len(b), "tariff shape mismatch")
    need(all(x > 0 for x in a + b), "positive sign-symmetric prices required")
    cap = 2 * sum(b)
    zero = (0,) * len(rows[0])
    states = {zero: (Fraction(0), ())}
    visited = 1
    for i, (row, price) in enumerate(zip(rows, b)):
        nxt = {}
        limit = int(cap // price)
        reserve = sum(b[i + 1:])
        for state, (cost, path) in states.items():
            for t in range(-limit, limit + 1):
                bill = cost + price * phi(t)
                if bill + reserve > cap:
                    continue
                new = tuple(x + t * y for x, y in zip(state, row))
                value = (bill, path + (t,))
                if new not in nxt or value < nxt[new]:
                    nxt[new] = value
        states = nxt
        visited += len(states)
    source_cost, witness = states[zero]
    return {"total": 2 * sum(a) + source_cost, "source_cost": source_cost,
            "balance": witness, "states": visited, "closed_total": 2 * sum(a) + cap}


def epoch(t):
    """Signed A/B word with reader coefficient +1 and B net t."""
    if t == 0:
        return (("A", -1), ("B", 1), ("A", 1), ("B", -1))
    sign = 1 if t > 0 else -1
    return (("A", -sign), ("B", sign), ("A", sign)) + (("B", sign),) * (abs(t) - 1)


# Nine distinct dirty scalar ports: x[0:2], u[2:4], z[4:6], y[6:9].
B = ((1, 1), (1, -1))
A = ((1, 0), (0, 1), (1, 1))
N = 9


def pilot(balance):
    need(len(balance) == 3, "three requests required")
    word = []
    for i, t in enumerate(balance):
        for kind, sign in epoch(t):
            if kind == "B":
                for target, row in enumerate(B, 4):
                    for source, coefficient in enumerate(row):
                        if coefficient:
                            word.append((source, target, sign * coefficient, i, "B"))
            else:
                for source, coefficient in enumerate(A[i], 4):
                    if coefficient:
                        word.append((source, 6 + i, sign * coefficient, i, "A"))
        # The source visits x,x+u,x+2u, then explicitly returns to x.
        for _ in range(1 if i < 2 else 2):
            for coordinate in range(2):
                word.append((2 + coordinate, coordinate, 1 if i < 2 else -1, i, "M"))
    return tuple(word)


def direct_pilot():
    """Opening A/B permits a cheaper direct comparator; no global optimum claim."""
    word = []
    for i in range(3):
        row = tuple(sum(A[i][h] * B[h][j] for h in range(2)) for j in range(2))
        for source, coefficient in enumerate(row):
            for _ in range(abs(coefficient)):
                word.append((source, 6 + i, 1 if coefficient > 0 else -1, i, "DIRECT"))
        for _ in range(1 if i < 2 else 2):
            for coordinate in range(2):
                word.append((2 + coordinate, coordinate, 1 if i < 2 else -1, i, "M"))
    return tuple(word)


def identity():
    return [[int(i == j) for j in range(N)] for i in range(N)]


def expected():
    matrix = identity()
    for i in range(3):
        for j in range(2):
            value = sum(A[i][h] * B[h][j] for h in range(2))
            matrix[6 + i][j] += value
            matrix[6 + i][2 + j] += i * value
    return matrix


def symbolic(word, inverse=False):
    matrix = identity()
    maxima = [1] * N
    checkpoints = []
    steps = list(word)
    if inverse:
        steps = [(s, t, -q, i, k) for s, t, q, i, k in reversed(steps)]
    last_epoch = None
    for source, target, sign, i, kind in steps:
        need(0 <= source < N and 0 <= target < N and source != target and sign in (-1, 1), "bad gate")
        if kind == "A":
            need(target == 6 + i and source in (4, 5), "delivery ownership violation")
        if kind == "B":
            need(target in (4, 5) and source in (0, 1), "source-query ownership violation")
        if last_epoch is not None and i != last_epoch:
            need(inverse or i > last_epoch, "nonchronological request order")
            checkpoints.append((last_epoch, [row[:] for row in matrix]))
        matrix[target] = [a + sign * b for a, b in zip(matrix[target], matrix[source])]
        maxima[target] = max(maxima[target], sum(map(abs, matrix[target])))
        last_epoch = i
    if last_epoch is not None:
        checkpoints.append((last_epoch, matrix))
    return matrix, maxima, checkpoints


def execute(word, vector):
    state = list(vector)
    for source, target, sign, _, _ in word:
        state[target] += sign * state[source]
    return state


def invoice(word):
    kinds = {kind: sum(g[4] == kind for g in word) for kind in sorted({g[4] for g in word})}
    # Explicit unit-cell model: start/end at address zero for EVERY ADD.
    # Travel includes visiting both operands, then returning to zero.
    moves = sum(2 * max(source, target) for source, target, _, _, _ in word)
    return {"unit_adds": len(word), "head_moves": moves, "unit_steps": moves + len(word),
            "fixed_scalar_ports": N, "by_kind": kinds,
            "peak_row_l1": max(symbolic(word)[1]), "per_port_peak_row_l1": symbolic(word)[1],
            "inverse_peak_row_l1": max(symbolic(word, inverse=True)[1]),
            "inverse_per_port_peak_row_l1": symbolic(word, inverse=True)[1]}


def finite_grid(word):
    target = expected()
    count = 0
    for vector in product((-1, 0, 1), repeat=N):
        result = execute(word, vector)
        need(result == [sum(a * b for a, b in zip(row, vector)) for row in target], "dirty-grid endpoint mismatch")
        inverse = tuple((s, t, -q, i, k) for s, t, q, i, k in reversed(word))
        need(execute(inverse, result) == list(vector), "dirty-grid inverse mismatch")
        count += 1
    return count
