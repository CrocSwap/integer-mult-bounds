#!/usr/bin/env python3
"""Exact certificate replay, dense lattice/transform oracle and rejection controls.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is a finite certificate check plus the scoped proof in PROOF.md, not a
formal proof-kernel verification or a multiplier/supplier admission.
"""
import copy
import hashlib
import json
import platform
from fractions import Fraction
from pathlib import Path

import kernel as production

HERE = Path(__file__).parent
N = 16
ROWS = (0x21, 0x906, 0x6FDE, 0x103, 0xA8EC, 0x29E)
SIGN = tuple((-1) ** j.bit_count() for j in range(N))
RE = tuple((1, 0, -1, 0)[j.bit_count() % 4] for j in range(N))
IM = tuple((0, -1, 0, 1)[j.bit_count() % 4] for j in range(N))
W = tuple(tuple((-1) ** (r & s).bit_count() for s in range(N)) for r in range(N))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def dense(v):
    return tuple(dot(row, v) for row in W)


def b(v):
    numerator = tuple(s * x for s, x in zip(SIGN, dense(v)))
    need(all(x % 4 == 0 for x in numerator), 'nonintegral B image')
    return tuple(x // 4 for x in numerator)


def k(v):
    return tuple(SIGN[j] * v[j ^ 15] for j in range(N))


def minus(v):
    return tuple(-x for x in v)


def inverse_matrix(matrix):
    n = len(matrix)
    a = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(n)]
         for i, row in enumerate(matrix)]
    det = Fraction(1)
    for j in range(n):
        p = next((i for i in range(j, n) if a[i][j]), None)
        need(p is not None, 'singular period matrix')
        if p != j:
            a[p], a[j] = a[j], a[p]
            det = -det
        pivot = a[j][j]
        det *= pivot
        a[j] = [x / pivot for x in a[j]]
        for i in range(n):
            if i != j:
                scale = a[i][j]
                a[i] = [x - scale * y for x, y in zip(a[i], a[j])]
    return tuple(tuple(row[n:]) for row in a), det


def rref(rows, width=16):
    rows = list(rows)
    pivots = []
    rank = 0
    for j in range(width):
        p = next((i for i in range(rank, len(rows)) if rows[i] >> j & 1), None)
        if p is None:
            continue
        rows[p], rows[rank] = rows[rank], rows[p]
        for i in range(len(rows)):
            if i != rank and rows[i] >> j & 1:
                rows[i] ^= rows[rank]
        pivots.append(j)
        rank += 1
    return rows[:rank], pivots


def period_oracle(rows):
    # Construct the physical lattice basis, then invert its dense rational
    # matrix. Membership/classification below does not use production.class_id.
    high = [j for j in range(N) if j.bit_count() >= 2]
    low = [0, 1, 2, 4, 8]
    l_cols = []
    for j in low:
        v = [0] * N
        if j == 0:
            v[0] = 4
        else:
            v[0], v[j] = -2, 2
        l_cols.append(tuple(v))
    for j in high:
        v = [0] * N
        v[j], v[0] = 1, j.bit_count() - 1
        for bit in range(4):
            if j >> bit & 1:
                v[1 << bit] = -1
        l_cols.append(tuple(v))
    reduced, pivots = rref(rows)
    need(len(pivots) == 6, 'period rank is not six')
    need(len(rref([r & 31 for r in rows], 5)[1]) == 5, 'odd-period restriction fails')
    c_cols = []
    for j in range(N):
        v = [0] * N
        if j in pivots:
            v[j] = 2
        else:
            v[j] = 1
            for row, pivot in zip(reduced, pivots):
                v[pivot] = row >> j & 1
        c_cols.append(v)
    gamma_cols = [tuple(sum(l_cols[j][i] * v[j] for j in range(N)) for i in range(N))
                  for v in c_cols]
    gamma = tuple(tuple(gamma_cols[j][i] for j in range(N)) for i in range(N))
    inv, det = inverse_matrix(gamma)
    need(abs(det) == 4096, 'wrong period index')
    need(all((8 * x).denominator == 1 for row in inv for x in row), '8Z not periodic')
    inv8 = tuple(tuple(int(8 * x) for x in row) for row in inv)

    def signature(v):
        return tuple(dot(row, v) % 8 for row in inv8)

    for col in gamma_cols:
        need(not any(signature(b(col))), 'period is not B invariant')
    for col in l_cols:
        need(b(b(col)) == k(col), 'B square mismatch')
    return signature, tuple(gamma_cols), abs(int(det))


