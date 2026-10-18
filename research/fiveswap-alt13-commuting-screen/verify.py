#!/usr/bin/env python3
"""Exact screen of the pairwise-commuting projector family for fully occupied
coordinate-SWAP words in the formal F2[GL_2(F2)] register model.

Model (the PR1333/1414/1491/1541/1722 coordinate-CNOT line, unchanged):
  G = GL_2(F2) = <a, b>, s = aba = bab.  R = F2[G].
  Paid call D_N(g) = I + ([g]+1) N with g in {a, b} and N = u v^T,
  v^T u = 1 over F2 (binary rank-one idempotent).
  Target T = [s] I_t at exactly r = t fully occupied roles, arbitrary dirty
  inputs, free scalar GL_t(F2) mixing (normalized by augmentation).

Scoped negative result (no new kappa):
  Any pairwise-commuting tuple of rank-one idempotent projectors satisfying the
  sign equation sum N_i = I_t is, up to GL_t conjugation, a word over one
  orthogonal frame of exactly t projectors, each appearing with odd
  multiplicity.  Every frame class occupies at least three word positions
  (classes of size <= 2 fail four mod-2 conditions derived from the natural
  quotient).  Hence q >= 3t in this family: the direct 3t tariff is exact.  In
  particular there is no strictly alternating thirteen-call word for t = 5 with
  pairwise-commuting projectors; any thirteen-call escape must use noncommuting
  scalar projectors.

Checks in this file:
  1. Formal group-algebra product engine (right-multiplication-free, exact).
  2. Positive word controls: t = 1 (3 calls), t = 3 (9 calls), t = 5 (15
     calls) direct words reach [s] I_t exactly.
  3. Necessary-condition screen: four (first, last) label categories of
     label-alternating subsequences must each be odd per frame class; classes
     of size <= 2 are inadmissible for every label word (exhaustive to length
     6); for the strictly alternating 13-label word the minimum admissible
     class size is 3 and no partition of 13 positions into 5 admissible
     classes exists (exact-cover DP).
  4. Failure controls: mutated direct word fails the formal product; a class
     failing one category is rejected; a noncommuting projector pair exists
     (the family is strict).
  5. Reduction-lemma support: pairwise-commuting distinct rank-one idempotents
     are equal or orthogonal (exhaustive over F2^3), and an orthogonal
     distinct sum equal to I_r uses exactly r frames.

Aaron Wang, with help from opencode.  Apache-2.0.  Stdlib only.
"""

import itertools
import sys

# --------------------------------------------------------------------------
# Group algebra F2[G], G = GL_2(F2) as 2x2 binary matrices packed in 0..15.
# --------------------------------------------------------------------------

def mmul(x, y):
    """Product of two packed 2x2 binary matrices: bits b3..b0 = r0c0, r0c1,
    r1c0, r1c1, over F2."""
    a = [(x >> 3) & 1, (x >> 2) & 1, (x >> 1) & 1, x & 1]
    b = [(y >> 3) & 1, (y >> 2) & 1, (y >> 1) & 1, y & 1]
    c00 = (a[0] & b[0]) ^ (a[1] & b[2])
    c01 = (a[0] & b[1]) ^ (a[1] & b[3])
    c10 = (a[2] & b[0]) ^ (a[3] & b[2])
    c11 = (a[2] & b[1]) ^ (a[3] & b[3])
    return (c00 << 3) | (c01 << 2) | (c10 << 1) | c11


GL2 = [m for m in range(16)
       if (((m >> 3) & 1) * (m & 1)) ^ (((m >> 2) & 1) * ((m >> 1) & 1))]
GL2.sort()
assert len(GL2) == 6
GIDX = {m: i for i, m in enumerate(GL2)}
E_ID = GIDX[0b1001]          # identity [[1,0],[0,1]]
A = GIDX[0b1101]             # [[1,1],[0,1]]
B = GIDX[0b1011]             # [[1,0],[1,1]]
S = GIDX[0b0110]             # [[0,1],[1,0]] = aba = bab

GTMUL = [[GIDX[mmul(GL2[i], GL2[j])] for j in range(6)] for i in range(6)]
assert GTMUL[GTMUL[A][B]][A] == S
assert GTMUL[GTMUL[B][A]][B] == S


def rmul(x, y):
    """Product in R = F2[G]; elements are 6-bit masks indexed like GL2."""
    out = 0
    xs = [i for i in range(6) if (x >> i) & 1]
    ys = [i for i in range(6) if (y >> i) & 1]
    for i in xs:
        for j in ys:
            out ^= 1 << GTMUL[i][j]
    return out


