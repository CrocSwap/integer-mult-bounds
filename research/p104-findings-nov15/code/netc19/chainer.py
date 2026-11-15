"""NETC11: greedy window chainer.  plan_chains(N, P, hidx, maxend) -> list of chain dicts(hs, diffs)."""
from diffsolve import *

def units(N, H0):
    U = {}
    for i, h in enumerate(H0):
        b = h['block']; U[i] = dict(G=b['frame'], t1=b['t1'], r=b['r'], u=N.udeliv(h), blk=id(b))
    return U

def plan_chains(N, P, H0, U, hidx, maxend=12, log=None):
    hidx = sorted(hidx, key=lambda i: (U[i]['t1'], i))
    chains = []; cost = {i: N.hcost(H0[i])[0] for i in hidx}
    sp = N.w.sp; tried = 0; ok = 0
    for i in hidx:
        best = None
        ends = [c for c in chains if U[c['hs'][-1]]['t1'] < U[i]['t1'] and sp[U[c['hs'][-1]]['G']] <= sp[U[i]['G']]]
        ends.sort(key=lambda c: -U[c['hs'][-1]]['t1'])
        for c in ends[:maxend]:
            e = U[c['hs'][-1]]; tried += 1
            excl = {U[h]['r'] for h in c['hs']}
            d = solve_diff(N, P, e, U[i], excl)
            if d is None: continue
            ok += 1
            new = N.merge(H0, c['hs'] + [i], c['diffs'] + [d]); cn = N.hcost(new)[0]
            sav = c['cost'] + cost[i] - cn
            if sav > 1e-9 and (best is None or sav > best[0]): best = (sav, c, d, cn)
        if best is None: chains.append(dict(hs=[i], diffs=[], cost=cost[i])); continue
        sav, c, d, cn = best
        c['hs'].append(i); c['diffs'].append(d); c['cost'] = cn
    if log: log('tried %d solved %d' % (tried, ok))
    return [c for c in chains if len(c['hs']) > 1]
