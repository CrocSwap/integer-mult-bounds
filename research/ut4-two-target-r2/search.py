#!/usr/bin/env python3
"""Exhaustive search for short two-target UT4(F2) central words without extra roles.

Model (CrocSwap/integer-mult-bounds#1662): paid factors I + ([g]+1) x y^T over F2[UT4(F2)], g in {a,b,c};
target I + ([z]+1) diag(I_w, 0). Words are lists of (label, x, y) in product order;
x, y are nonzero bit vectors over the r roles. Standard library only.

Aaron Wang / navinor, with help from Claude Code. Apache-2.0.
"""
import itertools

# ---------- UT4(F2) and its group algebra (elements are 64-bit masks) ----------
POS = ((0, 1), (1, 2), (2, 3), (0, 2), (1, 3), (0, 3))


def mat(bits):
    rows = [1 << i for i in range(4)]                      # row i, bit j = entry (i, j)
    for k, (i, j) in enumerate(POS):
        if bits >> k & 1:
            rows[i] |= 1 << j
    return tuple(rows)


def mmul4(A, B):
    out = []
    for i in range(4):
        row = 0
        for k in range(4):
            if A[i] >> k & 1:
                row ^= B[k]
        out.append(row)
    return tuple(out)


G = [mat(b) for b in range(64)]
idx = {g: i for i, g in enumerate(G)}
assert len(idx) == 64
MUL = [[idx[mmul4(g, h)] for h in G] for g in G]
E = idx[mat(0)]
GEN = {'a': idx[mat(1)], 'b': idx[mat(2)], 'c': idx[mat(4)]}
Z = mat(32)


def amul(u, v):
    out = 0
    while u:
        g = (u & -u).bit_length() - 1
        u &= u - 1
        row, w = MUL[g], v
        while w:
            h = (w & -w).bit_length() - 1
            w &= w - 1
            out ^= 1 << row[h]
    return out


def formal(word, r):
    M = [[(1 << E) if i == j else 0 for j in range(r)] for i in range(r)]
    for g, x, y in word:
        d = (1 << GEN[g]) | (1 << E)                       # [g] + 1
        for i in range(r):
            s = 0
            for k in range(r):
                if x >> k & 1:
                    s ^= amul(M[i][k], d)                  # (M x)(g+1)
            if s:
                for j in range(r):
                    if y >> j & 1:
                        M[i][j] ^= s
    return M


def formal_ok(word, r, w):
    zz = 1 << idx[Z]
    T = [[(zz if i < w else 1 << E) if i == j else 0 for j in range(r)] for i in range(r)]
    return formal(word, r) == T


# ---------- r x r binary matrices as bit masks (bit i*r+j) ----------
def mm(A, B, r):
    out = 0
    for i in range(r):
        for j in range(r):
            s = 0
            for k in range(r):
                s ^= (A >> (i * r + k)) & (B >> (k * r + j)) & 1
            out |= s << (i * r + j)
    return out


def rank_one(x, y, r=2):
    return sum(1 << (i * r + j) for i in range(r) for j in range(r) if x >> i & 1 and y >> j & 1)


def split(N, r=2):
    rows = [(N >> (i * r)) & ((1 << r) - 1) for i in range(r)]
    y = next(v for v in rows if v)
    x = sum(1 << i for i, v in enumerate(rows) if v)
    assert all(v in (0, y) for v in rows) and rank_one(x, y, r) == N
    return x, y


def diag(w, r):
    return sum(1 << (i * r + i) for i in range(w))


# ---------- degree-three quotient Q = F2<a,b,c>/(a^2,b^2,c^2,ac-ca,deg>=4) ----------
def reduce(m):
    if len(m) > 3:
        return None
    while 'ca' in m:
        m = m.replace('ca', 'ac')
    return None if any(m[i] == m[i + 1] for i in range(len(m) - 1)) else m


def q_image(word, r):
    st = {'': diag(r, r)}
    for g, x, y in word:
        N = rank_one(x, y, r)
        new = dict(st)
        for m, M in st.items():
            m2 = reduce(m + g)
            if m2 is not None:
                new[m2] = new.get(m2, 0) ^ mm(M, N, r)
        st = {m: M for m, M in new.items() if M}
    return st


