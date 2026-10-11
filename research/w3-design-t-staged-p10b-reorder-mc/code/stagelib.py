"""Shared helpers of the post-Design-T transcript stages (kernel, retiming, reorder) on PR249-format snapshots:
snapshot I/O, exact frame algebra over Q, the legality / formal-F2 replay and the source-span rule.
Chafik Boukhalfa (chafreaky) with substantial Anthropic Claude assistance; Apache-2.0."""
import collections, json, math, hashlib
from fractions import Fraction
from pathlib import Path
import numpy as np

HH = 20
def load_snapshot(d):
    d = Path(d)
    s = json.loads((d / '249-states.json').read_text())
    fr = json.loads((d / 'frames.json').read_text())
    rec = np.frombuffer((d / '249-records.bin').read_bytes(), dtype='<i4').reshape(-1, 6).copy()
    return dict(s=s, fr=fr, rec=rec)


def save_snapshot(snap, d):
    d = Path(d); d.mkdir(parents=True, exist_ok=True)
    (d / '249-records.bin').write_bytes(np.ascontiguousarray(snap['rec'], dtype='<i4').tobytes())
    (d / '249-states.json').write_text(json.dumps(snap['s']))
    (d / 'frames.json').write_text(json.dumps(snap['fr']))


def rec_sha(snap):
    return hashlib.sha256(np.ascontiguousarray(snap['rec'], dtype='<i4').tobytes()).hexdigest()


def dims(fr):
    return {int(k): len(v['B']) for k, v in fr['frames'].items()}


def kernel_int(B):
    M = [[Fraction(x) for x in b] for b in B]; m = len(M); piv = []; r = 0
    for c in range(HH):
        pr = next((i for i in range(r, m) if M[i][c] != 0), None)
        if pr is None: continue
        M[r], M[pr] = M[pr], M[r]; pv = M[r][c]; M[r] = [x / pv for x in M[r]]
        for i in range(m):
            if i != r and M[i][c] != 0:
                f_ = M[i][c]; M[i] = [a - f_ * b for a, b in zip(M[i], M[r])]
        piv.append(c); r += 1
        if r == m: break
    out = []
    for fc in [c for c in range(HH) if c not in piv]:
        x = [Fraction(0)] * HH; x[fc] = Fraction(1)
        for i, pc in enumerate(piv): x[pc] = -M[i][fc]
        den = 1
        for q in x: den = den * q.denominator // math.gcd(den, q.denominator)
        out.append([int(q * den) for q in x])
    return out



# ------------------------------------------------------------------------------------------- checker
class Frames:
    def __init__(self, fr):
        self.F = fr['frames']; self.dim = dims(fr); self.cache = {}; self.nd = {}
        self.Bm = {}; self.Am = {}

    def mats(self, f):
        if f not in self.Bm:
            self.Bm[f] = [list(map(int, r)) for r in self.F[str(f)]['B']]
            self.Am[f] = [list(map(int, r)) for r in self.F[str(f)]['A']]
        return self.Bm[f], self.Am[f]

    def sub(self, a, b):
        """span(B_a) <= span(B_b), exactly over Q: every row of B_a annihilated by every row of A_b"""
        key = (a, b)
        if key in self.cache: return self.cache[key]
        Ba, _ = self.mats(a); _, Ab = self.mats(b)
        ok = self.dim[a] <= self.dim[b] and all(sum(x * y for x, y in zip(r, s)) == 0 for r in Ba for s in Ab)
        self.cache[key] = ok
        return ok

    def frame_ok(self, f):
        """B has dim rows, A has h - dim rows, A B^T = 0 and rank B = dim (exact)"""
        B, A = self.mats(f); d = self.dim[f]
        if len(B) != d or len(A) != HH - d: return False
        if any(sum(x * y for x, y in zip(r, s)) for r in A for s in B): return False
        return rank_q(B) == d and rank_q(A) == HH - d

    def nondeg(self, f):
        """Gram matrix of B under G = I - J/9 nonsingular (exact)"""
        if f in self.nd: return self.nd[f]
        B, _ = self.mats(f); d = len(B)
        if d == 0: self.nd[f] = True; return True
        s = [sum(r) for r in B]
        M = [[9 * sum(x * y for x, y in zip(B[i], B[k])) - s[i] * s[k] for k in range(d)] for i in range(d)]
        self.nd[f] = rank_q(M) == d
        return self.nd[f]


