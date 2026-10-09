#!/usr/bin/env python3
"""Derive the pinned pair-disjoint modules (data/pair_module_p{11,12,13}.json).

A pair-disjoint module on n points has inputs x_{ab} (pairs of [n]) and, for every pair {i,j}, the output
sum of x_{ab} over pairs disjoint from {i,j}.  For fixed c, the bit outputs out(c,T) = sum_{S cap T = {c}} x_S
of a bit producer ARE such a query on the points other than c, so an exact zero restriction of a bit witness
to the triples {c,a,b} with a,b in a chosen n-set Z gives a module (support hash-consing, unary additions
contracted, inactive nodes pruned), exactly as PR #144's modules.restricted_pairs does for the PR117 DAG.

p=11, p=12: cut from the h=21 Fibonacci-strip bit witness (p=12: pair_module_p12_cut.json, the seed of the
           annealed pair_module_p12.json) (sha256 pinned below), c=14,
           Z = 10 resp. 11 consecutive points (the minimum-addition cut, first in (c, cyclic start) order).
p=13:       PR #144 modules.restricted_pairs(12) (PR117 DAG, pinned in the repository).
Usage: python3 derive_pair_modules.py --witness PATH/witness_21.json.gz --tree REPO_ROOT [--check]
"""
import argparse, gzip, hashlib, json, sys
from itertools import combinations
from pathlib import Path
HERE = Path(__file__).resolve().parent
WITNESS_SHA256 = None  # filled by first run, then pinned in data/pair_module_provenance.json


def cut(w, c, Z):
    Z = list(Z); n = len(Z); pos = {z: i for i, z in enumerate(Z)}
    pairs = list(combinations(range(n), 2)); pid = {pp: i for i, pp in enumerate(pairs)}
    args_w = {int(k): v for k, v in w['args'].items()}
    leaf = {int(k): v for k, v in w['leaf'].items()}
    args = [None] * len(pairs); support = [1 << i for i in range(len(pairs))]; by = {s: i for i, s in enumerate(support)}
    image = {}
    for x in sorted(args_w):
        a = args_w[x]
        if a is None:
            T = leaf[x]
            o = [t for t in T if t != c]
            image[x] = pid[tuple(sorted(pos[t] for t in o))] if c in T and all(t in pos for t in o) else None
            continue
        ia, ib = image.get(a[0]), image.get(a[1])
        if ia is None or ib is None:
            image[x] = ia if ib is None else ib
            continue
        assert not support[ia] & support[ib]
        s = support[ia] | support[ib]
        if s not in by:
            by[s] = len(args); args.append([ia, ib]); support.append(s)
        image[x] = by[s]
    outs = {}
    for cc, T, node in w['outputs']:
        o = [t for t in T if t != c]
        if cc == c and all(t in pos for t in o):
            outs[tuple(sorted(pos[t] for t in o))] = image[node]
    roots = []
    for (i, j) in pairs:
        r = outs[(i, j)]
        expected = sum(1 << k for k, (a, b) in enumerate(pairs) if i not in (a, b) and j not in (a, b))
        assert r is not None and support[r] == expected
        roots.append(r)
    active, stack = set(range(len(pairs))), list(roots)
    while stack:
        x = stack.pop()
        if x not in active:
            active.add(x)
            if args[x] is not None:
                stack.extend(args[x])
    ids = sorted(active); ren = {x: i for i, x in enumerate(ids)}
    return dict(kind='pair_disjoint', n=n, input_count=len(pairs), input_labels=[list(p_) for p_ in pairs],
                args=[None if args[x] is None else [ren[y] for y in args[x]] for x in ids], roots=[ren[x] for x in roots])


def best_cut(w, n):
    best = None
    for c in range(w['h']):
        others = [t for t in range(w['h']) if t != c]
        for start in range(len(others)):
            Z = sorted(others[(start + k) % len(others)] for k in range(n))
            m = cut(w, c, Z)
            adds = len(m['args']) - m['input_count']
            if best is None or adds < best[0]:
                best = (adds, c, Z, m)
    return best


def dumps(o):
    return json.dumps(o, sort_keys=True, separators=(',', ':')) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--witness', type=Path, required=True)
    ap.add_argument('--tree', type=Path, required=True)
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    raw = a.witness.read_bytes()
    wsha = hashlib.sha256(raw).hexdigest()
    w = json.loads(gzip.decompress(raw))
    sys.path.insert(0, str(a.tree / 'scripts'))
    from paired_cube.modules import restricted_pairs
    dag = a.tree / 'references/three-stage-cover/pr117/dag.json.gz'
    files = {}
    prov = dict(witness_sha256=wsha, witness='h=21 Fibonacci-strip bit witness (data/source_witness_21.json.gz)',
                pr117_dag_sha256=hashlib.sha256(dag.read_bytes()).hexdigest())
    for p in (11, 12):
        adds, c, Z, m = best_cut(w, p - 1)
        m['provenance'] = dict(source='bit witness cut', witness_sha256=wsha, c=c, Z=Z, additions=adds)
        files['pair_module_p%d.json' % p if p == 11 else 'pair_module_p12_cut.json'] = dumps(m)
    m = restricted_pairs(12)
    m = dict(kind='pair_disjoint', n=12, input_count=m['input_count'], input_labels=[list(x) for x in m['input_labels']],
             args=m['args'], roots=m['roots'],
             provenance=dict(source='PR144 modules.restricted_pairs(12) of the PR117 DAG', pr117_dag_sha256=prov['pr117_dag_sha256'],
                             additions=len(m['args']) - m['input_count']))
    files['pair_module_p13.json'] = dumps(m)
    files['pair_module_provenance.json'] = dumps(prov)
    for name, text in files.items():
        path = HERE / 'data' / name
        if a.check:
            assert path.read_text() == text, name
        else:
            path.write_text(text)
    print(('PASS' if a.check else 'wrote'), {k: len(v) for k, v in files.items()})


if __name__ == '__main__':
    main()
