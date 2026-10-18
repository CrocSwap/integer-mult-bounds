#!/usr/bin/env python3
"""Bi-frame decoders on punctured complex E8 units: delivery lower bounds for the asymmetric
centers of #968, and an independent re-derivation of #968's copy-cost floor.

Exact verifier for research/biframe-decoder-ladder/README.md.  Python 3.10+ standard
library only.  The certified format ceiling uses two pinned files of main
(#595's research/format-limits-corrected/scripts/{cert,skel}.py); the budget comparison
cites #968's README (pinned) and #717's helper prices.

From the repository root:

    python3 -B research/biframe-decoder-ladder/verify.py           # recompute, compare with RESULTS.json
    python3 -B research/biframe-decoder-ladder/verify.py --write   # rewrite RESULTS.json

Model (the B14 model of #717 section 5, rebuilt here independently): the 120 lines of
E8; the F2 label of a line is (class of the root in E8/2E8, 1) in F2^9 with the form
omega (+) 1; a decoder on a port set P is a list of terms (d_k, t_k) with
sum_k d_k t_k^T = 2G on P; the cost of a term with row support R and column support A
is the F2 rank of the label pairing span U(R) x span U(A) (Theorem C of #446, as used by
#595 C.3 and #717 D1); cst is the sum over terms.
"""
import argparse
import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
RESULTS = os.path.join(HERE, "RESULTS.json")

FAILS = []


def check(tag, cond, info=""):
    print(("PASS " if cond else "FAIL ") + tag + (" | " + info if info else ""), flush=True)
    if not cond:
        FAILS.append(tag)
    return cond


# ----------------------------------------------------------------------------------
# provenance
# ----------------------------------------------------------------------------------

def git_blob_id(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def load_sources():
    with open(os.path.join(HERE, "SOURCES.json")) as f:
        return json.load(f)


def check_sources(src):
    ok = True
    for rel, pin in sorted(src["vendored"].items()):
        data = open(os.path.join(HERE, rel), "rb").read()
        ok &= git_blob_id(data) == pin["blob"] and hashlib.sha256(data).hexdigest() == pin["sha256"]
    check("provenance.vendored-#717-hit-files", ok, "%d files, git blob ids and sha256" % len(src["vendored"]))
    ok = True
    for rel, sha in sorted(src["main"].items()):
        ok &= hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest() == sha
    check("provenance.main-files", ok, "%d files by sha256" % len(src["main"]))


# ----------------------------------------------------------------------------------
# E8 model
# ----------------------------------------------------------------------------------

def roots_717_order():
    """E8 roots, doubled coordinates, in the generation order of #717's e8model.py (so its
    P112 port indexing can be reproduced); <x,y> = x.y/4."""
    out = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                v = [0] * 8
                v[i] = 2 * si
                v[j] = 2 * sj
                out.append(tuple(v))
    for s in itertools.product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0:
            out.append(tuple(s))
    return out


def ip(x, y):
    s = sum(a * b for a, b in zip(x, y))
    assert s % 4 == 0
    return s // 4


def neg(v):
    return tuple(-a for a in v)


def canon(v):
    for a in v:
        if a:
            return tuple(v) if a > 0 else neg(v)
    raise ValueError("zero vector")


ROOTS = roots_717_order()
assert len(ROOTS) == 240
LINES = sorted({canon(r) for r in ROOTS})
assert len(LINES) == 120
LIDX = {l: i for i, l in enumerate(LINES)}
NL = 120
G = [[ip(a, b) for b in LINES] for a in LINES]

# a Z-basis of simple roots (doubled coordinates); its Cartan matrix is checked to be E8's
SIMPLE = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0), (-2, 2, 0, 0, 0, 0, 0, 0)] + \
         [tuple([0] * k + [-2, 2] + [0] * (6 - k)) for k in range(1, 6)]
CARTAN = [[ip(a, b) for b in SIMPLE] for a in SIMPLE]


