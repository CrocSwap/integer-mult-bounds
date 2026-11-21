#!/usr/bin/env python3
"""Exact rational and F2 controls for the P104 tight-edge note. No dependencies."""

from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import re
import sys


# DW4.labs at #7852 head 41beda1d6435760dc99e38bd7e65f36798aad212.
LABELS = [11, 19, 35, 131, 259, 13, 21, 37, 69, 133, 261, 41, 73, 265, 49,
          145, 161, 193, 321, 385, 14, 22, 38, 70, 134, 26, 74, 138, 50,
          146, 274, 194, 322, 386, 28, 44, 140, 84, 148, 276, 100, 292,
          196, 324, 388, 56, 88, 152, 168, 296, 200, 328, 392, 112, 176,
          304, 208, 336, 400, 224, 352, 416, 508, 506, 502, 494, 478, 446,
          382, 254, 505, 501, 493, 477, 445, 381, 253, 499, 475, 443, 379,
          251, 487, 471, 439, 375, 247, 463, 431, 367, 239, 415, 351, 223,
          319, 191, 81, 98, 164, 262, 268, 273, 280, 290]
SOURCE_SHA256 = "081bf16ed5e19930082ffb58548c6e6cded5c100f15332e797695e0cd07ef8c4"
FIXTURE = Path(__file__).with_name("data_p104.json")
FRAME = [0, 6, 16, 22, 29, 36, 45, 95]


def Z(r, c):
    return [[Q(0) for _ in range(c)] for _ in range(r)]


def span(*vs):
    s = {0}
    for v in vs:
        s |= {v ^ u for u in s}
    return frozenset(s)


def dot(x, y):
    return (x & y).bit_count() % 2


def dim(a):
    n = len(a)
    assert n and n & (n - 1) == 0
    return n.bit_length() - 1


@dataclass
class Net:
    labels: list
    a: list
    b: list
    H: list
    F: list
    G: list

    def clone(self):
        return Net(self.labels[:], self.a[:], self.b[:], [x[:] for x in self.H],
                   [x[:] for x in self.F], [x[:] for x in self.G])


def make(labels, a, b):
    n, p = len(a), len(labels)
    return Net(labels, a, b, Z(n, n), Z(n, p), Z(p, n))


def paths(H):
    """Return proper graph reachability (bit sets), not algebraic transfer."""
    n = len(H)
    reach = [sum(1 << v for v in range(n) if H[v][u]) for u in range(n)]
    for k in range(n):
        for i in range(n):
            if reach[i] >> k & 1:
                reach[i] |= reach[k]
    return reach


def dag(H):
    r = paths(H)
    return all(not (r[i] >> i & 1) for i in range(len(r)))


def solve(A, B):
    """Exact square inverse action, including for the explicit cyclic control."""
    n, m = len(A), len(B[0])
    W = [A[i][:] + B[i][:] for i in range(n)]
    for c in range(n):
        pivot = next((r for r in range(c, n) if W[r][c]), None)
        assert pivot is not None, "singular I-H"
        W[c], W[pivot] = W[pivot], W[c]
        scale = W[c][c]
        if scale != 1:
            W[c] = [x / scale for x in W[c]]
        for r in range(n):
            if r == c or W[r][c] == 0:
                continue
            scale = W[r][c]
            W[r] = [x - scale * y for x, y in zip(W[r], W[c])]
    return [row[n:n + m] for row in W]


def node_values(N):
    n = len(N.H)
    A = [[Q(i == j) - N.H[i][j] for j in range(n)] for i in range(n)]
    return solve(A, N.F)


def transfer(N):
    V = node_values(N)
    return [[sum((N.G[s][i] * V[i][p] for i in range(len(N.H))), Q(0))
             for p in range(len(N.labels))] for s in range(len(N.labels))]


def rank(M):
    A = [r[:] for r in M]
    nr, nc = len(A), len(A[0])
    row = 0
    for col in range(nc):
        p = next((i for i in range(row, nr) if A[i][col]), None)
        if p is None:
            continue
        A[row], A[p] = A[p], A[row]
        scale = A[row][col]
        A[row] = [x / scale for x in A[row]]
        for i in range(row + 1, nr):
            z = A[i][col]
            if z:
                A[i] = [x - z * y for x, y in zip(A[i], A[row])]
        row += 1
        if row == nr:
            break
    return row


def odd(M, labels):
    return [[M[s][p] if dot(labels[s], labels[p]) else Q(0)
             for p in range(len(labels))] for s in range(len(labels))]


def drop(N):
    return sum(dim(a) - dim(b) for a, b in zip(N.a, N.b))


