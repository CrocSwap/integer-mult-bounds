"""D2. The coupled (cross-level) cover relaxation with a helper-count objective, on the complex unit P112 and the bit unit E8.

D1 bounds the number of helper registers by a cut at one level of the frame lattice (the source end or the terminal
end).  Here the cuts at all levels are coupled through the register chains.

Model.  Let K be the top rank (K = 9 for P112 inside F_2^9, K = 8 for E8).  A register has a class and a chain of frame ranks:
  X (source)  : starts at rank 1, ends at rank K, stops at any subset of {2, ..., K-1};
  Y (target)  : starts at rank 0, ends at rank K-1 (the frame u_q^perp), stops at any subset of {1, ..., K-2};
  H (helper)  : starts at a rank s0 (0 for the bit unit, 0..5 for the complex unit) and ends at rank K, stops at any subset of
                {s0+1, ..., K-1}.
A hop from rank a to rank b > a carries one rank-one term of the transfer matrix, supported on (sources in a) x (terminals in
b^perp); it serves every level d with a < d <= b.  Its area (number of orthogonal source/terminal pairs it can serve) is at
most ell_a * ell_{K-b}, where ell_i is the largest number of source points in a subspace of rank i, further capped by
  * the exact unit rectangle cap M(d) of every level d spanned by the hop (largest area of a product (P cap a) x (P cap c) of
    mutually orthogonal subspaces a, c with dim a = d-1, dim c = K-d),
  * the largest section of a source's readers by a hyperplane (hops leaving rank 1) and of a terminal's sources (hops entering rank K-1),
  * for sink-only targets (a target is only a destination, its hop serves one terminal column) ell_a x 1.
Variables x_t >= 0 (integer for the ILP): the number of registers of type t = (class, chain).  Constraints:
  (level)    for every level d = 2..K-1:  sum_t area_t(d) x_t >= P, where P is the number of orthogonal pairs;
  (counts)   exactly nX registers of class X, exactly nY of class Y;
  (source)   every source is served by a multiset of registers standing at its rank-1 frame whose first hops are sections of its
             readers: at least cmin sections, any two cover at most u2 readers, together at least NT_src readers (patterns of
             registers, linked to the first hops of the chains by >= );
  (terminal) the same for the sources of every terminal q at the rank-(K-1) end: the registers entering the frame q^perp
             must cover the sources in q^perp by sections of q^perp (the target's own register contributes the section of
             the hop that enters its final frame; pseudo-targets at the 9 punctured lines of the bit unit have no own register).
Objective: the number of helper registers.  Scope: this is a relaxation under the assumptions above (frames are arbitrary
subspaces, the only drops are the decoder copies, the areas are exact maxima over the geometry); it is not a proof about every
conceivable design.  The shipped words of PR #555 (bit) and PR #569 (complex) are feasible points of it.

Claims.  (a) the optimum of the coupled model equals the single-cut bounds of D1 (212, 138 for the bit unit; 107, 0 for the
complex unit): coupling adds nothing; (b) exact geometry inputs (ell_k and unit caps of P112); (c) the shipped words are
feasible; (d) with the data ladders of the shipped words fixed, the least number of helpers is 222 (bit) and 146 / 123 (complex).
Upstream: PR #555 (bit word), PR #531 (P112 and its word), PR #569 (complex word with width-7 gauges).
"""
import sys

sys.dont_write_bytecode = True

import itertools
from collections import Counter

import numpy as np
from scipy.optimize import LinearConstraint, Bounds, milp
from scipy.sparse import lil_matrix, csr_matrix

import d_geometry as dg
from report import VENDOR, check, finish, load_json

