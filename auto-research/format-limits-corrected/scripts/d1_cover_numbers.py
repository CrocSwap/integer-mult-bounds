"""D1. Design-free cover numbers at the two ends of a register chain (complex P112 and bit E8), and the helper counts they force.

Setting.  A register carries a monotone chain of frames (subspaces) and a gate acts on registers that stand in a common
frame.  In a lossless transfer x_s -> y_q between a source s and a terminal q with s orthogonal to q, the information crosses
every level d exactly once, inside one register's climb from a frame a (dim a < d) into a frame b (dim b >= d); such a
climb contributes a rank-one term with support (sources lying in a) x (terminals lying in b^perp).

* Source end (level 2).  A source s starts in the one-dimensional frame <u_s>.  A register standing at <u_s> and climbing
  into a frame b = <u_s, w> serves the readers t of s (t perp s) with t . w = 0: a "hyperplane section"
  {t perp s, t.w = 0} of the set T(s) of readers of s.  Every reader of s is served by some crossing register, so the
  sections of the crossing registers cover T(s); the cover number of s is the least number of proper sections covering T(s).
* Terminal end (level h-1 -> h).  The same statement for the sources lying in q^perp, covered by hyperplane sections of q^perp.

Each source (terminal) is served by its own register x_s (y_q) and by other registers, so with cover number c every source
needs c-1 foreign crossing registers.  Data registers (x and y) can supply only a few of these; the rest are helpers.

This script computes the cover numbers exactly on the two units
  * complex P112 (PR #531): readers = the 52 ports orthogonal to a port; frames = F_2-subspaces of F_2^9;
  * bit E8 (PR #555): readers of a source = the 63 lines of E7 orthogonal to it; frames = subspaces of Q^8; the sections are
    the hyperplane flats of E7 (all lines of E7 inside a hyperplane of the 7-space),
and derives the lower bounds on the number of helper registers that follow from them.  Upstream: PR #531 (complex word,
geometry), PR #555 (bit word).
"""
import sys

sys.dont_write_bytecode = True

from collections import Counter, defaultdict
from fractions import Fraction as Fr

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

import d_geometry as dg
from report import check, finish

