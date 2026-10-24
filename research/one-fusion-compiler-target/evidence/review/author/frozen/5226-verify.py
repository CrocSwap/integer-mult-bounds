#!/usr/bin/env python3
"""Rebuild the fragmentation loss Lambda of the public #4610 word and the exact ship threshold.

Python standard library only (decimal, 60 digits); about 6 s.  Reads the public #4610 package
(Cao Yifan / intqwq), nothing else:
  research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz
  research/kappa-round3-warp-20261022/ARITHMETIC.json
  research/kappa-round3-warp-lean-20261022/NumericalMoments.lean

Usage:  python3 -B verify.py [PKG_ROOT] [BAR]
  PKG_ROOT  directory that contains research/kappa-round3-warp-20261022 (default: searched upward
            from this file, then $INTMULT_PKG).
  BAR       internal bar, default 0.0030233; t* = 1 - BAR.
Exit status 0 iff every assertion passes.  Output lines are numbered [k]; PROOF.md cites them.
"""
import sys, os, json, gzip, re, collections
from decimal import Decimal as D, getcontext
getcontext().prec = 60

def find_pkg():
    if len(sys.argv) > 1: return sys.argv[1]
    if os.environ.get('INTMULT_PKG'): return os.environ['INTMULT_PKG']
    here = os.path.dirname(os.path.abspath(__file__))
    p = here
    for _ in range(6):
        for cand in (p, os.path.join(p, 'wt')):
            if os.path.isdir(os.path.join(cand, 'research', 'kappa-round3-warp-20261022')): return cand
        p = os.path.dirname(p)
    sys.exit('cannot find the #4610 package; pass PKG_ROOT')
PKG = find_pkg()
BAR = D(sys.argv[2]) if len(sys.argv) > 2 else D('0.0030233')
TS = 1 - BAR
W3 = PKG + '/research/kappa-round3-warp-20261022/'
LN = PKG + '/research/kappa-round3-warp-lean-20261022/NumericalMoments.lean'
v, d = 112, 8

def pw(x, t):
    x = D(x)
    return D(0) if x == 0 else (t * x.ln()).exp()
def mom(Dct, t): return sum(D(n) * pw(r, t) for r, n in Dct.items())
def fmt(x, k=10): return f'{x:.{k}f}'
def near(x, ref, tol='1e-9'): return abs(D(x) - D(ref)) < D(tol)
default_bar = (BAR == D('0.0030233'))

# [1] public profiles and the controller family
A = json.load(open(W3 + 'ARITHMETIC.json'))
H = {int(k): n for k, n in A['local_helpers'].items()}
N = {int(k): n for k, n in A['local_paid'].items()}
lean = open(LN).read()
def lean_poly(name):
    body = re.search(r'def ' + name + r' \(t : ℝ\) : ℝ :=(.*?)\n\n', lean, re.S).group(1)
    return {int(r): int(n) for n, r in re.findall(r'(\d+) \* \((\d+) : ℝ\) \^ t', body)}
T_pub, P_pub = lean_poly('targetMoment'), lean_poly('paidMoment')

def inv(p, a, H, N, ports=v, block=d):
    T = collections.Counter({r: (p + 2) * n for r, n in H.items()})
    P = collections.Counter({r: (p + 2) * n for r, n in N.items()})
    P[1] += ports * (p - 1); T[1 + block * (p + 2)] += 2 * ports
    for L in (a, p - 1 - a):
        for j in range(1, L + 1):
            T[1 + block * (j + 1)] += 2 * ports; P[block * (j + 1)] += 2 * ports
    return dict(T), dict(P)
T16, P16 = inv(16, 7, H, N)
assert T16 == T_pub and P16 == P_pub, 'controller formula does not match the public invoice'
print('[1] kap-family formula at p16 a7 reproduces the public Lean invoice exactly:',
      len(T_pub), 'target and', len(P_pub), 'paid coefficients')

# [2] per-field climbs from the public word, both orientations
w = json.loads(gzip.decompress(open(W3 + 'ACTUAL-WORD.json.gz', 'rb').read()))
c = w['canonical']; fr = c['frames']; nf = len(c['start'])
R = [len(fr[c['final'][f]]) - len(fr[c['start'][f]]) for f in range(nf)]
res = {}
for orient in ('forward', 'backward'):
    jobs = collections.defaultdict(list); cur = list(c['start']); ncen = 0
    for e in w['programs'][orient]:
        if e[0] == 'climb':
            f, a_, b_, r = e[2], e[3], e[4], e[5]
            assert cur[f] == a_ and r == len(fr[b_]) - len(fr[a_]) and r > 0, e   # H1/H2: nested ascending climb
            jobs[f].append(r); cur[f] = b_
        elif e[0] == 'warp':
            f, a_, b_ = e[1][1], e[3], e[4]
            assert cur[f] == a_ and len(fr[a_]) == len(fr[b_]), e                 # H1: warps preserve dimension
            cur[f] = b_
        elif e[0] == 'center':
            ncen += 1
    assert cur == list(c['final'])
    assert all(sum(jobs[f]) == R[f] for f in range(nf))                          # telescoping
    prof = collections.Counter(r for f in range(nf) for r in jobs[f]); prof[8] += 8
    assert dict(prof) == N, (orient, dict(prof), N)
    res[orient] = jobs
    print(f'[2] {orient}: {nf} fields replay start->final; all climbs nested, rank = dim gap; sum climbs = R_f on all fields; '
          f'climb profile + 8 centre jobs = ARITHMETIC local_paid; centre events {ncen}')
