#!/usr/bin/env python3
"""Regenerate the pinned weighted carrier matchings for the skip-prefix DAGs.

Rohan Arun's PR #44 optimizer, unchanged in substance: the PR #44 profiler
(references/copied-fixed/pr44/profiles.cpp) in DUMP_EDGES mode lists every
admissible (donor,use) edge with its exact signed block change; we maximize
sum c_t*t*ln t over all maximum-cardinality matchings with scipy's
min_weight_full_bipartite_matching (each donor gets a private dummy column).
Only the graph import changes. Requires scipy; not needed to *check* the
pinned links, which producer.py replays and validates exactly.
Usage: python3 optimize_matching.py --work-dir DIR  (writes DIR/links-{h}.uses)
"""
import argparse, math, os, shlex, struct, subprocess, sys
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import min_weight_full_bipartite_matching, maximum_bipartite_matching
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'scripts')); sys.path.insert(0, str(HERE))
from partial_swap.graph import export
from pair_graph import graph


def solve(edges_path, h):
    E = []
    for line in open(edges_path):
        p = line.split(); x, e, j = map(int, p[:3])
        d = {int(k): int(v) for k, v in (q.split(':') for q in p[3:])}
        assert sum(t*c for t, c in d.items()) == -h
        E.append((x, j, e, sum(c*t*math.log(t) for t, c in d.items())))
    donors = sorted({x for x, *_ in E}); uses = sorted({j for _, j, *_ in E})
    di = {x: i for i, x in enumerate(donors)}; ui = {j: i for i, j in enumerate(uses)}
    nd, nu = len(donors), len(uses)
    r = [di[x] for x, *_ in E]; c = [ui[j] for _, j, *_ in E]
    card = int((maximum_bipartite_matching(csr_matrix((np.ones(len(E)), (r, c)), shape=(nd, nu)), perm_type='column') >= 0).sum())
    ws = np.array([w for *_, w in E]); C = ws.max()+1.0
    M = csr_matrix((list(C-ws)+[C+1e6]*nd, (r+list(range(nd)), c+[nu+i for i in range(nd)])), shape=(nd, nu+nd))
    ri, ci = min_weight_full_bipartite_matching(M)
    emap = {(di[x], ui[j]): (x, e) for x, j, e, _ in E}
    sel = sorted(emap[(i, k)] for i, k in zip(ri.tolist(), ci.tolist()) if k < nu)
    assert len(sel) == card
    return sel


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--work-dir', type=Path, required=True); a = ap.parse_args()
    a.work_dir.mkdir(parents=True, exist_ok=True); exe = a.work_dir/'profiles-dump'
    subprocess.run([*shlex.split(os.environ.get('CXX', 'c++')), '-O3', '-std=c++17', '-include', 'algorithm',
                    '-I', str(ROOT/'scripts/partial_swap'), str(ROOT/'references/copied-fixed/pr44/profiles.cpp'), '-o', str(exe)], check=True)
    for h in (23, 25):
        dag = a.work_dir/f'h{h}.bin'; export(graph(h), dag)
        subprocess.run([str(exe), str(dag)], env=dict(os.environ, DUMP_EDGES=str(a.work_dir/f'edges{h}.txt')), check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sel = solve(a.work_dir/f'edges{h}.txt', h)
        n = struct.unpack_from('<4I', dag.read_bytes()[:16])[2]
        out = a.work_dir/f'links-{h}.uses'
        out.write_bytes(struct.pack('<2I', n, len(sel))+b''.join(struct.pack('<2I', x, e) for x, e in sel))
        pinned = HERE/f'links-{h}.uses'
        same = pinned.exists() and sorted(struct.iter_unpack('<2I', out.read_bytes()[8:])) == sorted(struct.iter_unpack('<2I', pinned.read_bytes()[8:]))
        print(f'h={h} matched {len(sel)}; equals pinned links: {same}')
