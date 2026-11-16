# LOANBUILD templates (own code).  Side B: partner p (the source of r's X-write) inserts B after X; loan c += beta*r at A,
# c's existing X-transfer into p carries rho to X, readers re-read p (or a stationary snapshot of p), settles at B.
# Side A: partner p (the reader of r at X) inserts A before X; p reads r at A, signed role swap r += b*p, loan r += beta*c
# at A, p picks up r's X-writes from their sources (or stationary snapshots), settle r += eps*c at B.
import collections, math
from fractions import Fraction as Q
import lb

def fr(x): return Q(x)

def r_xinfo(Wd, r, X):
    """(A,B,kr0,k1,k2,k3, xops) for r's interior stop X, or None"""
    S = Wd.seg[r]; ks = Wd.segidx(r, X)
    if len(ks) != 1: return None
    k = ks[0]
    if k == 0 or k + 1 >= len(S): return None
    (A, kr0, k1), (_, _, k2), (B, _, k3) = S[k - 1], S[k], S[k + 1]
    return A, B, kr0, k1, k2, k3, Wd.ops_at(r, k1, k2)

def carriers(Wd, A, X, B, excl):
    out = []
    for q in range(Wd.n):
        if q in excl: continue
        S = Wd.seg[q]
        for j in range(len(S) - 2):
            if S[j][0] == A and S[j + 1][0] == X and S[j + 2][0] == B:
                out.append((q, S[j][1], S[j][2], S[j + 1][2], S[j + 2][2]))
    return out

def classify(Wd, r, xops):
    P = Wd.W['program']; W = []; R = []
    for i in xops:
        e = P[i]
        if e[0] != 'ADD': return None
        if e[1] == r and e[2] != r and e[2] < Wd.n: W.append((i, e[2], e[3]))
        elif e[2] == r and e[1] != r and e[1] < Wd.n: R.append((i, e[1], e[3]))
        else: return None
    return W, R

def build_B(Wd, r, X, p, c_info, beta, snap=False):
    P = Wd.W['program']; info = r_xinfo(Wd, r, X)
    if info is None: return None, 'r path'
    A, B, kr0, k1, k2, k3, xops = info
    cl = classify(Wd, r, xops)
    if cl is None: return None, 'r ops'
    Wr, Rd = cl
    if not Wr or any(s != p for _, s, _ in Wr): return None, 'writes not from p'
    if any(t == p for _, t, _ in Rd): return None, 'p reads r'
    js = Wd.segidx(p, X)
    if len(js) != 1: return None, 'p path'
    j = js[0]; Sp = Wd.seg[p]
    if j + 1 >= len(Sp): return None, 'p final at X'
    _, pa, pb = Sp[j]; C = Sp[j + 1][0]
    if not Wd.lt(B, C) or not Wd.lt(X, B): return None, 'nest'
    pXops = Wd.ops_at(p, pa, pb)
    q, cA0, ca1, ca2, ca3 = c_info
    rA = Wd.ops_at(r, kr0, k1); rLA = rA[-1] if rA else kr0
    rAw = [i for i in rA if P[i][1] == r]
    if not kr0 < ca1: return None, 'loan time'
    tL = ca1 - 0.5; slide = [i for i in rAw if i > tL]; gen = False
    for m, i in enumerate(slide):
        s = P[i][2]
        if (P[i][0] != 'ADD' or Wd.where(s, ca1) != A or [j for j in Wd.ops_at(s, ca1 - 1, i) if P[j][1] == s]
                or [j for j in Wd.ops_at(r, ca1 - 1, i) if P[j][2] == r]): gen = True
    if gen: slide = []
    rest = [i for i in rA if i not in slide and not (gen and i > tL)]
    tRM = max([tL] + rest) + 0.01
    sig = [i for i, _, _ in Rd]
    if any(i < pa for i in sig) and not snap: return None, 'read before p at X'
    lpX = max(pXops + sig + [pa])
    tp1 = lpX + 0.3
    if tp1 > pb: return None, 'p leave'
    tBc = max(ca2, tRM) + 0.4; tB = max(tp1, tRM) + 0.4
    if not (tB < pb and tBc < ca3): return None, 'settle window'
    cd = lb.Cand(Wd)
    cd.dele |= set(xops) | {k1, k2, pb}
    for m, i in enumerate(slide):
        cd.dele.add(i); cd.add(tL - 0.2 + 0.001 * m, list(P[i]))
    if gen and not slide_earlier(Wd, cd, r, kr0, k1, tL - 0.1): return None, 'slide r earlier'
    cd.add(tL, ['ADD', q, r, str(beta), A])
    cd.add(tRM, ['MOVE', r, A, B, False])
    used = set()
    for t_i, (i, t, al) in enumerate(Rd):
        if not snap:
            cd.add(i + 0.001, ['ADD', t, p, cd.var('$g%d' % t_i), X])
        else:
            # stationary snapshot of p taken right after the (removed) write time, read at the read time
            tw = max([w for w, _, _ in Wr if w < i] or [None]) if any(w < i for w, _, _ in Wr) else None
            if tw is None: cd.add(i + 0.001, ['ADD', t, p, cd.var('$g%d' % t_i), X]); continue
            o = lb.free_label(Wd, tw - 1, i + 1, used)
            if o is None: return None, 'no label'
            used.add(o)
            cd.add(tw - 0.003, ['INIT', o, X]); cd.add(tw - 0.002, ['ADD', o, p, '1', X])
            cd.add(i + 0.001, ['ADD', t, o, cd.var('$g%d' % t_i), X]); cd.add(i + 0.002, ['CLEAR', o, X])
    cd.add(tp1, ['MOVE', p, X, B, False])
    cd.add(float(pb), ['MOVE', p, B, C, False])
    cd.add(tB, ['ADD', p, r, cd.var('$z'), B])
    cd.add(tBc + 0.01, ['ADD', q, r, cd.var('$e'), B])
    tW = max(tB, tBc) + 0.1
    for m, (i, s, qq) in enumerate(Wr):
        cd.add(tW + 0.001 * m, ['ADD', r, p, qq, B])
    if not slide_later(Wd, cd, r, B, k2, k3, tW + 0.01): return None, 'slide later'
    cd.meta = dict(side='B', r=r, X=X, p=p, c=q, beta=str(beta), A=A, B=B, snap=snap)
    return cd, 'ok'

