#!/usr/bin/env python3
"""Exact checks of the helper-free Whitehead (t = -1, d = 0) native on the 104 ports of P104.  Standard library only.

  python3.12 -I -B window_native.py            check the shipped object, regenerate it, run the mutants
  python3.12 -I -B window_native.py --emit F   (re)write the object file F from the generator

What it does
  * regenerates the word from the generator below and requires it to equal data/window_native.json.gz exactly;
  * replays the object event by event in exact Fractions (engine A: frame law, dyadic coefficients, paid ranks,
    owned lifetimes, final frames, exact endpoint X = x + alpha y, Y = beta x, helpers none);
  * replays it a second time mod 2^61 - 1 on random inputs (engine B);
  * checks the 208 x 208 transfer matrix exactly (T[Y,Y] = 0 so d = 0, T[Y,X] = beta I, T[X,Y] = alpha I, det = 1);
  * prices the layer (public and owned) with the invoice rule at the kappa of the baseline, and the floor 208 * 8^(1-k);
  * recomputes the budget lines owned <= 111.573067 + T - dpub from the quoted ledger constants;
  * checks the 2 x 2 caller block (a dyadic conjugator exists for the -1 sector);
  * runs 100 single-edit mutants (pairs 0, 25, 51) and four wrong-target judgements; each non-null mutant must be rejected.
Owned moves go UP as well as down: the word is valid only under the owned-ascent allowance (declared in README.md)."""
import gzip, itertools, json, os, random, sys, decimal, hashlib
from fractions import Fraction as Q
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
KAPPA = decimal.Decimal('0.0036270188296')       # the baseline's kappa, used as the pricing exponent
PR = (1 << 61) - 1
decimal.getcontext().prec = 50


def span(b):
    s = {0}
    for v in b:
        if v not in s:
            s |= {x ^ v for x in s}
    return frozenset(s)


def basis(F):
    b = []; s = {0}
    for x in sorted(F):
        if x not in s:
            b.append(x); s |= {y ^ x for y in s}
    return b


def dim(F): return len(F).bit_length() - 1
def dot(a, b): return bin(a & b).count('1') & 1
def perp(v, k): return frozenset(x for x in range(2 ** k) if not dot(x, v))
def isdy(c): return c != 0 and (c.denominator & (c.denominator - 1)) == 0
def isunit(c): return isdy(c) and (abs(c.numerator) & (abs(c.numerator) - 1)) == 0


def matching(ports, seed=0):
    v = len(ports); adj = {i: [j for j in range(v) if j != i and not dot(ports[i], ports[j])] for i in range(v)}
    rng = random.Random(seed)
    for _ in range(20000):
        order = list(range(v)); rng.shuffle(order); used = set(); M = []
        for i in order:
            if i in used: continue
            c = [j for j in adj[i] if j not in used]
            if not c: break
            j = rng.choice(c); used |= {i, j}; M.append((i, j))
        if len(M) * 2 == v: return M
    return None


