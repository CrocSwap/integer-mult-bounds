#!/usr/bin/env python3
"""Exact physical local pair for the coded reverse controller.

The #4940 scalar A^-1 thin source fails against #4933's physical owner code C.
This verifier exhibits a changed thin source and x-boundary that make the pair
equal the standard pair exactly, with the physical C.

  S = Q D C^-1 Q^-1 D^-1      (thin source)
  R = Q C Q^-1                (input x boundary)
  L = D Q C^-1 Q^-1 D^-1      (output x boundary)

It also reproduces the #4940 coded-controller invoice roots (p=8/19) and the
outer bit cap 0.0034.  The full controller replay and the field-map tariff are
not run here.
"""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json, random, sys, importlib.util
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P, IMAG, OWNERS, SIZE = 65537, 256, 112, 512

def need(ok, why):
    if not ok: raise ValueError(why)

def parity(x): return x.bit_count() & 1
def mv(rows, x): return sum(parity(row & x) << bit for bit, row in enumerate(rows))
def transpose(rows):
    return [sum(((row >> bit) & 1) << j for j, row in enumerate(rows)) for bit in range(9)]
def signed_map(record, x, inverse=False, unsigned=False):
    rows, mask = record["G_rows"], record["Z_mask"]
    y = mv(transpose(rows) if inverse else rows, x)
    sign = 1 if unsigned else 1 - 2*parity(mask & (x if inverse else y))
    return y, sign
def empty(): return [[0]*SIZE for _ in range(OWNERS)]
def add(x, y, sign=1):
    return [[(a+sign*b) % P for a, b in zip(xi, yi)] for xi, yi in zip(x, y)]
def gaussian(bank, axes, inverse=False):
    a = (1+(-IMAG if inverse else IMAG))*pow(2, -1, P) % P
    b = (1-(-IMAG if inverse else IMAG))*pow(2, -1, P) % P
    out = [row[:] for row in bank]
    for bit in axes:
        step = 1 << bit
        for row in out:
            for start in range(0, SIZE, 2*step):
                for x in range(start, start+step):
                    u, v = row[x], row[x+step]
                    row[x] = (a*u+b*v) % P
                    row[x+step] = (b*u+a*v) % P
    return out
def scalar_code(bank, modes, inverse=False):
    temp = [[sum(sign*bank[i][x] for i, sign in contacts) % P for x in range(SIZE)] for contacts in modes]
    den = pow(52 if inverse else 4, -1, P)
    out = [row[:] for row in bank]
    for mode, contacts in enumerate(modes):
        for i, sign in contacts:
            out[i] = [(a-sign*den*b) % P for a, b in zip(out[i], temp[mode])]
    return out
def physical_code(bank, records, modes):
    mixed = empty()
    for i, row in enumerate(bank):
        for x, value in enumerate(row):
            if value:
                y, sign = signed_map(records[i], x)
                mixed[i][y] = sign*value % P
    mixed = scalar_code(mixed, modes)
    out = empty()
    for i, row in enumerate(mixed):
        for x, value in enumerate(row):
            if value:
                y, sign = signed_map(records[i], x, inverse=True)
                out[i][y] = sign*value % P
    return out
def physical_code_inv(bank, records, modes):
    mixed = empty()
    for i, row in enumerate(bank):
        for x, value in enumerate(row):
            if value:
                y, sign = signed_map(records[i], x)
                mixed[i][y] = sign*value % P
    mixed = scalar_code(mixed, modes, inverse=True)
    out = empty()
    for i, row in enumerate(mixed):
        for x, value in enumerate(row):
            if value:
                y, sign = signed_map(records[i], x, inverse=True)
                out[i][y] = sign*value % P
    return out
def diff(a, b):
    return sum(1 for i in range(OWNERS) for j in range(SIZE) if a[i][j] != b[i][j])

