"""Exact frame-assignment optimum for a fixed gate order (CP-SAT).

Feasible frame assignments are the solutions of X_g <= X_next along every register chain with fixed anchors;
they lie between the least and greatest solutions, so each gate's domain is the finite set of subspaces in
[least_g, greatest_g].  Chain-adjacent pairs are linked by pair variables carrying the climb cost W(d), and
the objective is the linearised recurrence weight. Run with a Python that has ortools.

usage: frame_exact.py WORD.json.gz [OUT.json.gz] [--time 600]
"""
import argparse, gzip, json, sys, math
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import frame_lift as L
from least import least

SCALE = 10 ** 6


def interval(lo, hi):
    """all subspaces S with lo <= S <= hi (masks)."""
    out = {lo}; frontier = [lo]
    els = [x for x in range(512) if hi >> x & 1 and not lo >> x & 1]
    while frontier:
        nxt = []
        for s in frontier:
            for x in els:
                if not s >> x & 1:
                    t = L.span_mask([y for y in range(512) if s >> y & 1] + [x])
                    if t not in out:
                        out.add(t); nxt.append(t)
        frontier = nxt
    return sorted(out)


def W(d):
    return round(L.W(d) * SCALE)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out', nargs='?')
    ap.add_argument('--time', type=float, default=600); ap.add_argument('--workers', type=int, default=8); ap.add_argument('--caps', action='store_true'); ap.add_argument('--recipe')
    a = ap.parse_args()
    from ortools.sat.python import cp_model
    word = json.load(gzip.open(a.src))
    caps = L.cone_caps(word) if a.caps else None
    print('cone caps', len(caps or {}))
    ch = L.chains(word, caps); G, orig = L.greatest(word, caps); lo, pos = least(word, ch, len(orig))
    assert all(x & ~y == 0 for x, y in zip(lo, orig)) and all(x & ~y == 0 for x, y in zip(orig, G))
    dom = [interval(l, g) for l, g in zip(lo, G)]
    if a.caps:   # admissible mode: early-cleanup (tail) frames are fixed by the word's early_cleanup list
        for g, (part, _, _) in enumerate(L.events(word)):
            if part == 'T': dom[g] = [orig[g]]
    print('domain sizes', sorted(Counter(map(len, dom)).items()))
    m = cp_model.CpModel()
    x = [{s: m.NewBoolVar('') for s in d} for d in dom]
    for g, d in enumerate(x):
        m.AddExactlyOne(d.values())
        m.AddHint(d[orig[g]], 1)
    obj = []; const = 0
    for r, c in enumerate(ch):
        nodes = [nd for nd in c if nd[0] != 'cap']
        for (k1, v1), (k2, v2) in zip(nodes, nodes[1:]):
            if k1 != 'g' and k2 != 'g':
                if v1 != v2: const += W(L.dim(v2) - L.dim(v1))
                continue
            if k1 != 'g':      # fixed -> gate
                for s, b in x[v2].items():
                    if v1 & ~s: m.Add(b == 0)
                    elif s != v1: obj.append(W(L.dim(s) - L.dim(v1)) * b)
                continue
            if k2 != 'g':      # gate -> fixed (final / anchor)
                for s, b in x[v1].items():
                    if s & ~v2 or (k2 == 'a' and s != v2): m.Add(b == 0)
                    elif s != v2: obj.append(W(L.dim(v2) - L.dim(s)) * b)
                continue
            if v1 == v2: continue
            A, B = x[v1], x[v2]
            if len(A) == 1 and len(B) == 1: 
                (s, _), (t, _) = next(iter(A.items())), next(iter(B.items()))
                assert s & ~t == 0
                if s != t: const += W(L.dim(t) - L.dim(s))
                continue
            pairs = {}
            for s, bs in A.items():
                for t, bt in B.items():
                    if s & ~t == 0:
                        y = m.NewBoolVar(''); pairs[s, t] = y
                        if s != t: obj.append(W(L.dim(t) - L.dim(s)) * y)
            for s, bs in A.items():
                m.Add(sum(y for (s2, _), y in pairs.items() if s2 == s) == bs)
            for t, bt in B.items():
                m.Add(sum(y for (_, t2), y in pairs.items() if t2 == t) == bt)
    m.Minimize(sum(obj))
    solver = cp_model.CpSolver(); solver.parameters.max_time_in_seconds = a.time
    solver.parameters.num_workers = a.workers
    st = solver.Solve(m)
    print('status', solver.StatusName(st), 'objective', (solver.ObjectiveValue() + const) / SCALE,
          'bound', (solver.BestObjectiveBound() + const) / SCALE)
    X = [next(s for s, b in d.items() if solver.Value(b)) for d in x]
    base = sum(L.W(d) * n for d, n in L.profile(word).items())
    p = L.profile(word, X)
    print('orig profile', dict(sorted(L.profile(word).items())), 'w %.6f' % base)
    print('best profile', dict(sorted(p.items())), 'w %.6f' % sum(L.W(d) * n for d, n in p.items()))
    print('changed gates', sum(o != y for o, y in zip(orig, X)))
    if a.recipe:
        gates = L.events(word); rows = []
        for (part, i, e), o, y in zip(gates, orig, X):
            if o != y:
                assert part in ('A', 'B'), 'tail frame change'
                rows.append([part, i, e[-1], L.basis_of(y)])
        Path(a.recipe).write_text(json.dumps(rows) + '\n'); print('recipe gates', len(rows))
    if a.out:
        w = L.apply_frames(word, X)
        assert L.profile(w) == p
        w['report']['local_profile'] = {str(k): z for k, z in sorted(p.items())}
        Path(a.out).write_bytes(gzip.compress(json.dumps(w, sort_keys=True, separators=(',', ':')).encode(), mtime=0))


if __name__ == '__main__':
    main()
