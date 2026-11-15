#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Lossless-CLEAR checker, law DUAL (our NETC4 lane; only this checker is shipped, not the NETC compiler).  Stdlib only.
  Live rows always span Q^n (n publics) until a lossy CLEAR.  The relation space
Lam(t) = {lam : sum_r lam_r row_r = 0} over live registers has dim = #live owned.  Ops act on it contragrediently:
  ADD dst += q src  :  lam_src -= q lam_dst          SCALE r *= q : lam_r /= q
  INIT o            :  Lam += e_o                    CLEAR o      : lossless iff some lam has lam_o != 0;
                                                                    then Lam := {lam in Lam : lam_o = 0}
So one forward pass mod p = 2^61-1 finds every lossy CLEAR.  A lossless CLEAR is never missed; a reported loss could,
with negligible probability, be a mod-p false zero of every lam_o, so re-check reported losses exactly (as
tests/test_checkers.py does with a Fraction rank).  dual_scan(W) -> list of (t, o, blame) where blame lists the
ops that wrote coordinate o of some relation (the reads of o by relation-carrying registers)."""
import collections
from fractions import Fraction as Q
P = (1 << 61) - 1
def m(q):
    q = Q(q); return q.numerator % P * pow(q.denominator % P, P - 2, P) % P

def dual_scan(W, track=None, stop_at=None):
    n = W['public']; prog = W['program']
    lam = {}; occ = collections.defaultdict(set); nid = [0]; home = {}
    loss = []; hist = collections.defaultdict(list)
    def setc(i, r, v):
        L = lam[i]
        if v: L[r] = v; occ[r].add(i)
        else: L.pop(r, None); occ[r].discard(i)
    for t, e in enumerate(prog):
        if stop_at is not None and t >= stop_at: break
        op = e[0]
        if op in ('ADD', 'COPY'):
            d, s = e[1], e[2]
            if occ.get(d):
                q = m(e[3])
                for i in list(occ[d]):
                    nv = (lam[i].get(s, 0) - q * lam[i][d]) % P
                    setc(i, s, nv)
                if s >= n: hist[s].append(t)
        elif op == 'SCALE':
            r = e[1]
            if occ.get(r):
                iq = pow(m(e[2]), P - 2, P)
                for i in list(occ[r]): setc(i, r, lam[i][r] * iq % P)
        elif op == 'INIT':
            o = e[1]; i = nid[0]; nid[0] += 1; lam[i] = {}; setc(i, o, 1); home[o] = i; hist[o] = []
        elif op == 'CLEAR':
            o = e[1]; c = list(occ.get(o, ()))
            if not c:
                loss.append((t, o, list(hist[o])))
            else:
                piv = min(c, key=lambda i: len(lam[i])); pv = lam[piv]; ip = pow(pv[o], P - 2, P)
                for i in c:
                    if i == piv: continue
                    f = lam[i][o] * ip % P
                    for r, v in pv.items(): setc(i, r, (lam[i].get(r, 0) - f * v) % P)
                for r in list(pv): occ[r].discard(piv)
                del lam[piv]
    return loss, lam, occ

def prank(vecs, cols):
    """rank mod P of the projections of vecs onto cols."""
    piv = {}; rk = 0
    for v in vecs:
        x = {c: v[c] for c in cols if v.get(c)}
        while x:
            p = min(x)
            if p not in piv: break
            f = x[p]; pv = piv[p]
            for k, y in pv.items():
                nv = (x.get(k, 0) - f * y) % P
                if nv: x[k] = nv
                else: x.pop(k, None)
        if x:
            p = min(x); ip = pow(x[p], P - 2, P); piv[p] = {k: y * ip % P for k, y in x.items()}; rk += 1
    return rk

def culprit_ops(W, tc, C, t_from):
    """re-scan; between t_from and tc report every op after which rank(pi_C(Lam)) changes (C = owned set cleared at tc)."""
    n = W['public']; prog = W['program']
    lam = {}; occ = collections.defaultdict(set); nid = [0]; out = []; last = None
    def setc(i, r, v):
        L = lam[i]
        if v: L[r] = v; occ[r].add(i)
        else: L.pop(r, None); occ[r].discard(i)
    Cs = set(C)
    for t, e in enumerate(prog[:tc]):
        op = e[0]; touched = False
        if op in ('ADD', 'COPY'):
            d, s = e[1], e[2]
            if occ.get(d):
                q = m(e[3])
                for i in list(occ[d]): setc(i, s, (lam[i].get(s, 0) - q * lam[i][d]) % P)
                touched = s in Cs
        elif op == 'SCALE':
            r = e[1]
            if occ.get(r):
                iq = pow(m(e[2]), P - 2, P)
                for i in list(occ[r]): setc(i, r, lam[i][r] * iq % P)
        elif op == 'INIT':
            o = e[1]; i = nid[0]; nid[0] += 1; lam[i] = {}; setc(i, o, 1); touched = o in Cs
        elif op == 'CLEAR':
            o = e[1]; c = list(occ.get(o, ()))
            if c:
                piv = min(c, key=lambda i: len(lam[i])); pv = lam[piv]; ip = pow(pv[o], P - 2, P)
                for i in c:
                    if i == piv: continue
                    f = lam[i][o] * ip % P
                    for r, v in pv.items(): setc(i, r, (lam[i].get(r, 0) - f * v) % P)
                for r in list(pv): occ[r].discard(piv)
                del lam[piv]
            touched = True
        if t >= t_from and touched:
            rk = prank(list(lam.values()), sorted(Cs))
            if rk != last: out.append((t, e, rk)); last = rk
    return out

def culprit_chain(W, tc, C, t_from):
    """like culprit_ops, with per-(relation, coordinate) provenance: for each rank-dropping read d <- o, follow the
    ops that made the relation coordinates nonzero back from d: returns list of (t_drop, op, chain=[(t, op), ...])."""
    n = W['public']; prog = W['program']
    lam = {}; occ = collections.defaultdict(set); nid = [0]; who = {}; out = []; last = None
    def setc(i, r, v, t):
        L = lam[i]
        if v: L[r] = v; occ[r].add(i); who[(i, r)] = t
        else: L.pop(r, None); occ[r].discard(i)
    Cs = set(C)
    for t, e in enumerate(prog[:tc]):
        op = e[0]; touched = False; snap = None
        if op in ('ADD', 'COPY'):
            d, s = e[1], e[2]
            if occ.get(d):
                if t >= t_from and s in Cs: snap = [(i, dict(lam[i])) for i in occ[d]]
                q = m(e[3])
                for i in list(occ[d]): setc(i, s, (lam[i].get(s, 0) - q * lam[i][d]) % P, t)
                touched = s in Cs
        elif op == 'SCALE':
            r = e[1]
            if occ.get(r):
                iq = pow(m(e[2]), P - 2, P)
                for i in list(occ[r]): setc(i, r, lam[i][r] * iq % P, who.get((i, r), t))
        elif op == 'INIT':
            o = e[1]; i = nid[0]; nid[0] += 1; lam[i] = {}; setc(i, o, 1, t); touched = o in Cs
        elif op == 'CLEAR':
            o = e[1]; c = list(occ.get(o, ()))
            if c:
                piv = min(c, key=lambda i: len(lam[i])); pv = lam[piv]; ip = pow(pv[o], P - 2, P)
                for i in c:
                    if i == piv: continue
                    f = lam[i][o] * ip % P
                    for r, v in pv.items(): setc(i, r, (lam[i].get(r, 0) - f * v) % P, max(who.get((i, r), -1), who.get((piv, r), -1)))
                for r in list(pv): occ[r].discard(piv)
                del lam[piv]
            touched = True
        if t >= t_from and touched:
            rk = prank(list(lam.values()), sorted(Cs))
            if last is not None and rk < last and op in ('ADD', 'COPY'):
                # chain back from d through the relations that held d
                chain = []; seen = set()
                for i, L in (snap or []):
                    x = e[1]; tt = t
                    while (i, x) in who and (i, x) not in seen:
                        seen.add((i, x)); ts = who[(i, x)]
                        if ts >= tt or ts < 0: break
                        ee = prog[ts]; chain.append((ts, ee))
                        if ee[0] not in ('ADD', 'COPY') or ee[2] != x: break
                        x = ee[1]; tt = ts
                out.append((t, e, chain))
            last = rk
    return out


def main(argv):
    import gzip, json
    if len(argv) != 1:
        print('usage: python3 lossless.py WORD.json[.gz]   -> every lossy CLEAR (t, owned register, reads of it)'); return 2
    op = gzip.open if argv[0].endswith('.gz') else open
    with op(argv[0], 'rt') as f:
        W = json.load(f)
    loss, lam, occ = dual_scan(W)
    print('lossy CLEARs: %d' % len(loss))
    for t, o, reads in loss[:50]:
        print('  t=%d owned=%d reads-of-o=%s' % (t, o, reads[-5:]))
    print('relations live at end: %d' % len(lam))
    return 0 if not loss else 1


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]))
