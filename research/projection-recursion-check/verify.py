#!/usr/bin/env python3
"""Independent check of the m >= 4 engine-game bound of PR #4628 (2.9447 / 2.99172 / 2.97290).

Prepared by lm1909 with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
Standard library only; nothing is imported from PR #4628 or from the author's repository.

Parts:
  counts   brute-force N_r(s): over ALL Lagrangians M of F_2^(2m) (m = 2, 3, 4) and every nonzero p,
           the reduced distance d(pi_p L0, pi_p M); compared with the closed form derived in README section 3.
           m = 5 on a deterministic random sample of Lagrangians.
  recur    the projection recursion from the block-4 hook profile (27456, 48576, 68320, 86592), exact
           fractions: T_5 = 834241/278850, T_6 = 1188222/399685, min over m = 5..60; profile monotonicity.
  tail     the all-m tail by a monotone coupling with an explicit dominating chain: the transition
           inequalities checked exactly for k <= 300 (proved for all k in README section 4) and the
           certified constant c* from the block-60 profile.
  sens     sensitivity: which block-4 inputs the numbers use, and what is left with weaker inputs.
  shapes   exclusions and smallest open shapes at m = 5, 6 implied by T_m and W + m.
  controls each corrupted claim below must be rejected.
"""
import random
import sys
from fractions import Fraction as F
from math import ceil

FAIL = []
QUIET = [False]


def check(cond, msg):
    if not cond:
        FAIL.append(msg)
        if not QUIET[0]:
            print("FAIL:", msg)
    return cond


# ---------------------------------------------------------------- symplectic geometry over F_2
def pc(x):
    return bin(x).count("1")


def form(m, a, b):
    """standard symplectic form on F_2^(2m); low m bits = x part, high m bits = z part."""
    M = (1 << m) - 1
    return (pc((a & M) & (b >> m)) + pc((a >> m) & (b & M))) & 1


def span(gens):
    out = {0}
    for g in gens:
        if g not in out:
            out |= {x ^ g for x in out}
    return frozenset(out)


def z_frame(m):
    return span([1 << (m + i) for i in range(m)])


def all_lagrangians(m):
    """orbit of the Z-frame under all symplectic transvections (they generate Sp(2m, 2))."""
    start = z_frame(m)
    seen = {start}
    todo = [start]
    vs = range(1, 1 << (2 * m))
    while todo:
        A = todo.pop()
        for v in vs:
            B = frozenset(x ^ v if form(m, x, v) else x for x in A)
            if B not in seen:
                seen.add(B)
                todo.append(B)
    return seen


def log2size(S):
    return len(S).bit_length() - 1


def dist(m, A, B):
    return m - log2size(A & B)


def proj(m, A, p):
    """pi_p A = (A cap p-perp) + <p>, as a subset of p-perp (a Lagrangian of p-perp/<p> plus p)."""
    S = [a for a in A if form(m, a, p) == 0]
    return frozenset(S) | frozenset(s ^ p for s in S)


def reduced_dist(m, A, B, p):
    # both projections contain p; in p-perp/<p> (dimension 2(m-1)) the distance is
    # (m-1) - (dim(piA cap piB) - 1) = m - dim(piA cap piB)
    return m - log2size(proj(m, A, p) & proj(m, B, p))


def N_closed(m, r):
    """closed form derived in README section 3 (own derivation)."""
    out = {}

    def add(s, c):
        if c:
            out[s] = out.get(s, 0) + c
    add(r, (2 ** (m - r) - 1) + (4 ** m - 2 ** (m + r)))            # p in L cap M, or p outside L + M
    add(r - 1, 2 * (2 ** m - 2 ** (m - r)))                           # p in exactly one of L, M
    add(r - 1, (2 ** r - 1) * 2 ** (r - 1) * 2 ** (m - r))            # p = l + m', omega(l, m') = 1
    add(r - 2, (2 ** r - 1) * (2 ** (r - 1) - 1) * 2 ** (m - r))      # p = l + m', omega(l, m') = 0
    assert sum(out.values()) == 4 ** m - 1
    return out