def build(ports, k, alpha, beta):
    """Windowed native: per dot-0 pair (a, b) two owned rank-1 registers exchange x_a, x_b through <q_a, q_b>
    (UP then DOWN each), then Y_b is moved into the window <q_a> (inside q_b-perp) where the swap
    X_a += delta Y_b, Y_b += gamma X_a removes y and creates beta x."""
    v = len(ports); X = list(range(v)); Y = list(range(v, 2 * v)); C1, C2 = 2 * v, 2 * v + 1
    full = span([1 << i for i in range(k)]); Z = span([])
    init = [span([q]) for q in ports] + [Z] * v + [None, None]
    final = [full] * v + [perp(q, k) for q in ports] + [None, None]
    owned = [False] * (2 * v) + [True, True]
    gam = Q(beta); dl = -1 / gam; s = Q(alpha) / dl
    assert isunit(s) and isdy(dl) and isdy(gam) and Q(alpha) * Q(beta) == -1
    M = matching(ports); assert M
    W = []
    for a, b in M:
        La, Lb, Lab = span([ports[a]]), span([ports[b]]), span([ports[a], ports[b]])
        W += [('INIT', C1, La), ('ADD', C1, X[a], Q(1)), ('INIT', C2, Lb), ('ADD', C2, X[b], Q(1)),
              ('MOVE', C1, Lab), ('MOVE', C1, Lb), ('MOVE', C2, Lab), ('MOVE', C2, La),
              ('ADD', C1, X[b], Q(-1)), ('ADD', X[b], C1, Q(1)), ('CLEAR', C1),
              ('ADD', C2, X[a], Q(-1)), ('ADD', X[a], C2, Q(1)), ('CLEAR', C2)]
        for (p, t) in ((a, b), (b, a)):
            W += [('MOVE', Y[t], span([ports[p]]))]
            if s != 1: W += [('SCALE', Y[t], s)]
            W += [('ADD', X[p], Y[t], dl), ('ADD', Y[t], X[p], gam)]
    for r in X + Y: W.append(('MOVE', r, final[r]))
    for a, b in M:
        W += [('ADD', X[a], X[b], Q(1)), ('ADD', X[b], X[a], Q(-1)), ('ADD', X[a], X[b], Q(1)), ('SCALE', X[b], Q(-1))]
    return dict(init=init, final=final, owned=owned, prog=W, v=v, k=k, alpha=Q(alpha), beta=Q(beta))


# ----------------------------------------------------------------------------------- object (de)serialisation
def to_obj(w, ports):
    fr = lambda F: None if F is None else basis(F)
    ev = []
    for e in w['prog']:
        if e[0] in ('INIT', 'MOVE'): ev.append([e[0], e[1], basis(e[2])])
        elif e[0] == 'CLEAR': ev.append(['CLEAR', e[1]])
        elif e[0] == 'SCALE': ev.append(['SCALE', e[1], str(e[2])])
        else: ev.append(['ADD', e[1], e[2], str(e[3])])
    return dict(format='p104-whitehead-window-native-1', ports=ports, k=w['k'], alpha=str(w['alpha']), beta=str(w['beta']),
                init=[fr(F) for F in w['init']], final=[fr(F) for F in w['final']], owned=w['owned'], events=ev)


def from_obj(o):
    assert o['format'] == 'p104-whitehead-window-native-1'
    fr = lambda b: None if b is None else span(b)
    prog = []
    for e in o['events']:
        if e[0] in ('INIT', 'MOVE'): prog.append((e[0], e[1], span(e[2])))
        elif e[0] == 'CLEAR': prog.append(('CLEAR', e[1]))
        elif e[0] == 'SCALE': prog.append(('SCALE', e[1], Q(e[2])))
        else: prog.append(('ADD', e[1], e[2], Q(e[3])))
    return dict(init=[fr(b) for b in o['init']], final=[fr(b) for b in o['final']], owned=o['owned'], prog=prog,
                v=len(o['ports']), k=o['k'], alpha=Q(o['alpha']), beta=Q(o['beta'])), o['ports']


