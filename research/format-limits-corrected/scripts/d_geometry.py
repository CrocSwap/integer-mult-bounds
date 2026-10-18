"""Geometry shared by the design-free lower-bound checks d1_cover_numbers.py, d2_coupled_count.py, d3_carrier_ledger.py.

Two incidence geometries are used.

* E8 (bit side, PR #555).  The 240 roots of E8 are scaled to norm 4 and live in {-2..2}^8 with even pairwise inner
  products; a "line" is a pair {r, -r}, so there are 120 lines.  The word of PR #555 uses 111 of them as sources; the other 9
  are punctured.  Two lines are orthogonal iff their inner product is 0.  For a line s the 63 lines orthogonal to s form an
  E7 line system of rank 7; its flats of rank 6 are the "hyperplane flats".
* P112 (complex side, PR #531).  The 112 ports are vectors of F_2^9 (odd weight), two ports are orthogonal iff their
  F_2 dot product is 0.  The root lines of PR #531's geometry file give a second description of the same 112 points, used
  by d3 (blocks, tetrads, signed adjacency).

All arithmetic is exact (integers); floating point is used only to group vectors by direction and every grouping result is
re-verified with integer arithmetic where it matters.
"""
import functools
import itertools
import sys

sys.dont_write_bytecode = True      # never write __pycache__ next to files of main

import numpy as np

from report import VENDOR, load_json, main_file

# ---------------------------------------------------------------------------------------------------------------
# F_2 helpers
# ---------------------------------------------------------------------------------------------------------------


def pdot(a, b):
    """F_2 dot product of two bit vectors stored as ints."""
    return (a & b).bit_count() & 1


def f2_reduce(vs):
    """a basis (list of ints) of the F_2 span of vs, built by xor-min reduction."""
    b = []
    for v in vs:
        for x in b:
            v = min(v, v ^ x)
        if v:
            b.append(v)
    return b


def f2_inspan(v, basis):
    for x in basis:
        v = min(v, v ^ x)
    return v == 0


if hasattr(np, 'bitwise_count'):                      # numpy >= 2.0
    def popcount(x):
        """number of set bits of every element of an unsigned integer array."""
        return np.bitwise_count(x).astype(np.int64)
else:
    def popcount(x):
        x = np.ascontiguousarray(x)
        return np.unpackbits(x.view(np.uint8)).reshape(x.shape + (8 * x.dtype.itemsize,)).sum(axis=-1).astype(np.int64)


def orth_tables(ports, nbits=9):
    """ORTH[w] (w in 0..2^nbits-1) = bit mask over the ports i with ports[i] . w = 0, plus the two 64-bit halves as
    uint64 arrays (the 112 ports need 112 bits)."""
    orth = [sum(1 << i for i, p in enumerate(ports) if not pdot(p, w)) for w in range(1 << nbits)]
    m64 = (1 << 64) - 1
    lo = np.array([o & m64 for o in orth], dtype=np.uint64)
    hi = np.array([o >> 64 for o in orth], dtype=np.uint64)
    return orth, lo, hi


def subspace_bases(m, nbits=9, chunk=1 << 14):
    """yield int64 arrays of shape (n, m); each row of an array is the reduced-row-echelon basis of one m-dimensional
    subspace of F_2^nbits, and every subspace occurs exactly once (the number of subspaces is the Gaussian binomial)."""
    if m == 0:
        yield np.zeros((1, 0), dtype=np.int64)
        return
    for piv in itertools.combinations(range(nbits), m):       # leading-bit positions of the m rows
        pivset = set(piv)
        free = [[b for b in range(p) if b not in pivset] for p in piv]
        tot = sum(len(f) for f in free)
        for start in range(0, 1 << tot, chunk):
            bits = np.arange(start, min(start + chunk, 1 << tot), dtype=np.int64)
            rows = np.empty((len(bits), m), dtype=np.int64)
            sh = 0
            for i in range(m):
                v = np.full(len(bits), 1 << piv[i], dtype=np.int64)
                for k, b in enumerate(free[i]):
                    v |= ((bits >> (sh + k)) & 1) << b
                sh += len(free[i])
                rows[:, i] = v
            yield rows


