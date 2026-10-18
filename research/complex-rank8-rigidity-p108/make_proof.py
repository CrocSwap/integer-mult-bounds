#!/usr/bin/env python3
"""Choose the 168 orbit representatives, pivots and cover words, and regenerate UNITS.json, COVER.json and
PROOFS.json.gz, which verify.py replays (needs python-sat, numpy and scipy; verify.py needs none of them).

    python3 -I -B research/complex-rank8-rigidity-p108/make_proof.py --out-dir /new/dir

Orbits of quadruples are labelled with numpy/scipy (connected components of the generator action); this only
proposes the grouping, and verify.py checks every cover word explicitly. Representative: the first candidate
(triple-orbit representative + one line, sorted) of each open orbit. Pivot: the first frame inside the live
set, in line order, that passes (I3), (I4), gluing and Lemma 9 connectivity. Deletion lines are dropped from
the solver's DRUP output (verify.py's checker ignores them anyway).
"""
import argparse
import gzip
import hashlib
import itertools
import json
import sys
from collections import deque
from math import comb
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402


def unit(X):
    from pysat.solvers import Solver
    live = [i for i in V.P112 if i not in X]
    F = next(F for F in V.frames_inside(live) if V.passes(V.inputs(live, F)))
    cnf, zvars = V.build_cnf(live, F)
    with Solver(name='g4', bootstrap_with=cnf.clauses + [zvars], with_proof=True) as s:
        if s.solve():
            raise SystemExit(f'{X}: UNEXPECTED satisfiable')
        proof = [ln for ln in s.get_proof() if not ln.startswith('d')]
    text = '\n'.join(proof) + '\n'
    return F, text, V.cnf_digest(cnf.clauses + [zvars])


def labels(gens):
    import numpy as np
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    pos = {x: n for n, x in enumerate(V.P112)}
    table = np.array([[comb(x, j + 1) for j in range(4)] for x in range(112)], dtype=np.int64)
    subs = np.array(list(itertools.combinations(range(112), 4)), dtype=np.int64)
    rank = lambda a: sum(table[a[:, j], j] for j in range(4))
    inv = np.empty(len(subs), dtype=np.int64)
    inv[rank(subs)] = np.arange(len(subs))
    rows, cols = [], []
    for g in gens:
        p = np.array([pos[g[x]] for x in V.P112])
        rows.append(np.arange(len(subs)))
        cols.append(inv[rank(np.sort(p[subs], axis=1))])
    r, c = np.concatenate(rows), np.concatenate(cols)
    n, lab = connected_components(coo_matrix((np.ones(len(r), dtype=np.int8), (r, c)), shape=(len(subs),) * 2),
                                  directed=False)
    return n, lambda Y: int(lab[inv[rank(np.array([[pos[y] for y in Y]]))][0]])


def words_from(gens, rep, targets):
    parent, todo, left = {rep: None}, deque([rep]), set(targets) - {rep}
    while left:
        Y = todo.popleft()
        for gi, g in enumerate(gens):
            Z = tuple(sorted(g[y] for y in Y))
            if Z not in parent:
                parent[Z] = (Y, gi)
                left.discard(Z)
                todo.append(Z)
    out = {}
    for c in targets:
        w, Y = [], c
        while parent[Y] is not None:
            Y, gi = parent[Y]
            w.append(gi)
        out[c] = w[::-1]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--jobs', type=int, default=8)
    args = ap.parse_args()
    out = Path(args.out_dir)
    for f in ('UNITS.json', 'COVER.json', 'PROOFS.json.gz'):
        if (out / f).exists():
            print(f'refusing to overwrite {out / f}')
            return 2
    gens = V.stabiliser(V.FRAME0)[::V.GEN_STEP]
    inframe = {Y for F in V.frames_inside(V.P112) for Y in itertools.combinations(F, 4)}
    torbs = V.triple_orbits(gens)
    cands = sorted({tuple(sorted(o[0] + (x,))) for o in torbs for x in V.P112 if x not in o[0]})
    open_c = [c for c in cands if c not in inframe]
    norb, lab = labels(gens)
    groups = {}
    for c in open_c:
        groups.setdefault(lab(c), []).append(c)
    reps = sorted(g[0] for g in groups.values())
    names = {r: f'u{n:03d}' for n, r in enumerate(reps, 1)}
    print(f'{norb} quadruple orbits; {len(open_c)} open candidates in {len(groups)} orbits', flush=True)
    cover = {}
    for g in groups.values():
        for c, w in words_from(gens, g[0], g).items():
            cover[' '.join(map(str, c))] = [names[g[0]], w]
    with Pool(args.jobs) as pool:
        res = pool.map(unit, reps)
    units, proofs = {}, {}
    for X, (F, text, cdig) in zip(reps, res):
        name = names[X]
        units[name] = {'quadruple': [V.LINES[i] for i in X], 'pivot': [V.LINES[i] for i in F],
                       'proof_sha256': hashlib.sha256(text.encode()).hexdigest(), 'cnf_sha256': cdig,
                       'lemmas': text.count('\n')}
        proofs[name] = text
    print(f'{len(units)} units, {sum(u["lemmas"] for u in units.values())} lemmas')
    (out / 'UNITS.json').write_text(json.dumps(units, indent=1) + '\n')
    (out / 'COVER.json').write_text(json.dumps(cover, sort_keys=True) + '\n')
    (out / 'PROOFS.json.gz').write_bytes(gzip.compress(json.dumps(proofs, sort_keys=True).encode(), mtime=0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