def q_ok(word, r, w):
    P = diag(w, r)
    return q_image(word, r) == {'': diag(r, r), **({m: P for m in ('abc', 'acb', 'bac', 'cba')} if P else {})}


def prefix_profile(word, g):
    """Sum of g-couplings before each b, in product order."""
    out, s = [], 0
    for h, x, y in word:
        if h == g:
            s ^= rank_one(x, y)
        elif h == 'b':
            out.append(s)
    return out


def suffix_profile(word, g):
    return prefix_profile(word[::-1], g)[::-1]


def side_coeffs(bseq, P, r=2):
    """(ab, ba, aba, bab) for an a-profile P with zero a-total; the same formula gives
    (cb, bc, cbc, bcb) for a c-suffix profile with zero c-total (characteristic two)."""
    ab = ba = aba = bab = 0
    for j, (N, p) in enumerate(zip(bseq, P)):
        pn = mm(p, N, r)
        ab ^= pn
        ba ^= mm(N, p, r)
        aba ^= mm(pn, p, r)
        for k in range(j + 1, len(bseq)):
            bab ^= mm(mm(N, P[k] ^ p, r), bseq[k], r)
    return ab, ba, aba, bab


def cross_coeffs(bseq, P, Q, r=2):
    """(abc, cba) for zero a- and c-totals."""
    abc = cba = 0
    for N, p, q in zip(bseq, P, Q):
        abc ^= mm(mm(p, N, r), q, r)
        cba ^= mm(mm(q, N, r), p, r)
    return abc, cba


# ---------- fast r = 2 screen: per-position tables and profile keys ----------
PAR = [bin(m).count('1') & 1 for m in range(64)]


def side_tables(bseq, r=2):
    """tab[j][p] packs (ab, ba, aba, bab) contributions of position j when P_j = p.
    bab = sum_{j<k} N_j (P_j+P_k) N_k = sum_j (L_j P_j N_j + N_j P_j R_j)."""
    tab = []
    for j, N in enumerate(bseq):
        L = R = 0
        for i, M in enumerate(bseq):
            if i < j:
                L ^= M
            elif i > j:
                R ^= M
        tab.append([mm(p, N, r) | mm(N, p, r) << 4 | mm(mm(p, N, r), p, r) << 8
                    | (mm(mm(L, p, r), N, r) ^ mm(mm(N, p, r), R, r)) << 12 for p in range(16)])
    return tab


def side_value(tab, P):
    v = 0
    for t, p in zip(tab, P):
        v ^= t[p]
    return v


def key(bseq, P):
    """(U0, U1, W0, W1): bit j of U_s is (P_j x_j)_s, bit j of W_t is (y_j^T P_j)_t."""
    U, W = [0, 0], [0, 0]
    for j, (N, p) in enumerate(zip(bseq, P)):
        x, y = split(N)
        for s in range(2):
            u = w = 0
            for k in range(2):
                u ^= (p >> (2 * s + k)) & (x >> k) & 1      # (P x)_s
                w ^= (y >> k) & (p >> (2 * k + s)) & 1      # (y^T P)_s
            U[s] |= u << j
            W[s] |= w << j
    return U[0], U[1], W[0], W[1]


def key_cross(kp, kq):
    """(abc, cba) from keys: abc_st = sum_j u_j(P)_s w_j(Q)_t, cba_st = sum_j u_j(Q)_s w_j(P)_t."""
    abc = cba = 0
    for s in range(2):
        for t in range(2):
            abc |= PAR[kp[s] & kq[2 + t]] << (2 * s + t)
            cba |= PAR[kq[s] & kp[2 + t]] << (2 * s + t)
    return abc, cba


_SOL = {}


def _sol(u0, u1, e0, e1):
    """6-bit masks m with parity(u0 & m) = e0 and parity(u1 & m) = e1."""
    k = (u0, u1, e0, e1)
    if k not in _SOL:
        _SOL[k] = [m for m in range(64) if PAR[u0 & m] == e0 and PAR[u1 & m] == e1]
    return _SOL[k]


