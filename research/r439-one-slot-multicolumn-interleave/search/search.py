#!/usr/bin/env python3
"""Seeded heuristic search for one-slot multi-column R439 scatter schedules.

NOT part of the acceptance check (verify.py replays WITNESS.json independently of
this file).  It records how the witness was found.  A "no better schedule found"
outcome here is a failed search over a finite option pool, not an impossibility
theorem.  thakrarsagar with substantial AI assistance from Claude (Anthropic,
Claude Opus 5.5).  Apache-2.0.  The deferred split ({31,51,52} kept) and the
suffix-response model follow PR2115 (Sagar Thakrar), PR2407 (Ross Richardson)
and PR2356 (Sricharan Vagvala).

Model.  rest = the 303 deferred undo gates (d,s): X[d] ^= X[s] on targets.  A tap
of the live copy of column j into target i at cut c has final response
U_after(c) e_i.  That response depends only on the "atom" (i, k): the k-th
lifetime segment of target i between gates having i as source.  A column
representation is a set of atoms whose responses XOR to column j of S; its tap
cuts must meet every atom's segment, so its canonical COPY core is the point
range [max lo, min hi] or the interval [min hi, max lo].

Search.  (1) Exact single-cut options for every column and all 304 cuts.
(2) Seeded tabu walks restricted to random cut intervals; moves are gate
relations (flip the three atoms touched by one gate), so every visited state is
a valid representation; every state with cost <= the cut-0 cost is pooled by
canonical core.  (3) Exact DP over chronological one-slot schedules (one COPY
interval per column, non-overlapping, same-cut handoff allowed) restricted to
the pooled options.  (4) Exact exclusion of representations of weight <= 4 over
the full cut range by meet-in-the-middle on the distinct responses.
"""
import argparse
import gzip
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORD = ROOT/'research/r439-bsection-stars-seed01/candidate.json.gz'
INF = 10**9


def load():
    w = json.loads(gzip.decompress(WORD.read_bytes()))
    v = w['v']
    target = lambda r: v <= r < 2*v
    yy = lambda g: target(g[1]) and all(target(s) for s in g[2])
    reads = [i for i, g in enumerate(w['D']) if target(g[1]) and all(s >= 2*v for s in g[2])]
    lo, hi = min(reads), max(reads)
    prep = [g for g in w['D'][:lo] if yy(g)]
    undo = [w['D'][i] for i, g in enumerate(w['D']) if i > hi and yy(g)]
    keep = [31, 51, 52]
    rest = [g for i, g in enumerate(undo) if i not in keep]
    S = [sum(1 << j for j in row) for row in w['scatter']]
    P = S.copy()
    for _, d, (s,) in prep+[undo[i] for i in keep]:
        P[d-v] ^= P[s-v]
    return v, S, P, [(d-v, s-v) for _, d, (s,) in rest]


class Model:
    def __init__(self):
        self.v, self.S, self.P, self.gates = v, S, P, gates = load()
        self.L = L = len(gates)
        seg = [0]*v; self.segs_at = []
        for c in range(L+1):
            self.segs_at.append(seg.copy())
            if c < L:
                seg[gates[c][1]] += 1
        self.atom = {}
        for i in range(v):
            for k in range(seg[i]+1):
                self.atom[(i, k)] = len(self.atom)
        self.inv = {a: k for k, a in self.atom.items()}
        self.arange = {}
        for i in range(v):
            starts = [0]+[c+1 for c in range(L) if gates[c][1] == i]
            ends = [c for c in range(L) if gates[c][1] == i]+[L]
            for k, (a, b) in enumerate(zip(starts, ends)):
                self.arange[self.atom[(i, k)]] = (a, b)
        sa = self.segs_at
        self.K = [(self.atom[(s, sa[c][s])], self.atom[(s, sa[c][s]+1)], self.atom[(d, sa[c][d])])
                  for c, (d, s) in enumerate(gates)]
        X = P.copy(); self.Xc = []
        for c in range(L+1):
            self.Xc.append(X.copy())
            if c < L:
                d, s = gates[c]; X[d] ^= X[s]
        self.W = [[sum(self.Xc[c][i] >> j & 1 for i in range(v)) for c in range(L+1)] for j in range(9)]

    def base_atoms(self, j, c):
        return [self.atom[(i, self.segs_at[c][i])] for i in range(self.v) if self.Xc[c][i] >> j & 1]

    def core(self, atoms):
        lo = max(self.arange[a][0] for a in atoms); hi = min(self.arange[a][1] for a in atoms)
        return (lo, hi, 'pt') if lo <= hi else (hi, lo, 'iv')


