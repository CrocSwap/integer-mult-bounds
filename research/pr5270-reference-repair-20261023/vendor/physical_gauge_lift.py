#!/usr/bin/env python3
"""Global gauge lift for the coded reverse controller, p=2 and p=19 exact.

The recovered full_build.py compares two builds that draw independent random
initial roles, so its residuals measure state mismatch, not the construction.
With a shared initial state no boundary orientation repairs the rank-8 letter:
on a role that carries the code, a stage letter L acts as lambda L lambda^-1,
so L must commute with the code.  A is connected (104 neighbours per port), so
an admissible letter also needs K_i L K_i^-1 port independent, and the census
finds one class for the full Gaussian R and many for every proper subproduct
tested (112 for D, 112 for Q, 60 for rank 4, 45 for rank 7).  Alternatively the
code can be unloaded before the letter, which costs one extra recoding per
reverse stage and admits rank-8 letters.

The lift is a gauge statement, checked gate by gate:

  every coded gate is the standard gate conjugated per role by the gauge lam,
  v = lam_r phi_r, the gauge is constant on each bridge parity class, and the
  invariant v = lam phi holds after every gate that writes a role.

  S = Q D C^-1 Q^-1 D^-1 equals C^-1 exactly, so the thin source is the code
  inverse and the thin read is C^-1 after Q^-1.

Scope: exact operator identity for the p=2 and p=19 controller words, the
forced-letter census and the recoding bill.  Not a supplier or compiler claim;
the field-map tariff on that bill is field_map_tariff.py.
"""
import json, random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P, IMAG, OWNERS, SIZE = 65537, 256, 112, 512
MONOMIAL_MAPS, SCALAR_ADDS, OWNED_CLEARS = 224, 896, 16

def need(ok, why):
    if not ok: raise ValueError(why)

def empty(): return [[0]*SIZE for _ in range(OWNERS)]
def add(x, y, s=1): return [[(a+s*b) % P for a, b in zip(xi, yi)] for xi, yi in zip(x, y)]
def gaussian(bank, axes, inverse=False):
    a = (1+(-IMAG if inverse else IMAG))*pow(2, -1, P) % P
    b = (1-(-IMAG if inverse else IMAG))*pow(2, -1, P) % P
    out = [r[:] for r in bank]
    for bit in axes:
        step = 1 << bit
        for row in out:
            for st in range(0, SIZE, 2*step):
                for x in range(st, st+step):
                    u, v = row[x], row[x+step]
                    row[x] = (a*u+b*v) % P
                    row[x+step] = (b*u+a*v) % P
    return out
def signed_map(rec, x, inverse=False):
    rows, mask = rec['G_rows'], rec['Z_mask']
    if inverse:
        y = sum((((sum(((r >> bit) & 1) << j for j, r in enumerate(rows)) & x).bit_count() & 1) << bit) for bit in range(9))
        sign = 1-2*((mask & x).bit_count() & 1)
    else:
        y = sum((((r & x).bit_count() & 1) << bit) for bit, r in enumerate(rows))
        sign = 1-2*((mask & y).bit_count() & 1)
    return y, sign
def signed_row(rec, row, inverse=False):
    out = [0]*SIZE
    for x, v in enumerate(row):
        if v:
            y, s = signed_map(rec, x, inverse)
            out[y] = s*v % P
    return out
def scalar_code(bank, modes, inverse=False):
    temp = [[sum(sg*bank[i][x] for i, sg in c) % P for x in range(SIZE)] for c in modes]
    den = pow(52 if inverse else 4, -1, P)
    out = [r[:] for r in bank]
    for m, c in enumerate(modes):
        for i, sg in c:
            out[i] = [(a-sg*den*b) % P for a, b in zip(out[i], temp[m])]
    return out
def physical_code(bank, records, modes, inverse=False):
    mixed = empty()
    for i, row in enumerate(bank):
        for x, v in enumerate(row):
            if v:
                y, s = signed_map(records[i], x); mixed[i][y] = s*v % P
    mixed = scalar_code(mixed, modes, inverse)
    out = empty()
    for i, row in enumerate(mixed):
        for x, v in enumerate(row):
            if v:
                y, s = signed_map(records[i], x, True); out[i][y] = s*v % P
    return out