# ---------------------------------------------------------------------------------------------------------------
# Expected values (hard-coded; each is the exact outcome of the computation below)
# ---------------------------------------------------------------------------------------------------------------
EXPECTED = dict(
    # complex P112 (F_2^9, 112 ports, 52 readers per port)
    cx_readers=52,
    cx_max_section=32,               # largest section {t perp s, t.w = 0} over all sources and all w (any frame)
    cx_closed_max_section=26,        # same when the frame <u_s, w> must be spanned by ports (w or u_s + w a port)
    cx_cover2=112,                   # sources whose 52 readers are covered by two proper sections (any frames and closed frames)
    # census of the word of PR #531
    c531_crossings_per_source={3: 112},                  # every source has exactly 3 level-2 crossings
    c531_class_mix={'h': 224, 'x': 112},                 # = X_s plus two helpers per source (224 helper crossings)
    c531_frame_dims={2: 336},                            # all 336 post-crossing frames are 2-dimensional
    c531_section=20,                                     # each such frame serves 20 readers
    c531_level8={'h': 266, 'y': 112, 'x': 14},           # entries into 8-dimensional frames by register class
    c531_nonport_rank1_frames=7,                         # frames of dim >= 2 are all port-spanned; 7 rank-1 frames are not ports
    # drop-free demand of the word of PR #531
    demand_nnz=5824, demand_minus_half=3920, demand_plus_half=1904,
    # bit E8 (63 readers of a source)
    bit_flats_sampled=2258,                              # 60000 random 6-subsets (seed 1) of E7: legacy sampled census
    bit_flats_sampled_hist={10: 232, 13: 589, 16: 683, 21: 663, 30: 63, 36: 28},
    bit_flats=8821,                                      # exhaustive census of the hyperplane flats of E7
    bit_flats_hist={10: 5040, 13: 2016, 16: 1008, 21: 666, 30: 63, 36: 28},
    bit_union2=52,                                       # largest union of two hyperplane flats
    bit_leftover=11,                                     # 63 - 52 lines left uncovered by the best two sections
    bit_cover_number=3,
    bit_term_live_leftover_min=6,                        # worst live-source leftover after any two sections, over all 120 terminals
    # shipped word of PR #555
    bit555_level2={'x': 111, 'y': 10, 'h': 285},
    bit555_per_source_min=3,
    bit555_per_source_hist={3: 78, 4: 6, 5: 17, 6: 7, 7: 3},
    bit555_level7={'x': 108, 'y': 111, 'h': 252},
    bit555_R=439,
    # forced helper counts
    bit_sink=212, bit_strict=138, cx_sink=107, cx_sink_closed=108, cx_strict=0,
)
# The seven maximal parabolic types J of E7 (delete one node of the Dynkin diagram): the flat of rank 6 is the root subsystem of
# type J; its connected components (lines joined when not orthogonal) have the listed numbers of lines.  There are
# |W(E7)| / (2 |W_J|) flats of type J (the number of parabolic subgroups conjugate to W_J is |W(E7)| / |N(W_J)|, and |N(W_J)| = 2 |W_J| for all seven types, as the
# census below confirms).
W_E7 = 2903040                                   # order of the Weyl group of E7
TYPES = {                                        # component sizes (in lines) -> (name, |W_J|)
    (36,): ('E6', 51840), (30,): ('D6', 23040), (21,): ('A6', 5040), (20, 1): ('D5+A1', 1920 * 2),
    (15, 1): ('A5+A1', 720 * 2), (10, 3): ('A4+A2', 120 * 6), (6, 3, 1): ('A3+A2+A1', 24 * 6 * 2),
}


# ---------------------------------------------------------------------------------------------------------------
# Complex P112: census of the word of PR #531
# ---------------------------------------------------------------------------------------------------------------
def census531():
    """replay the frame assignments of the word of PR #531 (phases precondition, A, cut, B, cleanup).  A register moved
    from a one-dimensional frame <u_s> into a frame F of dimension >= 2 is a level-2 crossing for the source s; its section is
    the set of readers t of s with t perp F.  Also records entries into 8-dimensional frames and the types of all frames."""
    d = dg.word531()
    V = 112
    ports = d['ports']
    red, inspan, pd = dg.f2_reduce, dg.f2_inspan, dg.pdot
    cls = lambda r: 'x' if r < V else 'y' if r < 2 * V else 'h'
    cur = {int(k): red(v) for k, v in d['start_extra'].items()}
    for s in range(V):
        cur[s] = [ports[s]]
    port_spanned = lambda B: len(red([p for p in ports if inspan(p, B)])) == len(B)
    cnt = defaultdict(list)
    c8 = Counter()
    for ph in ['precondition', 'A', 'cut', 'B', 'cleanup']:
        for e in d.get(ph, []):
            regs = (e[1], e[2]) if e[0] == 'add' else (e[1],)
            F = e[-1]
            if F is None:
                continue
            Fb = red(F)
            for r in regs:
                c = cur.get(r, [])
                if len(c) == 1 < len(Fb):
                    s = next((i for i in range(V) if inspan(ports[i], c)), None)
                    if s is not None:
                        sec = sum(1 for t in range(V) if not pd(ports[t], ports[s]) and all(not pd(ports[t], f) for f in Fb))
                        cnt[s].append((cls(r), len(Fb), sec, port_spanned(Fb)))
                if len(c) < 8 <= len(Fb) and len(Fb) == 8:
                    c8[cls(r)] += 1
                cur[r] = Fb
    frames = set()
    for ph in ['precondition', 'A', 'B', 'cleanup']:
        for e in d.get(ph, []):
            if e[-1] is not None:
                frames.add(tuple(sorted(e[-1])))
    for v in d['start_extra'].values():
        frames.add(tuple(sorted(v)))
    ftype = Counter()
    for F in frames:
        B = red(list(F))
        ftype[(len(B), port_spanned(B))] += 1
    return cnt, c8, ftype