def brute_counts(m, Ms, L0):
    """for each M: dict s -> #p; returns {r: set of frozen dicts}."""
    res = {}
    for M in Ms:
        r = dist(m, L0, M)
        if r == 0:
            continue
        cnt = {}
        for p in range(1, 1 << (2 * m)):
            s = reduced_dist(m, L0, M, p)
            cnt[s] = cnt.get(s, 0) + 1
        res.setdefault(r, set()).add(frozenset(cnt.items()))
    return res


def part_counts(closed=N_closed, quiet=False, ms=(2, 3, 4), sample=True):
    ok = True
    for m in ms:
        Ls = all_lagrangians(m)
        expect = 1
        for i in range(1, m + 1):
            expect *= 2 ** i + 1
        ok &= check(len(Ls) == expect, f"m={m}: {len(Ls)} Lagrangians, expected {expect}")
        L0 = z_frame(m)
        res = brute_counts(m, Ls, L0)
        for r in range(1, m + 1):
            got = res.get(r, set())
            ok &= check(len(got) == 1, f"m={m} r={r}: counts not constant over the {r}-distance class")
            ok &= check(got == {frozenset(closed(m, r).items())}, f"m={m} r={r}: brute {got} != closed {closed(m, r)}")
        if not quiet:
            print(f"counts m={m}: {len(Ls)} Lagrangians, all M at each distance r=1..{m} agree with the closed form")
    if not sample:
        return ok
    # m = 5: deterministic random sample of Lagrangians, generated by random transvection words
    m = 5
    rng = random.Random(4628)
    L0 = z_frame(m)
    sample = []
    for _ in range(60):
        A = L0
        for _ in range(rng.randrange(1, 12)):
            v = rng.randrange(1, 1 << (2 * m))
            A = frozenset(x ^ v if form(m, x, v) else x for x in A)
        sample.append(A)
    res = brute_counts(m, sample, L0)
    for r, got in res.items():
        ok &= check(got == {frozenset(closed(m, r).items())}, f"m=5 r={r}: sampled counts disagree")
    if not quiet:
        print(f"counts m=5: {len(sample)} sampled Lagrangians, distances {sorted(res)}, all agree")
    return ok


# ---------------------------------------------------------------- the recursion
BASE4 = (27456, 48576, 68320, 86592)   # block-4 hook k=8, f=9: cap (exact), and lower bounds for r = 2, 3, 4


def step(a, m, improve=False):
    """a[0..m-1] profile at block m-1 (a[0] = 0) -> profile at block m."""
    b = [0] * (m + 1)
    for r in range(1, m + 1):
        b[r] = sum(c * a[s] for s, c in N_closed(m, r).items() if 1 <= s <= m - 1)
    if improve:   # raise is subadditive: a_m <= a_r + (m - r) a_1, so a_r >= a_m - (m - r) a_1
        for r in range(2, m):
            b[r] = max(b[r], b[m] - (m - r) * b[1])
    return b


def run(base, M, improve=False):
    a = [0] + list(base)
    tops = {len(base): F(a[-1], a[1])}
    profs = {}
    for m in range(len(base) + 1, M + 1):
        a = step(a, m, improve)
        tops[m] = F(a[m], a[1])
        profs[m] = a
    return tops, profs


def part_recur(base=BASE4, quiet=False):
    tops, profs = run(base, 60)
    tops_i, _ = run(base, 60, improve=True)
    ok = check(tops[4] == F(41, 13), "T_4 != 41/13")
    ok &= check(tops[5] == F(834241, 278850), f"T_5 = {tops[5]}")
    ok &= check(tops[6] == F(1188222, 399685), f"T_6 = {tops[6]}")
    ok &= check(tops == tops_i, "triangle improvement changes the tops")
    mn = min(tops[m] for m in range(5, 61))
    ok &= check(mn > F(29447, 10000), f"min T_m (5..60) = {float(mn)}")
    ok &= check(all(tops[m + 1] < tops[m] for m in range(4, 60)), "tops not decreasing")
    a = profs[60]
    ok &= check(all(a[r] <= a[r + 1] for r in range(1, 60)), "block-60 profile not nondecreasing")
    if not quiet:
        print(f"recur: T_4 = {tops[4]}, T_5 = {tops[5]} = {float(tops[5]):.6f}, T_6 = {tops[6]} = {float(tops[6]):.6f}, "
              f"T_7 = {tops[7]}, T_60 = {float(tops[60]):.12f}; min(5..60) = {float(mn):.9f}")
    return ok, tops, profs