def walk(m, rng, j, l, r, iters, cap, pool):
    gl = list(range(l, r)); mem = {}
    for c in gl:
        for a in m.K[c]:
            mem.setdefault(a, []).append(c)
    par = {a: 1 for a in m.base_atoms(j, rng.randint(l, r))}
    cost = sum(par.values())
    delta = {c: sum(1-2*par.get(a, 0) for a in m.K[c]) for c in gl}
    tabu = {}; best = cost
    for it in range(iters):
        cand = None; cd = None
        for c in gl:
            dd = delta[c]
            if tabu.get(c, -1) > it and not cost+dd < best:
                continue
            if cd is None or dd < cd or (dd == cd and rng.random() < 0.3):
                cand, cd = c, dd
        if cand is None:
            break
        cost += cd
        for a in m.K[cand]:
            par[a] = par.get(a, 0) ^ 1
            ch = 2 if par[a] == 0 else -2
            for c2 in mem[a]:
                delta[c2] += ch
        tabu[cand] = it+rng.randint(5, 15)
        best = min(best, cost)
        if cost <= cap[j]:
            atoms = sorted(a for a, p in par.items() if p)
            k = m.core(atoms)
            if k not in pool[j] or pool[j][k][0] > cost:
                pool[j][k] = (cost, atoms)


def dp(m, pool):
    L, v = m.L, m.v
    pt = [[(m.W[j][t], None) for t in range(L+1)] for j in range(9)]
    iv = [{} for _ in range(9)]
    for j in range(9):
        for (x, y, kind), (c, atoms) in pool[j].items():
            if kind == 'pt':
                for t in range(x, y+1):
                    if c < pt[j][t][0]:
                        pt[j][t] = (c, atoms)
            elif (x, y) not in iv[j] or c < iv[j][(x, y)][0]:
                iv[j][(x, y)] = (c, atoms)
    g = {0: [0]*(L+1)}; par = {}
    for mask in sorted(range(512), key=lambda q: bin(q).count('1')):
        raw = g[mask]; pm = [0]*(L+1); arg = [0]*(L+1); best = INF; bi = -1
        for t in range(L+1):
            if raw[t] < best:
                best, bi = raw[t], t
            pm[t], arg[t] = best, bi
        g[mask] = (pm, arg)
        for j in range(9):
            if mask >> j & 1:
                continue
            h = g.setdefault(mask | 1 << j, [INF]*(L+1))
            for t in range(L+1):
                val = pm[t]+pt[j][t][0]
                if val < h[t]:
                    h[t] = val; par[(mask | 1 << j, t)] = (mask, arg[t], j, 'pt', t)
            for (x, y), (c, _) in iv[j].items():
                if pm[x]+c < h[y]:
                    h[y] = pm[x]+c; par[(mask | 1 << j, y)] = (mask, arg[x], j, 'iv', (x, y))
    pm, arg = g[511]; mask = 511; t = arg[L]; sched = []
    while mask:
        pmask, pt_, j, kind, key = par[(mask, t)]
        if kind == 'pt':
            c, atoms = pt[j][key]
            taps = ([[key, i] for i in range(v) if m.Xc[key][i] >> j & 1] if atoms is None
                    else [[key, m.inv[a][0]] for a in atoms])
            sched.append({'column': j, 'copy_cut': key, 'erase_cut': key, 'taps': sorted(taps)})
        else:
            x, y = key; c, atoms = iv[j][key]
            sched.append({'column': j, 'copy_cut': x, 'erase_cut': y,
                          'taps': sorted([max(m.arange[a][0], x), m.inv[a][0]] for a in atoms)})
        mask, t = pmask, pt_
    return pm[L], sched[::-1]


