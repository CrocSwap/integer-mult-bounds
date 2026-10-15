#!/usr/bin/env python3
# Independent re-implementation of the F2-dual-root census of census.py / CENSUS.json (written without reading
# census.py).  Builds on: PR1084 (navinor, research/bit-orthogonal-pair-decoders: cost-6 orthogonal label pairs,
# F2 duality B0[a_j, b_k] = delta_jk); PR555 (eumemic, research/e8-bit-p111: gen_p3 punctured-star L3 word,
# eligibility rule, frozen plan); PR589/PR545 (DreamingOfClouds: the tuned P111 word and the punctured-star unit).
# Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.
"""Independent census of F2 dual roots over admissible nine-line reader sets P of the frozen PR555 L3 plan.

Method (deliberately different from the path through e8.py / geom.py / gen_p3.py):
  1. The 240 E8 roots are built from scratch in the even coordinate system (D8 roots +-e_i+-e_j and the
     half-integer vectors with an even number of minus signs), stored as doubled integer vectors.
  2. The pinned PR589 word gives Hamming-coordinate vectors (form <x,y>/2) of its 111 live labels (ports_geom).
     A linear isometry Hamming-E8 -> standard E8 is found by matching the Gram matrix of eight live labels that
     form a Z-basis (Gram determinant 1) by backtracking over standard roots; all 111 images are then checked
     to be roots.  The nine punctured labels are recovered geometrically: each is the unique missing standard
     line inside the span of its D4 block (partition file) orthogonal to the three live mates of its 4-frame,
     where the 4-frames are the connected components of the plan's partner/qhost/kline relations.
  3. E8/2E8 classes come from integer coordinates in a Bourbaki simple-root basis; B0[x,y] = 1 + beta(c(x),c(y)).
  4. Eligibility (own reading of gen_p3.eligible / README): in the 4-frame f of p the "hosted" cells are the
     four pairs {t, qhost(t)}, t in f; the two remaining pairs of f are the (z,z) cells.  p is eligible iff both
     (z,z) cells contain p and kline(p) is neither p nor qhost(p).  Lines 0..7 stay live (rule Z).
  5. For each nine-subset P the duals are obtained by Gauss-Jordan inversion over F2 of the 9x9 matrix with rows
     (1, c(a_j)): the dual of a_k is the affine functional eps_k + lambda_k . c(y) with value delta_jk at a_j.
     It is a root line b iff eps_k = 1 and lambda_k = C c(b) (C = Cartan matrix mod 2) for a root class c(b).
usage: python3 -I -B independent_census.py [--write OUT.json]
"""
import gzip
import hashlib
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
WORD = REPO / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
PLAN = REPO / "research/e8-bit-p111/data/plan-l3.json"
PART = REPO / "research/e8-bit-carrier-skeleton/data/skeleton/d4part-pairs.json"
CENSUS = HERE / "CENSUS.json"
PIN = {WORD: "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f",
       PLAN: "d5c2494b4baae801143049e172db303b3c8e25a002e9d9715a1d79dcb2d74c58",
       PART: "d69ffe3326140bc541b8f1639e02db43a5835ab8ca02cc742b5bee2bf2ef1ba9"}
SHIPPED = (10, 15, 51, 53, 56, 66, 72, 89, 111)
CHECKS = []


def check(tag, cond, info=""):
    if not cond:
        raise SystemExit(f"FAIL {tag}: {info}")
    CHECKS.append(tag)