def main():
    src = ROOT/'research/coded-native-caller'
    receipt = json.loads((src/'NORMALIZERS.json').read_text())
    records = receipt['ports']; columns = receipt['mode_columns']
    modes = [[(i, s) for i, s in enumerate(col) if s] for col in columns]
    CODE = json.loads((src/'CODE.json').read_text())
    A = [[F(v) for v in row] for row in CODE['A']]
    need(len(records) == len(A) == OWNERS, '112 owners')
    need(all(A[i][j] == F(i == j)-F(sum(c[i]*c[j] for c in columns), 4)
             for i in range(OWNERS) for j in range(OWNERS)), 'A = I - R^T R/4')
    def C(x): return physical_code(x, records, modes)
    def Ci(x): return physical_code_inv(x, records, modes)
    def Q(x, inv=False): return gaussian(x, [0], inverse=inv)
    def D(x, inv=False): return gaussian(x, range(1, 9), inverse=inv)
    def S(x): return Q(D(Ci(Q(D(x, True), True))))
    def R(x): return Q(C(Q(x, True)))
    def L(x): return D(Q(Ci(Q(D(x, True), True))))
    def pair(x, y):
        x1 = add(D(R(x)), D(Q(C(y))), -1)
        y1 = add(D(y), Q(S(x1), True))
        return L(x1), y1
    def std(x, y):
        return add(D(x), D(Q(y)), -1), D(Q(x, True))
    # exact C inverse control
    rng = random.Random(23)
    def rb(n=40):
        b = empty()
        for _ in range(n): b[rng.randrange(OWNERS)][rng.randrange(SIZE)] = rng.randrange(1, P)
        return b
    for _ in range(2):
        z = rb(); need(diff(Ci(C(z)), z) == 0 and diff(C(Ci(z)), z) == 0, 'C inverse')
    # witness and random local identity
    w = empty(); w[1][1] = 1
    for tag, x, y in [('witness', empty(), w)] + [('random', rb(), rb()) for _ in range(3)]:
        xo, yo = pair(x, y); xs, ys = std(x, y)
        need(diff(xo, xs) == 0 and diff(yo, ys) == 0, 'S/L/R local pair exact ('+tag+')')
    # control: literal #5036 A^-1 thin and A/A^-1 boundary leaves the y block
    w = empty(); w[1][1] = 1
    x1 = add(D(empty()), D(Q(C(w))), -1)
    y1 = add(D(w), Q(scalar_code(x1, modes, inverse=True), True))
    xs, ys = std(empty(), w)
    need(diff(y1, ys) != 0, 'literal A^-1 thin fails (expected)')
    # control: C^-1 thin without the changed boundary leaves the x block
    x1 = add(D(empty()), D(Q(C(w))), -1)
    y1 = add(D(w), Q(Ci(x1), True))
    xs, ys = std(empty(), w)
    need(diff(x1, xs) != 0 or diff(y1, ys) != 0, 'C^-1 thin without R/L fails (expected)')
    # control: wrong left boundary
    x1 = add(D(empty()), D(Q(C(w))), -1)
    y1 = add(D(w), Q(S(x1), True))
    xs, ys = std(empty(), w)
    need(diff(x1, xs) != 0 or diff(y1, ys) != 0, 'identity output boundary fails (expected)')
    # ---- invoice model from #4940 ----
    H = {4: 28, 7: 7, 8: 47, 9: 326}
    P_NEW = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40}
    P_OLD = {1: 2237, 2: 388, 3: 494, 4: 147, 5: 36, 8: 8}
    from collections import Counter
    def invoice(p, pat, thick, prof):
        full = frozenset(range(2*p+1)); T, Dct = Counter(), Counter()
        outs = [full, full]
        for i, ch in enumerate(pat, 1):
            outs += [frozenset(range(0, 2*i+1)) if ch == 'I' else frozenset(range(2*i, 2*p+1))]*2
        for s in outs: T[1+8*len(s & thick)] += 112
        for i, ch in enumerate(pat, 1):
            if ch == 'I': Dct[8*len(frozenset(range(0, 2*i)) & thick)] += 224
            else: Dct[8*len(frozenset(range(2*i+1, 2*p+1)) & thick)] += 224
        for j in range(1, p): Dct[8*len(frozenset([2*j]) & thick)] += 224
        for r, n in H.items(): T[r] += len(thick)*n
        for r, n in prof.items(): Dct[r] += len(thick)*n
        Dct[1] += 112*(2*p+1-len(thick)); T.pop(0, None); Dct.pop(0, None)
        return T, Dct
    def root(T, Dct):
        f = lambda cc: sum(n*r**(1-cc) for r, n in T.items())-sum(n*r**(1-cc) for r, n in Dct.items())
        lo, hi = 0.0, 0.05
        for _ in range(200):
            mid = (lo+hi)/2
            if f(mid) > 0: lo = mid
            else: hi = mid
        return lo
    pub = root(*invoice(16, 'I'*7+'T'*8, frozenset({0, 32} | set(range(1, 32, 2))), P_OLD))
    need(abs(pub-0.0030201659770) < 1e-12, 'published p16 root reproduced')
    res = {p: root(*invoice(p, 'I'*((p-1)//2)+'T'*(p-1-(p-1)//2), frozenset(range(1, 2*p, 2)), P_NEW)) for p in (8, 19)}
    need(res[19] > 0.0034*1.5 and res[8] > 0.0034*1.5, 'coded raw roots clear the bit cap')


    # ---- exact algebra and an independent NumPy implementation ----
    def mm(X, Y):
        n = len(X); out = [[F(0)]*n for _ in range(n)]
        for i in range(n):
            for k in range(n):
                if X[i][k]:
                    for j in range(n):
                        if Y[k][j]: out[i][j] += X[i][k]*Y[k][j]
        return out
    Ainv = [[F(int(i == j))+(A[i][j]-F(int(i == j)))/13 for j in range(OWNERS)] for i in range(OWNERS)]
    need(mm(A, Ainv) == [[F(int(i == j)) for j in range(OWNERS)] for i in range(OWNERS)], 'A A^-1 = I exact')
    # Q and D inverses on the full 512-address basis
    for a in range(SIZE):
        e = empty(); e[0][a] = 1
        need(diff(Q(Q(e), True), e) == 0 and diff(D(D(e), True), e) == 0, 'Q/D inverses')
    # independent NumPy implementation of C, S, R, L and the pair
    import numpy as np
    inv2 = pow(2, -1, P)
    def modmat(X):
        return np.array([[int(X[i][j].numerator % P)*pow(int(X[i][j].denominator) % P, -1, P) % P for j in range(OWNERS)] for i in range(OWNERS)], dtype=np.int64)
    Am, Aim = modmat(A), modmat(Ainv)
    pf = np.zeros((OWNERS, SIZE), dtype=np.int64); sf = np.zeros((OWNERS, SIZE), dtype=np.int64)
    pi = np.zeros((OWNERS, SIZE), dtype=np.int64); si = np.zeros((OWNERS, SIZE), dtype=np.int64)
    for i, r in enumerate(records):
        for x in range(SIZE):
            y, s = signed_map(r, x); pf[i, x] = y; sf[i, x] = s
            y, s = signed_map(r, x, inverse=True); pi[i, x] = y; si[i, x] = s
    def Cnp(bank, inverse=False):
        tmp = np.zeros_like(bank)
        for i in range(OWNERS): tmp[i, pf[i]] = (sf[i]*bank[i]) % P
        mix = ((Aim if inverse else Am) @ tmp) % P
        out = np.zeros_like(bank)
        for i in range(OWNERS): out[i, pi[i]] = (si[i]*mix[i]) % P
        return out % P
    def gnp(bank, axes, inverse=False):
        a = (1+(-IMAG if inverse else IMAG))*inv2 % P; b = (1-(-IMAG if inverse else IMAG))*inv2 % P
        out = bank.copy()
        for bit in axes:
            step = 1 << bit
            for start in range(0, SIZE, 2*step):
                u = out[:, start:start+step].copy(); v = out[:, start+step:start+2*step].copy()
                out[:, start:start+step] = (a*u+b*v) % P; out[:, start+step:start+2*step] = (b*u+a*v) % P
        return out
    def Qn(x, inv=False): return gnp(x, [0], inv)
    def Dn(x, inv=False): return gnp(x, range(1, 9), inv)
    def Sn(x): return Qn(Dn(Cnp(Qn(Dn(x, True), True), True)))
    def Rn(x): return Qn(Cnp(Qn(x, True)))
    def Ln(x): return Dn(Qn(Cnp(Qn(Dn(x, True), True), True)))
    def pairn(x, y):
        x1 = (Dn(Rn(x))-Dn(Qn(Cnp(y)))) % P
        y1 = (Dn(y)+Qn(Sn(x1), True)) % P
        return Ln(x1), y1
    def stdn(x, y):
        return (Dn(x)-Dn(Qn(y))) % P, Dn(Qn(x, True)) % P
    def rb_np(n=40):
        z = np.zeros((OWNERS, SIZE), dtype=np.int64)
        for _ in range(n): z[rng.randrange(OWNERS), rng.randrange(SIZE)] = rng.randrange(1, P)
        return z
    wn = np.zeros((OWNERS, SIZE), dtype=np.int64); wn[1, 1] = 1
    for tag, x, y in [('witness', np.zeros_like(wn), wn)] + [('random', rb_np(), rb_np()) for _ in range(3)]:
        xo, yo = pairn(x, y); xs, ys = stdn(x, y)
        need(int((xo-xs).sum() % P) == 0 and int((yo-ys).sum() % P) == 0 and not (xo-xs).any() and not (yo-ys).any(), 'NumPy independent local pair exact ('+tag+')')
    need(not (Cnp(Cnp(wn), inverse=True)-wn).any(), 'NumPy independent C inverse witness')

    # p=19 tail guards at the outer bit cap 0.0034
    def guards(T, Dct, cc, u=0.2, cut=20, floor=21):
        t = 1-cc; Tt = sum(n*r**t for r, n in T.items()); Pt = sum(n*r**t for r, n in Dct.items())
        return Pt/Tt, sum(n*r**(t+u) for r, n in Dct.items())/(cut**u*Tt), floor*sum(T.values())/(cut**cc*Tt)
    a, g, d = guards(*invoice(19, 'I'*9+'T'*9, frozenset(range(1, 38, 2)), P_NEW), 0.0034)
    need(a < 1-1e-9 and g < 0.97 and d < 0.97, 'p=19 tail guards at 0.0034')
    # outer ledger: 0.0034 fails only the BIT cap; 0.0033999971 passes
    sys.path.insert(0, str(ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill'))
    spec = importlib.util.spec_from_file_location('ledger_mod', ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py')
    L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
    gap, atom = F(1, 1400000000), F(1, 250)
    def failing(kappa):
        prm = {'kappa': kappa, 'tested_saving': kappa+7*gap, 'complex_uniform_saving': kappa+6*gap, 'b': kappa+5*gap, 'a': kappa+4*gap,
               'q': kappa+3*gap, 'bit_saving': F(17, 5000), 'epsilon': 1-gap, 'beta': 1-3*gap, 'r0': gap/10, 'stop': gap, 'layout': gap, 'd': gap}
        out = L.ledger(prm); out['functional_checks']['actual_new_BIT_stock_sublinear'] = prm['beta']*(1-atom)
        return [k for part in ('strict_checks', 'functional_checks') for k, x in out[part].items() if x <= 0]
    need(failing(F(60403, 20000000)) == [], 'ledger passes at the selected kappa (control)')
    need(failing(F(3324, 1000000)) == [] and failing(F(33999, 10000000)) == [], 'ledger passes at 0.003324 and 0.0033999')
    need(failing(F(34, 10000)) == ['actual_bit_above_effective'], 'at 0.0034 only the BIT cap fails')
    print('PASS outer ledger: complex side clears 0.0034; BIT cap is the binding limit (+12.5%% over 0.00302015)')

    print('PASS physical S/L/R local pair exact; coded roots p=8 %.8f p=19 %.8f' % (res[8], res[19]))
    print(json.dumps({'status': 'PASS_CODED_REVERSE_PHYSICAL_LOCAL_FIX',
                      'local_pair': 'L*(T_B)*R == standard with C, S=Q D C^-1 Q^-1 D^-1, R=Q C Q^-1, L=D Q C^-1 Q^-1 D^-1',
                      'roots': {'p8': res[8], 'p19': res[19]},
                      'scope': 'exact local pair and invoice; full controller replay, field-map tariff, denominator 13 and compiler remain open'}, sort_keys=True))

if __name__ == '__main__':
    main()
