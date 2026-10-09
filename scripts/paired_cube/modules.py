#!/usr/bin/env python3
# Copyright 2026 icekylinx. Apache-2.0.
# Developed with GPT-6 Astra assistance; integrated with Codex assistance.
"""Exact positive scalar DAG modules for the paired-cube construction.

The pair-disjoint module is a specialization of the already adopted PR117
positive DAG (eumemic, Apache-2.0, pinned cbb05ce504d571546d9b7794c186a613c659c3bf).
The balanced all-but-one module is an explicit binary-tree construction.
All module nodes are zero-based; the first input_count nodes are inputs,
and args[node] is null on inputs or [left,right] on addition nodes.
"""
from pathlib import Path
from itertools import combinations
import gzip,json,argparse
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent

def restricted_pairs(n):
 assert 2<=n<=22
 w=json.loads(gzip.decompress((ROOT/'references/three-stage-cover/pr117/dag.json.gz').read_bytes()))
 oldtriples=list(combinations(range(24),3));pairs=list(combinations(range(n),2));pid={p:i for i,p in enumerate(pairs)}
 args=[None]*len(pairs);support=[1<<i for i in range(len(pairs))];by={s:i for i,s in enumerate(support)};image=[None]
 for t in oldtriples:
  p=tuple(x for x in t if x!=23)
  image.append(pid[p] if 23 in t and len(p)==2 and p[-1]<n else None)
 for aa,bb in zip(w['args'][::2],w['args'][1::2]):
  a,b=image[aa],image[bb]
  if a is None or b is None:image.append(a if b is None else b);continue
  assert not support[a]&support[b]
  s=support[a]|support[b]
  if s not in by:by[s]=len(args);args.append([a,b]);support.append(s)
  image.append(by[s])
 oldroots={t:x for t,x in zip(oldtriples,w['D'])}
 roots=[image[oldroots[(i,j,22)]] for i,j in pairs]
 for (i,j),r in zip(pairs,roots):
  expected=sum(1<<k for k,(a,b) in enumerate(pairs) if i not in (a,b) and j not in (a,b))
  assert r is not None and support[r]==expected
 active=set(range(len(pairs)));stack=list(roots)
 while stack:
  x=stack.pop()
  if x in active:continue
  active.add(x)
  if args[x] is not None:stack.extend(args[x])
 ids=sorted(active);ren={x:i for i,x in enumerate(ids)}
 args=[None if args[x] is None else [ren[y] for y in args[x]] for x in ids];roots=[ren[x] for x in roots]
 return dict(kind='pair_disjoint',n=n,input_count=len(pairs),input_labels=pairs,output_labels=pairs,args=args,roots=roots,
  source='PR117 h24 witness specialization: input triple {a,b,23}; output D_{i,j,22}; exact support hash-consing and pruning',
  source_commit='cbb05ce504d571546d9b7794c186a613c659c3bf')

def all_but_one(n):
 assert n>=3
 args=[None]*n;support=[1<<i for i in range(n)];by={s:i for i,s in enumerate(support)}
 def add(a,b):
  if a is None:return b
  if b is None:return a
  assert not support[a]&support[b]
  s=support[a]|support[b]
  if s not in by:by[s]=len(args);args.append([a,b]);support.append(s)
  return by[s]
 def tree(lo,hi):
  if hi-lo==1:return (lo,None,None)
  mid=(lo+hi)//2;L=tree(lo,mid);R=tree(mid,hi)
  return (add(L[0],R[0]),L,R)
 T=tree(0,n);roots=[None]*n
 def walk(t,outside):
  x,L,R=t
  if L is None:roots[x]=outside;return
  walk(L,add(outside,R[0]));walk(R,add(outside,L[0]))
 walk(T,None)
 full=(1<<n)-1
 assert all(support[r]==full^(1<<i) for i,r in enumerate(roots))
 active=set(range(n));stack=list(roots)
 while stack:
  x=stack.pop()
  if x in active:continue
  active.add(x)
  if args[x] is not None:stack.extend(args[x])
 ids=sorted(active);ren={x:i for i,x in enumerate(ids)}
 args=[None if args[x] is None else [ren[y] for y in args[x]] for x in ids];roots=[ren[x] for x in roots]
 return dict(kind='all_but_one',n=n,input_count=n,input_labels=list(range(n)),output_labels=list(range(n)),args=args,roots=roots,
  source='Explicit balanced binary-tree upward sums and complementary downward sums; all additions have disjoint supports')


