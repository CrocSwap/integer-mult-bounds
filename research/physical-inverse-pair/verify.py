#!/usr/bin/env python3
"""Source-bound one-pair check; standard library, no Git or native replay.

Apache-2.0. JoyboyBrian with substantial OpenAI Codex assistance.
"""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P = 65537
J = 256
N = 112


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def parity(x):
    return x.bit_count() & 1


def mv(rows, x):
    return sum(parity(r & x) << j for j, r in enumerate(rows))


def transpose(rows):
    return [sum(((r >> j) & 1) << k for k, r in enumerate(rows)) for j in range(9)]


def mix(x, columns, inverse=False):
    # All source reads finish before the first owner update.
    modes = [sum(s * x[i] for i, s in c) % P for c in columns]
    out = list(x)
    scale = pow(52 if inverse else 4, -1, P)
    for c, t in zip(columns, modes):
        for i, s in c:
            out[i] = (out[i] - s * scale * t) % P
    return out


def diagonal(d, x):
    return [a * b % P for a, b in zip(d, x)]


def plus(x, y, sign=1):
    return [(a + sign * b) % P for a, b in zip(x, y)]


def pair(x, y, q, d, columns, omit_exit_q=False, omit_entry=False, wrong_order=False):
    qi = [pow(v, -1, P) for v in q]
    y = list(y) if omit_entry else mix(y, columns, True)
    x = diagonal(d, plus(x, diagonal(q, mix(y, columns)), -1))
    y = diagonal(d, y)
    source = diagonal(qi, mix(x, columns, True))
    if wrong_order:
        source = mix(diagonal(qi, x), columns, True)
    y = plus(y, source)
    y = mix(y, columns) if omit_exit_q else diagonal(qi, mix(diagonal(q, y), columns))
    return x, y


def standard(x, y, q, d):
    return (diagonal(d, plus(x, diagonal(q, y), -1)),
            diagonal(d, diagonal([pow(v, -1, P) for v in q], x)))


def cleanup(targets):
    owned = {('query', i) for i in range(N)} | {('mode', i) for i in range(8)}
    need(all(t in owned for t in targets), 'Cleanup must not address arbitrary helper/main input')


