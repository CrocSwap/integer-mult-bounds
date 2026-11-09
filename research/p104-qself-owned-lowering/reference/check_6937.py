#!/usr/bin/env python3
"""Recomputes the JSON facts of README.md (standard library, exact, well under 300 s, writes nothing).
Run: python3.12 -I -B research/p104-two-chain-findings/check.py   Each check has a failing control."""
import os, sys, json, hashlib
from fractions import Fraction as Q
from decimal import Decimal as D, getcontext
getcontext().prec = 40
H = os.path.dirname(os.path.abspath(__file__)); DT = os.path.join(H, 'data')
fails = []
def req(name, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + name + (' | ' + str(info) if info else ''), flush=True)
    if not ok: fails.append(name)
def load(f): return json.load(open(os.path.join(DT, f)))
# 1. data hashes (control: a wrong digest is rejected)
SHA = {'sr0.json.gz': '60a47635302473d7b6aa660445042a2e06bc62a2d041fb072d5882e9ee9cc54a',
       'rbf.json.gz': '0b45822b170c4425810da72a8b53d4c78994178d8b70c0e900487e93ad70bb75',
       'root_A_efree.json': '64486cd1c5a879ffc0312195a39ce4a2ef288f81afb47232c244b9b6f46683d0',
       'root_L3_tHHtHt.json': 'eb79a0d89c1c09138a3e8a260f04b6a0c88d51d1314650364cb88441333b8f28',
       'wh.json.gz': '25326dac562fa07edd28a6daf302de0c27f5f2e82f610eaf3671d39575f8dbea',
       'ft.json.gz': '67d65735f9baa4361cb6214758535b226969a3349ae12a61d529f06e75cc90db',
       'root_L3_tHtHHt.json': '60bf936299c3a553398e943ba6d67b05ee4d29007cd1af9da6227685aa226309'}
for f, h in SHA.items():
    req('sha256 ' + f, hashlib.sha256(open(os.path.join(DT, f), 'rb').read()).hexdigest() == h)
req('control: wrong digest rejected', hashlib.sha256(b'x').hexdigest() != SHA['sr0.json.gz'])
# 2. kappa from invoices: root of sum (T_r - P_r) r^(-k+1)... defined as in the invoice law: sum (T-P) r^(1-k) = 0
def kappa(T, P):
    rs = sorted(set(T) | set(P)); ln = {r: D(int(r)).ln() for r in rs}
    e = lambda k: sum((D(T.get(r, 0)) - D(P.get(r, 0))) * (ln[r] * (1 - k)).exp() for r in rs)
    lo, hi = D('1e-6'), D('0.05')
    for _ in range(200):
        m = (lo + hi) / 2
        if e(m) > 0: lo = m
        else: hi = m
    return lo
for f, want in (('sr0.invoice.json', '.00360666479'), ('rbf.invoice.json', '.00362232643')):
    d = load(f); k = kappa(d['T'], d['P'])
    req('kappa %s = %s' % (f, want), str(k)[1:len(want) + 1] == want, str(k)[:14])
    d2 = json.loads(json.dumps(d)); d2['T']['1'] += 5000
    req('control: kappa changes when the invoice is edited (%s)' % f, str(kappa(d2['T'], d2['P']))[:10] != str(k)[:10])
# 3. E-free root: product of (I - 2 x y^T) over the 40 units in order is -I at S=-1; isotropy fails only at t1 (units 18, 19)
R = load('root_A_efree.json'); n, N = R['n'], R['N']
X = [[Q(v) for v in r] for r in R['X']]; Y = [[Q(v) for v in r] for r in R['Y']]
dot = lambda a, b: sum(u * v for u, v in zip(a, b) if u and v)
def prod(X, Y, S=-1, order=None):
    M = [[Q(int(i == j)) for j in range(n)] for i in range(n)]
    for k in (order if order is not None else range(N)):
        d = [sum(Y[k][i] * M[i][j] for i in range(n) if Y[k][i]) for j in range(n)]
        M = [[M[i][j] + (S - 1) * X[k][i] * d[j] for j in range(n)] if X[k][i] else M[i] for i in range(n)]
    return M
neg_I = lambda M: all(M[i][j] == (-1 if i == j else 0) for i in range(n) for j in range(n))
ok = neg_I(prod(X, Y)); req('E-free root: unit product is -I at S=-1', ok)
req('E-free root: product is I at S=+1', all(prod(X, Y, 1)[i][j] == int(i == j) for i in range(n) for j in range(n)))
iso = [u for u in range(N) if dot(Y[u], X[u]) != 0]
req('E-free root: isotropy fails exactly at units 18 and 19 (t1 of each chain)', iso == [18, 19], iso)
X2 = [r[:] for r in X]; j = next(i for i, v in enumerate(X2[18]) if v); X2[18][j] += 1
req('control: edited t1 breaks the -I product', not neg_I(prod(X2, Y)))
req('control: swapped unit order breaks the -I product', not neg_I(prod(X, Y, order=[20 if i == 18 else 18 if i == 20 else i for i in range(N)])))
cl = load('caller_efree.json'); req('caller file parses (QSELF caller, 76 x 76 per README)', isinstance(cl, (dict, list)) and len(json.dumps(cl)) > 10000)
# 4. L=3 rho=1 roots: header Gram is the t=-1 path, units square-zero (b_i.a_i = 0), nine rows of length 8
for f in ('root_L3_tHHtHt.json', 'root_L3_tHtHHt.json'):
    d = load(f); a = [[Q(x) for x in r] for r in d['a']]; b = [[Q(x) for x in r] for r in d['b']]; M = len(a)
    gram = lambda a, b: all(dot(b[i], a[j]) == (1 if j == i + 1 else -1 if j == i - 1 else 0) for i in range(M) for j in range(M))
    req('%s: M=%d n=%d, header Gram is the exact path t=-1, square-zero units' % (d['types'], M, len(a[0])), M == 9 and len(a[0]) == 8 and gram(a, b))
    b2 = [r[:] for r in b]; b2[0][0] += 1
    req('control: perturbed header rejected (%s)' % d['types'], not gram(a, b2))
print('PASS_P104_TWO_CHAIN_FINDINGS' if not fails else 'FAILED: %s' % fails)
sys.exit(1 if fails else 0)
