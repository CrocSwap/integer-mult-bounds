"""Authors' script (NOT run by verify.sh; needs sympy): finds same-support rational lifts with rank_Q <= rank_F2 on every block for minimisers, and dumps them
to data/lifts_nojoint.json, which verify.sh (group G2.nojoint-lifts) re-checks with exact Fractions.  Method of the card g1/exactlift.py (adapted, same math):
row/column scalings preserve all block ranks, so entries on a spanning forest of supp B are fixed to 1; the remaining variables are searched over small
integers, accepting a point only if the exact block ranks are <= the F2 ranks.  usage: python3 make_lifts.py   (from the package directory)"""
import sys, os, json, itertools
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from kit import *
import sympy as sp

def lift_system(B, R, A, rk):
    v = len(B); E = [(t, s) for t in range(v) for s in range(v) if B[t][s]]
    par = {('r', t): ('r', t) for t in range(v)}; par.update({('c', s): ('c', s) for s in range(v)})
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    W = {}; vs = []
    for (t, s) in E:
        a, b = find(('r', t)), find(('c', s))
        if a != b: par[a] = b; W[(t, s)] = sp.Integer(1)
        else:
            x = sp.Symbol('x%d_%d' % (t, s)); vs.append(x); W[(t, s)] = x
    eqs = []
    for j in range(3):
        rows = [t for t in R[j] if any(B[t][s] for s in A[j])]; cols = [s for s in A[j] if any(B[t][s] for t in R[j])]
        r = rk[j]
        if min(len(rows), len(cols)) <= r: continue
        M = sp.Matrix([[W.get((t, s), 0) for s in cols] for t in rows])
        for rs in itertools.combinations(range(len(rows)), r + 1):
            for cs in itertools.combinations(range(len(cols)), r + 1):
                d = sp.expand(M.extract(list(rs), list(cs)).det(method='berkowitz'))
                if d != 0: eqs.append(d)
    return vs, list(set(eqs)), W

def find_lift(B, R, A, rk, maxvars=12):
    vs, eqs, W = lift_system(B, R, A, rk)
    if len(vs) > maxvars: return None
    f = sp.lambdify(vs, eqs, 'math') if eqs else None
    v = len(B)
    for vals in ((1, -1), (1, -1, 2, -2)):
        for combo in itertools.product(vals, repeat=len(vs)):
            if f is None or all(e == 0 for e in f(*combo)):
                sub = dict(zip(vs, combo))
                M = [[int(W[(t, s)].subs(sub)) if (t, s) in W else 0 for s in range(v)] for t in range(v)]
                if all(M[t][s] != 0 for (t, s) in W) and all(qrank([[M[t][s] for s in A[j]] for t in R[j]]) <= rk[j] for j in range(3)):
                    return M
    return None

if __name__ == '__main__':
    out = []
    def do(name, items):
        P, Q = load_cfg(name); v = len(P); R, A, free = setup(P, Q)
        for g in items:
            B = tomat(g, free, v); rk = blockranks(B, R, A); M = find_lift(B, R, A, rk)
            print(name, bin(g).count('1'), rk, 'lift' if M else 'NONE', flush=True)
            if M: out.append({'config': name, 'g': g, 'lift': M})
    for name in ['cex_joint_v7.json'] + ['nojoint_21_%d.json' % i for i in range(1, 15)]:
        P, Q = load_cfg(name); best, ms, R, A, free = enum(P, Q)
        do(name, [g for _, g in sorted(ms, key=lambda x: (bin(x[1]).count('1'), x[1]))[:12 if 'nojoint' in name else 99]])
    gm = json.load(open('/Users/mason/repo_clones/intmult-work/cards/KPR4-T3/g1/gad.json.mins.json'))
    bad = sorted((e for e in gm if not all(e[2])), key=lambda e: (e[0], e[4]))
    do('gad.json', [e[4] for e in bad[:8]])
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'lifts_nojoint.json'), 'w'))