def local_check(table, reps):
    for s, z in enumerate(reps):
        c = table[s]
        need(sum(x*x for x in c) <= 64, 'radius violation')
        need(dot(RE, c) == dot(IM, c) == 0, 'weighted-sum violation')
        need(all((a*w+v) % 4 == 0 for a, w, v in zip(SIGN, dense(z), c)),
             'integrality violation')


def native_numerator(real, imag):
    # Direct coefficient formula 4U_rs=-d_r*d_s*(-1)^(r dot s).
    rr, ii = [], []
    phases = ((1, 0), (0, -1), (-1, 0), (0, 1))
    for r in range(N):
        ar = ai = 0
        for s in range(N):
            pr, pi = phases[(r.bit_count() + s.bit_count()) % 4]
            sign = -W[r][s]
            ar += sign * (pr * real[s] - pi * imag[s])
            ai += sign * (pi * real[s] + pr * imag[s])
        rr.append(ar)
        ii.append(ai)
    return tuple(rr), tuple(ii)


def error_energy(real, imag, output):
    ideal = native_numerator(real, imag)
    return sum((4*x-y)**2 for part, target in zip(output, ideal)
               for x, y in zip(part, target))


def reject(action, label):
    try:
        action()
    except (ValueError, TypeError, KeyError, IndexError):
        return label
    raise ValueError('negative control accepted: ' + label)


