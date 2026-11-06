"""Five-call, nullity-two census for three rank-two data registers over F2.

Apache-2.0. Prepared for Josie Elliston with Claude (Anthropic) assistance.

Model: research/bit-span4-auxiliary-structure, open question 1.  Paid factors
F_j = I + ([A_j] - 1) N_j with N_j a binary rank-one idempotent on W scalar
registers; the product lives in F2[Z^k / L], L the saturated relation lattice
of the frames.  Two subsets S, T of calls give the same address exactly when
1_S - 1_T lies in L, i.e. in D = L cap {-1,0,1}^k, so only D matters.

``run`` enumerates, for every L, only the words allowed by the derivative
condition offdiag(N_j) = sum_i (b_i)_j M_i (mod 2) for a Z-basis b of L
(README, step 2), one representative per register-permutation orbit of the
pattern assignment, weighted by orbit size.  ``run_unpruned`` enumerates
every word and checks that each diagonal word satisfies that condition.
No floating point, randomness or assertions; standard library only.
"""
import itertools
import sys
import time
from fractions import Fraction


def idempotents(W):
    out = set()
    for x in range(1, 1 << W):
        for y in range(1, 1 << W):
            if bin(x & y).count("1") % 2 == 1:
                rows = tuple(y if (x >> a) & 1 else 0 for a in range(W))
                out.add(rows)
    return sorted(out)


def offdiag(Mrows, W):
    p = 0
    for a, r in enumerate(Mrows):
        p |= (r & ~(1 << a)) << (W * a)
    return p


def mul(A, B):
    out = []
    for r in A:
        acc = 0
        b = 0
        while r:
            if r & 1:
                acc ^= B[b]
            r >>= 1
            b += 1
        out.append(acc)
    return tuple(out)


