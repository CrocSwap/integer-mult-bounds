#!/usr/bin/env python3
"""REVERSE lane (own code). TENSOR POTENTIAL check, GF(2) hosted toy, any run (relays, rendezvous, X deliveries, discards).
S(t) = sum over history of C_r (x) w_r  in F2^n (x) F2^W (cumulative).  Claims checked exactly:
 (1) every ADD / INIT / descent raises dim S by 0, every ascent C->D (any register) by <= dim D - dim C;
 (2) hence R_owned >= dim(S0 + T) - dim S0 - sum_public climbs, T = end configuration (any end state);
 (3) on runs that reach the toy finals this equals rank_F2(Q o M) (= |Q| for M = I).
Random legal runs: n=3,4; ports Q odd; 0-3 relays (random S<=F, start z_j); owned regs; moves biased to rendezvous."""
import random, sys, itertools
dot = lambda a, b: bin(a & b).count('1') & 1
def rank(vs):
    rows = []
    for v in vs:
        for r in rows: v = min(v, v ^ r)
        if v: rows.append(v)
    return len(rows)
def basis(vs):
    rows = []
    for v in vs:
        for r in rows: v = min(v, v ^ r)
        if v: rows.append(v)
    return rows
def span(vs):
    S = {0}
    for v in vs:
        if v not in S: S |= {x ^ v for x in S}
    return frozenset(S)
def subspaces(n):
    seen = {frozenset([0])}; fr = [frozenset([0])]
    while fr:
        nx = []
        for S in fr:
            for v in range(1 << n):
                if v not in S:
                    U = frozenset(S | {x ^ v for x in S})
                    if U not in seen: seen.add(U); nx.append(U)
        fr = nx
    return list(seen)
dimS = lambda S: len(S).bit_length() - 1
def tens(C, w, d):   # generators of C (x) w as bit vectors of length n*d  (index c_bit*d + content_bit)
    out = []
    for c in basis(sorted(C - {0})):
        v = 0
        for i in range(16):
            if c >> i & 1: v ^= w << (i * d)
        out.append(v)
    return out
def run_one(rng, n, Q, nrel, steps):
    k = len(Q); L = subspaces(n); V = frozenset(range(1 << n))
    perp = lambda q: frozenset(v for v in range(1 << n) if not dot(v, q))
    rel = []
    for j in range(nrel):
        while True:
            S, F = rng.choice(L), rng.choice(L)
            if S <= F: break
        rel.append((S, F))
    d = 2 * k + nrel
    ch, val, pub, fin = {}, {}, {}, {}
    for p in range(k):
        ch['X%d' % p] = span([Q[p]]); val['X%d' % p] = 1 << p; pub['X%d' % p] = V
        ch['Y%d' % p] = frozenset([0]); val['Y%d' % p] = 1 << (k + p); pub['Y%d' % p] = perp(Q[p])
    for j, (S, F) in enumerate(rel):
        ch['Z%d' % j] = S; val['Z%d' % j] = 1 << (2 * k + j); pub['Z%d' % j] = F
    S0 = [g for r in ch for g in tens(ch[r], val[r], d)]
    Sg = list(S0); dS = rank(Sg); R = 0; pubclimb = 0; viol = 0
    for r in pub: pass
    nown = rng.randint(1, 3)
    for t in range(steps):
        regs = list(ch); typ = rng.random()
        if typ < 0.4:                                     # ADD at a shared chart
            pairs = [(a, b) for a in regs for b in regs if a != b and ch[a] == ch[b]]
            if not pairs: continue
            a, b = rng.choice(pairs); nv = val[a] ^ val[b]
            # support rule (x_p needs q_p in chart)
            if any(nv >> p & 1 and Q[p] not in ch[a] for p in range(k)): continue
            val[a] = nv; inc = 0
        elif typ < 0.7:                                   # public ascent (one cover, inside its final)
            ps = [r for r in regs if r in pub and ch[r] != pub[r]]
            if not ps: continue
            r = rng.choice(ps); ups = [D for D in L if ch[r] < D <= pub[r] and dimS(D) == dimS(ch[r]) + 1]
            D = rng.choice(ups); inc = dimS(D) - dimS(ch[r]); pubclimb += inc; ch[r] = D
        else:                                             # owned: INIT / move (rendezvous-biased) / discard
            os_ = [r for r in regs if r[0] == 'O']
            if len(os_) < nown and rng.random() < 0.5:
                nm = 'O%d' % t; ch[nm] = rng.choice([ch[x] for x in regs]) if rng.random() < 0.7 else rng.choice(L); val[nm] = 0; inc = 0
            elif os_ and rng.random() < 0.1:
                del ch[os_[0]]; del val[os_[0]]; continue
            elif os_:
                r = rng.choice(os_); D = rng.choice([ch[x] for x in regs if x != r] + L)
                if not (D <= ch[r] or ch[r] <= D): continue
                if any(val[r] >> p & 1 and Q[p] not in D for p in range(k)): continue
                inc = max(0, dimS(D) - dimS(ch[r])); R += inc; ch[r] = D
            else: continue
        Sg += [g for r in ch for g in tens(ch[r], val[r], d)]
        dn = rank(Sg)
        if dn - dS > inc: viol += 1
        dS = dn
    T = [g for r in ch if r in pub for g in tens(ch[r], val[r], d)]
    bound = rank(S0 + T) - rank(S0) - pubclimb
    return R, bound, viol
if __name__ == '__main__':
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
    tot = viol = bad = 0
    for it in range(3000):
        n = rng.choice([3, 3, 4]); odd = [v for v in range(1, 1 << n) if dot(v, v)]
        Q = rng.sample(odd, rng.randint(1, min(4, len(odd))))
        R, b, vi = run_one(rng, n, Q, rng.randint(0, 3), rng.randint(10, 80))
        tot += 1; viol += vi; bad += (R < b)
    print('runs', tot, 'increment violations', viol, 'R < bound violations', bad)
