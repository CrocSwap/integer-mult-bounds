#!/usr/bin/env python3
"""Regenerate plan.json: a heavy matching of dead registers to later deferred births.

Needs numpy and scipy.  verify.py does not use this file: it checks the frozen plan directly, so the certified value
does not depend on how the plan was found, and no optimality is claimed.

  elim      taken unchanged from the existing plan.json (hpst3r's #147 plan at 29383a28d96b9880edbe59ed930f1da1dd6fdfa6);
  level     #144's selected gauges that survive the elimination;
  donors    every remaining slot that is neither an output slot nor a retained centre, at its last frame;
  edge      donor D -> level slot B when D's last operation precedes B's read in the latest timetable and U_D is
            inside sigma_B (screened modulo a prime here, verified exactly over Q by verify.py);
  weight    the first-order moment saved, 3 phi(23 - d) + phi(3f) - 3 phi(f - d);
  matching  maximum total weight (scipy.optimize.linear_sum_assignment).
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import word147  # noqa: E402
from frames147 import Exact  # noqa: E402

PRIME = 1048573
SAVING = 4.73e-4


def main():
    dr, W, D, S, record, folder = word147.load_schedule()
    h, m = S.h, 3 * S.h
    sel = json.loads((word147.ROOT / record['selection_file']).read_text())
    elim = json.loads((HERE / 'plan.json').read_text())['elim']; gone = set(elim)
    level = [s for s in sel['retained_readout_order'] if s not in gone]
    word = word147.Word(S, elim, level, [])
    exact = Exact(S, W, folder)
    donors = [s for s in range(S.R) if s not in S.out and s not in S.ret and s not in gone]
    last = {d: [k for k in S.chain_keys(d) if k[0] != 'F'][-1] for d in donors}
    rows, owner = [], []
    for i, d in enumerate(donors):
        for r in exact.basis(last[d]): rows.append([x % PRIME for x in r]); owner.append(i)
    V = np.array(rows, dtype=np.int64); owner = np.array(owner); size = np.bincount(owner, minlength=len(donors))
    inside = {}
    for b in level:
        key = tuple(map(tuple, S.sigma[b]))
        if key not in inside:
            if len(key) == h: inside[key] = np.arange(len(donors))
            else:
                N = np.array([[x % PRIME for x in z] for z in exact.null(('sigma', b))], dtype=np.int64)
                ok = (((V @ N.T) % PRIME) == 0).all(axis=1)
                inside[key] = np.nonzero(np.bincount(owner[ok], minlength=len(donors)) == size)[0]
    phi = lambda r: r * ((m / r) ** SAVING - 1) / SAVING if r else 0.0
    edges = []
    for j, b in enumerate(level):
        f = S.f[b]
        for i in inside[tuple(map(tuple, S.sigma[b]))]:
            d = donors[int(i)]
            if d == b or word.death[d] >= word.p[b]: continue
            dd = S.dim(last[d])
            edges.append((int(i), j, 3 * phi(h - dd) + phi(3 * f) - 3 * phi(f - dd)))
    used_r = sorted({e[0] for e in edges}); used_c = sorted({e[1] for e in edges})
    rr = {r: i for i, r in enumerate(used_r)}; cc = {c: i for i, c in enumerate(used_c)}
    A = np.zeros((len(used_r), len(used_c)))
    for r, c, x in edges: A[rr[r], cc[c]] = x
    ri, ci = linear_sum_assignment(A, maximize=True)
    pairs = sorted((level[used_c[c]], donors[used_r[r]]) for r, c in zip(ri, ci) if A[r, c] > 0)
    taken = {b for b, _ in pairs}
    plan = dict(elim=sorted(elim), retained=[s for s in level if s not in taken], pairs=[list(p) for p in pairs])
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'plan.json'
    out.write_text(json.dumps(plan, separators=(',', ':')) + '\n')
    print('edges %d, pairs %d, first-order gain %.0f -> %s' % (len(edges), len(pairs), sum(A[r, c] for r, c in zip(ri, ci)), out))


if __name__ == '__main__':
    main()
