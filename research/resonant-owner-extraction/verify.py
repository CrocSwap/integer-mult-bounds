#!/usr/bin/env python3
"""Exact uniform group-word certificate for a resonant partial target channel."""
import argparse
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ARITHMETIC = 'research/staggered-single-owner-obstruction/retained/arithmetic.py'
ARITHMETIC_SHA = '0d277854396e4ceda1e0f26916bd576b6decb474c0692b6671ebf2595283ddb9'


def require(value, message):
    if not value:
        raise ValueError(message)


def verify():
    path = HERE.parent.parent / ARITHMETIC
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == ARITHMETIC_SHA, 'arithmetic source hash')
    v = types.ModuleType('arithmetic')
    exec(compile(data, str(path), 'exec'), v.__dict__)
    v.mm = lru_cache(maxsize=8192)(v.mm)
    I = v.ident()
    C = [v.c_letter(j) for j in range(3)]
    S = v.s_letter(7)
    U = v.monomial([0, 5, 2, 7, 4, 1, 6, 3])
    V = v.monomial([0, 2, 1, 3, 4, 6, 5, 7])
    T = v.monomial([0, 4, 2, 6, 1, 5, 3, 7])
    V21 = v.monomial([0, 1, 4, 5, 2, 3, 6, 7])
    P, Q, Q2 = v.word(S, U, S), v.word(S, V, S), v.word(S, V21, S)
    W, N = v.pauli(0, 5), v.word(v.pauli(0, 2), V)
    L, J, K = v.word(N, T), v.word(N, C[2]), v.word(*C)
    a, b, central = v.pauli(1, 3), v.pauli(4, 4), v.scale(v.I, I)

    def plus(*rows):
        out = {}
        for row in rows:
            for key, coefficient in row.items():
                out[key] = out.get(key, F(0)) + coefficient
        return {key: value for key, value in out.items() if value}

    def scaled(row, coefficient):
        return {key: value * coefficient for key, value in row.items() if value * coefficient}

    def product(left, right):
        out = {}
        for g, c in left.items():
            for h, d in right.items():
                word = v.mm(g, h)
                out[word] = out.get(word, F(0)) + c * d
        return {word: value for word, value in out.items() if value}

    def apply(operator, row):
        out = {}
        for g, c in operator.items():
            for (owner, h), d in row.items():
                key = owner, v.mm(g, h)
                out[key] = out.get(key, F(0)) + c * d
        return {key: value for key, value in out.items() if value}

    def left(g, row, c=1):
        return apply({g: F(c)}, row)

    def monomial(matrix):
        return (all(sum(c != v.ZERO for c in row) == 1 for row in matrix)
                and all(sum(matrix[i][j] != v.ZERO for i in range(8)) == 1 for j in range(8))
                and all(c == v.ZERO or c in v.I_POWERS for row in matrix for c in row))

    def describe(matrix):
        require(monomial(matrix), 'fourth-root monomial')
        places = [next(i for i in range(8) if matrix[i][j] != v.ZERO) for j in range(8)]
        phases = [v.I_POWERS.index(matrix[places[j]][j]) for j in range(8)]
        shift = places[0]
        columns = [places[1 << j] ^ shift for j in range(3)]
        for x in range(8):
            image = shift
            for j in range(3):
                if x & (1 << j):
                    image ^= columns[j]
            require(places[x] == image, 'actual free alphabet: affine permutation')
        polynomial = phases[:]
        for bit in range(3):
            for mask in range(8):
                if mask & (1 << bit):
                    polynomial[mask] = (polynomial[mask] - polynomial[mask ^ (1 << bit)]) % 4
        require(polynomial[7] == 0 and all(polynomial[m] % 2 == 0 for m in (3, 5, 6)),
                'actual free alphabet: linear plus even quadratic phase')
        return {'permutation': places, 'phase_i': phases,
                'affine_shift': shift, 'affine_columns': columns,
                'phase_polynomial_mod4': polynomial}

    def serialize(operator):
        records = [{'coefficient': str(c), **describe(g)} for g, c in operator.items()]
        return sorted(records, key=lambda rec: (rec['permutation'], rec['phase_i']))

    def project(row, representative):
        out = {}
        for (owner, word), c in row.items():
            quotient = v.mm(word, v.adjoint(representative))
            if owner == 0 and monomial(quotient):
                out[quotient] = out.get(quotient, F(0)) + c
        return {word: c for word, c in out.items() if c}

    def program(feed, coefficient=1):
        x, y = {(0, I): F(1)}, {(1, I): F(1)}
        u = left(C[0], x)
        vv = left(C[0], plus(left(P, u), left(Q, u, coefficient)))
        r = left(v.word(v.adjoint(L), J), plus(left(W, vv), left(T, feed)))
        t = left(C[0], plus(left(P, r), left(Q, r, 2)))
        z = left(J, plus(left(W, t), left(Q2, r), left(P, vv)))
        return {'x': x, 'y': y, 'u': u, 'v': vv, 'r': r, 't': t, 'z': z}

    identity = {I: F(1)}
    B = scaled(product(plus(identity, {a: F(-1)}), plus(identity, {b: F(-1)})), F(1, 4))
    complement = plus(identity, scaled(B, -1))
    require(v.mm(a, a) == I and v.mm(b, b) == I and v.mm(a, b) == v.mm(b, a), 'commuting involutions')
    require(product(B, B) == B and plus(B, complement) == identity and product(B, complement) == {},
            'source projector and whole complement')
    output_projector = identity
    for factor in (plus(identity, {v.mm(central, central): F(1)}),
                   plus(identity, {v.mm(central, v.pauli(1, 0)): F(1)}),
                   *[plus(identity, {v.pauli(0, 1 << j): F(1)}) for j in range(3)]):
        output_projector = product(output_projector, factor)
    output_projector = scaled(output_projector, F(1, 32))
    require(len(output_projector) == 32 and product(output_projector, output_projector) == output_projector,
            'uniform output projector')
    rows = program(apply(B, {(1, I): F(1)}))
    A0 = v.word(v.adjoint(L), J, W)
    R4 = v.word(C[0], P, C[0])
    R7 = v.word(C[0], Q, A0, C[0], P, C[0])
    pivot = project(rows['z'], R7)
    require(len(pivot) == 2 and list(pivot.values()) == [1, 1], 'resonant pencil')
    g1, g2 = pivot
    R = v.mm(v.adjoint(g1), g2)
    powers = [I]
    for _ in range(4):
        powers.append(v.mm(powers[-1], R))
    require(powers[4] == I and len(set(powers[:4])) == 4, 'exact order four')
    E = {v.mm(powers[j], v.adjoint(g1)): F((-1) ** j) for j in range(4)}
    require(product(E, pivot) == {}, 'left annihilator in actual word algebra')
    decoder = {name: {} for name in rows}
    decoder['z'] = E
    row = apply(E, rows['z'])
    eliminations = []
    for name, representative in [('r', C[2]), ('v', R4), ('u', C[0]), ('x', I)]:
        coefficient = project(row, representative)
        old_pivot = project(rows[name], representative)
        require(len(old_pivot) == 1, 'single free pivot')
        pg, pc = next(iter(old_pivot.items()))
        correction = {v.mm(g, v.adjoint(pg)): -c / pc for g, c in coefficient.items()}
        decoder[name] = plus(decoder[name], correction)
        row = plus(row, apply(correction, rows[name]))
        require(project(row, representative) == {}, 'eliminated residual')
        eliminations.append({'register': name, 'terms': len(correction)})
    require(row == plus(*(apply(decoder[name], rows[name]) for name in rows)), 'literal retained decoder')
    final_decoder = {name: product(output_projector, op) for name, op in decoder.items()}
    result = plus(*(apply(final_decoder[name], rows[name]) for name in rows))
    require(result == apply(output_projector, row), 'projected literal decoder')
    require(result and all(owner == 0 for owner, _ in result), 'all-width y cancellation')
    target = project(result, K)
    require(len(target) == len(result), 'all x words in target coset')
    require(result == apply(target, {(0, K): F(1)}), 'exact pure target identity')
    # This also certifies that every actual monomial is in the engine free alphabet.
    decoder_records = {name: serialize(op) for name, op in final_decoder.items()}
    target_records = serialize(target)
    source_records, output_records = serialize(B), serialize(output_projector)

    def tensor_monomial_sum(operator, width):
        n = 8 ** width
        out = [[v.ZERO for _ in range(n)] for _ in range(n)]
        for g, coefficient in operator.items():
            d = describe(g)
            for col in range(n):
                rest, dest, phase, power = col, 0, 0, 1
                for _ in range(width):
                    digit, rest = rest % 8, rest // 8
                    dest += power * d['permutation'][digit]
                    power *= 8
                    phase += d['phase_i'][digit]
                out[dest][col] = v.add(out[dest][col], v.mul(v.q(coefficient), v.I_POWERS[phase % 4]))
        return out

    def gaussian_rank(matrix):
        rows = [list(row) for row in matrix]
        rank = 0
        def inverse(q):
            norm = q[0] ** 2 + q[1] ** 2
            return (q[0] / norm, -q[1] / norm)
        for col in range(len(rows[0])):
            pivot = next((r for r in range(rank, len(rows)) if rows[r][col] != v.ZERO), None)
            if pivot is None:
                continue
            rows[pivot], rows[rank] = rows[rank], rows[pivot]
            inv = inverse(rows[rank][col])
            rows[rank] = [v.mul(inv, q) for q in rows[rank]]
            for r in range(rank + 1, len(rows)):
                scale = rows[r][col]
                if scale != v.ZERO:
                    rows[r] = [v.add(x, v.mul((-scale[0], -scale[1]), y)) for x, y in zip(rows[r], rows[rank])]
            rank += 1
        return rank

    widths = []
    for width in (1, 2):
        concrete = tensor_monomial_sum(target, width)
        nonzero = [(r, c, q) for r, values in enumerate(concrete) for c, q in enumerate(values) if q != v.ZERO]
        rank = gaussian_rank(concrete)
        expected_rank = 0 if width == 1 else 1
        require(rank == expected_rank, 'exact small-width channel rank: width=' + str(width) + ', actual=' + str(rank))
        widths.append({'width': width, 'target_coefficient_rank': rank, 'nonzero_entries': len(nonzero),
                       'first_nonzero': [nonzero[0][0], nonzero[0][1], list(map(str, nonzero[0][2]))] if nonzero else None,
                       'source_projector_rank': gaussian_rank(tensor_monomial_sum(B, width)),
                       'output_projector_rank': gaussian_rank(tensor_monomial_sum(output_projector, width))})
    # Frobenius inner products tensorize word by word; collect exact trace powers.
    norm_polynomial = {}
    units = ((1, 0), (0, 1), (-1, 0), (0, -1))
    for first in target_records:
        for second in target_records:
            real = imag = 0
            for j in range(8):
                if first['permutation'][j] == second['permutation'][j]:
                    unit = units[(second['phase_i'][j] - first['phase_i'][j]) % 4]
                    real += unit[0]
                    imag += unit[1]
            key = real, imag
            norm_polynomial[key] = norm_polynomial.get(key, F(0)) + F(first['coefficient']) * F(second['coefficient'])
    norm_polynomial = {key: value for key, value in norm_polynomial.items() if value and key != (0, 0)}
    require(norm_polynomial == {(8, 0): F(1), (-8, 0): F(1), (2, 0): F(-20),
                                (-2, 0): F(-20), (1, 0): F(32), (-1, 0): F(32)},
            'all-width Hilbert-Schmidt norm polynomial')
    controls = []
    def rejects(name, condition):
        require(not condition, 'negative control incorrectly accepted: ' + name)
        controls.append(name)
    rejects('omit_output_projector', all(owner == 0 for owner, _ in row))
    wrong = program(apply(B, {(1, I): F(1)}), coefficient=2)
    wrong_result = plus(*(apply(final_decoder[name], wrong[name]) for name in wrong))
    rejects('restore_original_coefficient_two', wrong_result == result)
    unfed = program({(1, I): F(1)})
    unfed_result = plus(*(apply(final_decoder[name], unfed[name]) for name in unfed))
    rejects('omit_source_projector', all(owner == 0 for owner, _ in unfed_result))
    rejects('discard_source_complement', B == identity)
    rejects('identify_central_minus_I_with_I', v.mm(central, central) == I)
    rejects('infer_width_one_identity_at_width_two', widths[1]['target_coefficient_rank'] == widths[0]['target_coefficient_rank'])
    return {'status': 'PASS_RESONANT_OWNER_EXTRACTION', 'source_arithmetic_sha256': ARITHMETIC_SHA,
            'source_projector': source_records, 'output_projector': output_records,
            'annihilator': serialize(E), 'relative_order': 4, 'eliminations': eliminations,
            'decoder_before_output_projector': {name: serialize(op) for name, op in decoder.items()},
            'final_decoder_term_counts': {name: len(records) for name, records in decoder_records.items()},
            'target_coefficient_sha256': hashlib.sha256(json.dumps(target_records, sort_keys=True).encode()).hexdigest(),
            'hilbert_schmidt_trace_powers': [{'base': list(key), 'coefficient': str(value)} for key, value in sorted(norm_polynomial.items())],
            'formal_target_terms': len(target), 'formal_y_terms': 0, 'width_checks': widths,
            'negative_controls': controls,
            'scope': 'Exact all-positive-width pure partial Kx channel; nonzero at every even width, rank one at width two, and zero at odd widths. No full Kx, Ky, restoration budget, recursive saving or multiplication theorem.'}


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
