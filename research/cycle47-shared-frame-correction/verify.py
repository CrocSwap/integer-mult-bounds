#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact census for shared rank-8 corrections on the selected P112 E8 model.

All arithmetic used in the correction factorization and screening is exact.
The only float values are display summaries. Standard library only.
"""
import hashlib
import importlib.util
import itertools
import json
import tarfile
import time
from collections import Counter, defaultdict
from fractions import Fraction as Q
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERT = json.loads((HERE / 'CERTIFICATE.json').read_text())
FAILS = []


def check(tag, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + tag + ((' | ' + detail) if detail else ''), flush=True)
    if not ok:
        FAILS.append(tag)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inverse(A):
    n = len(A)
    M = [[Q(x) for x in row] + [Q(int(i == j)) for j in range(n)] for i, row in enumerate(A)]
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c]), None)
        if p is None:
            raise ValueError('singular pivot matrix')
        M[c], M[p] = M[p], M[c]
        z = M[c][c]
        M[c] = [x / z for x in M[c]]
        for r in range(n):
            if r != c and M[r][c]:
                z = M[r][c]
                M[r] = [x - z * y for x, y in zip(M[r], M[c])]
    return [row[n:] for row in M]


def row_pivots(rows):
    A = [[Q(x) for x in row] for row in rows]
    n = len(A[0])
    pivots = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, len(A)) if A[i][c]), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        z = A[r][c]
        A[r] = [x / z for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c]:
                z = A[i][c]
                A[i] = [x - z * y for x, y in zip(A[i], A[r])]
        pivots.append(c)
        r += 1
        if r == len(A):
            break
    return pivots


def qrank(rows):
    return len(row_pivots(rows))


def f2rank(rows):
    basis = {}
    rank = 0
    for row in rows:
        x = sum((int(v) & 1) << j for j, v in enumerate(row))
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                basis[h] = x
                rank += 1
                break
    return rank


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))]
            for i in range(len(A))]


def e8_binary_images(lines, gram, dot):
    # The same integral E8 basis as the geometry probe in the #2278 handoff.
    basis = [(2, -2, 0, 0, 0, 0, 0, 0), (0, 2, -2, 0, 0, 0, 0, 0),
             (0, 0, 2, -2, 0, 0, 0, 0), (0, 0, 0, 2, -2, 0, 0, 0),
             (0, 0, 0, 0, 2, -2, 0, 0), (0, 0, 0, 0, 0, 2, -2, 0),
             (0, 0, 0, 0, 0, 2, 2, 0), (-1,) * 8]

    def solve(v):
        n = 8
        A = [[Q(basis[j][i]) for j in range(n)] + [Q(v[i])] for i in range(n)]
        for c in range(n):
            p = next(r for r in range(c, n) if A[r][c])
            A[c], A[p] = A[p], A[c]
            z = A[c][c]
            A[c] = [x / z for x in A[c]]
            for r in range(n):
                if r != c and A[r][c]:
                    z = A[r][c]
                    A[r] = [x - z * y for x, y in zip(A[r], A[c])]
        x = [A[i][n] for i in range(n)]
        if any(t.denominator != 1 for t in x):
            raise ValueError('root is not in the declared E8 basis')
        return tuple(int(t) & 1 for t in x)

    bgram = [[dot(basis[i], basis[j]) & 1 for j in range(8)] for i in range(8)]
    images = [solve(v) for v in lines]

    def beta(x, y):
        return sum(x[i] * bgram[i][j] * y[j] for i in range(8) for j in range(8)) & 1

    if any(beta(images[i], images[j]) != (gram[i][j] & 1)
           for i in range(120) for j in range(120)):
        raise ValueError('E8 binary form disagrees with the pinned Gram matrix')
    return images, beta


def selected_labels():
    source = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
    expected = 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != expected:
        raise ValueError('selected replay archive SHA256 mismatch')
    member = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
    with tarfile.open(source, 'r:gz') as tf:
        data = json.load(tf.extractfile(member))
    q = sorted(int(row['q']) for row in data['recipes'])
    if len(q) != 112 or len(set(q)) != 112:
        raise ValueError('selected source does not contain 112 distinct q labels')
    return q


def map_checks(m, q):
    q_to_line = CERT['q_to_line']
    qkeys = [int(item['q']) for item in q_to_line]
    lines = [int(item['line']) for item in q_to_line]
    C = {x for x in range(512) if x.bit_count() in (3, 7)}
    O = sorted(C - set(q))
    if len(C) != 120 or len(O) != 8 or qkeys != q or len(set(lines)) != 112:
        return False, 'label-map cardinality'
    if set(lines) != set(m.P112):
        return False, 'map does not cover the selected P112 lines'
    by_q = dict(zip(qkeys, lines))
    # The 112-by-112 binary pairing and the eight deleted-frame signatures agree.
    for x in q:
        i = by_q[x]
        for y in q:
            j = by_q[y]
            if ((x & y).bit_count() & 1) != ((m.NROW[i] >> j) & 1):
                return False, 'selected-label pairing mismatch'
        for k, o in enumerate(O):
            if ((x & o).bit_count() & 1) != ((m.NROW[i] >> m.FRAME0[k]) & 1):
                return False, 'deleted-frame signature mismatch'
    # Mutation control: one incorrect line assignment must break the exact isomorphism.
    wrong = dict(by_q)
    wrong[q[0]] = next(i for i in m.P112 if i != wrong[q[0]])
    rejected = any(((x & y).bit_count() & 1) != ((m.NROW[wrong[x]] >> wrong[y]) & 1)
                   for x in q for y in q)
    return rejected, '112 labels mapped bijectively to P112; all internal/deleted signatures match; mutation rejected'


def enumerate_frames(selected, ip):
    orth = [[ip[a][b] == 0 for b in range(120)] for a in range(120)]
    frames = set()

    def extend(cur, cand):
        if len(cur) == 8:
            frames.add(tuple(cur))
            return
        for c in cand:
            if c > cur[-1]:
                extend(cur + [c], [z for z in cand if z > c and orth[c][z]])

    for a in selected:
        extend([a], [z for z in selected if z > a and orth[a][z]])
    return sorted(frames)


def correction_block(S, rp, selected, ip, images, beta):
    Sset = set(S)
    T = [b for b in selected if b not in Sset and beta(rp, images[b]) == 0
         and any(ip[a][b] & 1 for a in S)]
    rows = [[ip[a][b] if b in T else 0 for b in selected] for a in S]
    return rows, T


def main():
    started = time.monotonic()
    m = load_module('frame_pair_base', ROOT / 'research/complex-frame-pair-decoders/verify.py')
    q = selected_labels()
    mapped_ok, map_note = map_checks(m, q)
    check('selected-label-isomorphism', mapped_ok, map_note)
    selected = sorted(int(item['line']) for item in CERT['q_to_line'])
    ip = m.IP
    images, beta = e8_binary_images(m.LINES, ip, m.ip)
    frames = enumerate_frames(selected, ip)
    check('frame-domain', len(frames) == 1260, 'all orthogonal 8-frames in the selected 112 lines')

    groups = defaultdict(list)
    per_frame = Counter()
    for S in frames:
        rs = [tuple((x >> i) & 1 for i in range(8)) for x in range(256)
              if all(beta(tuple((x >> i) & 1 for i in range(8)), images[a]) == 1 for a in S)]
        per_frame[len(rs)] += 1
        for rp in rs:
            groups[rp].append(S)
    pair_count = sum(len(v) * (len(v) - 1) // 2 for v in groups.values())
    group_sizes = Counter(map(len, groups.values()))
    check('common-direction-domain', len(groups) == 135 and per_frame == Counter({16: 1260})
          and group_sizes == Counter({105: 16, 150: 112, 240: 7})
          and pair_count == 1539720,
          '135 directions; frame multiplicities 105x16, 150x112, 240x7; 1,539,720 unordered pairs')

    blocks = 0
    group_f2_ranks = Counter()
    scale_hist = Counter()
    scaled_block_f2_ranks = Counter()
    witness_data = None
    for rp, ss in groups.items():
        if len(ss) < 2:
            continue
        M0, T0 = correction_block(ss[0], rp, selected, ip, images, beta)
        pivots = row_pivots(M0)
        if len(pivots) != 8:
            raise ValueError('baseline correction block does not have rational rank 8')
        P0 = [[M0[i][j] for j in pivots] for i in range(8)]
        invP0 = inverse(P0)
        union_coeffs = []
        family_coeffs = []
        common_scale = 1
        for S in ss:
            M, T = correction_block(S, rp, selected, ip, images, beta)
            if len(T) not in (48, 52, 56):
                raise ValueError('unexpected correction target size')
            # M = C M0, with C computed from the fixed pivot minor.  This is an
            # exact rational row-space test and an explicit factorization.
            C = matmul([[M[i][j] for j in pivots] for i in range(8)], invP0)
            scale_s = 1
            for row in C:
                for x in row:
                    scale_s = scale_s * x.denominator // gcd(scale_s, x.denominator)
            Ds = [[int(x * scale_s) for x in row] for row in C]
            if matmul(Ds, M0) != [[v * scale_s for v in row] for row in M] or qrank(Ds) != 8:
                raise ValueError('exact shared rank-8 factorization failed')
            for row in C:
                for x in row:
                    common_scale = common_scale * x.denominator // gcd(common_scale, x.denominator)
            family_coeffs.append((Ds, scale_s, M))
            blocks += 1
            if witness_data is None and tuple(rp) == tuple(CERT['witness']['r_bits']) \
                    and tuple(S) == tuple(CERT['witness']['frames'][1]):
                witness_data = (rp, tuple(S), tuple(T), M, Ds, scale_s, M0, pivots)
        scale_hist[common_scale] += 1
        for Ds, scale_s, M in family_coeffs:
            D = [[x * (common_scale // scale_s) for x in row] for row in Ds]
            if matmul(D, M0) != [[v * common_scale for v in row] for row in M]:
                raise ValueError('scaled shared-basis reconstruction failed')
            scaled_block_f2_ranks[f2rank(D)] += 1
            union_coeffs.extend(D)
        shared_f2 = f2rank(union_coeffs)
        group_f2_ranks[shared_f2] += 1

    check('shared-correction-census', blocks == 20160 and scale_hist == Counter({2: 135})
          and group_f2_ranks == Counter({4: 135}),
          '20,160 rank-8 blocks; per-direction common Q basis; scale lcm %s; family F2 ranks %s; scaled block F2 ranks %s'
          % (dict(scale_hist), dict(group_f2_ranks), dict(scaled_block_f2_ranks)))
    check('witness-factorization', witness_data is not None,
          'certificate names two distinct frames with the same r; M_i = C_i M_0 checked entrywise')

    if witness_data is not None:
        rp, S2, T2, M2, D2s, scale2, M0, pivots = witness_data
        S1 = tuple(CERT['witness']['frames'][0])
        M1, T1 = correction_block(S1, rp, selected, ip, images, beta)
        invP0 = inverse([[M0[i][j] for j in pivots] for i in range(8)])
        C1 = matmul([[M1[i][j] for j in pivots] for i in range(8)], invP0)
        scale1 = 1
        for row in C1:
            for x in row:
                scale1 = scale1 * x.denominator // gcd(scale1, x.denominator)
        D1 = [[int(x * scale1) for x in row] for row in C1]
        assert matmul(D1, M0) == [[x * scale1 for x in row] for row in M1]
        pair_scale = scale1 * scale2 // gcd(scale1, scale2)
        D1 = [[x * (pair_scale // scale1) for x in row] for row in D1]
        D2 = [[x * (pair_scale // scale2) for x in row] for row in D2s]
        pair_f2 = f2rank(D1 + D2)
        if S1 == S2 or pair_f2 > 4:
            raise ValueError('witness pair does not fit the shared F2 rank-4 coefficient space')
        # A one-entry coefficient mutation is a meaningful failure control.
        bad = [row[:] for row in D2]
        bad[0][0] += 1
        check('factorization-negative-control', matmul(bad, M0) != [[x * pair_scale for x in row] for row in M2],
              'one changed coefficient is detected by exact reconstruction')

    # Favorable moment screen: the two upgrades create 8/7 unpaid coordinates per
    # family; one shared rank-8/rank-4 correction is charged as +8 centre units.
    ceiling = load_module('local_word_ceiling', ROOT / 'research/complex-local-word-ceiling/ceiling.py')
    local = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
    a_star = Q(35491136290869, 20000000000000000)  # 1.05 * selected a_hi
    shared = ceiling.relax(local, 73, 896, 9, 72, a_star, unpaid=Q(8, 7))
    one_frame = ceiling.relax(local, 73, 896, 9, 72, a_star, unpaid=Q(15, 14))
    unshared = ceiling.relax(local, 73, 896, 9, 80, a_star, unpaid=Q(8, 7))
    check('favorable-five-percent-screen', shared[1] < 1 and one_frame[0] > 1 and unshared[0] > 1,
          'shared two-frame relaxation %.15f; one-frame %.15f; unshared two-frame %.15f'
          % (float(shared[1]), float(one_frame[0]), float(unshared[0])))

    print('DOMAIN frames=1260 directions=135 pairs=%d correction_blocks=%d' % (pair_count, blocks))
    if witness_data is not None:
        print('FACTOR witness_r=%s frame_sizes=(%d,%d) target_sizes=(%d,%d) q_rank=8 common_scale=%d pair_f2_rank=%d'
              % (''.join(map(str, rp)), len(S1), len(S2), len(T1), len(T2), pair_scale, pair_f2))
    print('PRICE target=%s shared_upper=%s one_frame_lower=%s unshared_lower=%s'
          % (a_star, shared[1], one_frame[0], unshared[0]))
    print('SCOPE No complete supplier, interface charge, restoration, or new kappa is certified.')
    if not FAILS:
        print('PASS_CYCLE47_SHARED_FRAME_CORRECTION: 112 labels; 1260 frames; 1,539,720 pairs; 20,160 exact factorizations; time %.1fs'
              % (time.monotonic() - started))
    raise SystemExit(1 if FAILS else 0)


if __name__ == '__main__':
    main()