def restricted_triples(p):
    w = json.loads(gzip.decompress(
        (ROOT / 'references/three-stage-cover/pr117/dag.json.gz').read_bytes()))
    labels = list(combinations(range(p), 3))
    index = {t: i+1 for i, t in enumerate(labels)}
    args = [(0, 0)] + [(0, 0)] * len(labels)
    supports = [0] + [1 << i for i in range(len(labels))]
    intern = {s: i for i, s in enumerate(supports) if s}
    old_labels = list(combinations(range(w['h']), 3))
    image = [0] + [index.get(t, 0) for t in old_labels]
    for aa, bb in zip(w['args'][::2], w['args'][1::2]):
        a, b = image[aa], image[bb]
        if not a or not b:
            image.append(a or b)
            continue
        s = supports[a] | supports[b]
        if s not in intern:
            intern[s] = len(args)
            args.append((a, b))
            supports.append(s)
        image.append(intern[s])
    roots = [image[x] for t, x in zip(old_labels, w['D']) if t[-1] < p]
    active = set(range(len(labels)+1))
    stack = roots[:]
    while stack:
        x = stack.pop()
        if x in active:
            continue
        active.add(x)
        stack.extend(args[x])
    order = sorted(active)
    rename = {x: i for i, x in enumerate(order)}
    result = dict(
        kind='disjoint_triples', p=p, input_labels=labels,
        target_labels=labels, input_count=len(labels),
        args=[[rename[a], rename[b]] for x in order for a, b in [args[x]]],
        roots=[rename[x] for x in roots],
        source='Already adopted PR117 positive DAG, exact zero restriction and D-only pruning',
        source_commit='cbb05ce504d571546d9b7794c186a613c659c3bf',
        source_author='eumemic',
        contract='Root indexed by J sums input I exactly when I and J are disjoint.')
    return result


# ---- Generalized restrictions for other p / other #117-format sources (eumemic, Claude assistance; Apache-2.0).
# Same contracts and checks as restricted_triples/restricted_pairs above; the defaults of those functions are
# keep = 0..p-1 (triples) and keep = 0..n-1, pin = 23, out = 22 (pairs) on the PR117 h24 witness.
def _source_witness(path):
    return json.loads(gzip.decompress(Path(path).read_bytes()))

def restricted_triples_from(path, keep):
    w = _source_witness(path)
    keep = sorted(keep); p = len(keep); rename = {x: j for j, x in enumerate(keep)}
    labels = list(combinations(range(p), 3)); index = {t: i+1 for i, t in enumerate(labels)}
    args = [(0, 0)] + [(0, 0)] * len(labels); supports = [0] + [1 << i for i in range(len(labels))]
    intern = {s: i for i, s in enumerate(supports) if s}
    old_labels = list(combinations(range(w['h']), 3))
    def new(t): return tuple(rename[x] for x in t) if all(x in rename for x in t) else None
    image = [0] + [index.get(new(t), 0) for t in old_labels]
    for aa, bb in zip(w['args'][::2], w['args'][1::2]):
        a, b = image[aa], image[bb]
        if not a or not b:
            image.append(a or b); continue
        assert not supports[a] & supports[b]
        s = supports[a] | supports[b]
        if s not in intern:
            intern[s] = len(args); args.append((a, b)); supports.append(s)
        image.append(intern[s])
    roots = [image[x] for t, x in zip(old_labels, w['D']) if new(t) is not None]
    for J, r in zip(labels, roots):
        assert r and supports[r] == sum(1 << i for i, I in enumerate(labels) if not set(I) & set(J))
    active = set(range(len(labels)+1)); stack = roots[:]
    while stack:
        x = stack.pop()
        if x in active: continue
        active.add(x); stack.extend(args[x])
    order = sorted(active); rename2 = {x: i for i, x in enumerate(order)}
    return dict(kind='disjoint_triples', p=p, input_labels=labels, target_labels=labels, input_count=len(labels),
        args=[[rename2[a], rename2[b]] for x in order for a, b in [args[x]]], roots=[rename2[x] for x in roots],
        source='exact zero restriction of a pinned #117-format witness to kept points', kept=keep,
        contract='Root indexed by J sums input I exactly when I and J are disjoint.')