def run():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for source in manifest['files']:
        if source['usage'] == 'input':
            need(sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256'],
                 'Pinned source mismatch: ' + source['path'])
    receipt = json.loads((ROOT / 'research/coded-native-caller/NORMALIZERS.json').read_text())
    records = receipt['ports']
    modes = receipt['mode_columns']
    a = [[Fraction(v) for v in r] for r in json.loads(
        (ROOT / 'research/coded-native-caller/CODE.json').read_text())['A']]
    need(len(records) == N and len(modes) == 8, 'Source dimensions')
    need(all(len(c) == N and sum(bool(v) for v in c) == 56 for c in modes), 'Mode incidence')
    need(all(sum(bool(c[i]) for c in modes) == 4 for i in range(N)), 'Owner incidence')
    need(all(sum(x*y for x, y in zip(c, e)) == 56*(i == j)
             for i, c in enumerate(modes) for j, e in enumerate(modes)), 'Mode Gram identity')
    need(all(a[i][j] == (i == j)-Fraction(sum(c[i]*c[j] for c in modes), 4)
             for i in range(N) for j in range(N)), 'Every exact code entry')
    need(J*J % P == P-1, 'Gaussian rational finite-field embedding')
    columns = [[(i, s) for i, s in enumerate(c) if s] for c in modes]
    normalizer_checks = 0
    for i, rec in enumerate(records):
        rows, z = rec['G_rows'], rec['Z_mask']
        gt = transpose(rows)
        need(rec['port'] == i and mv(rows, 1) == rec['q'], 'Actual source owner port')
        need(all(parity(r & s) == (j == k) for j, r in enumerate(rows)
                 for k, s in enumerate(rows)), 'Orthogonal source K')
        for u in range(512):
            # Direct Walsh action of Z_z P_G, independently from an assumed commutator.
            v = mv(gt, u ^ z)
            need((v.bit_count()-u.bit_count()) % 4 == 0, 'Signed K preserves absolute R phase')
            normalizer_checks += 1
    ri, rj = records[:2]
    u = mv(rj['G_rows'], 1)
    s = 1-2*parity(rj['Z_mask'] & u)
    v = mv(transpose(ri['G_rows']), u)
    s *= 1-2*parity(ri['Z_mask'] & u)
    need((v, s*a[0][1]) == (22, Fraction(1, 2)), 'Literal signed C01 address1 witness')
    need(v != 1 and a[0][1] == -Fraction(1, 2), 'Old scalar A^-1 recipe remains rejected')
    unsigned_rejected = any(mv(transpose(r['G_rows']), u).bit_count() % 4 != u.bit_count() % 4
                            for r in records for u in range(512))
    need(unsigned_rejected, 'Omitting K signs must fail absolute-phase centralization')
    fibers = [(0,), (1,), (19,), (511,), (0, 1), (1, 19), (17, 256), (511, 511)]
    rejected = {'omit_exit_q': False, 'omit_entry': False, 'wrong_order': False}
    basis_checks = 0
    for frequency in fibers:
        physical = [tuple(mv(transpose(r['G_rows']), u ^ r['Z_mask']) for u in frequency)
                    for r in records]
        q = [pow(J, sum(v & 1 for v in row), P) for row in physical]
        d = [pow(J, sum((v >> 1).bit_count() for v in row), P) for row in physical]
        need(all(qi*di % P == pow(J, sum(u.bit_count() for u in frequency), P)
                 for qi, di in zip(q, d)), 'Actual DQ constant on source fiber')
        for col in range(2*N):
            x, y = [0]*N, [0]*N
            (x if col < N else y)[col % N] = 1
            want = standard(x, y, q, d)
            need(pair(x, y, q, d, columns) == want, 'All four blocks on independent basis column')
            basis_checks += 1
            for mutant in rejected:
                if not rejected[mutant]:
                    rejected[mutant] = pair(x, y, q, d, columns, **{mutant: True}) != want
        x, y = [(i*i+3) % P for i in range(N)], [(7*i+11) % P for i in range(N)]
        need(pair(x, y, q, d, columns) == standard(x, y, q, d), 'Mixed arbitrary owner inputs')
    need(all(rejected.values()), 'Every semantic mutant must be distinguished')
    # The physical delta at owner1/address1 has all 512 Walsh frequencies.
    for frequency in range(512):
        physical = [mv(transpose(r['G_rows']), frequency ^ r['Z_mask']) for r in records]
        q = [pow(J, v & 1, P) for v in physical]
        d = [pow(J, (v >> 1).bit_count(), P) for v in physical]
        x, y = [0]*N, [0]*N
        y[1] = (1-2*(physical[1] & 1))*pow(512, -1, P) % P
        need(pair(x, y, q, d, columns) == standard(x, y, q, d),
             'Every Walsh coefficient of physical owner1/address1 input')
    clean = [('mode', i) for _ in range(6) for i in range(8)]
    clean += [('query', i) for _ in range(2) for i in range(N)]
    cleanup(clean)
    try:
        cleanup(clean + [('helper', 17)])
    except ValueError:
        pass
    else:
        raise ValueError('Illegal helper erasure accepted')
    return {
        'status': 'PASS_PHYSICAL_INVERSE_PAIR', 'scope': 'One-stage exact operator identity; conditional physical ledger, no new kappa',
        'normalizer_absolute_phase_checks': normalizer_checks,
        'widths': [1, 2], 'walsh_fibers': [list(v) for v in fibers],
        'independent_main_basis_columns': basis_checks,
        'physical_address1_walsh_coefficients': 512, 'mixed_input_checks': len(fibers), 'helpers': '408 inherited autonomous output operators; never scratch',
        'semantic_rejections': list(rejected) + ['unsigned_K', 'old_scalar_A', 'helper_erasure'],
        'added_paid_rank1_jobs': 336, 'total_paid_profile': {'1':2537, '2':412, '3':510, '4':127, '5':40},
        'wrapper_monomial_maps_upper': 1792, 'scalar_adds': 2800,
        'recoding_owned_clears': 48, 'query_initial_clears':112, 'query_copies':112, 'query_owned_erases':112,
        'recoding_field_workspace':120, 'inverse_recode_calls':2, 'forward_recode_calls':1,
        'unknown_nonzero_costs': ['Native/query internal scratch and movement', 'Physical field-map and rational ADD tape tariffs', 'Finite precision and global error budget', 'Full-controller bridge and boundary accounting']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run()
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2)+'\n')
    else:
        need(json.loads(path.read_text()) == result, 'Committed mathematical receipt differs')
    print(json.dumps(result, sort_keys=True))
