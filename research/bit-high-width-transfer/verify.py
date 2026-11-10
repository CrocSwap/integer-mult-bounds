#!/usr/bin/env python3
"""Exact width-transfer controls; @CubeJerry/OpenAI assistance, Apache-2.0.

Finite controls corroborate PROOF.md; --full-census replays the inherited base.
"""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
from random import Random
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('retained_compress', HERE/'frozen/compression/compress.py')
CORE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CORE)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def neg(a):
    return tuple(-x for x in a)


def identity(n):
    return sum(1 << (i*n+i) for i in range(n))


def multiply(left, right, n):
    """Dense bit-entry binary matrix product, independent of retained code."""
    out = 0
    for i in range(n):
        for j in range(n):
            entry = 0
            for h in range(n):
                entry ^= ((left >> (i*n+h)) & 1) & ((right >> (h*n+j)) & 1)
            out |= entry << (i*n+j)
    return out


def full_endpoint(calls, n):
    """Expand all coefficient matrices, retaining every dirty-input column."""
    require(calls and n >= 1, 'positive word and scalar width required')
    dim = len(calls[0][0])
    zero = (0,)*dim
    out = {zero: identity(n)}
    for a, x, y in calls:
        require(len(a) == dim and a != zero, 'nonzero compatible address')
        require(0 < x < 1 << n and 0 < y < 1 << n and (x & y).bit_count() % 2,
                'legal rank-one scalar idempotent')
        N = sum(1 << (i*n+j) for i in range(n) for j in range(n)
                if (x >> i) & 1 and (y >> j) & 1)
        new = {}
        for exponent, matrix in out.items():
            product = multiply(matrix, N, n)
            new[exponent] = new.get(exponent, 0) ^ matrix ^ product
            shifted = tuple(p+q for p, q in zip(exponent, a))
            new[shifted] = new.get(shifted, 0) ^ product
        out = {e: m for e, m in new.items() if m}
    mask = identity(n)
    require(all(not (m & ~mask) for m in out.values()), 'whole endpoint must be diagonal')
    endpoints = []
    for i in range(n):
        terms = [e for e, m in out.items() if (m >> (i*n+i)) & 1]
        require(len(terms) == 1, 'every diagonal endpoint must be one monomial')
        endpoints.append(terms[0])
    return endpoints


def high_count(frames, endpoints):
    low = {(0,)*len(frames[0]), *frames, *(neg(a) for a in frames)}
    return sum(c not in low for c in endpoints)


def restrict_image(ordered, t):
    """Independent constructor: retain the span of call images, not paired rank."""
    basis, coordinates = [], {0: 0}
    for _, x, _ in ordered:
        v = x >> t
        if v not in coordinates:
            bit = 1 << len(basis)
            basis.append(v)
            coordinates.update({old ^ v: coeff ^ bit for old, coeff in list(coordinates.items())})
    mask = (1 << t)-1
    calls = []
    for a, x, y in ordered:
        xx = (x & mask) | (coordinates[x >> t] << t)
        yy = (y & mask) | (sum(((v & (y >> t)).bit_count()%2) << i
                              for i, v in enumerate(basis)) << t)
        calls.append((a, xx, yy))
    return calls, len(basis)


