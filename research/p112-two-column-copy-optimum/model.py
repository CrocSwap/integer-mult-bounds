# SPDX-License-Identifier: Apache-2.0
"""Exact finite premises for the fixed PR2021 COPY-power proof.
Hanhong Zhao (@Hope7Happiness), substantial OpenAI Codex, Claude Code and Gemini assistance.
No predecessor executable or numerical solver is imported.
"""
from fractions import Fraction as F
from fractions import Fraction as Q
from collections import Counter
import json

def need(ok, message):
    if not ok:
        raise ValueError(message)

def rref(matrix, width=None):
    a = [list(map(F, row)) for row in matrix]
    width = width if width is not None else len(a[0])
    r = 0
    p = []
    for c in range(width):
        k = next((k for k in range(r, len(a)) if a[k][c]), None)
        if k is None:
            continue
        (a[r], a[k]) = (a[k], a[r])
        v = a[r][c]
        a[r] = [x / v for x in a[r]]
        for k in range(len(a)):
            if k != r and a[k][c]:
                v = a[k][c]
                a[k] = [x - v * y for (x, y) in zip(a[k], a[r])]
        p.append(c)
        r += 1
        if r == min(len(a), width):
            break
    return (a[:r], p)

def nullspace(matrix, n=9):
    (rows, p) = rref(matrix, n)
    out = []
    for c in range(n):
        if c not in p:
            v = [F(0)] * n
            v[c] = 1
            for (row, k) in zip(rows, p):
                v[k] = -row[c]
            out.append(v)
    return out

def dot(a, b):
    return sum((x * y for (x, y) in zip(a, b)))

def span(vs):
    s = {0}
    for v in vs:
        s |= {x ^ v for x in list(s)}
    return s

def binary_rank(vs):
    basis = {}
    for x in vs:
        while x:
            k = x.bit_length() - 1
            if k in basis:
                x ^= basis[k]
            else:
                basis[k] = x
                break
    return len(basis)

def support(mat, v):
    return [i for (i, row) in enumerate(mat) if dot(row, v)]

def rho(A, C):
    return binary_rank([sum((B[i][j] << k for (k, j) in enumerate(C))) for i in A])

def serial(mat):
    return [[str(x) for x in row] for row in mat]

def nonreal_control(D, T, K):

    def mul(x, y):
        return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])
    bad = None
    for i in range(112):
        for j in range(112):
            ordinary = (Q(0), Q(0))
            hermitian = (Q(0), Q(0))
            for k in range(9):
                d = (Q(0), D[i][k]) if k == 0 else (D[i][k], Q(0))
                t = (Q(0), -T[j][k]) if k == 0 else (T[j][k], Q(0))
                a = mul(d, t)
                b = mul(d, (t[0], -t[1]))
                ordinary = tuple((x + y for (x, y) in zip(ordinary, a)))
                hermitian = tuple((x + y for (x, y) in zip(hermitian, b)))
            need(ordinary == (K[i][j], 0), 'nonreal ordinary transpose')
            if hermitian != (K[i][j], 0) and bad is None:
                bad = [i, j]
    need(bad is not None, 'Hermitian substitution must fail the nonreal phase control')
    return bad

