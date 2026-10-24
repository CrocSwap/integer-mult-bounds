#!/usr/bin/env python3
"""Build a one-dimensional ambient quotient of the BIT local word. Apache-2.0.

The BIT supplier's local word is PR589's E8 word: `h = 8`, `V = 111` roles per
side, `R = 439` helpers, 661 roles, 636 frames and 249 records.  Frames are
stored by annihilator rows, so a frame is the GF(2) nullspace of its rows.

For a nonzero kernel `v` with lowest set bit `j` the map

    phi(x) = drop_j( x xor v when bit_j(x) is set else x )

is linear and surjective onto F2^7 with kernel `span{v}`.  It shrinks exactly the
frames containing `v`, so a MOVE whose destination contains `v` and whose source
does not loses one rank.  Frames with the same image are identified, the helper
finals are restored to the full F2^8 (the contract requires every helper to be
physically `D_I8` and the tensor block to stay 7), and every MOVE rank is
recomputed from the new dimensions.

    python3 -B build.py
"""
import gzip
import json
import struct
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT/'research/kappa-rebuild/bit/sources/pr589-regenerated'
V, R, H = 111, 439, 8
ROLES = 2*V+R
KERNEL = 150
PIVOT = (KERNEL & -KERNEL).bit_length()-1
PAD_AXIS = 0x80


def need(ok, message):
    if not ok:
        raise ValueError(message)


def mask(row):
    return sum((row[j] & 1) << j for j in range(8))


def frame_vectors(annihilator):
    rows = [mask(r) for r in annihilator]
    return [x for x in range(1 << H)
            if all(bin(r & x).count('1') % 2 == 0 for r in rows)]


def phi(x):
    if (x >> PIVOT) & 1:
        x ^= KERNEL
    return (x & ((1 << PIVOT)-1)) | ((x >> (PIVOT+1)) << PIVOT)


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


def build(kernel=KERNEL):
    global KERNEL, PIVOT
    KERNEL, PIVOT = kernel, (kernel & -kernel).bit_length()-1
    word = json.load(gzip.open(SOURCE/'WORD.json.gz'))
    need((word['h'], word['v'], word['R']) == (H, V, R), 'Pinned local type')
    frames_raw = json.loads((SOURCE/'records/frames.json').read_text())['frames']
    records = list(struct.iter_unpack('<6i', (SOURCE/'records/249-records.bin').read_bytes()))
    need(len(word['start']) == ROLES, 'role count')

    vectors = {int(k): frame_vectors(v['A']) for k, v in frames_raw.items()}
    dims = {f: len(vectors[f]).bit_length()-1 for f in vectors}
    need(dims[1] == H, 'frame 1 is the full ambient')

    table, table_dim = {}, {}

    def index_of(mapped):
        key = span_of(dedupe(mapped))
        if key not in table:
            table[key] = len(table)
            table_dim[table[key]] = len(key).bit_length()-1
        return table[key]

    image = {f: index_of([phi(x) for x in vectors[f]]) for f in vectors}

    # The full ambient contains every vector, so its image is 7-dimensional.
    # Restore it: the frame is the whole of F2^8 again, so every role that ended
    # there ends there again, helper ranks are preserved and the block stays 7.
    full_image = image[1]
    base = next(key for key, idx in table.items() if idx == full_image)
    pad_key = frozenset(base | {x | PAD_AXIS for x in base})
    need(len(pad_key) == 1 << H, 'padded frame must be the full ambient')
    if pad_key not in table:
        table[pad_key] = len(table)
        table_dim[table[pad_key]] = H
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

    helpers = [r for r in range(2*V, ROLES)]
    need(all(table_dim[final[r]] == H for r in helpers), 'helper finals must be D_I8')
    need(all(table_dim[start[r]] == 0 for r in helpers), 'helper starts must be ground')

    mains = Counter(table_dim[final[r]]-table_dim[start[r]] for r in range(2*V))

    artifact = {'source_frames': len(vectors), 'kernel_vector': KERNEL,
                'pivot': PIVOT, 'ambient_dim': H,
                'main_widths': {str(k): v for k, v in sorted(mains.items())},
                'roles': ROLES, 'pairs': V, 'helpers': R,
                'frames': len(table), 'frame_dims': table_dim,
                'start': start, 'final': final, 'records': rewritten,
                'source_word_sha256': None}
    from hashlib import sha256
    artifact['source_word_sha256'] = sha256((SOURCE/'WORD.json.gz').read_bytes()).hexdigest()
    return artifact


def main():
    artifact = build()
    print('kernel %d  frames %d -> %d  roles %d'
          % (artifact['kernel_vector'], artifact['source_frames'],
             artifact['frames'], ROLES))
    print('frame dims %s' % dict(sorted(Counter(artifact['frame_dims'].values()).items())))
    print('main widths %s' % artifact['main_widths'])
    print('helper dims: start 0, final %d'
          % sorted({artifact['frame_dims'][f] for f in artifact['final']})[-1])
    with open(HERE/'QUOTIENT-BIT-WORD.json.gz', 'wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as handle:
            handle.write(json.dumps(artifact, sort_keys=True).encode())
    print('wrote QUOTIENT-BIT-WORD.json.gz')


if __name__ == '__main__':
    main()
