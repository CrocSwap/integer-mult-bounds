"""Frame lattice utilities and cost model over the cached parity-fused word."""
import pickle, json
from array import array
from collections import Counter
from fractions import Fraction as F
from math import gcd
from decimal import Decimal, localcontext
from pathlib import Path
HERE = Path(__file__).resolve().parent
H = 24

def prim(r):
    g = 0
    for x in r: g = gcd(g, x)
    if g == 0: return tuple(r)
    first = next(x for x in r if x)
    if first < 0: g = -g
    return tuple(x // g for x in r)

def reduce_rows(rows, h=H):
    rows = [list(r) for r in rows]; out, pivs = [], []
    for r in rows:
        for pr, pc in zip(out, pivs):
            if r[pc]:
                a, b = pr[pc], r[pc]; r = [x*a - y*b for x, y in zip(r, pr)]
        r = list(prim(r)); c = next((j for j in range(h) if r[j]), None)
        if c is None: continue
        for i, (pr, pc) in enumerate(zip(out, pivs)):
            if pr[c]:
                a, b = r[c], pr[c]; out[i] = list(prim([x*a - y*b for x, y in zip(pr, r)]))
        out.append(r); pivs.append(c)
    return out, pivs

def kernel(rows, h=H):
    red, pivs = reduce_rows(rows, h); ps = set(pivs); basis = []
    for f in range(h):
        if f in ps: continue
        D = 1
        for r, c in zip(red, pivs):
            if r[f]: D = D*abs(r[c])//gcd(D, abs(r[c]))
        v = [0]*h; v[f] = D
        for r, c in zip(red, pivs):
            if r[f]: v[c] = -r[f]*D//r[c]
        basis.append(prim(v))
    return basis

def dot(a, b): return sum(x*y for x, y in zip(a, b))

def rank(rows, n):
    return len(reduce_rows(rows, n)[0])

class Lattice:
    def __init__(self, data):
        self.B = data['B']; self.A = data['A']; self.dimf = data['dimf']
        self.ids = {}
        for f, B in self.B.items():
            key = tuple(sorted(map(tuple, reduce_rows(B)[0]), key=lambda r: next(i for i, x in enumerate(r) if x)))
            self.ids.setdefault(key, f)
        self.subc = {}; self.meetc = {}; self.ndc = {}
        self.next = max(self.B) + 1
    def register(self, rows):
        B = reduce_rows(rows)[0]
        key = tuple(sorted(map(tuple, B), key=lambda r: next(i for i, x in enumerate(r) if x)))
        if key in self.ids: return self.ids[key]
        f = self.next; self.next += 1
        self.B[f] = [list(r) for r in key]; self.A[f] = kernel(key); self.dimf[f] = len(key); self.ids[key] = f
        return f
    def sub(self, f, g):
        if f == g: return True
        k = (f, g); r = self.subc.get(k)
        if r is None:
            r = self.dimf[f] <= self.dimf[g] and all(dot(a, b) == 0 for a in self.A[g] for b in self.B[f])
            self.subc[k] = r
        return r
    def meet(self, f, g):
        if f == g or self.sub(f, g): return f
        if self.sub(g, f): return g
        k = (min(f, g), max(f, g)); r = self.meetc.get(k)
        if r is None:
            r = self.register(kernel(list(self.A[f]) + list(self.A[g])) or [])
            self.meetc[k] = r
        return r
    def nondeg(self, f):
        r = self.ndc.get(f)
        if r is not None: return r
        B, A = self.B[f], self.A[f]
        if not B or len(B) == H: r = True
        elif len(B) <= len(A):
            s = [sum(b) for b in B]
            M = [[9*dot(B[i], B[j]) - s[i]*s[j] for j in range(len(B))] for i in range(len(B))]
            r = rank(M, len(B)) == len(B)
        else:
            s = [sum(a) for a in A]
            M = [[(9-H)*dot(A[i], A[j]) + s[i]*s[j] for j in range(len(A))] for i in range(len(A))]
            r = rank(M, len(A)) == len(A)
        self.ndc[f] = r; return r

def load():
    d = pickle.loads((HERE/'cache.pkl').read_bytes())
    rec = array('i'); rec.frombytes(d['records']); d['rec'] = rec
    return d

def final_frames(d, L):
    v = d['v']; final = dict(d['initial']); rec = d['rec']
    for k in range(0, len(rec), 6):
        if rec[k] == 0: final[rec[k+1]] = rec[k+3]
    return final

def cost(d, L, frames):
    """Paid one-stage histogram (incl. 24 copies) for a gate->frame assignment (index by record)."""
    rec = d['rec']; n = d['n']; state = dict(d['initial']); hist = Counter(); final = d['final']
    def mv(s, f):
        b = state[s]
        if b == f: return
        assert L.sub(b, f), ('nest', s, b, f)
        g = L.dimf[f]-L.dimf[b]
        if g: hist[g] += 1
        state[s] = f
    for k in range(0, len(rec), 6):
        op, a, b, c, f, z = rec[k:k+6]
        if op == 0: continue
        if op == 1:
            g = frames.get(k//6, f); mv(a, g)
            if b != n: mv(b, g)
        elif op == 2:
            mv(a, c); hist[z] += 1
        elif op == 3:
            assert state[a] == c
    for s in sorted(final): mv(s, final[s])
    return hist

# ---- saving evaluation calibrated to the certificate profile
CERT = json.loads(Path(__file__).resolve().parents[2]/'community-pr279-audit/certificate.json'.read_text())
BASEH = Counter({int(r): n for r, n in CERT['bit_profile']['histogram'].items()})
M, WST = 120, CERT['bit_profile']['W']

def saving(Hn):
    with localcontext() as c:
        c.prec = 50
        terms = [(Decimal(r*n)/Decimal(M*WST), (Decimal(M)/Decimal(r)).ln()) for r, n in Hn.items() if n]
        fb = Decimal(32*M*sum(Hn.values()))/Decimal(10**16*WST); lm = Decimal(M).ln()
        lo, hi = Decimal(0), Decimal('.01')
        for _ in range(120):
            a = (lo+hi)/2
            if sum(p*(a*l).exp() for p, l in terms) + fb*(a*lm).exp() < 1: lo = a
            else: hi = a
        return float(lo)

def saving_from_local(local_hist, base_local_hist):
    delta = Counter(local_hist); delta.subtract(base_local_hist)
    Hn = Counter(BASEH)
    for r, c in delta.items(): Hn[r] += 60*c
    assert all(v >= 0 for v in Hn.values())
    return saving(Hn)
