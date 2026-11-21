"""UPHASE fattr.py (own code): FUTURE-ATTRIBUTION engine + exact checks.
Run model (FANOUT56 / RELAYTREE convention): registers hold Q-linear combos of symbols; charts are F2-subspaces of F2^N
(frozensets of ints); ADD dst += lam*src needs equal charts; publics only ascend; owned = INIT .. CLEAR, cost sum |d dim|.
Roles: ('X',t) target publics (label P[t]), ('Y',s) source publics (label P[s]), every other public = helper/relay.
Forward sweep: W[P] = cumulative reference weight (vector over targets t) on public P's content; an ADD dst += lam*src
into a public dst references src with weight omega = lam*([dst==X_t] e_t - W[dst]); src owned => output event alpha=omega.
Identity [P]: final(X_t)-start(X_t) = sum_P W_P[t] final_P + sum_e alpha_e[t] content_e.   Checked exactly here."""
import collections
from fractions import Fraction as Fr

dot = lambda a, b: bin(a & b).count('1') & 1
fdim = lambda F: len(F).bit_length() - 1

def basis(F):
    B = []
    for v in sorted(F):
        w = v
        for b in B:
            if w ^ b < w: w ^= b
        if w:
            B.append(w); B.sort(reverse=True)
    return B

def span(vs):
    S = {0}
    for v in vs:
        if v not in S: S |= {x ^ v for x in S}
    return frozenset(S)

def rank2(rows):
    """F2 rank of a list of int bitmasks"""
    piv = {}
    r = 0
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in piv: v ^= piv[h]
            else: piv[h] = v; r += 1; break
    return r

def v2(x):
    x = Fr(x); e = 0
    if x == 0: return 99
    n, d = x.numerator, x.denominator
    while n % 2 == 0: n //= 2; e += 1
    while d % 2 == 0: d //= 2; e -= 1
    return e

def mod4(x):
    """2-adic integer x mod 4"""
    x = Fr(x); assert v2(x) >= 0
    return (x.numerator * pow(x.denominator, -1, 4)) % 4

class Charts:
    def __init__(s, P): s.P = P; s.c = {}
    def info(s, F):
        if F not in s.c:
            B = basis(F)
            cold = frozenset(i for i, q in enumerate(s.P) if all(not dot(b, q) for b in B))   # F <= q_i^perp
            inn = frozenset(i for i, q in enumerate(s.P) if q in F)
            s.c[F] = (B, cold, inn)
        return s.c[F]

