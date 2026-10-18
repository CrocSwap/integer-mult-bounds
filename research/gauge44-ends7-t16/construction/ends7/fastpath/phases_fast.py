# Same driver as pr558/code/phases_full.py (sha a273c325...) with PR1029's exact sparse state evaluator.
"""Exact phase-aware lowering of every used edge; sparse exact state evaluation (PR1029).

Usage (same positional arguments as phases_full.py, plus the PR662 gate-table module):
  phases_fast.py LOCAL_DIR CLIFFORD_DIR FAST_STATE_PY [JOBS]
JOBS > 1 schedules edges and adapters over worker processes (as PR1041 phases_parallel.py) and collects them in
the serial order; each worker rebuilds the same frame ops and keeps every per-edge assertion.
The frame, edge and adapter loop, every assertion, and the output serialization are those of phases_full.py.
Only the state evaluator passed to the retained lowering routine differs (PR1029 lowering.py / sparse_state.py).
"""
import gzip, hashlib, importlib.util, json, multiprocessing as mp, sys, time
from collections import Counter
from pathlib import Path

if not __debug__:
    raise RuntimeError('Assertions must remain enabled')
HERE = Path(__file__).resolve().parent
PINS = {  # pinned bytes: PR1029 SOURCES.json (algebra, PR662 tables) and PR1029 head ff4d7b9a (lowering, sparse)
    'clifford_exact.py': '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
    'fast_state.py': '2fe087ba4558bd21ca49945dbedaa4047e4170e8fd4e2280701bb2f0481811b5',
    'lowering.py': 'ba42903b841722b872f98f3afa77d47976ca66a0cb4c0dd6b8de04462d4baa2b',
    'sparse_state.py': 'e91210ecd5085cf9add872f40bb434806838da488e12152c63c86e51fb5a7a37',
}


def load(path, name):
    path = Path(path).resolve()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == PINS[path.name], 'pinned source changed: ' + str(path)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod)
    return mod


A = tables = lowering = sparse = WORD = OPS = None


def setup(clifford_dir, fast_state):
    global A, tables, lowering, sparse
    A = load(Path(clifford_dir) / 'clifford_exact.py', 'clifford_exact')
    tables = load(fast_state, 'pr662_fast_state')
    lowering = load(HERE / 'lowering.py', 'pr1029_lowering')
    sparse = load(HERE / 'sparse_state.py', 'pr1029_sparse_state')


def lower_child(op):
    return lowering.lower_child(op, A, lambda o: sparse.zero_state(o, tables))


def frame_ops(c, check):
    n = c['h']; ops = []
    for U in c['frames']:
        op = A.canonical_frame(n, U)
        if check:
            L = [u | (u << n) for u in U] + [v << n for v in A.nullspace(U, n)]
            pre = [x | (z << n) for x, z, p in A.inverse(op.tab)[n:]]
            assert A.rank(L) == n and A.rank(L + pre) == n
            assert A.rank([x for x, z, p in op.tab[n:]]) == len(U)
        ops.append(op)
    return ops


def init_worker(clifford_dir, fast_state, word_path):
    global WORD, OPS
    setup(clifford_dir, fast_state); WORD = json.load(gzip.open(word_path)); OPS = frame_ops(WORD, check=False)


def edge_task(ab):
    a, b = ab
    rec, compiled = lower_child(OPS[a].adjoint().then(OPS[b]))
    assert rec['rank'] == abs(len(WORD['frames'][a]) - len(WORD['frames'][b]))
    return {'old': a, 'new': b, **rec}


def adapter_task(item):
    i, role = item; c = WORD; n = c['h']; q = c['ports'][i]
    old, f = ((A.cgate(n, q), c['start'][i]) if role == 'source' else
              (A.cgate(n, q).adjoint().then(A.fourier(n)), c['final'][c['v'] + i]))
    rec, compiled = lower_child(old.adjoint().then(OPS[f])); assert rec['rank'] == 0
    return {'port': i, 'role': role, 'frame': f, **rec}


def main():
    OUT = Path(sys.argv[1]); P = OUT / 'CANONICAL-WORD.json.gz'
    jobs = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    setup(sys.argv[2], sys.argv[3])
    c = json.load(gzip.open(P)); frames = c['frames']; start = time.monotonic()
    frame_ops(c, check=True)
    edges = set(map(tuple, c['edges'])) | {(a, b) for f in c['center_frames'] for a, b in ((f, 0), (0, f))}
    items = [(i, role) for i in range(len(c['ports'])) for role in ('source', 'target')]
    if jobs == 1:
        init_worker(sys.argv[2], sys.argv[3], P)
        recipes = []
        for i, e in enumerate(sorted(edges)):
            recipes.append(edge_task(e))
            if i % 200 == 0: print('exact phase edges', i, '/', len(edges), 'seconds', time.monotonic() - start, flush=True)
        adapters = [adapter_task(x) for x in items]
    else:
        ctx = mp.get_context('spawn')
        if sys.platform == 'win32':  # windowless workers: spawn console python.exe can open a visible console
            # base interpreter: a venv pythonw.exe launcher re-spawns and breaks the inherited pool pipe
            w = Path(getattr(sys, '_base_executable', sys.executable)).with_name('pythonw.exe')
            if w.exists(): ctx.set_executable(str(w))
        with ctx.Pool(jobs, initializer=init_worker, initargs=(sys.argv[2], sys.argv[3], str(P))) as pool:
            recipes = pool.map(edge_task, sorted(edges), chunksize=16)
            adapters = pool.map(adapter_task, items, chunksize=8)
    hist = Counter(r['rank'] for r in recipes)
    raw = json.dumps({'children': recipes, 'endpoint_adapters': adapters}, sort_keys=True, separators=(',', ':')).encode()
    (OUT / 'CLIFFORD-RECIPES.json').write_bytes(raw)
    result = {'status': 'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES',
              'canonical_word_sha256': hashlib.sha256(P.read_bytes()).hexdigest(),
              'frames': len(frames), 'directed_edges': len(edges), 'ranks': dict(hist),
              'endpoint_adapters': len(adapters), 'all_child_equalities_include_global_phase': True,
              'recipe_sha256': hashlib.sha256(raw).hexdigest(), 'seconds': time.monotonic() - start,
              'scope': 'Every local frame and center transition. Expanded scalar-interface integration and global emitted program are separate obligations.'}
    (OUT / 'CLIFFORD-REVIEW.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS exact local phases', result['seconds'], 'seconds', flush=True)


if __name__ == '__main__':
    main()