def rank_q(vectors):
    """Rank over Q (exact Fractions)."""
    rows = [[Fraction(v) for v in vec] for vec in vectors]
    rank = 0
    ncol = len(rows[0]) if rows else 0
    for c in range(ncol):
        piv = None
        for i in range(rank, len(rows)):
            if rows[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i][c] != 0:
                f = rows[i][c] / rows[rank][c]
                rows[i] = [x - f * y for x, y in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def in_span2(a, b, v):
    """v in Q-span(a, b) (a, b independent): all 3x3 minors of [a; b; v] vanish."""
    n = len(a)
    for i, j, l in itertools.combinations(range(n), 3):
        d = (a[i] * (b[j] * v[l] - b[l] * v[j]) - a[j] * (b[i] * v[l] - b[l] * v[i])
             + a[l] * (b[i] * v[j] - b[j] * v[i]))
        if d:
            return False
    return True


def independent(a, b):
    return any(a[i] * b[j] - a[j] * b[i] for i, j in itertools.combinations(range(len(a)), 2))


def lattices(k):
    """Every 2-dim Q-span V of two {-1,0,1}^k vectors, as (D, basis).

    D = V cap {-1,0,1}^k (a frozenset), basis = a Z-basis of the saturated lattice V cap Z^k.
    """
    cube = [v for v in itertools.product((-1, 0, 1), repeat=k) if any(v)]
    half = [v for v in cube if next(x for x in v if x) > 0]
    seen = {}
    covered = set()
    for a, b in itertools.combinations(half, 2):
        if (a, b) in covered or not independent(a, b):
            continue
        D = frozenset(v for v in cube if in_span2(a, b, v))
        Dh = sorted(v for v in D if v in set(half))
        for x, y in itertools.combinations(Dh, 2):
            covered.add((x, y))
        if D not in seen:
            seen[D] = saturate(a, b)
    return list(seen.items())


def minors_gcd(a, b):
    from math import gcd
    g = 0
    for i, j in itertools.combinations(range(len(a)), 2):
        g = gcd(g, a[i] * b[j] - a[j] * b[i])
    return g


def saturate(a, b):
    a, b = list(a), list(b)
    while True:
        g = minors_gcd(a, b)
        if g == 1:
            return (tuple(a), tuple(b))
        # find prime p | g and an integral (la + mb)/p
        p = next(q for q in range(2, abs(g) + 1) if g % q == 0)
        done = False
        for lam in range(p):
            for mu in range(p):
                if (lam, mu) == (0, 0):
                    continue
                c = [lam * x + mu * y for x, y in zip(a, b)]
                if all(x % p == 0 for x in c):
                    c = [x // p for x in c]
                    if mu != 0:
                        b = c
                    else:
                        a = c
                    done = True
                    break
            if done:
                break
        if not done:
            raise RuntimeError("saturation failed")


def in_span(basis, v):
    return in_span2(basis[0], basis[1], v)


def run(W, k=5, data=3, sym=True, log=sys.stderr, lowrank=False):
    idem = idempotents(W)
    enc = lambda rows: sum(r << (W * a) for a, r in enumerate(rows))
    lifts = {}
    for N in idem:
        lifts.setdefault(offdiag(N, W), []).append(N)
    patterns = sorted(lifts)
    perms = list(itertools.permutations(range(W))) if sym else [tuple(range(W))]
    def perm_pat(p, s):
        q = 0
        for a in range(W):
            for b in range(W):
                if (p >> (W * a + b)) & 1:
                    q |= 1 << (W * s[a] + s[b])
        return q
    ptab = {p: [perm_pat(p, s) for s in perms] for p in patterns}
    allp = set(patterns)
    # canonical pairs (p1,p2) and singles, with orbit weights
    def reps_pairs(need3):
        out = []
        for p1 in patterns:
            for p2 in patterns:
                if need3 and (p1 ^ p2) not in allp:
                    continue
                imgs = {(ptab[p1][i], ptab[p2][i]) for i in range(len(perms))}
                if (p1, p2) == min(imgs):
                    out.append((p1, p2, len(imgs)))
        return out
    R2, R3 = reps_pairs(False), reps_pairs(True)
    R1 = []
    for p in patterns:
        imgs = set(ptab[p])
        if p == min(imgs):
            R1.append((p, len(imgs)))
    I = enc(tuple(1 << a for a in range(W)))
    full = (1 << (W * W)) - 1
    diagmask = sum(1 << (W * a + a) for a in range(W))
    rowmask = (1 << W) - 1
    def mulint(X, B):
        out = 0
        for a in range(W):
            r = (X >> (W * a)) & rowmask
            acc = 0
            b = 0
            while r:
                if r & 1:
                    acc ^= (B >> (W * b)) & rowmask
                r >>= 1; b += 1
            out |= acc << (W * a)
        return out
    fac = {}
    for N in idem:
        n = enc(N)
        fac[N] = ((n ^ I, {}), (n, {}))
    lats = [(D, B) for D, B in lattices(k) if not any(sum(1 for x in v if x) == 1 for v in D)]
    if lowrank:
        cube = [v for v in itertools.product((-1, 0, 1), repeat=k) if any(v)]
        lats = [(frozenset(), ())]
        for r in cube:
            if next(x for x in r if x) > 0 and sum(1 for x in r if x) >= 2:
                lats.append((frozenset((r, tuple(-x for x in r))), (r,)))
    def inspan(Bs, v):
        if not Bs:
            return not any(v)
        if len(Bs) == 2:
            return in_span(Bs, v)
        return rank_q([Bs[0], v]) == 1
    words = wsum = diag = 0
    hist = {}
    cands = []
    t0 = time.time()
    for li, (D, B) in enumerate(lats):
        cid = []
        reps = []
        for S in range(1 << k):
            v = tuple((S >> j) & 1 for j in range(k))
            f = None
            for c, T in enumerate(reps):
                w = tuple(x - y for x, y in zip(v, T))
                if w in D:
                    f = c; break
            if f is None:
                f = len(reps); reps.append(v)
            cid.append(f)
        low = []
        for T in reps:
            lw = (not any(T)) or inspan(B, T)
            for j in range(k):
                for sg in (1, -1):
                    if lw: break
                    u = list(T); u[j] -= sg
                    lw = (not any(u)) or inspan(B, u)
            low.append(lw)
        kap = [tuple(b[j] % 2 for b in B) + (0,) * (2 - len(B)) for j in range(k)]
        used = sorted(set(c for c in kap if c != (0, 0)))
        if not used:
            assigns = [({}, 1)]
        elif len(used) == 1:
            assigns = [({used[0]: p}, w) for p, w in R1]
        else:
            c1, c2 = used[0], used[1]
            c3 = (c1[0] ^ c2[0], c1[1] ^ c2[1])
            if c3 in used:
                assigns = [({c1: p1, c2: p2, c3: p1 ^ p2}, w) for p1, p2, w in R3]
            else:
                assigns = [({c1: p1, c2: p2}, w) for p1, p2, w in R2]
        if not used and sym:
            pass  # all-coordinate words: no orbit reduction, weight 1 per word
        ncls = len(reps)
        for a, wt in assigns:
            choice = [lifts[a[c]] if c != (0, 0) else lifts[0] for c in kap]
            for Ns in itertools.product(*choice):
                words += 1; wsum += wt
                prods = [(0, I)]
                for j, N in enumerate(Ns):
                    (m0, d0), (m1, d1) = fac[N]
                    nxt = []
                    bit = 1 << j
                    for S, X in prods:
                        y = d0.get(X)
                        if y is None:
                            y = d0[X] = mulint(X, m0)
                        z = d1.get(X)
                        if z is None:
                            z = d1[X] = mulint(X, m1)
                        nxt.append((S, y)); nxt.append((S | bit, z))
                    prods = nxt
                acc = [0] * ncls
                for S, X in prods:
                    acc[cid[S]] ^= X
                ok = True
                seen = 0
                dcls = [None] * W
                for c, X in enumerate(acc):
                    if X & ~diagmask & full:
                        ok = False; break
                    if X & seen:
                        ok = False; break
                    seen |= X
                    if X:
                        for a_ in range(W):
                            if (X >> (W * a_ + a_)) & 1:
                                dcls[a_] = c
                if not ok or seen != diagmask:
                    continue
                diag += wt if used else 1
                high = sum(1 for c in dcls if not low[c])
                hist[high] = hist.get(high, 0) + (wt if used else 1)
                if high >= data:
                    cands.append((sorted(D), B, Ns))
        if log and li % 500 == 0:
            print(f"W={W} {li}/{len(lats)} words={words} diag={diag} t={time.time()-t0:.0f}s", file=log, flush=True)
    return dict(W=W, k=k, lattices=len(lats), evaluated_words=words, weighted_words=wsum,
                diagonal_words_weighted=diag, high_hist=dict(sorted(hist.items())), candidates=len(cands)), cands


def run_unpruned(W, k):
    idem = idempotents(W)
    I = tuple(1 << a for a in range(W))
    pairs = {N: (tuple(r ^ i for r, i in zip(N, I)), N) for N in idem}
    lats = [(D, B) for D, B in lattices(k) if not any(sum(1 for x in v if x) == 1 for v in D)]
    diag = 0; hist = {}; viol = 0
    for D, B in lats:
        cid, reps = [], []
        for S in range(1 << k):
            v = tuple((S >> j) & 1 for j in range(k))
            f = next((c for c, T in enumerate(reps) if tuple(x - y for x, y in zip(v, T)) in D), None)
            if f is None:
                f = len(reps); reps.append(v)
            cid.append(f)
        low = []
        for T in reps:
            lw = (not any(T)) or in_span(B, T)
            for j in range(k):
                for sg in (1, -1):
                    if lw: break
                    u = list(T); u[j] -= sg
                    lw = (not any(u)) or in_span(B, u)
            low.append(lw)
        kap = [(B[0][j] % 2, B[1][j] % 2) for j in range(k)]
        for Ns in itertools.product(idem, repeat=k):
            prods = [(0, I)]
            for j, N in enumerate(Ns):
                m0, m1 = pairs[N]
                prods = [q for S, X in prods for q in ((S, mul(X, m0)), (S | 1 << j, mul(X, m1)))]
            acc = [[0] * W for _ in reps]
            for S, X in prods:
                for a in range(W):
                    acc[cid[S]][a] ^= X[a]
            dcls = [None] * W; ok = True
            for c, X in enumerate(acc):
                for a in range(W):
                    if X[a] & ~(1 << a): ok = False
                    elif X[a]:
                        if dcls[a] is not None: ok = False
                        dcls[a] = c
            if not ok or None in dcls:
                continue
            diag += 1
            h = sum(1 for c in dcls if not low[c]); hist[h] = hist.get(h, 0) + 1
            # derivative condition: offdiag N_j = kap_j1 M1 + kap_j2 M2 for some M1, M2
            pats = [offdiag(N, W) for N in Ns]
            good = False
            cand = set(pats) | {0}
            for M1 in cand | {p ^ q for p in cand for q in cand}:
                for M2 in cand | {p ^ q for p in cand for q in cand}:
                    if all(p == ((M1 if c[0] else 0) ^ (M2 if c[1] else 0)) for p, c in zip(pats, kap)):
                        good = True; break
                if good: break
            if not good: viol += 1
    return dict(W=W, k=k, diagonal=diag, hist=dict(sorted(hist.items())), derivative_violations=viol)

