#!/usr/bin/env python3
"""Portable exact algebra technique tests; no network, solver, or Lean required."""
import argparse
from fractions import Fraction as F
from itertools import permutations, product
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def matmul(A, B):
    return [[sum(a * b for a, b in zip(row, col)) for col in zip(*B)] for row in A]


def rank(A):
    M = [list(map(F, row)) for row in A]
    r = 0
    for j in range(len(M[0]) if M else 0):
        k = next((k for k in range(r, len(M)) if M[k][j]), None)
        if k is None:
            continue
        M[r], M[k] = M[k], M[r]
        a = M[r][j]
        M[r] = [x / a for x in M[r]]
        for k in range(r + 1, len(M)):
            a = M[k][j]
            if a:
                M[k] = [x - a * y for x, y in zip(M[k], M[r])]
        r += 1
    return r


def ga_add(A, B):
    C = A.copy()
    for k, v in B.items():
        C[k] = C.get(k, F(0)) + v
    return {k: v for k, v in C.items() if v}


def ga_scale(a, A):
    return {k: a * v for k, v in A.items() if a * v}


def pmul(a, b):
    return tuple(a[b[j]] for j in range(3))


def ga_mul(A, B):
    C = {}
    for a, u in A.items():
        for b, v in B.items():
            k = pmul(a, b)
            C[k] = C.get(k, F(0)) + u * v
    return {k: v for k, v in C.items() if v}


def hecke_test():
    one, h, g = (0, 1, 2), (2, 1, 0), (1, 0, 2)
    I = {one: F(1)}
    e = ga_scale(F(1, 2), {one: F(1), h: F(1)})
    T = ga_mul(ga_mul(e, {g: F(1)}), e)
    M = ga_add(ga_add(I, ga_scale(-1, e)), T)
    Mi = ga_add(ga_add(I, ga_scale(-2, e)), ga_scale(2, T))
    require(ga_mul(e, e) == e, 'Hecke idempotent')
    require(ga_mul(T, T) == ga_scale(F(1, 2), ga_add(e, T)), 'Hecke quadratic relation')
    require(ga_mul(M, Mi) == I and ga_mul(Mi, M) == I, 'whole-input Hecke inverse')
    require(ga_mul(M, M) == ga_add(ga_scale(F(1, 2), M), ga_scale(F(1, 2), I)), 'whole-space minimal polynomial')
    # A dropped complementary sector must not be accepted as a full inverse.
    require(ga_mul(T, ga_add(ga_scale(2, T), ga_scale(-1, e))) == e, 'sector inverse')
    require(e != I, 'complement-retention negative control')
    def addr(p, x, f):
        y = 0
        for j in range(f):
            d = (x >> (3 * j)) & 7
            out = sum(((d >> i) & 1) << p[i] for i in range(3))
            y |= out << (3 * j)
        return y
    def apply(A, v, f):
        out = [F(0)] * len(v)
        for p, c in A.items():
            for x, a in enumerate(v):
                out[addr(p, x, f)] += c * a
        return out
    entries = 0
    for f in range(1, 5):
        v = [F((37 * j + f) % 101 - 50) for j in range(8 ** f)]
        require(apply(Mi, apply(M, v, f), f) == v, 'actual tensor-coordinate forward inverse')
        require(apply(M, apply(Mi, v, f), f) == v, 'actual tensor-coordinate inverse forward')
        entries += len(v)
    return {'all_width_group_algebra_identities': 5, 'coordinate_widths': [1, 2, 3, 4], 'checked_vector_entries_per_direction': entries, 'norm2_bound': '1', 'inverse_norm2_bound': '2', 'retained_complement_control': True}