def demand531():
    """the drop-free demand of the word of PR #531: replay the additions and scalings of the phases precondition, A, B,
    cleanup over Q with the decoder copies (phase cut) removed, tracking for each register its coefficient vector on the
    112 sources.  Returns the matrix L[t][s] = coefficient of x_s in y_t and the replay sanity flags."""
    d = dg.word531()
    V = 112
    n = 2 * V + d['report']['R']
    ports = d['ports']
    val = [{} for _ in range(n)]
    for s in range(V):
        val[s] = {s: Fr(1)}
    for ph in ['precondition', 'A', 'B', 'cleanup']:
        for e in d.get(ph, []):
            if e[0] == 'add':
                _, a, b, num, den, _F = e
                c = Fr(num, den)
                for k, x in val[b].items():
                    nv = val[a].get(k, 0) + c * x
                    if nv:
                        val[a][k] = nv
                    else:
                        val[a].pop(k, None)
            elif e[0] == 'scale':
                _, r, num, den, _F = e
                c = Fr(num, den)
                val[r] = {k: x * c for k, x in val[r].items()}
            else:
                raise ValueError(e)
    L = {t: val[V + t] for t in range(V)}
    restored = all(val[s] == {s: Fr(1)} for s in range(V))
    helpers_free = all(not val[r] for r in range(2 * V, n))
    return L, ports, restored, helpers_free


# ---------------------------------------------------------------------------------------------------------------
# Bit E8: hyperplane flats, covers, terminal side, shipped word
# ---------------------------------------------------------------------------------------------------------------
def sampled_flats():
    """the earlier sampled census: 60000 random 6-subsets of the 63 lines (numpy default_rng(1)); each independent
    6-subset together with s0 spans a hyperplane of R^8 whose E7 lines form a flat.  Returns the set of line-id frozensets."""
    E = dg.e8()
    s0 = E['srcid'][0]
    LN = E['L'].astype(float)
    P = np.array(dg.e7_of(s0))
    rng = np.random.default_rng(1)
    secs = set()
    for _ in range(60000):
        S = rng.choice(P, 6, replace=False)
        M = np.vstack([LN[S], LN[s0][None, :]])
        if np.linalg.matrix_rank(M) < 7:
            continue
        _, _, Vt = np.linalg.svd(M)
        nv = Vt[-1]
        secs.add(frozenset(int(x) for x in P[np.abs(LN[P] @ nv) < 1e-7]))
    return secs


def terminal_side(hyp):
    """for every one of the 120 lines q (111 targets and the 9 pseudo-targets at the punctured lines): the live sources
    lying in q^perp (the live lines orthogonal to q) and the least number of them left uncovered by any two hyperplane
    flats of E7(q).  The flats of E7(q) are the images of the flats of E7(s0) under an E8 symmetry taking s0 to q."""
    E = dg.e8()
    idx, _ = dg.e7_flats()
    s0, g, perms = dg.e8_isometries()
    F0 = np.zeros((len(hyp), 120), dtype=bool)
    for fi, m in enumerate(hyp):
        for k in range(63):
            if m >> k & 1:
                F0[fi, idx[k]] = True
    isl = E['isl']
    G = E['G']
    worst, nlive_min = 10 ** 9, 10 ** 9
    for q in range(120):
        Fq = np.zeros_like(F0)
        Fq[:, perms[q]] = F0
        perp = G[q] == 0
        assert (Fq <= perp[None, :]).all()
        nlive = int((perp & isl).sum())
        pad = np.zeros((len(hyp), 128), dtype=bool)
        pad[:, :120] = Fq & isl[None, :]
        words = np.packbits(pad, axis=1, bitorder='little').view(np.uint64)
        left = nlive - dg.max_pair_union(words)
        worst = min(worst, left)
        nlive_min = min(nlive_min, nlive)
    return worst, nlive_min


