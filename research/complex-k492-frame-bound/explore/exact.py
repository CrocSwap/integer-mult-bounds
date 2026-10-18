#!/usr/bin/env python3
"""Discovery cross-check: exact fixed-order A/B frame model solved by CP-SAT (needs ortools).

Not used by verify.py; CP-SAT optimality is a solver report, not a certificate.
Every free macro picks one subspace of its complete interval [lo, hi]; consecutive
free macros on a register must be nested. Objective: maximise -sum c_k(b) over
register climbs (c_k = k^(1-b) - k), scaled to integers.

usage: explore/exact.py DATA_WORD_DIR forward|backward SECONDS
"""
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import model as Mo
import engine as E
from ortools.sat.python import cp_model

lo_, hi_ = E.adjusted_bounds()
W = {k: round(-float(lo_[k]) * 10 ** 9) for k in range(10)}


def solve(c, F, nodes, lo, hi, seconds):
    m = cp_model.CpModel(); n = 2 * c['v'] + c['R']; seq = Mo.chains(c, nodes)
    free = [i for i, nd in enumerate(nodes) if nd[1] is None and len(lo[i]) < len(hi[i])]
    dom = {i: Mo.between(lo[i], hi[i]) for i in free}; x = {}; dv = {}
    for i in free:
        x[i] = m.NewIntVar(0, len(dom[i]) - 1, ''); dims = [len(g) for g in dom[i]]
        dv[i] = m.NewIntVar(min(dims), max(dims), ''); m.AddElement(x[i], dims, dv[i]); m.AddHint(x[i], dom[i].index(nodes[i][2]))
    D = lambda i: dv[i] if i in dv else len(nodes[i][2])
    obj = []; done = set()
    for r in range(n):
        s = seq[r]
        for a, b in zip(s, s[1:]):
            if a in x and b in x and (a, b) not in done:
                done.add((a, b))
                m.AddAllowedAssignments([x[a], x[b]], [(p, q) for p, g in enumerate(dom[a]) for q, h in enumerate(dom[b]) if Mo.contains(h, g)])
        chain = [len(F[c['start'][r]])] + [D(i) for i in s] + [len(F[c['final'][r]])]
        for u, w in zip(chain, chain[1:]):
            if isinstance(u, int) and isinstance(w, int): obj.append(W[w - u]); continue
            zs = [(t, m.NewBoolVar('')) for t in range(10)]
            m.AddExactlyOne(z for t, z in zs); m.Add(w - u == sum(t * z for t, z in zs)); obj.extend(W[t] * z for t, z in zs)
    m.Maximize(sum(obj))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = seconds; s.parameters.num_workers = 8; st = s.Solve(m)
    fr = [nd[2] for nd in nodes]
    for i in free: fr[i] = dom[i][s.Value(x[i])]
    return s.StatusName(st), s.ObjectiveValue(), s.BestObjectiveBound(), fr


if __name__ == '__main__':
    c, ev = Mo.load(sys.argv[1], sys.argv[2]); F, nodes, climbs, center = Mo.extract(c, ev); lo, hi = Mo.intervals(c, F, nodes)
    H0 = Mo.profile(c, F, nodes, [nd[2] for nd in nodes]); base = sum(W[k] * z for k, z in H0.items())
    st, val, bd, fr = solve(c, F, nodes, lo, hi, float(sys.argv[3]))
    H1 = Mo.profile(c, F, nodes, fr)
    print(st, 'objective', val, 'bound', bd, 'baseline', base, 'solution profile', dict(sorted(H1.items())),
          'changed frames', sum(fr[i] != nd[2] for i, nd in enumerate(nodes)))
