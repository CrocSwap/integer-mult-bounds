# SIXHEAVY impl A: E8 lines, labels (CARRIER lib), all w-flat masks via dual RREF, parabolic Off sets, cover DFS.
import sys, itertools, pickle, os
sys.path.insert(0, '../CARRIER')
from lib import lines, lab, simple, solve, n
coef = [[int(v) for v in solve(simple, l)] for l in lines]   # simple-root coords (canonical sign)
LAB = lab
def Z(u):  # mask of lines whose label is orthogonal (F2) to dual vector u
    m = 0
    for i, l in enumerate(LAB):
        if bin(u & l).count('1') % 2 == 0: m |= 1 << i
    return m
ZM = [Z(u) for u in range(512)]
def subspaces(k, N=9):
    """all k-dim subspaces of F2^N as lists of basis rows (RREF)"""
    for piv in itertools.combinations(range(N), k):
        free = []
        for r, p in enumerate(piv):
            for c in range(p + 1, N):
                if c not in piv: free.append((r, c))
        for bits in itertools.product((0, 1), repeat=len(free)):
            rows = [1 << p for p in piv]
            for (r, c), b in zip(free, bits):
                if b: rows[r] |= 1 << c
            yield rows
def flats(w):
    """distinct nonempty masks Lambda(V), dim V = w (V = kernel of 9-w dual rows)"""
    fn = '../SIXHEAVY/flats%d.pkl' % w
    if os.path.exists(fn): return pickle.load(open(fn, 'rb'))
    S = set()
    k = 9 - w
    for rows in subspaces(k):
        m = (1 << n) - 1
        for r in rows: m &= ZM[r]
        if m: S.add(m)
    S = sorted(S)
    pickle.dump(S, open(fn, 'wb'))
    return S
def off_parab(J):
    """Off set of h generic in the dominant face of standard parabolic J (subset of simple indices 0..7)"""
    m = 0
    for i, c in enumerate(coef):
        if any(c[k] != 0 for k in range(8) if k not in J): m |= 1 << i
    return m
pc = lambda x: bin(x).count('1')
def maximal(ms):
    ms = sorted(set(ms), key=pc, reverse=True); out = []
    for m in ms:
        if not any((m | o) == o for o in out): out.append(m)
    return out
def cover(O, dims, FL, budget=None):
    """can O be covered by flats of the given dims? FL[w] = list of masks. returns a witness list or None"""
    dims = sorted(dims, reverse=True)
    cand = {w: maximal([m & O for m in FL[w]]) for w in set(dims)}
    best = {w: max(map(pc, cand[w])) for w in cand}
    def rec(U, rem, chosen):
        if U == 0: return chosen
        if not rem: return None
        # capacity bound with per-dim max restricted to U
        if sum(max(pc(m & U) for m in cand[w]) for w in rem) < pc(U): return None
        # branch on the line of U in fewest candidates of remaining dims
        low = U & -U; bestl = None; bc = 10**9
        x = U
        while x:
            b = x & -x; x ^= b
            c = sum(1 for w in set(rem) for m in cand[w] if m & b)
            if c < bc: bc, bestl = c, b
            if c == 0: return None
        tried = set()
        for w in sorted(set(rem), reverse=True):
            r2 = list(rem); r2.remove(w)
            for m in cand[w]:
                if m & bestl:
                    mm = m & U
                    if (w, mm) in tried: continue
                    tried.add((w, mm))
                    res = rec(U & ~m, r2, chosen + [(w, m)])
                    if res is not None: return res
        return None
    return rec(O, dims, [])