def diff(a, b): return sum(1 for i in range(OWNERS) for j in range(SIZE) if a[i][j] != b[i][j])
IDENT = lambda x: x

class GaugeWord:
    """Logical roles v, physical roles phi, per-role gauge lam with v = lam phi."""

    def __init__(self, p, v0, C, Ci, Q):
        self.p, self.C, self.Ci, self.Q = p, C, Ci, Q
        self.v = [r[:] for r in v0]
        self.f = [r[:] for r in v0]
        self.lam = [IDENT]*2*p
        self.linv = [IDENT]*2*p
        self.fails = []
        self.recodings = 0

    def check(self, roles, tag):
        for r in roles:
            d = diff(self.lam[r](self.f[r]), self.v[r])
            if d: self.fails.append((tag, r, d))

    def set_gauge(self, r, lam, linv, change):
        self.f[r] = change(self.f[r]); self.lam[r] = lam; self.linv[r] = linv
        self.recodings += 1
        self.check([r], 'gauge%d' % r)

    def fwd(self, j, order):
        x, y = 2*j, 2*j+1
        self.v[y] = add(self.v[y], self.Q(self.v[x], True))
        src = self.f[x]
        if self.lam[x] is not IDENT: src = self.lam[x](src); self.recodings += 1
        if order == 'inv-first':
            src = self.Q(src, True)
            if self.linv[y] is not IDENT: src = self.linv[y](src); self.recodings += 1
        else:
            if self.linv[y] is not IDENT: src = self.linv[y](src); self.recodings += 1
            src = self.Q(src, True)
        self.f[y] = add(self.f[y], src)
        self.check([y], 'fwd%d' % j)

    def rev_add(self, j):
        a, b = 2*j, 2*j+1
        self.v[a] = add(self.v[a], self.Q(self.v[b]), -1)
        src = self.f[b]
        if self.lam[b] is not IDENT: src = self.lam[b](src); self.recodings += 1
        src = self.Q(src)
        if self.linv[a] is not IDENT: src = self.linv[a](src); self.recodings += 1
        self.f[a] = add(self.f[a], src, -1)
        self.check([a], 'rev%d-add' % j)

    def rev_letter(self, j, letter):
        for r in (2*j, 2*j+1):
            self.v[r] = letter(self.v[r])
            self.f[r] = letter(self.f[r])
        self.check([2*j, 2*j+1], 'rev%d-letter' % j)

    def bridge(self, dst, src, cf):
        for d, s, cc in ((2*dst, 2*src, cf), (2*src+1, 2*dst+1, -cf)):
            need(self.lam[d] is self.lam[s] and self.linv[d] is self.linv[s],
                 'gauge mismatch across bridge %d-%d' % (dst, src))
            self.v[d] = add(self.v[d], self.v[s], cc)
            self.f[d] = add(self.f[d], self.f[s], cc)
        self.check([2*dst, 2*src+1], 'bridge%d-%d' % (dst, src))

def reference(p, v0, letter, Qc):
    """The recovered full_build word: no code, given letter, same gate sequence."""
    st = [r[:] for r in v0]
    def fwd(j):
        x, y = 2*j, 2*j+1
        st[y] = add(st[y], Qc(st[x], True))
    def rev(j):
        a, b = 2*j, 2*j+1
        st[a] = add(st[a], Qc(st[b]), -1)
        st[a] = letter(st[a]); st[b] = letter(st[b])
    def bridge(dst, src, cf):
        for d, s, cc in ((2*dst, 2*src, cf), (2*src+1, 2*dst+1, -cf)):
            st[d] = add(st[d], st[s], cc)
    fwd(0)
    for j in range(p):
        rev(j)
        if j < p-1: bridge(j, j+1, 1)
        fwd(j)
        if j < p-1: bridge(j, j+1, -1)
    for j in reversed(range(p-1)): bridge(j+1, j, 1)
    return st