nh = sum(H.values()); nm = nf - nh
assert all(R[f] == d for f in range(nm)) and collections.Counter(R[nm:]) == collections.Counter(H)
print(f'[3] mains: {nm} fields with R_f = {d}; helpers: {nh} fields with R_f census = local_helpers {H}')

def Lam(jobs, t, fields):
    return sum(sum(pw(x, t) for x in jobs[f]) - pw(R[f], t) for f in fields)
lams = {}
for orient in ('forward', 'backward'):
    jobs = res[orient]
    Lh, Lm = Lam(jobs, TS, range(nm, nf)), Lam(jobs, TS, range(nm))
    lams[orient] = Lh + Lm
    print(f'[4] {orient}: Lambda(t*) = {fmt(Lh + Lm)}  (helpers {fmt(Lh)}, mains {fmt(Lm)})')
assert lams['forward'] == lams['backward']
jobs = res['forward']; L = lams['forward']

# [5] Theorem B identity
phi = mom(H, TS) - mom(N, TS)
centre = 8 * pw(8, TS)
resid = phi + 2 * v * pw(d, TS) + centre + L
print(f'[5] phi(t*) = {fmt(phi)};  -2v d^t* - 8*8^t* - Lambda = {fmt(-2*v*pw(d, TS) - centre - L)};  residual {resid:.2E}')
assert abs(resid) < D('1e-50')

# [6] ship threshold
Gam = lambda p, a, t: (lambda TP: mom(TP[0], t) - mom(TP[1], t))(inv(p, a, {}, {}))
G16 = Gam(16, 7, TS); phistar16 = -G16 / 18
Lstar = -phistar16 - (2 * v + 8) * pw(d, TS)
f_ts = mom(T_pub, TS) - mom(P_pub, TS)
print(f'[6] p16 a7: phi* = -Gamma(t*)/18 = {fmt(phistar16)};  Lambda* = -phi* - 232*8^t* = {fmt(Lstar)}')
print(f'    Lambda(#4610) - Lambda* = {fmt(L - Lstar)} per call;  18*(Lambda*-Lambda) = {fmt(18*(Lstar - L))};  public invoice f(t*) = {fmt(f_ts)}')
assert abs(18 * (Lstar - L) - f_ts) < D('1e-40')

# [7] Corollary A1: p16 is the best controller of the kap family at t*
best = max((Gam(p, a, TS) / (p + 2), p, a) for p in range(3, 61) for a in range(p))
okA1 = best[1] == 16 and best[2] in (7, 8) and abs(best[0] + phistar16) < D('1e-45')
print(f'[7] max over kap family p=3..60, all a: Gamma/(p+2) best at p={best[1]} a={best[2]} (phi* = {fmt(-best[0])}); '
      f'p16 a7 is the max (a and p-1-a give the same invoice): {okA1}')
assert okA1
# [7b] the rest of the family: exact max for p = 1..PMAX via prefix sums, and for p > PMAX the bound
# Gamma/(p+2) <= F(PMAX+1) + 2v*delta_1 - v, with F(p) = 2v(1+8(p+2))^t/(p+2) decreasing in p and
# delta_j = (1+8(j+1))^t - (8(j+1))^t <= delta_1 (Lemma 3), each bracket term 2v*delta_j - v > 0.
PMAX = 400
dl = [D(0)] + [pw(1 + d * (j + 1), TS) - pw(d * (j + 1), TS) for j in range(1, PMAX + 1)]
S = [D(0)]
for j in range(1, PMAX + 1): S.append(S[-1] + dl[j])
Fp = lambda p: 2 * v * pw(1 + d * (p + 2), TS) / (p + 2)
best_all = max((F + (2 * v * (S[a] + S[p - 1 - a]) - v * (p - 1)) / (p + 2), p, a)
               for p, F in ((p, Fp(p)) for p in range(1, PMAX + 1)) for a in range(p))
tail = Fp(PMAX + 1) + 2 * v * dl[1] - v
okA1b = best_all[1] == 16 and abs(best_all[0] + phistar16) < D('1e-45') and tail < -phistar16 and all(2 * v * x > v for x in dl[1:])
print(f'[7b] exact max over p=1..{PMAX}: p={best_all[1]} a={best_all[2]}; tail bound for p>{PMAX}: {fmt(tail, 4)} < {fmt(-phistar16, 4)}: {okA1b}')
assert okA1b

