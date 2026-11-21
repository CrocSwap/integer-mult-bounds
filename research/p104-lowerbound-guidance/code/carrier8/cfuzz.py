"""CARRIER8 cfuzz.py (own code): random PINNED carrier runs (eng legality: ADD d += lam*s needs chart(d) <= chart(s);
publics ascend, Y_s inside q_s^perp; owned nested moves, free INIT/descents, R = ascents) fed to pa.analyze.
Shapes: owned deposits into Y/H publics (frozen until it cleans them itself), hot pickups by other owned registers
(descend to the carrier chart, then read), X reads of dirty publics (public hot delivery), public->public relays
(source frozen until undone), owned->owned reads, multi-epoch lifetimes, re-INIT anywhere.
Checks: legality, pinned, PA identity, cold/chart facts, C = c + N C, receipts, relay legality, per-epoch segment bound,
acyclicity, R >= own-price, R >= drops >= level-cut sum.  Teeth: routing mass (one row per source content, total weight) > R."""
import random, sys
from fractions import Fraction as Fr
sys.path.insert(0, '.')
from pa import *

def rnd_sub(rng, n, k):
    return span([rng.randrange(1, 1 << n) for _ in range(k)])

def gen(n, P, F, rng, nh=1, steps=70):
    T = len(P)
    pub = {}
    for t, q in enumerate(P):
        pub[('X', t)] = [span([q]), {('x', t): F.c(1)}]; pub[('Y', t)] = [frozenset([0]), {('y', t): F.c(1)}]
    for j in range(nh): pub[('H', j)] = [frozenset([0]), {('h', j): F.c(1)}]
    init = {k: (v[0], dict(v[1])) for k, v in pub.items()}
    own = {}; obl = {}; pobl = []; pfro = {}
    ops = []; cnt = [0]
    scal = [1] if F.p == 2 else [1, -1, Fr(1, 2), 2, Fr(-3, 2)]
    ch = lambda r: (pub[r] if r in pub else own[r])[0]
    def setch(r, D):
        ops.append(('MOVE', r, D)); (pub[r] if r in pub else own[r])[0] = D
    def add(d, lam, s):
        ops.append(('ADD', d, lam, s)); dc = (pub[d] if d in pub else own[d])[1]; sc = (pub[s] if s in pub else own[s])[1]
        addv(F, dc, F.c(lam), dict(sc))
    def climb(o, C):
        D = join(ch(o), C)
        if D != ch(o): setch(o, D)
    def ycap(r, D):   # may public r take chart D?
        if r[0] == 'Y' and any(dot(v, P[r[1]]) for v in basis(D)): return False
        for (Pd, Q, lam) in pobl:
            if Pd == r and not D <= ch(Q): return False
        return True
    nonX = [k for k in pub if k[0] != 'X']
    for _ in range(steps):
        x = rng.random()
        if x < 0.07 or not own:
            o = ('O', cnt[0]); cnt[0] += 1; C = rnd_sub(rng, n, rng.randrange(0, 3))
            own[o] = [C, {}]; obl[o] = []; ops.append(('INIT', o, C)); continue
        o = rng.choice(list(own)); C = ch(o); frozen = bool(obl[o])
        if x < 0.17:      # owned move
            if rng.random() < 0.5: climb(o, span([rng.randrange(1, 1 << n)]))
            else:
                u = rng.randrange(1, 1 << n); D = frozenset(v for v in C if not dot(v, u))
                if D != C: setch(o, D)
        elif x < 0.37:    # intake (descend to the source chart first)
            if frozen: continue
            dirty = [p for oo in obl for (p, _) in obl[oo]] + [p for (p, q, _) in pobl]
            srcs = [k for k in pub if k[0] != 'X'] + [k for k in own if k != o]
            s = rng.choice(dirty) if (dirty and rng.random() < 0.6) else rng.choice(srcs); Cs = ch(s)
            if not C <= Cs: setch(o, frozenset(C & Cs))
            add(o, rng.choice(scal), s)
        elif x < 0.50:    # deposit into a public (frozen until cleaned)
            if not own[o][1]: continue
            p = rng.choice(nonX)
            if pfro.get(p, 0): continue
            climb(o, ch(p)); lam = rng.choice(scal); add(p, lam, o); obl[o].append((p, lam))
        elif x < 0.60:    # output into X_t
            if not own[o][1]: continue
            t = rng.randrange(T); climb(o, ch(('X', t))); add(('X', t), rng.choice(scal), o)
        elif x < 0.70:    # clean
            if not obl[o]: continue
            k = rng.randrange(len(obl[o])); p, lam = obl[o][k]
            if pfro.get(p, 0): continue
            climb(o, ch(p)); add(p, -lam, o); obl[o].pop(k)
        elif x < 0.80:    # public ascent
            p = rng.choice(nonX + [('X', t) for t in range(T)]); D = join(ch(p), span([rng.randrange(1, 1 << n)]))
            if ycap(p, D): setch(p, D)
        elif x < 0.86:    # X reads a public (public hot delivery when dirty)
            t = rng.randrange(T); q = rng.choice(nonX); D = join(ch(q), ch(('X', t)))
            if ycap(q, D):
                if D != ch(q): setch(q, D)
                add(('X', t), rng.choice(scal), q)
        elif x < 0.92:    # public -> public relay (source frozen)
            p, q = rng.sample(nonX, 2)
            if pfro.get(p, 0): continue
            D = join(ch(q), ch(p))
            if not ycap(q, D): continue
            if D != ch(q): setch(q, D)
            lam = rng.choice(scal); add(p, lam, q); pobl.append((p, q, lam)); pfro[q] = pfro.get(q, 0) + 1
        elif x < 0.96:    # undo a relay
            if not pobl: continue
            k = rng.randrange(len(pobl)); p, q, lam = pobl[k]
            if pfro.get(p, 0): continue
            add(p, -lam, q); pobl.pop(k); pfro[q] -= 1
        else:             # clear
            if not obl[o]: ops.append(('CLEAR', o)); del own[o]; del obl[o]
    # finish
    guard = 0
    while pobl and guard < 1000:
        guard += 1
        for k, (p, q, lam) in enumerate(pobl):
            if not pfro.get(p, 0):
                add(p, -lam, q); pobl.pop(k); pfro[q] -= 1; break
    for o in list(own):
        for (p, lam) in obl[o]:
            climb(o, ch(p)); add(p, -lam, o)
        ops.append(('CLEAR', o))
    return ops, init

