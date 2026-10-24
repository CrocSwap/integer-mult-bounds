"""Idea 3: exact checks of the frame reduction + instance sizes (no solving).

Object O(k'): saturated uniform system on W(2k'-1,2), multiplicity m = 2^(5-k'),
unit lines, |cos| in {0, 1/4}, N = m(4^k'-1) lines in R^T, T = m(2^k'-1).
k'=4 is the 510-line object of line-system-saturation section 11.1; k'=3,2,1 are its
descendants under Proposition D1 (descent at one label merges q, q+p: m doubles).

Frame reduction (argument in REPORT.md section 2): by saturation the T lines
with labels in a fixed generator L are pairwise orthogonal, an orthonormal
frame e_1..e_T; every other unit line has u.e_c in {0, +-1/4} and norm 1, so
u = (1/4) * (+-1 on exactly 16 frame coordinates). Its support is fixed by the
labels: the m twins of each x in L with b(x,p) = 1. This script checks the
combinatorial facts exactly and counts the sizes of two encodings:
  E1 = direct +-1 signing S of the blown-up non-collinearity graph, S^2 = 60S+256I
  E2 = frame-reduced sign bits with XOR auxiliaries (what OPB file would hold)
With --write-opb K it writes the E2 instance for k' = K as an OPB file (it does
NOT run any solver).

Run:  py -3.12 frame_reduction.py [--write-opb 2]
"""
import datetime
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "progress.log")


def log(msg):
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def b(p, q, k):
    s = 0
    for i in range(k):
        s ^= ((p >> (2 * i)) & 1) & ((q >> (2 * i + 1)) & 1)
        s ^= ((p >> (2 * i + 1)) & 1) & ((q >> (2 * i)) & 1)
    return s


def build(k):
    m = 2 ** (5 - k)
    pts = list(range(1, 4 ** k))
    # generator L = span of the even coordinates (totally isotropic, dim k)
    L = [p for p in pts if all(((p >> (2 * i + 1)) & 1) == 0 for i in range(k))]
    assert len(L) == 2 ** k - 1
    Lset = set(L)
    coords = [(x, j) for x in L for j in range(m)]  # frame lines
    cidx = {c: i for i, c in enumerate(coords)}
    T = len(coords)
    others = [p for p in pts if p not in Lset]
    supp = {}
    for p in others:
        s = [cidx[(x, j)] for x in L if b(x, p, k) for j in range(m)]
        supp[p] = s
    return m, pts, L, others, supp, T


