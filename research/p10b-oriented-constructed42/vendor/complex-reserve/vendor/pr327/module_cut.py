#!/usr/bin/env python3
"""module_cut.py: zero restriction of a query module to fewer points (p = 11 module files -> p = 10).

Setting the inputs that touch the dropped points to zero turns a module for n points into a module for n - k points:
an addition with one zero operand becomes its other operand, an addition of two live operands is kept (merged with an
equal-support node if one exists), and nodes that no kept root reaches are removed. The roots of the dropped labels
are discarded. The result satisfies the smaller module's contract whenever the original satisfies its own (every
root of a kept label still sums exactly its kept disjoint inputs); the loaders of the rebuilt tree check this.
min_cut() drops the points that leave the fewest additions (ties: lexicographically first drop), the rule by which the
control modules of this package (PR #168 v4's modules cut to p = 10) were made; verify.py re-derives them byte for byte.

Prepared by DreamingOfClouds with Anthropic Claude assistance (Apache-2.0); the cut is cp10's mkmods.py, unchanged
apart from file layout.
usage: module_cut.py KIND N_FROM K MODULE_JSON OUT_JSON      (KIND tmod: N = p; pmod: N = p - 1; qmod: N = p - 2)
"""
import json
import sys
from itertools import combinations
from pathlib import Path


def restrict(args, inputs_image, nin, roots_old, one_based):
    """generic zero restriction: inputs_image[k] = new input index or None (zero); returns (args, roots) pruned."""
    off = 1 if one_based else 0
    n_new = sum(1 for x in inputs_image if x is not None)
    support = [1 << i for i in range(n_new)]
    new_args = [None] * n_new
    by = {s: i for i, s in enumerate(support)}
    image = list(inputs_image)
    for x in range(nin + off, len(args)):
        a, b = args[x]
        A, B = image[a - off], image[b - off]
        if A is None or B is None:
            image.append(A if B is None else B)
            continue
        assert not support[A] & support[B]
        s = support[A] | support[B]
        if s not in by:
            by[s] = len(new_args); new_args.append([A, B]); support.append(s)
        image.append(by[s])
    roots = [image[r - off] for r in roots_old]
    active = set(range(n_new)); stack = list(roots)
    while stack:
        x = stack.pop()
        if x in active:
            continue
        active.add(x)
        if new_args[x] is not None:
            stack.extend(new_args[x])
    ids = sorted(active); ren = {x: i for i, x in enumerate(ids)}
    args2 = [None if new_args[x] is None else [ren[y] for y in new_args[x]] for x in ids]
    return args2, [ren[x] for x in roots], support, ren, ids


def cut_triple(d, P, keep):
    labels = list(combinations(range(P), 3))
    keep = sorted(keep); rn = {x: j for j, x in enumerate(keep)}; p2 = len(keep)
    new_labels = list(combinations(range(p2), 3)); nid = {t: i for i, t in enumerate(new_labels)}
    img = [nid[tuple(rn[x] for x in t)] if all(x in rn for x in t) else None for t in labels]
    roots_old = [r for t, r in zip(labels, d['roots']) if all(x in rn for x in t)]
    args, roots, support, ren, ids = restrict(d['args'], img, len(labels), roots_old, one_based=True)
    # back to the one-based layout of triple_module_from
    n = len(new_labels)
    out_args = [[0, 0]] * (n + 1) + [[x + 1, y + 1] for x, y in (a for a in args[n:])]
    return dict(kind='disjoint_triples', p=p2, input_labels=new_labels, target_labels=new_labels, input_count=n,
                args=out_args, roots=[r + 1 for r in roots], source='cp10 zero restriction to points %s' % keep)


def cut_pair(d, n, keep):
    pairs = list(combinations(range(n), 2))
    keep = sorted(keep); rn = {x: j for j, x in enumerate(keep)}; n2 = len(keep)
    new_pairs = list(combinations(range(n2), 2)); nid = {t: i for i, t in enumerate(new_pairs)}
    img = [nid[tuple(rn[x] for x in t)] if all(x in rn for x in t) else None for t in pairs]
    roots_old = [r for t, r in zip(pairs, d['roots']) if all(x in rn for x in t)]
    extra = d['roots'][len(pairs):]
    args, roots, *_ = restrict(d['args'], img, len(pairs), roots_old + extra, one_based=False)
    return dict(input_count=len(new_pairs), args=args, roots=roots, source='cp10 zero restriction to points %s' % keep)


def cut_q(d, n, keep):
    keep = sorted(keep); rn = {x: j for j, x in enumerate(keep)}
    img = [rn.get(i) for i in range(n)]
    roots_old = [d['roots'][i] for i in keep]
    args, roots, *_ = restrict(d['args'], img, n, roots_old, one_based=False)
    return dict(input_count=len(keep), args=args, roots=roots, source='cp10 zero restriction to points %s' % keep)


def additions(d):
    return sum(1 for a in d['args'] if a is not None and list(a) != [0, 0])


CUT = dict(tmod=cut_triple, pmod=cut_pair, qmod=cut_q)


def min_cut(kind, d, n, k=1):
    """the zero restriction to n - k points with the fewest additions (ties: lexicographically first drop)"""
    cands = []
    for drop in combinations(range(n), k):
        keep = [x for x in range(n) if x not in drop]
        e = CUT[kind](d, n, keep)
        cands.append((additions(e), drop, e))
    cands.sort(key=lambda c: (c[0], c[1]))
    return cands[0]


def encode(d):
    return (json.dumps(d, separators=(',', ':')) + '\n').encode()


if __name__ == '__main__':
    kind, n, k, src, dst = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5])
    adds, drop, e = min_cut(kind, json.loads(src.read_text()), n, k)
    dst.write_bytes(encode(e))
    print('%s: %d -> %d points, dropped %s, %d additions' % (kind, n, n - k, list(drop), adds))