# ------------------------------------------------------------------ exact linear algebra over Q and F2
def rank_q(rows):
    m = [[Fraction(x) for x in r] for r in rows]
    rk, ncol = 0, (len(m[0]) if m else 0)
    for c in range(ncol):
        piv = next((i for i in range(rk, len(m)) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[rk], m[piv] = m[piv], m[rk]
        for i in range(len(m)):
            if i != rk and m[i][c] != 0:
                f = m[i][c] / m[rk][c]
                m[i] = [x - f * y for x, y in zip(m[i], m[rk])]
        rk += 1
    return rk


def det_q(rows):
    m = [[Fraction(x) for x in r] for r in rows]
    n, d = len(m), Fraction(1)
    for c in range(n):
        piv = next((i for i in range(c, n) if m[i][c] != 0), None)
        if piv is None:
            return Fraction(0)
        if piv != c:
            m[c], m[piv] = m[piv], m[c]
            d = -d
        d *= m[c][c]
        for i in range(c + 1, n):
            f = m[i][c] / m[c][c]
            m[i] = [x - f * y for x, y in zip(m[i], m[c])]
    return d


def inverse_q(rows):
    n = len(rows)
    a = [[Fraction(x) for x in r] + [Fraction(int(i == j)) for j in range(n)] for i, r in enumerate(rows)]
    for c in range(n):
        piv = next(i for i in range(c, n) if a[i][c] != 0)
        a[c], a[piv] = a[piv], a[c]
        p = a[c][c]
        a[c] = [x / p for x in a[c]]
        for i in range(n):
            if i != c and a[i][c] != 0:
                f = a[i][c]
                a[i] = [x - f * y for x, y in zip(a[i], a[c])]
    return [r[n:] for r in a]


def f2_rank(masks):
    basis = {}
    for v in masks:
        while v:
            h = v.bit_length() - 1
            if h in basis:
                v ^= basis[h]
            else:
                basis[h] = v
                break
    return len(basis)


def f2_inverse(rows, n):
    """rows: n bitmasks (bit i = column i).  Returns the inverse rows, or None when singular (Gauss-Jordan)."""
    a = [(rows[i], 1 << i) for i in range(n)]
    for c in range(n):
        piv = next((i for i in range(c, n) if a[i][0] >> c & 1), None)
        if piv is None:
            return None
        a[c], a[piv] = a[piv], a[c]
        for i in range(n):
            if i != c and a[i][0] >> c & 1:
                a[i] = (a[i][0] ^ a[c][0], a[i][1] ^ a[c][1])
    return [r[1] for r in a]


# ------------------------------------------------------------------ 1. standard E8 (doubled coordinates)
def standard_roots():
    R = []
    for i, j in itertools.combinations(range(8), 2):
        for si, sj in itertools.product((2, -2), repeat=2):
            v = [0] * 8
            v[i], v[j] = si, sj
            R.append(tuple(v))
    for s in itertools.product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0:
            R.append(s)
    return R


def ip(x, y):                      # standard inner product of doubled vectors
    d = sum(a * b for a, b in zip(x, y))
    assert d % 4 == 0
    return d // 4


def canon(v):
    return v if next(a for a in v if a) > 0 else tuple(-a for a in v)


ROOTS = standard_roots()
ROOTSET = set(ROOTS)
check("E8.roots", len(ROOTS) == 240 and all(ip(r, r) == 2 for r in ROOTS) and all(tuple(-a for a in r) in ROOTSET for r in ROOTS)
      and all(ip(r, s) in (-2, -1, 0, 1, 2) for r in ROOTS for s in ROOTS), "240 norm-2 roots, closed under -1, integral")
SLINES = sorted({canon(r) for r in ROOTS})
check("E8.lines", len(SLINES) == 120)

# ------------------------------------------------------------------ 2. pinned inputs and the label isometry
for path, h in PIN.items():
    check("pin." + path.name, hashlib.sha256(path.read_bytes()).hexdigest() == h, str(path))
word = json.loads(gzip.decompress(WORD.read_bytes()))
check("word.meta", word["coords"] == "ham" and word["form"] == "<x,y>/2" and word["v"] == 111 == len(word["lines"])
      == len(word["ports_geom"]) and word["R"] == 439 and tuple(word["punctured"]) == SHIPPED)
hvec = {g: tuple(v) for g, v in zip(word["ports_geom"], word["lines"])}
check("word.labels", sorted(set(hvec) | set(SHIPPED)) == list(range(120)) and not set(hvec) & set(SHIPPED))


def hip(x, y):
    d = sum(a * b for a, b in zip(x, y))
    assert d % 2 == 0
    return d // 2


check("word.gram", all(hip(x, x) == 2 for x in hvec.values()) and all(hip(x, y) in (-1, 0, 1) for x, y in
      itertools.combinations(hvec.values(), 2)), "Hamming labels are distinct root lines under <x,y>/2")

# eight live labels that form a Z-basis (Gram det 1); deterministic seeded choice
rng = random.Random(20261015)
live_ids = sorted(hvec)
while True:
    pick = sorted(rng.sample(live_ids, 8))
    Hb = [hvec[g] for g in pick]
    Gh = [[hip(x, y) for y in Hb] for x in Hb]
    if det_q(Gh) == 1:
        break


def match(Gh):
    sol = []

    def rec(i):
        if i == 8:
            return True
        for r in ROOTS:
            if all(ip(r, sol[k]) == Gh[i][k] for k in range(i)):
                sol.append(r)
                if rec(i + 1):
                    return True
                sol.pop()
        return False
    assert rec(0)
    return sol


Sb = match(Gh)
Hinv = inverse_q([list(x) for x in Hb])            # rows of Hb; x = c . Hb  => c = x . Hinv


def to_std(x):
    c = [sum(Fraction(x[i]) * Hinv[i][j] for i in range(8)) for j in range(8)]
    y = [sum(c[j] * Sb[j][k] for j in range(8)) for k in range(8)]
    assert all(v.denominator == 1 for v in y)
    return tuple(int(v) for v in y)


LINE = {}
for g, x in hvec.items():
    y = to_std(x)
    check("iso.root", y in ROOTSET, f"label {g}")
    LINE[g] = canon(y)
check("iso.injective", len(set(LINE.values())) == 111)
check("iso.gram", all(ip(LINE[a], LINE[b]) in (hip(hvec[a], hvec[b]), -hip(hvec[a], hvec[b]))
                      for a, b in itertools.combinations(live_ids, 2)), "line Gram |<x,y>| preserved on 111 labels")
missing = sorted(set(SLINES) - set(LINE.values()))
check("iso.missing", len(missing) == 9)

# ------------------------------------------------------------------ plan, frames, D4 blocks
plan = json.loads(PLAN.read_text())
partner = {t: x for t, x in plan["partner"]}
qhost = {t: x for t, x in plan["qhost"]}
kline = {t: x for t, x in plan["kline"]}
check("plan.maps", sorted(partner) == sorted(qhost) == sorted(kline) == list(range(120)))
par = list(range(120))


def find(x):
    while par[x] != x:
        par[x] = par[par[x]]
        x = par[x]
    return x


for t in range(120):
    for u in (partner[t], qhost[t], kline[t]):
        par[find(t)] = find(u)
comp_of = defaultdict(list)
for t in range(120):
    comp_of[find(t)].append(t)
FRAMES = sorted(tuple(sorted(c)) for c in comp_of.values())
check("plan.frames", len(FRAMES) == 30 and all(len(f) == 4 for f in FRAMES), "plan relations close into 30 four-sets")
FRAME = {t: f for f in FRAMES for t in f}

BLOCKS = [[i for i in range(120) if int(h, 16) >> i & 1] for h in json.loads(PART.read_text())]
check("part.partition", sorted(i for b in BLOCKS for i in b) == list(range(120)) and all(len(b) == 12 for b in BLOCKS))
BLK = {i: k for k, b in enumerate(BLOCKS) for i in b}
check("part.frames", all(len({BLK[t] for t in f}) == 1 for f in FRAMES) and all(
    sum(1 for f in FRAMES if BLK[f[0]] == k) == 3 for k in range(10)), "each plan frame inside one block, 3 per block")
check("shipped.one-per-frame", len({FRAME[p] for p in SHIPPED}) == 9)


def span_contains(basis_vecs, y):
    return rank_q(basis_vecs + [y]) == rank_q(basis_vecs)


for p in SHIPPED:
    mates = [t for t in FRAME[p] if t != p]
    check("punct.mates-live", all(t in LINE for t in mates))
    blive = [list(LINE[t]) for t in BLOCKS[BLK[p]] if t in LINE]
    check("punct.block-span", rank_q(blive) == 4)
    cand = [y for y in missing if all(ip(y, LINE[m]) == 0 for m in mates) and span_contains(blive, list(y))]
    check("punct.unique", len(cand) == 1, f"punctured label {p}: {len(cand)} candidates")
    LINE[p] = cand[0]
check("labels.bijective", sorted(LINE) == list(range(120)) and len(set(LINE.values())) == 120)

GRAM = [[ip(LINE[a], LINE[b]) for b in range(120)] for a in range(120)]
check("labels.gram", all(sum(1 for b in range(120) if GRAM[a][b] == 0) == 63 and sum(1 for b in range(120) if
      abs(GRAM[a][b]) == 1) == 56 for a in range(120)))
check("frames.orthogonal", all(GRAM[x][y] == 0 for f in FRAMES for x, y in itertools.combinations(f, 2)))
for k, b in enumerate(BLOCKS):           # each block is a D4: 4-dim span holding exactly its 12 lines
    vecs = [list(LINE[t]) for t in b]
    inside = [t for t in range(120) if span_contains(vecs, list(LINE[t]))]
    check("blocks.D4", rank_q(vecs) == 4 and sorted(inside) == sorted(b), f"block {k}")
COMP = {k: next(j for j in range(10) if all(GRAM[x][y] == 0 for x in BLOCKS[k] for y in BLOCKS[j])) for k in range(10)}
check("blocks.pairs", all(COMP[COMP[k]] == k != COMP[k] for k in range(10)))
PAIR = {t: frozenset((BLK[t], COMP[BLK[t]])) for t in range(120)}

# ------------------------------------------------------------------ 3. E8/2E8 classes
SIMPLE = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0)] + [
    tuple(-2 if k == i else 2 if k == i + 1 else 0 for k in range(8)) for i in range(6)]
