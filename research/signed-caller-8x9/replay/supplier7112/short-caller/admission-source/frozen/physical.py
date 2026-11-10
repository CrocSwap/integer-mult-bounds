#!/usr/bin/env python3
"""Physical stream replay of the literal hosted word, own driver (standard library).
python3 -I -B physical.py WORD.json.gz CLIFFORD_EXACT.py [prime=1000000009] [seed=11] [mutate]
Every register carries a 512-component stream over F_p[i] (p = 1 mod 4, i a fixed square root of -1); inputs are random.
A MOVE a->b applies chart(a)^dagger then chart(b) as explicit gates (P, X, D, C, phase read from the retained Clifford
circuits, interpreted here); INIT zeroes, CLEAR erases, SCALE/ADD act linearly.  Prediction comes from the charts alone:
  X_out = M(X_in; init->final) + alpha M(Y_in; Y0->Xfinal),  Y_out = beta M(X_in; init->Yfinal) + (1+t) M(Y_in; Y0->Yfinal),
helpers: M(in; init->final).  Then the raw main-pair identities by tableau and phase on all 104 ports, with controls."""
import sys, gzip, json, time, importlib.util, random
from fractions import Fraction as Fr
wordp, cliff = sys.argv[1], sys.argv[2]
p = int(sys.argv[3]) if len(sys.argv) > 3 else 1000000009
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 11
mutate = len(sys.argv) > 5
assert p % 4 == 1
spec = importlib.util.spec_from_file_location('cliff', cliff); C = importlib.util.module_from_spec(spec); sys.modules['cliff'] = C; spec.loader.exec_module(C)
def find_i():
    for g in range(2, 200):
        v = pow(g, (p - 1) // 4, p)
        if v * v % p == p - 1: return v
IM = find_i(); HALF = (p + 1) // 2; N = 512; IP = [1, IM, p - 1, (p - IM) % p]
W = json.load(gzip.open(wordp, 'rt')); fr = W['frames']; n = len(W['initial']); NO = W['owned_fields']; NR = n + NO; live = W['live']
Hh = W['hosted']; alpha = Fr(Hh['alpha']); beta = Fr(Hh['beta']); t = alpha * beta; a2f = Fr(Hh['alpha2']); b2f = Fr(Hh['beta2']); X2 = Hh['X2']; Y2 = Hh['Y2']
if mutate: a2f = -a2f        # control run: predictions use the wrong sign of alpha2; must be rejected
fm = lambda q: (lambda f: f.numerator % p * pow(f.denominator, p - 2, p) % p)(Fr(q))
charts = {}
def chart(i):
    if i not in charts: charts[i] = C.canonical_frame(9, tuple(fr[i]))
    return charts[i]
def gates(op):
    g = []
    for e in op.circuit:
        k = e[0]
        if k == 'P': g.append(('P', [C.mv(e[1], x) for x in range(N)]))
        elif k == 'X': g.append(('X', [x ^ e[1] for x in range(N)]))
        elif k == 'D': g.append(('M', [IP[C.qvalue(e[1], e[2], x, 9)] for x in range(N)]))
        elif k == 'phase': g.append(('S', IP[e[1] % 4]))
        elif k == 'C':
            q, s = e[1], e[2]
            g.append(('C', [x ^ q for x in range(N)], (1 + s * IM) * HALF % p, (1 - s * IM) * HALF % p))
        else: raise SystemExit('unknown gate ' + str(k))
    return g
def apply(g, v):
    for x in g:
        k = x[0]
        if k == 'P':
            o = [0] * N
            for i, j in enumerate(x[1]): o[j] = v[i]
            v = o
        elif k == 'X': v = [v[j] for j in x[1]]
        elif k == 'M': v = [a * b % p for a, b in zip(v, x[1])]
        elif k == 'S': v = [a * x[1] % p for a in v]
        else:
            c1, c2, idx = x[2], x[3], x[1]
            v = [(a * c1 + v[j] * c2) % p for a, j in zip(v, idx)]
    return v
cache = {}
def move(a, b, v):
    if (a, b) not in cache: cache[a, b] = gates(chart(a).adjoint().then(chart(b)))
    return apply(cache[a, b], v)
# control of the interpreter against the library's exact state vectors (basis 0 and 5)
def to_c(pair): return (pair[0] + pair[1] * IM) % p
for a, b in ((W['initial'][live[0]], W['final'][live[0]]), (W['initial'][live[0] + 112], W['final'][live[0] + 112])):
    op = chart(a).adjoint().then(chart(b)); g = gates(op)
    for basis in (0, 5):
        v = [0] * N; v[basis] = 1; out = apply(g, v)
        vec, den = op.zero_state(basis); scale = pow(2, p - 1 - den, p) if den else 1
        # zero_state returns the state scaled by 2^den
        exp = [to_c(x) * pow(pow(2, den, p), p - 2, p) % p for x in vec]
        assert out == exp, 'gate interpreter disagrees with the library state vector'
print('gate interpreter agrees with the library on 4 exact state vectors', flush=True)
rnd = random.Random(seed)
S = [[rnd.randrange(p) for _ in range(N)] if r < n else [0] * N for r in range(NR)]; inp = [s[:] for s in S[:n]]
t0 = time.time()
for e in W['program']:
    op, r = e[0], e[1]
    if op == 'MOVE': S[r] = move(e[2], e[3], S[r])
    elif op in ('INIT', 'CLEAR'): S[r] = [0] * N
    elif op == 'SCALE':
        c = fm(e[2]); S[r] = [a * c % p for a in S[r]]
    else:
        c = fm(e[3]); s = S[e[2]]; S[r] = [(a + c * b) % p for a, b in zip(S[r], s)]
print('replayed %d events, %d chart pairs, %.0fs' % (len(W['program']), len(cache), time.time() - t0), flush=True)
main = set(live) | {r + 112 for r in live} | set(X2) | set(Y2)
badH = sum(S[r] != move(W['initial'][r], W['final'][r], inp[r]) for r in range(n) if r not in main)
DPs = set(Hh['Dports']); al_h, be_h, de_h = fm(alpha), fm(beta), fm(1 + t); al_d, be_d, de_d = 0, 1, 1      # hosted ports (pair alpha, beta) and two-chain ports (X = x, Y = x + y)
badX = badY = 0
for pi_, r in enumerate(live):
    al, be, de = (al_d, be_d, de_d) if pi_ in DPs else (al_h, be_h, de_h)
    y = r + 112; li, fu, y0, yf = W['initial'][r], W['final'][r], W['initial'][y], W['final'][y]
    px = [(a + al * b) % p for a, b in zip(move(li, fu, inp[r]), move(y0, fu, inp[y]))]
    py = [(be * a + de * b) % p for a, b in zip(move(li, yf, inp[r]), move(y0, yf, inp[y]))]
    badX += S[r] != px; badY += S[y] != py
badX2 = badY2 = 0; al2, be2, de2 = fm(a2f), fm(b2f), fm(1 + a2f * b2f)
for x2, y2 in zip(X2, Y2):
    li, fu, y0, yf = W['initial'][x2], W['final'][x2], W['initial'][y2], W['final'][y2]
    px = [(a + al2 * b) % p for a, b in zip(move(li, fu, inp[x2]), move(y0, fu, inp[y2]))]
    py = [(be2 * a + de2 * b) % p for a, b in zip(move(li, yf, inp[x2]), move(y0, yf, inp[y2]))]
    badX2 += S[x2] != px; badY2 += S[y2] != py
print('prime %d seed %d: helper rows bad %d (of %d), X rows bad %d, Y rows bad %d, X2 rows bad %d, Y2 rows bad %d (of %d ports; %d with second mains)' % (p, seed, badH, n - len(main), badX, badY, badX2, badY2, len(live), len(X2)), flush=True)
if mutate: sys.exit(0 if (badX or badY or badX2 or badY2) else 1)
# raw main-pair identities, tableau + phase, all ports
def same(a, b): return a.tab == b.tab and all(a.zero_state(k) == b.zero_state(k) for k in (0, 1))
bad = [0] * 6
for r, q in zip(live, W['ports']):
    y = r + 112; P = chart(W['final'][y]); Vv = chart(W['final'][r]); Z0 = chart(W['initial'][y]); a0 = chart(W['initial'][r])
    Qp = C.cgate(9, q, 1); Qm = C.cgate(9, q, -1); F = C.fourier(9); D = Qm.then(F)
    mp = C.lower_child(P.adjoint().then(Qm.then(F)))[1]            # free adapter on the Y output chart
    ma = C.lower_child(Qp.adjoint().then(a0))[1]
    bad[0] += not same(Qp.adjoint().then(Vv), D)                   # X->X
    bad[1] += not same(Z0.adjoint().then(P).then(mp), D)           # Y->Y
    bad[2] += not same(Qp.adjoint().then(P).then(mp), Qm.then(D))  # X->Y = Q^-1 D
    bad[3] += not same(Z0.adjoint().then(Vv), Qp.then(D))          # Y->X = Q D
    bad[4] += same(Z0.adjoint().then(Vv), Qm.then(D))              # control: Q^-1 must not match
    bad[5] += same(Qp.adjoint().then(P).then(mp), Qp.then(D))      # control
print('tableau on %d ports: XX!=D %d YY!=D %d YX!=Q^-1D %d XY!=QD %d | controls matching (must be 0): %d %d' % ((len(live),) + tuple(bad)))
ok = badH == 0 and badX == 0 and badY == 0 and badX2 == 0 and badY2 == 0 and bad == [0] * 6
print('PASS_PHYSICAL' if ok else 'FAIL_PHYSICAL', '%.0fs' % (time.time() - t0))
sys.exit(0 if ok else 1)
