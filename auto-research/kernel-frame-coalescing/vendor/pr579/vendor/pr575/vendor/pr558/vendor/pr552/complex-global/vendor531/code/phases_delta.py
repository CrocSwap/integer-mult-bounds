"""Reuse the pinned PR523 phase certificates and lower only changed edges.

The inherited Gaussian-dyadic compiler still checks every fresh tableau and
global phase. Its zero-state interpreter is accelerated with cached exact
integer permutations and Z4 phases. Overflow is checked before every sum;
there is no floating-point arithmetic in a phase equality.

Prepared for icekylinx with GPT-6 Astra assistance. Apache-2.0.
Compiler and certificate format: PR425/433, icekylinx with Codex assistance.
"""
import argparse
import copy
import gzip
import hashlib
import json
import sys
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path

import numpy as np


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frozen(x):
    return tuple(map(frozen, x)) if isinstance(x, (list, tuple)) else x


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--local', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--compiler', type=Path, required=True)
    a = p.parse_args()
    sys.path.insert(0, str(a.compiler.resolve()))
    import clifford_exact as ce
    started = time.monotonic()
    assert sha(a.compiler/'clifford_exact.py') == '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962', 'baseline canonical-frame and phase convention must remain pinned'
    c = json.load(gzip.open(a.local/'CANONICAL-WORD.json.gz'))
    b = json.load(gzip.open(a.baseline/'CANONICAL-WORD.json.gz'))
    old = json.loads((a.baseline/'CLIFFORD-RECIPES.json').read_text())
    prior = json.loads((a.baseline/'CLIFFORD-REVIEW.json').read_text())
    assert prior['all_child_equalities_include_global_phase']
    assert prior['recipe_sha256'] == sha(a.baseline/'CLIFFORD-RECIPES.json')
    assert prior['canonical_word_sha256'] == sha(a.baseline/'CANONICAL-WORD.json.gz')
    assert c['h'] == b['h'] == 9 and c['ports'] == b['ports']
    n = c['h']; N = 1 << n
    xs = np.arange(N, dtype=np.int64)
    parity = np.array([x.bit_count() & 1 for x in range(N)], dtype=np.int64)

    @lru_cache(None)
    def action(e):
        if e[0] == 'P':
            return sum(parity[xs & row] << i for i, row in enumerate(e[1]))
        if e[0] == 'D':
            Q, alpha = e[1:]
            phase = np.zeros(N, dtype=np.int64)
            for i in range(n):
                phase += ((xs >> i) & 1) * alpha[i]
                for j in range(i+1, n):
                    if (Q[i] >> j) & 1:
                        phase += 2*((xs >> i) & (xs >> j) & 1)
            return phase % 4
        if e[0] in ('C', 'X'):
            return xs ^ e[1]
        return e[1]

    @lru_cache(maxsize=4096)
    def state(circuit, basis):
        re = np.zeros(N, dtype=np.int64); im = np.zeros(N, dtype=np.int64)
        re[basis] = 1; den = 0
        for e in circuit:
            z = action(e)
            if e[0] == 'P':
                rr = np.empty_like(re); ii = np.empty_like(im)
                rr[z] = re; ii[z] = im; re, im = rr, ii
            elif e[0] == 'X':
                re, im = re[z], im[z]
            elif e[0] in ('D', 'phase'):
                sign = 1 - 2*(z//2)
                odd = z % 2
                re, im = sign*np.where(odd, -im, re), sign*np.where(odd, re, im)
            elif e[0] == 'C':
                assert max(int(np.max(np.abs(re))), int(np.max(np.abs(im)))) < 2**60
                s = e[2]; rr, ii = re[z], im[z]
                re, im = re-s*im+rr+s*ii, im+s*re+ii-s*rr
                den += 1
            else:
                raise AssertionError(e)
            while den and not bool(np.any((re & 1) | (im & 1))):
                re //= 2; im //= 2; den -= 1
        return tuple(zip(map(int, re), map(int, im))), den

    original = ce.Op.zero_state
    # Check the independent vectorized interpreter against the inherited
    # literal one on one nontrivial changed edge and its adjoint, once.
    probe = ce.canonical_frame(n, c['frames'][c['center_frames'][0]])
    probes = (probe, probe.adjoint().then(ce.fourier(n)))
    for op in probes:
        expected, den = original(op)
        got, d = state(frozen(op.circuit), 0)
        assert tuple(expected) == got and den == d
    ce.Op.zero_state = lambda self, basis=0: state(frozen(self.circuit), basis)

    @lru_cache(None)
    def frame(U):
        op = ce.canonical_frame(n, U)
        L = [u | (u << n) for u in U] + [v << n for v in ce.nullspace(U, n)]
        pre = [x | (z << n) for x, z, _ in ce.inverse(op.tab)[n:]]
        assert ce.rank(L) == ce.rank(L+pre) == n
        assert ce.rank([x for x, _, _ in op.tab[n:]]) == len(U)
        return op

    key = lambda frames, x, y: (tuple(frames[x]), tuple(frames[y]))
    known = {key(b['frames'], r['old'], r['new']): r for r in old['children']}
    edges = set(map(tuple, c['edges'])) | {(x,y) for f in c['center_frames'] for x,y in ((f,0),(0,f))}
    recipes = []; hist = Counter(); fresh = []; reused = []
    for i, (x, y) in enumerate(sorted(edges)):
        U, V = key(c['frames'], x, y)
        if (U,V) in known:
            rec = copy.deepcopy(known[U,V]); rec.update(old=x, new=y); reused.append([x,y])
        else:
            rec, _ = ce.lower_child(frame(U).adjoint().then(frame(V)))
            rec = dict(old=x, new=y, **rec); fresh.append([x,y])
        assert rec['rank'] == abs(len(U)-len(V))
        hist[rec['rank']] += 1; recipes.append(rec)
        if i and i % 600 == 0:
            print('delta phases', i, '/', len(edges), 'fresh', len(fresh), 'seconds', round(time.monotonic()-started, 2), flush=True)
    adapters = []
    for r in old['endpoint_adapters']:
        rec = copy.deepcopy(r); port = r['port']
        f = c['start'][port] if r['role'] == 'source' else c['final'][c['v']+port]
        assert tuple(c['frames'][f]) == tuple(b['frames'][r['frame']]) and rec['rank'] == 0
        rec['frame'] = f; adapters.append(rec)
    assert len(adapters) == 2*c['v']
    assert {(r['role'], r['port']) for r in adapters} == {(role, port) for role in ('source', 'target') for port in range(c['v'])}
    payload = json.dumps(dict(children=recipes, endpoint_adapters=adapters), sort_keys=True, separators=(',',':')).encode()
    (a.local/'CLIFFORD-RECIPES.json').write_bytes(payload)
    report = dict(status='PASS_REUSED_AND_FRESH_EXACT_LOCAL_PHASE_RECIPES',
        canonical_word_sha256=sha(a.local/'CANONICAL-WORD.json.gz'), frames=len(c['frames']),
        directed_edges=len(edges), reused_edges=len(reused), fresh_edges=len(fresh),
        ranks=dict(hist), endpoint_adapters=len(adapters), reused_endpoint_adapters=len(adapters),
        all_child_equalities_include_global_phase=True, recipe_sha256=hashlib.sha256(payload).hexdigest(),
        baseline_recipe_sha256=prior['recipe_sha256'], baseline_review_sha256=sha(a.baseline/'CLIFFORD-REVIEW.json'),
        compiler_sha256=sha(a.compiler/'clifford_exact.py'), seconds=time.monotonic()-started,
        vector_arithmetic='Exact checked int64 Gaussian dyadics; cached permutations and Z4 phase actions. No floating-point equality.',
        fresh_edge_ids=fresh,
        scope='Only previously unseen ordered pairs of actual canonical subspaces were freshly lowered. Identical baseline pairs and all endpoint adapters reuse the pinned phase certificates; no full cold replay was performed.')
    (a.local/'CLIFFORD-REVIEW.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','directed_edges','reused_edges','fresh_edges','seconds')},sort_keys=True),flush=True)


if __name__ == '__main__':
    main()