check("simple.roots", all(s in ROOTSET for s in SIMPLE))
CART = [[ip(a, b) for b in SIMPLE] for a in SIMPLE]
check("simple.cartan", det_q(CART) == 1 and all(CART[i][i] == 2 for i in range(8))
      and sum(1 for i in range(8) for j in range(8) if CART[i][j] == -1) == 14, "E8 Cartan matrix, det 1")
SINV = inverse_q([list(s) for s in SIMPLE])


def cls(y):
    c = [sum(Fraction(y[i]) * SINV[i][j] for i in range(8)) for j in range(8)]
    assert all(v.denominator == 1 for v in c)
    return sum((int(v) & 1) << j for j, v in enumerate(c))


CL = [cls(LINE[t]) for t in range(120)]
CM = [sum((CART[i][j] & 1) << j for j in range(8)) for i in range(8)]     # Cartan mod 2, rows as masks


def beta(c1, c2):
    acc = 0
    for i in range(8):
        if c1 >> i & 1:
            acc ^= CM[i]
    return bin(acc & c2).count("1") & 1


def lam(c):                                      # lambda = C c (mod 2) as a mask
    acc = 0
    for i in range(8):
        if c >> i & 1:
            acc ^= CM[i]
    return acc


check("classes.distinct", len(set(CL)) == 120 and 0 not in CL)
check("classes.form", all(beta(CL[a], CL[b]) == GRAM[a][b] % 2 for a in range(120) for b in range(120)))
B0 = [[(1 + GRAM[a][b]) % 2 for b in range(120)] for a in range(120)]
ROWS = [sum(B0[a][b] << b for b in range(120)) for a in range(120)]
b0_rank = f2_rank(ROWS)
# weight enumerator of the B0 row code = all affine functionals eps + lambda.c on the 120 root classes
weights = Counter()
for eps in (0, 1):
    for lm in range(256):
        weights[sum(eps ^ (bin(lm & c).count("1") & 1) for c in CL)] += 1