# ---------------------------------------------------------------------------------------------------------------
# Expected values (hard-coded; each is the exact outcome of the computation below)
# ---------------------------------------------------------------------------------------------------------------
EXPECTED = dict(
    cx_ell=[1, 2, 4, 8, 12, 20, 36, 64, 112],             # ell_k, k = 1..9: most ports in a k-dimensional subspace of F_2^9
    cx_nsubspaces=8283458,                                 # all subspaces of F_2^9 (sum of the Gaussian binomials)
    cx_unitcaps={2: 32, 3: 32, 4: 32, 5: 36, 6: 32, 7: 32, 8: 32},     # exact rectangle cap per level d = 2..8
    bit_ell=[1, 3, 6, 12, 20, 36, 63],                     # ell_i, i = 1..7: lines in the largest rank-i flat (A1, A2, A3, D4, D5, E6, E7)
    bit_sink=212, bit_strict=138, cx_sink=107, cx_strict=0,          # integer optima of the coupled model (helpers)
    lp=dict(bit_sink=2331 / 11, bit_strict=138.0, cx_sink=106.4, cx_strict=0.0),     # their LP relaxations
    ship_fixed_bit=222, ship_fixed_bit_strict=222, ship_fixed_cx_sink=146, ship_fixed_cx_strict=123,
)
TIME_LIMIT = 300            # seconds per ILP; every ILP below proves optimality in well under a second


# ---------------------------------------------------------------------------------------------------------------
# Exact geometry of P112: ell_k and the unit rectangle caps (exhaustive over all subspaces of F_2^9)
# ---------------------------------------------------------------------------------------------------------------
def cx_ell(orth_lo, orth_hi):
    """ell_k = largest number of ports in a k-dimensional subspace u of F_2^9, k = 0..9: u = W^perp for the (9-k)-dimensional
    subspace W spanned by the rows of an echelon basis; the ports in u are those orthogonal to every row.  Returns (ell,
    number of subspaces enumerated)."""
    ell, total = {}, 0
    for m in range(0, 10):
        best = 0
        for rows in dg.subspace_bases(m):
            total += len(rows)
            if m == 0:
                best = len(dg.cx_ports())
                continue
            lo = np.bitwise_and.reduce(orth_lo[rows], axis=1)
            hi = np.bitwise_and.reduce(orth_hi[rows], axis=1)
            best = max(best, int((dg.popcount(lo) + dg.popcount(hi)).max()))
        ell[9 - m] = best
    return [ell[k] for k in range(1, 10)], total


def cx_unit_caps(orth_lo, orth_hi):
    """M(d) for d = 2..8: the largest |P cap a| * |P cap c| over orthogonal subspaces a, c of F_2^9 with dim a = d-1,
    dim c = 9-d, c a hyperplane of a^perp.  Enumerated exhaustively over a for dim a = 1..4 (d = 2..5); the pair (a, c) is
    symmetric in its two members (a is a hyperplane of c^perp as well), so M(d) = M(10-d) gives d = 6, 7, 8."""
    ports = dg.cx_ports()
    isport = np.zeros(512, dtype=bool)
    isport[list(ports)] = True
    lo1, hi1 = orth_lo[1:], orth_hi[1:]                       # for w = 1..511
    caps = {}
    for p in (1, 2, 3, 4):
        best = 0
        for rows in dg.subspace_bases(p, chunk=1 << 13):
            n = len(rows)
            vs = np.zeros((n, 1), dtype=np.int64)             # all vectors of the span of each basis (column 0 is the zero vector)
            for i in range(p):
                vs = np.concatenate([vs, vs ^ rows[:, i:i + 1]], axis=1)
            na = isport[vs[:, 1:]].sum(axis=1)                # ports in a
            olo = np.bitwise_and.reduce(orth_lo[rows], axis=1)
            ohi = np.bitwise_and.reduce(orth_hi[rows], axis=1)    # ports in a^perp
            cc = dg.popcount(lo1[None, :] & olo[:, None]) + dg.popcount(hi1[None, :] & ohi[:, None])   # ports in a^perp cap w^perp
            np.put_along_axis(cc, vs[:, 1:] - 1, 0, axis=1)   # w in span(a) does not cut a hyperplane out of a^perp
            best = max(best, int((na * cc.max(axis=1)).max()))
        caps[p + 1] = best
    for d in (6, 7, 8):
        caps[d] = caps[10 - d]
    return caps


# ---------------------------------------------------------------------------------------------------------------
# The coupled cover model
# ---------------------------------------------------------------------------------------------------------------
class Spec:
    """parameters of one unit: K, ell[0..K], hstarts, capS(j), capT(i), ymode ('sink' or 'strict'), cmin, u2, NT_src, NT_top,
    P, nX, nY, nsrc, nterm and optionally unitcap {level: cap}."""