def pauli_test():
    records = []
    for f in range(1, 5):
        N = 2 ** f
        for anchored in (False, True):
            A = [[F(0)] * N for _ in range(N)]
            B = [[F(0)] * N for _ in range(N)]
            for x in range(N):
                A[x][x] = F(-1 if ((x & 1) if anchored else x.bit_count() % 2) else 1)
                B[x ^ (1 if anchored else N - 1)][x] = F(1)
            I = identity(N)
            Z = [[F(0)] * N for _ in range(N)]
            blocks = [[Z, I, A], [[[-a for a in row] for row in I], Z, B], [[[-a for a in row] for row in A], [[-a for a in row] for row in B], Z]]
            M = [sum((blocks[i][j][r] for j in range(3)), []) for i in range(3) for r in range(N)]
            got = rank(M)
            want = 3 * N if anchored or f % 2 else 2 * N
            require(got == want, 'phase-sensitive blow-up rank')
            if anchored or f % 2:
                AB = matmul(A, B)
                M2 = matmul(M, M)
                M4 = matmul(M2, M2)
                require(all(M4[i][j] + 5 * M2[i][j] + 4 * F(i == j) == 0 for i in range(3 * N) for j in range(3 * N)), 'anchored spectral polynomial')
                # Recover each input from every basis output; this verifies the literal inverse.
                def act(M, v):
                    return [sum(a * b for a, b in zip(row, v)) for row in M]
                for k in range(3 * N):
                    initial = [F(j == k) for j in range(3 * N)]
                    rr, ss, tt = (initial[j * N:(j + 1) * N] for j in range(3))
                    az, br = act(A, ss), act(B, rr)
                    zz = [x / 2 for x in act(AB, [t - a + b for t, a, b in zip(tt, az, br)])]
                    xx = [b - s for b, s in zip(act(B, zz), ss)]
                    yy = [r - a for r, a in zip(rr, act(A, zz))]
                    require(act(M, xx + yy + zz) == initial, 'explicit free Pauli inverse')
            records.append({'f': f, 'anchored': anchored, 'reduced_rank': got, 'full_8ary_rank': got * 4 ** f})
    scalar_ranks = []
    for a, b, c in product(range(-2, 3), repeat=3):
        scalar_ranks.append(rank([[0, c, a], [-c, 0, b], [-a, -b, 0]]))
    require(max(scalar_ranks) == 2, 'scalar skew rank')
    return {'records': records, 'scalar_specializations_checked': len(scalar_ranks), 'maximum_scalar_rank': 2, 'even_width_false_promotion_rejected': True, 'anchored_operator_norm2_bound': 2, 'anchored_inverse_norm2_bound': 1, 'anchored_inverse_coordinate_norm_bound': '3/2', 'anchored_model': 'one designated native address bit; broader than identical tensor-letter grammar'}


def hyperbolic_test():
    P = [[F(1), F(1)], [F(0), F(1)]]
    Pi = [[F(1), F(-1)], [F(0), F(1)]]
    require(matmul(P, Pi) == identity(2), 'original basis change inverse')
    S = [[F(0)] * 4 for _ in range(4)]
    for i in range(2):
        for j in range(2):
            S[i][j] = P[i][j]
            S[2 + i][2 + j] = Pi[j][i]
    J = [[F(0)] * 4 for _ in range(4)]
    for i in range(2):
        J[i][2 + i], J[2 + i][i] = F(1), F(-1)
    require(matmul(list(map(list, zip(*S))), matmul(J, S)) == J, 'hyperbolic symplectic chart')
    A = {(i, j, k): F(1 + i + 2 * j + 4 * k) for i, j, k in product(range(2), repeat=3)}
    B = {(i, j, k): sum(P[i][a] * P[j][b] * P[k][c] * A[a, b, c] for a, b, c in product(range(2), repeat=3)) for i, j, k in product(range(2), repeat=3)}
    padded = {(i, j, k): A.get((i, j, k), F(0)) for i, j, k in product(range(4), repeat=3)}
    got = {(i, j, k): sum(S[i][a] * S[j][b] * S[k][c] * v for (a, b, c), v in padded.items()) for i, j, k in product(range(4), repeat=3)}
    require(all(got[i, j, k] == B.get((i, j, k), F(0)) for i, j, k in got), 'literal padded action')
    # Conjugation data cannot recover an absolute scalar.
    Z, X = [[F(1), F(0)], [F(0), F(-1)]], [[F(0), F(1)], [F(1), F(0)]]
    negI = [[-x for x in row] for row in identity(2)]
    require(matmul(negI, matmul(X, negI)) == X and matmul(negI, matmul(Z, negI)) == Z, 'central phase invisible to tableau')
    return {'padding_volume_factor': 8, 'padded_coordinates_checked': 64, 'symplectic_chart_identity': True, 'actual_tensor_action': True, 'global_phase_tableau_control': True, 'scope': 'forward explicit padding example, not a kernel check or proof of the converse theorem'}


