#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""sl_lib.py (copy of our CALLEROUT sl_check.py library part, used by cap_check.py) [C exact mod p]: on a real exact caller (default: the #7113 caller in data/) compute, for every
native call k and each role block (A, B), the END-REFERRED sign-factor perturbation E_k = S (s(J_k) - I) S^-1 at q0 (S = suffix,
s(X) = X(q0) X(-q0)^-1), with random stage scalars D.  Report: rank E_k, pair invariant t_k = (tr s(J_k) - n)/4, whether the row and
column spaces of E_k are supported inside the mask Z_k = {roles whose target contains D_k} (the Support Law SL), rank K = rho of the
whole block, and for every pair of calls the cross Gram rank rank(Y_k^T X_m) = rank(E_k E_m) vs |Z_k cap Z_m| (Theorem 1').
Replay semantics copied from MONOCALLER/check.py (own re-implementation)."""
import json, random, sys
P = 2147483629
IM = next(pow(g, (P - 1) // 4, P) for g in range(2, 99) if pow(g, (P - 1) // 2, P) == P - 1); HALF = (P + 1) // 2
from fractions import Fraction as Q
fm = lambda x: (lambda f: f.numerator % P * pow(f.denominator, P - 2, P) % P)(Q(x))
def ident(n): return [[int(i == j) for j in range(n)] for i in range(n)]
def matmul(A, B):
    n = len(A); m = len(B[0]); Bt = list(zip(*B))
    return [[sum(a * b for a, b in zip(A[i], Bt[j])) % P for j in range(m)] for i in range(n)]
def inv(A):
    n = len(A); M = [r[:] + [int(i == j) for j in range(n)] for i, r in enumerate(A)]
    for c in range(n):
        p = next(i for i in range(c, n) if M[i][c]); M[c], M[p] = M[p], M[c]
        iv = pow(M[c][c], P - 2, P); M[c] = [v * iv % P for v in M[c]]
        for i in range(n):
            if i != c and M[i][c]:
                f = M[i][c]; M[i] = [(a - f * b) % P for a, b in zip(M[i], M[c])]
    return [r[n:] for r in M]
def rank(A):
    A = [r[:] for r in A]; rk = 0
    if not A: return 0
    for c in range(len(A[0])):
        p = next((i for i in range(rk, len(A)) if A[i][c]), None)
        if p is None: continue
        A[rk], A[p] = A[p], A[rk]; iv = pow(A[rk][c], P - 2, P); A[rk] = [v * iv % P for v in A[rk]]
        for i in range(len(A)):
            if i != rk and A[i][c]:
                f = A[i][c]; A[i] = [(a - f * b) % P for a, b in zip(A[i], A[rk])]
        rk += 1
    return rk
def basis(A):
    A=[r[:] for r in A if any(r)];out=[];
    if not A:return out
    rk=0
    for c in range(len(A[0])):
        p=next((i for i in range(rk,len(A)) if A[i][c]),None)
        if p is None:continue
        A[rk],A[p]=A[p],A[rk];iv=pow(A[rk][c],P-2,P);A[rk]=[v*iv%P for v in A[rk]]
        for i in range(len(A)):
            if i!=rk and A[i][c]:
                f=A[i][c];A[i]=[(a-f*b)%P for a,b in zip(A[i],A[rk])]
        rk+=1
    return A[:rk]
def host_rows(R, src, dst, al, be, qv, d):
    qi = pow(qv, P - 2, P); tt = al * be % P
    ns = [(x + al * qv % P * y) % P * d % P for x, y in zip(R[src], R[dst])]
    nd = [(be * qi % P * x + (1 + tt) * y) % P * d % P for x, y in zip(R[src], R[dst])]
    R[src], R[dst] = ns, nd
def apply_native(R, C, e, qv, Dv, part):
    """apply the A part (part='A') or B part (part='B') of J event e to row matrix R."""
    d = Dv[e[1]]; qi = pow(qv, P - 2, P)
    if part == 'A':
        form = C['types']['A']['form']
        if form == 'two-chain-HOST2':
            src, dst, x2, y2 = e[2]; a2 = fm(C['types']['A'].get('alpha2', '-1'))
            R[dst] = [(a + qi * b) % P for a, b in zip(R[dst], R[src])]
            R[x2] = [(a + a2 * qv % P * b) % P for a, b in zip(R[x2], R[y2])]
            for r in (src, dst, x2, y2): R[r] = [a * d % P for a in R[r]]
        else:
            src, dst, al, be = e[2]; host_rows(R, src, dst, fm(al), fm(be), qv, d)
    else:
        src, dst, al, be = e[3]; host_rows(R, src, dst, fm(al), fm(be), qv, d)
def apply_op(R, e, qv, Dv):
    op = e[1]
    if op == 'ADD': R[e[2]] = [(a + fm(e[4]) * b) % P for a, b in zip(R[e[2]], R[e[3]])]
    elif op == 'SCALE': c = fm(e[3]); R[e[2]] = [a * c % P for a in R[e[2]]]
    elif op == 'SWAP': R[e[2]], R[e[3]] = R[e[3]], R[e[2]]
    elif op == 'QUERY': c = pow(qv, e[4] % 4, P); R[e[2]] = [(a + c * b) % P for a, b in zip(R[e[2]], R[e[3]])]
    elif op == 'LAMBDA':
        s = e[3]; c = ((1 + s * IM) * HALF + (1 - s * IM) * HALF * qv * qv) % P; R[e[2]] = [a * c % P for a in R[e[2]]]
    elif op in ('IDLE_ONE', 'IDLE_ODD'):
        c = 1 if op == 'IDLE_ONE' else pow(qv, e[4] % 4, P)
        for s in e[3]: c = c * Dv[s] % P
        R[e[2]] = [a * c % P for a in R[e[2]]]
    else: raise SystemExit(op)
def analyse(C, q0, seed=7, label=''):
    n = C['roles']; rnd = random.Random(seed); Dv = {s: rnd.randrange(2, P) for s in range(1, 18)}
    R = ident(n); snaps = {}
    for e in C['events']:
        if e[0] == 'J':
            apply_native(R, C, e, q0, Dv, 'A'); apply_native(R, C, e, q0, Dv, 'B'); snaps[e[1]] = (e, [r[:] for r in R])
        else: apply_op(R, e, q0, Dv)
    F = R
    out = {}
    for part in ('A', 'B'):
        T = C['types'][part]; off = T['offset']; m = len(T['diagonal']); blk = range(off, off + m)
        masks = {k: {off + i for i, dg in enumerate(T['diagonal']) if dg[1 + k]} for k in range(1, 18)}
        Fi = inv(F); Es = {}; info = {}
        for k, (e, Rk) in snaps.items():
            # local sign factor of this part: J(q0) J(-q0)^-1 on the identity frame
            Jp = ident(n); apply_native(Jp, C, e, q0, Dv, part)
            Jm = ident(n); apply_native(Jm, C, e, (P - q0) % P, Dv, part)
            s = matmul(Jp, inv(Jm))
            # row-op convention: new R = J R, J acts on the left; suffix S with F = S Rk  => S = F Rk^-1
            S = matmul(F, inv(Rk)); E = [[(s[i][j] - (i == j)) % P for j in range(n)] for i in range(n)]
            Ee = matmul(matmul(S, E), inv(S))
            tr = sum(s[i][i] for i in range(n)) % P; t = (tr - n) * pow(4, P - 2, P) % P
            rows_sup = {i for i in range(n) if any(Ee[i])}; cols_sup = {j for j in range(n) if any(Ee[i][j] for i in range(n))}
            Es[k] = (basis([list(c) for c in zip(*Ee)]), basis(Ee))   # (x basis = column space, y basis = row space)
            tf = {fm(x): x for x in ('-1', '0', '-1/2', '-2', '1/2', '-1/4')}.get(t, str(t))
            info[k] = dict(rank=rank(Ee), t=tf, x_in_mask=rows_sup <= masks[k], y_in_mask=cols_sup <= masks[k], mask=len(masks[k]),
                           x_sup=len(rows_sup), y_sup=len(cols_sup))
        # whole-block K rank via product of all end-referred sign factors = s(F) restricted
        pairs = []
        for k in Es:
            for mm in Es:
                if k < mm:
                    gram = lambda Y, X: [[sum(a * b for a, b in zip(y, x)) % P for x in X] for y in Y]
                    r = rank(gram(Es[k][1], Es[mm][0])); r2 = rank(gram(Es[mm][1], Es[k][0]))
                    pairs.append((k, mm, r, r2, len(masks[k] & masks[mm])))
        out[part] = (info, pairs)
        bad_sl = [k for k, v in info.items() if not (v['x_in_mask'] and v['y_in_mask'])]
        ts = sorted({v['t'] for v in info.values()}); rks = sorted({v['rank'] for v in info.values()})
        nont = [k for k, v in info.items() if v['t'] != '-1']
        viol = [(a, b, r, r2, z) for (a, b, r, r2, z) in pairs if a in nont and b in nont and (r < 2 or r2 < 2 or z < 2)]
        sh = [z for (a, b, r, r2, z) in pairs]
        mincr = min(min(r, r2) for (a, b, r, r2, z) in pairs if a in nont and b in nont) if len(nont) > 1 else None
        print('%s q0=%s part %s: SL violations %s | call ranks %s | t values %s | calls with t!=-1: %d | min cross rank among them %s | '
              'Thm1\' violations %d | shared-mask roles over all pairs min %d max %d | rank(E_k E_m) <= shared always: %s'
              % (label, 'i' if q0 == IM else q0, part, bad_sl, rks, ts, len(nont), mincr, len(viol), min(sh), max(sh),
                 all(min(r, r2) <= z for (a, b, r, r2, z) in pairs)), flush=True)
    return out
if __name__ == '__main__':
    import gzip
    from pathlib import Path
    path = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent / 'data' / 'caller-7113.json.gz')
    with (gzip.open(path, 'rt') if path.endswith('.gz') else open(path)) as fh:
        C = json.load(fh)
    for q0 in (1, IM): analyse(C, q0, label=path.split('/')[-1])