ROOTDUAL = {lam(CL[b]): b for b in range(120)}  # functional 1 + lambda.c(y) is the row of line b
check("b0.rank", b0_rank == 9 and dict(weights) == {0: 1, 56: 255, 64: 255, 120: 1})
aff_rank = lambda ids: f2_rank([(1 << 8) | CL[t] for t in ids])       # noqa: E731
d4_aff = sorted({aff_rank(b) for b in BLOCKS})
pair_aff = sorted({aff_rank(BLOCKS[k] + BLOCKS[COMP[k]]) for k in range(10)})

# ------------------------------------------------------------------ 4. eligibility (own reading)
ELIG, ZZ = [], {}
for f in FRAMES:
    hosted = {frozenset((t, qhost[t])) for t in f}
    check("plan.hosted", len(hosted) == 4 and all(qhost[t] in f and qhost[t] != t for t in f)
          and all(partner[t] in f and partner[t] != t and kline[t] in f and kline[t] not in (t, partner[t]) for t in f))
    zz = [frozenset(c) for c in itertools.combinations(f, 2) if frozenset(c) not in hosted]
    check("plan.zz", len(zz) == 2)
    for p in f:
        ZZ[p] = zz
        if all(p in c for c in zz) and kline[p] not in (p, qhost[p]):
            ELIG.append(p)
