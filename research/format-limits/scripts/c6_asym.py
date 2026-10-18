"""Asymmetric pairing uniqueness: at the E8-linear decoder pattern the F_2 pairing is unique up to gauge at window <= 9.

Setting.  A cross-field unit on v ports has a decoder N over Q and an F_2 pairing B = W U^T, B_TS = <w_T, u_S>, between
sink words w_T and source labels u_S in F_2^c.  Lossless correction of the garbage N_TS x_S needs B_TS = 0, exactness
needs N o B = diag (N_TT != 0, B_TT = 1).  The window is the F_2 rank of B and the copy cost of a total j is
rank B[readers_j, sources_j].  The pair (U, W) -> (U P, W P^-T) with P in GL(c, F_2) leaves B fixed, so 'W != U' is
meaningful only through B != B^T or B != B0 = (J + G) mod 2, the pairing of the symmetric unit.

The E8-linear decoder pattern.  Ports are root lines of E8 (e8units.hamming_e8: 8 coordinate lines and the 112 code
lines, G = L L^T / 2); the decoder is the sum of the 8 coordinate terms N = G/2, so N_TS != 0 exactly where
G_TS != 0.  B must therefore vanish on every ordered pair with G_TS != 0 (T != S) and have unit diagonal.  P120 is the
set of all 120 lines, P112 the 112 code lines.  Gauge: K = a set of 8 pairwise non-orthogonal lines has B[K,K] = I
forced, which brings U_K = W_K to [I_8 | 0] (valid for every c >= 8).

Checks (Cadical 1.5.3 through pysat; minrank_sat.py):
* c = 9 on P112: a non-symmetric B is UNSAT; B != B0 on some free pair is UNSAT; with U fixed to the E8 labels and W free,
  a non-symmetric B is UNSAT; the unconstrained problem is SAT and every solution has B = B0 of rank 9.
* c = 9 on P120: non-symmetric B UNSAT; B != B0 UNSAT.
* c = 8 on the pattern of all 120 lines: UNSAT for symmetric and for non-symmetric words (and on P112).
  c = 9 with non-symmetric words is SAT (calibration of the encoding).
* an exact asymmetric 2-target unit on P112: relaxing two targets (sinks w_t != u_t) with one shared extra total of 24
  sources and copy cost 1 gives B != B0 at copy cost 8*8 + 1 = 65 and window 9, N' o B = diag on all 112 x 112 entries
  (rationals), the relaxed targets need 28 corrections instead of 52.
* an exact asymmetric toy: the directed 3-cycle with B non-symmetric of rank 2, decoded exactly on all 343 inputs.
Run: python3 c6_asym.py
"""
import itertools
import time
from fractions import Fraction as Fr

import numpy as np

from report import check, finish
from e8units import hamming_e8, e8_labels, f2_rank, first_clique, rank_q
from minrank_sat import solve_minrank, solve_asym

# ---------------------------------------------------------------------------------------------------------------
# expected values (from the recorded runs)
EXPECTED = {
    'ncl': 8,                                    # size of the gauge clique
    'sat': {                                     # (set, c, mode) -> result
        ('P112', 9, 'nonsym'): 'UNSAT', ('P112', 9, 'neB0'): 'UNSAT', ('P112', 9, 'fixU_nonsym'): 'UNSAT',
        ('P120', 9, 'nonsym'): 'UNSAT', ('P120', 9, 'neB0'): 'UNSAT',
        ('P112', 9, 'none'): 'SAT', ('P112', 9, 'fixU_none'): 'SAT',
    },
    'minrank': {('P120', 8, 'sym'): 'UNSAT', ('P120', 8, 'nonsym'): 'UNSAT', ('P120', 9, 'nonsym'): 'SAT'},
    'rankB0': 9,
    'unit': {      # d0 -> (relaxed lines, sinks, extra-total sources, corrections of a relaxed target)
        75: ([75, 76], [329, 438]), 76: ([75, 76], [329, 438]), 77: ([74, 77], [378, 389])},
    'unit_common': dict(Qsize=24, beta_alpha=1, beta_coord=[8] * 8, rankB=9, corr_relaxed=28, corr_E8=52, copy_cost=65),
    'toy3': dict(betas=[2, 2], cst=4, rankB=2, rankN=2, inputs=343, D=(-6, -12)),
}


