#!/usr/bin/env python3
"""Independent Prim optimum and direct set-valued D verification; no local imports.
Oscar Fennell, with substantial OpenAI Codex assistance; Apache-2.0.
"""
import gzip
import hashlib
import heapq
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
word = json.loads(gzip.decompress((ROOT/'research/e8-bit-r420/data/bitE8mut-r420.json.gz').read_bytes()))
pins = json.loads((HERE/'SOURCES.json').read_text())
raw = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
if hashlib.sha256(raw).hexdigest() != pins['files']['research/e8-bit-r420/data/bitE8mut-r420.json.gz']:
    raise ValueError('source mismatch')
coefficients = [set() for _ in range(120)]
for frame, dst, source in word['D']:
    coefficients[dst-120].symmetric_difference_update(source)
coefficients.append(set())
# Prim, rather than nomination's Kruskal or the verifier's cycle inequalities.
reached = {120}
queue = [(len(coefficients[t]), t) for t in range(120)]
heapq.heapify(queue)
minimum = 0
while len(reached) < 121:
    cost, vertex = heapq.heappop(queue)
    if vertex in reached:
        continue
    minimum += cost
    reached.add(vertex)
    for other in range(120):
        if other not in reached:
            heapq.heappush(queue, (len(coefficients[vertex] ^ coefficients[other])+2, other))
if minimum != 14921:
    raise ValueError('independent forest optimum')
recipe = json.loads((HERE/'RECIPE.json').read_text())
parents = recipe['feasible_parents']
depths = []
for vertex in range(120):
    path = set()
    current = vertex
    while current != 120:
        if current in path or not 0 <= current < 120:
            raise ValueError('not a rooted forest')
        path.add(current)
        current = parents[current]
    depths.append(len(path))
# Decreasing depth implements y_v ^= y_parent before the parent is changed.
prepare = sorted((v for v in range(120) if parents[v] != 120), key=lambda v: (-depths[v], v))
state = [{r} for r in range(660)]
for vertex in prepare:
    state[120+vertex] ^= state[120+parents[vertex]]
correction_cost = 0
for vertex in range(120):
    patch = coefficients[vertex] ^ coefficients[parents[vertex]]
    correction_cost += len(patch)
    state[120+vertex] ^= patch
for vertex in reversed(prepare):
    state[120+vertex] ^= state[120+parents[vertex]]
expected = [{r} for r in range(660)]
for vertex in range(120):
    expected[120+vertex] |= coefficients[vertex]
if state != expected:
    raise ValueError('independent arbitrary-dirty D operator')
cost = correction_cost + 2*len(prepare)
if cost != 15138 or len(prepare) != 108:
    raise ValueError('independent circuit invoice')
cert = json.loads((HERE/'CERTIFICATE.json').read_text())
if cert['minimum_forest_certificate']['cost'] != minimum or cert['feasible_forest']['D_XORs'] != cost:
    raise ValueError('certificate differs from independent calculation')
print('PASS_INDEPENDENT_FOREST minimum=14921 feasible=15138 preparation=108 restoration=108 dirty_columns=660')
