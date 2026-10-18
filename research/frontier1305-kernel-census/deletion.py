"""deletion.py: uncompensated deletion price per pivot (a screening heuristic, NOT a bound; see README).  Exact optimal frames (#1186 model: cone caps, tail-mutable, cut equality) of the
word with ALL early reads of pivot q deleted, WITHOUT any compensation and without the program-map screen.  Any exact
compensating kernel adds gates, so (cost after deletion - base cost) bounds below the delta of every kernel for q that
keeps the remaining frame structure ONLY when the deletion leaves the map-derived constraints (cone caps, cut equality)
unchanged; it does not in general: on #1297's input word the uncompensated deletion of pivot 555/567 is frame-infeasible while
the exact kernels gain.  usage: deletion.py TOOLKIT WORD OUT [--workers N]"""
import argparse, json, sys, time, multiprocessing as mp
ap = argparse.ArgumentParser(); ap.add_argument('toolkit'); ap.add_argument('word'); ap.add_argument('out'); ap.add_argument('--workers', type=int, default=12)
ap.add_argument('--pivots', nargs='*', type=int); a = ap.parse_args()
sys.path.insert(0, a.toolkit)
import harness as H, frames as F
from word import inline
from model import cone_caps
from compat import Timeout, deadline
P = None
def init():
    global P; P = H.Pricer(a.word, check_literal=True)
def run(q):
    w = P.base; B = w['B']; first = next((i for i, g in enumerate(B) if g[1] == q), len(B))
    dele = [i for i in range(first) if B[i][0] == 'add' and B[i][2] == q]
    w1 = H.compile_edits(w, dict(delete=dele))
    try:
        with deadline(300):
            caps, comp = cone_caps(w1)
            g = F.Graph(inline(w1, True), check_literal=False, tail_mutable=True, caps=caps, cut_equality=True)
            r = F.optimal_frames(inline(w1, True), P.costs, check_literal=False, graph=g)
        res = dict(status='ok' if r['certified'] else 'uncertified', delta=r['cost'] - P.base_cost, profile=dict(sorted(r['profile'].items())))
    except F.Infeasible as e: res = dict(status='infeasible')
    except Timeout: res = dict(status='timeout')
    except ValueError as e: res = dict(status='error:' + str(e)[:60])
    return dict(pivot=q, early=len(dele), targets=[B[i][1] for i in dele], **res)
if __name__ == '__main__':
    init(); B = P.base['B']; first = {}
    for i, g in enumerate(B): first.setdefault(g[1], i)
    piv = a.pivots or sorted({g[2] for i, g in enumerate(B) if g[0] == 'add' and g[2] >= 224 and i < first.get(g[2], len(B))})
    print('base', P.base_cost, P.base_profile, 'pivots', len(piv), flush=True); out = []; t0 = time.time()
    with mp.get_context('fork').Pool(a.workers, initializer=init, maxtasksperchild=10) as pool:
        for n, r in enumerate(pool.imap_unordered(run, piv), 1):
            out.append(r)
            if n % 50 == 0: print(f'  {n}/{len(piv)} {time.time()-t0:.0f}s', flush=True)
    out.sort(key=lambda r: (r.get('delta') if r.get('delta') is not None else 10 ** 30, r['pivot']))
    json.dump(out, open(a.out, 'w'), sort_keys=True)
    neg = [r for r in out if r.get('delta') is not None and r['delta'] < 0]
    print('pivots with a deletion gain', len(neg), 'of', len(out), {s: sum(1 for r in out if r['status'] == s) for s in {r['status'] for r in out}})
    for r in neg[:40]: print('  ', r['pivot'], 'early', r['early'], r['targets'], 'delta', r['delta'], r['profile'])
