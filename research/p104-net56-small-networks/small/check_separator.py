#!/usr/bin/env python3
"""Exact, bounded check of explicit P104 NetW examples at #7852's pinned head.

Run with the adjacent p104_roots.json. If the two byte-exact pinned Lean
sources are also present, their Git blob IDs and extracted data are checked.
Only the Python standard library is used.
"""

import ast
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
SOURCES = {
    "DataIdA.lean": "a5b7ff35d74ca0810edd243a6655d930f22777c6",
    "DecoderWall4Data.lean": "90949f8d5dbcdee99974de505018768f4f9f640e",
}


def pinned_text(name):
    raw = (HERE / name).read_bytes()
    digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert digest == SOURCES[name], (name, digest)
    return raw.decode()


fixture_raw = (HERE / "p104_roots.json").read_bytes()
assert hashlib.sha256(fixture_raw).hexdigest() == "2693077172c0e3036fdc293f1d8d71d5f20830a3eb2a88c0cc4fc0623e6310b7"
fixture = json.loads(fixture_raw)
codes, labels = fixture["rootCode"], fixture["labs"]
if all((HERE / name).exists() for name in SOURCES):
    root_source = pinned_text("DataIdA.lean")
    label_source = pinned_text("DecoderWall4Data.lean")
    assert codes == ast.literal_eval(re.search(r"def rootCode : List Nat := (\[[^\n]*\])", root_source)[1])
    assert labels == ast.literal_eval(re.search(r"def labs : List ℕ := (\[[^\n]*\])", label_source)[1])
    print("source: both Git blob IDs and extracted lists match the pinned Lean sources")
else:
    print("source: fixture digest matched; adjacent Lean sources absent, so not rechecked")
roots = [[((c >> (3 * i)) & 7) - 2 for i in range(8)] for c in codes]
assert len(labels) == len(roots) == len(set(labels)) == 104
assert all(x.bit_count() % 2 == 1 and 0 <= x < 512 for x in labels)
assert all(sum(x * x for x in r) == 8 for r in roots)


def dot2(x, y):
    return (x & y).bit_count() & 1


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def echelon(vectors):
    pivots = {}
    for x in vectors:
        while x:
            i = x.bit_length() - 1
            if i in pivots:
                x ^= pivots[i]
            else:
                pivots[i] = x
                break
    return list(pivots.values())


def contains(vectors, x):
    return len(echelon(vectors + [x])) == len(echelon(vectors))


def orth(vectors):
    return echelon([x for x in range(512) if all(dot2(x, y) == 0 for y in vectors)])


# f_i are independent real functionals on the doubled E8 roots.  d_i are
# their (unnormalised) duals: f_i dot d_j = diag_i delta_ij.
f = [
    [0,0,0,0,-1,0,0,1], [-1,0,0,0,0,1,0,0],
    [-1,1,-1,-1,1,-1,1,1], [0,1,0,1,0,0,0,0],
    [0,1,0,0,1,0,0,0], [1,0,0,1,0,0,0,0],
    [0,0,0,0,0,-1,0,1], [-1,1,1,1,-1,1,1,1],
]
d = [
    [1,1,-1,-1,-1,1,-1,1], [-1,-1,-1,1,1,1,-1,1],
    [0,0,-1,0,0,0,1,0], [1,-1,1,-1,1,1,1,1],
    [1,1,1,-1,1,1,-1,1], [1,-1,-1,1,1,1,1,1],
    [-1,-1,1,1,1,-1,-1,1], [0,0,1,0,0,0,1,0],
]
diag = [2, 2, 2, -2, 2, 2, 2, 2]
fnorm = [7,25,42,76,104,162,448,491]
dnorm = [67,137,266,289,97,127,52,82]
assert [[dot(x,y) for y in d] for x in f] == [
    [diag[i] if i == j else 0 for j in range(8)] for i in range(8)
]


def base_network():
    a = [orth([x]) for x in fnorm]
    b = [[x] for x in dnorm]
    F = [[Q(dot(f[i], roots[p])) for p in range(104)] for i in range(8)]
    G = [[Q(dot(d[i], roots[s]), 8 * diag[i]) for i in range(8)] for s in range(104)]
    H = [[Q(0) for _ in range(8)] for _ in range(8)]
    return dict(a=a, b=b, F=F, G=G, H=H)


def split_one_read(base):
    p = next(p for p in range(104) if base["F"][0][p] != 0)
    n = 9
    a = [[labels[p]]] + [list(row) for row in base["a"]]
    b = [[labels[p]]] + [list(row) for row in base["b"]]
    F = [[Q(0) for _ in range(104)]] + [list(row) for row in base["F"]]
    F[0][p], F[1][p] = F[1][p], Q(0)
    G = [[Q(0)] + list(row) for row in base["G"]]
    H = [[Q(0) for _ in range(n)] for _ in range(n)]
    H[1][0] = Q(1)
    return dict(a=a, b=b, F=F, G=G, H=H), p


