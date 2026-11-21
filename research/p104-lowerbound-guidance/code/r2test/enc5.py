"""R2TEST enc.py: exact SAT encoding of bounded pinned GF(2) runs (eng.py model).
One op per step: ADD(d,e) | MOVE(r) (public: ascend, free; owned: nested, ascent paid) | INIT(r) (owned: content 0, any chart).
build(n,P,target,R,L,nh,no,...) -> (nvars, clauses, decode-info)"""
import sys, itertools, subprocess, os
dot = lambda a, b: bin(a & b).count('1') & 1

def build(n, P, target, R, L, nh, no, readX=True, normal=True, por=True):
    T = len(P); V = list(range(1, 1 << n))
    regs = [('X', t) for t in range(T)] + [('Y', t) for t in range(T)] + [('H', j) for j in range(nh)] + [('O', k) for k in range(no)]
    N = len(regs); ri = {r: i for i, r in enumerate(regs)}
    syms = [('x', t) for t in range(T)] + [('y', t) for t in range(T)] + [('h', j) for j in range(nh)]
    S = len(syms)
    nv = [0]; cl = []
    def new(): nv[0] += 1; return nv[0]
    def C(*lits): cl.append(list(lits))
    c = [[[new() for _ in range(S)] for _ in range(N)] for _ in range(L + 1)]
    m = [[{v: new() for v in V} for _ in range(N)] for _ in range(L + 1)]
    owned = [ri[('O', k)] for k in range(no)]
    for r, (kind, i) in enumerate(regs):
        for s, (sk, j) in enumerate(syms):
            want = (kind == 'X' and sk == 'x' and j == i) or (kind == 'Y' and sk == 'y' and j == i) or (kind == 'H' and sk == 'h' and j == i)
            C(c[0][r][s] if want else -c[0][r][s])
        for v in V:
            C(m[0][r][v] if (kind == 'X' and v == P[i]) else -m[0][r][v])
    for t in range(L + 1):
        for r, (kind, i) in enumerate(regs):
            for v, w in itertools.combinations(V, 2):
                C(-m[t][r][v], -m[t][r][w], m[t][r][v ^ w])
            for v in V:
                if kind == 'Y' and dot(v, P[i]): C(-m[t][r][v])
            if kind == 'X': C(m[t][r][P[i]])
    # unary dims for owned (exact): u[t][r][k] <-> dim >= k+1 , k=0..n-1 ; thresholds count>= 1,2,4,8
    thr = [1 << k if k else 1 for k in range(n)]; thr = [1, 2, 4, 8][:n]
    u = {}
    W = max(thr)
    for t in range(L + 1):
        for r in owned:
            prev = None
            for i, v in enumerate(V):
                x = m[t][r][v]; cur = [new() for _ in range(W)]
                for j in range(W):
                    # cur[j] <-> prev[j] or (x and prev[j-1])  (prev[-1]=True)
                    pj = prev[j] if prev else None
                    pm = (prev[j - 1] if prev else None) if j > 0 else 'T'
                    # terms: A = pj ; B = x & pm
                    # cur -> A or B ; A -> cur ; B -> cur
                    if pj is not None: C(cur[j], -pj)
                    if pm == 'T': C(cur[j], -x)
                    elif pm is not None: C(cur[j], -x, -pm)
                    # cur -> A or (x and pm)
                    if pm == 'T':
                        C(-cur[j], *( [pj] if pj is not None else [] ), x)
                    elif pm is None:
                        C(-cur[j], *( [pj] if pj is not None else [] ))
                    else:
                        C(-cur[j], *( [pj] if pj is not None else [] ), x)
                        C(-cur[j], *( [pj] if pj is not None else [] ), pm)
                prev = cur
            u[(t, r)] = [prev[th - 1] for th in thr]
    # step variables (all created first)
    add = {}; mv = {}; ini = {}; asc = {}; zs = []
    noop = [new() for _ in range(L)]
    for t in range(L):
        for d in range(N):
            for e in range(N):
                if d == e: continue
                if not readX and regs[e][0] == 'X': continue
                add[(t, d, e)] = new()
        for r in owned: mv[(t, r)] = new()
        for r in owned: ini[(t, r)] = new()
    used = [[new() for _ in range(N)] for _ in range(L + 1)]
    for r in range(N): C(-used[0][r])
    def opsof(t): return [noop[t]] + [v for (tt, d, e), v in add.items() if tt == t] + [mv[(t, r)] for r in owned] + [ini[(t, r)] for r in owned]
    for t in range(L):
        ops = opsof(t)
        for a_, b_ in itertools.combinations(ops, 2): C(-a_, -b_)
        C(*ops)
        if t + 1 < L: C(-noop[t], noop[t + 1])
        for (tt, d, e), a_ in list(add.items()):
            if tt != t: continue
            if e in owned:
                for v in V: C(-a_, -m[t][d][v], m[t][e][v])
            else:
                for v in V: C(-a_, -m[t][d][v], m[t + 1][e][v])
        if normal:
            for r in range(N):
                acts = ([mv[(t, r)], ini[(t, r)]] if r in owned else [])
                acts += [add[(t, r, e)] for e in range(N) if (t, r, e) in add] + [add[(t, d, r)] for d in range(N) if (t, d, r) in add]
                for a_ in acts: C(-a_, used[t + 1][r])
                C(-used[t + 1][r], used[t][r], *acts)
                C(-used[t][r], used[t + 1][r])
                if (t, r) in ini: C(-ini[(t, r)], -used[t][r])
            for grp in (owned, [ri[('H', j)] for j in range(nh)]):
                for a_, b_ in zip(grp, grp[1:]): C(-used[t + 1][b_], used[t + 1][a_])
            for (tt, d, e), a_ in list(add.items()):
                if tt == t: C(-a_, *c[t][e])
            if t + 1 < L:
                for (tt, d, e), a_ in list(add.items()):
                    if tt == t and (t + 1, d, e) in add: C(-a_, -add[(t + 1, d, e)])
            if t + 1 < L and por:
                keys = [(d, e) for (tt, d, e) in add if tt == t]
                for (d1, e1) in keys:
                    for (d2, e2) in keys:
                        if (d2, e2) < (d1, e1) and len({d1, e1, d2, e2}) == 4:
                            C(-add[(t, d1, e1)], -add[(t + 1, d2, e2)])
            for r in owned:      # a write into an owned register must be read later
                later = [add[(t2, d, r)] for t2 in range(t + 1, L) for d in range(N) if (t2, d, r) in add]
                for e in range(N):
                    if (t, r, e) in add: C(-add[(t, r, e)], *later)
        # contents
        for r in range(N):
            for s in range(S):
                terms = []
                for e in range(N):
                    if (t, r, e) in add:
                        tv = new(); a_ = add[(t, r, e)]
                        C(-tv, a_); C(-tv, c[t][e][s]); C(tv, -a_, -c[t][e][s]); terms.append(tv)
                av = new()
                for tv in terms: C(av, -tv)
                C(-av, *terms)
                c0, c1 = c[t][r][s], c[t + 1][r][s]
                if r in owned:
                    ir = ini[(t, r)]
                    C(-ir, -c1)
                    C(ir, -c0, -av, -c1); C(ir, -c0, av, c1); C(ir, c0, -av, c1); C(ir, c0, av, -c1)
                else:
                    C(-c0, -av, -c1); C(-c0, av, c1); C(c0, -av, c1); C(c0, av, -c1)
        for r in range(N):
            if r not in owned:
                srcs = [add[(t, d, r)] for d in range(N) if (t, d, r) in add]
                for v in V:
                    C(-m[t][r][v], m[t + 1][r][v])                # publics only ascend
                    C(m[t][r][v], -m[t + 1][r][v], *srcs)          # lift only when read this step
                continue
            mvr = mv[(t, r)]; ir = ini[(t, r)]
            hold = [mvr, ir]
            for v in V:
                C(*hold, -m[t][r][v], m[t + 1][r][v]); C(*hold, m[t][r][v], -m[t + 1][r][v])
            if normal:
                dv = []
                for v in V:
                    x = new(); dv.append(x)
                    C(-x, m[t][r][v], m[t + 1][r][v]); C(-x, -m[t][r][v], -m[t + 1][r][v])
                    C(x, -m[t][r][v], m[t + 1][r][v]); C(x, m[t][r][v], -m[t + 1][r][v])
                C(-mvr, *dv)
            a_ = new(); asc[(t, r)] = a_
            for v in V:
                C(-mvr, -a_, -m[t][r][v], m[t + 1][r][v])
                C(-mvr, a_, -m[t + 1][r][v], m[t][r][v])
            for k in range(n):
                z = new(); zs.append(z)
                C(-mvr, -a_, -u[(t + 1, r)][k], u[(t, r)][k], z)
            if normal:
                srcnext = [add[(t + 1, d, r)] for d in range(N) if (t + 1, d, r) in add] if t + 1 < L else []
                dstnext = [add[(t + 1, r, e)] for e in range(N) if (t + 1, r, e) in add] if t + 1 < L else []
                C(-mvr, -a_, *srcnext)
                C(-mvr, a_, *dstnext, (mv[(t + 1, r)] if t + 1 < L else -mvr))
    # atmost R of zs (sequential counter)
    K = R
    if K == 0:
        for z in zs: C(-z)
    else:
        prev = None
        for i, z in enumerate(zs):
            cur = [new() for _ in range(K)]
            for j in range(K):
                pj = prev[j] if prev else None
                pm = (prev[j - 1] if prev else None) if j > 0 else 'T'
                if pj is not None: C(-pj, cur[j])
                if pm == 'T': C(-z, cur[j])
                elif pm is not None: C(-z, -pm, cur[j])
            # overflow
            if prev:
                C(-z, -prev[K - 1])
            prev = cur
    # final conditions
    odd = {(t, s) for t in range(T) for s in range(T) if dot(P[t], P[s])}
    for r, (kind, i) in enumerate(regs):
        for s, (sk, j) in enumerate(syms):
            if kind == 'H': want = (sk == 'h' and j == i)
            elif kind == 'Y': want = (sk == 'y' and j == i)
            elif kind == 'X':
                if sk == 'x': want = (j == i)
                elif sk == 'h': want = False
                else:
                    if (i, j) in odd: want = ((i, j) in target)
                    else: want = None
            else: want = None
            if want is True: C(c[L][r][s])
            elif want is False: C(-c[L][r][s])
    info = dict(regs=regs, syms=syms, c=c, m=m, add=add, mv=mv, ini=ini, L=L, V=V, n=n)
    return nv[0], cl, info