def feasible(caps, cmin, NT, u2):
    """can sections with these caps serve NT readers: at least cmin of them, and (if u2 is given) any two cover at most u2."""
    caps = sorted(caps, reverse=True)
    if len(caps) < cmin:
        return False
    top2 = sum(caps[:2])
    if u2 is not None:
        top2 = min(top2, u2)
    return top2 + sum(caps[2:]) >= NT


def minimal_patterns(fixed, itemcaps, cmin, NT, u2, maxextra=4):
    """minimal multisets of optional items (key -> cap) that, together with the fixed items, can serve NT readers; minimal
    means removing any optional item destroys feasibility.  Returns the list of item tuples."""
    keys = [k for k in itemcaps if itemcaps[k] > 0]
    base = [c for _, c in fixed]
    out = []
    for r in range(0, maxextra + 1):
        for combo in itertools.combinations_with_replacement(keys, r):
            if not feasible(base + [itemcaps[k] for k in combo], cmin, NT, u2):
                continue
            if all(not feasible(base + [itemcaps[k] for t, k in enumerate(combo) if t != idx], cmin, NT, u2) for idx in range(len(combo))):
                out.append(combo)
    return out


class CoverModel:
    def __init__(self, spec):
        self.sp = sp = spec
        K = sp.K
        self.types = []
        for ch in self._chains(1, K, 2, K - 1):
            self.types.append(('X', ch))
        for ch in self._chains(0, K - 1, 1, K - 2):
            self.types.append(('Y', ch))
        for s0 in sp.hstarts:
            for ch in self._chains(s0, K, s0 + 1, K - 1):
                self.types.append(('H', ch))
        self.index = {t: i for i, t in enumerate(self.types)}

    @staticmethod
    def _chains(start, end, lo, hi):
        mids = list(range(lo, hi + 1))
        return [(start,) + T + (end,) for k in range(len(mids) + 1) for T in itertools.combinations(mids, k)]

    def area(self, cls, ch, d):
        """largest number of orthogonal pairs the hop of the chain that spans level d can serve (0 if no hop spans d)."""
        sp = self.sp
        K = sp.K
        for a, b in zip(ch, ch[1:]):
            if a < d <= b:
                if a == 0:
                    return 0.0
                if cls == 'Y' and sp.ymode == 'sink':
                    return float(min(sp.ell[a], sp.capT(a)))
                ar = sp.ell[a] * sp.ell[K - b]
                uc = getattr(sp, 'unitcap', None)
                if uc:
                    ar = min(ar, min(uc.get(dd, 0) for dd in range(a + 1, b + 1)))
                if a == 1:
                    ar = min(ar, sp.capS(b))
                if b == K - 1:
                    ar = min(ar, sp.capT(a))
                return float(ar)
        return 0.0

    @staticmethod
    def first_hop(ch):
        """target rank of the hop leaving rank 1 (None if the chain has no rank-1 stop)."""
        return ch[ch.index(1) + 1] if 1 in ch[:-1] else None

    def last_hop(self, ch):
        """source rank of the hop entering rank K-1 (None if the chain never enters rank K-1)."""
        K = self.sp.K
        return ch[ch.index(K - 1) - 1] if (K - 1) in ch[1:] else None

    def build(self, xfix=None):
        sp = self.sp
        K, T = sp.K, self.types
        n = len(T)
        j1 = [self.first_hop(ch) for _, ch in T]
        i7 = [self.last_hop(ch) for _, ch in T]
        srcpat = []                                    # (rank of X's hop, tuple of other (class, hop rank) items)
        for jX in range(2, K + 1):
            capX = sp.capS(jX) if jX < K else 0
            if sp.ymode == 'sink':
                hk = [('H', j) for j in range(2, K)]
                for r in range(0, 4):
                    for combo in itertools.combinations_with_replacement(hk, r):
                        caps = [capX] + [sp.capS(j) for _, j in combo]
                        for a in range(0, int(sp.NT_src) + 1):                  # a sink-only targets, one reader each
                            if not feasible(caps + [1] * a, sp.cmin, sp.NT_src, sp.u2):
                                continue
                            ok = not (a > 0 and feasible(caps + [1] * (a - 1), sp.cmin, sp.NT_src, sp.u2))
                            for idx in range(len(combo)):
                                c2 = [capX] + [sp.capS(j) for t_, (_, j) in enumerate(combo) if t_ != idx] + [1] * a
                                if feasible(c2, sp.cmin, sp.NT_src, sp.u2):
                                    ok = False
                                    break
                            if ok:
                                srcpat.append((jX, tuple(combo) + tuple([('Y', 2)] * a)))
                            break
            else:
                optional = {}
                for j in range(2, K + 1):
                    optional[('H', j)] = sp.capS(j) if j < K else 0
                    optional[('Y', j)] = sp.capS(j) if j < K else 0
                for combo in minimal_patterns([(('X', jX), capX)], optional, sp.cmin, sp.NT_src, sp.u2):
                    srcpat.append((jX, combo))
        toppat = []                                    # (has own target section, its rank, tuple of other (class, hop rank) items)
        for hasY in (True, False):
            for iY in (range(0, K - 1) if hasY else [None]):
                fixed = [(('Y', iY), sp.capT(iY))] if hasY else []
                optional = {}
                for i in range(1, K - 1):
                    optional[('H', i)] = sp.capT(i)
                    optional[('X', i)] = sp.capT(i)
                for combo in minimal_patterns(fixed, optional, sp.cmin, sp.NT_top, sp.u2):
                    toppat.append((hasY, iY, combo))
        ns, nt = len(srcpat), len(toppat)
        N = n + ns + nt
        c = np.zeros(N)
        for t, (cls, ch) in enumerate(T):
            c[t] = 1.0 if cls == 'H' else 0.0
        rows, lo, hi = [], [], []

        def addrow(coefs, l, h):
            rows.append(coefs)
            lo.append(l)
            hi.append(h)

        for d in range(2, K):                                                    # level covers
            addrow({t: self.area(cls, ch, d) for t, (cls, ch) in enumerate(T) if self.area(cls, ch, d) > 0}, sp.P, np.inf)
        addrow({t: 1.0 for t, (cls, _) in enumerate(T) if cls == 'X'}, sp.nX, sp.nX)
        addrow({t: 1.0 for t, (cls, _) in enumerate(T) if cls == 'Y'}, sp.nY, sp.nY)
        addrow({n + k: 1.0 for k in range(ns)}, sp.nsrc, sp.nsrc)                # source patterns
        for cls in ('X', 'H', 'Y'):
            for j in range(2, K + 1):
                co = {t: 1.0 for t, (cl, _) in enumerate(T) if cl == cls and j1[t] == j}
                for k, (jX, combo) in enumerate(srcpat):
                    m = (1 if (cls == 'X' and jX == j) else 0) + sum(1 for it in combo if it == (cls, j))
                    if m:
                        co[n + k] = co.get(n + k, 0) - m
                addrow(co, 0, np.inf)
        addrow({n + ns + k: 1.0 for k in range(nt) if toppat[k][0]}, sp.nY, sp.nY)           # terminal patterns
        addrow({n + ns + k: 1.0 for k in range(nt) if not toppat[k][0]}, sp.nterm - sp.nY, sp.nterm - sp.nY)
        for cls in ('X', 'H', 'Y'):
            for i in range(0, K - 1):
                co = {t: 1.0 for t, (cl, _) in enumerate(T) if cl == cls and i7[t] == i}
                for k, (hasY, iY, combo) in enumerate(toppat):
                    m = (1 if (cls == 'Y' and hasY and iY == i) else 0) + sum(1 for it in combo if it == (cls, i))
                    if m:
                        co[n + ns + k] = co.get(n + ns + k, 0) - m
                if co:
                    addrow(co, 0, np.inf)
        if xfix:
            for t, v in xfix.items():
                addrow({t: 1.0}, v, v)
        A = lil_matrix((len(rows), N))
        for r, co in enumerate(rows):
            for k, v in co.items():
                A[r, k] = v
        self.c, self.A, self.lo, self.hi, self.N = c, csr_matrix(A), np.array(lo, float), np.array(hi, float), N
        self.npat = (ns, nt)

    def solve(self, integer, xfix=None):
        """minimise the number of helpers; returns scipy's result.  Integer solves use mip_rel_gap = 0."""
        self.build(xfix)
        cons = LinearConstraint(self.A, lb=self.lo, ub=self.hi)
        integ = np.ones(self.N) if integer else np.zeros(self.N)
        return milp(self.c, constraints=[cons], integrality=integ, bounds=Bounds(0, np.inf),
                    options=dict(time_limit=TIME_LIMIT, disp=False, mip_rel_gap=0.0))


