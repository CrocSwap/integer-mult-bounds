"""Exact checks for the non-existence of the 510-line signing (line-system-saturation section 11.1).

Standard library only. Every finite fact used by the proof in README.md is checked
exhaustively, plus a positive control (the k'=1 rung, 48 lines in R^16, built explicitly)
and the Delsarte inequalities showing that the two-point LP cannot decide the question.

    python3 -B research/line-system-510-signing-nonexistence/verify.py
"""
from fractions import Fraction as Fr
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  ({detail})" if detail else ""))
    if not ok:
        FAILS.append(name)


def b(p, q, k):
    """Standard symplectic form on F2^(2k), pairs (2i, 2i+1)."""
    s = 0
    for i in range(k):
        s ^= ((p >> (2 * i)) & 1) & ((q >> (2 * i + 1)) & 1)
        s ^= ((p >> (2 * i + 1)) & 1) & ((q >> (2 * i)) & 1)
    return s


# ---------------------------------------------------------------- 0. the open question we answer
def check_input():
    with open(os.path.join(ROOT, "research/line-system-saturation/README.md"), encoding="utf-8") as f:
        text = f.read()
    check("input: section 11.1 states the 510-vertex signing S^2 = 60S + 256I as OPEN",
          "510-vertex signing" in text and "S² = 60S + 256I" in text)


# ---------------------------------------------------------------- 1. frame form of the 120-line rung
def check_frame_form():
    k, m = 2, 8
    pts = range(1, 16)
    # coordinates (x1, y1, x2, y2) = bits (0, 1, 2, 3); L = <a, b>, a = x1, b = x2
    a, bb = 0b0001, 0b0100
    L = [a, bb, a ^ bb]
    check("L is totally isotropic", all(b(p, q, k) == 0 for p in L for q in L))
    check("labels and dimension", len(L) * m == 24 and len(pts) * m == 120)
    y1 = lambda p: (p >> 1) & 1
    y2 = lambda p: (p >> 3) & 1
    x1 = lambda p: p & 1
    x2 = lambda p: (p >> 2) & 1
    supp_ok = all((b(a, p, k), b(bb, p, k)) == (y1(p), y2(p)) for p in pts)
    check("b(a,p) = y1(p), b(b,p) = y2(p)", supp_ok)
    # every non-frame label is non-orthogonal to exactly 2 frame labels = 16 frame lines
    others = [p for p in pts if p not in L]
    check("each non-frame line meets 16 frame lines",
          all(sum(b(x, p, k) for x in L) * m == 16 for p in others))
    K1 = [p for p in others if (y1(p), y2(p)) == (1, 1)]   # support A u B
    K2 = [p for p in others if (y1(p), y2(p)) == (1, 0)]   # support A u C
    check("supports: K1 on A u B, K2 on A u C",
          all(b(a, p, k) and b(bb, p, k) and not b(a ^ bb, p, k) for p in K1)
          and all(b(a, p, k) and not b(bb, p, k) and b(a ^ bb, p, k) for p in K2)
          and len(K1) == 4 and len(K2) == 4)
    check("cross collinearity b(p,q) = x1(p) + x1(q) + x2(q)",
          all(b(p, q, k) == x1(p) ^ x1(q) ^ x2(q) for p in K1 for q in K2))
    check("K1 collinear iff x1+x2 equal",
          all(b(p, q, k) == (x1(p) ^ x2(p) ^ x1(q) ^ x2(q)) for p in K1 for q in K1 if p != q))
    P0 = [p for p in K1 if x1(p) == 0]
    check("the two points of P0 are non-collinear", len(P0) == 2 and b(P0[0], P0[1], k) == 1)
    groups = {}
    for p in K1:
        groups.setdefault(x1(p) ^ x2(p), []).append(p)
    check("each K1 collinearity group has one point of P0 and one of P1",
          all(sorted(x1(p) for p in g) == [0, 1] for g in groups.values()))


