"""repair: exhaustive fusion + enlarged-reader repair sweep, priced by the harness.

A fusion donates q*A into a holder H that the same target t reads later, deletes t's read of A and restores H (in B, by an
early-cleanup tail, or by a FULL-cleanup prepend). The donation enlarges A's and H's frames, so each fusion is also tried with
repairs that redirect later target reads of A or H to the copy partner (read-set exchange rule): every single swap, every
pair of swaps, and the full exchange of the copy pair containing A or H. Every candidate is priced by harness.Pricer (surrogate
optimum; audit_local on every negative delta).

usage: python -B repair.py WORD.json.gz OUT.json [--workers 3] [--timeout 90] [--max-tasks-per-child 50] [--interval]
Prints the gains (negative surrogate deltas; each is re-checked by audit_local). OUT.json keeps every candidate's best repair.
--interval (about 2x slower): also bound every priced candidate's possible true-moment gain at b (max_gain_units) and print
the largest bound among the candidates without a surrogate gain."""
import argparse, json, os, time, itertools
import harness as C
from compat import pool_context
from joint import swap_edit, merge
from exchange import copy_pairs, movable_reads
P = None; MOV = None; PAIRS = None; TIMEOUT = 90
def init(path, timeout=90, interval=False):
    global P, MOV, PAIRS, TIMEOUT
    TIMEOUT = timeout; P = C.Pricer(path, interval=interval); PAIRS = copy_pairs(P.base); MOV = {}
    for h, (r, ic) in PAIRS.items():
        for m in movable_reads(P.base, h, r, ic): MOV[m[0]] = (h, r, ic, m)
def repair(c):
    ed0 = c['ed']; A, H, p = c['A'], c['H'], c['p']
    later = [j for j, (h, r, ic, m) in MOV.items() if j >= p and m[2] in (A, H) and j not in ed0['delete']]
    opts = []
    for j in later:
        h, r, ic, m = MOV[j]; s = swap_edit(P.base, h, r, ic, m)
        if s: opts.append(((("swap", j),), s))
    singles = list(opts)
    for (k1, s1), (k2, s2) in itertools.combinations(singles, 2):
        m2 = merge([s1, s2])
        if m2: opts.append((k1 + k2, m2))
    for h, (r, ic) in PAIRS.items():
        if A in (h, r) or H in (h, r):
            rest = [m for m in movable_reads(P.base, h, r, ic) if m[0] not in ed0['delete']]
            ss = [swap_edit(P.base, h, r, ic, m) for m in rest]
            if rest and all(ss): opts.append(((("exchange", h),), merge(ss)))
    best = None; tried = 0; bound = None
    def priced(r):
        nonlocal bound
        usable = r.get('status') in ('ok', 'uncertified')   # 'audit-rejected' and screen failures carry no usable delta
        if usable and r['delta'] >= 0 and 'max_gain_units' in r: bound = max(bound or 0.0, r['max_gain_units'])   # interval needs no surrogate certificate
        return usable
    r0 = P.price(ed0, timeout=TIMEOUT); tried += 1
    if priced(r0): best = dict(delta=r0['delta'], steps=(), profile=r0['profile'])
    for key, e2 in opts[:40]:
        m = merge([ed0, e2])
        if m is None: continue
        r = P.price(m, timeout=TIMEOUT); tried += 1
        if priced(r) and (best is None or r['delta'] < best['delta']): best = dict(delta=r['delta'], steps=key, profile=r['profile'])
    return dict({k: v for k, v in c.items() if k != 'ed'}, ed=ed0, tried=tried, nrepairs=len(opts), best=best, max_gain_units=bound)
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("word"); ap.add_argument("out"); ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=90, help="wall-clock seconds per pricing (compat.deadline)")
    ap.add_argument("--max-tasks-per-child", type=int, default=50, help="recycle workers to bound resident memory")
    ap.add_argument("--interval", action="store_true", help="true-moment interval bounds for every priced candidate")
    a = ap.parse_args(); import fusion as G
    cs = G.candidates(C.load(a.word)); print("fusions to repair:", len(cs), flush=True); t0 = time.time(); res = []
    with pool_context().Pool(a.workers, initializer=init, initargs=(a.word, a.timeout, a.interval), maxtasksperchild=a.max_tasks_per_child) as pool:
        for n, r in enumerate(pool.imap_unordered(repair, cs, chunksize=1), 1):
            res.append(r)
            if n % 50 == 0: print(f"  {n}/{len(cs)} {time.time()-t0:.0f}s feasible {sum(1 for x in res if x['best'])} gains {sum(1 for x in res if x['best'] and x['best']['delta'] < 0)} evals {sum(x['tried'] for x in res)}", flush=True)
    gains = sorted([x for x in res if x['best'] and x['best']['delta'] < 0], key=lambda x: x['best']['delta'])
    print(f"done {len(res)} in {time.time()-t0:.0f}s | feasible {sum(1 for x in res if x['best'])} | gains {len(gains)} | evals {sum(x['tried'] for x in res)}")
    for x in gains[:20]: print(f"   gain {-x['best']['delta']} t={x['t']} A={x['A']} H={x['H']} p={x['p']} {x['rest']} steps {x['best']['steps']} {x['best']['profile']}")
    if a.interval:
        bs = [x['max_gain_units'] for x in res if x.get('max_gain_units') is not None]
        print(f"interval: {len(bs)} fusions with priced non-gain candidates; largest possible true gain at b among them {max(bs, default=0.0):.3g} units")
    json.dump(res, open(a.out, "w", encoding="utf-8", newline="\n"))