def main():
    raw = (HERE / 'CERTIFICATE.json').read_bytes()
    certificate = json.loads(raw)
    table = production.expand_certificate(certificate)
    reps = production.REPS
    signature, gamma, index = period_oracle(ROWS)
    classes = {signature(z): s for s, z in enumerate(reps)}
    need(len(classes) == 4096, 'representatives do not exhaust quotient')
    need(all(production.class_id(z) == s for s, z in enumerate(reps)), 'classifier mismatch')

    def cid(z):
        return classes[signature(z)]

    def t(z, candidate=table):
        numerator = tuple(a*w+c for a, w, c in zip(SIGN, dense(z), candidate[cid(z)]))
        need(all(x % 4 == 0 for x in numerator), 'nonintegral T value')
        return tuple(x // 4 for x in numerator)

    def relations(candidate, square=True):
        for s, z in enumerate(reps):
            c = candidate[s]
            need(candidate[cid(minus(z))] == minus(c), 'oddness violation')
            need(candidate[cid(k(z))] == k(c), 'K covariance violation')
            if square:
                y = t(z, candidate)
                need(candidate[cid(y)] == minus(b(c)), 'square correction violation')
                need(t(y, candidate) == k(z), 'exact square violation')

    local_check(table, reps)
    relations(table)
    need(len({cid(t(z)) for z in reps}) == 4096, 'quotient is not bijective')
    need(all(production.t_map(z, table) == t(z) for z in reps), 'fast/dense disagreement')
    energy = max(sum(x*x for x in c) for c in table)
    coordinate = max(abs(x) for c in table for x in c)
    need(energy == 64 and coordinate == 5, 'wrong sharp maxima')
    need(all(c == (0,)*16 for c in table[:64]), 'map does not fix integral Walsh classes')

    # Independent complex fixtures cover every real source class in each lane;
    # the proof, not a 4096^2 enumeration, establishes all complex pairs.
    complex_count = 0
    for s, real in enumerate(reps):
        imag = reps[(1597*s + 43) % 4096]
        out = production.forward(real, imag, table)
        twice = production.forward(*out, table)
        need(twice == (tuple(real[j^15] for j in range(N)),
                       tuple(imag[j^15] for j in range(N))), 'native square violation')
        need(production.inverse(*out, table) == (real, imag), 'inverse-after-forward violation')
        back = production.inverse(real, imag, table)
        need(production.forward(*back, table) == (real, imag), 'forward-after-inverse violation')
        phase = production.forward(minus(imag), real, table)
        need(phase == (minus(out[1]), out[0]), 'global Gaussian phase violation')
        need(tuple(map(sum, out)) == (sum(real), sum(imag)), 'native sum violation')
        need(error_energy(real, imag, out) <= 128, 'native error violation')
        complex_count += 1

    # Translation and signed large-word fixtures exercise low-bit extraction,
    # exact affine continuation and both executable directions.
    for trial, bits in enumerate((0, 1, 7, 31, 127, 509, 1021, 4090)):
        z = reps[(trial*683+31) % 4096]
        shift = tuple((1 << bits) * gamma[(trial+3) % 16][j] -
                      (2*trial+1)*gamma[trial % 16][j] for j in range(N))
        zz = tuple(x+y for x, y in zip(z, shift))
        need(cid(zz) == production.class_id(zz) == cid(z), 'large-word class mismatch')
        need(t(zz) == tuple(x+y for x, y in zip(t(z), b(shift))), 'affine period violation')
        real, imag = zz, tuple(-x+8*j for j, x in enumerate(zz))
        out = production.forward(real, imag, table)
        need(production.inverse(*out, table) == (real, imag), 'large-word inverse violation')
        need(error_energy(real, imag, out) <= 128, 'large-word error violation')

    sharp = (2,) + (0,)*15
    need(error_energy(sharp, sharp, production.forward(sharp, sharp, table)) == 128,
         'forward sharp witness missing')
    # J preserves the norm, and inverse=JF with ideal inverse=JU.
    inv_sharp = production.inverse(sharp, sharp, table)
    unpermute = tuple(tuple(part[j^15] for j in range(N)) for part in inv_sharp)
    need(error_energy(sharp, sharp, unpermute) == 128, 'inverse sharp witness missing')

    # Composition with the all-n tensor obstruction: this bounded-error,
    # conservative exact-square map attains its nonzero-image floor at n=4.
    zero = (0,)*16
    unit = (1,)+(0,)*15
    w = production.forward(unit, zero, table)
    target = tuple(int(j==3) for j in range(N))
    need(w == (target,zero), 'forced F(e0)=e3 fails')
    for source, destination in ((0,3),(3,15),(15,12),(12,0)):
        z = tuple(int(j==source) for j in range(N))
        expected = tuple(int(j==destination) for j in range(N))
        need(production.t_map(z,table) == expected, 'forced T basis cycle fails')
        need(sum(x*x for x in table[cid(z)]) == 24, 'forced correction energy is not24')

    def rows(array):
        return tuple(tuple(zip(*production.forward(*zip(*row), table))) for row in array)

    def columns(array):
        return tuple(zip(*rows(tuple(zip(*array)))))

    lam = tuple((a,-b) for a,b in zip(RE,IM))
    array = tuple(tuple(lam[i] if j==0 else (0,0) for j in range(N)) for i in range(N))
    row_column = rows(columns(array))
    column_row = columns(rows(array))
    delta = tuple(tuple((x[0]-y[0],x[1]-y[1]) for x,y in zip(r,t))
                  for r,t in zip(row_column,column_row))
    squared_defect = sum(a*a+b*b for row in delta for a,b in row)
    expected_first = tuple((RE[j]+4*int(j==3),IM[j]) for j in range(N))
    need(delta[0] == expected_first and all(v==(0,0) for row in delta[1:] for v in row),
         'tensor witness has wrong exact defect')
    need(squared_defect == 24, 'bounded-error exact-square map misses the sharp floor')
    differing = sum(v!=(0,0) for row in delta for v in row)
    need(differing == 16, 'universal witness difference support')

    controls = []
    controls.append(reject(lambda: need(row_column == column_row, 'rounded fibers do not commute'),
                           'false row-column commutation'))
    bad = copy.deepcopy(certificate)
    bad['cycles'].pop()
    controls.append(reject(lambda: production.expand_certificate(bad), 'missing cycle'))
    bad = copy.deepcopy(certificate)
    bad['cycles'][0][1][0] += 4
    controls.append(reject(lambda: production.expand_certificate(bad), 'weighted-sum corruption'))
    bad = copy.deepcopy(certificate)
    bad['cycles'][0][1][0] += 12
    controls.append(reject(lambda: production.expand_certificate(bad), 'radius corruption'))
    controls.append(reject(lambda: period_oracle((ROWS[0] ^ 32,) + ROWS[1:]),
                           'noninvariant period'))

    # This control remains integral, sharp, weighted-sum preserving, odd and
    # K-equivariant. It fails the additional two-step correction obligation.
    square_control = None
    for s, c in enumerate(table):
        if not any(c) or any(x % 2 for x in c):
            continue
        orbit = {s, cid(minus(reps[s])), cid(k(reps[s])), cid(minus(k(reps[s])))}
        candidate = list(table)
        for u in orbit:
            candidate[u] = minus(candidate[u])
        local_check(candidate, reps)
        relations(candidate, square=False)
        if any(candidate[cid(t(z, candidate))] != minus(b(candidate[u]))
               for u, z in enumerate(reps)):
            square_control = s
            controls.append(reject(lambda: relations(candidate), 'local predicates without exact square'))
            break
    need(square_control is not None, 'no meaningful square rejection control found')
    unit = (1,) + (0,)*15
    zero = (0,)*16
    out = production.forward(unit, zero, table)
    controls.append(reject(lambda: need(production.forward(*out, table) == (unit, zero),
                                        'forward is not the inverse'), 'forward-as-inverse'))
    controls.append(reject(lambda: need(energy < 64, 'radius cannot be smaller'), 'false smaller radius'))
    wrong = production.forward((64,)+(0,)*15, zero, table)
    wrong = (tuple(-x if j == 0 else x for j, x in enumerate(wrong[0])), wrong[1])
    controls.append(reject(lambda: need(error_energy((64,)+(0,)*15, zero, wrong) <= 128,
                                        'wrong native phase'), 'wrong native coordinate phase'))

    receipt = {
        'status': 'PASS_FOUR_AXIS_EXACT_SQUARE_GRID',
        'python': platform.python_version(),
        'period_index': index,
        'real_classes': len(table),
        'cycle_generators': len(certificate['cycles']),
        'complex_fixtures': complex_count,
        'large_word_fixtures': 8,
        'row_column_boundary': {'input': 'lambda e0^T; lambda_j=i^wt(j)', 'differing_coordinates': differing, 'squared_defect': squared_defect, 'F_e0': 'e3', 'sharp_bounded_error_native_square_attainment': True},
        'max_correction_energy': energy,
        'max_abs_correction': coordinate,
        'sharp_complex_error_squared': 8,
        'negative_controls': controls,
        'square_control_class': square_control,
        'certificate_sha256': hashlib.sha256(raw).hexdigest(),
        'expanded_table_sha256': hashlib.sha256(json.dumps(table, separators=(',', ':')).encode()).hexdigest(),
        'source_sha256': {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                          for name in ('kernel.py', 'verify.py')},
        'scope': 'Exact finite certificate and all-integer proof in PROOF.md; no new kappa or all-size supplier admission.'
    }
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
