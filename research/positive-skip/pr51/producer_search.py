#!/usr/bin/env python3
"""Exact changed pair DAGs and moment-sensitive carrier search.

Graph/frame primitives: pinned icekylinx PR36, Apache-2.0, with the credited
jacklightChen/earlier contributors. New search and objective: RaD GPU track.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time

SOURCE = None
WORK = None
MATCHER = None


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def initialize(source, work, matcher):
    global SOURCE, WORK, MATCHER
    SOURCE, WORK, MATCHER = map(Path, (source, work, matcher))
    sys.path.insert(0, str(SOURCE / 'scripts'))


def build(h, threshold, grouping, tree, seed):
    from partial_swap.paired import PairedExclusionCircuit
    from partial_swap.shared import SharedPointCircuit
    from partial_swap.graph import aligned_points

    class Changed(PairedExclusionCircuit):
        base_threshold = threshold

        def block(self, points, edges, weights):
            if grouping == 'pairs' or len(points) <= self.base_threshold:
                return super().block(points, edges, weights)
            groups = self.grouping(points)
            ng = len(groups)
            edge = lambda a,b: edges[tuple(sorted((a,b)))]
            coarse = {(i,j): self.total([edge(a,b) for a in groups[i] for b in groups[j]])
                      for i,j in combinations(range(ng),2)}
            wt = {i:self.total([weights[a] for a in g]+[edge(a,b) for a,b in combinations(g,2)])
                  for i,g in enumerate(groups)}
            total, outside, far = self.block(list(range(ng)),coarse,wt)
            strips, sums = {}, {}
            for i,g in enumerate(groups):
                other = [j for j in range(ng) if j != i]
                for a in g:
                    retained = [u for u in g if u != a]
                    carry = self.total([weights[u] for u in retained]+
                                       [edge(u,v) for u,v in combinations(retained,2)])
                    vals = [self.total([edge(u,v) for u in retained for v in groups[j]]) for j in other]
                    subtotal, one, _ = self.vector([carry]+vals,False)
                    strips[a] = {j:z for j,z in zip(other,one[1:])}
                    sums[a] = subtotal
            single = {a:self.add(outside[i],sums[a]) for i,g in enumerate(groups) for a in g}
            out = {}
            for i,g in enumerate(groups):
                for a,b in combinations(g,2):
                    retained = [u for u in g if u not in (a,b)]
                    local = [weights[u] for u in retained]
                    local += [edge(u,v) for u,v in combinations(retained,2)]
                    local += [edge(u,v) for u in retained for j,gg in enumerate(groups) if j != i for v in gg]
                    out[a,b] = self.add(outside[i],self.total(local))
            for i,j in combinations(range(ng),2):
                for a in groups[i]:
                    left = self.add(far[i,j],strips[a][j])
                    for b in groups[j]:
                        cross = self.total([edge(u,v) for u in groups[i] if u != a for v in groups[j] if v != b])
                        out[a,b] = self.add(left,self.add(strips[b][i],cross))
            return total,single,out

        def grouping(self, points):
            if grouping == 'pairs':
                return super().grouping(points)
            if grouping == 'triple-head' and len(points) > threshold:
                return [points[:3]] + [points[i:i+2] for i in range(3, len(points), 2)]
            if grouping == 'triples':
                return [points[i:i+3] for i in range(0, len(points), 3)]
            if grouping == 'single-head':
                return [points[:1]] + [points[i:i+2] for i in range(1, len(points), 2)]
            raise ValueError(grouping)

        def total(self, values):
            values = [x for x in values if x]
            if tree == 'balanced':
                return super().total(values)
            if tree == 'left':
                result = 0
                for node in values:
                    result = self.add(result, node)
                return result
            if tree in ('right','support-left','support-right','seeded-left'):
                if tree == 'right':
                    values.reverse()
                elif tree.startswith('support'):
                    values.sort(key=lambda node: (self.support[node].bit_count(), self.support[node]),
                                reverse=tree.endswith('right'))
                else:
                    values.sort(key=lambda node: sha256(repr((seed,self.support[node])).encode()).digest())
                result = 0
                for node in values:
                    result = self.add(result,node)
                return result
            if tree == 'skew':
                if len(values) <= 1:
                    return values[0] if values else 0
                cut = max(1,len(values)//3)
                return self.add(self.total(values[:cut]),self.total(values[cut:]))
            if tree == 'reuse-cover':
                target = 0
                for node in values:
                    assert not target & self.support[node]
                    target |= self.support[node]
                if not target:
                    return 0
                if target in self.lookup:
                    return self.lookup[target]
                remainder = target
                pieces = []
                available = sorted(((s,node) for s,node in self.lookup.items() if s and not s & ~target),
                                   key=lambda item: (-item[0].bit_count(),item[0]))
                for support,node in available:
                    if not support & ~remainder:
                        pieces.append(node)
                        remainder ^= support
                        if not remainder:
                            break
                assert not remainder
                result = 0
                for node in pieces:
                    result = self.add(result,node)
                return result
            if tree == 'support':
                values = sorted(values, key=lambda node: (self.support[node].bit_count(), node))
                while len(values) > 1:
                    first, second, *tail = values
                    values = [self.add(first, second), *tail]
                    values.sort(key=lambda node: (self.support[node].bit_count(), node))
                return values[0] if values else 0
            raise ValueError(tree)

    local = Changed(h-1)
    total = local.pair(list(range(h-1)))[0]
    local.outputs[()] = total
    stack = [total]
    while stack:
        node = stack.pop()
        if not node or node in local.active:
            continue
        local.active.add(node)
        if local.args[node]:
            stack.extend(local.args[node])
    local.additions = sum(local.args[node] is not None for node in local.active)
    return SharedPointCircuit(h, local, point_order=aligned_points)


def ordinary_profile(h, r):
    if 2*r > h:
        return Counter({2*r-h: 1, 1: h-r}) if 2*r-h != 1 else Counter({1: r})
    return Counter({1: r})


def profile(rows, reversed_corner=True):
    a, b = (row['h'] for row in rows)
    assert (a, b) in ((23, 25), (25, 23))
    m = a*b
    N = rows[0]['v']*rows[1]['v']
    Bs = [N//row['v']*row['R'] for row in rows]
    W = 2*N+sum(Bs)
    L = sum(N//row['v']*row['loss'] for row in rows)
    z = Counter()
    for h, B in zip((a, b), Bs):
        z[h] += B
        z[m-2*h] += B
    cp = [9, 21, 17, 481] if reversed_corner else [11, 21, 15, 481]
    z[1] += cp[0]*2*N
    for t in cp[1:]:
        z[t] += 2*N
    for row in rows:
        h, count = row['h'], N//row['v']
        hist = list(row['histogram'])
        assert hist[h] >= h and row['loss'] == h*(h-1)
        hist[1] += h
        hist[h] -= h
        for r, n in enumerate(hist):
            for t, k in ordinary_profile(h, r).items():
                z[t] += count*n*k
        for t, k in ordinary_profile(h, h-1).items():
            z[t] += 2*N*k
    z[1] += N
    z = {t: n for t, n in sorted(z.items()) if t and n}
    assert sum(t*n for t, n in z.items()) == W*m-N+L
    alpha = 0.00003850919324
    moment = sum(n*t*math.exp(alpha*math.log(m/t)) for t, n in z.items())/(W*m)
    low, high = 0.0, 0.001
    for _ in range(60):
        midpoint = (low+high)/2
        value = sum(n*t*math.exp(midpoint*math.log(m/t)) for t, n in z.items())/(W*m)
        if value < 1:
            low = midpoint
        else:
            high = midpoint
    return dict(dimensions=[a,b], m=m, N=N, W=W, L=L, deficit=N-L,
                total_rank=W*m-N+L, child_multiplicities=z,
                discovery_moment=moment, discovery_saving_interval=[low,high],
                alpha_evaluated=alpha, exact_certificate=False)


def worker(config):
    from partial_swap.graph import export
    from partial_swap.positive import run as positive_labels
    start = time.monotonic()
    case_id = '-'.join(str(config[key]) for key in ('h','threshold','grouping','tree','mode','seed'))
    target = WORK/'raw'/case_id
    target.mkdir(parents=True, exist_ok=False)
    row = dict(configuration=config, case_id=case_id, pid=os.getpid(), started_utc=datetime.now(timezone.utc).isoformat())
    try:
        circuit = build(config['h'], config['threshold'], config['grouping'], config['tree'], config['seed'])
        row['scalar'] = circuit.verify()
        dag = target/'dag.bin'
        export(circuit, dag)
        dep = subprocess.run([str(WORK/'builds'/'match_exported_dag'), str(dag), str(dag)+'.links'],
                             text=True, capture_output=True, check=True)
        row['envelope_carriers'] = json.loads(dep.stdout)
        labels = positive_labels(str(dag))
        row['labels'] = labels
        witness = target/'selected-links.json'
        matched = subprocess.run([str(MATCHER), str(dag), str(dag)+'.positive', str(config['seed']),
                                  str(config['mode']), str(witness)], text=True, capture_output=True, check=True)
        row.update(json.loads(matched.stdout))
        wit = json.loads(witness.read_text())
        row.update(status='producer and native rank audit passed',
                   witness_path=str(witness), witness_sha256=digest(witness),
                   dag_path=str(dag), dag_sha256=digest(dag), positive_sha256=digest(str(dag)+'.positive'),
                   exchanges=wit['exchanges'], logical_graph_sha256=row['scalar']['circuit_sha256'])
        if row['h'] in (23,25):
            axes = json.loads((SOURCE/'certificates'/'copied-centers-bit-axes.json').read_text())
            other = next(dict(x) for x in axes if x['h'] != row['h'])
            pair = [row, other] if row['h'] == 23 else [other, row]
            row['two_stage_reversed_profile'] = profile(pair)
        (target/'native-stderr.txt').write_text(dep.stderr+matched.stderr)
        row['seconds'] = time.monotonic()-start
        (target/'result.json').write_text(json.dumps(row, indent=2, sort_keys=True)+'\n')
        circuit.support_in.cache_clear()
        return row
    except Exception as error:
        row.update(status='failed', error=repr(error), seconds=time.monotonic()-start)
        (target/'result.json').write_text(json.dumps(row, indent=2, sort_keys=True)+'\n')
        return row


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--workers', type=int, default=8)
    p.add_argument('--small', action='store_true')
    p.add_argument('--set', choices=['initial','expanded','dimensions','associations'], default='initial')
    a = p.parse_args()
    assert not a.output.exists() and 1 <= a.workers <= 8
    a.work.mkdir(parents=True, exist_ok=True)
    (a.work/'builds').mkdir(exist_ok=True)
    native = Path(__file__).with_name('moment_match_positive.cpp')
    matcher = a.work/'builds'/'moment_match_positive'
    subprocess.run(['c++','-O3','-std=c++17',str(native),'-o',str(matcher)],check=True)
    subprocess.run(['c++','-O3','-std=c++17',str(a.source/'scripts'/'partial_swap'/'match_exported_dag.cpp'),
                    '-o',str(a.work/'builds'/'match_exported_dag')],check=True)
    initialize(a.source, a.work, matcher)
    configurations = []
    if a.small:
        for threshold, grouping, tree in ((2,'pairs','balanced'),(3,'triple-head','balanced'),(2,'pairs','left'),(2,'pairs','support')):
            configurations.append(dict(h=8,threshold=threshold,grouping=grouping,tree=tree,mode=1,seed=104729))
    elif a.set == 'initial':
        for h in (23,25):
            for threshold, grouping, tree, mode in ((2,'pairs','balanced',1),(3,'pairs','balanced',2),
                                                   (4,'pairs','support',4),(2,'triple-head','balanced',1)):
                configurations.append(dict(h=h,threshold=threshold,grouping=grouping,tree=tree,mode=mode,seed=104729))
    elif a.set == 'expanded':
        for h in (23,25):
            for threshold, grouping, tree, mode in ((2,'pairs','balanced',2),(2,'pairs','balanced',4),
                (2,'pairs','left',1),(2,'pairs','support',1),(3,'triple-head','support',2),
                (3,'triples','balanced',1),(4,'single-head','balanced',2),(5,'pairs','balanced',1)):
                configurations.append(dict(h=h,threshold=threshold,grouping=grouping,tree=tree,mode=mode,seed=130363))
    elif a.set == 'dimensions':
        for h in range(17,36):
            for threshold, grouping, tree, mode in ((2,'pairs','left',1),(2,'pairs','support',2),
                (4,'pairs','support',1),(3,'triple-head','balanced',2),
                (3,'triples','support',1),(3,'single-head','balanced',2)):
                configurations.append(dict(h=h,threshold=threshold,grouping=grouping,tree=tree,mode=mode,seed=155921))
    else:
        for h in (17,19,21,23,25,27,29,31,33,35):
            for tree in ('right','support-left','support-right','skew','reuse-cover','seeded-left'):
                configurations.append(dict(h=h,threshold=2,grouping='pairs',tree=tree,mode=2,seed=196613))
        for h in (23,25):
            for seed in (104729,130363,155921):
                configurations.append(dict(h=h,threshold=2,grouping='pairs',tree='seeded-left',mode=4,seed=seed))
    result = dict(status='running', source_revision='11817ccacb564bb7f98789c20dc11d3fece207e3',
                  source_repository='https://github.com/icekylinx/integer-mult-bounds',
                  started_utc=datetime.now(timezone.utc).isoformat(), configurations=configurations,
                  workers=a.workers, command=sys.argv, authored_source_sha256={p.name:digest(p) for p in (Path(__file__),native)},rows=[])
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with ProcessPoolExecutor(max_workers=a.workers,initializer=initialize,initargs=(a.source,a.work,matcher)) as pool:
        futures = {pool.submit(worker,c):c for c in configurations}
        for future in as_completed(futures):
            row = future.result()
            result['rows'].append(row)
            a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
            print(json.dumps({key:row.get(key) for key in ('case_id','status','R','matched','exchanges','seconds','pid')}),flush=True)
    result.update(status='complete', completed_utc=datetime.now(timezone.utc).isoformat())
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