# ---------------------------------------------------------------------------------------------------------------
class Geometry:
    def __init__(self):
        self.L, self.G = hamming_e8()
        self.U9 = e8_labels(self.G)                    # 120 x 9, U9 U9^T = (J + G) mod 2
        self.M0 = ((1 + self.G) % 2).astype(np.uint8)

    def port_set(self, name):
        return list(range(8, 120)) if name == 'P112' else list(range(120))

    def pattern(self, P):
        """ordered pairs (i, j), i != j, of positions in P with G != 0."""
        return {(i, j) for i in range(len(P)) for j in range(len(P)) if i != j and self.G[P[i], P[j]] != 0}

    def clique(self, P, size=8):
        adj = [[i != j and self.G[P[i], P[j]] != 0 for j in range(len(P))] for i in range(len(P))]
        return first_clique(adj, size), first_clique(adj, size + 1)


def sat_checks(geo):
    t_all = time.time()
    got = {}
    for name in ('P112', 'P120'):
        P = geo.port_set(name)
        pat = geo.pattern(P)
        K, K9 = geo.clique(P, EXPECTED['ncl'])
        assert K is not None and K9 is None, 'the largest set of pairwise non-orthogonal lines has 8 elements'
        B0 = geo.M0[np.ix_(P, P)]
        U = geo.U9[P]
        runs = [(9, 'nonsym', None), (9, 'neB0', None)]
        if name == 'P112':
            runs += [(9, 'none', None), (9, 'nonsym', U), (9, 'none', U)]
        for c, mode, Ufix in runs:
            r = solve_asym(len(P), pat, B0, c, mode, K, U_fixed=Ufix)
            key = (name, c, ('fixU_' + mode) if Ufix is not None else mode)
            got[key] = r
            extra = ''
            if r['result'] == 'SAT':
                Bm = r['B']
                extra = '; B == B0: %s, rank_F2 B = %d' % (bool((Bm == B0).all()), f2_rank(Bm.astype(np.uint8)))
            print('   %s c=%d %-12s %s (%.1f s, %d vars, %d clauses)%s' % (name, c, key[2], r['result'], r['sec'], r['vars'],
                                                                         r['clauses'], extra), flush=True)
    ok_all = True
    for key, want in EXPECTED['sat'].items():
        ok_all &= got[key]['result'] == want
    names = {('P112', 9, 'nonsym'): 'C6.P112.c9.nonsym', ('P112', 9, 'neB0'): 'C6.P112.c9.neB0',
             ('P112', 9, 'fixU_nonsym'): 'C6.P112.c9.fixU_nonsym', ('P120', 9, 'nonsym'): 'C6.P120.c9.nonsym',
             ('P120', 9, 'neB0'): 'C6.P120.c9.neB0'}
    text = {'nonsym': 'no non-symmetric pairing (B_TS != B_ST on some free pair)',
            'neB0': 'no pairing with B != B0 = (J+G) mod 2 on a free pair',
            'fixU_nonsym': 'U fixed to the E8 labels, W free: no non-symmetric pairing'}
    for key, cid in names.items():
        r = got[key]
        check(cid, r['result'] == EXPECTED['sat'][key],
              '%s at window 9 under the E8-linear pattern: %s -> %s (%.1f s)' % (key[0], text[key[2]], r['result'], r['sec']))
    # calibration: unconstrained is SAT and forces B = B0
    P = geo.port_set('P112')
    B0 = geo.M0[np.ix_(P, P)]
    cal = {}
    for key in (('P112', 9, 'none'), ('P112', 9, 'fixU_none')):
        r = got[key]
        okB = r['result'] == 'SAT' and bool((r['B'] == B0).all()) and f2_rank(r['B'].astype(np.uint8)) == EXPECTED['rankB0']
        cal[key] = okB
    check('C6.P112.c9.calibration', all(cal.values()) and all(got[k]['result'] == 'SAT' for k in cal),
          'unconstrained c=9 (and with U fixed) is SAT; the solution has B = B0 = (J+G) mod 2 of F_2 rank %d' % EXPECTED['rankB0'])
    print('  (window-9 SAT runs: %.1f s)' % (time.time() - t_all), flush=True)
    return got