def optimum(model, integer, xfix=None):
    """(value, proved) where proved says: solver status 'optimal', and for an ILP the dual bound equals the objective."""
    res = model.solve(integer, xfix)
    if res.status != 0 or res.x is None:
        return None, False
    proved = True
    if integer:
        proved = abs(res.fun - round(res.fun)) < 1e-6 and (res.mip_dual_bound is None or res.mip_dual_bound >= res.fun - 1e-6)
    return float(res.fun), proved


# ---------------------------------------------------------------------------------------------------------------
# Unit specifications
# ---------------------------------------------------------------------------------------------------------------
def e8_geometry():
    """cover parameters of the bit unit from the exact E7 flat lattice: ell_i = lines in the largest rank-i flat of E7 (for
    i <= 7 the largest rank-i flats of E8 have the same sizes: the largest root subsystems of rank i are A1, A2, A3, D4, D5, E6, E7
    by the classification of parabolic subsystems; only the E7 part is enumerated here), u2 = largest union of two hyperplane
    flats, cmin = cover number."""
    idx, lattice = dg.e7_flats()
    ell = [max(m.bit_count() for m in lattice[k]) for k in range(1, 7)] + [63]
    hyp = lattice[6]
    words = dg.masks_to_words(hyp, 63)
    full = dg.masks_to_words([(1 << 63) - 1], 63)[0]
    u2 = dg.max_pair_union(words)
    big = dg.masks_to_words([m for m in hyp if m.bit_count() >= 21], 63)
    cmin = 2 if u2 == 63 else (3 if dg.find_triple_cover(big, full) is not None else None)
    return ell, u2, cmin


