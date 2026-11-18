#!/usr/bin/env python3
"""BANK hub2: generalised #7682 move.  P->Q edges Ein (one, e1, re-destined to hub R), e2: Q->T re-sourced at R.
Q keeps k=|Ein|-1 carriers with new values U (from V_P); Q->R edges carry new values G; R recovers its old needs and
e2's value from (w1, G, V_R); every other receiver recovers its old value with its own local donors.
Screen mod p; build: forms solved mod p, rationally reconstructed, then EXACT terminal check + schedule.
usage: hub2.py WORD CIRCUIT DIR OUTPREFIX [shard nsh]"""
import sys, os, json, time
import numpy as np
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import *
import search2 as S2
import nest
p = S2.p; KAP = float(os.environ.get("BANK_KAPPA", "0.00373"))  # screen scoring only
f = lambda r: r ** (1 - KAP) if r else 0.0
rref, red = S2.rref, S2.red

def vec_mod(v, n):
    a = np.zeros(n, dtype=np.int64)
    for i, c in v.items(): a[i] = fmod(c, p)
    return a

def dimsum(*bases):
    rows = [r for b in bases for r in b]
    return len(rref(rows, NN)[0]) if rows else 0

def solve_mod(y, cols):
    """y = sum c_j cols[j] mod p; returns c (list) or None.  cols: list of vectors."""
    if not cols: return [] if not y.any() else None
    A = np.concatenate([np.array(cols).T % p, (y % p)[:, None]], axis=1); m = len(cols); r = 0; piv = []
    for c in range(m):
        nz = np.flatnonzero(A[r:, c]) if r < A.shape[0] else []
        if not len(nz): continue
        i = r + nz[0]; A[[r, i]] = A[[i, r]]; A[r] = A[r] * pow(int(A[r, c]), -1, p) % p
        col = A[:, c].copy(); col[r] = 0; nzr = np.flatnonzero(col)
        A[nzr] = (A[nzr] - np.outer(col[nzr], A[r])) % p
        piv.append(c); r += 1
    if A[r:, -1].any(): return None
    out = [0] * m
    for i, c in enumerate(piv): out[c] = int(A[i, -1])
    return out

