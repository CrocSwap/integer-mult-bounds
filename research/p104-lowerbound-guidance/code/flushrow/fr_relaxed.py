"""FLUSHROW fr_relaxed.py (own code): cost-0 counter-run in the RELAXED model (UP sec.1 / G2C: helper finals only need a
y-cold final, helpers need not restore their token).  Port-general: works for ANY label set Q.
Per port t (helper H_t with token h_t, Y_t at {0}, X_t at <q_t>):
  INIT A@{0}; A += H_t; H_t -= A; CLEAR A          (blank the helper: H_t = 0, token discarded, cost 0)
  H_t += Y_t; MOVE H_t -> <q_t>                   (public carries y_t up for free; now HOT)
  X_t -= H_t                                      (X_t = x_t - y_t, public hot delivery O3)
  INIT B@<q_t>; B += H_t; H_t -= B; CLEAR B        (clean H_t: H_t = 0, y-cold; cost 0)
Exact replay with the G2C global-FA engine.  CONTROL: the same run under the PINNED model (helper final must equal its token)
is flagged (every helper ends at 0 != h_t); and the honest per-port run (owned climbs {0}->{<q_t>}) has R = |Q|."""
import sys, pickle
sys.path.insert(0, 'code/g2cluster')
sys.path.insert(0, 'code/uphase')
from gfa import *

def relaxed_run(P):
    init, prog = {}, []
    Z = frozenset([0])
    for t, q in enumerate(P):
        init[('X', t)] = (span([q]), {('x', t): Fr(1)}); init[('Y', t)] = (Z, {('y', t): Fr(1)})
        init[('H', t)] = (Z, {('h', t): Fr(1)})
    for t, q in enumerate(P):
        H, X, Y, L = ('H', t), ('X', t), ('Y', t), span([q])
        prog += [('INIT', ('A', t), Z, {}, True), ('ADD', ('A', t), Fr(1), H), ('ADD', H, Fr(-1), ('A', t)), ('CLEAR', ('A', t))]
        prog += [('ADD', H, Fr(1), Y), ('MOVE', H, L), ('ADD', X, Fr(-1), H)]
        prog += [('INIT', ('B', t), L, {}, True), ('ADD', ('B', t), Fr(1), H), ('ADD', H, Fr(-1), ('B', t)), ('CLEAR', ('B', t))]
    return prog, init

def honest_run(P):
    init, prog = {}, []
    Z = frozenset([0])
    for t, q in enumerate(P):
        init[('X', t)] = (span([q]), {('x', t): Fr(1)}); init[('Y', t)] = (Z, {('y', t): Fr(1)})
        init[('H', t)] = (Z, {('h', t): Fr(1)})
    for t, q in enumerate(P):
        O = ('O', t)
        prog += [('INIT', O, Z, {}, True), ('ADD', O, Fr(1), ('Y', t)), ('MOVE', O, span([q])), ('ADD', ('X', t), Fr(-1), O), ('CLEAR', O)]
    return prog, init

def check(name, prog, init, P):
    res = gfa(prog, init, P)
    n = len(P); R = sum(lf['cost'] for lf in res['L'])
    fin = res['fin']
    exact = all(fin[('X', t)] == {('x', t): Fr(1), ('y', t): Fr(-1)} for t in range(n)) and all(fin[('Y', t)] == {('y', t): Fr(1)} for t in range(n))
    # helper finals: y-part cold at final chart (relaxed rule) / equal to token (pinned rule)
    hy = 0; hpin = 0
    for t in range(n):
        f = fin[('H', t)]
        hy += any(k[0] == 'y' for k in f)          # any y at all (stronger than y-cold)
        hpin += f != {('h', t): Fr(1)}
    nb, effs = odd_check(res, P, n)
    pr = sum(price(set(w), set(e), P) for w, e in effs if w and e)
    print('==', name, '| ports', n, '| legality problems', len(res['bad']), '| R', R, '| X,Y finals exact (X=x-y, Y=y)', exact,
          '| helper finals with any y', hy, '| helpers NOT restored (pinned violations)', hpin,
          '| identity fails', res['identity_fail'], '| odd-cell fails', nb, '| inv pub/row', res['viol_pub'], res['viol_row'],
          '| FA row price sum', pr)
    return R, exact, hy, hpin

if __name__ == '__main__':
    d = pickle.load(open('code/halvpay/f56run_nomix.pkl', 'rb'))
    P104 = d['P']
    for name, P in [('{1,2,7}', [1, 2, 7]), ('Fano-odd F2^4 (8 ports)', [v for v in range(1, 16) if bin(v).count('1') % 2]),
                    ('Q96', P104[:96]), ('P104', P104)]:
        check('RELAXED counter-run on ' + name, *relaxed_run(P), P)
        check('honest control on ' + name, *honest_run(P), P)