def legal(N, require_dag=True):
    n, p = len(N.H), len(N.labels)
    assert len(N.a) == len(N.b) == n
    for k in range(n):
        assert N.b[k] <= N.a[k]
        for q in range(p):
            if N.F[k][q]:
                assert N.labels[q] in N.a[k]
            if N.G[q][k]:
                assert all(dot(v, N.labels[q]) == 0 for v in N.b[k])
        for j in range(n):
            if N.H[k][j]:
                assert N.b[j] <= N.a[k]
    if require_dag:
        assert dag(N.H)


def diagonal_odd(N, c):
    M = transfer(N)
    p = len(N.labels)
    assert all(M[s][t] == (c[s] if s == t else 0)
               for s in range(p) for t in range(p)
               if dot(N.labels[s], N.labels[t]))
    return M


def cover(N, j, k):
    H = [row[:] for row in N.H]
    H[k][j] = Q(0)
    return not (paths(H)[j] >> k & 1)


def contract(N, j, k):
    """General exact substitution; cover only required for the result to be a DAG."""
    n, p, eta = len(N.H), len(N.labels), N.H[k][j]
    assert j != k and eta and N.a[k] == N.b[j] and dag(N.H)
    T = N.clone()
    T.a[j], T.b[j], T.a[k], T.b[k] = span(), span(), N.a[j], N.b[k]
    T.H, T.F, T.G = Z(n, n), Z(n, p), Z(p, n)
    keep = [x for x in range(n) if x != j]
    for t in range(p):
        T.F[k][t] = N.F[k][t] + eta * N.F[j][t]
        T.G[t][k] = N.G[t][k] + N.G[t][j] / eta
        for x in keep:
            if x != k:
                T.F[x][t] = N.F[x][t] - N.H[x][j] / eta * N.F[k][t]
                T.G[t][x] = N.G[t][x] - N.G[t][j] / eta * N.H[k][x]
    for y in keep:
        if y != k:
            T.H[k][y] = N.H[k][y] + eta * N.H[j][y]
    for x in keep:
        if x != k:
            T.H[x][k] = N.H[x][k] + N.H[x][j] / eta
            for y in keep:
                if y != k:
                    T.H[x][y] = N.H[x][y] - N.H[x][j] / eta * N.H[k][y]
    return T


def check_equation(N, T, j, k):
    A, B = transfer(N), transfer(T)
    for s in range(len(N.labels)):
        for p in range(len(N.labels)):
            assert B[s][p] - A[s][p] == N.G[s][j] * N.F[k][p] / N.H[k][j]
    assert odd(A, N.labels) == odd(B, N.labels)
    assert drop(N) == drop(T)


def legacy_unchecked(N, j, k, keep_other_k_inputs=False):
    """NetContract formulas, applied beyond their hypotheses, plus one naive repair."""
    T = N.clone()
    eta = N.H[k][j]
    T.a[j], T.b[j], T.a[k], T.b[k] = span(), span(), N.a[j], N.b[k]
    for p in range(len(N.labels)):
        T.F[j][p] = 0
        T.F[k][p] = N.F[k][p] + eta * N.F[j][p]
        T.G[p][j] = 0
        T.G[p][k] = N.G[p][k] + N.G[p][j] / eta
    for x in range(len(N.H)):
        T.H[x][j] = T.H[j][x] = 0
    for y in range(len(N.H)):
        if y != j:
            T.H[k][y] = eta * N.H[j][y] + (N.H[k][y] if keep_other_k_inputs else 0)
    return T


def p104_control():
    assert len(LABELS) == len(set(LABELS)) == 104
    assert all(0 < x < 512 and dot(x, x) == 1 for x in LABELS)
    c = [Q(1, 2) if s % 2 == 0 else Q(1) for s in range(104)]
    charts = [span(LABELS[0]), span(LABELS[0])] + [span(q) for q in LABELS[1:]]
    N = make(LABELS[:], charts, [span()] * 105)
    N.H[1][0] = Q(1)
    N.F[0][0] = N.F[1][0] = Q(1)
    N.G[0][0], N.G[0][1] = c[0] / 2, c[0] / 4
    for s in range(1, 104):
        N.F[s + 1][s] = Q(1)
        N.G[s][s + 1] = c[s]
    legal(N)
    M = diagonal_odd(N, c)
    assert all(M[s][p] == (c[s] if s == p else 0)
               for s in range(104) for p in range(104))
    assert rank(M) == 104 and drop(N) == 105
    edges = [(j, k) for k in range(105) for j in range(105) if N.H[k][j]]
    assert edges == [(0, 1)]
    assert all(N.b[j] != N.a[k] for j, k in edges)
    assert all(any(N.F[k]) and any(row[k] for row in N.G) for k in (0, 1))
    print("P104: actual labels=104, nodes=105, exact transfer=diag(c), rank=104,")
    print("      c in {1,1/2}, drop=105, relay edges=1, tight edges=0, two forced hubs")