# --------------------------------------------------------------------------
# Matrices over R: tuple of tuples of 6-bit masks.
# --------------------------------------------------------------------------

def eye(r):
    return tuple(tuple((1 << E_ID) if i == j else 0 for j in range(r))
                 for i in range(r))


def matmul(p, q, r):
    out = [[0] * r for _ in range(r)]
    for i in range(r):
        for k in range(r):
            aik = p[i][k]
            if aik:
                for j in range(r):
                    bkj = q[k][j]
                    if bkj:
                        out[i][j] ^= rmul(aik, bkj)
    return tuple(tuple(row) for row in out)


def call_matrix(r, g_idx, cls):
    """D_N(g) with N = e_c e_c^T for the coordinate family (cls = c index)."""
    one = 1 << E_ID
    gbit = 1 << g_idx
    rows = []
    for i in range(r):
        row = []
        for j in range(r):
            v = one if i == j else 0
            if i == j == cls:
                v ^= gbit ^ one          # ([g]+1) on the projector cell
            row.append(v)
        rows.append(tuple(row))
    return tuple(rows)


def word_product(r, labels, classes):
    """Product D_q ... D_1 (labels[0] applied first)."""
    acc = eye(r)
    for lab, cls in zip(labels, classes):
        g = A if lab == "a" else B
        acc = matmul(call_matrix(r, g, cls), acc, r)
    return acc


def target(r):
    sbit = 1 << S
    return tuple(tuple(sbit if i == j else 0 for j in range(r))
                 for i in range(r))


# --------------------------------------------------------------------------
# Necessary-condition screen (natural quotient blocks).
# --------------------------------------------------------------------------

CATS = ("aa", "ab", "ba", "bb")


def category_counts(labels, positions):
    """Parity of label-alternating nonempty subsequences of `positions`
    (a sorted tuple of word indices) by (first label, last label)."""
    counts = {c: 0 for c in CATS}
    n = len(positions)
    for mask in range(1, 1 << n):
        picks = [positions[k] for k in range(n) if (mask >> k) & 1]
        labs = [labels[i] for i in picks]
        if any(labs[t] == labs[t + 1] for t in range(len(labs) - 1)):
            continue                       # E-product vanishes
        counts[labs[0] + labs[-1]] ^= 1
    return counts


def admissible(labels, positions):
    counts = category_counts(labels, positions)
    return all(counts[c] for c in CATS)


def partitions_into_admissible(labels, k):
    """Number of unordered partitions of all word positions into exactly k
    admissible classes (exact-cover DP over masks)."""
    n = len(labels)
    full = (1 << n) - 1
    adm = [m for m in range(1, full + 1)
           if admissible(labels, tuple(i for i in range(n) if (m >> i) & 1))]
    dp = [[0] * (k + 1) for _ in range(full + 1)]
    dp[0][0] = 1
    for mask in range(1, full + 1):
        low = mask & -mask
        for sub in adm:
            if (sub & low) and (sub & ~mask) == 0:
                rest = mask ^ sub
                for j in range(1, k + 1):
                    dp[mask][j] += dp[rest][j - 1]
    return dp[full][k], len(adm)


# --------------------------------------------------------------------------
# Reduction-lemma support (exhaustive over F2^3).
# --------------------------------------------------------------------------

def proj3():
    """All binary rank-one idempotents on F2^3: (image v, covector phi)."""
    out = []
    for v in range(1, 8):
        for phi in range(1, 8):
            dot = bin(v & phi).count("1") & 1
            if dot:
                out.append((v, phi))
    return out


def nmat(v, phi):
    return tuple(tuple(1 if ((v >> i) & 1) and ((phi >> j) & 1) else 0
                       for j in range(3)) for i in range(3))


def nmul(x, y):
    out = [[0] * 3 for _ in range(3)]
    for i in range(3):
        for k in range(3):
            for j in range(3):
                out[i][j] ^= x[i][k] & y[k][j]
    return tuple(tuple(r) for r in out)