ELIG.sort()
ELIG_Z = [p for p in ELIG if p >= 8]
check("elig.shipped", set(SHIPPED) <= set(ELIG_Z))


# ------------------------------------------------------------------ 5. duals by F2 Gauss-Jordan
def duals(P):
    """None if the classes of P are affinely dependent; else list of (a_k, kind, b) with kind in root/self/nonroot."""
    A = [1 | (CL[a] << 1) for a in P]            # column 0: constant, columns 1..8: class bits
    inv = f2_inverse(A, 9)
    if inv is None:
        return None
    out = []
    for k, a in enumerate(P):
        u = 0                                    # column k of A^{-1}: u = (eps_k, lambda_k)
        for i in range(9):
            u |= (inv[i] >> k & 1) << i
        eps, lm = u & 1, u >> 1
        b = ROOTDUAL.get(lm) if eps == 1 else None
        if b is None:
            out.append((a, "nonroot", None))
        elif b == a:
            out.append((a, "self", b))
        else:
            assert b not in P and GRAM[a][b] == 0
            out.append((a, "root", b))
    return out


def verify_dual(P, D):                           # direct check of B0[a_j, b_k] = delta_jk for found root duals
    return all(B0[P[j]][b] == int(P[j] == a) for a, kind, b in D if kind != "nonroot" for j in range(9))


rows = {}
cnt = Counter()
frames_ok = True
for n_el, pool in ((19, ELIG), (18, ELIG_Z)):
    for P in itertools.combinations(pool, 9):
        cnt[f"subsets_{n_el}"] += 1
        frames_ok &= len({FRAME[p] for p in P}) == 9
        D = duals(P)
        if n_el == 19 and len({PAIR[p] for p in P}) < 2:
            cnt["fewer_than_two_block_pairs_19"] += 1
            assert D is None
        if D is None:
            cnt[f"dependent_{n_el}"] += 1
            continue
        rows.setdefault(P, D)
check("F.one-per-frame", frames_ok, "every nine-subset of eligible lines meets nine distinct 4-frames")
cnt["fewer_than_two_block_pairs_19"] += 0
cnt["decoder_only_EA_19"] = sum(1 for P in rows)
cnt["admissible_EZA_18"] = sum(1 for P in rows if min(P) >= 8)
check("counts.consistent", cnt["decoder_only_EA_19"] + cnt["dependent_19"] == cnt["subsets_19"]
      and cnt["admissible_EZA_18"] + cnt["dependent_18"] == cnt["subsets_18"])
check("duals.direct", all(verify_dual(P, D) for P, D in rows.items()), "B0 duality rechecked entrywise for every root dual")