def compact_p104_control(data):
    # Build the source Gram factorization using the orthogonal 8-frame shared
    # by the independent-challenge lane, then add one zero-drop slack relay.
    rows = data["gramRows"]
    gram = [[(rows[i] >> (2 * j) & 3) - 1 for j in range(104)] for i in range(104)]
    assert all(gram[i][j] == gram[j][i] for i in range(104) for j in range(104))
    assert all(gram[i][j] == (2 if i == j else 0) for i in FRAME for j in FRAME)
    A = [[gram[i][j] for j in FRAME] for i in range(104)]
    assert all(sum(A[i][k] * A[j][k] for k in range(8)) == 2 * gram[i][j]
               for i in range(104) for j in range(104))
    assert all(gram[i][j] == 0 for i in range(104) for j in range(104)
               if i != j and dot(LABELS[i], LABELS[j]))
    c = [Q(1, 2) if s % 2 == 0 else Q(1) for s in range(104)]
    support = [[i for i in range(104) if A[i][r]] for r in range(8)]
    chart = [span(*(LABELS[i] for i in support[r])) for r in range(8)]
    assert all(len(s) == 49 for s in support) and all(dim(a) == 9 for a in chart)
    at = lambda r: 0 if r == 0 else r + 1
    N = make(LABELS[:], [chart[0], span()] + chart[1:], [span()] * 9)
    for r in range(8):
        for i in range(104):
            N.F[at(r)][i] = Q(A[i][r], 2)
            N.G[i][at(r)] = c[i] * Q(A[i][r], 2)
    legal(N)
    base = diagonal_odd(N, c)
    assert rank(base) == 8 and drop(N) == 72
    assert all(base[s][p] == c[s] * Q(gram[s][p], 2)
               for s in range(104) for p in range(104))
    # j=0, k=1.  Put both F and G on k while compensating G at j.
    # The sole new outer product is at the even pair (output 1,input 0).
    assert dot(LABELS[0], LABELS[1]) == 0
    N.a[1] = N.b[1] = span(LABELS[0])
    N.H[1][0] = N.F[1][0] = N.G[1][1] = Q(1)
    N.G[1][0] -= 1
    legal(N)
    M = diagonal_odd(N, c)
    assert all(M[s][p] - base[s][p] == (1 if (s, p) == (1, 0) else 0)
               for s in range(104) for p in range(104))
    edges = [(j, k) for k in range(9) for j in range(9) if N.H[k][j]]
    assert edges == [(0, 1)] and N.b[0] < N.a[1]
    assert all(any(N.F[k]) and any(row[k] for row in N.G) for k in (0, 1))
    assert all(any(N.F[k]) and any(row[k] for row in N.G) for k in range(9))
    assert drop(N) == 72
    print("P104 compact: 9 gatherers, 9 depositors, D=72, rank %d -> %d," % (rank(base), rank(M)))
    print("              one slack edge, no tight edge, two forced hubs; odd transfer preserved")


def series_control():
    N = make([1, 2], [span(1, 2), span(2)], [span(2), span()])
    N.H[1][0] = Q(2)
    N.F[0][0] = N.F[1][1] = N.G[0][0] = N.G[1][1] = Q(1)
    legal(N)
    diagonal_odd(N, [Q(1), Q(1)])
    T = contract(N, 0, 1)
    legal(T)
    check_equation(N, T, 0, 1)
    assert transfer(T)[0][1] == Q(1, 2)  # lost direct term is on an even cell
    print("series: drop=2 -> 2; odd transfer preserved; even correction=1/2")


def merge_controls():
    # q_0 . q_1 = 1 and both labels have odd self-dot.
    N = make([1, 7], [span(7), span(1, 6), span(6)], [span(), span(6), span()])
    N.H[2][0], N.H[2][1] = Q(1, 2), Q(2)
    N.F[0][1], N.F[1][0] = Q(2), Q(1, 2)
    N.G[0][1], N.G[1][1], N.G[1][2] = Q(2), Q(-2), Q(1)
    legal(N)
    M = diagonal_odd(N, [Q(1), Q(1)])
    assert M == [[Q(1), Q(0)], [Q(0), Q(1)]]
    L = legacy_unchecked(N, 1, 2)
    legal(L)
    assert drop(L) == drop(N) == 3
    assert transfer(L) == [[Q(1), Q(0)], [Q(0), Q(0)]]
    assert rank(M) == 2 and rank(transfer(L)) == 1
    N.G = Z(2, 3)
    N.F[0][1] = Q(1)
    N.G[0][1] = Q(2)
    N.G[1][0] = Q(1)
    legal(N)
    diagonal_odd(N, [Q(1), Q(1)])
    L = legacy_unchecked(N, 1, 2, keep_other_k_inputs=True)
    legal(L)
    assert transfer(L) == [[Q(1), Q(1, 2)], [Q(0), Q(1)]]
    assert dot(N.labels[0], N.labels[1]) == 1
    T = contract(N, 1, 2)
    legal(T)
    check_equation(N, T, 1, 2)
    print("merge: unchecked existing formula rank 2 -> 1; naive input-preserving repair")
    print("       creates forbidden odd off-diagonal 1/2; full substitution preserves odd transfer")