def analyze(prog, init, targets, P, verbose=True, check_identity=True):
    CH = Charts(P)
    reg = {k: [f, dict(c)] for k, (f, c) in init.items()}
    start = {k: dict(c) for k, (f, c) in init.items()}
    owned = {}            # reg -> lifetime index
    L = []                # lifetimes
    W = collections.defaultdict(dict)
    ev = []               # output events: (life, alpha dict, chart)
    bad = []
    isX = lambda r: isinstance(r, tuple) and r[0] == 'X'
    def addv(a, c, b):
        for k, v in b.items():
            a[k] = a.get(k, 0) + c * v
            if a[k] == 0: del a[k]
    for i, op in enumerate(prog):
        t = op[0]
        if t == 'INIT':
            r, f, c = op[1], op[2], op[3]
            reg[r] = [f, dict(c)]; owned[r] = len(L)
            L.append(dict(reg=r, init=f, cost=0, path=[f], intakes=[], outs=[], content=None, gtd=True, cold=True, nox=True))
        elif t == 'MOVE':
            r, f = op[1], op[2]; a = reg[r][0]
            if r in owned:
                if not (a <= f or f <= a): bad.append(('nest', i))
                lf = L[owned[r]]; lf['cost'] += abs(fdim(f) - fdim(a)); lf['path'].append(f)
            else:
                if not a <= f: bad.append(('public-descends', i, r))
                # invariant check: W[r][t]!=0 => q_t in chart (kept automatically since a<=f)
            reg[r][0] = f
        elif t == 'ADD':
            d, lam, s = op[1], Fr(op[2]), op[3]
            if reg[d][0] != reg[s][0]: bad.append(('frame', i))
            C = reg[d][0]
            if d in owned:
                lf = L[owned[d]]
                if lf['outs']: lf['gtd'] = False
                cont = reg[s][1]
                _, cold, _ = CH.info(C)
                hot = [k for k in cont if k[0] == 'y' and k[1] not in cold]
                hasx = [k for k in cont if k[0] == 'x']
                if hot: lf['cold'] = False
                if hasx: lf['nox'] = False
                lf['intakes'].append(C)
            else:
                om = {}
                if isX(d): om[d[1]] = lam
                for tt, v in W[d].items():
                    om[tt] = om.get(tt, 0) - lam * v
                om = {k: v for k, v in om.items() if v != 0}
                if s in owned:
                    lf = L[owned[s]]
                    cy = {k: v for k, v in reg[s][1].items()}
                    if lf['content'] is None: lf['content'] = cy
                    elif lf['content'] != cy: lf['gtd'] = False
                    lf['outs'].append(C); ev.append((owned[s], om, C, dict(cy)))
                else:
                    Ws = W[s]
                    for k, v in om.items():
                        Ws[k] = Ws.get(k, 0) + v
                        if Ws[k] == 0: del Ws[k]
            addv(reg[d][1], lam, reg[s][1])
        elif t == 'CLEAR':
            r = op[1]; del owned[r]; del reg[r]
        else:
            raise ValueError(op)
    fin = {k: dict(v[1]) for k, v in reg.items()}
    out = dict(bad=bad, L=L, ev=ev, W=W, fin=fin, start=start)
    # ---- chart invariants
    viol_W = sum(1 for p, w in W.items() for tt in w if P[tt] not in reg[p][0])
    viol_a = sum(1 for (_, om, C, _) in ev for tt in om if P[tt] not in C)
    out['viol_W'], out['viol_alpha'] = viol_W, viol_a
    # ---- x-balance: W on X publics must vanish at the end
    out['W_X_nonzero'] = sum(len(w) for p, w in W.items() if isX(p))
    # ---- Y-final terms on odd cells
    yodd = 0
    for p, w in W.items():
        if isinstance(p, tuple) and p[0] == 'Y':
            ss = p[1]
            for tt in w:
                if dot(P[tt], P[ss]): yodd += 1
    out['Yfinal_odd_terms'] = yodd
    # ---- helper finals y-free
    out['helper_final_y'] = sum(1 for p in W if not (isinstance(p, tuple) and p[0] in 'XY') and any(k[0] == 'y' for k in fin.get(p, {})))
    # ---- exact identity
    if check_identity:
        nbad = 0
        Xs = [k for k in init if isX(k)]
        for X in Xs:
            tt = X[1]
            lhs = dict(fin[X]); addv(lhs, -1, start[X])
            rhs = {}
            for p, w in W.items():
                if tt in w: addv(rhs, w[tt], fin[p])
            for (_, om, C, cy) in ev:
                if tt in om: addv(rhs, om[tt], cy)
            if lhs != rhs: nbad += 1
        out['identity_fail'] = nbad
    return out

def decoder_rows(out, P, ports=None):
    """one row per owned lifetime (needs GTD): w = sum alpha, v = y-part of content"""
    L, ev = out['L'], out['ev']
    rows = []
    for k, lf in enumerate(L):
        w = {}
        for (kk, om, C, cy) in ev:
            if kk != k: continue
            for tt, v in om.items(): w[tt] = w.get(tt, 0) + v
        w = {a: b for a, b in w.items() if b != 0 and (ports is None or a in ports)}
        v = {kk2[1]: b for kk2, b in (lf['content'] or {}).items() if kk2[0] == 'y' and (ports is None or kk2[1] in ports)}
        rows.append((w, v))
    return rows