def bit_spec(ymode, ell, u2, cmin):
    E = dg.e8()
    K = 8
    G, isl = E['G'], E['isl']
    nlive_perp = [int(((G[q] == 0) & isl).sum()) for q in range(120)]
    sp = Spec()
    sp.K, sp.ell = K, [0] + list(ell) + [120]
    sp.hstarts = [0]
    sp.capS = lambda j: sp.ell[K - j]
    sp.capT = lambda i: sp.ell[i]
    sp.ymode, sp.cmin, sp.u2 = ymode, cmin, u2
    sp.NT_src, sp.NT_top = 63, min(nlive_perp)
    sp.P = sum(int((G[E['srcid'][i]] == 0).sum()) for i in range(111))
    sp.nX = sp.nY = sp.nsrc = 111
    sp.nterm = 120
    return sp


def cx_spec(ymode, ell, unitcap, sec, cmin):
    K = 9
    sp = Spec()
    sp.K, sp.ell = K, [0] + list(ell)
    sp.hstarts = [0, 1, 2, 3, 4, 5]
    sp.capS = lambda j: min(sp.ell[K - j], sec) if j < K else 0
    sp.capT = lambda i: min(sp.ell[i], sec)
    sp.unitcap = unitcap
    sp.ymode, sp.cmin, sp.u2 = ymode, cmin, None
    sp.NT_src = sp.NT_top = 52
    sp.P = 112 * 52
    sp.nX = sp.nY = sp.nsrc = sp.nterm = 112
    return sp


# ---------------------------------------------------------------------------------------------------------------
# Chains of the shipped words
# ---------------------------------------------------------------------------------------------------------------
def bit_ship_counts():
    """(class, chain of frame ranks) -> number of registers, for the 661 registers of the word of PR #555."""
    w, dims, path = dg.bit_paths()
    v = w['v']
    cnt = Counter()
    for r, p in enumerate(path):
        cnt[('X' if r < v else 'Y' if r < 2 * v else 'H', tuple(dims[f] for f in p))] += 1
    return cnt, w['R']


