"""G2CLUSTER gfa_test.py: global FA (owned weights + flush) on UP gadgets, the 2-epoch runs, and UP-generator fuzz."""
import sys, random
sys.path.insert(0, 'code/g2cluster')
sys.path.insert(0, 'code/uphase')
from gfa import *
from fuzz import gen

def lifetime_report(res, P, verbose=False):
    """per lifetime: rows, prices, cost, NRI (no flush) + cold => check price <= dim Bl - dim(Bl cap A) <= cost"""
    out = []
    for k, lf in enumerate(res['L']):
        rws = [res['rows'][j] for j in lf['rows']]
        pr = 0
        for (_, w, c, C, kind) in rws:
            e = eff(c, res['fin'])
            if w and e: pr += price(set(w), set(e), P)
        nri = lf['flushes'] == 0
        bound = None
        if nri and lf['cold'] and rws and eff(rws[0][2], res['fin']):
            (_, w, c, C, _), = rws
            A = nri_bound(lf, w)
            Bl = span([P[t] for t in w]) if w else frozenset([0])
            bound = fdim(Bl) - fdim(Bl & A)
        out.append(dict(reg=lf['reg'], cost=lf['cost'], price=pr, nri=nri, cold=lf['cold'], bound=bound, nrows=len(rws)))
        if verbose: print('   life', lf['reg'], 'cost', lf['cost'], 'price', pr, 'NRI', nri, 'cold', lf['cold'], 'bound', bound, 'rows', len(rws))
    return out

def run_named(name, prog, init, P):
    res = gfa(prog, init, P)
    nb, _ = odd_check(res, P, len(P))
    R = sum(lf['cost'] for lf in res['L'])
    print('==', name, '| legality', res['bad'][:2], '| R', R, '| identity fails', res['identity_fail'], '| odd-cell fails', nb,
          '| inv pub/row', res['viol_pub'], res['viol_row'])
    lifetime_report(res, P, verbose=True)

def classify(res, P):
    rep = lifetime_report(res, P)
    ok = all(r['cold'] and (r['nri'] or r['price'] <= r['cost']) for r in rep)
    okstrict = all(r['cold'] and r['nri'] for r in rep)
    return rep, okstrict, ok

if __name__ == '__main__':
    from adjoint import adjoint
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    T = dict(runs=0, idfail=0, invpub=0, invrow=0, adj_idfail=0, lives=0, multi=0, nri_cert=0, nri_price_gt_bound=0, nri_bound_gt_cost=0,
             flushed_cold=0, flushed_cold_price_gt_cost=0, hot=0, F=0, P=0, FuP=0, neither=0, F_sum_gt_R=0, P_sum_gt_R=0,
             best_sum_gt_R=0, neither_sum_gt_R_both=0)
    worst = []
    for it in range(n):
        N = rng.choice([3, 4]); nports = rng.randint(2, 5 if N == 4 else 4)
        prog, init, P = gen(rng, N, nports, rng.randint(1, 3), rng.randint(40, 120))
        res = gfa(prog, init, P)
        if res['bad']: continue
        T['runs'] += 1; T['idfail'] += res['identity_fail'] > 0
        T['invpub'] += res['viol_pub'] > 0; T['invrow'] += res['viol_row'] > 0
        rep, F, _ = classify(res, P)
        ap, ai = adjoint(prog, init, N); ra = gfa(ap, ai, P); T['adj_idfail'] += ra['identity_fail'] > 0
        repa, Pc, _ = classify(ra, P)
        for lf, r in zip(res['L'], rep):
            T['lives'] += 1
            ev = [e[0] for e in lf['events'] if e[0] in 'IO']
            T['multi'] += ('O' in ev and 'I' in ev[ev.index('O'):])
            if not r['cold']: T['hot'] += 1; continue
            if r['nri']:
                if r['bound'] is not None:
                    T['nri_cert'] += 1
                    T['nri_price_gt_bound'] += r['price'] > r['bound']; T['nri_bound_gt_cost'] += r['bound'] > r['cost']
            else:
                T['flushed_cold'] += 1; T['flushed_cold_price_gt_cost'] += r['price'] > r['cost']
        R = sum(r['cost'] for r in rep); sF = sum(r['price'] for r in rep); sP = sum(r['price'] for r in repa)
        T['F'] += F; T['P'] += Pc; T['FuP'] += F or Pc; T['neither'] += not (F or Pc)
        T['F_sum_gt_R'] += F and sF > R; T['P_sum_gt_R'] += Pc and sP > R
        T['best_sum_gt_R'] += min(sF, sP) > R
        if not (F or Pc) and min(sF, sP) > R: T['neither_sum_gt_R_both'] += 1; worst.append((len(prog), it))
    print('FUZZ', T)
    print('smallest runs where both FA and PA row sums exceed R:', sorted(worst)[:5])
