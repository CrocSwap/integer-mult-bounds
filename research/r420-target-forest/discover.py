#!/usr/bin/env python3
"""Reproduce the bounded seed-5 nomination and eight precision-driven cuts.
This search chooses a witness. verify.py certifies optimality independently.
Oscar Fennell, with substantial OpenAI Codex assistance; Apache-2.0.
"""
import importlib.util
import json
from pathlib import Path
import random
from fractions import Fraction

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('forest_verify', HERE/'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
w = v.load_source()
K = v.rows(w)
# Reverse positive envelopes before D; no frame calculations or F2 cancellation.
stream = []
for section in ('A', 'scatter', 'B', 'C'):
    if section == 'scatter':
        for k, q in enumerate(w['ret']):
            stream.append(('copy', 660, q))
            for t, row in enumerate(w['scatter']):
                if k in row:
                    stream.append(('add', 120+t, 660))
            stream.append(('erase', 660, q))
    else:
        for frame, d, sources in w[section]:
            stream.extend(('add', d, s) for s in sources)
base = [1]*661
for op, d, s in reversed(stream):
    if op == 'add':
        base[d] += base[s]
    else:
        base[d] = base[s] if op == 'erase' else 0


def measure(parents):
    order = v.traversal(parents)
    norms = base[:]
    for t in reversed(order):
        if parents[t] != 120:
            norms[120+t] += norms[120+parents[t]]
    for t, p in enumerate(parents):
        row = K[t] ^ (K[p] if p != 120 else 0)
        norms[120+t] += sum(base[s] for s in range(240, 660) if row >> s & 1)
    for t in order:
        if parents[t] != 120:
            norms[120+t] += norms[120+parents[t]]
    reverse = max(norms)
    return v.forest_cost(K, parents), reverse, (64*144651**3*reverse**2).bit_length()


best = None
for attempt in range(256):
    rng = random.Random(5+attempt)
    edges = [(row.bit_count(), rng.random(), 120, t) for t, row in enumerate(K)]
    edges += [((K[i]^K[j]).bit_count()+2, rng.random(), i, j) for i in range(120) for j in range(i)]
    components = list(range(121))
    adjacency = [[] for _ in range(121)]
    def component(x):
        while components[x] != x:
            x = components[x]
        return x
    for cost, tie, a, b in sorted(edges):
        ca, cb = component(a), component(b)
        if ca != cb:
            components[ca] = cb
            adjacency[a].append(b)
            adjacency[b].append(a)
    parents = {120: None}
    queue = [120]
    for a in queue:
        for b in adjacency[a]:
            if b not in parents:
                parents[b] = a
                queue.append(b)
    parents = [parents[t] for t in range(120)]
    cost, reverse, bits = measure(parents)
    v.need(cost == 14921, 'nominated tree must attain certified floor')
    key = bits, reverse, attempt
    if best is None or key < best[0]:
        best = key, parents
minimum = best[1]
feasible = minimum[:]
cuts = []
while measure(feasible)[2] > 104:
    cost0, reverse0, _ = measure(feasible)
    candidates = []
    for t, p in enumerate(feasible):
        if p == 120:
            continue
        proposal = feasible[:]
        proposal[t] = 120
        cost, reverse, bits = measure(proposal)
        if reverse < reverse0:
            v.need(cost > cost0, 'this cut domain has positive extra cost')
            candidates.append((Fraction(reverse0-reverse, cost-cost0), -cost, -reverse, t))
    v.need(candidates, 'no improving precision cut')
    t = max(candidates)[-1]
    cuts.append(t)
    feasible[t] = 120
recipe = {'assignment_seed':5, 'minimum_parents':minimum,
          'minimum_search_attempt':best[0][2], 'feasible_parents':feasible,
          'cut_vertices':cuts, 'search_attempts':256}
v.need(recipe == json.loads((HERE/'RECIPE.json').read_text()), 'nomination reproduction mismatch')
print('PASS_FOREST_DISCOVERY trees=256 chosen_attempt='+str(best[0][2])+' cuts='+str(cuts)+' cost='+str(measure(feasible)[0]))