def jdist(Ps, pred):
    return dict(sorted(Counter(sum(1 for a, k, b in rows[P] if pred(k, b)) for P in Ps).items()))


EZA = [P for P in rows if min(P) >= 8]
EA = list(rows)
is_root = lambda k, b: k == "root"               # noqa: E731
out07 = lambda k, b: k == "root" and b >= 8      # noqa: E731
J = dict(admissible_EZA=jdist(EZA, is_root), admissible_EZA_dead_duals_outside_0_7=jdist(EZA, out07),
         admissible_EZA_nonroot_dual_terms=jdist(EZA, lambda k, b: k == "nonroot"),
         admissible_EZA_self_dual_terms=jdist(EZA, lambda k, b: k == "self"),
         decoder_only_EA_19=jdist(EA, is_root), decoder_only_EA_19_dead_duals_outside_0_7=jdist(EA, out07))
jmax = {k: max(J[k]) for k in ("admissible_EZA", "admissible_EZA_dead_duals_outside_0_7", "decoder_only_EA_19")}
jof = {P: sum(1 for a, k, b in rows[P] if k == "root") for P in rows}
at_max = sorted(P for P in EZA if jof[P] == jmax["admissible_EZA"])
freq = Counter(b for P in EZA for a, k, b in rows[P] if k == "root")
ge4 = sorted(P for P in EZA if jof[P] >= 4)


def table_row(P):
    return ",".join(map(str, P)) + ":" + ",".join(f"{a}-{b}" for a, k, b in rows[P] if k == "root")


# ------------------------------------------------------------------ 6. shipped P: costs by rational ranks
def term_costs(P, extra=()):
    D = duals(P)
    dead = set(P) | set(extra)
    live = [y for y in range(120) if y not in dead]
    inv = f2_inverse([1 | (CL[a] << 1) for a in P], 9)
    src = []
    for k in range(9):
        u = sum((inv[i] >> k & 1) << i for i in range(9))
        src.append([y for y in live if (u & 1) ^ (bin((u >> 1) & CL[y]).count("1") & 1)])
    rdr = [[y for y in live if B0[a][y]] for a in P]
    ident = all(sum(1 for k in range(9) if x in rdr[k] and y in src[k]) % 2 == B0[x][y] for x in live for y in live)
    costs = [rank_q([[GRAM[x][y] for y in src[k]] for x in rdr[k]]) for k in range(9)]
    return D, ident, costs, len(live)


Dsh, id111, c111, v111 = term_costs(SHIPPED)
roots_sh = [(a, b) for a, k, b in Dsh if k == "root"]
check("shipped.j", len(roots_sh) == 1)
_, id110, c110, v110 = term_costs(SHIPPED, extra=(roots_sh[0][1],))
orth_sh = sum(1 for x in SHIPPED for y in SHIPPED if x != y and GRAM[x][y] == 0)
check("shipped.costs", id111 and id110 and sorted(c111) == [7] * 9 and sorted(c110) == [6] + [7] * 8
      and v111 == 111 and v110 == 110 and orth_sh == 44)

# ------------------------------------------------------------------ controls (non-vacuity)
check("ctl.non-eligible", any(t not in ELIG for t in range(8, 120)) and all(
    not (all(p in c for c in ZZ[p]) and kline[p] not in (p, qhost[p])) for p in range(120) if p not in ELIG))
dep = next(P for P in itertools.combinations(ELIG_Z, 9) if duals(P) is None)
check("ctl.dependent", f2_rank([(1 << 8) | CL[a] for a in dep]) < 9)
bad = list(SHIPPED)
bad[0] = next(t for t in ELIG if t < 8) if any(t < 8 for t in ELIG) else bad[0]
check("ctl.zero-frame", min(bad) < 8 and tuple(sorted(bad)) not in EZA)
B0[SHIPPED[0]][roots_sh[0][1]] ^= 1
check("ctl.corrupt-b0", not verify_dual(SHIPPED, Dsh))
B0[SHIPPED[0]][roots_sh[0][1]] ^= 1