def price(D, S, P):
    rowsb = []
    Sl = sorted(S)
    for tt in D:
        m = 0
        for j, ss in enumerate(Sl):
            if dot(P[tt], P[ss]): m |= 1 << j
        rowsb.append(m)
    return rank2(rowsb)

def chart_bound(lf):
    A = None
    for C in lf['intakes']:
        A = C if A is None else (A & C)
    if A is None: A = frozenset([0])
    B = span([x for C in lf['outs'] for x in basis(C)]) if lf['outs'] else frozenset([0])
    return fdim(B) - fdim(B & A)

def odd_check(out, rows, P, ports):
    """sum_k w_k v_k^T == receipts on all odd cells (incl. diagonal) restricted to ports"""
    fin, start = out['fin'], out['start']; nb = 0; ncell = 0
    for tt in ports:
        X = ('X', tt); rec = dict(fin[X])
        for k, v in start[X].items(): rec[k] = rec.get(k, 0) - v
        for ss in ports:
            if not dot(P[tt], P[ss]): continue
            ncell += 1
            val = sum((w.get(tt, 0) * v.get(ss, 0) for (w, v) in rows), Fr(0))
            if val != rec.get(('y', ss), 0): nb += 1
    return nb, ncell

def master(rows, P, ports, sign=-1):
    """mod-4 doubling quantities (ORBITLP sec.3) for a half-integer decoder: sign*sum w v^T = I on odd cells, rows rescaled to (1/2) W V^T."""
    ports = list(ports); idx = {p: i for i, p in enumerate(ports)}; n = len(ports)
    A = []; Bv = []; Wp = []; Vp = []
    for (w, v) in rows:
        if not w or not v: continue
        mw = min(v2(x) for x in w.values()); mv = min(v2(x) for x in v.values())
        # HC convention: row = (1/2) W V^T with W, V 2-adically integral (then sum W V^T o Q = 2I on odd cells)
        if mw + mv < -1: return dict(error='not half-integral', mw=mw, mv=mv)
        a = -mw
        wd = {p: mod4(sign * x * Fr(2) ** a) for p, x in w.items()}
        vd = {p: mod4(x * Fr(2) ** (1 - a)) for p, x in v.items()}
        A.append({p: c % 2 for p, c in wd.items()}); Wp.append({p: (c // 2) % 2 for p, c in wd.items()})
        Bv.append({p: c % 2 for p, c in vd.items()}); Vp.append({p: (c // 2) % 2 for p, c in vd.items()})
    odd = lambda t, s: dot(P[ports[t]], P[ports[s]])
    def mat(L1, L2):
        M = [0] * n
        for l1, l2 in zip(L1, L2):
            for p, c1 in l1.items():
                if not c1: continue
                t = idx[p]
                for q, c2 in l2.items():
                    if c2 and odd(t, idx[q]): M[t] ^= 1 << idx[q]
        return M
    LL = mat(A, Bv); Y = mat(Wp, Bv); Z = mat(A, Vp); E = mat(Wp, Vp)
    # X = (N/2 mod 2), N = sum (a b^T) o Q over Z
    N = [[0] * n for _ in range(n)]
    for l1, l2 in zip(A, Bv):
        for p, c1 in l1.items():
            if not c1: continue
            for q, c2 in l2.items():
                if c2 and odd(idx[p], idx[q]): N[idx[p]][idx[q]] += 1
    Xm = [sum(((N[t][s] // 2) % 2) << s for s in range(n)) for t in range(n)]
    IX = [Xm[t] ^ (1 << t) for t in range(n)]
    big = [(Y[t] | (E[t] << n)) for t in range(n)] + [(Z[t] << n) for t in range(n)]
    return dict(lowerleft=sum(bin(x).count('1') for x in LL), rkY=rank2(Y), rkZ=rank2(Z), rkBlock=rank2(big),
                rkIX=rank2(IX), YZ_eq_IX=all((Y[t] ^ Z[t]) == IX[t] for t in range(n)), m=len(A))