def ratrec(a):
    """rational reconstruction mod p (half-gcd style); None if fails."""
    a %= p
    if a == 0: return Q(0)
    r0, r1, s0, s1 = p, a, 0, 1
    B = int((p // 2) ** 0.5)
    while r1 > B:
        q = r0 // r1; r0, r1 = r1, r0 - q * r1; s0, s1 = s1, s0 - q * s1
    if s1 == 0 or abs(s1) > B: return None
    return Q(r1, s1)

class Ctx:
    def __init__(s, net, dim):
        s.net, s.dim = net, dim; s.n = len(net.init); global NN; NN = s.n
        s.order = schedule(net); s.V = values(net, p, s.order)
        s.toks = defaultdict(list); s.tv = {}
        for r in range(s.n):
            e = np.zeros(s.n, dtype=np.int64); e[r] = 1; s.toks[net.init[r]].append(~r); s.tv[~r] = e
        for k, (a, b) in net.moves.items(): s.toks[b].append(k); s.tv[k] = s.V[k]
        s.nodes_at = defaultdict(list)
        for k in net.forms: s.nodes_at[net.chart_of_node(k)].append(k)
        s.ins = defaultdict(list); s.outs = defaultdict(list)
        for k, (a, b) in net.moves.items(): s.ins[b].append(k); s.outs[a].append(k)
        kids = defaultdict(list)
        for k, row in net.forms.items():
            for d in row:
                if d >= 0: kids[d].append(k)
        s.desc = {}
        for k in reversed(s.order):
            b = 1 << k if k < net.first else 0
            for m in kids[k]: b |= s.desc[m]
            s.desc[k] = b
    def basis(s, X, ex=0):
        return rref([s.tv[x] for x in s.toks[X] if x < 0 or not (ex >> x) & 1], s.n)

def screen_group(c, Qc, P, out, log, tag):
    net, dim, n = c.net, c.dim, c.n
    Ein = [e for e in c.ins[Qc] if net.moves[e][0] == P]; k = len(Ein) - 1; e1 = Ein[0]
    RQt = [x for x in c.toks[Qc] if x not in set(Ein)]
    pQ, BQ = rref([c.tv[x] for x in RQt], n)
    pP, BP = c.basis(P, c.desc[e1])
    a = abs(dim[Qc] - dim[P])
    # lifts for every need x at Q: residual mod (RQ + V_X) lifted into V_P
    lift = {}
    for x in c.nodes_at[Qc]:
        X = net.moves[x][1] if x < net.first else None
        if X is not None: pX, BX = c.basis(X, c.desc[x]); pb, Bb = rref(list(BQ) + list(BX), n)
        else: pb, Bb = pQ, BQ
        d = red(c.V[x], pb, Bb)
        if not d.any(): lift[x] = None; continue
        Rp = red(BP, pb, Bb); sol = solve_mod(d, list(Rp))
        if sol is None: lift[x] = 'X'; continue
        lift[x] = sum(ci * BP[i] for i, ci in enumerate(sol) if ci) % p
    for e2 in c.outs[Qc]:
        T = net.moves[e2][1]; b = abs(dim[T] - dim[Qc])
        Rs = {net.moves[x][1] for x in c.outs[Qc]} - {P, Qc, T}
        for R_ in Rs:
            a2 = nest.trank(FR, P, R_); b2 = nest.trank(FR, R_, T)
            if a2 is None or b2 is None or a2 == 0 or b2 == 0: continue
            G = f(a) + f(b) - f(a2) - f(b2)
            if G <= 1e-12: continue
            Redges = [x for x in c.outs[Qc] if net.moves[x][1] == R_]
            Lf = [lift[x] for x in c.nodes_at[Qc] if x != e2 and x not in Redges]
            if any(isinstance(l, str) for l in Lf): continue
            pU, BU = rref([l for l in Lf if l is not None], n)
            if len(pU) > k: continue
            # R quotient
            exR = c.desc[e2] | c.desc[e1]
            for x in Redges: exR |= c.desc[x]
            pR, BR = c.basis(R_, exR)
            pRT, BRT = rref(list(BR) + list(c.basis(T, c.desc[e2])[1]), n)
            Sv = [red(c.V[x], pR, BR) for x in Redges] + [red(c.V[e2], pR, BR)]
            pS, BS = rref([v for v in Sv if v.any()], n)
            pA, BA = rref([red(v, pR, BR) for v in list(BQ) + list(BU)], n)
            piS = [red(v, pA, BA) for v in BS]; pPi, BPi = rref([v for v in piS if v.any()], n)
            dS, dpi, m = len(pS), len(pPi), len(Redges)
            if dpi > 1: continue
            if dpi == 1:
                Bq = [red(red(v, pR, BR), pA, BA) for v in BP]
                if solve_mod(BPi[0], Bq) is None: continue
                if dS > m + 1: continue
                if dS == m + 1:
                    # S cap B not inside A
                    Bm = [red(v, pR, BR) for v in BP]
                    ok = False
                    for v in Bm:   # cheap sufficient check on basis of B
                        if red(red(v, pS, BS), pS, BS).any(): continue
                        if red(v, pA, BA).any(): ok = True; break
                    if not ok:
                        # exact: intersection S cap B
                        M = list(BS) + [(-v) % p for v in Bm]
                        ker = kernel(M, len(BS))
                        ok = any(red(sum(kk[i] * BS[i] for i in range(len(BS))) % p, pA, BA).any() for kk in ker)
                    if not ok: continue
            elif dS > m: continue
            h = dict(dir=tag, e1=e1, e2=e2, P=P, Q=Qc, T=T, R=R_, ranks=[a, b, a2, b2], G=G, k=k, m=m, dS=dS, dpi=dpi)
            out.append(h); log.write(json.dumps(h) + '\n'); log.flush()

def kernel(rows, ns):
    """left kernel of matrix with given rows; returns list of coefficient vectors restricted to first ns rows."""
    m = len(rows); A = np.concatenate([np.array(rows) % p, np.eye(m, dtype=np.int64)], axis=1); r = 0; nc = len(rows[0])
    for cidx in range(nc):
        if r == m: break
        nz = np.flatnonzero(A[r:, cidx])
        if not len(nz): continue
        i = r + nz[0]; A[[r, i]] = A[[i, r]]; A[r] = A[r] * pow(int(A[r, cidx]), -1, p) % p
        col = A[:, cidx].copy(); col[r] = 0; nzr = np.flatnonzero(col)
        A[nzr] = (A[nzr] - np.outer(col[nzr], A[r])) % p
        r += 1
    return [A[i, nc:nc + ns] for i in range(r, m)]

if __name__ == '__main__':
    W = load(sys.argv[1]); dim = [len(f_) for f_ in W['frames']]; FR = W['frames']
    net = load_circuit(sys.argv[2]); d = sys.argv[3]
    sh, nsh = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (0, 1)
    c = Ctx(net if d == 'forward' else transpose(net), dim)
    out = []; log = open(sys.argv[4] + '.jsonl', 'a'); t0 = time.time(); gi = 0
    onlyQ = os.environ.get('BANK_Q')
    for Qc in sorted(c.ins):
        if not c.outs[Qc]: continue
        if onlyQ and Qc != int(onlyQ): continue
        for P in sorted({c.net.moves[e][0] for e in c.ins[Qc]}):
            if P == Qc: continue
            gi += 1
            if gi % nsh != sh: continue
            if gi <= int(os.environ.get('BANK_GSTART', '0')): continue
            screen_group(c, Qc, P, out, log, d)
            print('gdone', gi, file=sys.stderr, flush=True)
            if gi % 200 < nsh: print('prog', gi, len(out), round(time.time() - t0), file=sys.stderr, flush=True)
    print(d, 'groups', gi, 'hits', len(out), Counter(tuple(h['ranks']) for h in out).most_common(12))
