"""Cube-zero pencil lifts. Ali Romman with OpenAI Codex assistance. Apache-2.0."""
from itertools import product
import json

MONOMIALS = ((0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2))
X, Y, L = 2, 4, 6


def require(ok, message):
    if not ok:
        raise ValueError(message)


def ring_table():
    lookup = {a: i for i, a in enumerate(MONOMIALS)}
    table = [[0]*64 for _ in range(64)]
    for a, b in product(range(64), repeat=2):
        for i, (ix, iy) in enumerate(MONOMIALS):
            for j, (jx, jy) in enumerate(MONOMIALS):
                if (a >> i) & (b >> j) & 1 and ix+iy+jx+jy <= 2:
                    table[a][b] ^= 1 << lookup[(ix+jx, iy+jy)]
    return table


def mm(a, b, t):
    return (t[a[0]][b[0]] ^ t[a[1]][b[2]],
            t[a[0]][b[1]] ^ t[a[1]][b[3]],
            t[a[2]][b[0]] ^ t[a[3]][b[2]],
            t[a[2]][b[1]] ^ t[a[3]][b[3]])


def response(row, matrix, col, t):
    a = t[row[0]][matrix[0]] ^ t[row[1]][matrix[2]]
    b = t[row[0]][matrix[1]] ^ t[row[1]][matrix[3]]
    return t[a][col[0]] ^ t[b][col[1]]


def parity(q):
    return ((q >> 3).bit_count() & 1)


def main():
    t = ring_table()
    radical = range(0, 64, 2)
    quadratics = range(0, 64, 8)
    ideal = {t[L][a] for a in radical}
    require(ideal == {0, 24, 40, 48}, 'quadratic ideal')
    rows = ((1, 0), (0, 1), (1, 1))
    bases = [(a, b) for a, b in product(rows, repeat=2) if a != b]
    ideals = [{t[a][b] for b in range(64)} for a in range(64)]
    g = (1, 1, 0, 1)
    counts = [0, 0]; zero_charts = constructions = covariance = 0
    for q in product(quadratics, repeat=4):
        m = (X ^ q[0], Y ^ q[1], Y ^ q[2], X ^ q[3])
        omega = q[0] ^ q[1] ^ q[2] ^ q[3]
        good = omega in ideal
        require(t[m[0]][m[3]] ^ t[m[1]][m[2]] == 40, 'fixed nonzero determinant')
        criterion = any(response(row, m, v, t) in ideals[response(row, m, w, t)]
                        for row in rows for w, v in bases)
        require(criterion == good, 'literal two-factor chart criterion')
        require(good == (parity(omega) == 0), 'parity expression')
        counts[not good] += 1
        exact_zero = sum(response(row, m, col, t) == 0 for row, col in product(rows, repeat=2))
        zero_charts += exact_zero
        require(exact_zero == int(omega == 0), 'unique common base-field zero')
        if good:
            n = mm(mm(g, m, t), g, t)
            b = next(b for b in (0, X, Y, L) if t[L][b] == omega)
            c1 = (n[0], 0, n[2], 1)
            c2 = (1, b, 0, n[3] ^ t[n[2]][b])
            require(mm(mm(mm(g, c1, t), c2, t), g, t) == m, 'literal two-factor word')
            constructions += 1
        for a, b, c, d in product((0, X, Y, L), repeat=4):
            lifted = response((1 ^ a, 1 ^ b), m, (1 ^ c, 1 ^ d), t)
            require((lifted ^ omega) in ideal, 'second-order class under lifted rows and columns')
            covariance += 1
    determinant_pairs = [(a, b) for a, b in product(radical, repeat=2) if t[a][b] == 40]
    require(len(determinant_pairs) == 64, 'all nonunit determinant pairs')
    for a, b in determinant_pairs:
        require(a & 6 == b & 6 == L, 'forced linear determinants')
        require(all(t[t[a][b]][c] in ideal for c in range(64)), 'normal-form corner class')
    require(counts == [2048, 2048] and zero_charts == 512, 'lift census')
    require(8 not in ideal and 24 in ideal, 'opposite lifting controls')
    require(t[t[X][X]][X] == 0 and t[X][X] != 0, 'cube-zero versus square-zero')
    require(t[L][L] == 40 != 0, 'nonzero determinant premise')
    print(json.dumps(dict(status='PASS_CUBE_ZERO_LIFT_OBSTRUCTION', lifts=sum(counts),
                         cost_two=counts[0], unreachable=counts[1], exact_zero_chart_targets=zero_charts,
                         literal_constructions=constructions, covariance_checks=covariance,
                         nonunit_determinant_pairs_checked=1024, feasible_determinant_pairs=len(determinant_pairs),
                         no_new_kappa=True), sort_keys=True))


if __name__ == '__main__':
    main()