def rank_q(M):
    M = [[Fraction(x) for x in r] for r in M]
    if not M: return 0
    rk = 0; cols = len(M[0])
    for c in range(cols):
        p = next((i for i in range(rk, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[rk], M[p] = M[p], M[rk]
        for i in range(len(M)):
            if i != rk and M[i][c] != 0:
                q = M[i][c] / M[rk][c]; M[i] = [a - q * b for a, b in zip(M[i], M[rk])]
        rk += 1
        if rk == len(M): break
    return rk


def check(snap, frames=None, ncopies=HH, want_final=True):
    """Legality replay (state frames, exact nesting, ranks, ADD frames, COPY/ERASE lifecycle), final frames, exact
    nondegeneracy of every used frame, and a formal F2 replay of all columns. Returns a receipt with the residual
    sigma-0 dirt of each target (to be cancelled by frame-0 completion reads)."""
    s, rec = snap['s'], snap['rec']
    Fm = frames or Frames(snap['fr']); dim = Fm.dim
    n, v, ZERO, FULL = s['n'], s['v'], s['ZERO'], s['FULL']
    state = [s['initial'][str(r)] for r in range(n)] + [ZERO]
    copied = False; src = -1; copies = erases = 0; used = set(state); bad = []
    for k, (o, a, b, c, f, z) in enumerate(rec.tolist()):
        if o == 0:
            if state[a] != b: bad.append(('move state', k))
            if not Fm.sub(b, c): bad.append(('move nest', k))
            if dim[c] - dim[b] != f: bad.append(('move rank', k))
            state[a] = c; used.add(c)
        elif o == 1:
            if state[a] != f or state[b] != f: bad.append(('add frame', k))
            if a == b: bad.append(('self add', k))
            if copied and (a == src or a == n): bad.append(('copy window', k))
            if (a == n or b == n) and not copied: bad.append(('temp inactive', k))
            used.add(f)
        elif o == 2:
            if copied or b != n or state[a] != c or z != dim[c]: bad.append(('copy', k))
            copied = True; src = a; state[n] = f; copies += 1; used.add(f)
        elif o == 3:
            if not copied or a != src or state[a] != c or state[n] != f: bad.append(('erase', k))
            copied = False; erases += 1
        else: bad.append(('op', k))
    assert not copied and copies == ncopies and erases == ncopies, (copies, erases)
    finals = sum(1 for r in range(n) if state[r] != s['final'][str(r)])
    assert not bad, bad[:10]
    if want_final: assert finals == 0, finals
    badframes = [f for f in used if not Fm.frame_ok(f)]
    degen = [f for f in used if not Fm.nondeg(f)]
    assert not badframes and not degen, (badframes[:5], degen[:5])
    # formal F2 replay
    WD = (n + 1 + 63) // 64
    val = np.zeros((n + 1, WD), np.uint64)
    for r in range(n): val[r, r // 64] |= np.uint64(1) << np.uint64(r % 64)
    for o, a, b, c, f, z in rec.tolist():
        if o == 1:
            if c & 1: val[a] ^= val[b]
        elif o == 2: val[n] = val[a]
        elif o == 3: val[n] = 0
    sig = [dim[s['initial'][str(r)]] for r in range(n)]
    badX = badH = 0; resid = []; other = 0
    ident = np.zeros((n + 1, WD), np.uint64)
    for r in range(n + 1): ident[r, r // 64] |= np.uint64(1) << np.uint64(r % 64)
    diff = val ^ ident
    for t in range(v): diff[v + t, t // 64] ^= np.uint64(1) << np.uint64(t % 64)
    for r in np.nonzero(diff[:n].any(axis=1))[0].tolist():
        if r < v: badX += 1
        elif r >= 2 * v:
            if sig[r] < HH: badH += 1
        else:
            bitsr = np.unpackbits(diff[r].view(np.uint8), bitorder='little')
            for q in np.nonzero(bitsr)[0].tolist():
                if 2 * v <= q < n and sig[q] == 0: resid.append((r - v, q))
                else: other += 1
    temp_clean = not val[n].any()
    return dict(records=len(rec), copies=copies, erases=erases, used_frames=len(used), final_mismatch=finals,
                X_not_restored=badX, H_not_restored=badH, resid_sigma0=len(resid), resid_other=other,
                temp_clean=temp_clean, resid=resid)



def span_check(snap, chi, frames=None):
    """Source-span rule: at every ADD the integer source support of each non-target operand lies in the gate frame
    (chi_s annihilated by every row of the frame's A). Returns the number of violating (gate, operand) pairs."""
    s, rec = snap['s'], snap['rec']; n, v = s['n'], s['v']
    Fm = frames or Frames(snap['fr'])
    cols = [{i: 1} if i < v else {} for i in range(n + 1)]; centre = None; bad = 0; okc = {}
    def ok(g, sup):
        _, A = Fm.mats(g)
        for x in sup:
            key = (g, x)
            r = okc.get(key)
            if r is None:
                r = all(sum(p * q for p, q in zip(row, chi[x])) == 0 for row in A); okc[key] = r
            if not r: return False
        return True
    for o, a, b, c, f, z in rec.tolist():
        if o == 2: centre = a; cols[n] = dict(cols[a]); continue
        if o == 3: centre = None; cols[n] = {}; continue
        if o != 1: continue
        src = cols[b]; ca = cols[a]
        for x, y in src.items():
            w = ca.get(x, 0) + c * y
            if w: ca[x] = w
            else: ca.pop(x, None)
        if not (v <= a < 2 * v) and not ok(f, ca): bad += 1
        if not (v <= b < 2 * v) and b != n and not ok(f, cols[b]): bad += 1
    return bad


def key_of(basis):
    """canonical RREF over Q of a list of rows (hashable subspace key)"""
    M = [[Fraction(x) for x in r] for r in basis]
    if not M: return ()
    rk = 0; cols = len(M[0])
    for c in range(cols):
        p = next((i for i in range(rk, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[rk], M[p] = M[p], M[rk]; pv = M[rk][c]; M[rk] = [x / pv for x in M[rk]]
        for i in range(len(M)):
            if i != rk and M[i][c] != 0:
                q = M[i][c]; M[i] = [a - q * b for a, b in zip(M[i], M[rk])]
        rk += 1
    return tuple(tuple(r) for r in M[:rk])


def labels_chi(path):
    lab = json.load(open(path))['lab']
    return [[1 if j in l else 0 for j in range(HH)] for l in lab]


def full_check(snap, chi, log=print, tag=''):
    """legality, final frames, exact frame validity and nondegeneracy, formal F2 of every column, source spans"""
    c = check(snap)
    c['span_violations'] = span_check(snap, chi)
    c.pop('resid')
    log('%s check: %s' % (tag, c))
    assert c['final_mismatch'] == 0 and c['X_not_restored'] == 0 and c['H_not_restored'] == 0 and c['resid_sigma0'] == 0 \
        and c['resid_other'] == 0 and c['temp_clean'] and c['span_violations'] == 0, c
    return c