# [8] root of the public invoice
def froot(T, P):
    lo, hi = D('1e-6'), D('0.05')
    for _ in range(140):
        m = (lo + hi) / 2
        if mom(T, 1 - m) - mom(P, 1 - m) > 0: lo = m
        else: hi = m
    return lo
kap = froot(T_pub, P_pub)
print(f'[8] public invoice root kappa = {kap:.13f} (package: in (0.0030217758, 0.0030217759))')
assert D('0.0030217758') < kap < D('0.0030217759')
print('SHIP TEST: a word in this family clears the bar iff Lambda(t*) <=', fmt(Lstar, 7), '; #4610 has', fmt(L, 7))

# [9] descent price (Theorem D), merge values
price = lambda r: pw(r, TS) + pw(9 + r, TS) - pw(9, TS)
n_desc = int(Lstar / price(1))
print('[9] descent price lower bound r^t+(9+r)^t-9^t:', ', '.join(f'r={r}: {fmt(price(r), 5)}' for r in (1, 2, 3, 4)),
      f'; max rank-1 descents with Lambda <= Lambda*: {n_desc}')
print('[10] merge values: 1+1->2', fmt(2 - pw(2, TS), 7), ' 4+4->3+5', fmt(2*pw(4, TS) - pw(3, TS) - pw(5, TS), 8),
      ' needed per call', fmt(L - Lstar, 7))

# [11] A30-CUT dual constants
Lf_max = max(sum(pw(x, TS) for x in jobs[f]) - pw(R[f], TS) for f in range(nf))
y = pw(8, TS) / 8
print('[11] A30 dual: y = 8^t/8 =', fmt(y, 6), ' 9^(t-1) =', fmt(pw(9, TS) / 9, 6), ' max_f Lambda_f =', fmt(Lf_max, 5))
assert y < 1 and pw(9, TS) / 9 >= D(25) / 27 and Lf_max < D('0.06')

# [12] consistency at #4610's own root: Lambda*(bar = kappa) equals Lambda(t0)
t0 = 1 - kap
Ls0 = -(-(Gam(16, 7, t0) / 18)) - (2 * v + 8) * pw(d, t0)
L0 = Lam(jobs, t0, range(nf))
print(f'[12] at its own root t0 = 1 - kappa: Lambda(t0) = {fmt(L0)}, Lambda*(bar=kappa) = {fmt(Ls0)}, difference {abs(L0 - Ls0):.2E}')
assert abs(L0 - Ls0) < D('1e-9')

# [13] budget arithmetic for the centre-free (coded) family: the centre is deleted, nothing else changes
f8 = pw(8, TS)
phi_coded = phi + 8 * f8
B = phi_coded - phistar16
print(f'[13] centre-free budget B = phi_coded - phi* = {fmt(B, 12)} per call = 8 f(8) - gap = {fmt(8*f8 - (L - Lstar), 12)}; 8 f(8) = {fmt(8*f8, 10)}')
print(f'     whole invoice 18B = {fmt(18*B, 8)};  144 f(8) = {fmt(144*f8, 8)};  shortfall 144 f(8) - 18B = {fmt(144*f8 - 18*B, 10)} = 18 x gap')
print(f'     per negative bank if the positive half is free: 18B/16 = {fmt(18*B/16, 10)};  53 debt classes x 8 f(8) = {fmt(53*8*f8, 2)};  '
      f'16 banks x 112 f(2) = {fmt(16*112*pw(2, TS), 1)}')
assert abs(B - (8 * f8 - (L - Lstar))) < D('1e-40')
assert 144 * f8 - 18 * B == 18 * (L - Lstar) or abs(144 * f8 - 18 * B - 18 * (L - Lstar)) < D('1e-40')
if default_bar:
    assert near(B, '63.577975271157', '1e-9') and near(Lstar, '23.8536932758', '1e-9') and near(L, '23.8746264727', '1e-9')
    assert near(L - Lstar, '0.0209331969', '1e-9') and n_desc == 11
    assert near(price(1), '1.99022', '1e-5') and near(price(2), '3.97594', '1e-5')
    assert near(53 * 8 * f8, '3370.74', '1e-2') and near(18 * B / 16, '71.5252221801', '1e-9')

# [14] Lean file hygiene (text-level only; the Lean build is separate, see README)
lp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lean', 'Skel.lean')
if os.path.exists(lp):
    src = open(lp, encoding='utf-8').read()
    code = re.sub(r'/-.*?-/', '', src, flags=re.S)
    decls = re.findall(r'^\s*(?:private\s+)?(?:theorem|lemma)\s+(\S+)', code, re.M)
    has_sorry = 'sorry' in code
    has_axiom = bool(re.search(r'^\s*axiom\b', code, re.M))
    print(f'[14] lean/Skel.lean: {len(decls)} theorem/lemma declarations; "sorry" present: {has_sorry}; "axiom" present: {has_axiom}')
    assert 'sorry' not in code
print('ALL CHECKS PASSED')
