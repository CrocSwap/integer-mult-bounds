#!/usr/bin/env python3
"""Exact polynomial and literal-matrix checks; standard library only.

apoursh, with substantial OpenAI Codex and separate agent assistance.
Apache-2.0. The written proof supplies the infinite quantifiers.
"""
from fractions import Fraction as F
from hashlib import sha1, sha256
from itertools import product
import json
from math import factorial
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent
ZERO, ONE, I = (0, 0), (1, 0), (0, 1)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rejected(action, message):
    try:
        action()
    except ValueError:
        return 1
    raise ValueError('Control accepted: ' + message)


def qa(a, b):
    return a[0] + b[0], a[1] + b[1]


def qn(a):
    return -a[0], -a[1]


def qc(a):
    return a[0], -a[1]


def qm(a, b):
    if a == ZERO or b == ZERO:
        return ZERO
    if b == ONE:
        return a
    if a == ONE:
        return b
    if b[1] == 0:
        return a[0] * b[0], a[1] * b[0]
    if a[1] == 0:
        return a[0] * b[0], a[0] * b[1]
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def qd(a, b):
    norm = b[0] * b[0] + b[1] * b[1]
    require(norm != 0, 'division by zero')
    return qm(a, (F(b[0], norm), -F(b[1], norm)))


def qp(a, k):
    out = ONE
    for _ in range(k):
        out = qm(out, a)
    return out


def mi(d):
    return {(j, j): ONE for j in range(d)}


def ms(a, z):
    return {key: qm(value, z) for key, value in a.items() if qm(value, z) != ZERO}


def star(a):
    return {(j, i): qc(value) for (i, j), value in a.items()}


def mm(a, b):
    rows = {}
    for (k, j), value in b.items():
        rows.setdefault(k, []).append((j, value))
    out = {}
    for (i, k), x in a.items():
        for j, y in rows.get(k, ()):
            key = i, j
            out[key] = qa(out.get(key, ZERO), qm(x, y))
    return {key: value for key, value in out.items() if value != ZERO}


def tr_product(a, b):
    out = ZERO
    for (i, j), value in a.items():
        out = qa(out, qm(value, b.get((j, i), ZERO)))
    return out


def determinant(a, d):
    rows = [[a.get((i, j), ZERO) for j in range(d)] for i in range(d)]
    out = ONE
    for k in range(d):
        pivot = next((i for i in range(k, d) if rows[i][k] != ZERO), None)
        if pivot is None:
            return ZERO
        if pivot != k:
            rows[k], rows[pivot] = rows[pivot], rows[k]
            out = qn(out)
        diagonal = rows[k][k]
        out = qm(out, diagonal)
        for i in range(k + 1, d):
            if rows[i][k] == ZERO:
                continue
            factor = qd(rows[i][k], diagonal)
            for j in range(k + 1, d):
                rows[i][j] = qa(rows[i][j], qn(qm(factor, rows[k][j])))
            rows[i][k] = ZERO
    return out


def projective_key(a):
    keys = sorted(a)
    lead = a[keys[0]]
    return tuple((key, qd(a[key], lead)) for key in keys)


H = {(0, 0): (F(1, 2), F(1, 2)), (0, 1): (F(1, 2), F(1, 2)),
     (1, 0): (F(1, 2), F(1, 2)), (1, 1): (-F(1, 2), -F(1, 2))}
S = {(0, 0): ONE, (1, 1): I}
PX = {(0, 1): ONE, (1, 0): ONE}
PZ = {(0, 0): ONE, (1, 1): (-1, 0)}


def one_qubit_group():
    result = [mi(2)]
    seen = {projective_key(result[0])}
    for u in result:
        for g in (H, S):
            v = mm(g, u)
            key = projective_key(v)
            if key not in seen:
                seen.add(key)
                result.append(v)
                require(len(result) <= 24, 'one-qubit closure too large')
    require(len(result) == 24, 'one-qubit closure incomplete')
    for u in result:
        require(mm(u, star(u)) == mi(2), 'one-qubit unitarity')
    return result


def pc(z):
    return {} if z == ZERO else {(0, 0, 0, 0): z}


def pv(j):
    exponents = [0] * 4
    exponents[j] = 1
    return {tuple(exponents): ONE}


def pa(a, b):
    out = dict(a)
    for exponent, value in b.items():
        out[exponent] = qa(out.get(exponent, ZERO), value)
    return {key: value for key, value in out.items() if value != ZERO}


def ps(a, z):
    return {key: qm(value, z) for key, value in a.items() if qm(value, z) != ZERO}


def pm(a, b):
    out = {}
    for alpha, x in a.items():
        for beta, y in b.items():
            exponent = tuple(u + v for u, v in zip(alpha, beta))
            out[exponent] = qa(out.get(exponent, ZERO), qm(x, y))
    return {key: value for key, value in out.items() if value != ZERO}


def pmat(a, b):
    return [[pa(pm(a[i][0], b[0][j]), pm(a[i][1], b[1][j]))
             for j in range(2)] for i in range(2)]


def pconstant_matrix(a):
    return [[pc(a.get((i, j), ZERO)) for j in range(2)] for i in range(2)]