def check(k):
    m, pts, L, others, supp, T = build(k)
    N = m * len(pts)
    assert T == m * (2 ** k - 1) and N == m * (4 ** k - 1)
    sizes = {len(s) for s in supp.values()}
    # classes by functional f_p = b(., p)|_L
    cls = {}
    for p in others:
        key = tuple(b(x, p, k) for x in L)
        cls.setdefault(key, []).append(p)
    ok_class = all(len(v) == 2 ** k for v in cls.values()) and len(cls) == 2 ** k - 1
    # inside a class: collinear iff f(x) = f(y) where p = p0 + x
    ok_inside = True
    for key, members in cls.items():
        for p, q in itertools.combinations(members, 2):
            same_supp = supp[p] == supp[q]
            ok_inside &= same_supp
    # within each class the two collinearity groups have 16 vectors each
    ok_groups = True
    for key, members in cls.items():
        p0 = members[0]
        g0 = [q for q in members if q == p0 or b(p0, q, k) == 0]
        ok_groups &= (len(g0) * m == 16) and all(b(x, y, k) == 0 for x, y in itertools.combinations(g0, 2))
    inter = set()
    keys = list(cls)
    for k1, k2 in itertools.combinations(keys, 2):
        inter.add(len(set(supp[cls[k1][0]]) & set(supp[cls[k2][0]])))
    # per-line distance distribution
    p = pts[0]
    orth = (m - 1) + m * sum(1 for q in pts if q != p and b(p, q, k) == 0)
    ang = m * sum(1 for q in pts if b(p, q, k) == 1)
    log(f"k'={k}: m={m}, N={N} lines in R^{T}; non-frame lines {len(others)*m}; "
        f"support sizes {sorted(sizes)}; classes {len(cls)} x {2**k} points "
        f"(ok={ok_class}, same support inside class={ok_inside}, Hadamard-16 groups={ok_groups}); "
        f"cross-class support intersections {sorted(inter)}; per line: {orth} orthogonal + {ang} at 1/4")
    # sizes of encodings
    nv = len(others) * m
    pairs_in = len(cls) * (2 ** k * m) * (2 ** k * m - 1) // 2
    pairs_x = (len(cls) * (len(cls) - 1) // 2) * (2 ** k * m) ** 2
    ov = 8 if k >= 2 else 0
    e2_bits = nv * 16
    e2_xor = pairs_in * 16 + pairs_x * ov
    adj_edges = N * ang // 2
    common = ang // 2  # common neighbours of an adjacent pair (k'=4: 128)
    e1_pairs = N * (N - 1) // 2
    log(f"   E1 (direct signing): {adj_edges} edge-sign bits, {e1_pairs} pair constraints, "
        f"~{adj_edges*common + (e1_pairs-adj_edges)*ang:.3g} product terms")
    log(f"   E2 (frame-reduced): {e2_bits} sign bits, {pairs_in} in-class + {pairs_x} cross-class pair constraints, "
        f"{e2_xor} XOR auxiliaries")
    return dict(m=m, N=N, T=T, cls=cls, supp=supp, L=L, others=others,
                pairs=(pairs_in, pairs_x), e2=(e2_bits, e2_xor))


def write_opb(k, path):
    """E2 for k': x[v,c] sign bit of line v at frame coordinate c (value (-1)^x).
    Pair constraint for lines v, w with common support I:
      sum_{c in I} y_c = |I|/2          (orthogonal: twins, collinear labels)
      sum_{c in I} y_c = |I|/2 - 2 + 4z (|cos| = 1/4: non-collinear labels)
    with y_c = x[v,c] XOR x[w,c] (4 linear inequalities each).
    Gauge: x = 0 on a spanning forest of the line/coordinate incidence graph."""
    m, pts, L, others, supp, T = build(k)
    lines = [(p, j) for p in others for j in range(m)]
    var = {}

    def v(name):
        if name not in var:
            var[name] = len(var) + 1
        return var[name]

    cons = []
    # gauge by union-find
    parent = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    fixed = 0
    for li, (p, j) in enumerate(lines):
        for c in supp[p]:
            ra, rb = find(("l", li)), find(("c", c))
            if ra != rb:
                parent[ra] = rb
                cons.append(f"+1 x{v(('x', li, c))} = 0 ;")
                fixed += 1
    for (i1, (p, j)), (i2, (q, jj)) in itertools.combinations(enumerate(lines), 2):
        I = sorted(set(supp[p]) & set(supp[q]))
        if not I:
            continue
        ys = []
        for c in I:
            a, bb, y = v(("x", i1, c)), v(("x", i2, c)), v(("y", i1, i2, c))
            # y >= a - b, y >= b - a, y <= a + b, y <= 2 - a - b
            cons += [f"+1 x{y} -1 x{a} +1 x{bb} >= 0 ;",
                     f"+1 x{y} +1 x{a} -1 x{bb} >= 0 ;",
                     f"-1 x{y} +1 x{a} +1 x{bb} >= 0 ;",
                     f"-1 x{y} -1 x{a} -1 x{bb} >= -2 ;"]
            ys.append(y)
        orth = (p == q) or b(p, q, k) == 0
        lhs = " ".join(f"+1 x{y}" for y in ys)
        if orth:
            cons.append(f"{lhs} = {len(I)//2} ;")
        else:
            z = v(("z", i1, i2))
            cons.append(f"{lhs} -4 x{z} = {len(I)//2 - 2} ;")
    with open(path, "w", encoding="ascii") as f:
        f.write(f"* #variable= {len(var)} #constraint= {len(cons)}\n")
        f.write(f"* idea3 frame-reduced instance E2, k'={k}, m={2**(5-k)}; gauge-fixed bits {fixed}\n")
        f.write("\n".join(cons) + "\n")
    log(f"   wrote {os.path.basename(path)}: {len(var)} variables, {len(cons)} constraints, {fixed} gauge-fixed (NOT solved)")


def main():
    log("=== frame_reduction.py start (exact combinatorics, no solver) ===")
    for k in (1, 2, 3, 4):
        check(k)
    if "--write-opb" in sys.argv:
        k = int(sys.argv[sys.argv.index("--write-opb") + 1])
        write_opb(k, os.path.join(HERE, f"e2_k{k}.opb"))
    log("=== frame_reduction.py done ===")


if __name__ == "__main__":
    main()
