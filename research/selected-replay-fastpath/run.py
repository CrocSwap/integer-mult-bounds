#!/usr/bin/env python3
"""Compile every local frame, edge and endpoint of a canonical word exactly."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import time

import lowering
from sources import engines
import sparse_state


def run(word, out, engine):
    algebra, dense = engines()
    if out.exists():
        raise ValueError('Use a fresh output directory')
    raw_word = word.read_bytes()
    canonical = json.loads(gzip.decompress(raw_word))
    if engine == 'reference':
        lower = algebra.lower_child
    else:
        evaluate = (dense.zero_state if engine == 'dense' else
                    lambda op: sparse_state.zero_state(op, dense))
        lower = lambda op: lowering.lower_child(op, algebra, evaluate)
    n, frames = canonical['h'], canonical['frames']
    start = time.monotonic()
    ops = []
    for U in frames:
        op = algebra.canonical_frame(n, U)
        L = [u | (u << n) for u in U] + [v << n for v in algebra.nullspace(U, n)]
        pre = [x | (z << n) for x, z, p in algebra.inverse(op.tab)[n:]]
        assert algebra.rank(L) == n and algebra.rank(L + pre) == n
        assert algebra.rank([x for x, z, p in op.tab[n:]]) == len(U)
        ops.append(op)
    edges = set(map(tuple, canonical['edges'])) | {
        edge for f in canonical['center_frames'] for edge in ((f, 0), (0, f))}
    recipes, hist = [], Counter()
    for a, b in sorted(edges):
        rec, _ = lower(ops[a].adjoint().then(ops[b]))
        assert rec['rank'] == abs(len(frames[a]) - len(frames[b]))
        hist[rec['rank']] += 1
        recipes.append({'old': a, 'new': b, **rec})
    adapters, F = [], algebra.fourier(n)
    for i, q in enumerate(canonical['ports']):
        for role, old, f in [
            ('source', algebra.cgate(n, q), canonical['start'][i]),
            ('target', algebra.cgate(n, q).adjoint().then(F),
             canonical['final'][canonical['v'] + i]),
        ]:
            rec, _ = lower(old.adjoint().then(ops[f]))
            assert rec['rank'] == 0
            adapters.append({'port': i, 'role': role, 'frame': f, **rec})
    raw = json.dumps({'children': recipes, 'endpoint_adapters': adapters},
                     sort_keys=True, separators=(',', ':')).encode()
    result = dict(
        status='PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES',
        canonical_word_sha256=hashlib.sha256(raw_word).hexdigest(),
        frames=len(frames), directed_edges=len(edges), ranks=dict(hist),
        endpoint_adapters=len(adapters), all_child_equalities_include_global_phase=True,
        recipe_sha256=hashlib.sha256(raw).hexdigest(), seconds=time.monotonic()-start,
        scope='Every local frame and center transition. Expanded scalar-interface integration '
              'and global emitted program are separate obligations.')
    out.mkdir(parents=True)
    (out / 'CLIFFORD-RECIPES.json').write_bytes(raw)
    (out / 'CLIFFORD-REVIEW.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS exact local phases', result['seconds'], 'seconds', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--engine', choices=('reference', 'dense', 'sparse'), default='sparse')
    args = parser.parse_args()
    run(args.word, args.out, args.engine)