# ------------------------------------------------------------------ result and comparison
mine = dict(
    counts=dict(sorted(cnt.items())),
    eligibility=dict(eligible=ELIG, eligible_in_0_7=[p for p in ELIG if p < 8], eligible_outside_0_7=ELIG_Z,
                     one_line_per_frame=len({FRAME[p] for p in ELIG}) == len(ELIG), pr545_line_39_eligible=39 in ELIG),
    geometry=dict(lines=120, b0_f2_rank=b0_rank, code_weights={str(k): v for k, v in sorted(weights.items())},
                  d4_block_class_affine_ranks=d4_aff, complementary_pair_class_affine_ranks=pair_aff),
    j_distribution=J,
    j_max=dict(jmax, number_of_admissible_P_at_jmax=len(at_max), P102_reachable=jmax["admissible_EZA"] == 9),
    dead_dual_line_frequency={str(b): n for b, n in sorted(freq.items())},
    admissible_P_with_j_at_least_4=[list(P) for P in ge4],
    shipped=dict(P=list(SHIPPED), j=len(roots_sh), ordered_orthogonal_pairs=orth_sh, dual_root=roots_sh[0],
                 P111_costs=c111, P110_costs=c110),
    per_P_table_sha256=hashlib.sha256("\n".join(sorted(table_row(P) for P in EZA)).encode()).hexdigest(),
)

if "--write" in sys.argv:
    Path(sys.argv[sys.argv.index("--write") + 1]).write_text(json.dumps(mine, indent=1, default=list) + "\n")

ref = json.loads(CENSUS.read_text())
diffs, agree = [], []


def cmp(name, a, b):
    (agree if a == b else diffs).append(name if a == b else f"{name}: mine={a!r} census={b!r}")


for k in sorted(set(mine["counts"]) | set(ref["counts"])):
    cmp(f"counts.{k}", mine["counts"].get(k), ref["counts"].get(k))
for k in ("eligible", "eligible_in_0_7", "eligible_outside_0_7", "one_line_per_frame", "pr545_line_39_eligible"):
    cmp(f"eligibility.{k}", mine["eligibility"][k], ref["eligibility"].get(k))
g = ref["geometry"]
cmp("geometry.lines", 120, g.get("lines"))
cmp("geometry.b0_f2_rank", b0_rank, g.get("b0_f2_rank"))
cmp("geometry.code_weights", {int(k): v for k, v in mine["geometry"]["code_weights"].items()},
    {int(k): v for k, v in g.get("code_weights", {}).items()})
cmp("geometry.d4_block_class_affine_ranks", d4_aff, g.get("d4_block_class_affine_ranks"))
cmp("geometry.complementary_pair_class_affine_ranks", pair_aff, g.get("complementary_pair_class_affine_ranks"))
for k, v in J.items():
    cmp(f"j_distribution.{k}", v, {int(a): b for a, b in ref["j_distribution"].get(k, {}).items()})
for k, v in mine["j_max"].items():
    cmp(f"j_max.{k}", v, ref["j_max"].get(k))
cmp("dead_dual_line_frequency", mine["dead_dual_line_frequency"], ref["dead_dual_line_frequency"])


def as_P(x):
    if isinstance(x, dict):
        x = x.get("P", x.get("lines"))
    if isinstance(x, str):
        x = x.split(":")[0].split(",")
    return tuple(sorted(int(t) for t in x))


cmp("admissible_P_with_j_at_least_4", sorted(ge4), sorted(as_P(x) for x in ref["admissible_P_with_j_at_least_4"]))
be = [as_P(x) for x in ref.get("best_examples", [])]
cmp("best_examples_all_at_jmax_and_admissible", True, all(P in rows and min(P) >= 8 and jof[P] ==
                                                          jmax["admissible_EZA"] for P in be))
