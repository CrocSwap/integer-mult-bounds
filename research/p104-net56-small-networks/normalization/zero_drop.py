#!/usr/bin/env python3
"""Zero-drop routing normalization and D=56 P104 boundary controls.

Run beside check.py, with the sibling 01-net-small directory available. The
small-case checker and its source-pinned data are read, never modified.
"""
from fractions import Fraction as Q
from pathlib import Path
import copy
import runpy
import sys

HERE = Path(__file__).resolve().parent
c = runpy.run_path(str(HERE / "check.py"))
Net, make, span = c["Net"], c["make"], c["span"]
legal, transfer, drop = c["legal"], c["transfer"], c["drop"]
dim, odd, dot, dag, rank = c["dim"], c["odd"], c["dot"], c["dag"], c["rank"]
diagonal_odd = c["diagonal_odd"]


def graph_reach(N):
    """Reachability among nodes, input ports, and separate output ports."""
    n, p = len(N.H), len(N.labels)
    size = n + 2 * p
    adj = [set() for _ in range(size)]
    for x in range(n):
        for y in range(n):
            if N.H[x][y]:
                adj[y].add(x)
        for q in range(p):
            if N.F[x][q]:
                adj[n + q].add(x)
            if N.G[q][x]:
                adj[x].add(n + p + q)
    reach = []
    for source in range(size):
        seen, todo = set(), list(adj[source])
        while todo:
            v = todo.pop()
            if v not in seen:
                seen.add(v)
                todo.extend(adj[v] - seen)
        reach.append(seen)
    return reach


def topological(N):
    """Reindex to Fin n order and return old-to-new node map."""
    n = len(N.H)
    rem = set(range(n))
    order = []
    while rem:
        choices = [k for k in sorted(rem) if not any(N.H[k][j] for j in rem)]
        assert choices, "cycle"
        k = choices[0]
        rem.remove(k)
        order.append(k)
    back = {old: new for new, old in enumerate(order)}
    T = Net(N.labels[:], [N.a[i] for i in order], [N.b[i] for i in order],
            [[N.H[i][j] for j in order] for i in order],
            [N.F[i][:] for i in order],
            [[row[j] for j in order] for row in N.G])
    assert all(not T.H[k][j] or j < k for k in range(n) for j in range(n))
    return T, back


def split_node(N, j):
    assert dag(N.H)
    n, p = len(N.H), len(N.labels)
    ins = [("node", y, N.H[j][y]) for y in range(n) if N.H[j][y]]
    ins += [("port", q, N.F[j][q]) for q in range(p) if N.F[j][q]]
    outs = [("node", x, N.H[x][j]) for x in range(n) if N.H[x][j]]
    outs += [("port", q, N.G[q][j]) for q in range(p) if N.G[q][j]]
    keep = [i for i in range(n) if i != j]
    pairs = [(u, v) for u in ins for v in outs]
    # For each route use the least input chart L and b=L intersect U, where U
    # is the target chart or the orthogonal complement of the output label.
    aa, bb = [], []
    for (ik, iv, _), (ok, ov, _) in pairs:
        L = N.b[iv] if ik == "node" else span(N.labels[iv])
        B = (L & N.a[ov]) if ok == "node" else frozenset(v for v in L if not dot(v, N.labels[ov]))
        aa.append(L)
        bb.append(B)
    a = [N.a[i] for i in keep] + aa
    b = [N.b[i] for i in keep] + bb
    T = make(N.labels[:], a, b)
    index = {old: new for new, old in enumerate(keep)}
    for x in keep:
        for y in keep:
            T.H[index[x]][index[y]] = N.H[x][y]
        T.F[index[x]] = N.F[x][:]
        for q in range(p):
            T.G[q][index[x]] = N.G[q][x]
    for i, ((ik, iv, iw), (ok, ov, ow)) in enumerate(pairs):
        clone = len(keep) + i
        if ik == "node":
            T.H[clone][index[iv]] = iw
        else:
            T.F[clone][iv] = iw
        if ok == "node":
            T.H[index[ov]][clone] = ow
        else:
            T.G[ov][clone] = ow
    T, reordered = topological(T)
    mapping = {old: reordered[new] for old, new in index.items()}
    clones = [reordered[len(keep) + i] for i in range(len(pairs))]
    return T, mapping, clones, len(ins), len(outs)


def check_split(N, j):
    legal(N)
    before = graph_reach(N)
    T, mapping, clones, num_in, num_out = split_node(N, j)
    legal(T)
    assert transfer(T) == transfer(N)
    invoice = sum(dim(T.a[k]) - dim(T.b[k]) for k in clones)
    old_drop = dim(N.a[j]) - dim(N.b[j])
    assert drop(T) == drop(N) - old_drop + invoice
    assert len(clones) == num_in * num_out
    for k in clones:
        assert sum(bool(v) for v in T.F[k]) + sum(bool(v) for v in T.H[k]) == 1
        assert sum(bool(row[k]) for row in T.G) + sum(bool(row[k]) for row in T.H) == 1
    oldn, newn, p = len(N.H), len(T.H), len(N.labels)
    vertex = dict(mapping)
    vertex.update({oldn + q: newn + q for q in range(p)})
    vertex.update({oldn + p + q: newn + p + q for q in range(p)})
    after = graph_reach(T)
    assert all((y in before[x]) == (vertex[y] in after[vertex[x]])
               for x in vertex for y in vertex)
    return T, mapping, clones