# ---------------------------------------------------------------- tail
def p_up(k, j):
    r = k - j
    return F(N_closed(k, r).get(r - 2, 0), 4 ** k - 1) if r >= 1 else F(0)


def p_down(k, j):
    r = k - j
    return F(N_closed(k, r).get(r, 0), 4 ** k - 1) if r >= 1 else F(1)


def dominating_ok(K, qup, qdown):
    for k in range(1, K + 1):
        for j in range(0, k + 1):
            if p_up(k, j) > qup(j):
                return False, (k, j, "up")
            if j >= 1 and p_down(k, j) < qdown(j):
                return False, (k, j, "down")
    # Q is a probability kernel and is monotone (Q_up(j) + Q_down(j+1) <= 1)
    for j in range(0, 400):
        if qup(j) + (qdown(j) if j >= 1 else 0) > 1 or qup(j) + qdown(j + 1) > 1:
            return False, (None, j, "Q")
    return True, None


QUP = lambda j: F(1, 2 ** (j + 1))
QDOWN = lambda j: 1 - F(1, 2 ** j)


def cstar(prof, M0, J=80):
    w = [F(1)]
    for j in range(1, J + 1):
        w.append(w[-1] / (2 ** j - 1))
    Zup = sum(w) + 2 * w[J]           # w_(j+1)/w_j <= 1/3 for j >= 1
    R = lambda r: F(prof[r], prof[1]) if r >= 1 else F(0)
    return sum(w[j] * R(M0 - j) for j in range(0, min(J, M0) + 1)) / Zup


def part_tail(profs, quiet=False):
    ok, where = dominating_ok(300, QUP, QDOWN)
    check(ok, f"dominating chain inequality fails at {where}")
    c = cstar(profs[60], 60)
    ok &= check(c > F(29447, 10000), f"c* = {float(c)}")
    if not quiet:
        print(f"tail: transition inequalities hold for every k <= 300 and 0 <= j <= k; c*(block 60) = {float(c):.12f} > 2.9447")
    return ok


# ---------------------------------------------------------------- sensitivity
def part_sens(quiet=False):
    a1, a2, a3, a4 = BASE4
    weak = (a1, a4 - 2 * a1, a4 - a1, a4)       # triangle lower bounds only: a2 >= a4 - 2 a1, a3 >= a4 - a1
    t_full, _ = run(BASE4, 6)
    t_weak, _ = run(weak, 6)
    # which inputs does T_5 use?  T_5 = (N_5(4) a4 + N_5(3) a3) / (N_1(1) a1): a2 does not enter
    t_a2, _ = run((a1, 0, a3, a4), 6)
    ok = check(t_a2[5] == t_full[5], "T_5 depends on a2")
    ok &= check(t_a2[6] != t_full[6], "T_6 does not depend on a2")
    tw, pw = run(weak, 60)
    if not quiet:
        print(f"sens: T_5 uses a1, a3, a4 only; T_6 also a2.  With triangle-only a2 = {weak[1]}, a3 = {weak[2]}: "
              f"T_5 = {float(t_weak[5]):.5f}, T_6 = {float(t_weak[6]):.5f}, T_60 = {float(tw[60]):.5f}")
    return ok, tw


# ---------------------------------------------------------------- shapes
def smallest_open(T, m, W):
    s = max(ceil(T * W), W + m if W >= 2 else m, 2 * W)
    return s if s < m * W else None