def polynomial_for(u):
    a, b, c, d = [pv(j) for j in range(4)]
    x = [[a, b], [c, d]]
    adj = [[d, ps(b, (-1, 0))], [ps(c, (-1, 0)), a]]
    delta = pa(pm(a, d), ps(pm(b, c), (-1, 0)))
    factors = []
    for p in (PX, PZ):
        q = mm(mm(u, p), star(u))
        m = pmat(pmat(pmat(pconstant_matrix(q), x), pconstant_matrix(p)), adj)
        t = ps(pa(m[0][0], m[1][1]), (F(1, 2), 0))
        factors.append(ps(pa(pm(t, t), pm(t, delta)), (F(1, 2), 0)))
    return pm(*factors), factors


def homogeneous(poly, degree):
    require(bool(poly) and all(sum(alpha) == degree for alpha in poly),
            'wrong homogeneous degree')


def dyadic_coefficients(poly):
    for coefficient in poly.values():
        for value in coefficient:
            denominator = value.denominator
            require(denominator > 0 and denominator & (denominator - 1) == 0,
                    'odd coefficient denominator')


def tensor_index(alpha):
    row = col = 0
    f = sum(alpha)
    for coordinate, multiplicity in enumerate(alpha):
        for _ in range(multiplicity):
            row = 2 * row + coordinate // 2
            col = 2 * col + coordinate % 2
    return row * (2 ** f) + col


def tensor_coordinate(u, f, index):
    row, col = divmod(index, 2 ** f)
    out = ONE
    for bit in range(f - 1, -1, -1):
        out = qm(out, u.get(((row >> bit) & 1, (col >> bit) & 1), ZERO))
    return out


def kronecker(a, b, bd):
    return {(i * bd + k, j * bd + l): qm(x, y)
            for (i, j), x in a.items() for (k, l), y in b.items()
            if qm(x, y) != ZERO}