def window8_checks(geo):
    t0 = time.time()
    P = geo.port_set('P120')
    off = sorted((i, j) for (i, j) in geo.pattern(P) if i < j)
    K, _ = geo.clique(P, 8)
    res = {}
    for c, sym in ((8, True), (8, False), (9, False)):
        r = solve_minrank(len(P), off, c, sym, K)
        res[(c, sym)] = r
        print('   pattern of 120 lines, c=%d %s: %s (%.1f s, %d vars, %d clauses)' % (c, 'sym' if sym else 'nonsym', r[0], r[1], r[2], r[3]),
              flush=True)
    check('C6.P120.c8.sym', res[(8, True)][0] == EXPECTED['minrank'][('P120', 8, 'sym')],
          '120-line pattern (%d off-cap pairs), symmetric words at window 8: %s' % (len(off), res[(8, True)][0]))
    check('C6.P120.c8.nonsym', res[(8, False)][0] == EXPECTED['minrank'][('P120', 8, 'nonsym')],
          '120-line pattern, non-symmetric words at window 8: %s' % res[(8, False)][0])
    check('C6.P120.c9.minrank_calibration', res[(9, False)][0] == EXPECTED['minrank'][('P120', 9, 'nonsym')],
          '120-line pattern, non-symmetric words at window 9 (the encoding finds solutions): %s (%.1f s)'
          % (res[(9, False)][0], res[(9, False)][1]))
    P112 = geo.port_set('P112')
    off112 = sorted((i, j) for (i, j) in geo.pattern(P112) if i < j)
    K112, _ = geo.clique(P112, 8)
    r112 = solve_minrank(len(P112), off112, 8, False, K112)
    print('   pattern of the 112 code lines, c=8 nonsym: %s (%.1f s)' % (r112[0], r112[1]), flush=True)
    check('C6.P112.c8.nonsym', r112[0] == 'UNSAT', '112-line pattern, non-symmetric words at window 8: %s' % r112[0])
    print('  (window-8 runs: %.1f s)' % (time.time() - t0), flush=True)


# ---------------------------------------------------------------------------------------------------------------
def bits9(w):
    return [(w >> (8 - j)) & 1 for j in range(9)]


def int9(row):
    return int(''.join(str(int(x)) for x in row), 2)


