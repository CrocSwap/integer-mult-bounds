#!/usr/bin/env python3
"""Exact base-word certificate for a uniform single-owner coset obstruction."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ARITHMETIC_SHA = '0d277854396e4ceda1e0f26916bd576b6decb474c0692b6671ebf2595283ddb9'


def require(value, message):
    if not value:
        raise ValueError(message)


def load():
    path = HERE / 'retained' / 'arithmetic.py'
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == ARITHMETIC_SHA, 'retained arithmetic hash')
    module = types.ModuleType('retained_arithmetic')
    exec(compile(data, str(path), 'exec'), module.__dict__)
    return module


def verify():
    v = load()
    I = v.ident()
    C = [v.c_letter(j) for j in range(3)]
    S = v.s_letter(7)
    U = v.monomial([0, 5, 2, 7, 4, 1, 6, 3])
    V = v.monomial([0, 2, 1, 3, 4, 6, 5, 7])
    T = v.monomial([0, 4, 2, 6, 1, 5, 3, 7])
    V21 = v.monomial([0, 1, 4, 5, 2, 3, 6, 7])
    P, Q, Q2 = v.word(S, U, S), v.word(S, V, S), v.word(S, V21, S)
    W = v.pauli(0, 5)
    N = v.word(v.pauli(0, 2), V)
    L, J = v.word(N, T), v.word(N, C[2])
    K = v.word(*C)
    A = v.word(v.adjoint(L), J, W)
    R4 = v.word(C[0], P, C[0])
    R6 = v.word(C[0], P, A, C[0], Q, C[0])
    R7 = v.word(C[0], Q, A, C[0], P, C[0])
    refs = [('I', I), ('C0', C[0]), ('R4', R4), ('C2', C[2]), ('R7', R7), ('R6', R6)]
    row_order = ['x', 'u', 'v', 'r', 'z', 't']

    def plus(*rows):
        result = {}
        for row in rows:
            for key, coefficient in row.items():
                result[key] = result.get(key, F(0)) + coefficient
        return {key: value for key, value in result.items() if value}

    def left(matrix, row, coefficient=F(1)):
        result = {}
        for (owner, word), value in row.items():
            key = owner, v.mm(matrix, word)
            result[key] = result.get(key, F(0)) + coefficient * value
        return {key: value for key, value in result.items() if value}

    def program(feed):
        x = {(0, I): F(1)}
        y = {(1, I): F(1)}
        u = left(C[0], x)
        vv = left(C[0], plus(left(P, u), left(Q, u, 2)))
        r = left(v.word(v.adjoint(L), J), plus(left(W, vv), left(T, feed)))
        t = left(C[0], plus(left(P, r), left(Q, r, 2)))
        z = left(J, plus(left(W, t), left(Q2, r), left(P, vv)))
        return {'x': x, 'y': y, 'u': u, 'v': vv, 'r': r, 't': t, 'z': z}

    def monomial(matrix):
        return (all(sum(c != v.ZERO for c in row) == 1 for row in matrix)
                and all(sum(matrix[i][j] != v.ZERO for i in range(8)) == 1 for j in range(8))
                and all(c == v.ZERO or c in v.I_POWERS for row in matrix for c in row))

    def describe(matrix):
        require(monomial(matrix), 'fourth-root monomial')
        places = [next(i for i in range(8) if matrix[i][j] != v.ZERO) for j in range(8)]
        return {'permutation': places, 'phase_i': [v.I_POWERS.index(matrix[places[j]][j]) for j in range(8)]}

    def digest(matrix):
        return hashlib.sha256(json.dumps([[str(x) for pair in row for x in pair] for row in matrix]).encode()).hexdigest()

    def project(row):
        out = [[] for _ in refs]
        for (owner, word), coefficient in row.items():
            if owner != 0:
                continue
            for index, (_, representative) in enumerate(refs):
                quotient = v.word(word, v.adjoint(representative))
                if monomial(quotient):
                    out[index].append((coefficient, quotient))
        return out

    def certificate(rows):
        table = [project(rows[name]) for name in row_order]
        require(all(not table[i][j] for i in range(6) for j in range(i + 1, 6)), 'triangular support')
        require([c for c, _ in table[0][0]] == [1], 'x pivot')
        require([c for c, _ in table[1][1]] == [1], 'u pivot')
        require([c for c, _ in table[2][2]] == [1], 'v pivot')
        require([c for c, _ in table[3][3]] == [1], 'r pivot')
        require([c for c, _ in table[4][4]] == [1, 2], 'z unit pencil')
        require([c for c, _ in table[5][5]] == [2], 't pivot')
        return table

    all_refs = refs + [('K', K)]
    separated = []
    for i, (name, representative) in enumerate(all_refs):
        require(v.word(representative, v.adjoint(representative)) == I, 'unitary base word')
        for other, value in all_refs[:i]:
            require(not monomial(v.word(representative, v.adjoint(value))), 'distinct left H cosets')
            separated.append([other, name])
    rows = program({(1, I): F(1)})
    table = certificate(rows)
    g1, g2 = [matrix for _, matrix in table[4][4]]
    R = v.word(v.adjoint(g1), g2)
    powers = [I]
    for _ in range(4):
        powers.append(v.mm(powers[-1], R))
    require(powers[4] == I and len(set(powers[:4])) == 4, 'relative monomial has exact order four')
    # Verify in the group algebra, not only its possibly nonfaithful 8x8 representation.
    polynomial = {powers[k]: F((-2) ** k) for k in range(4)}
    multiplied = plus({(0, key): value for key, value in polynomial.items()},
                      left(R, {(0, key): value for key, value in polynomial.items()}, 2))
    require(multiplied == {(0, I): F(-15)}, 'group-algebra geometric inverse')
    inverse = v.scale(v.q(F(-1, 15)), v.plus(v.plus(I, v.scale(v.q(-2), powers[1])),
                                                    v.plus(v.scale(v.q(4), powers[2]), v.scale(v.q(-8), powers[3]))))
    D = v.plus(g1, v.scale(v.q(2), g2))
    require(v.word(D, inverse, v.adjoint(g1)) == I, 'right concrete inverse')
    require(v.word(inverse, v.adjoint(g1), D) == I, 'left concrete inverse')

    sectors = []
    y = {(1, I): F(1)}
    for shift in range(1, 8):
        X = v.pauli(shift, 0)
        require(v.word(X, X) == I and X != I, 'nontrivial sector involution')
        for sign in (-1, 1):
            feed = plus(left(I, y, F(1, 2)), left(X, y, F(sign, 2)))
            complement = plus(left(I, y, F(1, 2)), left(X, y, F(-sign, 2)))
            require(plus(feed, complement) == y, 'fresh-owner complement retained')
            changed = program(feed)
            require(certificate(changed) == table, 'x certificate independent of sector feed')
            sectors.append({'shift': shift, 'sign': sign, 'same_x_certificate': True})

    controls = []
    def rejects(name, action):
        try:
            action()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('control accepted: ' + name)

    broken = dict(rows); broken['t'] = {}
    rejects('missing_t_pivot', lambda: certificate(broken))
    broken2 = dict(rows); broken2['r'] = {(0, K): F(1)}
    rejects('target_substituted_for_residual', lambda: certificate(broken2))
    bad_d = v.plus(g1, g2)
    alternating = v.plus(v.plus(I, v.scale(v.q(-1), powers[1])), v.plus(powers[2], v.scale(v.q(-1), powers[3])))
    require(alternating != v.scale(v.ZERO, I) and v.word(bad_d, alternating) == v.scale(v.ZERO, I), 'coefficient-one singular control')
    controls.append('coefficient_one_is_not_a_unit')
    alpha, beta = v.q(F(1, 2), F(1, 2)), v.q(F(1, 2), F(-1, 2))
    require(C[0] == v.plus(v.scale(alpha, I), v.scale(beta, v.pauli(1, 0))), 'width-one free span calibration')
    # At width two the (00,01) entry is alpha*beta=1/2, whereas a*I+b*(X tensor X) gives zero.
    require(v.mul(alpha, beta) == v.q(F(1, 2)), 'width-one identity does not tensorize as a sum')
    controls.append('width_one_free_span_does_not_tensorize')
    require(v.scale(v.q(-1), I) != I and v.word(v.scale(v.q(-1), I), v.scale(v.q(-1), I)) == I, 'central phases remain distinct base words')
    controls.append('central_phase_not_quotiented')

    return {'status': 'PASS_STAGGERED_SINGLE_OWNER_OBSTRUCTION',
            'source_arithmetic_sha256': ARITHMETIC_SHA,
            'rows': row_order, 'columns': [name for name, _ in refs],
            'coset_representative_sha256': {name: digest(matrix) for name, matrix in all_refs},
            'separated_coset_pairs': separated,
            'coefficient_table': [[ [{'coefficient': str(c), **describe(g)} for c, g in cell] for cell in row] for row in table],
            'last_unit': {'g1': describe(g1), 'g2': describe(g2), 'relative': describe(R), 'order': 4,
                          'inverse_polynomial': ['-1/15', '2/15', '-4/15', '8/15']},
            'sector_variants': sectors, 'negative_controls': controls,
            'scope': 'Uniform finite words over complex scalars independent of tensor width; any fresh-owner-only feed preserving the original x chronology. No fixed-width or global small-unit impossibility.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = verify()
    target = HERE / 'RESULT.json'
    if args.write:
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        require(json.loads(target.read_text()) == result, 'frozen receipt')
    print(result['status'])


if __name__ == '__main__':
    main()