def reduce_diagonal(calls, n):
    endpoints = full_endpoint(calls, n)
    zero = (0,)*len(calls[0][0])
    active = [i for i, c in enumerate(endpoints) if c != zero]
    inactive = [i for i, c in enumerate(endpoints) if c == zero]
    permutation = active + inactive
    def rearrange(v):
        return sum(((v >> old) & 1) << new for new, old in enumerate(permutation))
    ordered = [(a, rearrange(x), rearrange(y)) for a, x, y in calls]
    direct, direct_w = restrict_image(ordered, len(active))
    require(len(active)+direct_w <= len(calls), 'independent image-span width')
    direct_endpoint = [endpoints[i] for i in active]+[zero]*direct_w
    require(full_endpoint(direct, len(active)+direct_w) == direct_endpoint, 'image restriction full endpoint')
    small, w = CORE.compress_calls(ordered, len(active), n)
    width = len(active) + w
    expected = [endpoints[i] for i in active] + [zero]*w
    require(full_endpoint(small, width) == expected, 'all compressed endpoint blocks')
    require([a for a, _, _ in small] == [a for a, _, _ in calls], 'same ordered frames')
    require(len(active) <= len(calls) and w <= (len(calls)-len(active))//2,
            'rank bound and compression surplus')
    require(width <= len(calls), 'call-count scalar width')
    mask = (1 << len(active))-1
    for (_, x, y), (_, xx, yy) in zip(ordered, small):
        require((x & mask, y & mask) == (xx & mask, yy & mask), 'active data components')
    for i in range(len(calls)):
        for j in range(len(calls)):
            require((ordered[i][2] & ordered[j][1]).bit_count()%2 ==
                    (small[i][2] & small[j][1]).bit_count()%2, 'all scalar pairings')
            require((ordered[i][2] & ordered[j][1]).bit_count()%2 ==
                    (direct[i][2] & direct[j][1]).bit_count()%2, 'image restriction pairings')
    high = high_count([a for a, _, _ in calls], endpoints)
    require(high == high_count([a for a, _, _ in small], expected), 'high count with multiplicity')
    return {'calls': len(calls), 'original_width': n, 'nonidentity': len(active),
            'compressed_width': width, 'compressed_helpers': w, 'high': high}, small


def coord(frame, role):
    return frame, 1 << role, 1 << role


E11, E22, E12 = (1, 0, 0, 0), (0, 0, 0, 1), (0, 1, 0, 0)
ZERO = (0, 0, 0, 0)


