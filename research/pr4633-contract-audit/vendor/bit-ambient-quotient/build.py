#!/usr/bin/env python3
"""Build a quotient of the BIT local word by a kernel subspace. Apache-2.0.

The BIT supplier's local word is PR589's E8 word: `h = 8`, `V = 111` roles per
side, `R = 439` helpers, 661 roles, 636 frames and 249 records.  Frames are
stored by annihilator rows, so a frame is the GF(2) nullspace of its rows.

For a kernel subspace `K` of dimension `k` the linear map

    phi : F2^8 -> F2^(8-k),   phi(x) = (r_1.x, ..., r_(8-k).x)

over a basis `r` of the annihilator of `K` is surjective with kernel exactly `K`.
It shrinks exactly the frames meeting `K`, so a MOVE whose destination meets `K`
more than its source does loses that many ranks.  Frames with the same image are
identified, the helper finals are restored to the full F2^8 (the contract requires
every helper to be physically `D_I8` and the tensor block to stay 7), and every
MOVE rank is recomputed from the new dimensions.

The kernel is chosen by replay, not arithmetic: `scan_kernels.py` builds, replays
and prices the candidates.  One dimension gives 0.0124, two give 0.0218, three give
0.0322, and four fall back to 0.0175.

    python3 -B build.py
"""
import gzip
import json
import struct
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT/'research/kappa-rebuild/bit/sources/pr589-regenerated'
V, R, H = 111, 439, 8
ROLES = 2*V+R
KERNEL_BASIS = (150, 102, 255)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def mask(row):
    return sum((row[j] & 1) << j for j in range(H))


def frame_vectors(annihilator):
    rows = [mask(r) for r in annihilator]
    return [x for x in range(1 << H)
            if all(bin(r & x).count('1') % 2 == 0 for r in rows)]


def rref(rows):
    piv = {}
    for r in [x for x in rows if x]:
        y = r
        for p in sorted(piv, reverse=True):
            if y >> p & 1:
                y ^= piv[p]
        if y:
            piv[y.bit_length()-1] = y
    return [piv[p] for p in sorted(piv)]


def annihilator(kernels):
    """Basis of {r : r . k = 0 for every k in the kernel basis}."""
    basis = rref(kernels)
    pivots = {b.bit_length()-1 for b in basis}
    out = []
    for f in [j for j in range(H) if j not in pivots]:
        v = 1 << f
        for b in basis:
            if bin(b & v).count('1') & 1:
                v |= 1 << (b.bit_length()-1)
        out.append(v)
    return out


def span_of(vectors):
    out = {0}
    for v in vectors:
        out |= {x ^ v for x in out}
    return frozenset(out)


def dedupe(vectors):
    pivots, keep = {}, []
    for v in vectors:
        y = v
        while y:
            b = y.bit_length()-1
            if b in pivots:
                y ^= pivots[b]
            else:
                pivots[b] = y
                keep.append(v)
                break
    return keep


def build(kernels=KERNEL_BASIS):
    kernels = list(kernels)
    need(len(rref(kernels)) == len(kernels), 'kernel basis must be independent')
    width = H-len(kernels)
    rows = annihilator(kernels)
    need(len(rows) == width, 'annihilator dimension')

    def phi(x):
        return sum((bin(r & x).count('1') & 1) << i for i, r in enumerate(rows))

    word = json.load(gzip.open(SOURCE/'WORD.json.gz'))
    need((word['h'], word['v'], word['R']) == (H, V, R), 'Pinned local type')
    frames_raw = json.loads((SOURCE/'records/frames.json').read_text())['frames']
    records = list(struct.iter_unpack('<6i', (SOURCE/'records/249-records.bin').read_bytes()))
    need(len(word['start']) == ROLES, 'role count')

    vectors = {int(k): frame_vectors(v['A']) for k, v in frames_raw.items()}
    need(len(vectors[1]) == 1 << H, 'frame 1 is the full ambient')

    table, table_dim, table_basis = {}, {}, []

    def index_of(mapped):
        basis = dedupe(mapped)
        key = span_of(basis)
        if key not in table:
            table[key] = len(table)
            table_dim[table[key]] = len(key).bit_length()-1
            table_basis.append(sorted(basis))
        return table[key]

    image = {f: index_of([phi(x) for x in vectors[f]]) for f in vectors}

    # The full ambient meets every kernel direction, so its image is (8-k)-
    # dimensional.  Restore it: the frame becomes the whole of F2^8 again, so
    # every role that ended there ends there again and helper ranks are preserved.
    full_image = image[1]
    base = next(key for key, idx in table.items() if idx == full_image)
    freed = [1 << j for j in range(width, H)]
    extras = [sum(1 << (width+i) for i in bits) for bits in _subsets(len(freed))]
    pad_key = frozenset(x | e for x in base for e in extras)
    need(len(pad_key) == 1 << H, 'padded frame must be the full ambient')
    if pad_key not in table:
        table[pad_key] = len(table)
        table_dim[table[pad_key]] = H
        table_basis.append([1 << i for i in range(H)])
    pad_index = table[pad_key]
    for f in image:
        if image[f] == full_image:
            image[f] = pad_index

    start = [image[s] for s in word['start']]
    final = [image[f] for f in word['final']]

    rewritten = []
    for op, x, y, c, f, z in records:
        if op == 0:
            old, new = image[y], image[c]
            rewritten.append([op, x, old, new, table_dim[new]-table_dim[old], z])
        elif op == 1:
            rewritten.append([op, x, y, c, image[f], z])
        else:
            rewritten.append([op, x, y, image[c], image[f], z])

    helpers = list(range(2*V, ROLES))
    need(all(table_dim[final[r]] == H for r in helpers), 'helper finals must be D_I8')
    need(all(table_dim[start[r]] == 0 for r in helpers), 'helper starts must be ground')

    mains = Counter(table_dim[final[r]]-table_dim[start[r]] for r in range(2*V))
    return {'kernel_basis': kernels, 'ambient_dim': H, 'quotient_width': width,
            'roles': ROLES, 'pairs': V, 'helpers': R,
            'source_frames': len(vectors), 'frames': len(table),
            'frame_dims': table_dim, 'frame_bases': table_basis,
            'start': start, 'final': final,
            'records': rewritten,
            'main_widths': {str(k): v for k, v in sorted(mains.items())},
            'main_rank_mass': sum(k*v for k, v in mains.items()),
            'helper_rank_mass': sum(table_dim[final[r]]-table_dim[start[r]]
                                    for r in helpers),
            'source_word_sha256': sha256((SOURCE/'WORD.json.gz').read_bytes()).hexdigest()}


def _subsets(n):
    return [[j for j in range(n) if i >> j & 1] for i in range(1 << n)]


def main():
    artifact = build()
    print('kernel %s  frames %d -> %d  roles %d'
          % (artifact['kernel_basis'], artifact['source_frames'],
             artifact['frames'], ROLES))
    print('frame dims %s' % dict(sorted(Counter(artifact['frame_dims'].values()).items())))
    print('main widths %s (mass %d)'
          % (artifact['main_widths'], artifact['main_rank_mass']))
    print('helper rank mass %d' % artifact['helper_rank_mass'])
    with open(HERE/'QUOTIENT-BIT-WORD.json.gz', 'wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as handle:
            handle.write(json.dumps(artifact, sort_keys=True).encode())
    print('wrote QUOTIENT-BIT-WORD.json.gz')


if __name__ == '__main__':
    main()