def restricted_pairs_from(path, keep, pin, out):
    w = _source_witness(path)
    keep = sorted(keep); n = len(keep)
    assert pin not in keep and out not in keep and pin != out
    rename = {x: j for j, x in enumerate(keep)}
    oldtriples = list(combinations(range(w['h']), 3)); pairs = list(combinations(range(n), 2))
    pid = {q: i for i, q in enumerate(pairs)}
    args = [None]*len(pairs); support = [1 << i for i in range(len(pairs))]; by = {s: i for i, s in enumerate(support)}
    image = [None]
    for t in oldtriples:
        rest = tuple(x for x in t if x != pin)
        ok = pin in t and len(rest) == 2 and all(x in rename for x in rest)
        image.append(pid[tuple(sorted(rename[x] for x in rest))] if ok else None)
    for aa, bb in zip(w['args'][::2], w['args'][1::2]):
        a, b = image[aa], image[bb]
        if a is None or b is None:
            image.append(a if b is None else b); continue
        assert not support[a] & support[b]
        s = support[a] | support[b]
        if s not in by:
            by[s] = len(args); args.append([a, b]); support.append(s)
        image.append(by[s])
    oldroots = {t: x for t, x in zip(oldtriples, w['D'])}
    roots = [image[oldroots[tuple(sorted((keep[i], keep[j], out)))]] for i, j in pairs]
    for (i, j), r in zip(pairs, roots):
        expected = sum(1 << k for k, (a, b) in enumerate(pairs) if i not in (a, b) and j not in (a, b))
        assert r is not None and support[r] == expected
    active = set(range(len(pairs))); stack = list(roots)
    while stack:
        x = stack.pop()
        if x in active: continue
        active.add(x)
        if args[x] is not None: stack.extend(args[x])
    ids = sorted(active); ren = {x: i for i, x in enumerate(ids)}
    args = [None if args[x] is None else [ren[y] for y in args[x]] for x in ids]
    return dict(kind='pair_disjoint', n=n, input_count=len(pairs), input_labels=pairs, output_labels=pairs,
        args=args, roots=[ren[x] for x in roots], kept=keep, pin=pin, out=out,
        source='zero restriction of a pinned #117-format witness: inputs {a,b,pin}, outputs D_{i,j,out}')


# ---- Direct pair-module source (PMOD lane; eumemic, Claude assistance; Apache-2.0).
def pair_module_from(path, n):
    """Zero-based pair-disjoint module given as JSON {input_count, args, roots}; same contract as restricted_pairs(n):
    additions combine disjoint supports and root (i,j) sums exactly the inputs {a,b} disjoint from {i,j}."""
    d = json.loads(Path(path).read_text())
    pairs = list(combinations(range(n), 2))
    assert d['input_count'] == len(pairs) == len(d['roots'])
    support = []
    for x, a in enumerate(d['args']):
        if x < len(pairs):
            assert a is None
            support.append(1 << x)
        else:
            assert a is not None and 0 <= a[0] < x and 0 <= a[1] < x and not support[a[0]] & support[a[1]]
            support.append(support[a[0]] | support[a[1]])
    for (i, j), r in zip(pairs, d['roots']):
        assert support[r] == sum(1 << k for k, (a, b) in enumerate(pairs) if i not in (a, b) and j not in (a, b))
    return dict(kind='pair_disjoint', n=n, input_count=len(pairs), input_labels=pairs, output_labels=pairs,
                args=[None if a is None else list(a) for a in d['args']], roots=list(d['roots']),
                source='Direct pair module JSON; contract checked above')


# ---- Direct triple-module source (TMOD lane; eumemic, Claude assistance; Apache-2.0).
def triple_module_from(path, p):
    """One-based disjoint-triples module given as JSON (the layout of restricted_triples(p)); same contract:
    additions combine disjoint supports and the root indexed by J sums input I exactly when I and J are disjoint."""
    d = json.loads(Path(path).read_text())
    labels = list(combinations(range(p), 3))
    assert d['input_count'] == len(labels) == len(d['roots'])
    assert [tuple(x) for x in d['input_labels']] == labels == [tuple(x) for x in d['target_labels']]
    args = d['args']
    assert all(list(a) == [0, 0] for a in args[:len(labels) + 1])
    support = [0] + [1 << i for i in range(len(labels))]
    for x in range(len(labels) + 1, len(args)):
        a, b = args[x]
        assert 0 < a < x and 0 < b < x and not support[a] & support[b]
        support.append(support[a] | support[b])
    for J, r in zip(labels, d['roots']):
        assert support[r] == sum(1 << i for i, I in enumerate(labels) if not set(I) & set(J))
    return dict(kind='disjoint_triples', p=p, input_labels=labels, target_labels=labels, input_count=len(labels),
                args=[list(a) for a in args], roots=list(d['roots']),
                source='Direct triple module JSON; contract checked above',
                contract='Root indexed by J sums input I exactly when I and J are disjoint.')


# ---- Direct all-but-one source (QMOD lane; eumemic, Claude assistance; Apache-2.0).
def all_but_one_from(path, n):
    """Zero-based all-but-one module given as JSON {input_count, args, roots}; same contract as all_but_one(n):
    additions combine disjoint supports and root i sums exactly the inputs other than i."""
    d = json.loads(Path(path).read_text())
    assert d['input_count'] == n == len(d['roots'])
    support = []
    for x, a in enumerate(d['args']):
        if x < n:
            assert a is None
            support.append(1 << x)
        else:
            assert a is not None and 0 <= a[0] < x and 0 <= a[1] < x and not support[a[0]] & support[a[1]]
            support.append(support[a[0]] | support[a[1]])
    full = (1 << n) - 1
    assert all(support[r] == full ^ (1 << i) for i, r in enumerate(d['roots']))
    return dict(kind='all_but_one', n=n, input_count=n, input_labels=list(range(n)), output_labels=list(range(n)),
                args=[None if a is None else list(a) for a in d['args']], roots=list(d['roots']),
                source='Direct all-but-one module JSON; contract checked above')