def key_pairs(akeys, ckeys=None, target=(9, 9)):
    """All (ka, kc) with key_cross(ka, kc) == target. The abc half fixes kc's W masks to an
    affine solution set of ka's U masks, so look kc up by (W0, W1) and confirm the cba half."""
    ckeys = akeys if ckeys is None else ckeys
    abc = target[0]
    byW = {}
    for k in ckeys:
        byW.setdefault(k[2:], []).append(k)
    for ka in akeys:
        for m0 in _sol(ka[0], ka[1], abc & 1, abc >> 2 & 1):
            for m1 in _sol(ka[0], ka[1], abc >> 1 & 1, abc >> 3 & 1):
                for kc in byW.get((m0, m1), ()):
                    if key_cross(ka, kc) == target:
                        yield ka, kc


def check_quotient_homomorphism():
    """Define phi on UT4(F2) by BFS words in a, b, c with phi(g) = 1 + g, and check
    phi(g) phi(h) = phi(gh) for all 4096 pairs in Q, plus phi(z) = 1+abc+acb+bac+cba."""
    def qmul(u, v):
        out = set()
        for m in u:
            for n in v:
                k = reduce(m + n)
                if k is not None:
                    out ^= {k}
        return frozenset(out)

    phi, frontier = {E: frozenset({''})}, [E]
    while frontier:
        nxt = []
        for g in frontier:
            for letter, s in GEN.items():
                h = MUL[g][s]
                if h not in phi:
                    phi[h] = qmul(phi[g], frozenset({'', letter}))
                    nxt.append(h)
        frontier = nxt
    assert len(phi) == 64
    assert all(phi[GEN[x]] == frozenset({'', x}) for x in 'abc')
    assert phi[idx[Z]] == frozenset({'', 'abc', 'acb', 'bac', 'cba'})
    n = 0
    for g in range(64):
        for h in range(64):
            assert qmul(phi[g], phi[h]) == phi[MUL[g][h]], (g, h)
            n += 1
    return n


# ---------- shared enumeration helpers ----------
def couplings(r):
    return [(x, y) for x in range(1, 1 << r) for y in range(1, 1 << r)]


def make_seqs(r, kmax):
    """seqs[k][d]: ordered k-tuples of couplings summing to d."""
    seqs = [dict() for _ in range(kmax + 1)]
    for k in range(kmax + 1):
        for t in itertools.product(couplings(r), repeat=k):
            d = 0
            for x, y in t:
                d ^= rank_one(x, y, r)
            seqs[k].setdefault(d, []).append(t)
    return seqs


def profiles(nb, n, seqs):
    """All prefix-sum profiles (P_1..P_nb) of n couplings in nb+1 gaps with zero total."""
    out = set()

    def rec(gap, left, s, acc):
        if gap == nb:                                      # last gap must cancel the running sum
            if s in seqs[left]:
                out.add(tuple(acc))
            return
        for k in range(left + 1):
            for d in seqs[k]:
                rec(gap + 1, left - k, s ^ d, acc + [s ^ d])
    rec(0, n, 0, [])
    return sorted(out)


def gap_choices(P, n, seqs):
    """All per-gap coupling tuples realising prefix profile P with n couplings in total."""
    sums = [P[0]] + [P[j] ^ P[j - 1] for j in range(1, len(P))] + [P[-1]] if P else [0]
    res = []

    def rec(g, left, acc):
        if g == len(sums):
            if left == 0:
                res.append(acc)
            return
        for k in range(left + 1):
            for t in seqs[k].get(sums[g], ()):
                rec(g + 1, left - k, acc + [t])
    rec(0, n, [])
    return res


def shuffles(A, C):
    """All interleavings of a-tuple A and c-tuple C within one gap."""
    n = len(A) + len(C)
    out = []
    for pos in itertools.combinations(range(n), len(A)):
        ia, ic, w = iter(A), iter(C), []
        for i in range(n):
            w.append(('a',) + next(ia) if i in pos else ('c',) + next(ic))
        out.append(w)
    return out


def expand(bt, P, Q, na, nc, seqs, r, w, stats, sols, seen=None):
    """Every word with b-sequence bt, a-prefix profile P and c-suffix profile Q. Each is
    checked against the full quotient and, independently, the full formal endpoint;
    with `seen`, words are only collected (completeness tests)."""
    nb = len(bt)
    for ga in gap_choices(list(P), na, seqs):
        for gc in gap_choices(list(Q), nc, seqs):          # zero total: suffix sums equal prefix sums
            for parts in itertools.product(*[shuffles(ga[j], gc[j]) for j in range(nb + 1)]):
                word = []
                for j in range(nb + 1):
                    word += parts[j]
                    if j < nb:
                        word.append(('b',) + split(bt[j], r))
                stats['words'] += 1
                if seen is not None:
                    seen.append(word)
                    continue
                stats['q_pass'] += q_ok(word, r, w)
                if formal_ok(word, r, w):
                    stats['formal_pass'] += 1
                    sols.append(tuple(word))