def bit555_crossings():
    """level-2 crossings (rank-1 frame -> rank >= 2) and level-7 crossings (rank < 7 -> rank-7 frame) of the registers of the
    word of PR #555, by register class (x sources, y targets, h helpers), and the number of level-2 crossings per source."""
    w, dims, path = dg.bit_paths()
    v = w['v']
    cls = lambda r: 'x' if r < v else 'y' if r < 2 * v else 'h'
    c2, c7, per = Counter(), Counter(), Counter()
    for r, p in enumerate(path):
        for a, b in zip(p, p[1:]):
            if dims[a] < 2 <= dims[b] and dims[a] == 1:
                c2[cls(r)] += 1
                per[tuple(w['frames'][a])] += 1
            if dims[a] < 7 <= dims[b] and dims[b] == 7:
                c7[cls(r)] += 1
    return dict(c2), dict(c7), per, w


def main():
    # ===== complex P112: covers of the readers of a source ======================================================
    cv = dg.cx_section_covers()
    ok = (cv['readers'] == {EXPECTED['cx_readers']} and cv['cover2_all'] == EXPECTED['cx_cover2'] and cv['left_all'] == 0
          and cv['max_all'] == EXPECTED['cx_max_section'] and cv['improper_all'] == 0)
    check('D1.cx-cover2', ok,
          'every source (%d/112): its %d readers are covered by two proper sections {t perp s, t.w = 0} (no single section covers them: '
          'cover number 2); largest single section %d' % (cv['cover2_all'], EXPECTED['cx_readers'], cv['max_all']))
    ok = (cv['cover2_closed'] == EXPECTED['cx_cover2'] and cv['left_closed'] == 0 and cv['max_closed'] == EXPECTED['cx_closed_max_section']
          and cv['improper_closed'] == 0)
    check('D1.cx-cover2-closed', ok,
          'frames spanned by ports only: largest section %d, two sections still cover %d/112 sources'
          % (cv['max_closed'], cv['cover2_closed']))

    # ===== complex P112: the word of PR #531 ====================================================================
    cnt, c8, ftype = census531()
    per_src = Counter(len(v) for v in cnt.values())
    mix = Counter(c for v in cnt.values() for c, _, _, _ in v)
    dims = Counter(dm for v in cnt.values() for _, dm, _, _ in v)
    secs = Counter(sc for v in cnt.values() for _, _, sc, _ in v)
    allclosed = all(ps for v in cnt.values() for _, _, _, ps in v)
    ok = (len(cnt) == 112 and dict(per_src) == EXPECTED['c531_crossings_per_source'] and dict(mix) == EXPECTED['c531_class_mix']
          and dict(dims) == EXPECTED['c531_frame_dims'] and dict(secs) == {EXPECTED['c531_section']: 336} and allclosed)
    check('D1.cx531-level2', ok,
          'every source has exactly 3 level-2 crossings (X_s + 2 helpers: %d helper crossings), all into 2-dim port-spanned frames '
          'with section %d (3 x %d = %d >= 52 > 2 x %d)' % (mix['h'], EXPECTED['c531_section'], EXPECTED['c531_section'],
                                                          3 * EXPECTED['c531_section'], EXPECTED['c531_section']))
    check('D1.cx531-level8', dict(c8) == EXPECTED['c531_level8'],
          'entries into 8-dimensional frames: helpers %d, targets %d, sources %d' % (c8['h'], c8['y'], c8['x']))
    nonport = ftype[(1, False)]
    ok = all(ps for (dm, ps) in ftype if dm >= 2) and nonport == EXPECTED['c531_nonport_rank1_frames']
    check('D1.cx531-frame-types', ok,
          'every frame of dimension >= 2 used by the word is port-spanned (closed); %d rank-1 entrance frames are not ports' % nonport)
    sec531 = EXPECTED['c531_section']
    ok = 2 * sec531 < EXPECTED['cx_readers'] <= 3 * sec531 and cv['cover2_all'] == 112 and cv['cover2_closed'] == 112
    check('D1.cx-224-is-section-type', ok,
          "the 224 helper crossings (2 per source) are forced by #531's section type (2 x %d = %d < 52 <= %d), not by the format: "
          'sections of size up to %d (%d with closed frames) let two sections cover every source'
          % (sec531, 2 * sec531, 3 * sec531, cv['max_all'], cv['max_closed']))

    L, ports, restored, helpers_free = demand531()
    nz = sum(len(r) for r in L.values())
    northo = sum(1 for t in range(112) for s in range(112) if not dg.pdot(ports[s], ports[t]))
    bad = sum(1 for t in L for s in L[t] if dg.pdot(ports[s], ports[t]))
    hist = Counter(str(x) for r in L.values() for x in r.values())
    ok = (restored and helpers_free and nz == northo == EXPECTED['demand_nnz'] and bad == 0
          and hist == Counter({'-1/2': EXPECTED['demand_minus_half'], '1/2': EXPECTED['demand_plus_half']}))
    check('D1.cx-demand', ok,
          'drop-free demand: %d nonzeros = all %d orthogonal (source, target) pairs, values -1/2 x %d and +1/2 x %d, %d entries on non-orthogonal pairs'
          % (nz, northo, hist['-1/2'], hist['1/2'], bad))

    # ===== bit E8: hyperplane flats of E7 =======================================================================
    E = dg.e8()
    idx, lattice = dg.e7_flats()
    hyp = lattice[6]
    pos = {l: i for i, l in enumerate(idx)}
    sampled = sampled_flats()
    hs = Counter(len(x) for x in sampled)
    hyp_set = set(hyp)
    sampled_masks = {sum(1 << pos[l] for l in x) for x in sampled}
    ok = len(sampled) == EXPECTED['bit_flats_sampled'] and dict(hs) == EXPECTED['bit_flats_sampled_hist'] and sampled_masks <= hyp_set
    check('D1.bit-flats-sampled', ok,
          'earlier census by sampling 60000 random 6-subsets (seed 1): %d flats %s, all genuine hyperplane flats of E7 but an '
          'undercount of the small types' % (len(sampled), dict(sorted(hs.items()))))
    hh = Counter(m.bit_count() for m in hyp)
    certified = dg.certify_hyperplane_flats(hyp)
    G7 = E['G'][np.ix_(idx, idx)]
    by_type = Counter()
    for m in hyp:
        members = [i for i in range(63) if m >> i & 1]
        sub = (G7[np.ix_(members, members)] != 0) & ~np.eye(len(members), dtype=bool)
        _, lab = connected_components(csr_matrix(sub), directed=False)
        by_type[tuple(sorted(Counter(lab.tolist()).values(), reverse=True))] += 1
    orb_ok = (set(by_type) == set(TYPES)
              and all(by_type[k] == W_E7 // (2 * TYPES[k][1]) for k in TYPES))
    ok = len(hyp) == EXPECTED['bit_flats'] == certified and dict(hh) == EXPECTED['bit_flats_hist'] and orb_ok
    check('D1.bit-flats', ok,
          'exhaustive census of the hyperplane flats of E7 (closure of flats, each certified in integers): %d flats, by size %s; by type %s '
          '(= |W(E7)| / (2 |W_J|) for each of the 7 maximal parabolic types)'
          % (len(hyp), dict(sorted(hh.items())), {TYPES[k][0]: by_type[k] for k in sorted(TYPES, key=lambda k: -sum(k))}))

    words = dg.masks_to_words(hyp, 63)
    full = dg.masks_to_words([(1 << 63) - 1], 63)[0]
    u2 = dg.max_pair_union(words)
    big = dg.masks_to_words([m for m in hyp if m.bit_count() >= 21], 63)     # a witness may be searched among the large flats
    triple = dg.find_triple_cover(big, full)
    ok = u2 == EXPECTED['bit_union2'] and 63 - u2 == EXPECTED['bit_leftover'] and triple is not None
    check('D1.bit-cover3', ok,
          'readers of a source (63 lines of E7): two hyperplane flats cover at most %d, leaving >= %d lines; three flats of size %s '
          'cover all 63, so the cover number is %d' % (u2, 63 - u2, [int(dg.popcount(big[i]).sum()) for i in triple], EXPECTED['bit_cover_number']))

    worst, nlive_min = terminal_side(hyp)
    ok = worst == EXPECTED['bit_term_live_leftover_min'] and worst >= (63 - u2) - 9
    check('D1.bit-terminal-cover3', ok,
          'terminal side: for each of the 120 terminals q, the live sources in q^perp (at least %d) are not covered by two flats of E7(q): at '
          'least %d live sources remain (>= 11 - 9 punctured lines = 2), so the cover number is 3' % (nlive_min, worst))

    c2, c7, per, w = bit555_crossings()
    ph = Counter(per.values())
    ok = c2 == EXPECTED['bit555_level2'] and len(per) == 111 and min(ph) == EXPECTED['bit555_per_source_min'] and dict(ph) == EXPECTED['bit555_per_source_hist']
    check('D1.bit555-level2', ok,
          'shipped #555 word: level-2 crossings from rank-1 frames x %d / y %d / h %d; every source has >= %d (histogram %s)'
          % (c2['x'], c2['y'], c2['h'], min(ph), dict(sorted(ph.items()))))
    check('D1.bit555-level7', c7 == EXPECTED['bit555_level7'],
          'shipped #555 word: level-7 crossings into rank-7 frames x %d / y %d / h %d' % (c7['x'], c7['y'], c7['h']))

    # ===== derived helper counts ================================================================================
    nsrc = w['v']
    nterm = 120
    cmin_bit = EXPECTED['bit_cover_number']
    leftover_bit = 63 - u2
    sink_bit, strict_bit = dg.single_cut_bounds(nsrc, nterm, leftover_bit, cmin_bit)
    ok = (sink_bit == EXPECTED['bit_sink'] and strict_bit == EXPECTED['bit_strict'] and w['R'] == EXPECTED['bit555_R']
          and triple is not None and u2 < 63)
    check('D1.bit-bounds', ok,
          'bit (cover number %d, leftover %d): sink-only targets R >= 2 x %d - floor(%d/%d) = %d; strict R >= max(3 x %d - %d, 3 x %d - %d) = %d '
          '(shipped %d: %.1f%%)' % (cmin_bit, leftover_bit, nsrc, nsrc, leftover_bit, sink_bit, nsrc, 2 * nsrc, nterm, 2 * nsrc, strict_bit,
                                    w['R'], 100.0 * strict_bit / w['R']))
    V = 112
    cmin_cx = 2 if cv['cover2_all'] == V else None
    left_cx = EXPECTED['cx_readers'] - cv['max_all']
    left_cl = EXPECTED['cx_readers'] - cv['max_closed']
    sink_cx, strict_cx = dg.single_cut_bounds(V, V, left_cx, cmin_cx)
    sink_cl, strict_cl = dg.single_cut_bounds(V, V, left_cl, cmin_cx)
    R531 = dg.word531()['report']['R']
    ok = (sink_cx == EXPECTED['cx_sink'] and sink_cl == EXPECTED['cx_sink_closed'] and strict_cx == strict_cl == EXPECTED['cx_strict']
          and R531 == 504 and len(dg.word531()['centers']) == 8)
    check('D1.cx-bounds', ok,
          'complex (cover number %d, symmetric ends): sink-only targets R >= 112 - floor(112/%d) = %d (%d with closed frames, section %d); '
          'strict R >= 2 x 112 - 224 = %d (shipped %d helpers + 8 centres)' % (cmin_cx, left_cx, sink_cx, sink_cl, cv['max_closed'], strict_cx, R531 - 8))


main()
finish()