# ---- Output merging (pmerge.py variants; eumemic, Claude assistance; Apache-2.0).
def merge_outputs(g, G, variant):
    """Replace #144's single-target channels of each port T=(I,b) -- face2 P[I,I2,1-b2] (1/2), edge02
    Q[I,I0,I2,b0^b2] ((2b0-1)/2), edge12 Q[I,I1,I2,b1^b2] ((2b1-1)/2) -- by signed sums read with coefficient 1/2.
    w02: face2 + (2b0-1)*edge02, one node per (b0,b2) shared by the ports b1=0,1; edge12 stays single.  The decoder
    contribution is unchanged and Graph.add asserts disjoint supports."""
    from fractions import Fraction
    side = [r for r in g['roots'] if r['kind'] == 'side']
    centre = [r for r in g['roots'] if r['kind'] != 'side']
    if variant.startswith('f8:'):
        # per-class fold orders: port t folds its face2, edge02, edge12 singles in order PERMS[code[t % 8]]
        perms = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
        code = variant[3:]
        assert len(code) == 8 and all(ch in '012345' for ch in code)
        names = ('face2', 'edge02', 'edge12')
        single = {}
        keep = []
        for r in side:
            if r['channel'] in names:
                assert len(r['targets']) == 1
                single[r['targets'][0], r['channel']] = (r['node'], Fraction(r['coefficients'][0]))
            else:
                keep.append(r)
        new = []
        for t in range(g['v']):
            parts = [single[t, ch] for ch in names]
            order = perms[int(code[t % 8])]
            node, c0 = parts[order[0]]
            for k in order[1:]:
                nd, c = parts[k]
                sg = c / c0
                assert sg in (1, -1)
                node = G.add(node, nd, int(sg))
            new.append(dict(node=node, targets=[t], coefficients=[str(c0)], kind='side', channel='fused'))
        return dict(g, roots=keep + new + centre, args=G.a, signs=G.signs)
    if variant == 'pf':
        # PR #163's fold rule: each port's three single-target channels face2, edge02, edge12 become one signed
        # sum, folded left with the positive-coefficient channels first (in that channel order), then the negatives.
        names = ('face2', 'edge02', 'edge12')
        single = {}
        keep = []
        for r in side:
            if r['channel'] in names:
                assert len(r['targets']) == 1
                single[r['targets'][0], r['channel']] = (r['node'], Fraction(r['coefficients'][0]))
            else:
                keep.append(r)
        new = []
        for t in range(g['v']):
            parts = [single[t, ch] for ch in names]
            order = [k for k in range(3) if parts[k][1] > 0] + [k for k in range(3) if parts[k][1] < 0]
            node, c0 = parts[order[0]]
            for k in order[1:]:
                nd, c = parts[k]
                sg = c / c0
                assert sg in (1, -1)
                node = G.add(node, nd, int(sg))
            new.append(dict(node=node, targets=[t], coefficients=[str(c0)], kind='side', channel='fused'))
        return dict(g, roots=keep + new + centre, args=G.a, signs=G.signs)
    specs = {'w02': [('face2', 'edge02')], 'w12': [('face2', 'edge12')],
             's': [('face2', 'edge02', 'edge12')]}[variant]
    chan = {c: k for k, spec in enumerate(specs) for c in spec}
    found = {}
    keep = []
    for r in side:
        if r['channel'] in chan:
            assert all(Fraction(c) == Fraction(r['coefficients'][0]) for c in r['coefficients'])
            found[chan[r['channel']], tuple(r['targets']), r['channel']] = (r['node'], Fraction(r['coefficients'][0]))
        else:
            keep.append(r)
    new = []
    for k, tg in sorted({(k, tg) for k, tg, _ in found}):
        parts = [found[k, tg, ch] for ch in specs[k]]
        node, c0 = parts[0]
        for nd, c in parts[1:]:
            sg = c / c0
            assert sg in (1, -1)
            node = G.add(node, nd, int(sg))
        new.append(dict(node=node, targets=list(tg), coefficients=[str(c0)] * len(tg), kind='side', channel=variant))
    new.sort(key=lambda r: -len(r['targets']))   # multi-target roots before singles (target chains ascend)
    return dict(g, roots=keep + new + centre, args=G.a, signs=G.signs)