def write(path, nv, cl):
    with open(path, 'w') as f:
        f.write(f'p cnf {nv} {len(cl)}\n')
        for x in cl: f.write(' '.join(map(str, x)) + ' 0\n')

def solve(path, timeout=1200):
    p = subprocess.run(['kissat', '-q', '--time=%d' % timeout, path], capture_output=True, text=True)
    out = p.stdout; model = set()
    st = 'UNKNOWN'
    for line in out.splitlines():
        if line.startswith('s SATISFIABLE'): st = 'SAT'
        elif line.startswith('s UNSATISFIABLE'): st = 'UNSAT'
        elif line.startswith('v'):
            for x in line.split()[1:]:
                x = int(x)
                if x > 0: model.add(x)
    return st, model

def decode(info, model, P):
    regs = info['regs']; L = info['L']; V = info['V']; n = info['n']
    ops = []
    def chart(t, r):
        return frozenset([0] + [v for v in V if info['m'][t][r][v] in model])
    for t in range(L):
        for (tt, d, e), a in info['add'].items():
            if tt == t and a in model:
                if regs[e][0] != 'O' and chart(t + 1, e) != chart(t, e): ops.append(('MOVE', regs[e], chart(t + 1, e)))
                ops.append(('ADD', regs[d], 1, regs[e]))
        for (tt, r), a in info['mv'].items():
            if tt == t and a in model: ops.append(('MOVE', regs[r], chart(t + 1, r)))
        for (tt, r), a in info['ini'].items():
            if tt == t and a in model: ops.append(('CLEARINIT', regs[r], chart(t + 1, r)))
    return ops

