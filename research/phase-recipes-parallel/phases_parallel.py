# SPDX-License-Identifier: Apache-2.0
"""Opt-in parallel runner for the pinned exact phase lowering (phases_full.py).

Usage: phases_parallel.py OUT_DIR CLIFFORD_DIR [--jobs N] [--engine reference|dense662]

Same arguments and outputs as research/complex-k492-owner-repair/vendor/multicold/
vendor/pr558/code/phases_full.py, which stays the reference. Every frame, directed
edge and endpoint adapter is processed by the unchanged functions of the pinned
clifford_exact.py, with every assertion of the serial loop kept. Only scheduling
differs: edges and adapters are computed in worker processes and collected in the
serial order, so CLIFFORD-RECIPES.json is byte-identical. A failure in any worker
fails the run before any output is written.

--engine dense662 additionally installs the merged PR662 exact state evaluator
(research/clifford-state-performance/fast_state.py, pinned by digest) as
Op.zero_state in every process, exactly as PR662's own run.py does. The default
engine, reference, runs the pinned clifford_exact.py unmodified.
"""
import argparse
import gzip
import hashlib
import json
import multiprocessing as mp
import os
import sys
import time
from collections import Counter
from pathlib import Path

CE = None          # the pinned clifford_exact module (loaded per process)
ROOT = Path(__file__).resolve().parents[2]
DENSE662 = ('research/clifford-state-performance/fast_state.py',
            '2fe087ba4558bd21ca49945dbedaa4047e4170e8fd4e2280701bb2f0481811b5')
WORD = None
OPS = None


def load_clifford(directory, engine='reference'):
    global CE
    sys.path.insert(0, str(Path(directory).resolve()))
    import clifford_exact
    CE = clifford_exact
    if engine == 'dense662':
        import importlib.util
        path = ROOT / DENSE662[0]
        if hashlib.sha256(path.read_bytes()).hexdigest() != DENSE662[1]:
            raise RuntimeError('PR662 fast_state.py digest mismatch')
        spec = importlib.util.spec_from_file_location('fast_state_pr662', path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.clear_caches()
        CE.Op.zero_state = mod.zero_state
    elif engine != 'reference':
        raise ValueError('unknown engine ' + engine)
    return CE


def frame_ops(c, check):
    """The serial frame loop, verbatim in substance; asserts run when check is true."""
    n = c['h']
    ops = []
    for U in c['frames']:
        op = CE.canonical_frame(n, U)
        if check:
            L = [u | (u << n) for u in U] + [v << n for v in CE.nullspace(U, n)]
            pre = [x | (z << n) for x, z, p in CE.inverse(op.tab)[n:]]
            assert CE.rank(L) == n and CE.rank(L + pre) == n
            assert CE.rank([x for x, z, p in op.tab[n:]]) == len(U)
        ops.append(op)
    return ops


def init_worker(clifford_dir, word_path, engine='reference'):
    global WORD, OPS
    load_clifford(clifford_dir, engine)
    WORD = json.load(gzip.open(word_path))
    OPS = frame_ops(WORD, check=False)       # identical deterministic objects; the parent ran the checks


def edge_task(ab):
    a, b = ab
    op = OPS[a].adjoint().then(OPS[b])
    rec, compiled = CE.lower_child(op)
    assert rec['rank'] == abs(len(WORD['frames'][a]) - len(WORD['frames'][b]))
    return {'old': a, 'new': b, **rec}


def adapter_task(item):
    i, role = item
    c, n = WORD, WORD['h']
    q = c['ports'][i]
    if role == 'source':
        old, f = CE.cgate(n, q), c['start'][i]
    else:
        old, f = CE.cgate(n, q).adjoint().then(CE.fourier(n)), c['final'][c['v'] + i]
    rec, compiled = CE.lower_child(old.adjoint().then(OPS[f]))
    assert rec['rank'] == 0
    return {'port': i, 'role': role, 'frame': f, **rec}


def run(out, clifford_dir, jobs, log=print, engine='reference'):
    out = Path(out)
    word_path = out / 'CANONICAL-WORD.json.gz'
    load_clifford(clifford_dir, engine)
    c = json.load(gzip.open(word_path))
    start = time.monotonic()
    frame_ops(c, check=True)
    edges = sorted(set(map(tuple, c['edges'])) | {(a, b) for f in c['center_frames'] for a, b in ((f, 0), (0, f))})
    items = [(i, role) for i in range(len(c['ports'])) for role in ('source', 'target')]
    if jobs == 1:
        init_worker(clifford_dir, word_path, engine)
        recipes = [edge_task(e) for e in edges]
        adapters = [adapter_task(x) for x in items]
    else:
        ctx = mp.get_context('spawn')
        with ctx.Pool(jobs, initializer=init_worker, initargs=(str(clifford_dir), str(word_path), engine)) as pool:
            recipes = []
            for i, rec in enumerate(pool.imap(edge_task, edges, chunksize=8)):
                recipes.append(rec)
                if i % 200 == 0:
                    log('exact phase edges', i, '/', len(edges), 'seconds', time.monotonic() - start)
            adapters = list(pool.imap(adapter_task, items, chunksize=8))
    hist = Counter(r['rank'] for r in recipes)
    raw = json.dumps({'children': recipes, 'endpoint_adapters': adapters}, sort_keys=True, separators=(',', ':')).encode()
    (out / 'CLIFFORD-RECIPES.json').write_bytes(raw)
    result = {'status': 'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES',
              'canonical_word_sha256': hashlib.sha256(word_path.read_bytes()).hexdigest(),
              'frames': len(c['frames']), 'directed_edges': len(edges), 'ranks': dict(hist),
              'endpoint_adapters': len(adapters), 'all_child_equalities_include_global_phase': True,
              'recipe_sha256': hashlib.sha256(raw).hexdigest(), 'seconds': time.monotonic() - start,
              'scope': 'Every local frame and center transition. Expanded scalar-interface integration and global emitted program are separate obligations.'}
    with open(out / 'CLIFFORD-REVIEW.json', 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(result, indent=2) + '\n')
    log('PASS exact local phases', result['seconds'], 'seconds', 'jobs', jobs, 'engine', engine)
    return result


def main():
    if not __debug__:
        raise RuntimeError('assertions must remain enabled')
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('clifford_dir')
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    ap.add_argument('--engine', choices=('reference', 'dense662'), default='reference')
    a = ap.parse_args()
    run(a.out, a.clifford_dir, max(1, a.jobs), log=lambda *x: print(*x, flush=True), engine=a.engine)


if __name__ == '__main__':
    main()
