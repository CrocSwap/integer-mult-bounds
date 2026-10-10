#!/usr/bin/env python3
"""The zeta family: a finite-network construction on the Boolean lattice.

Graph: inputs = all nonzero, non-full bitmasks of [h] (v = 2^h - 2).
DAG: the fast Yates zeta transform A_j(W) accumulators (h*2^(h-1) - (2^h-1) adds).
Roots: one side root per input t (except the all-ones target), delivering
Z_{full^t} = sum over inputs submasked into complement(t), i.e. bit-disjoint
from t. Their side-root contract (span contained in the orthogonal complement
of the targets' addresses) holds BY CONSTRUCTION: the zeta accumulates only
addresses bit-disjoint from t.
No centers: ell = 0; the compiler derives deficit = 2v.
"""


def zeta_graph(h):
    full = (1 << h) - 1
    masks = list(range(1, full))
    v = len(masks)
    idx = {u: i for i, u in enumerate(masks)}
    args = [None] * v
    prev = {u: idx[u] for u in masks}
    for j in range(h):
        cur = {}
        for W in masks:
            node = prev[W]
            lower = W ^ (1 << j)
            if (W >> j) & 1 and lower != 0 and lower in prev:
                args.append([node, prev[lower]])
                node = len(args) - 1
            cur[W] = node
        prev = cur
    roots = [dict(node=prev[full ^ t], kind='side', targets=[idx[t]]) for t in masks if full ^ t]
    src = {2: v}
    if h >= 4:
        src[1] = v * (h - 3)          # legal w(h-1) mass; the in-tree default
                                       # collapses at h in {5,6} (duplicate keys)
    return dict(h=h, inputs=masks, args=args, roots=roots, matching_frames='coordinate',
                source_data_histogram={str(r): n for r, n in src.items()})