cmp("per_P_table_sha256", mine["per_P_table_sha256"], ref.get("per_P_table_sha256"))
s = ref["shipped"]
cmp("shipped.P", list(SHIPPED), s.get("P"))
cmp("shipped.j", len(roots_sh), s.get("j"))
cmp("shipped.ordered_orthogonal_pairs", orth_sh, s.get("ordered_orthogonal_pairs"))
cmp("shipped.P111_costs", sorted(c111), sorted(s.get("P111_costs", [])))
dr = s.get("dual_root", {})
cmp("shipped.dual_root", list(roots_sh[0]), [dr.get("a", dr.get("reader")), dr.get("b", dr.get("dual"))])
p110 = s.get("P110", {})
cmp("shipped.P110_costs(in P order)", c110, p110.get("costs"))
cmp("shipped.P110_cst_v", (sum(c110), v110), (p110.get("cst"), p110.get("v")))
# the census' Hamming vectors of the dual-root pair (66 is punctured) land on the lines recovered geometrically here
cmp("shipped.dual_root_vectors", [LINE[dr["a"]], LINE[dr["b"]]], [canon(to_std(dr["a_vec"])), canon(to_std(dr["b_vec"]))])


def record(P):
    D = rows[P]
    pairs = [[a, b] for a, k, b in D if k == "root"]
    dead = sorted(b for a, b in pairs)
    return dict(P=list(P), j=len(pairs), j_restricted=sum(1 for a, b in pairs if b >= 8), dead_duals=dead,
                pairs=pairs, block_pairs_met=len({PAIR[p] for p in P}), blocks=[BLK[p] for p in P])


for x in ref["admissible_P_with_j_at_least_4"]:
    r = record(as_P(x))
    cmp(f"ge4.{r['P']}", {k: r[k] for k in ("j", "j_restricted", "dead_duals", "block_pairs_met")},
        {k: x.get(k) for k in ("j", "j_restricted", "dead_duals", "block_pairs_met")})
for x in ref.get("best_examples", []):
    P = as_P(x)
    r = record(P)
    _, ident, cs, v = term_costs(P, extra=r["dead_duals"])
    cmp(f"best.{r['P']}", dict(r, costs=cs, cst=sum(cs), v=v, identity=ident, wall=(4 * v, 439 <= 4 * v)),
        dict({k: x.get(k) for k in r}, costs=x["extension"]["costs"], cst=x["extension"]["cst"], v=x["extension"]["v"],
             identity=x["extension"]["decoder_identity"], wall=(x["hosting_wall_R439_nine_stage"]["capacity_4v"],
                                                                x["hosting_wall_R439_nine_stage"]["holds"])))

# informational: does the extra (dead-dual) puncture keep gen_p3's one-punctured-line-per-4-frame shape?
info = []
for P in at_max:
    dead = [b for a, k, b in rows[P] if k == "root"]
    allp = list(P) + dead
    shared = sorted({FRAME[t] for t in allp if sum(1 for u in allp if FRAME[u] == FRAME[t]) > 1})
    info.append((P, dead, len(shared), [b for b in dead if b in ELIG]))

print(f"checks {len(CHECKS)}; fields agreeing {len(agree)}; disagreeing {len(diffs)}")
for P, dead, nshared, deadelig in info:
    print(f"  info jmax P {list(P)} dead duals {dead}: 4-frames holding >= 2 punctured lines {nshared}; "
          f"dead duals that are gen_p3-eligible {deadelig}")
for d in diffs:
    print("  DIFF", d)
if diffs:
    raise SystemExit("FAIL_BIT_P102_INDEPENDENT_CENSUS")
print(f"PASS_BIT_P102_INDEPENDENT_CENSUS: eligible {len(ELIG)} ({len(ELIG_Z)} outside 0..7); EZA admissible "
      f"{cnt['admissible_EZA_18']}/{cnt['subsets_18']}; EA {cnt['decoder_only_EA_19']}/{cnt['subsets_19']}; "
      f"j dist {J['admissible_EZA']}; jmax {jmax['admissible_EZA']} ({len(at_max)} P); P102 reachable "
      f"{jmax['admissible_EZA'] == 9}; shipped j 1 -> P110 cst {sum(c110)}; {len(agree)} fields agree")
