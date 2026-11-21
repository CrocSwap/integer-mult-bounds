#!/usr/bin/env python3
"""REVERSE ctl.py (own code): (a) teeth control: allow ADD d+=s when chart(s) <= chart(d) (cross-chart read) -> expect violations;
(b) exact replays: per-port witness and a relay free-carry gadget (FC s3 shape) on {1,2,7}, n=3: bound must equal R=|Q|=3."""
import random, tensor as T
from tensor import *
def ctl(seed):
    rng = random.Random(seed); viol = 0; runs = 0
    for it in range(1500):
        n = 3; odd = [v for v in range(1, 8) if dot(v, v)]; Q = rng.sample(odd, 3); k = 3; L = subspaces(n); V = frozenset(range(8))
        perp = lambda q: frozenset(v for v in range(8) if not dot(v, q))
        ch = {}; val = {}; pub = {}
        for p in range(k):
            ch['X%d'%p] = span([Q[p]]); val['X%d'%p] = 1<<p; pub['X%d'%p] = V
            ch['Y%d'%p] = frozenset([0]); val['Y%d'%p] = 1<<(k+p); pub['Y%d'%p] = perp(Q[p])
        d = 2*k; S0 = [g for r in ch for g in tens(ch[r], val[r], d)]; Sg = list(S0); dS = rank(Sg); R = 0; pc = 0
        for t in range(60):
            regs = list(ch)
            if rng.random() < 0.5:
                pairs = [(a,b) for a in regs for b in regs if a!=b and ch[b] <= ch[a]]
                if not pairs: continue
                a,b = rng.choice(pairs); nv = val[a]^val[b]
                if any(nv>>p&1 and Q[p] not in ch[a] for p in range(k)): continue
                val[a] = nv; inc = 0
            else:
                ps = [r for r in regs if ch[r] != pub[r]]
                if not ps: continue
                r = rng.choice(ps); ups = [D for D in L if ch[r] < D <= pub[r] and dimS(D) == dimS(ch[r])+1]
                D = rng.choice(ups); inc = 1; pc += 1; ch[r] = D
            Sg += [g for r in ch for g in tens(ch[r], val[r], d)]; dn = rank(Sg)
            if dn - dS > inc: viol += 1
            dS = dn
        runs += 1
    print('CONTROL cross-chart ADD: runs', runs, 'increment violations', viol)
def replay(n, Q, prog, rel=()):
    k = len(Q); V = frozenset(range(1<<n)); perp = lambda q: frozenset(v for v in range(1<<n) if not dot(v, q))
    ch = {}; val = {}; pub = {}
    for p in range(k):
        ch['X%d'%p] = span([Q[p]]); val['X%d'%p] = 1<<p; pub['X%d'%p] = V
        ch['Y%d'%p] = frozenset([0]); val['Y%d'%p] = 1<<(k+p); pub['Y%d'%p] = perp(Q[p])
    for j,(S,F) in enumerate(rel): ch['Z%d'%j] = S; val['Z%d'%j] = 1<<(2*k+j); pub['Z%d'%j] = F
    d = 2*k+len(rel); S0 = [g for r in ch for g in tens(ch[r], val[r], d)]; R = 0; pc = 0
    for op in prog:
        if op[0] == 'add':
            a,b = op[1],op[2]; assert ch[a] == ch[b]; val[a] ^= val[b]
        elif op[0] == 'init': ch[op[1]] = op[2]; val[op[1]] = 0
        else:
            r, D = op[1], op[2]; assert ch[r] <= D or D <= ch[r]
            if r in pub: assert ch[r] <= D; pc += dimS(D)-dimS(ch[r])
            else: R += max(0, dimS(D)-dimS(ch[r]))
            ch[r] = D
        for r in ch:
            for p in range(k): assert not (val[r]>>p&1) or Q[p] in ch[r], ('support', op)
    for r in pub:
        tgt = {'X': lambda p: (1<<p)|(1<<(k+p)), 'Y': lambda p: 1<<(k+p), 'Z': lambda p: 1<<(2*k+p)}[r[0]](int(r[1:]))
        assert ch[r] == pub[r] and val[r] == tgt, ('final', r)
    T_ = [g for r in pub for g in tens(ch[r], val[r], d)]
    return R, rank(S0+T_) - rank(S0) - pc
if __name__ == '__main__':
    ctl(7)
    n, Q = 3, [1, 2, 7]; V = frozenset(range(8)); perp = lambda q: frozenset(v for v in range(8) if not dot(v, q))
    W = []
    for p, q in enumerate(Q):
        W += [('mv','Y%d'%p,perp(q)),('init','O%d'%p,perp(q)),('add','O%d'%p,'Y%d'%p),('mv','O%d'%p,V),('mv','X%d'%p,V),('add','X%d'%p,'O%d'%p)]
    print('witness {1,2,7}: (R, bound) =', replay(n, Q, W))
    # rendezvous gadget (FC s3 shape), Q={1,2,4}: Y_r (port r, q=2) carries y_c (port c, q=1) cold {0} -> hot <1>;
    # O carries cold y_r up (climb 1); O' born AT the hot chart <1> takes y_c and delivers it into X_c and cleans Y_r.
    Q = [1, 2, 4]; c, r = 0, 1; H = span([1])
    G = [('init','O1',frozenset([0])), ('add','O1','Y1'), ('add','Y1','Y0'), ('mv','Y1',H), ('mv','O1',H),
         ('init','O2',H), ('add','O2','Y1'), ('add','O2','O1'), ('add','Y1','O2'), ('add','X0','O2'),
         ('mv','Y1',perp(2)), ('mv','X0',V), ('mv','Y0',perp(1))]
    for p in (1, 2):
        q = Q[p]; G += [('mv','Y%d'%p,perp(q)),('init','P%d'%p,perp(q)),('add','P%d'%p,'Y%d'%p),('mv','P%d'%p,V),('mv','X%d'%p,V),('add','X%d'%p,'P%d'%p)]
    print('rendezvous gadget {1,2,4}: (R, bound) =', replay(3, Q, G))