# ---------------------------------------------------------------------------------------------------------------
# P112 (PR #531)
# ---------------------------------------------------------------------------------------------------------------
WORD531 = 'research/direct-delivery504-global/evidence/local/FULL-WORD.json.gz'
PROTO531 = 'research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json'
GK_WORD = 'research/direct-delivery504-global/vendor/gk/gk_word.py'
GK_COMMON = 'research/direct-delivery504-global/vendor/gk/gk_common.py'


@functools.lru_cache(None)
def word531():
    """the complex word of PR #531 (a file of main)."""
    return load_json(main_file(WORD531))


@functools.lru_cache(None)
def cx_ports():
    """the 112 ports of P112 as 9-bit integers (orthogonality = even F_2 dot product)."""
    return tuple(word531()['ports'])


@functools.lru_cache(None)
def p112():
    """P112 with its root-line description (PR #531's geometry file, lines 8..119): returns a dict with
    ports, root lines RL, the signed adjacency Gm[t,s] = (RL_t . RL_s)/2, ADJ = (Gm != 0), the 14 blocks (supports of
    the root lines), the parity par (number of minus signs mod 2) and the tetrad id tet = 2*block + par (28 tetrads)."""
    D = load_json(main_file(PROTO531))
    ports = [D['binary_ports'][i] for i in range(8, 120)]
    RL = [D['root_lines'][i] for i in range(8, 120)]
    assert tuple(ports) == cx_ports() and RL == word531()['root_lines']
    n = 112
    Gm = np.array([[sum(x * y for x, y in zip(RL[t], RL[s])) // 2 for s in range(n)] for t in range(n)], dtype=np.int8)
    np.fill_diagonal(Gm, 0)
    ADJ = Gm != 0
    assert (ADJ == ADJ.T).all()
    supp = [tuple(i for i in range(8) if RL[s][i]) for s in range(n)]
    blocks = sorted(set(supp))
    blk = np.array([blocks.index(supp[s]) for s in range(n)])
    par = np.array([sum(RL[s][i] < 0 for i in supp[s]) % 2 for s in range(n)])
    tet = blk * 2 + par
    return dict(n=n, ports=ports, RL=RL, Gm=Gm, ADJ=ADJ, blk=blk, par=par, tet=tet, nblocks=len(blocks))


@functools.lru_cache(None)
def gk():
    """PR #531's word helpers (gk_word.py / gk_common.py of main): basis(), perp(), FULL."""
    p = main_file(GK_WORD)
    main_file(GK_COMMON)                                  # imported by gk_word.py from the same directory
    sys.path.insert(0, str(p.parent))
    import gk_word
    return gk_word


def cx_section_covers():
    """covers of the readers of a source by sections, for every source s of P112.  The readers are T(s) = the ports orthogonal
    to u_s (52 of them); a section is T(s) & {t : t.w = 0} for a vector w outside <u_s> (a frame <u_s, w> of dimension 2); it
    is proper if it is not all of T(s).  "all" uses every w in F_2^9, "closed" only those w for which w or u_s + w is a port
    (frames spanned by ports).  For each family returns the largest section size over all sources, the number of sources
    whose readers are covered by two proper sections, the largest leftover (uncovered readers) after the best two, and the
    number of improper sections (w outside <u_s> whose section is all of T(s); zero means the readers of s span u_s^perp, so no
    single frame serves them all and the cover number is exactly 2).  The orthogonality relation of P112 is symmetric, so the
    same numbers hold for the sources lying in the perp of a terminal."""
    ports = cx_ports()
    orth, _, _ = orth_tables(ports)
    out = dict(readers=set(), max_all=0, max_closed=0, cover2_all=0, cover2_closed=0, left_all=0, left_closed=0,
               improper_all=0, improper_closed=0)
    m64 = (1 << 64) - 1

    def words(masks):
        return np.array([[m & m64, m >> 64] for m in masks], dtype=np.uint64)

    for s, us in enumerate(ports):
        T = orth[us]
        out['readers'].add(T.bit_count())
        secs = {T & orth[w] for w in range(1, 512) if w != us}
        closed = {T & orth[w] for w in ({p for p in ports if p != us} | {p ^ us for p in ports if p != us})}
        for key, fam in (('all', secs), ('closed', closed)):
            out['improper_' + key] += int(T in fam)
            fam = sorted(fam - {T})                              # proper sections only
            out['max_' + key] = max(out['max_' + key], max(x.bit_count() for x in fam))
            best = max_pair_union(words(fam))
            out['left_' + key] = max(out['left_' + key], T.bit_count() - best)
            out['cover2_' + key] += (best == T.bit_count())
    return out


# ---------------------------------------------------------------------------------------------------------------
# E8 (PR #555)
# ---------------------------------------------------------------------------------------------------------------
BIT_WORD = VENDOR / 'pr555' / 'bitE8mut-p111.json.gz'


@functools.lru_cache(None)
def bit_word():
    return load_json(BIT_WORD)


@functools.lru_cache(None)
def e8():
    """the 120 lines of E8 (integer vectors of norm 4, one representative per +-pair, sorted), the 111 live source lines of
    PR #555's word (srcid[i] = line index of the i-th source) and the inner-product matrix G.

    The lines are the norm-4 vectors with entries in {-2..2} that have even inner product with every live line; the
    candidates are the vectors (+-2, 0, ..., 0) and (+-1, +-1, +-1, +-1, 0, 0, 0, 0)."""
    live = np.array(bit_word()['lines'], dtype=np.int64)
    cands = []
    for i in range(8):
        for s in (2, -2):
            v = [0] * 8
            v[i] = s
            cands.append(v)
    for pos in itertools.combinations(range(8), 4):
        for sg in itertools.product((1, -1), repeat=4):
            v = [0] * 8
            for p, s in zip(pos, sg):
                v[p] = s
            cands.append(v)
    C = np.array(cands, dtype=np.int64)
    roots = C[((C @ live.T) % 2 == 0).all(axis=1)]
    canon = lambda a: max(tuple(a), tuple(-x for x in a))
    L = np.array(sorted({canon(r) for r in roots.tolist()}), dtype=np.int64)
    assert len(roots) == 240 and len(L) == 120
    index = {tuple(l): i for i, l in enumerate(L.tolist())}
    srcid = [index[canon(a)] for a in live.tolist()]
    assert len(set(srcid)) == 111
    isl = np.zeros(120, dtype=bool)
    isl[srcid] = True
    G = L @ L.T
    return dict(L=L, srcid=srcid, isl=isl, G=G, index=index, canon=canon)


def e8_line_index(v):
    E = e8()
    return E['index'][E['canon'](tuple(int(x) for x in v))]


def e7_of(q):
    """indices of the 63 lines orthogonal to line q."""
    G = e8()['G']
    return [j for j in range(120) if G[q, j] == 0]


@functools.lru_cache(None)
def e8_isometries():
    """for every line q a matrix g_q (8x8, float with exact binary entries) of the E8 symmetry group generated by the
    reflections in the roots, with g_q(line s0) = +-(line q), where s0 = line of the first live source; and the induced
    permutation perm_q of the 120 lines (line i is sent to line perm_q[i])."""
    E = e8()
    L = E['L'].astype(float)
    s0 = E['srcid'][0]
    refl = [np.eye(8) - np.outer(L[i], L[i]) / 2.0 for i in range(120)]
    g = {s0: np.eye(8)}
    todo = [s0]
    while todo:
        a = todo.pop()
        for r in range(120):
            m = refl[r] @ g[a]
            b = e8_line_index(np.rint(m @ L[s0]).astype(int))
            if b not in g:
                g[b] = m
                todo.append(b)
    assert len(g) == 120
    perms = {}
    for q, m in g.items():
        img = np.rint(L @ m.T).astype(int)
        perms[q] = np.array([e8_line_index(v) for v in img])
        assert sorted(perms[q]) == list(range(120))
    return s0, g, perms


# --- flats of a vector configuration --------------------------------------------------------------------------


def flat_lattice(V, top_rank):
    """all flats of the matroid of the rows of V (float array, rows are vectors) of rank 1..top_rank, as int bit masks.
    A flat of rank k+1 is the closure of a flat F of rank k together with one more vector, so level k+1 is found by
    grouping the vectors outside F by the direction of their component orthogonal to span(F).
    returns {rank: sorted list of masks}."""
    n = len(V)
    levels = {}
    level = {0}
    for k in range(1, top_rank + 1):
        nxt = set()
        for mask in level:
            idx = [i for i in range(n) if mask >> i & 1]
            if idx:
                U, S, _ = np.linalg.svd(V[idx].T, full_matrices=False)
                Q = U[:, S > 1e-9]
                Rr = V - (V @ Q) @ Q.T
            else:
                Rr = V.copy()
            nrm = np.linalg.norm(Rr, axis=1)
            out = [i for i in range(n) if nrm[i] > 1e-9]
            Rn = Rr[out] / nrm[out][:, None]
            same = np.abs(Rn @ Rn.T) > 1 - 1e-9
            seen = set()
            for a in range(len(out)):
                if a in seen:
                    continue
                grp = np.nonzero(same[a])[0]
                seen.update(grp.tolist())
                m = mask
                for g_ in grp:
                    m |= 1 << out[g_]
                nxt.add(m)
        level = nxt
        levels[k] = sorted(level)
    return levels


@functools.lru_cache(None)
def e7_flats():
    """flats of ranks 1..6 of the E7 line system E7(s0) (the 63 lines orthogonal to the line s0 of the first live source).
    returns (E7 line indices, {rank: masks over the 63 positions}); the rank-6 flats are the hyperplane flats."""
    E = e8()
    s0 = E['srcid'][0]
    idx = e7_of(s0)
    assert len(idx) == 63
    V = E['L'][idx].astype(float)
    assert np.linalg.matrix_rank(V) == 7
    return idx, flat_lattice(V, 6)


def rank_mod_p(rows, p=1000003, want=None):
    """rank of an integer matrix modulo the prime p (stops early once the rank reaches want).  For the 8-column matrices of
    norm-4 vectors used here every nonzero 6x6 minor is at most 2^6 < p in absolute value, so the rank mod p equals the
    rank over the rationals as long as the rank is at most 6."""
    rows = [[x % p for x in r] for r in rows]
    rk = 0
    ncol = len(rows[0])
    for c in range(ncol):
        piv = next((i for i in range(rk, len(rows)) if rows[i][c]), None)
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        inv = pow(rows[rk][c], -1, p)
        rows[rk] = [(x * inv) % p for x in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][c]:
                f = rows[i][c]
                rows[i] = [(x - f * y) % p for x, y in zip(rows[i], rows[rk])]
        rk += 1
        if want is not None and rk >= want:
            break
    return rk


def certify_hyperplane_flats(masks):
    """exact (integer) certificate that every mask is a hyperplane flat of E7(s0).  For a mask with member lines l_1..l_k the
    vector s0 and the members span a hyperplane n^perp of R^8; n is found numerically, scaled to an integer vector and then
    checked EXACTLY: (i) the lines of E7(s0) with n . l = 0 are precisely the members (so the mask is closed under taking
    the span), and (ii) the members have rank 6 (computed modulo a prime larger than every nonzero 6x6 minor)."""
    E = e8()
    idx, _ = e7_flats()
    E7 = E['L'][idx]
    sv = E['L'][E['srcid'][0]]
    for m in masks:
        members = [i for i in range(63) if m >> i & 1]
        A = np.vstack([E7[members], sv[None, :]]).astype(float)
        _, S, Vt = np.linalg.svd(A)
        assert S[6] > 1e-6 and S[7] < 1e-9
        nv = Vt[7]
        nz = np.abs(nv) > 1e-9
        nn = nv / np.abs(nv[nz]).min()
        for t in range(1, 49):
            if np.abs(t * nn - np.rint(t * nn)).max() < 1e-7:
                break
        else:
            raise AssertionError('normal vector is not rational with small denominator')
        n = np.rint(t * nn).astype(np.int64)
        assert (E7 @ n == 0).tolist() == [bool(m >> i & 1) for i in range(63)], 'flat is not closed'
        assert int(sv @ n) == 0
        assert rank_mod_p(E7[members].tolist(), want=6) == 6
    return len(masks)


def max_pair_union(words):
    """maximum, over unordered pairs (a, b) of rows (a = b allowed), of the number of set bits in the union of two rows;
    words: (n, k) uint64 array (the bit sets).  Exact; pairs are pruned with |a|+|b| <= current best."""
    sizes = popcount(words).sum(axis=1)
    order = np.argsort(-sizes, kind='stable')
    W, S = words[order], sizes[order]
    best = 0
    neg = -S
    for i in range(len(W)):
        if 2 * S[i] <= best:
            break
        cnt = int(np.searchsorted(neg, -(best - S[i]), side='left'))   # rows j with S[j] > best - S[i]
        cnt = max(cnt, i + 1)
        u = popcount(W[i][None, :] | W[i:cnt]).sum(axis=1)
        best = max(best, int(u.max()))
    return best


def masks_to_words(masks, nbits):
    """list of int bit masks -> (n, ceil(nbits/64)) uint64 array."""
    k = (nbits + 63) // 64
    m64 = (1 << 64) - 1
    return np.array([[(m >> (64 * j)) & m64 for j in range(k)] for m in masks], dtype=np.uint64)


def find_triple_cover(words, universe):
    """indices (i, j, k) of three rows of words (an (n, w) uint64 array) whose union is the universe (a (w,) uint64 row), or
    None.  For every pair (i, j) the rows containing the leftover are searched."""
    n = len(words)
    for i in range(n):
        for j in range(i, n):
            left = universe & ~(words[i] | words[j])
            ok = np.nonzero(((words & left) == left).all(axis=1))[0]
            if len(ok):
                return i, j, int(ok[0])
    return None


def single_cut_bounds(nsrc, nterm, leftover, cmin):
    """lower bounds on the number of helper registers from the cover numbers at the two ends of the chains.
    nsrc sources (and nsrc targets, so 2 nsrc data registers), nterm terminals; cmin = cover number (every source and every
    terminal needs cmin crossing registers at its end); leftover = number of readers that the best (cmin-1) sections leave
    uncovered (the readers a further register must serve).
    * strict (every data register may serve as a crossing register, each crossing a level at most once): the cmin x nsrc
      crossings needed at the source end and cmin x nterm at the terminal end are supplied by at most 2 nsrc data registers,
      so  R >= max(cmin nsrc - 2 nsrc, cmin nterm - 2 nsrc, 0).
    * sink-only (a target register is only a destination, so it can serve a single reader of a source): a source can do
      with one helper fewer only if `leftover` targets serve its leftover readers one by one; nsrc targets allow that for at
      most floor(nsrc / leftover) sources, so  R >= (cmin - 1) nsrc - floor(nsrc / leftover).
    returns (sink-only bound, strict bound)."""
    data = 2 * nsrc
    sink = (cmin - 1) * nsrc - nsrc // leftover
    strict = max(cmin * nsrc - data, cmin * nterm - data, 0)
    return sink, strict


# --- paths of the registers of the word of PR #555 --------------------------------------------------------------


@functools.lru_cache(None)
def bit_paths():
    """replay the frame changes of PR #555's word.  Each register r (0..110 sources x, 111..221 targets y, then 439
    helpers) starts in frame w['start'][r]; every gate (phases D, A, B, C in this order) [f, dst, srcs] moves dst and the
    srcs into frame f; finally every register is moved to its final frame.  Returns (word, dims, path) where
    dims[f] = rank of frame f (span of its lines) and path[r] = list of frame indices visited by r."""
    w = bit_word()
    lines = np.array(w['lines'], dtype=float)
    dims = [int(np.linalg.matrix_rank(lines[F])) if F else 0 for F in w['frames']]
    cur = list(w['start'])
    path = [[f] for f in cur]
    for ph in 'DABC':
        for f, dst, srcs in w[ph]:
            for r in [dst] + list(srcs):
                if cur[r] != f:
                    cur[r] = f
                    path[r].append(f)
    for r in range(len(cur)):
        if cur[r] != w['final'][r]:
            path[r].append(w['final'][r])
            cur[r] = w['final'][r]
    return w, dims, path
