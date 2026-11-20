"""Exact common H schedule on complete coarse fibers with different local matchings."""

from fractions import Fraction as F
from itertools import product
from math import prod

BITS = (0, 1, 0)
N = 4
AXES = 3


def check(condition, message):
    if not condition:
        raise ValueError(message)


def pairs(bit):
    return [(i, i ^ (1 << bit)) for i in range(N) if (i >> bit) & 1 == 0]


def route(mask):
    permutation = list(range(N))
    for k, bit in enumerate(BITS):
        for j, (u, v) in enumerate(pairs(bit)):
            if mask & (1 << (2 * k + j)):
                permutation[u], permutation[v] = permutation[v], permutation[u]
    return tuple(permutation)


ROUTES = {route(mask): mask for mask in range(64)}
check(len(ROUTES) == 24, "three stages realize all four-wire permutations")


def compile_steps(steps):
    # Endianness here is execution order. Entries are pairs on adjacent wires.
    diagonals = [(F(1), F(1))]
    for step in steps:
        if step is None:
            diagonals.append((F(1), F(1)))
        else:
            diagonals[-1] = tuple(v * w for v, w in zip(diagonals[-1], step))
    return diagonals


def shear(q):
    q = F(q)
    return [(5 / (4 * q), 1), None, (-3, 1), None, (2, 1), None,
            (-F(1, 8), -F(1, 6)), (4 * q / 5, 1)]


def gate(kind, t):
    if kind in ("U", "L"):
        c = 2 * abs(t) + 1
        steps = shear(-c) + shear(t + c)
        if kind == "L":
            steps.reverse()
    else:
        first = (1, 1 if kind == "I" else -1)
        steps = [None, first, None, (F(1, 2), F(1, 2))]
        steps += [None, None, (F(1, 2), F(1, 2))] * 2
    ds = compile_steps(steps)
    check(len(ds) == 7, "six actual Hadamards on both controls")
    return ds


def program(permutation, gates):
    mask = ROUTES[permutation]
    layers = []
    for k, bit in enumerate(BITS):
        diag = [F(1)] * N
        for j, (_, v) in enumerate(pairs(bit)):
            if mask & (1 << (2 * k + j)):
                diag[v] = -1
        layers.append((bit, diag))
    def switches(group):
        out = []
        for bit, diag in group:
            out += [("H", bit), ("D", diag), ("H", bit), ("D", [F(1, 2)] * N)]
        return out
    middle = []
    gd = [gate(*info) for info in gates]
    for k in range(7):
        middle.append(("D", [gd[i // 2][k][i % 2] for i in range(N)]))
        if k < 6:
            middle.append(("H", 0))
    return switches(layers) + middle + switches(reversed(layers))


def direct(permutation, gates):
    matrix = [[F(0)] * N for _ in range(N)]
    for i, (kind, t) in enumerate(gates):
        local = {
            "U": ((1, t), (0, 1)),
            "L": ((1, 0), (t, 1)),
            "I": ((1, 0), (0, 1)),
            "J": ((0, 1), (1, 0)),
        }[kind]
        for r, c in product(range(2), repeat=2):
            matrix[permutation[2 * i + r]][permutation[2 * i + c]] = F(local[r][c])
    return matrix


def replay():
    specs = [[((2, 0, 3, 1), (("U", 0), ("L", F(-4, 9)))),
              ((1, 3, 2, 0), (("J", 0), ("U", F(3, 7)))),
              ((2, 3, 0, 1), (("L", 1), ("I", 0)))],
             [((0, 1, 2, 3), (("I", 0), ("U", F(-1, 5)))),
              ((2, 1, 0, 3), (("L", F(2, 11)), ("J", 0))),
              ((1, 2, 3, 0), (("U", -2), ("L", 0)))]]
    plans = [[program(*spec) for spec in group] for group in specs]
    matrices = [[direct(*spec) for spec in group] for group in specs]
    positions = tuple(product(range(N), repeat=AXES))
    steps = len(plans[0][0])
    hbits = []
    for step in range(steps):
        cases = [plans[c][j][step] for c in range(2) for j in range(AXES)]
        check(len({t[0] for t in cases}) == 1, "nonuniform call shape")
        if cases[0][0] == "H":
            check(len({t[1] for t in cases}) == 1, "nonuniform selected slot")
            hbits.append(cases[0][1])
    for col in positions:
        x = {(c, row): F(row == col) for c in range(2) for row in positions}
        for step in range(steps):
            typ, d = plans[0][0][step]
            if typ == "D":
                x = {(c, row): v * prod(plans[c][j][step][1][row[j]] for j in range(AXES))
                     for (c, row), v in x.items()}
            else:
                # Exactly H^tensor(3) on this slot, independently of the coarse label.
                # Factorization below is the slow oracle for this one uniform public gate.
                for j in range(AXES):
                    nxt = {}
                    for (c, row), v in x.items():
                        partner = list(row)
                        partner[j] ^= 1 << d
                        w = x[c, tuple(partner)]
                        nxt[c, row] = w - v if (row[j] >> d) & 1 else v + w
                    x = nxt
        for (c, row), v in x.items():
            expected = prod(matrices[c][j][row[j]][col[j]] for j in range(AXES))
            check(v == expected, "global H/diagonal word differs from wanted tensor")
    return len(hbits), 2 * len(positions) ** 2


if __name__ == "__main__":
    print("Common complete Hadamard calls and exact matrix entries", replay())
