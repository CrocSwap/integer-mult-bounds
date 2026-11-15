"""BIG-RELAY mover.py (own code): FRAME-LEVEL removal of a relay frame F by SHEAR TRANSPORT.
Each op at F is a shear/scale E on the stopping helpers. Moving E earlier (later) to a co-presence of its two registers at G != F
conjugates every intervening op O touching them: O' = E O E^-1 (earlier) / E^-1 O E (later). O' is decomposed into elementary
SCALE/ADD ops; legal iff every register it touches is at O's frame at O's time. When all F-ops are moved, the stopping helpers'
two MOVEs a->F->b merge into one a->b. Exact Fractions throughout."""
from fractions import Fraction as Q
import bisect, collections, copy
from lib import *

class Prog:
    def __init__(self, W):
        self.W = W; self.ops = [(float(i), e) for i, e in enumerate(W['program'])]
    def keys(self): return [k for k, _ in self.ops]

def timeline(ops, NP, NO, initial):
    """per register: list of (key, frame) meaning frame from key on (initial key -inf)."""
    tl = {r: [(-1e18, initial[r] if r < NP else None)] for r in range(NP + NO)}
    for k, e in ops:
        if e[0] == 'MOVE': tl[e[1]].append((k, e[3]))
        elif e[0] == 'INIT': tl[e[1]].append((k - 1e-9, e[2]))
        elif e[0] == 'CLEAR': tl[e[1]].append((k + 1e-9, None))
    return tl
def frame_at(tl, r, k):
    L = tl.get(r)
    if L is None: return None
    i = bisect.bisect_right([x[0] for x in L], k) - 1   # small lists
    return L[i][1]
def stays(tl, r):
    L = tl[r]; return [(L[i][0], L[i + 1][0] if i + 1 < len(L) else 1e18, L[i][1]) for i in range(len(L))]

def opmat(e):
    """op -> (dict-of-dict N) with map s -> (I+N)s on register rows."""
    if e[0] == 'ADD': return {e[1]: {e[2]: Q(e[3])}}
    if e[0] == 'SCALE': return {e[1]: {e[1]: Q(e[2]) - 1}}
    return None
def mat_full(N, regs):
    A = {r: {c: (Q(1) if r == c else Q(0)) for c in regs} for r in regs}
    for r, row in N.items():
        for c, v in row.items(): A[r][c] += v
    return A
def mul(A, B, regs): return {r: {c: sum(A[r][k] * B[k][c] for k in regs) for c in regs} for r in regs}
def decompose(A, regs):
    """A (invertible, dict) -> list of elementary ops [(kind, r, s, q)] whose sequential application realises s -> A s.
    Row-reduce A to I with row ops; A = E1^-1 ... Ek^-1; apply Ek^-1 first."""
    A = {r: dict(A[r]) for r in regs}; ops = []   # ops recorded as E_i applied to A from the left
    regs = list(regs)
    for c in regs:
        if A[c][c] == 0:
            p = next((r for r in regs if r != c and A[r][c] != 0 and all(A[r][cc] == (1 if r == cc else 0) or True for cc in regs)), None)
            if p is None: return None
            # row c += row p
            for cc in regs: A[c][cc] += A[p][cc]
            ops.append(('ADD', c, p, Q(1)))
        if A[c][c] != 1:
            q = 1 / A[c][c]
            for cc in regs: A[c][cc] *= q
            ops.append(('SCALE', c, c, q))
        for r in regs:
            if r != c and A[r][c] != 0:
                q = -A[r][c]
                for cc in regs: A[r][cc] += q * A[c][cc]
                ops.append(('ADD', r, c, q))
    # E_k ... E_1 A = I  =>  A = E_1^-1 ... E_k^-1 ; applying A to s = apply E_k^-1 first
    out = []
    for kind, r, s, q in reversed(ops):
        if kind == 'SCALE': out.append(('SCALE', r, r, 1 / q))
        else: out.append(('ADD', r, s, -q))
    return out
def nontriv(A, regs):
    return {r for r in regs for c in regs if A[r][c] != (1 if r == c else 0)} | {c for r in regs for c in regs if r != c and A[r][c] != 0}

def conj(E, O, inv_first, regs):
    """earlier: E O E^-1 ; later: E^-1 O E.  E, O full dicts on regs."""
    Ei = inverse(E, regs)
    return mul(mul(E, O, regs), Ei, regs) if not inv_first else mul(mul(Ei, O, regs), E, regs)
def inverse(E, regs):
    seq = decompose(E, regs)       # s -> E s  = apply seq in order ; inverse = reversed inverted
    I = mat_full({}, regs)
    for kind, r, s, q in reversed(seq):
        e = elem(kind, r, s, (1 / q) if kind == 'SCALE' else -q, regs)
        I = mul(I, e, regs) if False else mul(I, e, regs)
    # I currently = product applied... recompute safely by Gauss-Jordan instead
    return gj_inverse(E, regs)
def elem(kind, r, s, q, regs):
    return mat_full({r: {s: q - 1}} if kind == 'SCALE' else {r: {s: q}}, regs)