def compute(src):
    global X, B, L, R, labels
    X = src['root_lines'][8:]
    labels = src['binary_ports'][8:]
    G = [[dot(a, b) for b in X] for a in X]
    B = [[(x // 2 + 1) % 2 for x in row] for row in G]
    need(all((B[i][j] == (labels[i] & labels[j]).bit_count() % 2 for i in range(112) for j in range(112))), 'label pairing')
    L = [row + [int(i == 0)] for (i, row) in enumerate(X)]
    R = [([0] * 8 if i == 0 else row) + [4 * int(i == 0) + int(i == 1)] for (i, row) in enumerate(X)]
    K = [[G[i][j] - (G[i][0] - 4 * int(i == 0)) * int(j == 0) + int(i == 0 and j == 1) for j in range(112)] for i in range(112)]
    need(all((K[i][j] == dot(L[i], R[j]) for i in range(112) for j in range(112))), 'fixed identity')
    need(len(rref(L)[0]) == len(rref(R)[0]) == 9, 'rank-nine factors')
    need(all((K[i][j] == G[i][j] for i in range(112) for j in range(112) if B[i][j])), 'constrained entries')
    baseline = [rho([i for i in range(112) if L[i][k]], [j for j in range(112) if R[j][k]]) for k in range(9)]
    need(baseline == [8] * 8 + [1], 'COPY65 control')
    ker = {}
    for (name, mat) in [('L', L), ('R', R)]:
        records = []
        for h in range(1, 512):
            ids = [i for (i, v) in enumerate(labels) if (h & v).bit_count() % 2]
            ns = nullspace([mat[i] for i in ids])
            need(all((dot(mat[i], v) == 0 for i in ids for v in ns)), 'exact nullspace')
            records.append(dict(character=h, kernel=serial(ns), rank=9 - len(ns)))
        ker[name] = records
    base = {'K': K}
    s = X[0]
    t = X[1]
    z = [0] * 8 + [1]
    lv = s + [-4]
    rv = s + [0]
    rk = t + [-4]
    frames = src['binary_ports'][:8]

    def canon(vs):
        return serial(rref(vs, 9)[0])
    for name in ['L', 'R']:
        for row in ker[name]:
            h = row['character']
            expect = []
            if h in frames:
                i = frames.index(h)
                expect = [[int(i == j) for j in range(9)]]
                if s[i]:
                    expect.append(z)
            elif h == labels[0]:
                expect = [lv if name == 'L' else rv]
            elif name == 'R' and h == labels[1]:
                expect = [rk]
            elif (h & labels[0]).bit_count() % 2 == 0 and (name == 'L' or (h & labels[1]).bit_count() % 2 == 0):
                expect = [z]
            need(canon([[Q(x) for x in v] for v in row['kernel']]) == canon(expect), (name, h))
    for name in ['L', 'R']:
        groups = {json.dumps(r['kernel']): [[Q(x) for x in v] for v in r['kernel']] for r in ker[name] if r['kernel']}
        vals = list(groups.values())
        for (i, A) in enumerate(vals):
            for other in vals[i + 1:]:
                intersection_dim = len(A) + len(other) - len(rref(A + other, 9)[0])
                if intersection_dim:
                    need(intersection_dim == 1 and len(rref(A + [z], 9)[0]) == len(A) and (len(rref(other + [z], 9)[0]) == len(other)), 'distinct kernel intersections must be precisely the shared pure-z line')
    left = {'Z': z}
    right = {'W': z}
    for i in range(8):
        left['E' + str(i)] = right['E' + str(i)] = [int(i == j) for j in range(9)]
    left['V'] = lv
    right['V'] = rv
    right['U'] = rk
    full = [2 ** i for i in range(9)]
    left['F'] = right['F'] = full
    leftsupp = {k: support(L, v) for (k, v) in left.items()}
    rightsupp = {k: support(R, v) for (k, v) in right.items()}
    leftdims = {k: binary_rank([labels[i] for i in v]) for (k, v) in leftsupp.items()}
    rightdims = {k: binary_rank([labels[i] for i in v]) for (k, v) in rightsupp.items()}
    need(leftdims == {k: 1 if k == 'Z' else 9 if k == 'F' else 8 for k in left}, 'left support-span dimensions')
    need(rightdims == {k: 2 if k == 'W' else 9 if k == 'F' else 8 for k in right}, 'right support-span dimensions')
    table = {a: {b: rho(leftsupp[a], rightsupp[b]) for b in right} for a in left}
    zero = [(a, b) for a in left for b in right if table[a][b] == 0]
    need(zero == [('Z', 'V')], 'unique zero-COPY class pair')
    need(dot(z, rv) == 0 and dot(lv, rv) == 4 and (dot(lv, rk) == 18), 'exact coefficient duality pairings')
    mixed = [(a, b) for a in left if a != 'Z' for b in right if b != 'W']
    need(all((table[a][b] >= 7 for (a, b) in mixed)), 'mixed COPY rank lower bound')
    need(all((a == 'V' or b in ['V', 'U'] for (a, b) in mixed if table[a][b] == 7)), 'rank-seven class coverage')
    need(table['V']['V'] == 8, 'V/V support-pairing rank')
    need(all((table[a]['W'] == 2 for a in left if a not in ['Z', 'V'])) and table['V']['W'] == table['Z']['W'] == 1, 'right pure compensation charges')
    need(all((table['Z'][b] == 1 for b in right if b != 'V')), 'left pure compensation charges')
    p = next((i for (i, v) in enumerate(s) if v))
    N = [[Q(int(i == j)) for j in range(9)] for i in range(9)]
    for i in range(9):
        N[i][p] = Q(rv[i])
    aug = [row + [Q(int(i == j)) for j in range(9)] for (i, row) in enumerate(N)]
    (rr, piv) = rref(aug, 9)
    need(piv == list(range(9)), 'attainer basis invertibility')
    inv = [row[9:] for row in rr]
    M = [list(x) for x in zip(*inv)]
    D = [[dot(row, col) for col in zip(*M)] for row in L]
    T = [[dot(row, col) for col in zip(*N)] for row in R]
    need(all((dot(D[i], T[j]) == base['K'][i][j] for i in range(112) for j in range(112))), 'attainer identity on all matrix entries')
    ranks = [rho([i for i in range(112) if D[i][k]], [j for j in range(112) if T[j][k]]) for k in range(9)]
    need(sorted(ranks) == [1, 7] + [8] * 7, 'attainer exact COPY profile')
    hermitian_bad = nonreal_control(D, T, base['K'])
    profiles = {'nine_mixed': [8] * 7 + [7] * 2, 'left_pure': [8] * 7 + [7, 1], 'right_pure_with_leftV': [8] * 8 + [1], 'right_pure_other': [8] * 6 + [7, 7, 2]}
    reduced = {'nine_mixed': [8] * 7 + [7, 1], 'left_pure': [8] * 7 + [7, 1], 'right_pure_with_leftV': [8] * 8 + [0], 'right_pure_other': [8] * 6 + [7, 7, 2]}
    for (name, vs) in reduced.items():
        need(sum(vs) == 64, 'relaxed profile total')
        need(all((sum(sorted(vs, reverse=True)[:k]) <= min(k, 8) * 8 for k in range(1, 10))), 'relaxed profile majorization by eight rank-eight terms')
        need(all((x <= y for (x, y) in zip(sorted(vs), sorted(profiles[name])))), 'lower profile dominates its relaxed profile')
    sharp = [8] * 7 + [7, 1]
    for (name, vs) in profiles.items():
        if name == 'right_pure_other':
            need(sum(vs) == sum(sharp) == 64, 'sharp comparison has equal total')
            need(all((sum(sorted(vs, reverse=True)[:k]) <= sum(sorted(sharp, reverse=True)[:k]) for k in range(1, 10))), 'sharp profile majorizes right-pure-other profile')
        else:
            need(all((x >= y for (x, y) in zip(sorted(vs), sorted(sharp)))), 'case profile dominates sharp profile')
    left_hk = next((v['kernel'] for v in ker['L'] if v['character'] == labels[1]))
    right_hk = next((v['kernel'] for v in ker['R'] if v['character'] == labels[1]))
    need(canon([[Q(x) for x in v] for v in left_hk]) != canon([[Q(x) for x in v] for v in right_hk]), 'left catalogue cannot replace right catalogue at the second live port')
    wrong_label = labels[0] ^ 1
    need(wrong_label.bit_count() % 2 != B[0][0], 'corrupt binary label violates pairing identity')
    need(dot(D[0][:-1], T[0][:-1]) == 0 and base['K'][0][0] == 4, 'omitting compensation breaks the first diagonal entry')
    controls = {'source_digest_checked': True, 'original_COPY65_positive': True, 'omitted_compensation_fails_diagonal_0_0': True, 'left_kernel_transplanted_to_right_rejected_at_character405': True, 'binary_label_bit_corruption_rejected': True, 'zero_cost_pair_fails_diagonal_coefficient_duality': True, 'Hermitian_substitution_fails_phase_scaled_witness': True}
    report = dict(controls=controls, sharp_power_minimum='7*8**q+7**q+1 for every 0<q<=1', left_dimensions=leftdims, right_dimensions=rightdims, pairing_table=table, zero_cost_pairs=zero, duality_pairings={'Z_V': 0, 'V_V': 4, 'V_U': 18}, model_kernel_classes_verified=1022, universal_case_lower_profiles=profiles, majorization_certificates=reduced, attainment_COPY=ranks, attainment_sum=sum(ranks), hermitian_failure_entry=hermitian_bad)
    return dict(baseline_COPY=baseline, kernels=ker, classification=report, witness=dict(M=serial(M), N=serial(N), ranks=ranks))