def gl(r):
    I = diag(r, r)
    inv = {}
    for g in range(1 << (r * r)):
        for h in range(1 << (r * r)):
            if mm(g, h, r) == I:
                inv[g] = h
    return inv


def middle_sequences(r, nb, symmetric):
    """Zero-sum b-sequences; with symmetric=True only GL_r-conjugation-minimal ones."""
    inv = gl(r)
    R1 = sorted(rank_one(x, y, r) for x, y in couplings(r))
    for bt in itertools.product(R1, repeat=nb):
        tot = 0
        for N in bt:
            tot ^= N
        if tot:
            continue
        if symmetric and any(tuple(mm(mm(g, N, r), h, r) for N in bt) < bt for g, h in inv.items()):
            continue
        yield bt


# ---------- reference driver (any small r, slow formulas) ----------
def search(r, w, counts, log=None):
    na, nb, nc = counts
    seqs = make_seqs(r, max(na, nc))
    PA, PC = profiles(nb, na, seqs), profiles(nb, nc, seqs)
    target = diag(w, r)
    stats = dict(canonical=0, a_pass=0, c_pass=0, pairs=0, words=0, q_pass=0, formal_pass=0)
    sols = []
    for bt in middle_sequences(r, nb, w == r):             # conjugation fixes the target only if P = I
        stats['canonical'] += 1
        SA = [P for P in PA if side_coeffs(bt, P, r) == (0, 0, 0, 0)]
        SC = [Q for Q in PC if side_coeffs(bt, Q, r) == (0, 0, 0, 0)]
        stats['a_pass'] += len(SA)
        stats['c_pass'] += len(SC)
        for P in SA:
            for Q in SC:
                if cross_coeffs(bt, P, Q, r) == (target, target):
                    stats['pairs'] += 1
                    expand(bt, P, Q, na, nc, seqs, r, w, stats, sols)
    if log is not None:
        log.update(stats)
    return sols


# ---------- fast driver for r = w = 2, counts (4, 6, 4) ----------
def fast_search(log=None, limit=None, bseqs=None, want=None, seen=None):
    """want = (a-side value, c-side value, (abc, cba)); the default is the two-target
    endpoint. Other `want`/`bseqs` values exist only for the completeness tests."""
    r = w = 2
    na, nb, nc = 4, 6, 4
    seqs = make_seqs(r, 4)
    PA = profiles(nb, na, seqs)                           # c-suffix profiles form the same set
    wa, wc, cross = want or (0, 0, (9, 9))
    stats = dict(canonical=0, profiles=len(PA), side_pass=0, keys=0, key_pairs=0, pairs=0,
                 words=0, q_pass=0, formal_pass=0)
    sols = []
    for n, bt in enumerate(bseqs or middle_sequences(r, nb, True)):
        if limit is not None and n >= limit:
            break
        stats['canonical'] += 1
        tab = side_tables(bt)
        ga, gc = {}, {}
        for P in PA:
            v = side_value(tab, P)                         # same formula serves the c side (see side_coeffs)
            if v == wa:
                ga.setdefault(key(bt, P), []).append(P)
            if v == wc:
                gc.setdefault(key(bt, P), []).append(P)
        stats['side_pass'] += sum(map(len, ga.values()))
        stats['keys'] += len(ga)
        for ka, kc in key_pairs(ga, gc, cross):
            stats['key_pairs'] += 1
            for P in ga[ka]:
                for Q in gc[kc]:
                    stats['pairs'] += 1
                    expand(bt, P, Q, na, nc, seqs, r, w, stats, sols, seen)
    if log is not None:
        log.update(stats)
    return sols


if __name__ == '__main__':
    import json, sys, time
    t = time.time()
    stats = {}
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else None
    sols = fast_search(stats, lim)
    stats['solutions'] = len(sols)
    stats['seconds'] = round(time.time() - t, 1)
    print(json.dumps(stats))
    for s in sols[:5]:
        print(s)