def branching_cover_control():
    # j=0, u=1, k=2, x=3; j->k, u->k, j->x, no other j->k path.
    N = make([1, 7, 2], [span(1, 2), span(7), span(2), span(2)],
             [span(2), span(), span(), span()])
    N.H[2][0], N.H[2][1], N.H[3][0] = Q(2), Q(1, 2), Q(3, 2)
    N.F[0][0], N.F[1][1], N.F[2][2] = Q(1, 2), Q(1), Q(1, 3)
    N.G[0][0], N.G[1][1] = Q(2), Q(1)
    N.G[2][1], N.G[2][2], N.G[2][3] = Q(-3, 2), Q(3), Q(1)
    legal(N)
    diagonal_odd(N, [Q(1), Q(1), Q(1)])
    assert cover(N, 0, 2)
    T = contract(N, 0, 2)
    legal(T)
    check_equation(N, T, 0, 2)
    assert T.H[3][1] == Q(-3, 8)
    assert not (paths(N.H)[1] >> 3 & 1) and (paths(T.H)[1] >> 3 & 1)
    assert node_values(N)[3][1] == node_values(T)[3][1] == 0
    print("branching cover: D=4 -> 4, odd transfer preserved, new u->x reachability;")
    print("                 new direct u->x edge -3/8 cancels the indirect transfer")


def cancellation_control():
    N = make([1, 2], [span(1, 2), span(2), span(2)], [span(2), span(), span()])
    N.H[1][0], N.H[2][0], N.H[2][1] = Q(2), Q(-1), Q(1, 2)
    N.F[0][0] = N.F[1][1] = N.G[0][0] = N.G[1][2] = Q(1)
    N.G[1][1] = Q(1, 2)
    legal(N)
    diagonal_odd(N, [Q(1), Q(1)])
    assert cover(N, 0, 1) and paths(N.H)[1] >> 2 & 1
    T = contract(N, 0, 1)
    legal(T)
    check_equation(N, T, 0, 1)
    assert T.H[2][1] == 0 and not (paths(T.H)[1] >> 2 & 1)
    print("cancellation: original k->x reachability is deleted after the exact substitution")


def alternate_path_control():
    N = make([1, 2], [span(1, 2), span(2), span(2)], [span(2), span(), span()])
    N.H[1][0], N.H[2][0], N.H[2][1] = Q(1, 2), Q(2), Q(1, 2)
    N.F[0][0] = N.F[2][1] = N.G[0][0] = N.G[1][1] = N.G[1][2] = Q(1)
    legal(N)
    diagonal_odd(N, [Q(1), Q(1)])
    assert not cover(N, 0, 2)
    T = contract(N, 0, 2)
    legal(T, require_dag=False)
    check_equation(N, T, 0, 2)
    assert T.H[1][1] == Q(-1, 8) and not dag(T.H)
    print("alternate path: substitution preserves drop and odd transfer but creates")
    print("                an inadmissible self-loop of weight -1/8")


def main():
    data = json.loads(FIXTURE.read_text())
    assert data["source_commit"] == "41beda1d6435760dc99e38bd7e65f36798aad212"
    assert data["source_blob"] == "90949f8d5dbcdee99974de505018768f4f9f640e"
    assert data["labs"] == LABELS and len(data["gramRows"]) == 104
    if len(sys.argv) > 1:
        source = Path(sys.argv[1]).read_bytes()
        assert sha256(source).hexdigest() == SOURCE_SHA256
        match = re.search(rb"def labs : List \xe2\x84\x95 := \[([^]]+)\]", source)
        assert match
        assert [int(x.strip()) for x in match.group(1).split(b",")] == LABELS
        match = re.search(rb"def gramRows : List \xe2\x84\x95 := \[([^]]+)\]", source)
        assert match
        assert [int(x) for x in re.findall(rb"\d+", match.group(1))] == data["gramRows"]
        print("source SHA-256, 104 labels and packed Gram rows: matched")
    p104_control()
    compact_p104_control(data)
    series_control()
    merge_controls()
    branching_cover_control()
    cancellation_control()
    alternate_path_control()
    print("ALL EXACT CONTROLS PASSED")


if __name__ == "__main__":
    main()