def routing_mass(r, P, F):
    """one row per epoch content c_g with its total forwarded weight Wt_g = sum_d T[d,g] w_d (needs acyclic)"""
    EP = r['EP']; order = topo(EP)
    Wt = {j: dict(EP[j]['w']) for j in range(len(EP))}
    for j in reversed(order):
        for i2, mu in EP[j]['N'].items(): addv(F, Wt[i2], mu, Wt[j])
    m = 0
    for j, ep in enumerate(EP):
        D = [t for t, v in Wt[j].items() if v != 0]; S = [s for s, v in ep['c'].items() if v != 0]
        if D and S: m += pairing_rank(P, D, S)
    return m

if __name__ == '__main__':
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1; N = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    rng = random.Random(seed)
    cases = [(3, [1, 2, 4, 7]), (4, [1, 2, 7, 11, 13]), (4, [1, 2, 4, 8, 7, 11, 13, 14])]
    agg = dict(runs=0, badrun=0, unpinned=0, cyclic=0, fails=0, hot=0, xreg_hot=0, cri=0, tight_LS=0, teeth=0, own_gt_R=0, LS_gt_R=0, drops_gt_R=0)
    for i in range(N):
        n, P = cases[i % 3]; F = Fld(2 if i % 2 else 0)
        ops, init = gen(n, P, F, rng)
        r = analyze(ops, init, P, F)
        agg['runs'] += 1
        if r['bad']: agg['badrun'] += 1; print('BAD', i, r['bad'][:3]); continue
        if r['pinned']: agg['unpinned'] += 1; print('UNPINNED', i, r['pinned'][:3]); continue
        c = r['chk']; nf = sum(v for k, v in c.items() if k.endswith('_fail'))
        if c['pot_viol'] and r['acyclic'] is False: print('POT+CYC', i)
        if nf: agg['fails'] += 1; print('FAIL', i, c)
        agg['cri'] += c['pot_viol'] > 0; agg['naive_teeth'] = agg.get('naive_teeth', 0) + (c['naive_gt_seg'] > 0)
        if not r['acyclic']: agg['cyclic'] += 1; print('CYCLIC', i, c); continue
        agg['hot'] += c['hot_intakes'] > 0
        xh = any(r['EP'][i2]['life'] != ep['life'] for ep in r['EP'] for i2 in ep['N'])
        agg['xreg_hot'] += xh
        LS = r['LS']['all'][0]
        if r['own'] > r['R']: agg['own_gt_R'] += 1; print('OWN>R', i)
        if r['drops'] > r['R']: agg['drops_gt_R'] += 1; print('DROPS>R', i)
        if LS > r['drops']: agg['LS_gt_R'] += 1; print('LS>drops', i, LS, r['drops'], r['R'])
        agg['tight_LS'] += (LS == r['R'] and LS > 0)
        rm = routing_mass(r, P, F)
        if xh and rm > r['R']: agg['teeth'] += 1
    print('seed', seed, agg)
