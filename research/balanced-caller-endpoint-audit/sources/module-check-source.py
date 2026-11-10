"""Check the four-field composition with three formal commuting variables.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
This checker does not import the caller generator.
"""
from fractions import Fraction as Q

ZERO = (0, 0, 0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def constant(matrix):
    return [[{ZERO: Q(x)} if x else {} for x in row] for row in matrix]


def identity():
    return constant([[int(i == j) for j in range(4)] for i in range(4)])


def multiply(a, b):
    out = [[{} for _ in range(4)] for _ in range(4)]
    for i in range(4):
        for k in range(4):
            for j in range(4):
                for x, u in a[i][k].items():
                    for y, v in b[k][j].items():
                        key = tuple(s+t for s, t in zip(x, y))
                        value = out[i][j].get(key, 0)+u*v
                        if value:
                            out[i][j][key] = value
                        else:
                            out[i][j].pop(key, None)
    return out


def run():
    R = constant([[1, 0, 0, 1], [0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]])
    L = constant([[1, 0, 0, 0], [0, 0, 0, 1], [1, 0, -1, 0], [0, -1, 0, 1]])
    S = identity()
    S[0][2] = {ZERO: Q(1)}
    Si = identity()
    Si[0][2] = {ZERO: Q(-1)}
    C = identity()
    C[2][1], C[2][3] = {(1, 0, 0): Q(-1)}, {(1, 0, 0): Q(1)}
    idle = identity()
    idle[2][2] = idle[3][3] = {(0, 1, 1): Q(1)}
    A = identity()
    A[0][0] = A[1][1] = {(0, 1, 0): Q(1)}
    A[0][1] = {(1, 1, 0): Q(1)}
    B = identity()
    B[0][0] = B[1][1] = {(0, 0, 1): Q(1)}
    B[1][0] = {(-1, 0, 1): Q(-1)}
    word = [R, C, Si, idle, B, A, S, L]
    result = identity()
    for gate in word:
        result = multiply(gate, result)
    expected = identity()
    for i in range(4):
        expected[i][i] = {(0, 1, 1): Q(1)}
    expected[0][1] = {(1, 1, 1): Q(1)}
    expected[2][2] = {(1, 1, 1): Q(1)}
    expected[3][3] = {(-1, 1, 1): Q(1)}
    need(result == expected, 'Exact four-field query-extension identity')
    bad = identity()
    for gate in word[:3]+word[4:]:
        bad = multiply(gate, bad)
    need(bad != expected, 'Removing the charged idle fails')
    need(multiply(S, Si) == identity(), 'Common two-field plane has an ordinary inverse')
    return {'variables': ['q', 'D_A', 'D_B'], 'coefficients': 16,
            'identity': 'L S A B Idle S^-1 C R = D_A D_B (U(q) direct-sum q direct-sum q^-1)',
            'missing_idle_rejected': True}


if __name__ == '__main__':
    print(run())