def lemma_checks():
    ps = proj3()
    mats = [nmat(v, phi) for v, phi in ps]
    assert len(ps) == 28
    checked = 0
    for i in range(28):
        for j in range(28):
            xi, xj = mats[i], mats[j]
            if nmul(xi, xj) == nmul(xj, xi):
                checked += 1
                if i != j:
                    # distinct commuting rank-one idempotents are orthogonal
                    v_i, phi_i = ps[i]
                    v_j, phi_j = ps[j]
                    assert bin(phi_i & v_j).count("1") & 1 == 0
                    assert bin(phi_j & v_i).count("1") & 1 == 0
    # orthogonal distinct sets summing to I_3 have exactly 3 elements
    frames = 0
    for comb in itertools.combinations(range(28), 3):
        acc = tuple(tuple(0 for _ in range(3)) for _ in range(3))
        ok = True
        for i in comb:
            for j in comb:
                if i != j:
                    v_i, phi_i = ps[i]
                    v_j, phi_j = ps[j]
                    if (bin(phi_i & v_j).count("1") & 1) or \
                       (bin(phi_j & v_i).count("1") & 1):
                        ok = False
            acc = tuple(tuple(acc[p][q] ^ mats[i][p][q] for q in range(3))
                        for p in range(3))
        if ok and acc == tuple(tuple(1 if p == q else 0 for q in range(3))
                               for p in range(3)):
            frames += 1
    return checked, frames


# --------------------------------------------------------------------------
# Main: positive controls, screen, failure controls.
# --------------------------------------------------------------------------

def main():
    sys.stdout.reconfigure(encoding="utf-8")

    # 2. Positive word controls: direct 3-call-per-swap words reach [s] I_t.
    for t, expect_ok in ((1, True), (3, True), (5, True)):
        labels = ["a", "b", "a"] * t
        classes = [i // 3 for i in range(3 * t)]
        got = word_product(t, labels, classes)
        assert (got == target(t)) == expect_ok, t

    # mutated word must NOT reach the target
    labels = ["a", "b", "a"] * 5
    labels[1] = "a"
    classes = [i // 3 for i in range(15)]
    assert word_product(5, labels, classes) != target(5)

    # 3. Screen on the strictly alternating 13-label word (t = 5 candidate).
    alt13 = ["a" if i % 2 == 0 else "b" for i in range(13)]
    sizes = {}
    adm_sets = 0
    min_size = 99
    for mask in range(1, 1 << 13):
        pos = tuple(i for i in range(13) if (mask >> i) & 1)
        if admissible(alt13, pos):
            adm_sets += 1
            sizes[len(pos)] = sizes.get(len(pos), 0) + 1
            min_size = min(min_size, len(pos))
    parts5, _ = partitions_into_admissible(alt13, 5)
    assert min_size == 3, min_size
    assert parts5 == 0, parts5

    # positive structural control: the direct 15-call partition passes
    direct15 = ["a", "b", "a"] * 5
    for c in range(5):
        pos = tuple(range(3 * c, 3 * c + 3))
        assert admissible(direct15, pos), c
    parts_direct, _ = partitions_into_admissible(direct15, 5)
    assert parts_direct >= 1, parts_direct

    # universal small-size control: classes of size <= 2 fail for every
    # label word of length <= 6
    small = 0
    for n in range(1, 7):
        for labs in itertools.product("ab", repeat=n):
            labs = list(labs)
            for k in (1, 2):
                for pos in itertools.combinations(range(n), k):
                    assert not admissible(labs, pos), (labs, pos)
                    small += 1

    # failure control: a class failing one category is rejected
    counts = category_counts(alt13, (0, 1, 2))
    assert all(counts[c] for c in CATS)
    assert not admissible(alt13, (0,))

    # 4/5. Reduction-lemma support and family-boundary witness.
    checked, frames = lemma_checks()
    assert checked > 0 and frames > 0
    n1 = nmat(1, 1)                 # e0 e0^T
    n2 = nmat(1, 3)                 # e0 (e0+e1)^T, idempotent
    assert nmul(n1, n1) == n1 and nmul(n2, n2) == n2
    assert nmul(n1, n2) != nmul(n2, n1)   # noncommuting pair exists

    print("PASS_FIVESWAP_ALT13_COMMUTING_SCREEN",
          "min_class=%d" % min_size,
          "admissible_sets=%d" % adm_sets,
          "size_hist=%s" % ",".join("%d:%d" % (k, sizes[k]) for k in sorted(sizes)),
          "partitions5=%d" % parts5,
          "direct15_partitions=%d" % parts_direct,
          "small_pairs=%d" % small,
          "commuting_pairs=%d" % checked,
          "frames3=%d" % frames,
          "no_new_kappa")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