def row_evaluation(poly, u, f, normalization):
    require(f % 2 == 0, 'one-qubit normalized check requires even width')
    out = ZERO
    for alpha, coefficient in poly.items():
        # Observe the literal normalized tensor coordinate, not a monomial evaluator.
        observation = qm(tensor_coordinate(u, f, tensor_index(alpha)), (F(1, 2 ** (f // 2)), 0))
        out = qa(out, qm(qm(coefficient, (normalization, 0)), observation))
    return out


def embedded(g, n, qubit):
    out = {}
    for col in range(2 ** n):
        source_bit = (col >> qubit) & 1
        for dest_bit in (0, 1):
            value = g.get((dest_bit, source_bit), ZERO)
            if value != ZERO:
                row = (col & ~(1 << qubit)) | (dest_bit << qubit)
                out[row, col] = value
    return out


def cnot(n, control, target):
    return {(col ^ ((1 << target) if (col >> control) & 1 else 0), col): ONE
            for col in range(2 ** n)}


def pauli(n, x, z):
    phase = qp(I, (x & z).bit_count() % 4)
    return {(col ^ x, col): qm(phase, ((-1) ** ((z & col).bit_count() % 2), 0))
            for col in range(2 ** n)}


def four_qubit_samples():
    gates = {'H' + str(q): embedded(H, 4, q) for q in range(4)}
    gates.update({'S' + str(q): embedded(S, 4, q) for q in range(4)})
    gates.update({'C01': cnot(4, 0, 1), 'C12': cnot(4, 1, 2),
                  'C23': cnot(4, 2, 3)})
    words = [(), ('H0',), ('S0',), ('H1',), ('S1',), ('H2',), ('S2',),
             ('H3',), ('S3',), ('C01',), ('C12',), ('C23',),
             ('H0', 'C01', 'S1'), ('S2', 'H2', 'C23', 'H3'),
             ('H0', 'H1', 'H2', 'H3'), ('C01', 'S1', 'C12', 'H2', 'C23')]
    samples = []
    for word in words:
        u = mi(16)
        for name in word:
            u = mm(gates[name], u)
        samples.append(u)
    require(len({projective_key(u) for u in samples}) == len(samples),
            'duplicate four-qubit sample')
    return samples


def authenticate(item, data):
    require(len(data) == item['bytes'], 'source length changed')
    require(sha256(data).hexdigest() == item['sha256'], 'source SHA256 changed')
    git_object = b'blob ' + str(len(data)).encode('ascii') + b'\0' + data
    require(sha1(git_object).hexdigest() == item['git_blob'], 'source Git blob changed')


def main():
    started = time.monotonic()
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())['files']
    require(len(pins) == 3, 'source coverage changed')
    source_controls = 0
    for item in pins:
        data = (ROOT / item['path']).read_bytes()
        authenticate(item, data)
        mutated = bytes([data[0] ^ 1]) + data[1:]
        source_controls += rejected(lambda: authenticate(item, mutated), 'source byte')

    group = one_qubit_group()
    polynomials, factor_lists = zip(*(polynomial_for(u) for u in group))
    for poly in polynomials:
        homogeneous(poly, 8)
        dyadic_coefficients(poly)
        require(len({tensor_index(alpha) for alpha in poly}) == len(poly),
                'tensor lift merged distinct monomials')
    coefficients = sum(map(len, polynomials))
    for a, poly in enumerate(polynomials):
        for b, u in enumerate(group):
            require(row_evaluation(poly, u, 8, 16) == (ONE if a == b else ZERO),
                    'one-qubit normalized left inverse failed')

    # Literal Kronecker construction independently fixes the flattening convention.
    calibration = mm(S, H)
    literal = mi(1)
    for _ in range(4):
        literal = kronecker(literal, calibration, 2)
    for index in range(256):
        require(literal.get(divmod(index, 16), ZERO) == tensor_coordinate(calibration, 4, index),
                'literal Kronecker index mismatch')

    samples = four_qubit_samples()
    generators = [embedded(p, 4, q) for q in range(4) for p in (PX, PZ)]
    signed_paulis = set()
    for x, z in product(range(16), repeat=2):
        p = pauli(4, x, z)
        signed_paulis.add(tuple(sorted(p.items())))
        signed_paulis.add(tuple(sorted(ms(p, (-1, 0)).items())))
    images, determinants = [], []
    for u in samples:
        require(mm(u, star(u)) == mi(16), 'four-qubit unitarity')
        delta = determinant(u, 16)
        require(delta == ONE and qp(delta, 4) == ONE, 'four-qubit determinant')
        determinants.append(delta)
        qlist = [mm(mm(u, p), star(u)) for p in generators]
        for q in qlist:
            require(tuple(sorted(q.items())) in signed_paulis, 'not a signed Pauli image')
        images.append(qlist)
    pairings = 0
    for a, qa_list in enumerate(images):
        for b, qb_list in enumerate(images):
            out = ONE
            delta = determinants[b]
            for qa_matrix, qb_matrix in zip(qa_list, qb_list):
                u = qm(tr_product(qa_matrix, qb_matrix), (F(1, 16), 0))
                require(u in ((-1, 0), ZERO, ONE), 'non-discrete Pauli pairing')
                t = qm(delta, u)
                out = qm(out, qm(qa(qm(t, t), qm(t, delta)), (F(1, 2), 0)))
                pairings += 1
            require(out == (ONE if a == b else ZERO), 'four-qubit interpolation failed')

    # Faults target mathematical hypotheses, coefficient lift and normalization.
    controls = 0
    controls += rejected(lambda: homogeneous(polynomials[0], 7), 'wrong width')
    controls += rejected(lambda: require(row_evaluation(polynomials[0], group[0], 8, 1) == ONE,
                                        'wrong normalized-map factor'), 'wrong normalization')
    # Omitting the Z generator cannot distinguish I from X.
    controls += rejected(lambda: require(row_evaluation(factor_lists[0][0], PX, 4, 4) == ZERO,
                                        'missing generator admits X'), 'missing generator')
    # Dividing by orbit size but keeping only one ordered word is not this lift.
    incorrectly_averaged = {}
    for alpha, coefficient in polynomials[0].items():
        orbit_size = factorial(8)
        for exponent in alpha:
            orbit_size //= factorial(exponent)
        incorrectly_averaged[alpha] = qm(coefficient, (F(1, orbit_size), 0))
    controls += rejected(lambda: require(row_evaluation(incorrectly_averaged, group[0], 8, 16) == ONE,
                                        'unearned multinomial division'), 'factorial normalization')
    # Squared pairings erase the signs, admitting nontrivial Paulis.
    unsigned = ONE
    for p in (PX, PZ):
        u = qm(tr_product(p, mm(mm(PZ, p), star(PZ))), (F(1, 2), 0))
        unsigned = qm(unsigned, qm(u, u))
    controls += rejected(lambda: require(unsigned == ZERO, 'unsigned image admits Z'),
                         'unsigned image')
    # At the S target, determinant=i and each exact matching t=i.
    bad_factor = qm(qa(qm(I, I), I), (F(1, 2), 0))
    controls += rejected(lambda: require(qm(bad_factor, bad_factor) == ONE,
                                        'dropped determinant phase'), 'dropped determinant')
    require(determinant(S, 2) == I, 'phase-control source')
    require(qm((-1, 0), (-1, 0)) == ONE, 'two matching phase factors must cancel')
    result = {
        'status': 'PASS_CLIFFORD_DYADIC_LEFT_INVERSE',
        'source_files': len(pins), 'source_mutations_rejected': source_controls,
        'one_qubit_cosets': len(group), 'polynomial_degree': 8,
        'polynomial_coefficients': coefficients, 'left_inverse_entries': len(group) ** 2,
        'literal_fourfold_tensor_entries': 256,
        'four_qubit_samples': len(samples), 'four_qubit_generator_images': len(samples) * 8,
        'four_qubit_pairings': pairings, 'four_qubit_interpolation_entries': len(samples) ** 2,
        'fault_controls_rejected': controls,
        'scope': 'Finite implementation checks; PROOF.md establishes all n and all sufficient widths. '
                 'The full four-qubit tensor matrix and decoder are not materialized.',
        'seconds': round(time.monotonic() - started, 3),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