def mat_inv(M):
    n = len(M)
    A = [[Fr(x) for x in row] + [Fr(int(i == j)) for j in range(n)] for i, row in enumerate(M)]
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[p] = A[p], A[c]
        pv = A[c][c]
        A[c] = [x / pv for x in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    return [row[n:] for row in A]


def rank_q(rows):
    A = [[Fr(x) for x in r] for r in rows]
    rk = 0
    ncol = len(A[0]) if A else 0
    for c in range(ncol):
        p = next((r for r in range(rk, len(A)) if A[r][c] != 0), None)
        if p is None:
            continue
        A[rk], A[p] = A[p], A[rk]
        for r in range(len(A)):
            if r != rk and A[r][c] != 0:
                f = A[r][c] / A[rk][c]
                A[r] = [x - f * y for x, y in zip(A[r], A[rk])]
        rk += 1
    return rk


# fundamental weights (true coordinates): <omega_i, alpha_j> = delta_ij
ALPHA = [[Fr(x, 2) for x in r] for r in SIMPLE]
OMEGA_W = [list(col) for col in zip(*mat_inv(ALPHA))]          # rows omega_i (true coordinates)
for i in range(8):
    for j in range(8):
        assert sum(a * b for a, b in zip(OMEGA_W[i], ALPHA[j])) == (1 if i == j else 0)


def coords(r):
    """coordinates of a root (doubled coords) in the simple-root basis: c_i = <r, omega_i>"""
    c = [sum(Fr(a, 2) * b for a, b in zip(r, OMEGA_W[i])) for i in range(8)]
    assert all(x.denominator == 1 for x in c)
    return [int(x) for x in c]


FORM_ROWS = [[CARTAN[i][j] % 2 for j in range(8)] + [0] for i in range(8)] + [[0] * 8 + [1]]


def bits(vec):
    """F2 vector (list of 0/1, coordinate 0 first) -> int with coordinate 0 as the top bit"""
    x = 0
    for b in vec:
        x = (x << 1) | (b & 1)
    return x


LAB = [bits([c % 2 for c in coords(l)] + [1]) for l in LINES]   # labels in F2^9
FORM_INT = [bits(r) for r in FORM_ROWS]


def apply_form(x):
    """S x over F2, S = omega (+) 1"""
    xs = [(x >> (8 - i)) & 1 for i in range(9)]
    return bits([sum(FORM_ROWS[i][j] * xs[j] for j in range(9)) % 2 for i in range(9)])


def par(x):
    return bin(x).count("1") & 1


LABS = [apply_form(u) for u in LAB]          # S u_i


def dot(i, j):
    return par(LABS[i] & LAB[j])


def f2_basis(vals):
    basis = []
    for v in vals:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return basis


def span_dim(lines):
    return len(f2_basis([LAB[i] for i in lines]))


def beta(R, A):
    """Theorem-C pairing rank of a term with row support R and column support A"""
    if not R or not A:
        return 0
    br = f2_basis([LABS[i] for i in R])
    ba = f2_basis([LAB[j] for j in A])
    rows = []
    for v in br:
        row = 0
        for k, w in enumerate(ba):
            row |= par(v & w) << k
        rows.append(row)
    return len(f2_basis(rows))


def support(vec_doubled, ports):
    """ports i with <line_i, v> != 0, v in doubled coordinates (or any rational multiple)"""
    return [i for i in ports if sum(a * b for a, b in zip(LINES[i], vec_doubled)) != 0]


def flat_size(vec):
    return sum(1 for l in LINES if sum(a * b for a, b in zip(l, vec)) == 0)


# ----------------------------------------------------------------------------------
# geometry checks
# ----------------------------------------------------------------------------------

def orthogonal_frames():
    nb = [set(j for j in range(NL) if j != i and G[i][j] == 0) for i in range(NL)]
    out = []

    def ext(c, cand):
        if len(c) == 8:
            out.append(tuple(c))
            return
        for x in sorted(cand):
            if x > c[-1]:
                ext(c + [x], cand & nb[x])
    for i in range(NL):
        ext([i], {x for x in nb[i] if x > i})
    return out


def model_checks(res):
    check("model.cartan-is-E8", all(CARTAN[i][i] == 2 for i in range(8)) and
          sorted(sum(1 for j in range(8) if CARTAN[i][j] == -1) for i in range(8)) == [1, 1, 1, 2, 2, 2, 2, 3] and
          sum(1 for i in range(8) for j in range(8) if CARTAN[i][j] == -1) == 14 and
          all(CARTAN[i][j] in (0, -1) for i in range(8) for j in range(8) if i != j))
    check("model.lines-gram", all(G[i][i] == 2 for i in range(NL)) and
          {G[i][j] for i in range(NL) for j in range(NL) if i != j} == {-1, 0, 1})
    check("model.label-pairing-is-parity-of-ip",
          all(dot(i, j) == (1 if G[i][j] % 2 == 0 else 0) for i in range(NL) for j in range(NL)),
          "label pairing 1 iff the E8 inner product is even")
    check("model.labels-span-F2^9", span_dim(range(NL)) == 9)
    fr = orthogonal_frames()
    F0 = tuple(sorted(LIDX[canon(tuple(2 if t == 2 * a else (2 * s if t == 2 * a + 1 else 0) for t in range(8)))]
                      for a in range(4) for s in (1, -1)))
    disj = [f for f in fr if not set(f) & set(F0)]
    check("model.orthogonal-frames", len(fr) == 2025 and F0 in set(fr) and len(disj) == 1260,
          "%d frames; %d disjoint from the coordinate frame F0" % (len(fr), len(disj)))
    # W(E8) is transitive on frames: orbit of F0 under the 8 simple reflections
    def reflect_line(i, al):
        c = ip(LINES[i], al)                       # <r, alpha>; roots have norm 2
        return LIDX[canon(tuple(x - c * y for x, y in zip(LINES[i], al)))]
    orbit = {F0}
    frontier = [F0]
    while frontier:
        nxt = []
        for f in frontier:
            for al in SIMPLE:
                g = tuple(sorted(reflect_line(i, al) for i in f))
                if g not in orbit:
                    orbit.add(g)
                    nxt.append(g)
        frontier = nxt
    check("model.W-transitive-on-frames", orbit == set(fr), "orbit of F0 under W(E8) = all %d frames" % len(orbit))
    res["frames"] = {"orthogonal_frames": len(fr), "disjoint_from_F0": len(disj), "W_orbit_of_F0": len(orbit)}
    return fr, F0, disj


# ----------------------------------------------------------------------------------
# section 1: the #717 D3 decoders are bi-frames
# ----------------------------------------------------------------------------------

def model717_ports():
    """reproduce #717 e8model.py's 112-port order and signed representatives"""
    seen = {}
    lines = []
    for i, r in enumerate(ROOTS):
        key = r if r > neg(r) else neg(r)
        if key not in seen:
            seen[key] = i
            lines.append(i)
    Rl = [ROOTS[i] for i in lines]
    frame = []
    for a in range(4):
        for s in (1, -1):
            v = [0] * 8
            v[2 * a] = 2
            v[2 * a + 1] = 2 * s
            frame.append(tuple(v))
    fidx = [next(k for k, r in enumerate(Rl) if r == f or r == neg(f)) for f in frame]
    P = [k for k in range(120) if k not in fidx]
    return [Rl[k] for k in P], [Rl[k] for k in fidx]


def load_hit(path):
    D, T = [], []
    for line in open(path):
        s = line.strip()
        if s.startswith("d:"):
            D.append([int(x) for x in s[2:].split()])
        if s.startswith("t:"):
            T.append([int(x) for x in s[2:].split()])
    return [list(r) for r in zip(*D)], [list(r) for r in zip(*T)]      # ports x terms


CLIQUE_717 = [9, 15, 24, 46, 52, 66, 94, 104]          # #717 D3: rng(1) 8-clique, model port indices
P111_PUNCTURE = {"g0": 0, "g1": 1, "g30": 30, "g48": 48, "g70": 70, "g111": 111, "c2_0": 0, "c2_111": 111}


def hit_ports(name):
    if name.startswith("P104/"):
        return [i for i in range(112) if i not in CLIQUE_717]
    q = P111_PUNCTURE[name[len("P111/HIT_"):]]
    return [i for i in range(112) if i != q]


def biframe_of(D, T, reps):
    """solve D = R V, T = R W exactly; return (V, W) as column lists or None"""
    R = [[Fr(x, 2) for x in r] for r in reps]
    idx = []
    for i in range(len(R)):
        if rank_q([R[j] for j in idx + [i]]) == len(idx) + 1:
            idx.append(i)
        if len(idx) == 8:
            break
    Ai = mat_inv([R[i] for i in idx])
    n = len(D[0])
    V = [[sum(Ai[r][c] * D[idx[c]][k] for c in range(8)) for r in range(8)] for k in range(n)]
    W = [[sum(Ai[r][c] * T[idx[c]][k] for c in range(8)) for r in range(8)] for k in range(n)]
    for i in range(len(R)):
        for k in range(n):
            if sum(R[i][j] * V[k][j] for j in range(8)) != D[i][k]:
                return None
            if sum(R[i][j] * W[k][j] for j in range(8)) != T[i][k]:
                return None
    return V, W


def section1(res, F0, disj):
    reps112, frame_reps = model717_ports()
    lines112 = [LIDX[canon(r)] for r in reps112]
    check("s1.model717-frame-is-F0", sorted(LIDX[canon(r)] for r in frame_reps) == list(F0))
    clique = sorted(lines112[i] for i in CLIQUE_717)
    check("s1.717-clique-is-an-orthogonal-frame", tuple(clique) in {tuple(sorted(f)) for f in disj})
    hits = {}
    for name in sorted(load_sources()["vendored"]):
        if not name.startswith("inputs/pr717-hits/"):
            continue
        short = name[len("inputs/pr717-hits/"):-4]
        D, T = load_hit(os.path.join(HERE, name))
        keep = hit_ports(short)
        reps = [reps112[i] for i in keep]
        n = len(D[0])
        exact = all(sum(D[i][k] * T[j][k] for k in range(n)) == 2 * ip(reps[i], reps[j])
                    for i in range(len(keep)) for j in range(len(keep)))
        bf = biframe_of(D, T, reps)
        vw_ok = bf is not None and all(
            sum(bf[0][k][r] * bf[1][k][c] for k in range(n)) == (2 if r == c else 0) for r in range(8) for c in range(8))
        ports = [lines112[i] for i in keep]
        punct = sorted(set(range(NL)) - set(ports))
        costs = []
        kinds = []
        mixed = 0
        for k in range(n):
            Rk = [ports[i] for i in range(len(keep)) if D[i][k] != 0]
            Ak = [ports[i] for i in range(len(keep)) if T[i][k] != 0]
            costs.append(beta(Rk, Ak))
            # flat sizes of v_k, w_k (63 = E7 = a root direction); doubled -> any multiple works
            fv = flat_size([x * 2 for x in bf[0][k]]) if bf else None
            fw = flat_size([x * 2 for x in bf[1][k]]) if bf else None
            kinds.append([fv, fw])
            if fv == 63 and fw == 63:
                av = canon_line_of(bf[0][k])
                aw = canon_line_of(bf[1][k])
                if av != aw and av in punct and aw in punct:
                    mixed += 1
        cst = sum(costs)
        hits[short] = {"n": n, "ports": len(keep), "exact_all_pairs": exact, "biframe": bf is not None,
                       "VWt_is_2I": vw_ok, "costs": costs, "cst": cst, "mixed_root_terms": mixed,
                       "flat_sizes_v_w": kinds, "cst_equals_72_minus_punctures": cst == 72 - len(punct)}
        check("s1.%s.exact-bi-frame" % short, exact and bf is not None and vw_ok,
              "n=%d, exact on all %d^2 pairs, D=RV, T=RW, VW^T=2I" % (n, len(keep)))
        check("s1.%s.cost" % short, cst == 72 - len(punct) and cst >= 56,
              "costs %s = %d = 72 - |punctures| (%d); mixed root terms %d" % (costs, cst, len(punct), mixed))
    res["section1_hits"] = hits
    p104 = [h for k, h in hits.items() if k.startswith("P104")]
    p111 = [h for k, h in hits.items() if k.startswith("P111")]
    check("s1.summary", len(p104) == 3 and len(p111) == 8 and
          all(h["mixed_root_terms"] == 8 and h["costs"] == [7] * 8 for h in p104) and
          all(h["mixed_root_terms"] == 1 and sorted(h["costs"]) == [7] + [8] * 7 for h in p111),
          "P104: 8 mixed root terms of cost 7; P111: 1 mixed root term of cost 7 + 7 terms of cost 8")
    return lines112


def canon_line_of(vec):
    """line index of a rational multiple of a root, else None"""
    nz = [x for x in vec if x != 0]
    for l in LINES:
        lz = [Fr(x, 2) for x in l]
        ratio = None
        ok = True
        for a, b in zip(vec, lz):
            if (a == 0) != (b == 0):
                ok = False
                break
            if b != 0:
                q = a / b
                if ratio is None:
                    ratio = q
                elif q != ratio:
                    ok = False
                    break
        if ok and ratio is not None:
            return LIDX[l]
    return None


# ----------------------------------------------------------------------------------
# section 2: span thresholds over all W(E8)-classes of supports
# ----------------------------------------------------------------------------------

def popcount(x):
    return x.bit_count()


def section2(res):
    # IN[g] = mask of lines whose label lies in gamma^perp (u_i^T S gamma = 0), gamma in F2^9 - 0
    Sg = [apply_form(g) for g in range(512)]
    IN = [0] * 512
    for g in range(1, 512):
        m = 0
        for i in range(NL):
            if not par(LAB[i] & Sg[g]):
                m |= 1 << i
        IN[g] = m
    # all codim-2 subspaces: 2-dim subspaces {0,g1,g2,g1^g2} of the dual
    seen = set()
    IN2 = []
    for g1 in range(1, 512):
        for g2 in range(g1 + 1, 512):
            key = tuple(sorted((g1, g2, g1 ^ g2)))
            if key in seen:
                continue
            seen.add(key)
            IN2.append(IN[g1] & IN[g2])
    check("s2.codim2-subspaces", len(IN2) == 43435)
    rows = []
    for mask in range(1, 256):          # node subsets with at least one nonzero coefficient
        v = [sum(OMEGA_W[i][t] for i in range(8) if (mask >> i) & 1) for t in range(8)]
        S = [k for k in range(NL) if sum(Fr(a, 2) * b for a, b in zip(LINES[k], v)) != 0]
        Sm = sum(1 << k for k in S)
        d = span_dim(S)
        n = len(S)
        c1 = sorted(n - popcount(Sm & IN[g]) for g in range(1, 512))     # deletions per hyperplane
        best1, second1 = c1[0], c1[1]
        best2 = n - max(popcount(Sm & m) for m in IN2)
        rows.append({"nodes_nonzero": [i for i in range(8) if (mask >> i) & 1], "flat_lines": NL - n,
                     "support": n, "span": d, "deletions_to_span_le_8": best1,
                     "second_cheapest_hyperplane": second1, "deletions_to_span_le_7": best2})
    root_rows = [r for r in rows if r["flat_lines"] == 63]
    other = [r for r in rows if r["flat_lines"] != 63]
    check("s2.all-supports-span-F2^9", all(r["span"] == 9 for r in rows), "%d W-classes of supports N(v)" % len(rows))
    check("s2.root-type", len(root_rows) == 1 and root_rows[0]["support"] == 57 and
          root_rows[0]["deletions_to_span_le_8"] == 1 and root_rows[0]["deletions_to_span_le_7"] == 25,
          "N[a]: 57 lines; span 8 after deleting a; span 7 needs >= 25 deletions")
    m8 = min(r["deletions_to_span_le_8"] for r in other)
    m7 = min(r["deletions_to_span_le_7"] for r in other)
    check("s2.non-root-types", m8 == 14 and m7 == 42,
          "every non-root support needs >= %d deletions for span 8 and >= %d for span 7" % (m8, m7))
    d7 = [r for r in other if r["flat_lines"] == 42]
    rest = [r for r in other if r["flat_lines"] != 42]
    check("s2.second-cheapest", root_rows[0]["second_cheapest_hyperplane"] == 24 and len(d7) == 1
          and d7[0]["deletions_to_span_le_8"] == 14 and d7[0]["second_cheapest_hyperplane"] == 34
          and min(r["deletions_to_span_le_8"] for r in rest) == 26,
          "below 16 deletions a side spans 8 only as N(a) with a deleted, or as a D7 support with its unique "
          "14-line set deleted (next hyperplanes: 24 / 34; all other classes >= 26)")
    d7orb = d7_orbit_unions()
    check("s2.D7-orbit-unions", d7orb["orbit"] == 2160 and d7orb["outside_set_is_ip2_lines"]
          and min(int(k) for k in d7orb["union_sizes"]) == 21,
          "the 14-line set of a D7 support is {r : |<r,w>| = 2}; two distinct D7 directions need >= 21 deletions")
    res["section2_D7_orbit"] = d7orb
    table = {}
    for r in rows:
        key = "flat%02d" % r["flat_lines"]
        t = table.setdefault(key, {"flat_lines": r["flat_lines"], "support": r["support"], "classes": 0,
                                   "min_deletions_to_span_le_8": r["deletions_to_span_le_8"],
                                   "min_deletions_to_span_le_7": r["deletions_to_span_le_7"]})
        t["classes"] += 1
        t["min_deletions_to_span_le_8"] = min(t["min_deletions_to_span_le_8"], r["deletions_to_span_le_8"])
        t["min_deletions_to_span_le_7"] = min(t["min_deletions_to_span_le_7"], r["deletions_to_span_le_7"])
        t["min_second_cheapest_hyperplane"] = min(t.get("min_second_cheapest_hyperplane", 999), r["second_cheapest_hyperplane"])
    res["section2_thresholds"] = {"node_subsets": len(rows), "by_flat_size": [table[k] for k in sorted(table)],
                                  "root_type": {"to_8": 1, "second_hyperplane": 24, "to_7": 25},
                                  "D7_type": {"to_8": 14, "second_hyperplane": 34, "to_7": 42},
                                  "other_min": {"to_8": min(r["deletions_to_span_le_8"] for r in rest)}}
    return IN, IN2


def d7_orbit_unions():
    """W-orbit of the D7-type weight omega_0; the 14-line deletion set of each D7 support; unions with omega_0's"""
    start = tuple(OMEGA_W[0])
    Sg = [apply_form(g) for g in range(512)]
    S0 = [k for k in range(NL) if sum(Fr(a, 2) * b for a, b in zip(LINES[k], start)) != 0]
    cheapest = min(range(1, 512), key=lambda g: sum(1 for k in S0 if par(LAB[k] & Sg[g])))
    out0 = frozenset(k for k in S0 if par(LAB[k] & Sg[cheapest]))
    Lt = [[Fr(a, 2) for a in l] for l in LINES]
    ipv = lambda k, x: sum(p * q for p, q in zip(Lt[k], x))
    O = lambda x: frozenset(k for k in range(NL) if abs(ipv(k, x)) == 2)
    seen = {start}
    frontier = [start]
    while frontier:
        nxt = []
        for x in frontier:
            for al in ALPHA:
                c = sum(p * q for p, q in zip(x, al))       # <x, alpha> (roots have norm 2)
                y = tuple(p - c * q for p, q in zip(x, al))
                if y not in seen:
                    seen.add(y)
                    nxt.append(y)
        frontier = nxt
    dirs = {max(x, tuple(-p for p in x)) for x in seen}
    k0 = max(start, tuple(-p for p in start))
    O0 = O(start)
    unions = {}
    for x in dirs:
        if x != k0:
            u = len(O0 | O(x))
            unions[str(u)] = unions.get(str(u), 0) + 1
    return {"orbit": len(seen), "directions": len(dirs), "outside_set_is_ip2_lines": out0 == O0 and len(O0) == 14,
            "union_sizes": dict(sorted(unions.items()))}


# ----------------------------------------------------------------------------------
# section 3: root bi-frames on two deleted orthogonal frames
# ----------------------------------------------------------------------------------

def det_nonzero(vecs):
    return rank_q([[Fr(x) for x in v] for v in vecs]) == 8


def root_biframes(pool):
    pool = sorted(pool)
    pairs = [(a, b) for a in pool for b in pool if G[a][b] != 0]
    comp = {p: set() for p in pairs}
    for p in pairs:
        for q in pairs:
            if p < q and p[0] != q[0] and p[1] != q[1] and G[p[0]][q[1]] == 0 and G[q[0]][p[1]] == 0:
                comp[p].add(q)
                comp[q].add(p)
    out = []

    def ext(c, cand):
        if len(c) == 8:
            if det_nonzero([LINES[a] for a, _ in c]):
                out.append(tuple(c))
            return
        for q in sorted(cand):
            if q > c[-1]:
                ext(c + [q], cand & comp[q])
    for p in pairs:
        ext([p], {q for q in comp[p] if q > p})
    return out


def biframe_costs(bf, ports):
    return [beta(support(LINES[a], ports), support(LINES[b], ports)) for a, b in bf]


def abs_det_true(vecs):
    """|det| of 8 doubled-coordinate vectors, in true coordinates (E8 has covolume 1)"""
    M = [[Fr(x, 2) for x in v] for v in vecs]
    det = Fr(1)
    for c in range(8):
        p = next((r for r in range(c, 8) if M[r][c] != 0), None)
        if p is None:
            return Fr(0)
        if p != c:
            M[c], M[p] = M[p], M[c]
        det *= M[c][c]
        for r in range(c + 1, 8):
            f = M[r][c] / M[c][c]
            M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return abs(det)


def section3(res, F0, disj):
    classes = {}
    examples = {}
    dets = {}
    splits = {}
    for C in disj:
        pool = list(F0) + list(C)
        ports = [i for i in range(NL) if i not in pool]
        bfs = root_biframes(pool)
        costs = [biframe_costs(bf, ports) for bf in bfs]
        mixed = [bf for bf in bfs if all(a != b for a, b in bf)]
        key = (len(bfs), len(mixed), min(sum(c) for c in costs))
        classes[key] = classes.get(key, 0) + 1
        examples.setdefault(key, (C, bfs, costs))
        for bf in bfs:
            dk = ("fully_mixed" if bf in mixed else "pure", str(abs_det_true([LINES[a] for a, _ in bf])))
            dets[dk] = dets.get(dk, 0) + 1
            if bf in mixed:
                split = (sum(1 for a, _ in bf if a in F0), sum(1 for _, b in bf if b in F0))
                splits[split] = splits.get(split, 0) + 1
    summary = [{"root_biframes": k[0], "fully_mixed": k[1], "min_cst_on_P104": k[2], "second_frames": v}
               for k, v in sorted(classes.items())]
    check("s3.census", sorted((k, v) for k, v in classes.items()) == [((2, 0, 64), 336), ((4, 0, 64), 28), ((10, 8, 56), 896)],
          "second frames C: 896 admit 8 fully mixed root bi-frames of cst 56 on P120-F0-C; 336 + 28 admit none (min 64)")
    check("s3.mixed-biframes-are-unimodular-root-bases", dets == {("fully_mixed", "1"): 896 * 8, ("pure", "16"): 1260 * 2 + 28 * 2},
          "every fully mixed bi-frame: the a_k are a Z-basis of E8 (|det| 1) with dual basis +-b_k; pure frames: index 16")
    res["section3_determinants"] = {"%s|det|=%s" % k: v for k, v in sorted(dets.items())}
    check("s3.mixed-split-4-4", splits == {(4, 4): 896 * 8},
          "every fully mixed bi-frame takes 4 a's and 4 b's from F0 (the rest from C)")
    C, bfs, costs = examples[(10, 8, 56)]
    ok = all((sum(c) == 56 and c == [7] * 8) if all(a != b for a, b in bf) else (c == [8] * 8)
             for bf, c in zip(bfs, costs))
    check("s3.good-class-costs", ok, "mixed bi-frames: 8 x 7; the two pure frames: 8 x 8")
    res["section3_two_frame_census"] = summary
    good_C = C
    mixed_bf = sorted(bf for bf in bfs if all(a != b for a, b in bf))[0]
    bad_C = examples[(2, 0, 64)][0]
    return good_C, mixed_bf, bad_C


# ----------------------------------------------------------------------------------
# section 4: an explicit P104 decoder and its center geometry
# ----------------------------------------------------------------------------------

def explicit_decoder(bf, ports):
    D = [[ip(LINES[i], LINES[a]) for a, _ in bf] for i in ports]
    T = [[Fr(2 * ip(LINES[i], LINES[b]), ip(LINES[a], LINES[b])) for a, b in bf] for i in ports]
    return D, T


def is_exact(D, T, ports):
    n = len(D[0])
    return all(sum(D[x][k] * T[y][k] for k in range(n)) == 2 * G[ports[x]][ports[y]]
               for x in range(len(ports)) for y in range(len(ports)))


def section4(res, F0, C, bf):
    pool = list(F0) + list(C)
    ports = [i for i in range(NL) if i not in pool]
    D, T = explicit_decoder(bf, ports)
    ex = is_exact(D, T, ports)
    costs = biframe_costs(bf, ports)
    check("s4.explicit-P104-decoder", ex and costs == [7] * 8 and all(abs(x) <= 1 for r in D for x in r)
          and all(x in (0, 2, -2) for r in T for x in r),
          "8 root pairs from F0 u C; d in {0,+-1}, t in {0,+-2}; exact on all 104^2 pairs; cst 56")
    # center geometry: gather span u_b^perp, reader span u_a^perp, Theorem-C survivor <u_a>
    geo = []
    for (a, b), c in zip(bf, costs):
        Rk = support(LINES[a], ports)
        Ak = support(LINES[b], ports)
        span_R = f2_basis([LAB[i] for i in Rk])
        span_A = f2_basis([LAB[j] for j in Ak])
        in_perp = lambda lst, u: all(par(apply_form(u) & x) == 0 for x in lst)
        geo.append({"a": list(LINES[a]), "b": list(LINES[b]), "ip_ab": G[a][b], "readers": len(Rk), "sources": len(Ak),
                    "reader_span": len(span_R), "source_span": len(span_A),
                    "reader_span_is_ua_perp": len(span_R) == 8 and in_perp(span_R, LAB[a]),
                    "source_span_is_ub_perp": len(span_A) == 8 and in_perp(span_A, LAB[b]),
                    "ua_in_source_span": len(f2_basis(span_A + [LAB[a]])) == 8,
                    "beta": c, "drop_cost_to_ua": 8 + 1 - 2 * 1})
    check("s4.center-geometry", all(g["reader_span_is_ua_perp"] and g["source_span_is_ub_perp"] and g["ua_in_source_span"]
                                    and g["beta"] == 7 == g["drop_cost_to_ua"] for g in geo),
          "each center gathers in u_b^perp, its readers span u_a^perp, survivor = <u_a>: drop u_b^perp -> <u_a> costs 7")
    # readers' frame requirement: t must contain u_{a_k} for each mixed center it reads
    hist = {}
    for t in ports:
        K = [k for k, (a, b) in enumerate(bf) if ip(LINES[t], LINES[a]) != 0]
        d = len(f2_basis([LAB[bf[k][0]] for k in K]))
        hist[(len(K), d)] = hist.get((len(K), d), 0) + 1
    # coordinate decoder on P112 for comparison: readers of star f read at 0 (survivor <u_f> cap u_f^perp = 0)
    P112 = [i for i in range(NL) if i not in F0]
    coord_hist = {}
    for t in P112:
        K = [f for f in F0 if ip(LINES[t], LINES[f]) != 0]
        coord_hist[len(K)] = coord_hist.get(len(K), 0) + 1
    check("s4.reader-frames", sum(hist.values()) == 104 and all(n == d for (n, d) in hist) and coord_hist == {4: 112},
          "P104 targets: (centers read, dim of required cut frame) -> %s; coordinate decoder: every target reads 4 centers at frame 0"
          % dict(sorted(hist.items())))
    # single-cut delivery: a copy that is never dropped again can only climb, so it serves a chain of
    # nested reader frames; Dilworth: copies per center >= minimum chain cover of its readers' frames
    chains = []
    shape = []
    for a, b in bf:
        readers = support(LINES[a], ports)
        frames = [f2_basis([LAB[a2] for a2, _ in bf if ip(LINES[t], LINES[a2]) != 0]) for t in readers]
        chains.append(min_chain_cover(frames))
        inc = sum(1 for i in range(len(frames)) for j in range(i + 1, len(frames))
                  if not span_contains(frames[i], frames[j]) and not span_contains(frames[j], frames[i]))
        shape.append((len(readers), len({span_set(f) for f in frames}), inc))
    check("s4.single-cut-reader-frames", shape == [(52, 52, 1059)] * 8,
          "per center: 52 readers, 52 distinct cut frames, 1059 incomparable reader pairs")
    check("s4.single-cut-chain-cover", chains == [19] * 8,
          "each center's 52 readers need 52 distinct cut frames; minimum chain cover 19 per center, %d in all: "
          ">= %d delivery copies beyond the 8 centers" % (sum(chains), sum(chains) - 8))
    # staggered delivery: every target reads its centers in one global order, climbing by u_{a_k} before
    # each read; the reads of center k form one phase, so chain order and read order never conflict
    stag = {"increasing": staggered_chains(bf, ports, list(range(8))),
            "decreasing": staggered_chains(bf, ports, list(range(7, -1, -1))),
            "best_global_order": staggered_chains(bf, ports, list(BEST_ORDER))}
    check("s4.staggered-chain-cover", stag == {"increasing": 57, "decreasing": 56, "best_global_order": BEST_CHAINS},
          "global read orders need %s chains in all (single cut: %d); best order %s: >= %d copies beyond the 8 centers"
          % (stag, sum(chains), list(BEST_ORDER), BEST_CHAINS - 8))
    res["section4_explicit_P104"] = {
        "F0": [list(LINES[i]) for i in F0], "C": [list(LINES[i]) for i in C],
        "pairs_doubled_coordinates": [[list(LINES[a]), list(LINES[b])] for a, b in bf],
        "costs": costs, "exact_all_pairs": ex, "centers": geo,
        "target_reads_and_cut_frame_dim": [{"centers_read": k[0], "cut_frame_dim": k[1], "targets": v}
                                           for k, v in sorted(hist.items())],
        "single_cut_min_chain_cover_per_center": chains,
        "single_cut_extra_delivery_copies_lower_bound": sum(chains) - 8,
        "staggered_global_order_total_chains": stag,
        "staggered_best_global_order": list(BEST_ORDER),
        "staggered_extra_delivery_copies_lower_bound_best_order": BEST_CHAINS - 8}
    return ports, D, T


# exhaustive over all 8! global read orders by `--orders` (about 5 minutes); recorded here
BEST_ORDER = (0, 1, 2, 3, 4, 6, 5, 7)          # first order (lexicographic) attaining the minimum
BEST_CHAINS = 55
ORDER_HIST = {55: 11520, 56: 5760, 57: 17280, 58: 5760}


def staggered_chains(bf, ports, order):
    pos = {k: i for i, k in enumerate(order)}
    at = {}
    for t in ports:
        cur = []
        for k in sorted((k for k in range(8) if ip(LINES[t], LINES[bf[k][0]]) != 0), key=lambda k: pos[k]):
            cur = f2_basis(cur + [LAB[bf[k][0]]])
            at.setdefault(k, []).append(list(cur))
    return sum(min_chain_cover(at[k]) for k in range(8))


def all_orders(bf, ports):
    hist = {}
    best = None
    for order in itertools.permutations(range(8)):
        c = staggered_chains(bf, ports, list(order))
        hist[c] = hist.get(c, 0) + 1
        if best is None or c < best[0]:
            best = (c, order)
    return hist, best


def span_set(B):
    out = {0}
    for b in f2_basis(B):
        out |= {x ^ b for x in out}
    return frozenset(out)


def span_contains(B1, B2):
    return len(f2_basis(B1 + B2)) == len(f2_basis(B1))


def min_chain_cover(frames):
    """Dilworth: minimum number of chains (under containment) covering the given subspaces; readers at
    equal frames share a copy, so duplicates are merged first"""
    uniq = {}
    for f in frames:
        uniq.setdefault(span_set(f), f)
    frames = list(uniq.values())
    n = len(frames)
    less = [[i != j and span_contains(frames[j], frames[i]) and not span_contains(frames[i], frames[j])
             for j in range(n)] for i in range(n)]
    match = [-1] * n

    def aug(i, seen):
        for j in range(n):
            if less[i][j] and not seen[j]:
                seen[j] = True
                if match[j] == -1 or aug(match[j], seen):
                    match[j] = i
                    return True
        return False
    return n - sum(aug(i, [False] * n) for i in range(n))


# ----------------------------------------------------------------------------------
# section 5: pricing (certified ceiling of #595, deficit identity); no construction
# ----------------------------------------------------------------------------------

def section5(res):
    sys.path.insert(0, os.path.join(REPO, "research", "format-limits-corrected", "scripts"))
    from skel import X       # pinned by sha256 in SOURCES.json
    units = [(120, 72), (112, 64), (111, 63), (104, 56), (96, 56)]
    out = []
    for v, cst in units:
        x = Fr(cst, v)
        row = {"v": v, "cst": cst, "x": "%d/%d" % (x.numerator, x.denominator),
               "deficit_per_call_s9": 8 * v - 9 * cst, "deficit_per_port_s9": str(Fr(8 * v - 9 * cst, v))}
        for s in (5, 9):
            r = X(s, 9, 1, x)
            row["ceiling_s%d_upper" % s] = "%.9e" % float(r["hi"])
        out.append(row)
    base = next(r for r in out if r["v"] == 112)
    p104 = next(r for r in out if r["v"] == 104)
    p96 = next(r for r in out if r["v"] == 96)
    rel = float(p104["ceiling_s9_upper"]) / float(base["ceiling_s9_upper"]) - 1
    check("s5.ceilings", float(p104["ceiling_s9_upper"]) > float(base["ceiling_s9_upper"]) > float(p96["ceiling_s9_upper"])
          and abs(float(base["ceiling_s5_upper"]) - 5.1863e-3) < 1e-7,
          "P112 reproduces #595 (5.1863e-3 at s=5); s=9 ceiling P104/P112 - 1 = %+.2f%%; P96/56 is below P112" % (100 * rel))
    # delivery copies against #968's favorable budget, both CITED: #968 (merged) prices P104 at +5.51% b on
    # the selected T37 profile and says the PR589 bit cap leaves about 1.33% of b; #717 P3 prices a removed
    # helper of width 4/5/7/8/9 at +0.026/0.031/0.038/0.051/0.070% b without merge and w9 merged at +0.140%
    text = open(os.path.join(REPO, "research", "complex-frame-pair-decoders", "README.md"), encoding="utf-8").read()
    check("s5.cited-968-budget", "b rises 5.51%" in text and "1.33% above the bit c" in text,
          "#968's README (sha256-pinned) states the +5.51% b budget and the 1.33% bit-cap margin used here")
    budget, cap = Fr(551, 100), Fr(133, 100)
    rates = ("0.026", "0.031", "0.038", "0.051", "0.070", "0.140")
    s4 = res["section4_explicit_P104"]
    models = {"single_cut": s4["single_cut_extra_delivery_copies_lower_bound"],
              "staggered_best_global_order": s4["staggered_extra_delivery_copies_lower_bound_best_order"]}
    price = {"budget_percent_b_cited_from_968": "5.51", "bit_cap_margin_percent_b_cited_from_968": "1.33",
             "break_even_copies_at_rate": {r: "%.1f" % float(budget / Fr(r)) for r in rates}}
    for m, c in models.items():
        price[m] = {"copies_lower_bound": c,
                    "copy_cost_percent_b": {r: "%.3f" % float(c * Fr(r)) for r in rates},
                    "net_vs_budget_percent_b": {r: "%.3f" % float(budget - c * Fr(r)) for r in rates},
                    "can_reach_bit_cap": {r: c * Fr(r) < cap for r in rates}}
    one, stag = price["single_cut"], price["staggered_best_global_order"]
    check("s5.delivery-vs-968-budget",
          all(float(one["net_vs_budget_percent_b"][r]) < 0 for r in ("0.051", "0.070", "0.140"))
          and not any(one["can_reach_bit_cap"].values())
          and all(float(stag["net_vs_budget_percent_b"][r]) > 0 for r in ("0.051", "0.070"))
          and float(stag["net_vs_budget_percent_b"]["0.140"]) < 0
          and [r for r in rates if stag["can_reach_bit_cap"][r]] == ["0.026"],
          "single cut (>= %d copies) costs %s / %s / %s%% b at w8 / w9 / merged, beyond the 5.51%% budget; staggered "
          "(>= %d) costs %s / %s / %s%% b; only width-4 copies would let staggered delivery reach the bit cap"
          % (one["copies_lower_bound"], one["copy_cost_percent_b"]["0.051"], one["copy_cost_percent_b"]["0.070"],
             one["copy_cost_percent_b"]["0.140"], stag["copies_lower_bound"], stag["copy_cost_percent_b"]["0.051"],
             stag["copy_cost_percent_b"]["0.070"], stag["copy_cost_percent_b"]["0.140"]))
    res["section5_pricing"] = {"units": out, "ceiling_s9_P104_over_P112_minus_1": "%.6f" % rel,
                               "note": "R-free format ceiling of #595 (certified upper ends), not a supplier value",
                               "delivery_vs_968_budget": price}


# ----------------------------------------------------------------------------------
# negative and sharpness controls
# ----------------------------------------------------------------------------------

def controls(res, F0, C, bf, ports, D, T, IN, IN2, bad_C, lines112):
    out = {}
    # N1: corrupt one coefficient of a vendored P104 hit -> exactness fails
    reps112, _ = model717_ports()
    Dh, Th = load_hit(os.path.join(HERE, "inputs/pr717-hits/P104/HIT_flip_3a.txt"))
    keep = hit_ports("P104/HIT_flip_3a")
    reps = [reps112[i] for i in keep]
    i0 = next(i for i in range(len(keep)) if Dh[i][0] != 0)
    Dh[i0][0] = 0
    bad = not all(sum(Dh[i][k] * Th[j][k] for k in range(8)) == 2 * ip(reps[i], reps[j])
                  for i in range(len(keep)) for j in range(len(keep)))
    out["N1_corrupted_hit_coefficient_rejected"] = check("ctrl.N1.corrupted-hit-rejected", bad)
    # N2: swap two t-columns of the explicit decoder -> exactness fails
    T2 = [r[:] for r in T]
    for r in T2:
        r[0], r[1] = r[1], r[0]
    out["N2_swapped_columns_rejected"] = check("ctrl.N2.swapped-columns-rejected", not is_exact(D, T2, ports))
    # N3: re-admit a mixed term's reader root a_0 as a port -> that term's cost rises to 8
    a0 = bf[0][0]
    ports3 = sorted(ports + [a0])
    c3 = biframe_costs(bf, ports3)
    out["N3_unpunctured_root_costs"] = c3
    check("ctrl.N3.unpunctured-root-raises-cost", c3[0] == 8 and sum(c3) == 57,
          "costs with a_0 restored: %s" % c3)
    # N4: a pure term (f,f) on a punctured f costs 8, not 7 (mixing is what saves)
    P112 = [i for i in range(NL) if i not in F0]
    c4 = [beta(support(LINES[f], P112), support(LINES[f], P112)) for f in F0]
    out["N4_pure_terms_on_P112"] = c4
    c4u = [beta(support(LINES[f], list(range(NL))), support(LINES[f], list(range(NL)))) for f in F0]
    out["N4_coordinate_decoder_on_P120"] = c4u
    check("ctrl.N4.pure-terms-cost-8", c4 == [8] * 8 and c4u == [9] * 8,
          "coordinate decoder: 8 x 8 = 64 on P112 (frame punctured), 8 x 9 = 72 on P120")
    # N5: flip one label bit -> the label/inner-product parity identity fails
    saved = LAB[0]
    LAB[0] ^= 1 << 3
    LABS[0] = apply_form(LAB[0])
    broken = not all(dot(i, j) == (1 if G[i][j] % 2 == 0 else 0) for i in range(NL) for j in range(NL))
    LAB[0] = saved
    LABS[0] = apply_form(saved)
    out["N5_flipped_label_rejected"] = check("ctrl.N5.flipped-label-rejected", broken)
    # N6: tampered vendored bytes -> blob id mismatch
    data = open(os.path.join(HERE, "inputs/pr717-hits/P111/HIT_g0.txt"), "rb").read()
    pin = load_sources()["vendored"]["inputs/pr717-hits/P111/HIT_g0.txt"]["blob"]
    out["N6_tamper_detected"] = check("ctrl.N6.tamper-detected", git_blob_id(data + b" ") != pin)
    # N7: a second frame of the other class admits no mixed root bi-frame
    bfs_bad = root_biframes(list(F0) + list(bad_C))
    out["N7_bad_class_mixed_biframes"] = sum(1 for b in bfs_bad if all(x != y for x, y in b))
    check("ctrl.N7.bad-class-has-no-mixed-biframe", out["N7_bad_class_mixed_biframes"] == 0)
    # S1/S2: the thresholds are attained (sharpness): explicit deletion sets
    a = LIDX[canon((2, 2, 0, 0, 0, 0, 0, 0))]
    Na = [k for k in range(NL) if G[k][a] != 0]
    Nam = sum(1 << k for k in Na)
    m2 = max(IN2, key=lambda m: popcount(Nam & m))
    keep2 = [k for k in Na if (m2 >> k) & 1]
    out["S1_root_support_25_deletions_span"] = [len(Na) - len(keep2), span_dim(keep2)]
    check("ctrl.S1.root-threshold-attained", len(Na) - len(keep2) == 25 and span_dim(keep2) == 7)
    w = [sum(OMEGA_W[i][t] for i in (0,)) for t in range(8)]
    Sd = [k for k in range(NL) if sum(Fr(x, 2) * y for x, y in zip(LINES[k], w)) != 0]
    Sdm = sum(1 << k for k in Sd)
    g1 = max(range(1, 512), key=lambda g: (popcount(Sdm & IN[g]) if popcount(Sdm & IN[g]) < len(Sd) else -1))
    keep1 = [k for k in Sd if (IN[g1] >> k) & 1]
    out["S2_D7_support_14_deletions_span"] = [len(Sd) - len(keep1), span_dim(keep1)]
    check("ctrl.S2.non-root-threshold-attained", len(Sd) - len(keep1) == 14 and span_dim(keep1) == 8)
    res["controls"] = out


# ----------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="rewrite RESULTS.json")
    ap.add_argument("--orders", action="store_true", help="also re-run the exhaustive search over all 8! read orders (~5 min)")
    args = ap.parse_args()
    if sys.version_info < (3, 10):
        sys.exit("Python 3.10+ required")
    res = {"schema": "biframe-decoder-ladder/1"}
    check_sources(load_sources())
    fr, F0, disj = model_checks(res)
    lines112 = section1(res, F0, disj)
    IN, IN2 = section2(res)
    good_C, mixed_bf, bad_C = section3(res, F0, disj)
    ports, D, T = section4(res, F0, good_C, mixed_bf)
    res["section4_explicit_P104"]["staggered_all_global_orders_recorded"] = {
        "orders": 40320, "total_chains_histogram": {str(k): v for k, v in sorted(ORDER_HIST.items())},
        "minimum": BEST_CHAINS}
    if args.orders:
        hist, best = all_orders(mixed_bf, ports)
        check("s4.exhaustive-global-orders", hist == ORDER_HIST and best[0] == BEST_CHAINS,
              "all 40320 global read orders: min %d chains (histogram %s)" % (best[0], dict(sorted(hist.items()))))
    section5(res)
    controls(res, F0, good_C, mixed_bf, ports, D, T, IN, IN2, bad_C, lines112)
    blob = json.dumps(res, indent=1, sort_keys=True) + "\n"
    if args.write:
        with open(RESULTS, "w") as f:
            f.write(blob)
        print("wrote", os.path.relpath(RESULTS, REPO))
    else:
        same = os.path.exists(RESULTS) and open(RESULTS).read() == blob
        check("receipt.matches-RESULTS.json", same)
    if FAILS:
        print("FAILED:", ", ".join(FAILS))
        sys.exit(1)
    print("PASS_BIFRAME_DECODER_LADDER: P104 centers need >= 144 delivery copies at a single cut, >= 47 staggered; "
          "#968 floor cst >= max(v - 48, 56) re-derived; 11 #717 decoders are exact bi-frames; %d controls" % len(res["controls"]))


if __name__ == "__main__":
    main()