def gj_inverse(E, regs):
    regs = list(regs); A = {r: dict(E[r]) for r in regs}; I = mat_full({}, regs)
    for c in regs:
        p = next(r for r in regs[regs.index(c):] if A[r][c] != 0)
        if p != c: A[c], A[p] = A[p], A[c]; I[c], I[p] = I[p], I[c]
        q = 1 / A[c][c]; A[c] = {k: v * q for k, v in A[c].items()}; I[c] = {k: v * q for k, v in I[c].items()}
        for r in regs:
            if r != c and A[r][c] != 0:
                m = A[r][c]; A[r] = {k: A[r][k] - m * A[c][k] for k in regs}; I[r] = {k: I[r][k] - m * I[c][k] for k in regs}
    return I

def realise(A, regs, frame, key, tl):
    """elementary op list for s -> A s at `frame`; None if a touched register is absent there at `key`."""
    t = nontriv(A, regs)
    if any(frame_at(tl, r, key) != frame for r in t): return None
    seq = decompose(A, sorted(t)) if t else []
    if seq is None: return None
    out = []
    for kind, r, s, q in seq:
        if kind == 'SCALE':
            if q != 1: out.append(['SCALE', r, str(q), frame])
        elif q != 0: out.append(['ADD', r, s, str(q), frame])
    return out
def opframe(e): return evframe(e)

def try_move(ops, j, F, tl, direction):
    """ops: list of (key, op). Move op ops[j] (a shear/scale at F) earlier/later to a co-presence of its registers at G != F.
    Returns new ops list or None."""
    k0, e = ops[j]
    regsE = sorted({e[1], e[2]} if e[0] == 'ADD' else {e[1]})
    # co-presence windows of regsE at frames != F
    st = [stays(tl, r) for r in regsE]
    wins = []
    for a in st[0]:
        for rest in [st[1:]]:
            lo, hi, G = a
            ok = True
            for L in rest:
                m = [(max(lo, x[0]), min(hi, x[1])) for x in L if x[2] == G and max(lo, x[0]) < min(hi, x[1])]
                if not m: ok = False; break
                lo, hi = m[0]
            if ok and G != F and lo < hi: wins.append((lo, hi, G))
    if direction < 0: cand = sorted([w for w in wins if w[0] < k0], key=lambda w: -w[1])
    else: cand = sorted([w for w in wins if w[1] > k0], key=lambda w: w[0])
    for lo, hi, G in cand[:3]:
        if direction < 0:
            # place just before min(hi, k0): find insertion key strictly inside (lo, min(hi,k0))
            tgt = min(hi, k0); between = [i for i in range(len(ops)) if lo < ops[i][0] < k0 and i != j]
            ins_key = None
            # latest key in (lo, tgt) with no op of regsE after it until tgt: choose just below the first op >= tgt... simple: tgt - tiny
            ins_key = nextafter_below(ops, tgt, lo)
            if ins_key is None: continue
            span = [i for i in range(len(ops)) if ins_key < ops[i][0] < k0 and i != j]
        else:
            tgt = max(lo, k0); ins_key = nextafter_above(ops, tgt, hi)
            if ins_key is None: continue
            span = [i for i in range(len(ops)) if k0 < ops[i][0] < ins_key and i != j]
        if ins_key is None: continue
        res = transport(ops, j, span, regsE, tl, direction)
        if res is None: continue
        newops = [x for i, x in enumerate(ops) if i != j and i not in res[0]]
        for kk, op in res[1]: newops.append((kk, op))
        Ae = mat_full(opmat(e), regsE)
        seq = realise(Ae, regsE, G, ins_key, tl)
        if seq is None: continue
        for n_, op in enumerate(seq): newops.append((ins_key + n_ * 1e-6 * (1 if direction > 0 else 1), op))
        newops.sort(key=lambda x: x[0])
        return newops, G
    return None
def nextafter_below(ops, tgt, lo):
    ks = [k for k, _ in ops if lo < k < tgt]
    a = max(ks) if ks else lo
    if a == -1e18: a = tgt - 1
    return (a + tgt) / 2 if tgt - a > 1e-3 else None
def nextafter_above(ops, tgt, hi):
    ks = [k for k, _ in ops if tgt < k < hi]
    b = min(ks) if ks else hi
    if b == 1e18: b = tgt + 1
    return (tgt + b) / 2 - 1e-5 if b - tgt > 1e-3 else None

def transport(ops, j, span, regsE, tl, direction):
    """conjugate each op in span touching regsE. returns (set of replaced indices, [(key, newop)]) or None."""
    E = ops[j][1]; rem = set(); add = []
    for i in span:
        k, O = ops[i]
        if O[0] == 'MOVE' or O[0] in ('INIT', 'CLEAR'): continue
        part = {O[1], O[2]} if O[0] in ('ADD', 'COPY') else {O[1]}
        if not (part & set(regsE)): continue
        if O[0] == 'COPY': return None
        regs = sorted(part | set(regsE))
        Em = mat_full(opmat(E), regs); Om = mat_full(opmat(O), regs)
        C = conj(Em, Om, direction > 0, regs)
        seq = realise(C, regs, opframe(O), k, tl)
        if seq is None: return None
        rem.add(i)
        for n_, op in enumerate(seq): add.append((k + n_ * 1e-7, op))
    return rem, add
