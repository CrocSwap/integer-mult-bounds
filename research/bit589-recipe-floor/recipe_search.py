#!/usr/bin/env python3
"""Exhaustive search of K-pair stage recipes with one local per stage, L = 2K+1 stages (the floor of PROOF.md).

Class (stated in README.md): stage s >= 1 may be preceded by no bridge or by exactly ONE bridge (d, src, c), c = +-1,
d != src; stage 0 has none; any final Levi (bridges after the last local) is free. A recipe is valid iff its scalar
product maps L0 -> L1 and L1 -> L0, i.e. a final bridge sequence plus the exchange restores the identity. Products with
an entry above BOUND in absolute value are pruned (BOUND = 8; at K = 3, BOUND = 64 gives the same recipes).
Pruning uses the invariants of PROOF.md: max(mu, K-mu') + max(K-nu, nu') <= remaining stages (a necessary condition).
Completability of (stage, product) is memoised, so only completable branches are walked.

Output (JSON): counts and every distinct idle-window structure with one witness recipe each.
usage: recipe_search.py K OUT.json [--jobs N] [--bound B] [--depth D]
Prepared by Ian Libânio with substantial AI assistance (Claude Opus 5.5, Anthropic, via Claude Code). Apache-2.0."""
import argparse, json, sys, time
from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import recipe_lib as RL

K = L = BOUND = BPG = None
BR = []


def setup(k, bound, bpg=1):
    global K, L, BOUND, BR, GAPS, BPG
    K, L, BOUND, BPG = k, 2 * k + 1, bound, bpg
    BR = [(d, s, c) for d in range(K) for s in range(K) if d != s for c in (1, -1)]
    GAPS = gap_options(bpg)


def feasible(P, t):
    mu, mup, nu, nup = RL.invariants(P, K)
    return max(mu, K - mup) + max(K - nu, nup) <= L - t


GAPS = None


def gap_options(bpg):
    opts = [None] + BR
    if bpg >= 2: opts += [[b1, b2] for b1 in BR for b2 in BR if b1[:2] != b2[:2]]
    return opts


def children(t, P):
    for g in ([None] if t == 0 else GAPS):
        Q = P
        for b in RL.gap_bridges(g): Q = RL.bridge(Q, K, *b)
        if g is not None and Q == P: continue
        for p in range(K):
            if t == 0 and p: continue           # relabel pairs: the first local acts on pair 0
            for ty in 'FR':
                R = RL.local(Q, K, p, ty)
                if max(abs(x) for r in R for x in r) <= BOUND and feasible(R, t + 1):
                    yield (g, p, ty), R


@lru_cache(maxsize=None)
def can(t, P):
    if t == L: return RL.antidiagonal(P, K)
    return any(can(t + 1, R) for _, R in children(t, P))


def walk(item):
    k, bound, bpg, t0, P0, hist0 = item
    if (K, BOUND, BPG) != (k, bound, bpg): setup(k, bound, bpg)
    out = {}; count = 0
    def rec(t, P, hist):
        nonlocal count
        if t == L:
            count += 1
            key = RL.structure_key(RL.windows(RL.schedule(hist, K)))
            out.setdefault(key, list(hist)); return
        for step, R in children(t, P):
            if can(t + 1, R): rec(t + 1, R, hist + [step])
    rec(t0, P0, hist0)
    return count, out


def canon(h):
    return [(tuple(RL.gap_bridges(g)), p, ty) for g, p, ty in h]


def run(k, jobs=1, bound=8, depth=3, log=True, bpg=1):
    setup(k, bound, bpg); t0 = time.time()
    front = [(0, RL.ident(K), [])]
    for _ in range(min(depth, L - 1)):
        front = [(t + 1, R, h + [step]) for t, P, h in front for step, R in children(t, P)]
    items = [(k, bound, bpg, t, P, h) for t, P, h in front]
    total = 0; structures = {}
    pool = Pool(jobs) if jobs > 1 else None
    it = pool.imap_unordered(walk, items, chunksize=1) if pool else map(walk, items)
    for i, (cnt, out) in enumerate(it):
        total += cnt
        for key, h in out.items():
            if key not in structures or canon(h) < canon(structures[key]): structures[key] = h   # deterministic witness
        if log and (i + 1) % max(1, len(items) // 10) == 0:
            print('   %d/%d branches, %d recipes, %d structures, %.0fs' % (i + 1, len(items), total, len(structures), time.time() - t0), flush=True)
    if pool: pool.close(); pool.join()
    rows = [dict(windows=[[r, list(st)] for r, st in key], witness=[[[list(b) for b in RL.gap_bridges(g)] if bpg > 1 and g else (list(g) if g else None), p, ty] for g, p, ty in h])
            for key, h in sorted(structures.items())]
    return dict(K=k, stages=2 * k + 1, bridges_per_gap=bpg, entry_bound=bound, valid_recipes=total,
                distinct_window_structures=len(rows), structures=rows, seconds=round(time.time() - t0, 1))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('K', type=int); ap.add_argument('out', type=Path)
    ap.add_argument('--jobs', type=int, default=1); ap.add_argument('--bound', type=int, default=8)
    ap.add_argument('--depth', type=int, default=3); ap.add_argument('--bridges-per-gap', type=int, default=1, choices=(1, 2))
    a = ap.parse_args()
    res = run(a.K, a.jobs, a.bound, a.depth, bpg=a.bridges_per_gap)
    a.out.write_text(json.dumps(res, separators=(',', ':')) + '\n')
    print('   K=%d: %d valid recipes, %d distinct window structures (%.0fs)' % (a.K, res['valid_recipes'], res['distinct_window_structures'], res['seconds']))