# ----------------------------------------------------------------------------------- engine A: exact
def engineA(w, prog, alpha, beta):
    v = w['v']; n = len(w['init']); V = []
    def bad(i, why): V.append((i, why))
    cur = list(w['init']); live = [False] * n
    rows = [({r: Q(1)} if r < 2 * v else {}) for r in range(n)]
    owned = w['owned']; pub = Counter(); own = Counter(); peak = 0; life = 0; dirty = 0
    ups = Counter(); downs = Counter(); ok_sub = {}
    def sub(F):
        if F not in ok_sub: ok_sub[F] = (span(basis(F)) == F)
        return ok_sub[F]
    for i, e in enumerate(prog):
        op = e[0]
        if op == 'INIT':
            r, F = e[1], e[2]
            if not owned[r] or live[r]: bad(i, 'init'); continue
            if not sub(F): bad(i, 'frame not subspace')
            live[r] = True; cur[r] = F; rows[r] = {}; life += 1; peak = max(peak, sum(live))
        elif op == 'CLEAR':
            r = e[1]
            if not (owned[r] and live[r]): bad(i, 'clear'); continue
            if rows[r]: dirty += 1
            live[r] = False; cur[r] = None; rows[r] = {}
        elif op == 'MOVE':
            r, F = e[1], e[2]; A = cur[r]
            if A is None: bad(i, 'move dead'); continue
            if not sub(F): bad(i, 'frame not subspace')
            if owned[r]:
                if not live[r] or not (A < F or F < A): bad(i, 'owned nest')
                d = dim(F) - dim(A); own[abs(d)] += 1; (ups if d > 0 else downs)[abs(d)] += 1
            else:
                if not (A < F): bad(i, 'public up')
                pub[dim(F) - dim(A)] += 1
            cur[r] = F
        elif op == 'SCALE':
            r, c = e[1], Q(e[2])
            if cur[r] is None or (owned[r] and not live[r]): bad(i, 'scale dead'); continue
            if not isunit(c): bad(i, 'scale unit')
            rows[r] = {k: x * c for k, x in rows[r].items()}
        elif op == 'ADD':
            d, a, c = e[1], e[2], Q(e[3])
            if d == a: bad(i, 'self add'); continue
            if cur[d] is None or cur[a] is None or cur[d] != cur[a]: bad(i, 'chart'); continue
            if (owned[d] and not live[d]) or (owned[a] and not live[a]): bad(i, 'dead owned'); continue
            if not isdy(c): bad(i, 'dyadic')
            if not (abs(c) + 1 < 2 ** 16): bad(i, 'growth')
            rd = rows[d]
            for k, x in rows[a].items():
                y = rd.get(k, 0) + c * x
                if y: rd[k] = y
                else: rd.pop(k, None)
        else: bad(i, 'unknown op ' + str(op))
    if any(live): bad(-1, 'owned live at end')
    for r in range(2 * v):
        if cur[r] != w['final'][r]: bad(-1, 'final frame r=%d' % r)
    badrows = 0
    for p in range(v):
        if rows[p] != {p: Q(1), v + p: Q(alpha)}: badrows += 1
        if rows[v + p] != {p: Q(beta)}: badrows += 1
    for r in range(2 * v, n):
        if rows[r]: badrows += 1
    return dict(viol=V, bad=badrows, pub=pub, own=own, peak=peak, life=life, dirty=dirty, rows=rows, ups=ups, downs=downs)


# ----------------------------------------------------------------------------------- engine B: mod 2^61 - 1
def engineB(w, prog, alpha, beta, K=4, seed=7):
    v = w['v']; n = len(w['init']); rnd = random.Random(seed); bad = 0
    m = lambda c: (Q(c).numerator % PR) * pow(Q(c).denominator, PR - 2, PR) % PR
    for _ in range(K):
        x0 = [rnd.randrange(PR) for _ in range(2 * v)]
        val = x0 + [0] * (n - 2 * v)
        for e in prog:
            op = e[0]
            if op in ('INIT', 'CLEAR'): val[e[1]] = 0
            elif op == 'SCALE': val[e[1]] = val[e[1]] * m(e[2]) % PR
            elif op == 'ADD': val[e[1]] = (val[e[1]] + m(e[3]) * val[e[2]]) % PR
        for p in range(v):
            if val[p] != (x0[p] + m(alpha) * x0[v + p]) % PR: bad += 1
            if val[v + p] != m(beta) * x0[p] % PR: bad += 1
        bad += sum(1 for r in range(2 * v, n) if val[r])
    return bad