def build_A(Wd, r, X, p, c_info, snap=False, early=False, slide=True):
    P = Wd.W['program']; info = r_xinfo(Wd, r, X)
    if info is None: return None, 'r path'
    A, B, kr0, k1, k2, k3, xops = info
    cl = classify(Wd, r, xops)
    if cl is None: return None, 'r ops'
    Wr, Rd = cl
    if len(Rd) != 1 or Rd[0][1] != p: return None, 'reads'
    sgm, _, al = Rd[0]
    if any(s == p for _, s, _ in Wr): return None, 'p writes r'
    if any(w > sgm for w, _, _ in Wr): return None, 'write after read'
    js = Wd.segidx(p, X)
    if len(js) != 1: return None, 'p path'
    j = js[0]; Sp = Wd.seg[p]
    if j == 0: return None, 'p initial at X'
    Z, pz0, pa = Sp[j - 1]; _, _, pb = Sp[j]
    if not Wd.lt(Z, A) or not Wd.lt(A, X): return None, 'nest'
    pZ = Wd.ops_at(p, pz0, pa); lpZ = pZ[-1] if pZ else pz0
    pX = Wd.ops_at(p, pa, pb); fpX = pX[0] if pX else pb
    q, cA0, ca1, ca2, ca3 = c_info
    rA = Wd.ops_at(r, kr0, k1); rLA = rA[-1] if rA else kr0
    hi = min(fpX, ca1); tA = hi - 0.5
    if not (max(kr0, pz0) < tA - 0.5): return None, 'A window'
    if rLA > tA - 0.5 or lpZ > tA - 0.5:
        if not slide: return None, 'A window'
    tL = max(ca1 - 0.5, tA + 0.3); tRM = max(tA + 0.45, tL + 0.01)
    tB = max(ca2, tRM) + 0.5
    if not tB < ca3: return None, 'B window'
    cd = lb.Cand(Wd)
    cd.dele |= set(xops) | {k1, k2, pa}
    if not slide_earlier(Wd, cd, r, kr0, k1, tA - 0.45): return None, 'slide r earlier'
    if not slide_earlier(Wd, cd, p, pz0, pa, tA - 0.45): return None, 'slide p earlier'
    cd.add(tA, ['MOVE', p, Z, A, False])
    cd.add(tA + 0.1, ['ADD', p, r, al, A])
    cd.add(tA + 0.2, ['ADD', r, p, cd.var('$b'), A])
    cd.add(tL, ['ADD', r, q, cd.var('$be'), A])
    cd.add(tA + 0.4, ['MOVE', p, A, X, False])
    cd.add(tRM, ['MOVE', r, A, B, False])
    used = set()
    for m, (w, s, qq) in enumerate(Wr):
        g = str(Q(al) * Q(qq))
        # direct read if s is at X at the read time and unchanged since the write; else stationary snapshot
        tr = (max(w, tA + 0.4) + 0.0005 + 0.0001 * m) if early else (sgm + 0.001 + 0.0001 * m)
        sch = Wd.where(s, int(tr) + 1) if s < Wd.n else None
        unchanged = not [i for i in Wd.ops_at(s, w, int(tr) + 1) if P[i][1] == s and i != w]
        if not snap and sch == X and unchanged:
            cd.add(tr, ['ADD', p, s, g, X])
        else:
            o = lb.free_label(Wd, w - 1, int(tr) + 1, used)
            if o is None: return None, 'no label'
            used.add(o)
            cd.add(w - 0.003, ['INIT', o, X]); cd.add(w - 0.002, ['ADD', o, s, '1', X])
            cd.add(tr, ['ADD', p, o, g, X]); cd.add(tr + 0.00005, ['CLEAR', o, X])
    cd.add(tB, ['ADD', r, q, cd.var('$ep'), B])
    if not slide_later(Wd, cd, r, B, k2, k3, tB + 0.01): return None, 'slide later'
    cd.meta = dict(side='A', r=r, X=X, p=p, c=q, A=A, B=B, snap=snap, early=early)
    return cd, 'ok'