def asym_unit(geo):
    """exact 2-target asymmetric P112 unit.  Relax two targets: sink w_t != u_t, decoder row n_t = L d + mu L e + alpha
    where d, e are root vectors and alpha is the extra total with sources Q (coefficients -<L_S, d>)."""
    t0 = time.time()
    L, G, U9 = geo.L, geo.G, geo.U9
    P = geo.port_set('P112')
    v = len(P)
    Lp = L[P].astype(np.int64)
    u = np.array([[int(x) for x in U9[p]] for p in P], dtype=np.int64)
    Wall = np.array([bits9(w) for w in range(512)], dtype=np.int64)
    Zall = (Wall @ u.T) % 2 == 1                     # Zall[w, t]: <w, u_t> = 1
    uint = [int9(U9[p]) for p in P]

    def nodes_of(e, d0):
        pe, pd = Lp @ e, Lp @ d0
        eperp = pe == 0
        V2 = eperp & (pd == 0)
        out = []
        for t in range(v):
            for w in range(1, 512):
                if not Zall[w, t] or w == uint[t]:
                    continue
                Z = Zall[w].copy()
                Z[t] = False
                o = np.nonzero(Z & ~eperp)[0]
                mus = {Fr(-int(pd[S]), int(pe[S])) for S in o}
                if len(mus) > 1:
                    continue
                if mus:
                    mu = mus.pop()
                else:
                    mu = next(Fr(k) for k in range(1, 50) if pd[t] + k * pe[t] != 0) if (pd[t] or pe[t]) else None
                if mu is None or pd[t] + mu * pe[t] == 0:
                    continue
                E = Z & eperp & ~V2
                if E[t]:
                    continue
                out.append((t, w, mu, E))
        return out

    res = {}
    for (ei, di) in [(0, 75), (0, 76), (0, 77)]:
        e, d0 = L[ei], L[di]
        ns = nodes_of(e, d0)
        pair = None
        for a in range(len(ns)):
            for b in range(a + 1, len(ns)):
                ta, wa, ma, Ea = ns[a]
                tb, wb, mb, Eb = ns[b]
                if ta != tb and not (Ea & ~Zall[wb]).any() and not (Eb & ~Zall[wa]).any() and not Ea[tb] and not Eb[ta]:
                    pair = (ns[a], ns[b])
                    break
            if pair:
                break
        (ta, wa, ma, Ea), (tb, wb, mb, Eb) = pair
        Q = Ea | Eb
        sinks = {t: uint[t] for t in range(v)}
        sinks[ta], sinks[tb] = wa, wb
        Wm = np.array([bits9(sinks[t]) for t in range(v)], dtype=np.int64)
        B = (Wm @ u.T) % 2
        alpha = {S: -Fr(int(Lp[S] @ d0)) for S in np.nonzero(Q)[0]}
        N = [[Fr(int(G[P[t], P[S]]), 2) for S in range(v)] for t in range(v)]
        for t, mu in ((ta, ma), (tb, mb)):
            vec = [Fr(int(d0[i])) + mu * Fr(int(e[i])) for i in range(8)]
            N[t] = [sum(Fr(int(Lp[S][i])) * vec[i] for i in range(8)) + alpha.get(S, 0) for S in range(v)]
        exact = all((t == S) or N[t][S] == 0 or B[t, S] == 0 for t in range(v) for S in range(v)) and \
            all(B[t, t] == 1 and N[t][t] != 0 for t in range(v))
        Qi = list(np.nonzero(Q)[0])
        beta_alpha = f2_rank(B[np.ix_([ta, tb], Qi)].astype(np.uint8))
        beta_coord = [f2_rank(B[np.ix_([t for t in range(v) if Lp[t, a] != 0 or t in (ta, tb)],
                                       [S for S in range(v) if Lp[S, a] != 0])].astype(np.uint8)) for a in range(8)]
        corr = {int(t): sum(1 for S in range(v) if S != t and N[t][S] != 0) for t in (ta, tb)}
        B0 = geo.M0[np.ix_(P, P)]
        res[di] = dict(relaxed=[int(P[ta]), int(P[tb])], sinks=[int(wa), int(wb)], mu=[str(ma), str(mb)], exact=bool(exact),
                       Qsize=len(Qi), beta_alpha=int(beta_alpha), beta_coord=[int(b) for b in beta_coord],
                       rankB=int(f2_rank(B.astype(np.uint8))), corr=corr, differs_from_B0=int((B != B0).sum()),
                       asym_pairs=int((B != B.T).sum() // 2), nodes=len(ns))
        print('   pencil e=line %d, d0=line %d: %s' % (ei, di, res[di]), flush=True)
    Ex, Exc = EXPECTED['unit'], EXPECTED['unit_common']
    ok = True
    for di, r in res.items():
        ok &= r['relaxed'] == Ex[di][0] and r['sinks'] == Ex[di][1] and r['exact'] and r['Qsize'] == Exc['Qsize'] \
            and r['beta_alpha'] == Exc['beta_alpha'] and r['beta_coord'] == Exc['beta_coord'] and r['rankB'] == Exc['rankB'] \
            and set(r['corr'].values()) == {Exc['corr_relaxed']} and r['differs_from_B0'] > 0
    r = res[75]
    cost = sum(r['beta_coord']) + r['beta_alpha']
    check('C6.unit.exact', ok and cost == Exc['copy_cost'],
          '2-target asymmetric P112 unit (3 pencils): N\' o B = diag on 112 x 112 rational entries; relaxed lines %s with sinks %s '
          '(w != u); extra total: %d sources, copy cost %d; 8 coordinate totals at 8 each; copy cost %d total, window rank B = %d'
          % (r['relaxed'], r['sinks'], r['Qsize'], r['beta_alpha'], cost, r['rankB']))
    check('C6.unit.corrections', all(set(r['corr'].values()) == {Exc['corr_relaxed']} for r in res.values()),
          'relaxed targets need %s corrections instead of %d' % (sorted({c for r in res.values() for c in r['corr'].values()}),
                                                                   Exc['corr_E8']))
    check('C6.unit.not_gauge', all(r['differs_from_B0'] > 0 and r['asym_pairs'] > 0 for r in res.values()),
          'B differs from B0 in %s entries and is non-symmetric on %s pairs (not a gauge of the symmetric unit)'
          % ([r['differs_from_B0'] for r in res.values()], [r['asym_pairs'] for r in res.values()]))
    print('  (2-target unit: %.1f s)' % (time.time() - t0), flush=True)


# ---------------------------------------------------------------------------------------------------------------
def toy3():
    """directed 3-cycle: U = (10,01,11), W = (10,11,01) in F_2^2, B = W U^T non-symmetric; decoder N of rank 2."""
    U = [(1, 0), (0, 1), (1, 1)]
    W = [(1, 0), (1, 1), (0, 1)]
    B = [[sum(a * b for a, b in zip(W[t], U[s])) % 2 for s in range(3)] for t in range(3)]
    N = [[Fr(1), Fr(1), Fr(0)], [Fr(0), Fr(1), Fr(1)], [Fr(-1), Fr(0), Fr(1)]]
    ok_pattern = all((N[t][s] == 0) or (t == s) or B[t][s] == 0 for t in range(3) for s in range(3)) and \
        all(B[t][t] == 1 and N[t][t] != 0 for t in range(3))
    # totals tau1 = x1 + x2 (read by ports 1, 3), tau2 = x2 + x3 (read by ports 2, 3)
    terms = [({0, 2}, {0, 1}, {0: Fr(1), 2: Fr(-1)}, {0: Fr(1), 1: Fr(1)}),
             ({1, 2}, {1, 2}, {1: Fr(1), 2: Fr(1)}, {1: Fr(1), 2: Fr(1)})]        # (readers, sources, reader coeffs, source coeffs)
    Nr = [[sum(rd.get(t, 0) * ad.get(s, 0) for _, _, rd, ad in terms) for s in range(3)] for t in range(3)]
    n_inputs = 0
    exact = Nr == N
    for x in itertools.product(range(-3, 4), repeat=3):
        x = [Fr(a) for a in x]
        tau = [sum(ad[s] * x[s] for s in ad) for _, _, _, ad in terms]
        for t in range(3):
            y = sum(rd.get(t, 0) * tau[j] for j, (_, _, rd, _) in enumerate(terms))
            for s in range(3):
                if s != t and N[t][s] != 0:
                    if B[t][s] != 0:
                        exact = False        # a lossless correction is only legal on pairs with B_TS = 0
                    y -= N[t][s] * x[s]
            exact &= (y == N[t][t] * x[t])
        n_inputs += 1
    betas = [f2_rank(np.array([[B[t][s] for s in sorted(A)] for t in sorted(R)], dtype=np.uint8)) for R, A, _, _ in terms]
    Ex = EXPECTED['toy3']
    sym = B == [list(r) for r in zip(*B)]
    rankB = f2_rank(np.array(B, dtype=np.uint8))
    rankN = rank_q([[int(x) for x in row] for row in N])
    D = (2 * 3 - 3 * sum(betas), 8 * 3 - 9 * sum(betas))
    check('C6.toy3', ok_pattern and exact and not sym and n_inputs == Ex['inputs'] and betas == Ex['betas']
          and sum(betas) == Ex['cst'] and rankB == Ex['rankB'] and rankN == Ex['rankN'] and D == Ex['D'],
          'directed 3-cycle: B = %s non-symmetric, rank_F2 B = %d, rank_Q N = %d; decoded exactly on all %d integer inputs '
          '(corrections only where B_TS = 0); betas %s, cst %d, D at s=3,9: %s (<0: formalism toy)'
          % (B, rankB, rankN, n_inputs, betas, sum(betas), D))


def main():
    t_start = time.time()
    geo = Geometry()
    sat_checks(geo)
    window8_checks(geo)
    asym_unit(geo)
    toy3()
    print('total %.1f s' % (time.time() - t_start))
    finish()


if __name__ == '__main__':
    main()