def cx_ship_counts():
    """the same for the word of PR #569 with width-7 gauges, without its 8 rank-8 centres (which are not helpers of the
    model).  The chain of a register is the sequence of ranks of the frames it occupies during the phases A and B and at the
    end (sources and helpers end in the full frame, targets in the perp of their port)."""
    g = dg.gk()
    word = load_json(VENDOR / 'pr569' / 'width7-eight-FULL-WORD.json.gz')
    V = 112
    R = word['report']['R']
    n = 2 * V + R
    P = word['ports']
    start_extra = word.get('start_extra', {})
    cur = {}
    for r in range(n):
        if r < V:
            cur[r] = (P[r],)
        elif r >= 2 * V:
            cur[r] = g.basis(start_extra[str(r)]) if str(r) in start_extra else ()
        else:
            cur[r] = ()
    chain = {r: [len(cur[r])] for r in range(n)}

    def climb(r, F):
        F = g.basis(F)
        if cur[r] != F:
            chain[r].append(len(F))
            cur[r] = F

    for seq in (word['A'], word['B']):
        for e in seq:
            for r in [e[1]] + ([e[2]] if e[0] == 'add' else []):
                climb(r, e[-1])
    for r in range(n):
        climb(r, g.FULL if (r < V or r >= 2 * V) else g.perp(P[r - V]))
    ctr = set(word['centers'])
    cnt = Counter()
    for r in range(n):
        if r in ctr:
            continue
        cnt[('X' if r < V else 'Y' if r < 2 * V else 'H', tuple(chain[r]))] += 1
    return cnt, R, len(ctr)


def fix_all(model, cnt):
    """x fixed to the counts cnt for every type (missing types are fixed to 0); returns (xfix, types of cnt not in the model)."""
    missing = [k for k in cnt if k not in model.index]
    return {i: cnt.get(t, 0) for i, t in enumerate(model.types)}, missing


def fix_data(model, cnt):
    """x fixed to the shipped counts for the data classes X and Y only."""
    missing = [k for k in cnt if k[0] in 'XY' and k not in model.index]
    return {i: cnt.get(t, 0) for i, t in enumerate(model.types) if t[0] in 'XY'}, missing