def replay(n, P, nh, no, ops):
    from eng import Run, Field
    F = Field(2); T = len(P)
    meta = dict(nh=nh, Xch=None, Ych=None, Hch=None)
    R = Run(n, P, F, nh=nh)
    for k in range(no): R.INIT(('O', k), frozenset([0]))
    for op in ops:
        if op[0] == 'ADD': R.ADD(op[1], op[2], op[3])
        elif op[0] == 'MOVE': R.MOVE(op[1], op[2])
        else: R.CLEAR(op[1]); R.INIT(op[1], op[2])
    for k in range(no): R.CLEAR(('O', k))
    return R

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--R', type=int); ap.add_argument('--L', type=int); ap.add_argument('--nh', type=int); ap.add_argument('--no', type=int)
    ap.add_argument('--case', default='Q5'); ap.add_argument('--raw', action='store_true'); ap.add_argument('--nopor', action='store_true'); ap.add_argument('--cells', default=None); ap.add_argument('--noreadX', action='store_true'); ap.add_argument('--timeout', type=int, default=1200)
    a = ap.parse_args()
    if a.case == 'Q5':
        n = 4; P = [1, 2, 7, 11, 13]
        target = {(0, 2), (0, 3), (2, 0), (2, 1), (2, 2), (3, 0), (3, 1), (3, 3)}
    elif a.case == 'Q3':   # {1,2,7} identity-diagonal receipts: honest R=3 control
        n = 3; P = [1, 2, 7]; target = {(0, 0), (1, 1), (2, 2)}
    if a.cells: target = {tuple(map(int, x.split(','))) for x in a.cells.split(';')}
    nv, cl, info = build(n, P, target, a.R, a.L, a.nh, a.no, readX=not a.noreadX, normal=not a.raw, por=not a.nopor)
    path = f'cnf5_{a.case}{abs(hash(a.cells))%10000 if a.cells else ""}_R{a.R}_L{a.L}_h{a.nh}_o{a.no}.cnf'
    write(path, nv, cl); print('vars', nv, 'clauses', len(cl), flush=True)
    import time; t0 = time.time()
    st, model = solve(path, a.timeout)
    print(st, 'time %.1f' % (time.time() - t0), flush=True)
    if st == 'SAT':
        ops = decode(info, model, P)
        R = replay(n, P, a.nh, a.no, ops)
        T = len(P); odd = {(t, s) for t in range(T) for s in range(T) if dot(P[t], P[s])}
        got = {(t, s) for t in range(T) for s in range(T) if R.reg[('X', t)][1].get(('y', s)) and (t, s) in odd}
        print('replay: bad', R.bad, 'pinned errs', R.pinned(), 'cost', R.cost, 'odd receipts ok', got == target)
        for op in ops: print(op)