def part_shapes(tops, quiet=False):
    ok = True
    T5, T6 = tops[5], tops[6]
    ok &= check(T5 * 3 > 8 and T6 * 3 > 8, "3 in 8 not excluded")
    ok &= check(T5 * 4 > 11 and T6 * 4 > 11, "4 in 11 not excluded")
    ok &= check(T6 * 5 > 14, "5 in 14 at m=6 not excluded")
    ok &= check(T5 * 3 <= 9 and T6 * 3 <= 9, "3 in 9 excluded?")
    ok &= check(smallest_open(T5, 5, 2) == 7 and smallest_open(T5, 5, 3) == 9, "m=5 smallest open shapes")
    ok &= check(smallest_open(T6, 6, 2) == 8 and smallest_open(T6, 6, 3) == 9, "m=6 smallest open shapes")
    w5 = max(W for W in range(1, 1000) if T5 * W > 3 * W - 1)
    w6 = max(W for W in range(1, 1000) if T6 * W > 3 * W - 1)
    ok &= check((w5, w6) == (120, 36), f"3W-1 exclusion range {w5}, {w6}")
    if not quiet:
        print("shapes: " + "; ".join(f"m={m} W={W}: smallest open s={smallest_open(tops[m], m, W)}"
                                     for m in (5, 6) for W in (2, 3, 4, 5)) + f"; 3W-1 excluded for W <= {w5} (m=5), {w6} (m=6)")
    return ok


# ---------------------------------------------------------------- controls
def part_controls():
    rej = []

    def bad_closed(m, r):            # move one p from s = r-1 to s = r-2
        d = dict(N_closed(m, r))
        if r >= 2 and d.get(r - 1):
            d[r - 1] -= 1
            d[r - 2] = d.get(r - 2, 0) + 1
        return d
    saved = FAIL[:]
    QUIET[0] = True
    rej.append(("perturbed closed form (m = 3)", not part_counts(bad_closed, quiet=True, ms=(3,), sample=False)))
    _, tops, profs = part_recur(quiet=True)
    rej.append(("T_5 claimed 834241/278849", tops[5] != F(834241, 278849)))
    rej.append(("T_6 claimed 1188222/399684", tops[6] != F(1188222, 399684)))
    t_bad, _ = run((27456, 48576, 68321, 86592), 6)
    rej.append(("a3 = 68321 reproduces T_5", t_bad[5] != tops[5]))
    okq, _ = dominating_ok(60, lambda j: F(1, 2 ** (j + 2)), QDOWN)
    rej.append(("dominating chain with up-probability 2^-(j+2)", not okq))
    okq2, _ = dominating_ok(60, QUP, lambda j: 1 - F(1, 2 ** (j + 1)))
    rej.append(("dominating chain with down-probability 1 - 2^-(j+1)", not okq2))
    rej.append(("3 in 9 at m=6 claimed excluded", not (tops[6] * 3 > 9)))
    rej.append(("3 in 8 at m=5 claimed allowed", not (tops[5] * 3 <= 8)))
    tw, _ = run((27456, 86592 - 2 * 27456, 86592 - 27456, 86592), 6)
    rej.append(("2.99172 claimed from triangle-only inputs", tw[5] < F(299172, 100000)))
    fake = [0, 1, 3, 2, 4]
    rej.append(("nonmonotone profile accepted", not all(fake[r] <= fake[r + 1] for r in range(1, 4))))
    QUIET[0] = False
    del FAIL[:]
    FAIL.extend(saved)
    for name, r in rej:
        check(r, f"control not rejected: {name}")
        print(f"control {'REJECTED' if r else 'ACCEPTED (bad)'}: {name}")
    return all(r for _, r in rej)


def main():
    part_counts()
    _, tops, profs = part_recur()
    part_tail(profs)
    part_sens()
    part_shapes(tops)
    part_controls()
    if FAIL:
        print(f"FAIL ({len(FAIL)} checks)")
        return 1
    print("PASS_PROJECTION_RECURSION_CHECK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
