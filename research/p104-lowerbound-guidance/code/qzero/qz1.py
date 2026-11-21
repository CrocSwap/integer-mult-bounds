# QZERO qz1: own exact checker. Expands a caller JSON (data) into CallerWord events (host, then idle contacts in code order),
# replays over Q(i)[q]/(q^4-1)[D] (= product over q in {1,-1,i,-i}, CRT, i in base field) with symbolic D, checks the target,
# counts the CallerWord columns Iota (nonzero q-odd slots), builds the frame A,B at q=1,D=1 and the stage K-blocks (sgK),
# and evaluates cHat(.99) = 104/k * invoice against HP(k).
import sys, json, sympy as sp
from fractions import Fraction as F
I_ = sp.I
def load(f):
    C = json.load(open(f)); n, k = C['roles'], C['stages']; ev = []
    for e in C['events']:
        op = e[0]
        if op == 'HOST':
            t, s, tt, a, b = e[1]-1, e[2], e[3], sp.Rational(e[4]), sp.Rational(e[5])
            ev += [('host', s, tt, a, b), ('idle', s, frozenset({t}), 0), ('idle', tt, frozenset({t}), 0)]
        elif op == 'ADD': ev.append(('add', e[1], e[2], sp.Rational(e[3])))
        elif op == 'SCALE': ev.append(('scale', e[1], sp.Rational(e[2])))
        elif op == 'SWAP': ev.append(('swap', e[1], e[2]))
        elif op == 'QUERY': ev.append(('query', e[1], e[2], e[3]))
        elif op == 'LAMBDA': ev.append(('lam', e[1], e[2]))
        elif op == 'IDLE_ONE': ev.append(('idle', e[1], frozenset(s-1 for s in e[2]), 0))
        else: raise ValueError(op)
    masks = [frozenset(s for s, b in enumerate(dg[2:]) if b) for dg in C['diagonal']]
    ex = [dg[0] for dg in C['diagonal']]
    return n, k, ev, masks, ex
def qp(q, s): return q**(s % 4)
def evmat(e, n, q, D):
    M = sp.eye(n); op = e[0]
    if op == 'add': M[e[1], e[2]] += e[3]
    elif op == 'scale': M[e[1], e[1]] = e[2]
    elif op == 'swap': M = sp.zeros(n); [M.__setitem__((x, x if x not in (e[1], e[2]) else (e[2] if x == e[1] else e[1])), 1) for x in range(n)]
    elif op == 'query': M[e[1], e[2]] += qp(q, e[3])
    elif op == 'lam': M[e[1], e[1]] = sp.Rational(1, 2)*(1+e[2]*I_) + sp.Rational(1, 2)*(1-e[2]*I_)*q**2
    elif op == 'idle': M[e[1], e[1]] = qp(q, e[3]) * sp.Mul(*[D[t] for t in e[2]])
    elif op == 'host':
        s, t, a, b = e[1:]; M[s, t] = a*q; M[t, s] = b*q**3; M[t, t] = 1 + a*b
    return M
def terms(e):
    op = e[0]
    if op == 'query': return [(e[1], e[2], -2 if e[3] % 2 else 0)]
    if op == 'idle': return [(e[1], e[1], -2 if e[3] % 2 else 0)]
    if op == 'host': return [(e[1], e[2], -2*e[3]), (e[2], e[1], -2*e[4])]
    return []
def check(f):
    n, k, ev, masks, ex = load(f)
    D = sp.symbols('D0:%d' % k)
    ok = True
    for q in (1, -1, I_, -I_):
        P = sp.eye(n)
        for e in ev: P = (evmat(e, n, q, D) * P).applyfunc(sp.expand)
        T = sp.diag(*[sp.expand(qp(q, ex[r]) * sp.Mul(*[D[t] for t in masks[r]])) for r in range(n)])
        good = (P - T).applyfunc(sp.expand) == sp.zeros(n)
        ok &= good
        print('  replay q=%s symbolic D: %s' % (q, good))
    print(f.split('/')[-1], 'n', n, 'k', k, 'events', len(ev), 'ex', ex, 'masks', [sorted(m) for m in masks], 'LEGAL(all 4 q, symbolic D):', ok)
    print('  WF hosts distinct:', all(e[1] != e[2] for e in ev if e[0] == 'host'))
    # frame
    one = {t: 1 for t in range(k)}
    pre = [sp.eye(n)]
    for e in ev: pre.append(evmat(e, n, 1, [1]*k) * pre[-1])
    cols = []
    for j, e in enumerate(ev):
        for (x, y, c) in terms(e):
            if c != 0:
                a = pre[j+1].inv()[:, x] * c; b = pre[j].T[:, y]
                cols.append((j, a, b))
    print('  |Iota| =', len(cols), ' 2k =', 2*k, ' Q = |Iota|-2k =', len(cols)-2*k, ' n+2 =', n+2)
    m = len(cols); A = sp.Matrix.hstack(*[c[1] for c in cols]); B = sp.Matrix.hstack(*[c[2] for c in cols]); beta = [c[0] for c in cols]
    G = B.T * A
    K = sp.Matrix(m, m, lambda i, j: (2 if i == j else 0) + (G[i, j] if beta[i] <= beta[j] else -G[i, j]))
    print('  rank K =', K.rank(), ' rank G =', G.rank())
    Vp = sp.eye(n)
    for j in sorted(set(beta)):
        idx = [i for i in range(m) if beta[i] == j]
        Vp = (sp.eye(n) + A[:, idx] * B[:, idx].T) * Vp
    print('  prod V =', Vp.tolist())
    hosts = sorted({c[0] for c in cols if ev[c[0]][0] == 'host'})
    for j in hosts:
        idx = [i for i in range(m) if beta[i] == j]
        print('  host event', j, 'stage', [t for t in ev[j+1][2]], 'K-block det', K.extract(idx, idx).det(), ' a*b', ev[j][3]*ev[j][4])
    s = sp.Rational(99, 100)
    inv = sum((8*len(mk)+1)**s for mk in masks) - sum((8*len(e[2]))**s for e in ev if e[0] == 'idle' and e[2])
    chat = sp.N(104*inv/k, 20)
    HP = sp.N(sp.Rational(208, k)*((k-2)*(17**s-16**s) + (8*k+1)**s - 8**s*k), 20)
    print('  degrees', [len(mk) for mk in masks], ' cHat(.99) =', chat, ' HP(k) =', HP, ' cHat<=HP:', chat <= HP)
for f in sys.argv[1:]: check(f)
