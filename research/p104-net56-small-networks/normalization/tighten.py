#!/usr/bin/env python3
"""Exact finite controls for support-saturated chart normalization."""
from pathlib import Path
import copy
import runpy
import sys

HERE = Path(__file__).resolve().parent
c = runpy.run_path(str(HERE / "check.py"))
z = runpy.run_path(str(HERE / "zero_drop.py"))
make, span, dot = c["make"], c["span"], c["dot"]
drop, dim, legal, transfer = c["drop"], c["dim"], c["legal"], c["transfer"]
net_from_small = z["net_from_small"]


def support_charts(N, j):
    """Incoming join L and its intersection with all outgoing constraints U."""
    L = {0}
    generators = [N.labels[p] for p in range(len(N.labels)) if N.F[j][p]]
    for y in range(len(N.H)):
        if N.H[j][y]:
            generators.extend(N.b[y])
    for v in generators:
        if v not in L:
            L |= {w ^ v for w in L}
    L = frozenset(L)
    B = frozenset(v for v in L
                  if all(not N.G[s][j] or not dot(v, N.labels[s])
                         for s in range(len(N.labels)))
                  and all(not N.H[x][j] or v in N.a[x]
                          for x in range(len(N.H))))
    return L, B


def potential(N, h):
    return (sum(map(dim, N.a)), sum(h - dim(b) for b in N.b))


def normalize(N, h):
    N = N.clone()
    legal(N)
    events = []
    while True:
        changed = False
        for j in range(len(N.H)):
            L, B = support_charts(N, j)
            if L == N.a[j] and B == N.b[j]:
                continue
            old_a, old_b, old_D = N.a[j], N.b[j], drop(N)
            old_potential = potential(N, h)
            assert L <= old_a and B <= L
            if L == old_a:
                assert old_b <= B
            N.a[j], N.b[j] = L, B
            legal(N)
            assert drop(N) <= old_D
            assert potential(N, h) < old_potential
            assert len(L) == len(B) * 2 ** (dim(L) - dim(B))
            events.append((j, dim(old_a), dim(old_b), dim(L), dim(B)))
            changed = True
        if not changed:
            break
    assert all(support_charts(N, j) == (N.a[j], N.b[j]) for j in range(len(N.H)))
    return N, events


def check(N, h):
    oldM, oldD = transfer(N), drop(N)
    H, F, G = copy.deepcopy(N.H), copy.deepcopy(N.F), copy.deepcopy(N.G)
    T, events = normalize(N, h)
    assert T.H == H and T.F == F and T.G == G
    assert transfer(T) == oldM and drop(T) <= oldD
    return T, events


def synthetic():
    # Each old b is nested.  Updating node 0 changes the relay chart available
    # to node 1, so the test exercises the iteration rather than a pointwise
    # independent chart simplification.
    from fractions import Fraction as Q
    N = make([1, 2], [span(1, 2, 4), span(1, 2, 4)], [span(2), span()])
    N.F[0][0] = N.G[0][0] = Q(1)
    N.F[1][1] = N.G[1][1] = Q(1)
    N.H[1][0] = Q(1)
    legal(N)
    T, events = check(N, 3)
    assert drop(N) == 5 and drop(T) == 2 and len(events) == 2
    print("synthetic fixed point: D=5 -> 2, two chart updates, all coefficients unchanged")


def stale_batch_control():
    from fractions import Fraction as Q
    N = make([1], [span(1), span(1)], [span(), span()])
    N.F[0][0] = N.H[1][0] = Q(1)
    legal(N)
    old_updates = [support_charts(N, j) for j in range(2)]
    # Applying both independently computed updates at once breaks relay 0->1.
    assert not old_updates[0][1] <= old_updates[1][0]
    T, events = check(N, 1)
    assert len(events) >= 1
    legal(T)
    print("stale-batch control: simultaneous updates break a relay; sequential updates stay legal")


def local_minimum_control():
    # Exhaust all subspace pairs in F2^3, and all legal chart choices for each
    # pair. This checks the local rank invoice, independent of the DAG code.
    subspaces = {span()}
    for v in range(1, 8):
        for S in tuple(subspaces):
            subspaces.add(frozenset(set(S) | {x ^ v for x in S}))
    assert len(subspaces) == 16
    for L in subspaces:
        for U in subspaces:
            invoice = dim(L) - dim(L & U)
            actual = min(dim(A) - dim(B) for A in subspaces if L <= A
                         for B in subspaces if B <= A and B <= U)
            assert invoice == actual
    print("local minimum: all 256 pairs of F2^3 subspaces passed exhaustive chart search")


def p104(small_dir):
    small = runpy.run_path(str(small_dir / "check_separator.py"))
    labels = small["labels"]
    for name, original in [("8/8", small["base"]), ("9/8 two-low", small["two_low"])]:
        N = net_from_small(original, labels)
        T, events = check(N, 9)
        assert drop(N) == 56 and drop(T) == 56 and len(events) == 0
        print("P104 %s fixed point: D=56 -> 56, %d chart updates" % (name, len(events)))


if __name__ == "__main__":
    small_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "01-net-small"
    synthetic()
    stale_batch_control()
    local_minimum_control()
    p104(small_dir)
    print("ALL CHART-NORMALIZATION CONTROLS PASSED")
