"""retime.py: exact re-timing of early pivot reads.  An early read g_j = (t += c*q) at B position j < first(q) may move to
any position p in (j, first(q)] such that no B gate in (j, p) reads t or scales t (t's suffix effect is then unchanged) and
q is still unwritten (its value is the initial one), so the program map is unchanged exactly.  Prices (PR #1186 revision 2
harness, surrogate-optimal frames and true-moment interval bounds, bounds.py): every single move to the segment end and
to every intermediate slot; then, per pivot, the joint move of all its early reads to their segment ends.
usage: retime.py TOOLKIT WORD ORACLE.json OUT.json [--top N] [--workers N]"""
import argparse, json, sys, time, multiprocessing as mp
ap = argparse.ArgumentParser(); ap.add_argument('toolkit'); ap.add_argument('word'); ap.add_argument('oracle'); ap.add_argument('out')
ap.add_argument('--top', type=int, default=160); ap.add_argument('--workers', type=int, default=14); a = ap.parse_args()
sys.path.insert(0, a.toolkit)
import harness as H, bounds
P = None
def init():
    global P; P = bounds.pricer(H)(a.word, check_literal=True, interval=True)
def segment_end(B, j, q, first):
    t = B[j][1]; p = j + 1
    while p < first:
        g = B[p]
        if (g[0] == 'add' and g[2] == t) or (g[0] == 'scale' and g[1] == t) or (g[0] == 'add' and g[1] == q) or (g[0] == 'scale' and g[1] == q): break
        p += 1
    return p   # insert before base index p (exclusive end); p == j+1 means no room
def run(job):
    kind, q, moves = job
    ed = dict(delete=[j for j, p in moves], insert=[[p, list(P.base['B'][j][:-1]) + [[]]] for j, p in moves])
    r = P.price(ed, timeout=300)
    extra = {k: r[k] for k in ('realized_delta_units', 'gain_certified', 'max_gain_units_ceil', 'interval_width_units_ceil', 'audit') if k in r}
    return dict(kind=kind, pivot=q, moves=moves, status=r.get('status'), delta=r.get('delta'), profile=r.get('profile'), **extra)
if __name__ == '__main__':
    init(); B = P.base['B']; ora = [r for r in json.load(open(a.oracle)) if r.get('delta') is not None and r['delta'] < 0][:a.top]
    jobs = []
    for r in ora:
        q = r['pivot']; first = next((i for i, g in enumerate(B) if g[1] == q), len(B))
        dele = [i for i in range(first) if B[i][0] == 'add' and B[i][2] == q]
        ends = []
        for j in dele:
            e = segment_end(B, j, q, first)
            if e > j + 1:
                ends.append((j, e))
                for p in sorted({j + 2, (j + e) // 2, e}):
                    if j + 1 < p <= e: jobs.append(('single', q, [(j, p)]))
        if len(ends) > 1: jobs.append(('joint-end', q, ends))
    print('pivots', len(ora), 'jobs', len(jobs), flush=True); out = []; t0 = time.time()
    with mp.get_context('fork').Pool(a.workers, initializer=init, maxtasksperchild=12) as pool:
        for n, r in enumerate(pool.imap_unordered(run, jobs), 1):
            out.append(r)
            if r['delta'] is not None and r['delta'] < 0: print('  GAIN', r, flush=True)
            if n % 100 == 0: print(f'  {n}/{len(jobs)} {time.time()-t0:.0f}s', flush=True)
    out.sort(key=lambda r: (r['pivot'], r['kind'], r['moves']))
    json.dump(out, open(a.out, 'w'), sort_keys=True)
    import collections
    print('done', len(out), collections.Counter((r['status'], (r['delta'] > 0) - (r['delta'] < 0) if r['delta'] is not None else None) for r in out))