def word(p, v0, C, Ci, Q, letter, mode, order='inv-first'):
    w = GaugeWord(p, v0, C, Ci, Q)
    if mode == 'odd-gauge':
        for r in range(1, 2*p, 2): w.set_gauge(r, C, Ci, Ci)
    elif mode == 'even-gauge':
        for r in range(0, 2*p, 2): w.set_gauge(r, C, Ci, Ci)
    elif mode == 'coded-all':
        for r in range(2*p): w.set_gauge(r, C, Ci, Ci)
    coded = mode in ('odd-gauge', 'even-gauge', 'coded-all')
    w.fwd(0, order if coded else 'inv-last')
    for j in range(p):
        if mode == 'transient':
            w.set_gauge(2*j+1, C, Ci, Ci)
            w.rev_add(j)
            w.set_gauge(2*j+1, IDENT, IDENT, C)
            w.rev_letter(j, letter)
        else:
            w.rev_add(j)
            w.rev_letter(j, letter)
        if j < p-1: w.bridge(j, j+1, 1)
        w.fwd(j, order if coded else 'inv-last')
        if j < p-1: w.bridge(j, j+1, -1)
    for j in reversed(range(p-1)): w.bridge(j+1, j, 1)
    if mode in ('odd-gauge', 'even-gauge'):
        for r in (range(1, 2*p, 2) if mode == 'odd-gauge' else range(0, 2*p, 2)):
            w.set_gauge(r, IDENT, IDENT, C)
    return w

def bill(w):
    return {'recodings': w.recodings, 'monomial_field_maps': w.recodings*MONOMIAL_MAPS,
            'scalar_adds': w.recodings*SCALAR_ADDS, 'owned_clears': w.recodings*OWNED_CLEARS}