def rank_inv(M):
    n = len(M); A = [r[:] + [Q(int(i == j)) for j in range(n)] for i, r in enumerate(M)]
    for c in range(n):
        p = next((i for i in range(c, n) if A[i][c] != 0), None)
        if p is None: return None
        A[c], A[p] = A[p], A[c]; f = 1 / A[c][c]; A[c] = [x * f for x in A[c]]
        for i in range(n):
            if i != c and A[i][c] != 0:
                g = A[i][c]; A[i] = [x - g * y for x, y in zip(A[i], A[c])]
    return [r[n:] for r in A]


def structure(w, rows, alpha, beta):
    v = w['v']; out = {}
    T = [[rows[r].get(c, Q(0)) for c in range(2 * v)] for r in range(2 * v)]
    out['T[Y,Y] == 0 on all %d entries (d = 0, raw)' % (v * v)] = all(T[v + p][v + q] == 0 for p in range(v) for q in range(v))
    out['T[Y,X] == beta I'] = all(T[v + p][q] == (Q(beta) if p == q else 0) for p in range(v) for q in range(v))
    out['T[X,X] == I'] = all(T[p][q] == (1 if p == q else 0) for p in range(v) for q in range(v))
    out['T[X,Y] == alpha I'] = all(T[p][v + q] == (Q(alpha) if p == q else 0) for p in range(v) for q in range(v))
    out['every row supported on its own (x_p, y_p)'] = all(set(rows[r]) <= {r % v, v + r % v} for r in range(2 * v))
    inv = rank_inv(T)
    out['T invertible (exact, %d x %d)' % (2 * v, 2 * v)] = inv is not None
    if inv is not None:
        out['Tinv[X,Y] == -alpha I'] = all(inv[p][v + q] == (-Q(alpha) if p == q else 0) for p in range(v) for q in range(v))
        out['Tinv[Y,Y] == I'] = all(inv[v + p][v + q] == (1 if p == q else 0) for p in range(v) for q in range(v))
    out['det per port = -alpha beta = 1'] = (-Q(alpha) * Q(beta) == 1)
    return out


def wgt(r): return (decimal.Decimal(r).ln() * (1 - KAPPA)).exp()
def bill(c): return sum(decimal.Decimal(n) * wgt(r) for r, n in c.items())


