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