def main():
    receipt = json.loads((ROOT/'research/coded-native-caller/NORMALIZERS.json').read_text())
    records, cols = receipt['ports'], receipt['mode_columns']
    modes = [[(i, s) for i, s in enumerate(c) if s] for c in cols]
    C = lambda x: physical_code(x, records, modes, False)
    Ci = lambda x: physical_code(x, records, modes, True)
    Q = lambda x, inv=False: gaussian(x, [0], inv)
    Dg = lambda x, inv=False: gaussian(x, range(1, 9), inv)
    R = lambda x, inv=False: gaussian(x, range(9), inv)

    rng = random.Random(5)
    def dense(): return [[rng.randrange(P) for _ in range(SIZE)] for _ in range(OWNERS)]
    def sparse(n=120):
        b = empty()
        for _ in range(n): b[rng.randrange(OWNERS)][rng.randrange(SIZE)] = rng.randrange(1, P)
        return b

    probe = dense()
    need(diff(Ci(C(probe)), probe) == 0 and diff(C(Ci(probe)), probe) == 0, 'C inverse on a dense bank')
    print('PASS code inverse: C C^-1 = C^-1 C = I on a dense bank')
    need(diff(Q(Dg(Ci(Q(Dg(probe, True), True)))), Ci(probe)) == 0, 'S = C^-1')
    print('PASS thin source S = Q D C^-1 Q^-1 D^-1 equals the code inverse C^-1 exactly')
    cd, cq, cr = diff(Dg(C(probe)), C(Dg(probe))), diff(Q(C(probe)), C(Q(probe))), diff(R(C(probe)), C(R(probe)))
    need(cd and cq and cr == 0, 'letter commutation')
    print('PASS letters: [C,D] differs on %d entries, [C,Q] on %d, [C,R] on 0' % (cd, cq))

    nb = [set() for _ in range(OWNERS)]
    for c in cols:
        idx = [i for i, s in enumerate(c) if s]
        for i in idx: nb[i] |= set(idx)
    seen, stack = {0}, [0]
    while stack:
        i = stack.pop()
        for j in nb[i]:
            if j not in seen: seen.add(j); stack.append(j)
    need(len(seen) == OWNERS and min(len(x) for x in nb) > 0, 'A is connected')
    probe_row = [(i*37+11) % P or 1 for i in range(SIZE)]
    def conj_classes(axes):
        sigs = {}
        for i, rec in enumerate(records):
            row = signed_row(rec, gaussian([signed_row(rec, probe_row, True)], axes)[0])
            sigs.setdefault(tuple(row), []).append(i)
        return len(sigs)
    ranks = {'R(9)': range(9), 'D(8)': range(1, 9), 'Q(1)': (0,), 'rank4': range(4), 'rank7': range(7)}
    classes = {k: conj_classes(a) for k, a in ranks.items()}
    need(classes['R(9)'] == 1 and all(v > 1 for k, v in classes.items() if k != 'R(9)'), 'forced letter')
    print('PASS forced letter: A connected (112 nodes, %d neighbours each); distinct K-conjugates %s'
          % (len(nb[0]), classes))

    p = 2
    v0 = [dense() for _ in range(2*p)]
    total = 2*p*OWNERS*SIZE
    ref = reference(p, v0, Dg, Q)
    w = word(p, v0, C, Ci, Q, Dg, 'std', 'inv-last')
    need(all(diff(w.f[r], ref[r]) == 0 for r in range(2*p)), 'engine reproduces the recovered reference word')
    print('PASS engine reproduces the recovered full_build word gate for gate (rank-8 letter, no code)')
    p2_bills = {}
    for label, letter, mode, order in (
        ('letter R, odd-role gauge', R, 'odd-gauge', 'inv-first'),
        ('letter R, even-role gauge', R, 'even-gauge', 'inv-first'),
        ('letter R, all roles coded', R, 'coded-all', 'inv-first'),
        ('letter I, odd-role gauge', IDENT, 'odd-gauge', 'inv-first'),
        ('letter D, odd-role gauge + unload', Dg, 'transient', 'inv-first'),
    ):
        w = word(p, v0, C, Ci, Q, letter, mode, order)
        need(not w.fails, 'p=2 gate invariant: ' + label + ' ' + mode)
        decoded = sum(diff(w.lam[r](w.f[r]), w.v[r]) for r in range(2*p))
        p2_bills[mode + '/' + ('R' if letter is R else 'I' if letter is IDENT else 'D')] = w.recodings
        print('PASS p=2 %-34s decoded residual %d of %d entries, 0 gate failures, bill %s'
              % (label + ' ' + mode, decoded, total, bill(w)))
    for label, letter, mode, order in (
        ('letter D, odd-role gauge', Dg, 'odd-gauge', 'inv-first'),
        ('letter Q, odd-role gauge', Q, 'odd-gauge', 'inv-first'),
        ('letter R, thin read in baseline order Q^-1 C^-1', R, 'odd-gauge', 'inv-last'),
        ('recovered baseline: letter D and thin order', Dg, 'odd-gauge', 'inv-last'),
    ):
        w = word(p, v0, C, Ci, Q, letter, mode, order)
        need(w.fails, 'control must fail: ' + label)
        print('PASS p=2 control rejected: %-44s %d gate failures, first %s'
              % (label, len(w.fails), w.fails[0]))

    p = 19
    v0 = [sparse() for _ in range(2*p)]
    total = 2*p*OWNERS*SIZE
    bills = {}
    for label, mode in (('odd-role gauge', 'odd-gauge'), ('even-role gauge', 'even-gauge')):
        w = word(p, v0, C, Ci, Q, R, mode)
        need(not w.fails, 'p=19 gate invariant: ' + label)
        decoded = sum(diff(w.lam[r](w.f[r]), w.v[r]) for r in range(2*p))
        bills[mode] = w.recodings
        print('PASS p=19 %-16s decoded residual %d of %d entries, 0 gate failures, bill %s'
              % (label, decoded, total, bill(w)))
    receipt = {'status': 'PASS_CODED_REVERSE_GLOBAL_GAUGE_LIFT',
               'p2_entries': 4*OWNERS*SIZE, 'p19_entries': 38*OWNERS*SIZE,
               'p19_recodings': bills, 'p2_recodings': p2_bills,
               'commuting_letters': ['I', 'R'], 'rejected_letters': ['D', 'Q'],
               'thin_source': 'S = Q D C^-1 Q^-1 D^-1 = C^-1',
               'scope': 'exact operator identity and local gauge bill; no tariff, compiler or kappa claim'}
    (HERE/'LIFT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, sort_keys=True))

if __name__ == '__main__':
    main()