# ---------------------------------------------------------------- 2. finite lemmas of Step 3
def check_lemmas():
    S = list(itertools.product((1, -1), repeat=4))
    # (a) a row m with m.s = +-1 for all s in {+-1}^4: entries are forced into {0,+-1}
    # (flip one coordinate: 2 m_i in {0, +-2}); among those, exactly one non-zero entry.
    rows = [mm for mm in itertools.product((0, 1, -1), repeat=4)
            if all(abs(sum(u * v for u, v in zip(mm, s))) == 1 for s in S)]
    check("(a) linear maps {+-1}^4 -> {+-1}^4 have rows with one non-zero entry",
          len(rows) == 8 and all(sum(1 for t in mm if t) == 1 for mm in rows))
    # (b) the 8 lines s (mod sign); partitions into 4 + 4 with all cross |s.t| = 2
    lines = [s for s in S if s[0] == 1]
    dot = lambda s, t: sum(u * v for u, v in zip(s, t))
    parts = []
    for U in itertools.combinations(range(8), 4):
        V = [i for i in range(8) if i not in U]
        if all(abs(dot(lines[i], lines[j])) == 2 for i in U for j in V):
            parts.append(U)
    par = lambda s: sum(1 for t in s if t < 0) % 2
    ok = len(parts) == 2 and all(len({par(lines[i]) for i in U}) == 1 for U in parts)
    ok &= all(dot(lines[i], lines[j]) == 0 for U in parts for i, j in itertools.combinations(U, 2))
    check("(b) only the parity split works, and each parity class is pairwise orthogonal", ok,
          f"{len(parts)} ordered splits")
    # inner products in S0 = {(s, Ms)} are 2 s.t for a signed permutation M
    M = [(2, 1), (0, -1), (3, 1), (1, -1)]
    emb = lambda s: tuple(s) + tuple(sgn * s[i] for i, sgn in M)
    check("(a') (s,Ms).(t,Mt) = 2 s.t for a signed permutation M",
          all(dot(emb(s), emb(t)) == 2 * dot(s, t) for s in S for t in S))


# ---------------------------------------------------------------- 3. the contradiction (Step 4)
def check_contradiction():
    bad = [(d, t) for d in (8, -8) for t in range(-8, 9, 2) if abs(d + t) == 4 and abs(d - t) == 4]
    check("Step 4: no t with |8d+t| = |8d-t| = 4", not bad)
    # twins on one A-direction: (e, w), (e', w2) orthogonal with e' = +-e forces w2 = -+w
    S8 = list(itertools.product((1, -1), repeat=8))
    w = S8[37]
    forced = [w2 for w2 in S8 if 8 + sum(u * v for u, v in zip(w, w2)) == 0]
    check("Step 4: twin with the same A-part has B-part -w", forced == [tuple(-u for u in w)])


# ---------------------------------------------------------------- 4. positive control: the k'=1 rung
def check_control():
    """48 lines in R^16: frame + Sylvester rows + bent-shifted Sylvester rows (labels of W(1,2))."""
    xs = list(range(16))
    pc = lambda v: bin(v).count("1") & 1
    f = lambda x: ((x & 1) & ((x >> 1) & 1)) ^ (((x >> 2) & 1) & ((x >> 3) & 1))  # bent
    frame = [[4 if c == r else 0 for c in xs] for r in xs]
    H = [[(-1) ** pc(a & x) for x in xs] for a in xs]
    Hb = [[(-1) ** (pc(a & x) ^ f(x)) for x in xs] for a in xs]
    vecs = [(0, v) for v in frame] + [(1, v) for v in H] + [(2, v) for v in Hb]

    def violations(vs):
        bad = 0
        for (la, u), (lb, v) in itertools.combinations(vs, 2):
            d = sum(s * t for s, t in zip(u, v))
            bad += (d != 0) if la == lb else (abs(d) != 4)
        return bad

    check("control: 48 lines in R^16 with |cos| in {0,1/4} exist (exact)",
          violations(vecs) == 0 and all(sum(t * t for t in v) == 16 for _, v in vecs))
    broken = [(l, list(v)) for l, v in vecs]
    broken[20][1][3] *= -1
    check("failure control: one flipped sign is rejected", violations(broken) > 0)
    unbent = vecs[:32] + [(2, v) for v in H]
    check("failure control: two copies of the same basis are rejected", violations(unbent) > 0)


# ---------------------------------------------------------------- 5. Delsarte inequalities
def gegenbauer(n, kmax, t):
    lam = Fr(n - 2, 2)
    c, c1 = [Fr(1), 2 * lam * t], [Fr(1), 2 * lam]
    for k in range(1, kmax):
        c.append((2 * (k + lam) * t * c[k] - (k + 2 * lam - 1) * c[k - 1]) / (k + 1))
        c1.append((2 * (k + lam) * c1[k] - (k + 2 * lam - 1) * c1[k - 1]) / (k + 1))
    return [c[k] / c1[k] for k in range(kmax + 1)]


def check_delsarte():
    for n, a0, a1 in [(30, 253, 256), (28, 123, 128), (24, 55, 64), (16, 15, 32)]:
        q0, qa = gegenbauer(n, 40, Fr(0)), gegenbauer(n, 40, Fr(1, 4))
        vals = [1 + a0 * q0[k] + a1 * qa[k] for k in range(2, 41, 2)]
        check(f"Delsarte: R^{n}, distribution 1+{a0}+{a1}: degree 2 = 0, degrees 4..40 > 0",
              vals[0] == 0 and all(v > 0 for v in vals[1:]))


def main():
    check_input()
    check_frame_form()
    check_lemmas()
    check_contradiction()
    check_control()
    check_delsarte()
    if FAILS:
        print(f"FAIL {len(FAILS)} check(s)")
        return 1
    print("PASS_LINE_SYSTEM_510_SIGNING_NONEXISTENCE_FINITE_FACTS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