# ----------------------------------------------------------------------------------- caller block
def mmul(A, B): return [[sum(A[i][k] * B[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
def minv(A):
    d = A[0][0] * A[1][1] - A[0][1] * A[1][0]; return [[A[1][1] / d, -A[0][1] / d], [-A[1][0] / d, A[0][0] / d]]


def caller(al, be):
    al, be = Q(al), Q(be); t = al * be
    W2 = [[Q(1), -2 * al], [-2 * be, 1 + 4 * t]]
    gp = [[1 + t, be], [al, Q(1)]]; gm = [[1 + t, -be], [-al, Q(1)]]
    A = mmul(gm, minv(gp)); res = dict(t=t, A=A, W=W2)
    vals = [Q(s * 2 ** e) if e >= 0 else Q(s, 2 ** -e) for e in range(-6, 7) for s in (1, -1, 3, -3)] + [Q(0)]
    sol = None
    for p, q in itertools.product(vals, vals):
        r = (p * A[0][0] + q * A[1][0] - W2[0][0] * p) / W2[0][1]; s = (p * A[0][1] + q * A[1][1] - W2[0][0] * q) / W2[0][1]
        d = p * s - q * r
        if d == 0 or not isunit(d) or not all(isdy(x) or x == 0 for x in (p, q, r, s)): continue
        O = [[p, q], [r, s]]
        if mmul(O, A) == mmul(W2, O): sol = O; break
    res['O'] = sol
    if sol:
        OR = minv(mmul(sol, gp))
        res['plus1'] = mmul(mmul(sol, gp), OR) == [[1, 0], [0, 1]]
        res['minus1'] = mmul(mmul(sol, gm), OR) == W2
        res['dyadic'] = all(isdy(x) or x == 0 for r in sol + OR for x in r)
    return res


# ----------------------------------------------------------------------------------- mutants
def mutants(w, prog, ports, m, starts):
    v = w['v']; s0 = starts[m]; xa, xb = prog[s0 + 1][2], prog[s0 + 3][2]; ya, yb = xa + v, xb + v
    sub = lambda i, ev: (lambda p: (p.__setitem__(i, ev), p)[1])(list(prog))
    E = lambda k: prog[s0 + k]
    qa, qb = ports[xa], ports[xb]
    Lab = span([qa, qb]); Lb = span([qb]); gi = [i for i, e in enumerate(prog) if e[0] == 'ADD' and e[1] == xa and e[2] == xb][0]
    yield 'coef: C1 -= Xb sign flipped', sub(s0 + 8, ('ADD', E(8)[1], E(8)[2], Q(1)))
    yield 'coef: Xb += C1 coefficient 2', sub(s0 + 9, ('ADD', E(9)[1], E(9)[2], Q(2)))
    yield 'coef: Xa += dl Yb with dl halved', sub(s0 + 15, ('ADD', E(15)[1], E(15)[2], E(15)[3] / 2))
    yield 'coef: Yb += gam Xa with gam negated', sub(s0 + 16, ('ADD', E(16)[1], E(16)[2], -E(16)[3]))
    yield 'coef: Yb += gam Xa with gam times 3', sub(s0 + 16, ('ADD', E(16)[1], E(16)[2], 3 * E(16)[3]))
    yield 'coef: Yb += gam Xa with gam / 3 (non-dyadic)', sub(s0 + 16, ('ADD', E(16)[1], E(16)[2], E(16)[3] / 3))
    yield 'coef: Xb += dl Ya coefficient zero', sub(s0 + 18, ('ADD', E(18)[1], E(18)[2], Q(0)))
    yield 'coef: C2 -= Xa sign flipped', sub(s0 + 11, ('ADD', E(11)[1], E(11)[2], Q(1)))
    yield 'frame: Yb window moved to <qb>', sub(s0 + 14, ('MOVE', yb, Lb))
    yield 'frame: C1 skips UP', [e for i, e in enumerate(prog) if i != s0 + 4]
    yield 'frame: C2 DOWN target Lb instead of La', sub(s0 + 7, ('MOVE', E(7)[1], Lb))
    yield 'frame: C1 UP to <qa, qc> for foreign c', sub(s0 + 4, ('MOVE', E(4)[1], span([qa, ports[(xa + 7) % v]])))
    yield 'frame: C1 INIT at Z instead of <qa>', sub(s0, ('INIT', E(0)[1], frozenset({0})))
    yield 'frame: Ya window at a dot-1 line', sub(s0 + 17, ('MOVE', ya, span([next(q for q in ports if dot(q, qa) and q != qa)])))
    ff = [i for i, e in enumerate(prog) if e[0] == 'MOVE' and e[1] == xa and len(e[2]) == 512][0]
    yield 'frame: final X_a stops at <qa, qb>', sub(ff, ('MOVE', xa, Lab))
    p = list(prog); p[s0 + 8], p[s0 + 9] = p[s0 + 9], p[s0 + 8]; yield 'order: swap C1 -= Xb and Xb += C1', p
    p = list(prog); p[s0 + 15], p[s0 + 16] = p[s0 + 16], p[s0 + 15]; yield 'order: swap the two bounce ADDs', p
    p = list(prog); p[s0 + 10], p[s0 + 9] = p[s0 + 9], p[s0 + 10]; yield 'order: CLEAR C1 before Xb += C1', p
    p = list(prog); blk = p[s0 + 14:s0 + 20]; del p[s0 + 14:s0 + 20]; p[s0:s0] = blk; yield 'order: bounce block before the exchange', p
    p = list(prog); blk = p[s0 + 11:s0 + 14]; del p[s0 + 11:s0 + 14]; p[s0 + 8:s0 + 8] = blk; yield 'order: C2 exchange before C1 exchange (equivalent)', p
    p = list(prog); ev = p.pop(gi); p.insert(s0 + 14, ev); yield 'order: V-gate ADD hoisted before bounce', p
    p = list(prog); del p[gi + 3]; yield 'drop: V-gate SCALE(-1)', p
    p = list(prog); p[gi + 3] = ('SCALE', xb, Q(2)); yield 'coef: V-gate SCALE -1 -> 2', p
    p = list(prog); p[gi + 3] = ('SCALE', xb, Q(1)); yield 'coef: V-gate SCALE -1 -> 1', p
    p = list(prog); p[gi] = ('ADD', xa, xb, Q(-1)); yield 'coef: V-gate first ADD sign flipped', p
    yield 'drop: CLEAR C1', [e for i, e in enumerate(prog) if i != s0 + 10]
    yield 'drop: INIT C2', [e for i, e in enumerate(prog) if i != s0 + 2]
    yield 'drop: owned DOWN of C1', [e for i, e in enumerate(prog) if i != s0 + 5]
    p = list(prog); p.insert(s0 + 16, prog[s0 + 15]); yield 'dup: repeat Xa += dl Yb', p
    yield 'drop: Xa += dl Yb', [e for i, e in enumerate(prog) if i != s0 + 15]
    yield 'drop: last event', list(prog[:-1])
    xc = (xa + 13) % v
    if xc not in (xa, xb): yield 'partner: C1 -= X_c (foreign register)', sub(s0 + 8, ('ADD', E(8)[1], xc, Q(-1)))


def main():
    ports = [int(l) for l in open(os.path.join(DATA, 'ports104.txt')).read().split()]
    assert len(ports) == 104 == len(set(ports)) and all(0 < q < 512 for q in ports)
    path = os.path.join(DATA, 'window_native.json.gz')
    raw = open(path, 'rb').read()
    obj = json.loads(gzip.decompress(raw))
    w, oports = from_obj(obj); assert oports == ports
    alpha, beta, prog = w['alpha'], w['beta'], w['prog']
    print('object', hashlib.sha256(raw).hexdigest()[:16], 'events', len(prog), 'ports', len(ports), 'alpha', alpha, 'beta', beta)
    # regenerate
    g = build(ports, 9, alpha, beta)
    assert to_obj(g, ports) == obj, 'the shipped object differs from the generator output'
    print('PASS regenerated word equals the shipped object')
    # SPEC mains
    full = frozenset(range(512)); v = 104
    assert all(w['init'][p] == span([ports[p]]) and w['final'][p] == full for p in range(v))
    assert all(w['init'][v + p] == frozenset({0}) and w['final'][v + p] == perp(ports[p], 9) and dim(w['final'][v + p]) == 8 for p in range(v))
    print('PASS mains: X from <q> to the 9-dim space, Y from {0} to q-perp (dim 8)')
    A = engineA(w, prog, alpha, beta)
    assert not A['viol'] and A['bad'] == 0, (A['viol'][:3], A['bad'])
    assert dict(A['pub']) == {1: 104, 7: 104, 8: 104} and dict(A['own']) == {1: 208} and dict(A['ups']) == {1: 104} and dict(A['downs']) == {1: 104}
    assert A['peak'] == 2 and A['life'] == 104
    print('PASS A exact Fractions: 0 violations, 0 bad rows; public paid', dict(sorted(A['pub'].items())), 'owned UP', dict(A['ups']), 'DOWN', dict(A['downs']),
          'peak owned', A['peak'], 'lifetimes', A['life'], 'dirty clears', A['dirty'])
    assert engineB(w, prog, alpha, beta) == 0
    print('PASS B mod 2^61-1, 4 random inputs: 0 bad entries')
    S = structure(w, A['rows'], alpha, beta)
    assert all(S.values()), S
    for k in S: print('PASS structure:', k)
    # price and budget (ledger constants quoted)
    pb, ob = bill(A['pub']), bill(A['own'])
    fl = 208 * wgt(8)
    assert abs(pb - decimal.Decimal('1652.6284887')) < decimal.Decimal('1e-6') and ob == 208 and abs(fl - decimal.Decimal('1651.4970321')) < decimal.Decimal('1e-6')
    print('PASS price: public %s owned %s floor %s gap %s' % (str(pb)[:10], ob, str(fl)[:10], str(pb - fl)[:7]))
    pub_mm, own_mm = decimal.Decimal('1702.405'), decimal.Decimal('111.573067')
    dpub = pb - pub_mm
    for nm, T in (('outer w=1', decimal.Decimal('11.4263770958522')), ('rho=1', decimal.Decimal('14.513107'))):
        mx = own_mm + T - dpub
        print('budget %s: dpub %s, owned max %s (%s per port), owned 208 over by %s' % (nm, str(dpub)[:8], str(mx)[:8], str(mx / 104)[:6], str(ob - mx)[:6]))
        assert ob > mx
    assert abs((own_mm + decimal.Decimal('11.4263770958522') - dpub) - decimal.Decimal('172.776')) < decimal.Decimal('0.001')
    assert abs((own_mm + decimal.Decimal('14.513107') - dpub) - decimal.Decimal('175.863')) < decimal.Decimal('0.001')
    print('PASS budget lines 172.776 / 175.863; the word is over by 35.224 / 32.137')
    # caller block
    for ab in ((-2, Q(1, 2)), (-1, 1)):
        c = caller(*ab); assert c['O'] and c['plus1'] and c['minus1'] and c['dyadic'] and c['t'] == -1
    print('PASS caller block: a dyadic conjugator exists for (alpha, beta) = (-2, 1/2) and (-1, 1)')
    # the other (alpha, beta): same events, other coefficients, same checks
    w2 = build(ports, 9, Q(-1), Q(1)); A2 = engineA(w2, w2['prog'], Q(-1), Q(1))
    assert not A2['viol'] and A2['bad'] == 0 and dict(A2['own']) == {1: 208} and engineB(w2, w2['prog'], Q(-1), Q(1)) == 0
    print('PASS (alpha, beta) = (-1, 1) word: same checks, 0 bad rows')
    # mutants
    starts = [i for i, e in enumerate(prog) if e[0] == 'INIT' and e[1] == 2 * v]
    assert len(starts) == 52 and starts[1] - starts[0] == 20
    total = rej = 0; acc = []
    for m in (0, 25, 51):
        for name, pg in mutants(w, prog, ports, m, starts):
            a = engineA(w, pg, alpha, beta); b = engineB(w, pg, alpha, beta)
            r = bool(a['viol']) or a['bad'] > 0 or b > 0
            total += 1; rej += r
            if not r: acc.append((m, name))
    for ab in ((Q(-1), Q(1)), (Q(-2), Q(1)), (Q(2), Q(1, 2)), (Q(-2), Q(1, 4))):
        a = engineA(w, prog, *ab); b = engineB(w, prog, *ab)
        total += 1; rej += bool(a['viol']) or a['bad'] > 0 or b > 0
    print('mutants %d, rejected %d, accepted %d' % (total, rej, total - rej), sorted({n for _, n in acc}))
    assert total == 100 and rej == 97 and sorted({n for _, n in acc}) == ['order: C2 exchange before C1 exchange (equivalent)']
    print('PASS the only mutant accepted is the true equivalence (independent owned registers), at each of three pairs')
    print('PASS_WINDOW_NATIVE')


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--emit':
        ports = [int(l) for l in open(os.path.join(DATA, 'ports104.txt')).read().split()]
        g = build(ports, 9, Q(-2), Q(1, 2))
        with gzip.GzipFile(sys.argv[2], 'wb', mtime=0) as f:
            f.write(json.dumps(to_obj(g, ports), sort_keys=True, separators=(',', ':')).encode())
        print('wrote', sys.argv[2])
    else:
        main()
