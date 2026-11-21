"""FLUSHROW fr_pinned.py (own code): the hot carry in the PINNED model (helpers restore their token exactly).
Per port t: helper H_t (token h_t) absorbs y_t at {0} and ascends to <q_t> for free; O'_t copies h_t at {0} and CLIMBS to <q_t>
(cost 1); O_t is born at <q_t>, takes h_t+y_t from H_t, subtracts O'_t (-> y_t), delivers -y_t into X_t and restores H_t := h_t.
Exact replay: R = |Q|, all finals pinned; per-lifetime FA rows: O_t price 1 at cost 0 (HOT intake), O'_t price 0 at cost 1.
=> even with pinned helpers no per-lifetime law closes (b); the row must be re-charged to the token carrier O'_t."""
import sys, pickle
sys.path.insert(0, 'code/g2cluster')
sys.path.insert(0, 'code/uphase')
from gfa import *

def pinned_run(P):
    init, prog = {}, []; Z = frozenset([0])
    for t, q in enumerate(P):
        init[('X', t)] = (span([q]), {('x', t): Fr(1)}); init[('Y', t)] = (Z, {('y', t): Fr(1)}); init[('H', t)] = (Z, {('h', t): Fr(1)})
    for t, q in enumerate(P):
        H, L, O, Op = ('H', t), span([q]), ('O', t), ('Op', t)
        prog += [('INIT', Op, Z, {}, True), ('ADD', Op, Fr(1), H), ('ADD', H, Fr(1), ('Y', t)), ('MOVE', H, L), ('MOVE', Op, L),
                 ('INIT', O, L, {}, True), ('ADD', O, Fr(1), H), ('ADD', O, Fr(-1), Op), ('ADD', ('X', t), Fr(-1), O),
                 ('ADD', H, Fr(-1), O), ('CLEAR', O), ('CLEAR', Op)]
    return prog, init

if __name__ == '__main__':
    d = pickle.load(open('code/halvpay/f56run_nomix.pkl', 'rb'))
    for name, P in [('{1,2,7}', [1, 2, 7]), ('Q96', d['P'][:96])]:
        prog, init = pinned_run(P); res = gfa(prog, init, P); n = len(P)
        pinned = all(res['fin'][k] == ({('x', k[1]): Fr(1), ('y', k[1]): Fr(-1)} if k[0] == 'X' else c) for k, (f, c) in init.items())
        nb, effs = odd_check(res, P, n)
        per = collections.Counter()
        for k, lf in enumerate(res['L']):
            pr = 0
            for j in lf['rows']:
                (_, w, c, C, _) = res['rows'][j]; e = eff(c, res['fin'])
                if w and e: pr += price(set(w), set(e), P)
            per[(lf['reg'][0], lf['cost'], pr, lf['cold'])] += 1
        print(name, '| legal', not res['bad'], '| all finals pinned', pinned, '| R', sum(lf['cost'] for lf in res['L']),
              '| identity fails', res['identity_fail'], '| odd fails', nb, '| lifetimes (kind, cost, price, eff-cold): count', dict(per))