def main():
    ports = dg.cx_ports()
    _, olo, ohi = dg.orth_tables(ports)

    # ===== exact geometry of P112 ==============================================================================
    ell, nsub = cx_ell(olo, ohi)
    check('D2.cx-ell', ell == EXPECTED['cx_ell'] and nsub == EXPECTED['cx_nsubspaces'],
          'largest number of ports in a k-dimensional subspace of F_2^9, k = 1..9: %s (all %d subspaces enumerated)' % (ell, nsub))
    caps = cx_unit_caps(olo, ohi)
    check('D2.cx-unitcaps', caps == EXPECTED['cx_unitcaps'],
          'exact rectangle cap per level d = 2..8: %s (the product ell_(d-1) x ell_(9-d) = 8 x 8 = 64 at d = 5 is not attained)'
          % [caps[d] for d in range(2, 9)])
    cv = dg.cx_section_covers()
    sec, cmin_cx = cv['max_all'], (2 if cv['cover2_all'] == 112 else None)
    assert sec == caps[2] == 32 and cmin_cx == 2

    ell_bit, u2, cmin_bit = e8_geometry()
    check('D2.bit-ell', ell_bit == EXPECTED['bit_ell'],
          'largest flat of rank i = 1..7 of E7 (exhaustive census of the flats): %s lines = A1, A2, A3, D4, D5, E6, E7; E8 itself has 120 lines; '
          'two hyperplane flats cover at most %d of 63 lines, cover number %d' % (ell_bit, u2, cmin_bit))

    # ===== the coupled model: count-minimal helpers =============================================================
    results = {}
    for name, mk in (('bit', lambda y: bit_spec(y, ell_bit, u2, cmin_bit)), ('cx', lambda y: cx_spec(y, ell, caps, sec, cmin_cx))):
        for ymode in ('sink', 'strict'):
            m = CoverModel(mk(ymode))
            lp, _ = optimum(m, False)
            ip, proved = optimum(m, True)
            results[(name, ymode)] = (lp, ip, proved, m)
    leftover_bit, leftover_cx = 63 - u2, 52 - sec
    sc = {('bit', 'sink'): None, ('bit', 'strict'): None, ('cx', 'sink'): None, ('cx', 'strict'): None}
    s, t = dg.single_cut_bounds(111, 120, leftover_bit, cmin_bit)
    sc[('bit', 'sink')], sc[('bit', 'strict')] = s, t
    s, t = dg.single_cut_bounds(112, 112, leftover_cx, cmin_cx)
    sc[('cx', 'sink')], sc[('cx', 'strict')] = s, t
    labels = {('bit', 'sink'): ('D2.bit-sink', 'bit_sink', 'bit unit, sink-only targets'),
              ('bit', 'strict'): ('D2.bit-strict', 'bit_strict', 'bit unit, strict targets'),
              ('cx', 'sink'): ('D2.cx-sink', 'cx_sink', 'complex unit, sink-only targets'),
              ('cx', 'strict'): ('D2.cx-strict', 'cx_strict', 'complex unit, strict targets')}
    for key, (cid, exp, text) in labels.items():
        lp, ip, proved, m = results[key]
        ok = (proved and round(ip) == EXPECTED[exp] == sc[key] and abs(lp - EXPECTED['lp'][exp]) < 1e-6
              and int(np.ceil(lp - 1e-9)) == round(ip))
        check(cid, ok, '%s: coupled optimum %d helpers (ILP %s, LP relaxation %.4f, %d types, %d+%d patterns) = single-cut bound %d: '
              'coupling adds %d' % (text, round(ip), 'proved optimal' if proved else 'NOT proved optimal', lp, len(m.types), m.npat[0],
                                    m.npat[1], sc[key], round(ip) - sc[key]))

    # ===== the shipped words are feasible points ================================================================
    bit_cnt, bit_R = bit_ship_counts()
    stat = []
    for ymode in ('sink', 'strict'):
        m = results[('bit', ymode)][3]
        xf, missing = fix_all(m, bit_cnt)
        val, proved = optimum(m, False, xf)
        stat.append((ymode, val, missing))
    ok = all(v is not None and not mi for _, v, mi in stat) and sum(bit_cnt.values()) == 661 and bit_R == 439
    check('D2.bit-ship-feasible', ok, 'the word of PR #555 (111 x + 111 y + %d helpers) is feasible in the model, sink-only and strict' % bit_R)
    cx_cnt, cx_R, ncent = cx_ship_counts()
    stat = []
    for ymode in ('sink', 'strict'):
        m = results[('cx', ymode)][3]
        xf, missing = fix_all(m, cx_cnt)
        val, proved = optimum(m, False, xf)
        stat.append((ymode, val, missing))
    ok = all(v is not None and not mi for _, v, mi in stat) and sum(cx_cnt.values()) == 112 + 112 + 496 and ncent == 8
    check('D2.cx-ship-feasible', ok, 'the word of PR #569 (width 7) without its %d centres (112 x + 112 y + %d helpers) is feasible in the model, '
          'sink-only and strict' % (ncent, cx_R - ncent))

    # ===== data ladders fixed to the shipped words ================================================================
    fixed_bit = {}
    for ymode in ('sink', 'strict'):
        m = results[('bit', ymode)][3]
        xf, missing = fix_data(m, bit_cnt)
        fixed_bit[ymode] = optimum(m, True, xf) + (missing,)
    ok = (all(p and not mi for _, p, mi in fixed_bit.values()) and round(fixed_bit['sink'][0]) == EXPECTED['ship_fixed_bit']
          and round(fixed_bit['strict'][0]) == EXPECTED['ship_fixed_bit_strict'])
    check('D2.bit-fixed-data', ok,
          'bit unit, data ladders fixed to the shipped word (X: 1,2,4,6,7,8 ...; Y: 0,2,7 ...): at least %d helpers sink-only, %d strict '
          '(= the 222 carriers, 2 per source; the free optima are 212 and 138)'
          % (round(fixed_bit['sink'][0]), round(fixed_bit['strict'][0])))
    vals = {}
    for ymode in ('sink', 'strict'):
        m = results[('cx', ymode)][3]
        xf, missing = fix_data(m, cx_cnt)
        vals[ymode] = optimum(m, True, xf) + (missing,)
    ok = (all(p and not mi for _, p, mi in vals.values()) and round(vals['sink'][0]) == EXPECTED['ship_fixed_cx_sink']
          and round(vals['strict'][0]) == EXPECTED['ship_fixed_cx_strict'])
    check('D2.cx-fixed-data', ok,
          'complex unit, data ladders fixed to the shipped word: at least %d helpers sink-only, %d strict (free optima 107 and 0; the shipped X ladders '
          'have no hop across ranks 5-8, so helpers must supply the large rectangles there; shipped 496)'
          % (round(vals['sink'][0]), round(vals['strict'][0])))


main()
finish()