def small_cancellation_control():
    N = make([1, 7, 2], [span(1), span(7), span(2), span(2), span(2)],
             [span(), span(), span(2), span(), span()])
    N.F[0][0], N.F[1][1], N.F[2][2] = Q(1), Q(1), Q(2)
    N.H[2][0], N.H[2][1] = Q(1), Q(2)
    N.H[3][2], N.H[4][2], N.H[3][0] = Q(1), Q(-2), Q(-1)
    N.G[0][2], N.G[1][3], N.G[0][4] = Q(3), Q(1), Q(1)
    assert N.H[3][0] + N.H[3][2] * N.H[2][0] == 0
    old_reach = graph_reach(N)
    n, p = len(N.H), len(N.labels)
    assert n + p + 1 in old_reach[n + 0]  # input 0 -> output 1
    T, mapping, clones = check_split(N, 2)
    assert len(clones) == 9 and drop(T) == 4 and all(T.a[k] == T.b[k] for k in clones)
    assert transfer(N)[1][0] == 0  # two nonzero paths cancel algebraically
    print("zero-drop fan routing: 3 incoming x 3 outgoing = 9 zero-drop clones;")
    print("  exact full transfer and every retained-node/terminal reachability preserved")
    print("  cancellation control: graph input 0 -> output 1 persists although transfer is 0")


def paid_normalization_control():
    N = make([1, 2, 7], [span(1, 2, 4)], [span()])
    for p in range(3):
        N.F[0][p] = N.G[p][0] = Q(1)
    T, mapping, clones = check_split(N, 0)
    assert len(clones) == 9 and drop(N) == 3 and drop(T) == 7
    assert sum(dim(T.a[k]) - dim(T.b[k]) for k in clones) == 7
    print("paid fan routing: exact rank invoice 7 versus original node drop 3")


def net_from_small(base, labels):
    return Net(labels[:], [span(*a) for a in base["a"]],
               [span(*b) for b in base["b"]],
               [row[:] for row in base["H"]], [row[:] for row in base["F"]],
               [row[:] for row in base["G"]])


def p104_boundary_and_review(small_dir):
    source = small_dir / "check_separator.py"
    small = runpy.run_path(str(source))
    labels, original = small["labels"], small["base_network"]()
    assert labels == c["LABELS"]
    original = copy.deepcopy(original)
    cs = [Q(1, 2) if s % 2 == 0 else Q(1) for s in range(104)]
    for s in range(104):
        original["G"][s] = [cs[s] * x for x in original["G"][s]]
    base = net_from_small(original, labels)
    legal(base)
    M0 = diagonal_odd(base, cs)
    assert drop(base) == 56
    ins = [p for p in range(104) if base.F[0][p]]
    outs = [s for s in range(104) if base.G[s][0]]
    price = sum(dot(labels[p], labels[s]) for p in ins for s in outs)
    assert (len(ins), len(outs), price) == (52, 52, 1462)
    assert dim(base.a[0]) - dim(base.b[0]) == 7
    print("P104 paid fan invoice: 52 x 52 routes, cost 1462 versus original drop 7")
    # Same construction as base, with one extra zero-drop slack-relay node.
    orig_index = lambda r: 0 if r == 0 else r + 1
    a = [base.a[0], span(67, 11)] + base.a[1:]
    b = [base.b[0], span(67, 11)] + base.b[1:]
    N = make(labels[:], a, b)
    for r in range(8):
        k = orig_index(r)
        N.F[k] = base.F[r][:]
        for s in range(104):
            N.G[s][k] = base.G[s][r]
    assert labels[0] == 11 and labels[1] == 19 and base.b[0] == span(67)
    assert dot(11, 19) == dot(67, 19) == 0
    assert base.b[0] < N.a[1] and dim(N.a[1]) == 2
    N.H[1][0] = N.F[1][0] = N.G[1][1] = Q(1)
    N.G[1][0] -= 1
    legal(N)
    M = diagonal_odd(N, cs)
    assert all(M[s][p] - M0[s][p] == (1 if (s, p) == (1, 0) else 0)
               for s in range(104) for p in range(104))
    assert drop(N) == 56 and rank(M0) == 8
    assert all(any(N.F[k]) and any(row[k] for row in N.G) for k in range(9))
    assert [(j, k) for k in range(9) for j in range(9) if N.H[k][j]] == [(0, 1)]
    assert N.b[0] != N.a[1]  # sole edge is slack; both endpoints forced hubs
    T, mapping, clones = check_split(N, 1)
    assert len(clones) == 2 and drop(T) == 56
    print("P104 equality boundary: 9 gatherers, 9 depositors, D=56; one slack edge")
    print("  two forced hubs block tight-contraction-only-to-bowtie; odd matrix unchanged")
    print("  zero-drop normalization replaces its sink with 2 clones at the same D")

    # Independently exercise the reciprocal reviewer claim with nonconstant c.
    split = copy.deepcopy(small["split"])
    for s in range(104):
        split["G"][s] = [cs[s] * x for x in split["G"][s]]
    before = net_from_small(split, labels)
    after = net_from_small(small["reverse"](split), labels)
    legal(before)
    legal(after)
    A = diagonal_odd(before, cs)
    B = diagonal_odd(after, cs)
    assert all(B[s][p] == A[p][s] for s in range(104) for p in range(104))
    assert all(dim(before.a[k]) - dim(before.b[k]) ==
               dim(after.a[8-k]) - dim(after.b[8-k]) for k in range(9))
    print("transpose review: alternating c_s in {1/2,1}, exact M^T, all odd cells,")
    print("  charts, relay support and per-node drops verified")


def main():
    small_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "01-net-small"
    small_cancellation_control()
    paid_normalization_control()
    p104_boundary_and_review(small_dir)
    print("ALL ZERO-DROP AND RECIPROCAL CONTROLS PASSED")


if __name__ == "__main__":
    main()
