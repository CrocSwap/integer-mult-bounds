"""SEPPAYS arun_check.py (own code): Task 0. Check the FLUSHROW relaxed cost-0 run against EVERY constructor premise of
FutureAttr.lean's ARun (hne, hch, hgtd, hcold; down/upOwn/upPub chart premises; init on owned) and the final-data
hypotheses of attribution_decoder (h0, hq, hfx, hfy, hfyX, hbal).  ARun has no separate CLEAR: `init` resets an owned
register to 0 (closing its lifetime); owned registers keep a chart, so B is given start chart <q_t> (s0 is arbitrary).
eff(c)[u] = c[y_u] - sum_v c[x_v] Fy[v][u],  Fy = y-part of final X.  hcold: owned d, l*eff(c_e)[u] != 0 => chart(d) <= q_u^perp."""
from fractions import Fraction as Fr
import sys
sys.path.insert(0, '.')
from eng import span, dot, fdim

def check(P, variant='relaxed'):
    T = len(P); Z = frozenset([0])
    ch, v = {}, {}
    pub = set()
    for t, q in enumerate(P):
        ch[('X', t)] = span([q]); v[('X', t)] = {('x', t): Fr(1)}
        ch[('Y', t)] = Z; v[('Y', t)] = {('y', t): Fr(1)}
        ch[('H', t)] = Z; v[('H', t)] = {('h', t): Fr(1)}
        pub |= {('X', t), ('Y', t), ('H', t)}
        ch[('A', t)] = Z; v[('A', t)] = {}
        ch[('B', t)] = span([q]); v[('B', t)] = {}
        if variant == 'honest': ch[('O', t)] = Z; v[('O', t)] = {}
    prog = []
    for t, q in enumerate(P):
        H, X, Y, A, B, L = ('H', t), ('X', t), ('Y', t), ('A', t), ('B', t), span([q])
        if variant == 'relaxed':
            prog += [('add', A, 1, H), ('add', H, -1, A), ('init', A), ('add', H, 1, Y), ('upPub', H, L), ('add', X, -1, H),
                     ('add', B, 1, H), ('add', H, -1, B), ('init', B)]
        else:
            O = ('O', t)
            prog += [('add', O, 1, Y), ('upOwn', O, L), ('add', X, -1, O), ('init', O)]
    # pass 1: run to get finals (Fy)
    def run(record):
        c = {k: dict(x) for k, x in v.items()}; h = dict(ch); dep = {k: False for k in v}; fails = []; cost = 0
        for i, op in enumerate(prog):
            if op[0] == 'add':
                _, d, l, e = op
                if d == e: fails.append((i, 'hne'))
                if not h[d] <= h[e]: fails.append((i, 'hch'))
                if d not in pub:
                    if dep[d]: fails.append((i, 'hgtd'))
                    if record is not None:
                        Fy = record
                        ec = {}
                        for sym, val in c[e].items():
                            if sym[0] == 'y': ec[sym[1]] = ec.get(sym[1], 0) + val
                            if sym[0] == 'x':
                                for u, fy in Fy[sym[1]].items(): ec[u] = ec.get(u, 0) - val * fy
                        hot = [u for u, val in ec.items() if l * val != 0 and any(dot(a, P[u]) for a in h[d])]
                        if hot: fails.append((i, 'hcold', d, 'hot ports', hot, 'chart dim', fdim(h[d])))
                if d in pub and e not in pub: dep[e] = True
                for sym, val in c[e].items():
                    c[d][sym] = c[d].get(sym, 0) + l * val
                    if c[d][sym] == 0: del c[d][sym]
            elif op[0] == 'init':
                c[op[1]] = {}; dep[op[1]] = False
            elif op[0] == 'upPub':
                if op[1] not in pub or not h[op[1]] <= op[2]: fails.append((i, 'upPub'))
                h[op[1]] = op[2]
            elif op[0] == 'upOwn':
                if op[1] in pub or not h[op[1]] <= op[2]: fails.append((i, 'upOwn'))
                cost += fdim(op[2]) - fdim(h[op[1]]); h[op[1]] = op[2]
        return c, h, fails, cost
    c, h, _, cost = run(None)
    Fy = {t: {sym[1]: val for sym, val in c[('X', t)].items() if sym[0] == 'y'} for t in range(T)}
    c, h, fails, cost = run(Fy)
    # final-data hypotheses
    fin = []
    for r in pub:
        for u in range(T):
            want = Fr(1) if r == ('X', u) else Fr(0)
            if c[r].get(('x', u), 0) != want: fin.append(('hfx', r, u))
        if r[0] != 'X':
            for sym, val in c[r].items():
                if sym[0] == 'y' and any(dot(a, P[sym[1]]) for a in h[r]): fin.append(('hfy', r, sym))
    for t in range(T):
        for u in range(T):
            if c[('X', t)].get(('x', u), 0) != v[('X', t)].get(('x', u), 0): fin.append(('hbal', t, u))
    for t, q in enumerate(P):
        if q not in ch[('X', t)]: fin.append(('hq', t))
    rec_ok = all(Fy[t] == {t: Fr(-1)} for t in range(T))
    restored = sum(c[('H', t)] == {('h', t): Fr(1)} for t in range(T))
    return cost, fails, fin, rec_ok, restored

if __name__ == '__main__':
    for name, P in [('{1,2,7}', [1, 2, 7]), ('F2^4 odd', [v for v in range(1, 16) if bin(v).count('1') % 2])]:
        for var in ['relaxed', 'honest']:
            cost, fails, fin, rec_ok, restored = check(P, var)
            kinds = sorted({f[1] for f in fails})
            print(f'{name:9s} {var:8s} R={cost} receipts=-I:{rec_ok} helpers restored {restored}/{len(P)} | ARun premise failures: {len(fails)} kinds {kinds} | final-data failures: {len(fin)}')
            for f in fails[:2]: print('    e.g.', f)
