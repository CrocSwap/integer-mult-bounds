"""UPHASE fuzz.py: random exact runs over Q (no target constraint) testing the proof steps of the future-attribution law:
 (1) identity final-start = sum W f + sum alpha c  (exact);  (2) chart invariants W_P[t]!=0 => q_t in chart(P), alpha_e[t]!=0 => q_t in C_e;
 (3) price lemma: GTD + cold-intake + no-x lifetime => rank_F2 Q[D,S] <= dim B - dim(B cap A) <= cost;
 (4) transposition: adjoint run delivers exactly M^T.
Teeth: T1 hot-intake lifetimes with price > cost must occur; T2 variant with descending publics must break (2)."""
import random, sys
from fattr import *
from adjoint import adjoint

def gen(rng, N, nports, nh, steps, descend=False):
    odd = [v for v in range(1, 1 << N) if bin(v).count('1') % 2]
    P = rng.sample(odd, nports)
    V = frozenset(range(1 << N))
    perpq = lambda q: frozenset(x for x in range(1 << N) if not dot(x, q))
    init = {}
    for t in range(nports):
        init[('X', t)] = (span([P[t]]), {('x', t): Fr(1)})
        init[('Y', t)] = (frozenset([0]), {('y', t): Fr(1)})
    for h in range(nh): init[('H', h)] = (frozenset([0]), {('h', h): Fr(1)})
    ch = {k: f for k, (f, c) in init.items()}
    cap = {k: (perpq(P[k[1]]) if k[0] == 'Y' else V) for k in init}
    prog = []; owned = []; no = 0
    sc = [Fr(1), Fr(-1), Fr(1, 2), Fr(-1, 2), Fr(2), Fr(3, 2)]
    def up(F, top):
        tg = [G for G in set(ch.values()) if F < G and G <= top]
        if tg and rng.random() < 0.6:
            G = min(tg, key=len); return G
        c = [v for v in top if v not in F]
        if not c: return None
        v = rng.choice(c); return frozenset(F | {x ^ v for x in F})
    def down(F):
        B = basis(F)
        if not B: return None
        # random hyperplane of F
        while True:
            fn = rng.randrange(1, 1 << len(B))
            H = frozenset(x for x in F if not bin(sum(1 << i for i, b in enumerate(B) if _coord(x, B, i)) & fn).count('1') % 2)
            return H
    for _ in range(steps):
        r = rng.random()
        if r < 0.12:
            k = rng.choice([k for k in ch if k not in owned] or list(ch))
            if k in owned: continue
            if descend and rng.random() < 0.3 and len(ch[k]) > 1:
                F = down(ch[k])
                if k[0] == 'X' and P[k[1]] not in F: continue
            else:
                F = up(ch[k], cap[k])
            if F is None: continue
            prog.append(('MOVE', k, F)); ch[k] = F
        elif r < 0.17 and len(owned) < 4:
            k = ('O', no); no += 1
            # birth chart: a random chart already in use (rendezvous-biased) or {0}
            F = rng.choice([frozenset([0])] + list(ch.values()))
            prog.append(('INIT', k, F, {}, True)); ch[k] = F; owned.append(k)
        elif r < 0.30 and owned:
            k = rng.choice(owned)
            tg = [G for G in set(ch.values()) if G != ch[k] and (G < ch[k] or ch[k] < G)]
            F = rng.choice(tg) if tg and rng.random() < 0.5 else (up(ch[k], V) if rng.random() < 0.6 else down(ch[k]))
            if F is None or F == ch[k]: continue
            prog.append(('MOVE', k, F)); ch[k] = F
        elif r < 0.34 and owned:
            k = rng.choice(owned); prog.append(('CLEAR', k)); owned.remove(k); del ch[k]
        else:
            ks = list(ch); d = rng.choice(ks)
            same = [s for s in ks if s != d and ch[s] == ch[d]]
            if not same: continue
            s = rng.choice(same)
            prog.append(('ADD', d, rng.choice(sc), s))
    for k in owned: prog.append(('CLEAR', k))
    return prog, init, P

def _coord(x, B, i):
    # coordinate i of x in echelon basis B (B sorted desc by leading bit, reduced greedily)
    c = 0; y = x
    for j, b in enumerate(B):
        if y ^ b < y:
            y ^= b
            if j == i: c = 1
    return c

def main(nruns, seed, descend=False):
    rng = random.Random(seed)
    tot = dict(runs=0, idfail=0, vW=0, va=0, lives=0, inclass=0, price_viol=0, bound_viol=0, hot=0, hot_price_gt_cost=0, adj_mis=0, adj_bad=0)
    for it in range(nruns):
        N = rng.choice([3, 4]); nports = rng.randint(2, 5 if N == 4 else 4)
        prog, init, P = gen(rng, N, nports, rng.randint(1, 3), rng.randint(40, 120), descend)
        out = analyze(prog, init, {}, P)
        tot['runs'] += 1
        if out['bad'] and not descend: tot['adj_bad'] += 1
        tot['idfail'] += out['identity_fail'] > 0
        tot['vW'] += out['viol_W'] > 0; tot['va'] += out['viol_alpha'] > 0
        rows = decoder_rows(out, P)
        for k, lf in enumerate(out['L']):
            tot['lives'] += 1
            w, v = rows[k]
            if not w or not v: continue
            pr = price(set(w), set(v), P)
            if lf['gtd'] and lf['cold'] and lf['nox']:
                tot['inclass'] += 1
                b = chart_bound(lf)
                if pr > b: tot['price_viol'] += 1
                if b > lf['cost']: tot['bound_viol'] += 1
            elif lf['gtd'] and not lf['cold']:
                tot['hot'] += 1
                if pr > lf['cost']: tot['hot_price_gt_cost'] += 1
        if not descend:
            ap, ai = adjoint(prog, init, N)
            o2 = analyze(ap, ai, {}, P, check_identity=False)
            mis = 0
            for t in range(nports):
                for s in range(nports):
                    a = out['fin'][('X', t)].get(('y', s), 0)
                    b = o2['fin'][('X', s)].get(('y', t), 0)
                    if a != b: mis += 1
            tot['adj_mis'] += mis > 0
            tot['adj_bad'] += len(o2['bad']) > 0
    return tot

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    print('MAIN   ', main(n, 1))
    print('T2 (publics may descend; expect chart-invariant violations)', main(n // 4, 2, descend=True))