def split_all_reads(base):
    # Every P104 label has odd total parity, so a label has dot 0 with
    # exactly one of the normals 1 and 510=511 xor 1.  Split the first
    # old F row into those two 7-dimensional charts, then relay both into
    # the old node.  Both new nodes have a=b, hence zero drop.
    n = 10
    new_a = [orth([fnorm[0], 1]), orth([fnorm[0], 510])]
    a = new_a + [list(row) for row in base["a"]]
    b = [list(row) for row in new_a] + [list(row) for row in base["b"]]
    F = [[Q(0) for _ in range(104)] for _ in range(2)] + [list(row) for row in base["F"]]
    for p in range(104):
        j = dot2(labels[p], 1)
        F[j][p], F[2][p] = F[2][p], Q(0)
    G = [[Q(0), Q(0)] + list(row) for row in base["G"]]
    H = [[Q(0) for _ in range(n)] for _ in range(n)]
    H[2][0] = H[2][1] = Q(1)
    return dict(a=a, b=b, F=F, G=G, H=H)


def reverse(network):
    a,b,F,G,H = (network[x] for x in ("a", "b", "F", "G", "H"))
    n = len(a)
    rev = lambda k: n - 1 - k
    return dict(
        a=[orth(b[rev(k)]) for k in range(n)],
        b=[orth(a[rev(k)]) for k in range(n)],
        F=[[G[p][rev(k)] for p in range(104)] for k in range(n)],
        G=[[F[rev(k)][s] for k in range(n)] for s in range(104)],
        H=[[H[rev(j)][rev(k)] for j in range(n)] for k in range(n)],
    )


def verify(name, network):
    a,b,F,G,H = (network[x] for x in ("a", "b", "F", "G", "H"))
    n = len(a)
    assert all(len(echelon(b[k])) <= len(echelon(a[k])) for k in range(n))
    assert all(contains(a[k], x) for k in range(n) for x in b[k])
    for k in range(n):
        for p in range(104):
            assert not F[k][p] or contains(a[k], labels[p]), (name, "hF", k, p)
        for s in range(104):
            assert not G[s][k] or all(dot2(y, labels[s]) == 0 for y in b[k]), (name, "hG", s, k)
        for j in range(n):
            if H[k][j]:
                assert j < k, (name, "hHlt", k, j)
                assert all(contains(a[k], y) for y in b[j]), (name, "hH", k, j)
    # Exact recurrence N = I + H N.  H is strictly lower triangular.
    N = [[Q(i == j) for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            N[i][j] = Q(i == j) + sum(H[i][k] * N[k][j] for k in range(i))
    NF = [[sum(N[k][j] * F[j][p] for j in range(n)) for p in range(104)] for k in range(n)]
    M = [[sum(G[s][k] * NF[k][p] for k in range(n)) for p in range(104)] for s in range(104)]
    for s in range(104):
        for p in range(104):
            # c_s = 1; this checks every odd cell of NetW.hM, including the diagonal.
            if dot2(labels[s], labels[p]):
                assert M[s][p] == Q(s == p), (name, "hM", s, p, M[s][p])
            assert M[s][p] == Q(dot(roots[s], roots[p]), 8), (name, "Gram", s, p)
    gat = [k for k in range(n) if any(F[k])]
    dep = [k for k in range(n) if any(row[k] for row in G)]
    dims = [(len(echelon(a[k])), len(echelon(b[k]))) for k in range(n)]
    D = sum(max(x-y, 0) for x,y in dims)
    print(f"{name}: nodes={n}, gathers={len(gat)}, deposits={len(dep)}, D={D}")
    print(f"  (dim a, dim b) by node: {dims}")
    print(f"  gather dimensions: {[dims[k][0] for k in gat]}")
    return M, gat, dep, D, dims


base = base_network()
M0, g0, d0, D0, _ = verify("base", base)
split, port = split_one_read(base)
M1, g1, d1, D1, dims1 = verify("split", split)
M2, g2, d2, D2, dims2 = verify("reversed split", reverse(split))
two_low = split_all_reads(base)
M3, g3, d3, D3, dims3 = verify("two-low split", two_low)
M4, g4, d4, D4, dims4 = verify("reversed two-low split", reverse(two_low))
assert (len(g0),len(d0),D0) == (8,8,56)
assert (len(g1),len(d1),D1) == (9,8,56) and min(dims1[k][0] for k in g1) == 1
assert (len(g2),len(d2),D2) == (8,9,56) and max(dims2[k][1] for k in d2) == 8
assert (len(g3),len(d3),D3) == (9,8,56) and [dims3[k][0] for k in g3].count(7) == 2
assert (len(g4),len(d4),D4) == (8,9,56) and [dims4[k][1] for k in d4].count(2) == 2
assert M0 == M1 == M2 == M3 == M4
print(f"split port={port}, label={labels[port]}; all NetW and b≤a checks passed")