def slide_earlier(Wd, cd, x, a, b, cut):
    """move x's ops in its stay (a,b) that come after cut to just before cut (order kept).  Partners must sit at the
    chart at cut and be untouched in between (other than by the slid ops)."""
    P = Wd.W['program']; ops = [i for i in Wd.ops_at(x, a, b) if i > cut and i not in cd.dele]
    if not ops: return True
    ch = Wd.where(x, ops[0])
    for m, i in enumerate(ops):
        e = P[i]; ys = [y for y in ([e[1], e[2]] if e[0] in ('ADD', 'COPY') else [e[1]]) if y != x]
        for y in ys:
            if y >= Wd.n or Wd.where(y, int(cut)) != ch: return False
            if [j for j in Wd.ops_at(y, int(cut) - 1, i) if j > cut and j != i and j not in ops]: return False
    for m, i in enumerate(ops):
        cd.dele.add(i); cd.add(cut - 0.4 + 0.001 * m, list(P[i]))
    return True

def slide_later(Wd, cd, r, B, k2, k3, tW):
    """move r's ops that precede the cursor (starting at tW, chart B) to just after it, cascading through r's later
    stops (r's MOVEs follow).  Partner registers must sit at that chart at the new time and be untouched in between."""
    P = Wd.W['program']; S = Wd.seg[r]
    k = [j for j, x in enumerate(S) if x[1] == k2][0]
    cur = tW; moved = set()
    while k < len(S):
        Y, a, b = S[k]
        ops = [i for i in Wd.ops_at(r, a, b) if i < cur and i not in cd.dele]
        t0 = cur + 0.5
        for m, i in enumerate(ops):
            e = P[i]; ys = [x for x in ([e[1], e[2]] if e[0] in ('ADD', 'COPY') else [e[1]]) if x != r]
            for y in ys:
                if y >= Wd.n: return False
                if Wd.where(y, int(t0) + 1) != Y: return False
                if [j for j in Wd.ops_at(y, i, int(t0) + 1) if j != i and j not in ops and j not in moved]: return False
            cd.dele.add(i); cd.add(t0 + 0.001 * m, list(e)); moved.add(i)
        last = t0 + 0.001 * len(ops) if ops else cur
        if b >= Wd.T or b > last: return True
        cd.dele.add(b); cd.add(last + 0.1, list(P[b])); cur = last + 0.1; k += 1
    return True

def betas(Wd, r, X, p, cinfo):
    """loan coefficient candidates from c's transfers into p at X and r's write coefficients"""
    P = Wd.W['program']; q, cA0, ca1, ca2, ca3 = cinfo
    lam = [Q(P[i][3]) for i in Wd.ops_at(q, ca1, ca2) if P[i][0] == 'ADD' and P[i][1] == p and P[i][2] == q]
    info = r_xinfo(Wd, r, X); qs = [Q(P[i][3]) for i in info[6] if P[i][1] == r]
    out = []
    for l in lam:
        for qq in qs:
            out += [1 / (qq * l), -1 / (qq * l), 1 / l, -1 / l]
    out += [Q(1), Q(-1), Q(2), Q(-2), Q(1, 2), Q(-1, 2), Q(4), Q(-4), Q(1, 4), Q(-1, 4)]
    return list(dict.fromkeys(out)), bool(lam)

def try_instance(Wd, r, X, p, side, maxc=12):
    """returns (W2, cand, sol) or (None, reason)"""
    info = r_xinfo(Wd, r, X)
    if info is None: return None, 'r path'
    A, B = info[0], info[1]
    cs = carriers(Wd, A, X, B, {r, p})
    if not cs: return None, 'no carrier'
    why = collections.Counter()
    for snap in (False, True):
        for ci in cs[:maxc]:
            if side == 'B':
                bl, haslam = betas(Wd, r, X, p, ci)
                if not haslam: bl = bl[-10:]
                for be in bl:
                    cd, msg = build_B(Wd, r, X, p, ci, be, snap)
                    if cd is None: why[msg] += 1; break
                    sol = cd.solve()
                    if sol is None: why['nosol'] += 1; continue
                    return (cd.instantiate(sol), cd, sol), 'ok'
            else:
                for early in (False, True):
                    cd, msg = build_A(Wd, r, X, p, ci, snap, early)
                    if cd is None: why[msg] += 1; continue
                    sol = cd.solve()
                    if sol is None: why['nosol'] += 1; continue
                    return (cd.instantiate(sol), cd, sol), 'ok'
    return None, dict(why)
