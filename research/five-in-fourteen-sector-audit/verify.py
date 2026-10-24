#!/usr/bin/env python3
"""Independent actual-port/declared-observation audit of the retained 5-in-14 claim.

Cinna Davis, with OpenAI Codex assistance. Apache-2.0. No new kappa.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/complex-block3-five-in-fourteen/verify_schedule.py'
Z, O, I = (Q(0), Q(0)), (Q(1), Q(0)), (Q(0), Q(1))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def neg(a):
    return -a[0], -a[1]


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def conjugate(a):
    return a[0], -a[1]


def div(a, b):
    d = b[0]*b[0]+b[1]*b[1]
    return ((a[0]*b[0]+a[1]*b[1])/d, (a[1]*b[0]-a[0]*b[1])/d)


def phase(k):
    return (O, I, neg(O), neg(I))[k % 4]


def identity(n=8):
    return [[O if i == j else Z for j in range(n)] for i in range(n)]


def adjoint(a):
    return [[conjugate(a[j][i]) for j in range(len(a))] for i in range(len(a))]


def plus(a, b):
    return [[add(x, y) for x, y in zip(r, s)] for r, s in zip(a, b)]


def scale(c, a):
    return [[mul(c, x) for x in row] for row in a]


def mm(a, b):
    n = len(a); result = [[Z]*n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if a[i][k] != Z:
                for j in range(n):
                    if b[k][j] != Z:
                        result[i][j] = add(result[i][j], mul(a[i][k], b[k][j]))
    return result


def word(*matrices):
    result = identity(len(matrices[0]))
    for matrix in matrices:
        result = mm(result, matrix)
    return result


def mv(a, x):
    result = []
    for row in a:
        value = Z
        for c, d in zip(row, x):
            value = add(value, mul(c, d))
        result.append(value)
    return result


def norm2(x):
    return sum(a*a+b*b for a, b in x)


def monomial(p, phases=None):
    n = len(p); a = [[Z]*n for _ in range(n)]
    phases = [0]*n if phases is None else phases
    for j, i in enumerate(p):
        a[i][j] = phase(phases[j])
    return a


def is_monomial(a):
    return (all(sum(x != Z for x in row) == 1 for row in a) and
            all(sum(a[i][j] != Z for i in range(len(a))) == 1 for j in range(len(a))))


def matrix_rank(a):
    a = [list(row) for row in a]; rank = 0
    for j in range(len(a[0])):
        i = next((i for i in range(rank, len(a)) if a[i][j] != Z), None)
        if i is None:
            continue
        a[rank], a[i] = a[i], a[rank]
        p = a[rank][j]; a[rank] = [div(x, p) for x in a[rank]]
        for k in range(rank+1, len(a)):
            c = a[k][j]
            if c != Z:
                a[k] = [add(x, neg(mul(c, y))) for x, y in zip(a[k], a[rank])]
        rank += 1
    return rank


def independent_operators():
    unit = identity(); cs = []
    for bit in range(3):
        shift = monomial([x ^ (1 << bit) for x in range(8)])
        cs.append(plus(scale((Q(1, 2), Q(1, 2)), unit),
                       scale((Q(1, 2), -Q(1, 2)), shift)))
    C0, C1, C2 = cs
    U = monomial([x ^ (4 if x % 2 else 0) for x in range(8)])
    V = monomial([((x//2) % 2)+2*(x % 2)+4*(x//4) for x in range(8)])
    S = monomial(list(range(8)), [sum((x >> j) & 1 for j in range(3)) for x in range(8)])
    P, BQ = word(S, U, S), word(S, V, S)
    T = monomial([4*(x % 2)+(x & 2)+(x//4) for x in range(8)])
    M = monomial([2, 0, 3, 1, 4, 6, 5, 7], [0, 0, 2, 2, 1, 3, 3, 1])
    pa = monomial([x ^ 1 for x in range(8)], [1+2*((x & 3).bit_count()) for x in range(8)])
    W = monomial(list(range(8)), [2*((x & 5).bit_count()) for x in range(8)])
    Z1 = monomial(list(range(8)), [2*((x >> 1) & 1) for x in range(8)])
    K = word(C0, C1, C2); J = word(Z1, V, C2); D = word(J, W, C0)
    B = word(D, plus(P, scale((Q(2), Q(0)), BQ)), C0)
    out = word(K, pa, adjoint(K)); H = scale((Q(1, 2), Q(0)), adjoint(out))
    need(word(D, P, C0) == word(M, C2), 'first source branch lifts separately')
    need(word(D, BQ, C0) == word(K, pa), 'second source branch lifts separately')
    for a in [*cs, U, V, S, T, M, pa, K, D]:
        need(mm(adjoint(a), a) == unit, 'exact unitary source factor')
    need(C2 == word(T, C0, T), 'swap conjugacy')
    return {'I': unit, 'C0': C0, 'C1': C1, 'C2': C2, 'K': K, 'A': C0,
            'D': D, 'B': B, 'F': word(C0, plus(P, scale((Q(2), Q(0)), BQ)), C0),
            'T': T, 'M': M, 'W': W, 'J': J, 'H': H, 'E': mm(H, D),
            'G': word(adjoint(K), H, D), 'out_pauli': out}


def encode(vector):
    return [[str(a), str(b)] for a, b in vector]


def calculate():
    pins = json.loads((HERE/'SOURCES.json').read_text()); hashes = {}
    for row in pins['files']:
        if row['usage'] == 'input':
            raw = (ROOT/row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'pinned source bytes')
            hashes[row['path']] = row['sha256']
    module = types.ModuleType('authenticated_source_under_audit')
    raw = (ROOT/SOURCE).read_bytes()
    exec(compile(raw, SOURCE, 'exec'), module.__dict__)
    source = module.load_operators(); ops = independent_operators()
    for name, matrix in ops.items():
        need([list(row) for row in source[name]] == matrix, 'independent source operator '+name)
    A, B, D, H, M, T, K, E = [ops[k] for k in ('A', 'B', 'D', 'H', 'M', 'T', 'K', 'E')]
    basis = [[O if i == j else Z for i in range(8)] for j in range(8)]
    x, y = basis[1], basis[2]; cases = []; sector_checks = 0
    for sigma in (1, -1):
        scalar = (Q(sigma), Q(0))
        actual_matrix = plus(mm(H, B), scale(neg(scalar), word(H, M, T, A)))
        defect = plus(actual_matrix, scale(neg(O), K))
        sharp = word(H, M, T, A, plus(T, scale(neg(scalar), identity())))
        need(defect == sharp, 'exact unrestricted defect identity')
        sector = plus(T, scale(neg(scalar), identity()))
        need(matrix_rank(defect) == matrix_rank(sector) == (2 if sigma == 1 else 6),
             'exact local validity domain')
        for point in basis:
            error = mv(defect, point)
            need(norm2(error) == norm2(mv(sector, point))/4, 'sharp defect norm')
            projected = [add(a, mul(scalar, b)) for a, b in zip(point, mv(T, point))]
            need(mv(defect, projected) == [Z]*8, 'true sector positive control')
            sector_checks += 1
        actual = [add(a, b) for a, b in zip(mv(actual_matrix, x), mv(E, y))]
        declared = [add(a, b) for a, b in zip(mv(K, x), mv(E, y))]
        delta = [add(a, neg(b)) for a, b in zip(actual, declared)]
        need(norm2(delta) == Q(1, 2), 'concrete arbitrary-input failure')
        cases.append({'sigma': sigma, 'x_basis_index': 1, 'y_basis_index': 2,
                      'actual': encode(actual), 'declared': encode(declared),
                      'difference': encode(delta), 'squared_error_norm': '1/2'})
    need(not is_monomial(ops['C2']), 'C2 not a free monomial')
    quotient = word(ops['C2'], adjoint(ops['C0']))
    need(not is_monomial(quotient), 'C2 outside free left coset of C0')
    need(sorted({sum(x != Z for x in row) for row in quotient}) == [4], 'quotient row support')
    # A width-one monomial expansion is not a uniform free correction.
    coefficients = [(Q(1, 2), Q(0)), (Q(0), Q(1, 2)), (Q(0), -Q(1, 2)), (Q(1, 2), Q(0))]
    shifts = (0, 1, 4, 5); expansion = [[Z]*8 for _ in range(8)]
    for c, shift in zip(coefficients, shifts):
        expansion = plus(expansion, scale(c, monomial([j ^ shift for j in range(8)])))
    need(expansion == quotient, 'width-one free expansion positive control')
    qcol = mv(quotient, basis[0])
    actual2 = [mul(qcol[i % 8], qcol[i//8]) for i in range(64)]
    wrong2 = [Z]*64
    for c, shift in zip(coefficients, shifts):
        wrong2[shift+8*shift] = add(wrong2[shift+8*shift], c)
    need(norm2([add(a, neg(b)) for a, b in zip(actual2, wrong2)]) == Q(3, 2),
         'width-two rejects width-one expansion lift')
    block = [[Z]*40 for _ in range(40)]
    for bank in range(5):
        for i in range(8):
            for j in range(8):
                block[8*bank+i][8*bank+j] = A[i][j]
    need(matrix_rank(block) == 40, 'retained single-call observations already full rank')
    manifest_path = ROOT/'research/complex-block3-five-in-fourteen/MANIFEST.json'
    manifest = json.loads(manifest_path.read_text())
    source_dir = manifest_path.parent
    drift = [name for name, digest in manifest.items()
             if not (source_dir/name).is_file() or hashlib.sha256((source_dir/name).read_bytes()).hexdigest() != digest]
    return {'schema_version': 1, 'no_new_kappa': True, 'source_hashes': hashes,
            'all_source_factory_matrices_match_independent_construction': True,
            'arbitrary_input_counterexamples': cases, 'true_sector_basis_checks': sector_checks,
            'local_defect_ranks_sigma_plus_minus': [2, 6],
            'retained_A_observation_rows': 40, 'retained_A_observation_rank': 40,
            'free_correction_quotient_nonzeros_per_row': 4,
            'width_one_free_expansion_wrong_width_two_squared_error': '3/2',
            'source_wrapper_manifest_drift': drift,
            'boundary': 'Local sector inference and verification coverage; no global five-in-fourteen impossibility'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-result', type=Path)
    args = ap.parse_args(); actual = calculate()
    if args.write_result:
        with args.write_result.open('x') as stream:
            json.dump(actual, stream, indent=2, sort_keys=True); stream.write('\n')
    else:
        need(json.loads((HERE/'RESULT.json').read_text()) == actual, 'committed receipt equality')
    print('PASS_FIVE_IN_FOURTEEN_SECTOR_AUDIT counterexamples=2 '
          'squared_error=1/2 retained_rank=40 no_new_kappa')


if __name__ == '__main__':
    main()