def controls():
    records = []
    rec, small = reduce_diagonal([coord(E11, 7)], 9)
    require(rec['compressed_width'] == 1 and full_endpoint(small, 2) == [E11, ZERO],
            'width-one case pads into width-two census')
    records.append(rec)
    identity_calls = [(a, 0b101, 0b110) for a in [E11]*4+[(-4, 0, 0, 0)]]
    rec, _ = reduce_diagonal(identity_calls, 8)
    require((rec['nonidentity'], rec['compressed_width']) == (0, 1), 'all-identity width-one case')
    records.append(rec)
    frames = [E11, E22, E11, E22, E12]
    require(all(a != ZERO and a[0]*a[3] == a[1]*a[2] for a in frames), 'rank-one realization')
    require(len(set(frames)) == 3 and {E11, E22, E12} == set(frames), 'independent matrix units')
    for n, roles in [(3, (0, 1, 2)), (8, (7, 2, 5)), (13, (10, 1, 12))]:
        calls = [coord(a, role) for a, role in zip(frames, [roles[0]]*2+[roles[1]]*2+[roles[2]])]
        rec, _ = reduce_diagonal(calls, n)
        require((rec['nonidentity'], rec['high'], rec['compressed_width']) == (3, 2, 3),
                'sharpness and permutation promotion')
        records.append(rec)
    # A binary change of basis within equal endpoint roles makes the paid
    # scalar projectors noncoordinate while preserving the full endpoint.
    calls = [(E11, 1, 3), (E22, 1, 3), (E11, 3, 2), (E22, 3, 2), coord(E12, 2)]
    rec, _ = reduce_diagonal(calls, 9)
    require((rec['nonidentity'], rec['high']) == (3, 2), 'noncoordinate sharpness word')
    records.append(rec)
    rec, _ = reduce_diagonal([coord(E11, 0), coord(E22, 6)], 8)
    require((rec['nonidentity'], rec['compressed_width']) == (2, 2), 'promote nonidentity dirty output')
    records.append(rec)
    rec, _ = reduce_diagonal([coord(a, i*2) for i, a in enumerate(frames)], 10)
    require((rec['nonidentity'], rec['compressed_width'], rec['high']) == (5, 5, 0), 'width five retained')
    records.append(rec)
    calls = [(E11, 0b10101, 0b00110), (E22, 0b11000, 0b10001),
             (neg(E22), 0b11000, 0b10001), (neg(E11), 0b10101, 0b00110)]
    rec, _ = reduce_diagonal(calls, 7)
    require(rec['nonidentity'] == 0 and rec['compressed_width'] <= 2, 'empty data block')
    records.append(rec)
    calls = [coord(a, role) for role in range(3) for a in (E11, E22)]
    rec, _ = reduce_diagonal(calls, 9)
    require(rec['high'] == 3 and rec['calls'] == 6, 'six-call detector must fire')
    records.append(rec)
    rng = Random(2026110608)
    for trial in range(32):
        n = 5 + trial%5
        calls = [coord(E11, rng.randrange(n))]
        nest = []
        for frame in (E22, E12):
            x, y = rng.randrange(1, 1 << n), rng.randrange(1, 1 << n)
            while not (x & y).bit_count()%2:
                y = rng.randrange(1, 1 << n)
            nest.append((frame, x, y))
        calls += nest + [(neg(a), x, y) for a, x, y in reversed(nest)]
        rec, _ = reduce_diagonal(calls, n)
        require(rec['nonidentity'] == 1 and rec['compressed_width'] <= 3, 'nested inverse width')
        records.append(rec)
    rejected = []
    def reject(name, action):
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('control accepted: '+name)
    reject('nondiagonal_dirty_block', lambda: reduce_diagonal([(E11, 1, 3)], 2))
    reject('zero_frame', lambda: reduce_diagonal([coord(ZERO, 0)], 2))
    reject('invalid_scalar_idempotence', lambda: reduce_diagonal([(E11, 1, 2)], 2))
    broken = [coord(E11, 0), (E22, 3, 5), (E22, 3, 5)]
    reject('missing_helper_restoration', lambda: reduce_diagonal(broken, 3))
    require(high_count([E11], [neg(E11), E11, ZERO]) == 0, 'signed-frame low classes')
    wrong = [coord(E11, 0), coord(E22, 1)]
    _, w = CORE.compress_calls(wrong, 1, 2)
    require(w == 1 > (len(wrong)-1)//2, 'false restoration premise violates surplus bound')
    return records, rejected


def source_checks():
    manifest = json.loads((HERE/'ORIGINS.json').read_text())
    for row in manifest['files']:
        data = (HERE/row['local_path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256 '+row['local_path'])
        gitsha = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        require(gitsha == row['git_blob'], 'source Git blob '+row['local_path'])
    certificate = json.loads((HERE/'frozen/census/CERTIFICATE.json').read_text())['rows']
    for n in range(2, 6):
        for mode in ('rank2', 'rank_le_1'):
            row = certificate[f'W{n}_{mode}']
            require(row['candidates'] == 0 and max(map(int, row['high_hist'])) <= 2,
                    'finite source row covers width '+str(n))
    return len(manifest['files'])


def main():
    started = time.monotonic()
    sources = source_checks()
    records, rejected = controls()
    summary = {'cases': len(records), 'rejection_controls': rejected, 'source_files': sources,
               'width_distribution': dict(sorted(Counter(r['compressed_width'] for r in records).items())),
               'full_census_replayed': '--full-census' in sys.argv}
    if '--full-census' in sys.argv:
        subprocess.run([sys.executable, '-I', '-B', str(HERE/'frozen/census/verify.py'), '--long'], check=True)
    print('PASS_DIAGONAL_WIDTH_TRANSFER '+json.dumps(summary, sort_keys=True))
    print('elapsed_seconds='+str(round(time.monotonic()-started, 3)))


if __name__ == '__main__':
    main()
