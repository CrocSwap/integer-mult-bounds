#!/usr/bin/env python3
"""Carrier-arc compilation under PR162's sufficient conditions.

Copyright 2026 DaysSky (PR162, research/extended-links/cxlinks.py), Apache-2.0; moved here unchanged apart from
this header and the imports (eumemic, Claude assistance). compile_graph() in frames.py accepts a carrier arc only
when the donor's coordinate-padded maximal frame already lies inside the receiving frame, which is sufficient but
not necessary. compile_closure() accepts any arc set whose generalized dependency graph is acyclic and whose full
backward intersections still contain every value span; scripts/paired_cube/verify.py checks those conditions
independently. With arcs that pass the pre-test and repository_order=True it returns compile_graph's record.
"""
import heapq
from collections import Counter

from paired_cube.frames import basis, perp, contained


def compile_closure(g, arcs, repository_order=False):
    """compile_graph() of scripts/paired_cube/frames.py for an arbitrary legal arc list [[donor node, use code], ...].

    Frames are the full backward intersections (as in the repository) and the positive-rank ledger is the
    repository's.  The operation order is (frame rank, generalized topological index); with repository_order it is
    the repository's own key (dimension of the coordinate-padded frame, node), which is a linear extension only for
    arcs that pass the repository's pre-test.  Raises AssertionError if the arc set is cyclic, if the order is not a
    linear extension, or if a value span leaves its frame."""
    g = dict(g)
    g['args'] = [None] + [None if a is None else [x + 1 for x in a] for a in g['args']]
    g['roots'] = [dict(r, node=r['node'] + 1) for r in g['roots']]
    h, inputs, args, roots = g['h'], g['inputs'], g['args'], g['roots']
    v, n, q = len(inputs), len(args), len(roots)
    spans = [()] * n
    for i, u in enumerate(inputs): spans[i + 1] = (u,)
    for x in range(v + 1, n):
        a, b = args[x]
        assert 0 < a < x and 0 < b < x
        spans[x] = basis(spans[a] + spans[b])
    rframe, rann, Y, targetH, ell = [], [], [() for _ in inputs], Counter(), 0
    for r in roots:
        x = r['node']
        if r.get('kind', 'side') == 'center':
            U = spans[x]; A = perp(U, h); ell += len(U)
        else:
            A = basis(inputs[t] for t in r['targets']); U = perp(A, h)
            for t in r['targets']:
                assert contained(Y[t], U), ('target retreat', t)
                targetH[len(U) - len(Y[t])] += 1; Y[t] = U
        assert contained(spans[x], U), ('root physical incompatibility', x)
        rframe.append(U); rann.append(A)
    for t in range(v):
        cap = perp((inputs[t],), h)
        assert contained(Y[t], cap)
        targetH[h - 1 - len(Y[t])] += 1
    active = set(range(1, v + 1)); todo = [r['node'] for r in roots]
    while todo:
        x = todo.pop()
        if x in active: continue
        active.add(x)
        if args[x]: todo.extend(args[x])
    arcs = dict(arcs)
    def use_node(code): return None if code >> 31 else code // 2
    def use_value(code): return roots[code & 0x7fffffff]['node'] if code >> 31 else args[code // 2][code & 1]
    succ, direct, indeg = [[] for _ in args], [[] for _ in args], [0] * n
    for x in sorted(active):
        if args[x]:
            for y in args[x]: succ[y].append(x); indeg[x] += 1
    for j, r in enumerate(roots): direct[r['node']].extend(rann[j])
    assert len(set(arcs.values())) == len(arcs), 'one donor per use'
    for x, code in arcs.items():
        assert args[x] and use_value(code) in args[x] and code not in (2 * x, 2 * x + 1), 'a donor carries one of its own operands'
        t = use_node(code)
        if t is None: direct[x].extend(rann[code & 0x7fffffff])
        else: succ[x].append(t); indeg[t] += 1
    heap = [x for x in sorted(active) if indeg[x] == 0]; heapq.heapify(heap); topo = []
    while heap:
        x = heapq.heappop(heap); topo.append(x)
        for y in succ[x]:
            indeg[y] -= 1
            if indeg[y] == 0: heapq.heappush(heap, y)
    assert len(topo) == len(active), 'the generalized dependency graph is acyclic'
    ann, rank = [None] * n, [0] * n
    for x in reversed(topo):
        ann[x] = basis(direct[x] + [z for y in succ[x] for z in ann[y]]); rank[x] = h - len(ann[x])
        assert contained(spans[x], perp(ann[x], h)), ('value span outside its frame', x)
    index = {x: i for i, x in enumerate(topo)}
    if repository_order:
        dag = [[] for _ in args]; constraint = [[] for _ in args]; padded = {}
        for x in sorted(active):
            if args[x]:
                for y in args[x]: dag[y].append(x)
        for j, r in enumerate(roots): constraint[r['node']].extend(rann[j])
        pre = [None] * n
        for x in sorted(active, reverse=True):
            pre[x] = basis(constraint[x] + [z for y in dag[x] for z in pre[y]])
            cover = g.get('side_padding_mask', 0)
            for u in spans[x]: cover |= u
            padded[x] = perp(pre[x] + tuple(1 << j for j in range(h) if not cover >> j & 1), h)
        order = sorted(active, key=lambda x: (len(padded[x]), x))
    else:
        order = sorted(active, key=lambda x: (rank[x], index[x]))
    position = {x: i for i, x in enumerate(order)}
    for x in order:
        for y in succ[x]: assert position[y] > position[x]
    uses = [[] for _ in args]
    for x in order:
        if args[x]:
            for j, y in enumerate(args[x]): uses[y].append(2 * x + j)
    for j, r in enumerate(roots): uses[r['node']].append((1 << 31) | j)
    donors = [x for x in order if args[x]]
    H = Counter()
    for x in order:
        r, degree = rank[x], len(uses[x]); assert degree > 0, ('unused input', x)
        H[r] += degree - 1
        if args[x]:
            H[h - r] += 1
            for y in args[x]:
                assert contained(ann[x], ann[y])
                H[r - rank[y]] += 1
        else: H[1] += 1; H[r - 1] += 1
    for j, rt in enumerate(roots):
        x = rt['node']; r = rank[x]; top = len(rframe[j]); assert r <= top
        if rt.get('kind', 'side') == 'center':
            assert r == top
            H[r] += 1; H[h - r] += 1
        else: H[top - r] += 1; H[h - top] += 1
    for x, code in arcs.items():
        value, t = use_value(code), use_node(code); rv, rd = rank[value], rank[x]
        top = rank[t] if t is not None else len(rframe[code & 0x7fffffff])
        assert top >= rd >= rv
        H[h - rd] -= 1; H[rv] -= 1; H[top - rv] -= 1; H[top - rd] += 1
    assert min(H.values()) >= 0
    R = len(donors) + q - len(arcs)
    mass = sum(r * c for r, c in H.items()); assert mass == h * R + ell, (mass, h * R + ell)
    source = Counter({int(r): c for r, c in g['source_data_histogram'].items()})
    assert sum(r * c for r, c in source.items()) == v * (h - 1)
    m, W = 3 * h, 2 * v + R
    children = Counter({r: 3 * c for r, c in H.items() if r})
    children.update({r: 3 * c for r, c in source.items() if r})
    children.update({r: 3 * c for r, c in targetH.items() if r})
    children[2] += 2 * v
    cmass = sum(r * c for r, c in children.items()); deficit = W * m - cmass
    assert deficit == 2 * v - 3 * ell
    profile = dict(h=h, v=v, R=R, q=q, c=len(donors), matched=len(arcs), loss=ell, selected_roles=0,
                   selected_rank_histogram={}, remaining_internal_histogram=[H[r] for r in range(h + 1)],
                   source_data_histogram=dict(source), target_data_histogram=dict(targetH), copied_centers_already=True,
                   m=m, W_per_vertex=W, rank_per_vertex=cmass, deficit_per_vertex=deficit,
                   child_histogram=dict(children), matching_frames='coordinate')
    witness = dict(matching_arcs=[[x, c] for x, c in arcs.items()], annihilators=ann, order=order)
    return profile, witness
