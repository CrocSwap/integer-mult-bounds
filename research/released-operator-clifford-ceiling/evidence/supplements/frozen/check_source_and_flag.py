#!/usr/bin/env python3
"""Read-only source/flag checks, not a universal operator theorem checker."""
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def linear(rows, vector):
    return sum(((row & vector).bit_count() & 1) << j
               for j, row in enumerate(rows))


def image(columns, vector):
    answer = 0
    while vector:
        low = vector & -vector
        answer ^= columns[low.bit_length() - 1]
        vector ^= low
    return answer


def compose(left, right):
    return [image(left, column) for column in right]


def span_basis(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            p = vector.bit_length() - 1
            if p in pivots:
                vector ^= pivots[p]
            else:
                pivots[p] = vector
                break
    return pivots


def belongs(vector, pivots):
    while vector:
        p = vector.bit_length() - 1
        if p not in pivots:
            return False
        vector ^= pivots[p]
    return True


def preserves(operator, space):
    pivots = span_basis(space)
    return all(belongs(image(operator, vector), pivots) for vector in space)


def main():
    manifest = json.loads((ROOT / 'SOURCES.json').read_text())
    for item in manifest['files']:
        path = ROOT / 'frozen' / Path(item['path']).name
        require(hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'],
                'Frozen source hash mismatch: ' + str(path))
    code = json.loads((ROOT / 'frozen/CODE.json').read_text())
    normalizers = json.loads((ROOT / 'frozen/NORMALIZERS.json').read_text())
    matrix = [[Fraction(x) for x in row] for row in code['A']]
    ports = normalizers['ports']
    require(len(matrix) == 112 and all(len(row) == 112 for row in matrix),
            'Owner matrix shape changed')
    require(len(ports) == 112, 'Port inventory changed')
    qs = [linear(p['G_rows'], 1) for p in ports]
    checks = {
        'zero_diagonal': all(matrix[i][i] == 0 for i in range(112)),
        'row_and_column_nonzero_counts_52': all(
            sum(x != 0 for x in row) == 52 for row in matrix) and all(
            sum(matrix[i][j] != 0 for i in range(112)) == 52
            for j in range(112)),
        '112_distinct_q': len(set(qs)) == 112,
        'G_rows_match_literal_q': all(q == p['q'] for q, p in zip(qs, ports)),
        'q_weight_3_or_7': all(q.bit_count() in (3, 7) for q in qs),
        'all_G_orthogonal': all(
            ((p['G_rows'][i] & p['G_rows'][j]).bit_count() & 1) == (i == j)
            for p in ports for i in range(9) for j in range(9)),
        'A2_plus_12A_equals_13I': all(
            sum(matrix[i][k] * matrix[k][j] for k in range(112))
            + 12 * matrix[i][j] == (13 if i == j else 0)
            for i in range(112) for j in range(112)),
    }
    require(all(checks.values()), 'Source structural check failed')

    # Binary symplectic witness on the actual 17 axes; global phases are
    # deliberately outside this finite flag check's scope.
    n = 17
    q, w = 0, 9
    xmask = (1 << n) - 1
    ident = [1 << j for j in range(2*n)]
    Q = ident.copy()
    Q[n + q] ^= 1 << q
    D = ident.copy()
    for j in range(9, 17):
        D[n + j] ^= 1 << j
    H = ident.copy()  # CZ(q,w)
    H[q] ^= 1 << (n + w)
    H[w] ^= 1 << (n + q)
    K = compose(D, compose(H, D))
    L0 = [1 << (n+j) for j in range(n)]
    Lq = [image(Q, v) for v in L0]
    Lw = [image(D, v) for v in L0]
    Lqw = [image(D, v) for v in Lq]
    monomial = lambda op: all((image(op, v) & xmask) == 0 for v in L0)
    flag = {
        'h_CZ_in_H0': all(preserves(H, space) for space in (L0, Lq, Lw)),
        'Qinv_h_Q_monomial': monomial(compose(Q, compose(H, Q))),
        'D3_h_D3inv_monomial': monomial(K),
        'k_preserves_correct_transported_flags': all(
            preserves(K, space) for space in (L0, Lw, Lqw)),
        'k_central_X_image_is_q_plus_w':
            (image(K, 1 << q) & xmask) == ((1 << q) | (1 << w)),
        'k_does_not_preserve_Lq': not preserves(K, Lq),
        'Qinv_k_Q_not_monomial': not monomial(compose(Q, compose(K, Q))),
        'quotient_flag_excludes_noncentral_U_vectors': all(
            (image(K, v) & ((1 << 9)-2)) != 0
            for v in range(1, 1 << 9) if v != 1),
    }
    require(all(flag.values()), 'Transported-flag witness failed')
    corrupted_qs = qs.copy()
    corrupted_qs[1] = corrupted_qs[0]
    bad_G = ports[0]['G_rows'].copy()
    bad_G[0] ^= 1
    controls = {
        'reject_nonzero_code_diagonal': not all(
            (Fraction(1) if i == 0 else matrix[i][i]) == 0 for i in range(112)),
        'reject_duplicated_port_direction': len(set(corrupted_qs)) != 112,
        'reject_corrupted_orthogonal_map': not all(
            ((bad_G[i] & bad_G[j]).bit_count() & 1) == (i == j)
            for i in range(9) for j in range(9)),
        'reject_untransported_H0_substitution': not preserves(K, Lq),
        'reject_central_shift_erasure':
            (image(K, 1 << q) & xmask) != (1 << q),
    }
    require(all(controls.values()), 'A rejection control failed')
    print(json.dumps({
        'status': 'PASS_SOURCE_AND_TRANSPORTED_FLAG_ONLY',
        'scope': 'Exact pinned source structure and one 17-axis binary symplectic '
                 'transport witness; not an all-width theorem replay, phase '
                 'checker, t0 search, native/compiler replay, or supplier admission.',
        'source_checks': checks,
        'transported_flag_witness': flag,
        'rejection_controls': controls,
        'axis_embedding': {'central': 0, 'stage1': list(range(1, 9)),
                           'stage3': list(range(9, 17))},
    }, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
