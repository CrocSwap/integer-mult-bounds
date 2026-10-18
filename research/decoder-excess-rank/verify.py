#!/usr/bin/env python3
"""Exact evidence for PROOF.md; finite examples are not its universal proof.

Hanson Sun with substantial OpenAI Codex assistance. Apache-2.0.
Gaussian arithmetic and E8 roots: woklerx / PR1077, authenticated before import.
"""
import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from math import gcd, lcm
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = {
    'research/complex-decoder-field-extension-seed44/exact.py',
    'research/complex-decoder-field-extension-seed44/PROOF.md',
    'research/complex-local-word-ceiling/RESULT.json',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def check_sources(manifest=None):
    if manifest is None:
        manifest = json.loads((HERE / 'SOURCES.json').read_text())
    rows = [r for r in manifest['files'] if r['usage'] == 'input']
    need(len(rows) == len(INPUTS) and {r['path'] for r in rows} == INPUTS, 'source inventory')
    for row in rows:
        raw = (ROOT / row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source bytes')
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        need(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source Git blob')


check_sources()
SPEC = importlib.util.spec_from_file_location(
    'pinned_gaussian', ROOT / 'research/complex-decoder-field-extension-seed44/exact.py')
EX = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EX)
G = EX.G
I = G(0, 1)


def transpose(a):
    return [list(x) for x in zip(*a)]


def zeros(n, m):
    return [[G() for _ in range(m)] for _ in range(n)]


def matmul(a, b):
    need(a and b and len(a[0]) == len(b), 'matrix dimensions')
    return [[sum((x * y for x, y in zip(row, col) if x and y), G())
             for col in transpose(b)] for row in a]


def subtract(a, b):
    need(len(a) == len(b) and len(a[0]) == len(b[0]), 'matrix sum dimensions')
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def rank_gaussian(a):
    """Ordinary row elimination in Q(i)."""
    a = [[G(x) for x in row] for row in a]
    count = 0
    for c in range(len(a[0])):
        p = next((j for j in range(count, len(a)) if a[j][c]), None)
        if p is None:
            continue
        a[p], a[count] = a[count], a[p]
        pivot = a[count][c]
        a[count] = [x / pivot for x in a[count]]
        for j in range(count + 1, len(a)):
            if a[j][c]:
                q = a[j][c]
                a[j] = [x - q * y for x, y in zip(a[j], a[count])]
        count += 1
    return count


def integer_rank(a):
    """Separate fraction-free elimination with row-content reduction."""
    a = [list(row) for row in a]
    count = 0
    for c in range(len(a[0])):
        p = next((j for j in range(count, len(a)) if a[j][c]), None)
        if p is None:
            continue
        a[p], a[count] = a[count], a[p]
        pivot = a[count][c]
        for j in range(count + 1, len(a)):
            if not a[j][c]:
                continue
            q = a[j][c]
            row = [pivot * x - q * y for x, y in zip(a[j], a[count])]
            divisor = 0
            for x in row:
                divisor = gcd(divisor, x)
            a[j] = [x // divisor for x in row] if divisor else row
        count += 1
    return count


def clear(a):
    denominator = 1
    for row in a:
        for x in row:
            denominator = lcm(denominator, x.r.denominator, x.i.denominator)
    return denominator, [[(int(x.r * denominator), int(x.i * denominator))
                           for x in row] for row in a]


def rank_realified(a):
    """Use rank_C(a) = rank_Q([[Re,-Im],[Im,Re]])/2."""
    _, a = clear(a)
    real = [[x for x, y in row] + [-y for x, y in row] for row in a]
    real += [[y for x, y in row] + [x for x, y in row] for row in a]
    r = integer_rank(real)
    need(r % 2 == 0, 'realification rank parity')
    return r // 2


def paired_rank(a):
    r = rank_gaussian(a)
    need(r == rank_realified(a), 'independent exact ranks disagree')
    return r


def all_pairs(roots, d, t, conjugate=False):
    """Literal identity with integer complex products after clearing denominators.

    roots are twice the true roots, so target = roots*roots^T/2.
    """
    n = len(roots)
    need(len(d) == len(t) == n and n > 0, 'decoder row count')
    m = len(d[0])
    need(m > 0 and all(len(row) == m for row in d + t), 'decoder term count')
    dd, di = clear(d)
    td, ti = clear(t)
    for i, ri in enumerate(roots):
        for j, rj in enumerate(roots):
            real = imag = 0
            for (a, b), (c, e) in zip(di[i], ti[j]):
                if conjugate:
                    e = -e
                real += a * c - b * e
                imag += a * e + b * c
            need(imag == 0 and 2 * real == dd * td * sum(x * y for x, y in zip(ri, rj)),
                 'all-pairs identity')


def domains():
    roots = EX.roots()
    need(len(roots) == 120 and len(set(roots)) == 120, 'E8 root count')
    need(all(sum(x * x for x in row) == 8 for row in roots), 'E8 norms')
    h = zeros(8, 8)
    for j in range(0, 8, 2):
        h[j][j] = h[j][j + 1] = h[j + 1][j] = G(1)
        h[j + 1][j + 1] = G(-1)
    frame = {tuple(int(2 * x.r) for x in col) for col in transpose(h)}
    need(len(frame) == 8 and frame <= set(roots), 'puncture frame')
    answer = []
    for name, raw in (('P120', roots), ('P112', [r for r in roots if r not in frame])):
        r = [[G(Q(x, 2)) for x in row] for row in raw]
        gram = matmul(transpose(r), r)
        scale = Q(len(raw), 4)
        need(gram == [[G(scale if i == j else 0) for j in range(8)] for i in range(8)],
             'live Gram matrix')
        need(paired_rank(r) == 8, 'live root rank')
        answer.append((name, raw, r, scale, h))
    return answer


def project(r, scale, d):
    a = [[x / scale for x in row] for row in matmul(transpose(r), d)]
    return a, subtract(d, matmul(r, a))


def residual_basis(r, scale, k=6):
    columns = []
    for j in range(len(r)):
        candidate = [G(i == j) - sum((x * y for x, y in zip(ri, r[j])), G()) / scale
                     for i, ri in enumerate(r)]
        if rank_realified(transpose(columns + [candidate])) > len(columns):
            columns.append(candidate)
        if len(columns) == k:
            break
    need(len(columns) == k, 'residual basis length')
    u = transpose(columns)
    need(paired_rank(u) == k and not any(x for row in matmul(transpose(r), u) for x in row),
         'residual basis')
    return u


def gauge(a, coefficient):
    # Right multiplication by I + coefficient * 11^T.
    result = []
    for row in a:
        shift = coefficient * sum(row, G())
        result.append([x + shift for x in row])
    return result


def general_fixture(r, h, u, q, s, t):
    m = 8 + q
    need(0 <= s and 0 <= t and s + t <= q, 'feasible rank pair')
    core = matmul(r, h)
    d, e = zeros(len(r), m), zeros(len(r), m)
    for j in range(len(r)):
        d[j][:8] = core[j]
        e[j][:8] = core[j]
        for a in range(s):
            d[j][8 + a] = u[j][a]
        for a in range(t):
            e[j][8 + s + a] = u[j][a]
    return gauge(d, G(1)), gauge(e, G(-Q(1, m + 1)))


def symmetric_fixture(r, h, u, q, s, mix=True):
    m = 8 + q
    need(0 <= s and 2 * s <= q, 'symmetric rank budget')
    core = matmul(r, h)
    d = zeros(len(r), m)
    for j in range(len(r)):
        d[j][:8] = core[j]
        for a in range(s):
            d[j][8 + a] = u[j][a]
            d[j][8 + s + a] = I * u[j][a]
    return gauge(d, G(-Q(2, m))) if mix else d


def factor_rank_one(n):
    pivot = next(((i, j) for i, row in enumerate(n) for j, x in enumerate(row) if x), None)
    need(pivot is not None, 'nonzero rank-one residual')
    i, j = pivot
    v = [row[j] for row in n]
    z = [x / n[i][j] for x in n[i]]
    need(n == [[x * y for y in z] for x in v], 'rank-one factorization')
    return v, z


def ten_term_conditions(r, a, b, n, p, z, w):
    need(len(z) == len(w) == 10, 'ten-term shape')
    need(all(any(v) for v in (n, p, z, w)), 'nonzero residual factors')
    need(matmul(a, transpose(b)) == [[G(2 * (i == j)) for j in range(8)] for i in range(8)],
         'ten-term core')
    for v in (n, p):
        need(not any(sum((x * y for x, y in zip(col, v)), G()) for col in transpose(r)),
             'outside root orthogonality')
    need(not any(sum((x * y for x, y in zip(row, z)), G()) for row in b), 'Bz')
    need(not any(sum((x * y for x, y in zip(row, w)), G()) for row in a), 'Aw')
    need(not sum((x * y for x, y in zip(z, w)), G()), 'residual coupling')


def costs(roots, d, t):
    n, m = len(roots), len(d[0])
    rows = []
    for ri in roots:
        row = 0
        for j, rj in enumerate(roots):
            dot4 = sum(x * y for x, y in zip(ri, rj))
            need(dot4 % 4 == 0, 'integral E8 pairing')
            row |= ((dot4 // 4 + 1) % 2) << j
        rows.append(row)
    need(EX.rank2(rows) == 9, 'binary label pairing rank')
    charges = []
    for k in range(m):
        left = [i for i in range(n) if d[i][k]]
        mask = sum((bool(t[j][k]) << j) for j in range(n))
        charges.append(EX.rank2([rows[i] & mask for i in left]))
    return charges


def inspect(roots, r, scale, d, t, expected, check_ten=False):
    all_pairs(roots, d, t)
    m = len(d[0])
    need(all(any(col) for col in transpose(d) + transpose(t)), 'every term active')
    a, nd = project(r, scale, d)
    b, nt = project(r, scale, t)
    rd, rt = paired_rank(nd), paired_rank(nt)
    need((rd, rt) == expected, 'residual rank fixture')
    need(paired_rank(d) == 8 + rd and paired_rank(t) == 8 + rt, 'factor ranks')
    need(rd + rt <= m - 8, 'excess-rank budget')
    if check_ten:
        v, z = factor_rank_one(nd)
        w, y = factor_rank_one(nt)
        ten_term_conditions(r, a, b, v, w, z, y)
    return {'terms': m, 'residual_ranks': [rd, rt], 'factor_ranks': [8 + rd, 8 + rt],
            'all_terms_active': True, 'identity_entries': len(roots) ** 2,
            'matrix_sha256': hashlib.sha256(json.dumps(
                [EX.encoded(d), EX.encoded(t)], separators=(',', ':')).encode()).hexdigest()}


def run():
    check_sources()
    records, symmetric, controls, representatives = [], [], [], []

    def reject(label, action):
        try:
            action()
        except ValueError:
            controls.append(label)
        else:
            raise ValueError('accepted false claim: ' + label)

    for name, raw, r, scale, h in domains():
        u = residual_basis(r, scale)
        for q in range(7):
            for s in range(q + 1):
                for t in range(q - s + 1):
                    d, e = general_fixture(r, h, u, q, s, t)
                    record = inspect(raw, r, scale, d, e, (s, t), q == 2 and s == t == 1)
                    records.append({'domain': name, **record})
            for s in range(q // 2 + 1):
                d = symmetric_fixture(r, h, u, q, s)
                record = inspect(raw, r, scale, d, d, (s, s), q == 2 and s == 1)
                symmetric.append({'domain': name, **record})
        if name != 'P112':
            continue
        d = symmetric_fixture(r, h, u, 2, 1, mix=False)
        a, n = project(r, scale, d)
        v, z = factor_rank_one(n)
        need(any(x for row in n for x in row), 'symmetric complex residual is nonzero')
        all_pairs(raw, d, d)
        charges = costs(raw, d, d)
        mixed = gauge(d, G(-Q(1, 5)))
        all_pairs(raw, mixed, mixed)
        mixed_charges = costs(raw, mixed, mixed)
        need(charges[:8] == [8] * 8 and all(charges[k] > 0 for k in (8, 9)), 'copy accounting')
        need(sum(charges) != sum(mixed_charges), 'gauge changes the charged cost')
        representatives.append({'domain': name, 'D': EX.encoded(d), 'costs': charges,
                                'mixed_costs': mixed_charges, 'residual_vector': [x.record() for x in v],
                                'residual_channel': [x.record() for x in z]})
        reject('Hermitian transpose substituted for ordinary transpose', lambda: all_pairs(raw, d, d, True))
        reject('complex symmetric factors forced into root code', lambda: need(paired_rank(n) == 0, 'nonzero isotropic residual'))
        reject('omitted two compensation-term copy charges', lambda: need(sum(charges) == sum(charges[:8]), 'copy invoice'))
        reject('term gauge preserves copied rank', lambda: need(charges == mixed_charges, 'copy supports changed'))
        changed = [[G(x) for x in row] for row in d]
        changed[0][8] = changed[0][8] + 1
        reject('one mutated residual coefficient', lambda: all_pairs(raw, changed, d))
        wrong = [[G(x) for x in row] for row in d]
        for row in wrong:
            row[9] = -I * row[9]
        reject('real residual pair cannot self-cancel', lambda: all_pairs(raw, wrong, wrong))
        altered_z = [G(x) for x in z]
        altered_z[9] = G(1)
        reject('ten-term residual coupling is required', lambda: ten_term_conditions(r, a, a, v, v, z, altered_z))
        reject('higher-rank residual cannot use rank-one normal form', lambda: factor_rank_one(u))
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    bad = json.loads(json.dumps(pins))
    bad['files'] = [x for x in bad['files'] if x['path'] != sorted(INPUTS)[0]]
    reject('omitted live source pin', lambda: check_sources(bad))
    bad = json.loads(json.dumps(pins))
    next(x for x in bad['files'] if x['usage'] == 'input')['sha256'] = '0' * 64
    reject('changed live source digest', lambda: check_sources(bad))
    need(len(records) == 168 and len(symmetric) == 32 and len(controls) == 10, 'coverage inventory')
    return {'schema_version': 1, 'status': 'PASS_DECODER_EXCESS_RANK', 'general_examples': records,
            'symmetric_examples': symmetric, 'controls': controls, 'representatives': representatives,
            'scope': 'Finite exact evidence for the universal written rank theorem in PROOF.md; no copy optimum, physical supplier, new kappa or full multiplication theorem.'}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate RESULT.json')
    args = parser.parse_args()
    result = run()
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), 'complete receipt mismatch')
    print('PASS_DECODER_EXCESS_RANK general=168 symmetric=32 controls=10')


if __name__ == '__main__':
    main()