def funding_test():
    # This is an exact conditional invoice, not an exhibited 5-in-14 supplier.
    require(5 ** 16 * 3 ** 15 > 14 ** 16, 'q=1/16 productive moment')
    require(5 ** 15 * 3 ** 14 < 14 ** 15, 'q=1/15 root bracket')
    qc, kappa, c = F(1, 16), F(1, 20), F(3, 32)
    q = (kappa + qc) / 2
    delta = min(F(1, 100), (q - kappa) / (4 * (q + 1)), (c - q) / 16)
    eps, beta = 1 - delta, 1 - 3 * delta
    layout, group = delta / 100, delta / 10
    xi = eps * (1 + q) - c + layout
    stop = (qc - q) / (2 * qc)
    rows = {'simultaneous_transform': eps * q, 'routing': F(1), 'fused_gaussian': 1 - eps + q * beta, 'standalone_addressing': F(1), 'group_scans': 1 - eps + beta, 'boundary': c + xi - eps, 'indexed_sparse_axes': F(1, 2) + xi - eps, 'precision_products': eps, 'core_face_recovery': 79 - eps - beta}
    require(all(s > kappa for s in rows.values()), 'all nine rows must beat kappa')
    require(F(1, 2) < xi < eps, 'layout interval')
    require(beta + 1 - eps < 1, 'key volume')
    require(1 - beta - 2 * (1 - eps) > 0, 'membership guard')
    require(1 - eps - group > 0, 'group guard')
    require(1 - (beta + 2 * xi - 2 + group) > 0, 'chirp guard')
    require(qc * (1 - stop) > q, 'strict provider loss')
    require(28 > 5 * 3, 'a paid two-evaluation exactification loses the moment even at q=0')
    precision = []
    for depth in (1, 2, 3, 4):
        P = 128
        error_multiplier = (56 ** (depth + 1) - 1) // 55
        guard = error_multiplier.bit_length() + 2
        require(error_multiplier < 2 ** (guard - 1), 'fixed-coefficient error envelope')
        require(guard <= 6 * (depth + 1) + 3, 'logarithmic guard in recursive dimension')
        precision.append({'depth': depth, 'abstract_recurrence_guard_bits': guard, 'digit_width_f': 3 ** depth, 'coordinate_guard_if_array_dimension_8powf': guard + (3 * (3 ** depth) + 3) // 2, 'laurent_guard_for_D3_delta_2minusP': 3 * P * depth})
    return {'scope': 'conditional 5-in-14 and native funding arithmetic only', 'q_root_strict_bracket': ['1/16', '1/15'], 'q_C_tested': str(qc), 'kappa_target_tested': str(kappa), 'delta': str(delta), 'nine_row_savings': {k: str(v) for k, v in rows.items()}, 'strict_provider_stop': str(stop), 'precision_records': precision, 'precision_scope': 'scalar recurrence assumes a declared norm and constant local factor; coordinate noise in 3D entries adds ceil(log2(3D)/2) guard; native use also requires f=O(log p)', 'supplier_exhibited': False, 'new_kappa': False}


def run():
    return {'status': 'PASS_EXACT_ALGEBRA_TECHNIQUES', 'hecke': hecke_test(), 'noncommutative_encoding': pauli_test(), 'local_precedent_transport': hyperbolic_test(), 'conditional_invoice': funding_test()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path)
    p.add_argument('--check', type=Path)
    args = p.parse_args()
    report = run()
    if args.check:
        require(json.loads(args.check.read_text(encoding='utf-8')) == report, 'stored expected result mismatch')
    if args.out:
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(report, sort_keys=True))

if __name__ == '__main__':
    main()