def check(m, sched):
    cols = [1 << i for i in range(m.v)]; suffix = {m.L: cols.copy()}
    for cut in reversed(range(m.L)):
        d, s = m.gates[cut]; cols[s] ^= cols[d]; suffix[cut] = cols.copy()
    prev = 0
    assert sorted(sg['column'] for sg in sched) == list(range(9))
    for sg in sched:
        assert prev <= sg['copy_cut'] <= sg['erase_cut']; prev = sg['erase_cut']
        want = sum(1 << i for i, row in enumerate(m.S) if row >> sg['column'] & 1); act = 0
        for c, i in sg['taps']:
            assert sg['copy_cut'] <= c <= sg['erase_cut']; act ^= suffix[c][i]
        assert act == want
    return sum(len(sg['taps']) for sg in sched)


def mitm(m):
    """Exact: minimum weight per column if <= 4 over all 304 cuts, else '>=5'."""
    cols = [1 << i for i in range(m.v)]; resp = set(cols)
    for c in reversed(range(m.L)):
        d, s = m.gates[c]; cols[s] ^= cols[d]; resp.add(cols[s])
    D = sorted(resp); Dset = set(D); pairs = {}
    for a in range(len(D)):
        for b in range(a+1, len(D)):
            pairs.setdefault(D[a] ^ D[b], (a, b))
    out = {}
    for j in range(9):
        t = sum(1 << i for i, row in enumerate(m.S) if row >> j & 1)
        if t in Dset:
            out[j] = 1
        elif t in pairs:
            out[j] = 2
        elif any((t ^ x) in pairs for x in D):   # overlap would give weight 1, excluded above
            out[j] = 3
        elif any((t ^ p) in pairs for p in pairs):  # overlap would give weight <= 2, excluded above
            out[j] = 4
        else:
            out[j] = '>=5'
    return len(D), out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=6); ap.add_argument('--walks', type=int, default=20000)
    ap.add_argument('--out', type=Path)
    a = ap.parse_args()
    m = Model(); rng = random.Random(a.seed)
    cap = [m.W[j][0] for j in range(9)]
    pool = {j: {} for j in range(9)}
    for n in range(a.walks):
        j = rng.randrange(9); x = rng.randint(0, m.L); y = rng.randint(0, m.L)
        l, r = min(x, y), max(x, y)
        if r-l < 2:
            continue
        walk(m, rng, j, l, r, rng.choice([300, 800, 1500]), cap, pool)
        if (n+1) % 2000 == 0:
            print('walks', n+1, 'best pooled per column',
                  [min([c for c, _ in pool[q].values()] or [cap[q]]) for q in range(9)], flush=True)
    best, sched = dp(m, pool)
    total = check(m, sched)
    assert total == best
    nresp, low = mitm(m)
    rec = {'seed': a.seed, 'walks': a.walks, 'cut0_costs': cap, 'single_cut_minima': [min(r) for r in m.W],
           'pooled_minima': [min([c for c, _ in pool[q].values()] or [cap[q]]) for q in range(9)],
           'pool_cores': [len(pool[q]) for q in range(9)], 'dp_best': best,
           'pooled_minimum_cores': {str(q): sorted([x, y, kind] for (x, y, kind), (c, _) in pool[q].items()
                                                   if c == min(cc for cc, _ in pool[q].values()))[:40]
                                    for q in range(9) if pool[q]},
           'pooled_minimum_core_counts': [sum(c == min(cc for cc, _ in pool[q].values()) for c, _ in pool[q].values())
                                          if pool[q] else 0 for q in range(9)],
           'schedule': [[sg['column'], sg['copy_cut'], sg['erase_cut'], len(sg['taps'])] for sg in sched],
           'distinct_responses': nresp, 'exact_min_weight_full_range': low}
    print(json.dumps(rec))
    if a.out:
        a.out.write_text(json.dumps({'record': rec, 'segments': sched}, indent=1)+'\n')


if __name__ == '__main__':
    main()
