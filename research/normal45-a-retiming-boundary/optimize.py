# SPDX-License-Identifier: Apache-2.0
"""Exact finite-domain variable elimination with certified moment comparisons.

No numerical optimizer is used. Each DP cell stores its rank-count vector.
Every nontrivial comparison has a strict rationally certified sign throughout
B_LO..B_HI; ambiguous comparisons fail. Equal vectors are symbolic ties.
Tekalign, with substantial OpenAI Codex assistance.
"""
import collections
import itertools
from fractions import Fraction as Q
from functools import lru_cache
import frames as f
import common as s
import exact_root

B_LO = Q('0.001722816319863214327995')
B_HI = Q('0.001722816319863214327998')
SCALE = 10**40
ZERO = (0,) * 9


@lru_cache(None)
def interval(lo, hi):
    span = [0]
    for v in hi:
        span += [x ^ v for x in span]
    found, pending = {lo}, [lo]
    while pending:
        frame = pending.pop()
        for v in span:
            nxt = f.join(frame, (v,))
            if nxt not in found:
                found.add(nxt)
                pending.append(nxt)
    return sorted(found, key=lambda x: (len(x), x))


@lru_cache(None)
def prices():
    return tuple((int(exact_root.H(r, B_LO)[0] * SCALE),
                  (exact_root.H(r, B_HI)[1] * SCALE).__ceil__())
                 for r in range(1, 10))


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def compare(a, b, stats):
    delta = tuple(x - y for x, y in zip(a, b))
    if not any(delta):
        stats['symbolic_ties'] += 1
        return 0
    lower = sum(d * (p[0] if d >= 0 else p[1]) for d, p in zip(delta, prices()))
    upper = sum(d * (p[1] if d >= 0 else p[0]) for d, p in zip(delta, prices()))
    s.require(upper < 0 or lower > 0, 'unresolved exact cost comparison')
    stats['strict_comparisons'] += 1
    margin = -upper if upper < 0 else lower
    stats['minimum_margin_scaled'] = min(stats.get('minimum_margin_scaled', margin), margin)
    return -1 if upper < 0 else 1


def optimize(word):
    _, model = f.solve(word)
    domains = {i: interval(model['lo'][i], model['hi'][i]) for i in model['pred']
               if model['lo'][i] != model['hi'][i] and i not in model['fixed']}
    fixed = {**model['lo'], **model['fixed']}
    edges = collections.Counter((j, i) for i, ps in model['pred'].items() for j in ps)
    for r, frame in enumerate(model['upper']):
        if r in word['removed']:
            continue
        node = 10000 + r
        fixed[node] = frame
        edges[(model['last'][r], node)] += 1
    factors, constant = [], ZERO
    for (i, j), multiplicity in edges.items():
        variables = tuple(k for k in (i, j) if k in domains)
        table = {}
        for assignment in itertools.product(*(range(len(domains[k])) for k in variables)):
            vals = dict(zip(variables, assignment))
            left = domains[i][vals[i]] if i in domains else fixed[i]
            right = domains[j][vals[j]] if j in domains else fixed[j]
            if f.join(left, right) != right:
                continue
            delta = len(right) - len(left)
            vec = list(ZERO)
            if delta:
                vec[delta - 1] = multiplicity
            table[assignment] = tuple(vec)
        if variables:
            factors.append((variables, table))
        else:
            constant = add(constant, table[()])
    stats = {'free_nodes': len(domains), 'maximum_table_entries': 0,
             'strict_comparisons': 0, 'symbolic_ties': 0}
    remaining, backs = set(domains), []
    while remaining:
        def neighbors(v):
            return set().union(*(set(vs) for vs, _ in factors if v in vs)) - {v}
        def envelope(v):
            size = 1
            for other in neighbors(v):
                size *= len(domains[other])
            return size
        node = min(remaining, key=lambda v: (envelope(v), v))
        touched = [z for z in factors if node in z[0]]
        others = sorted(neighbors(node))
        indices = [tuple(([node] + others).index(k) for k in vs) for vs, _ in touched]
        table, back = {}, {}
        for assignment in itertools.product(*(range(len(domains[k])) for k in others)):
            best, choice = None, None
            for value in range(len(domains[node])):
                all_values, cost = (value,) + assignment, ZERO
                for (_, data), ix in zip(touched, indices):
                    term = data.get(tuple(all_values[j] for j in ix))
                    if term is None:
                        cost = None
                        break
                    cost = add(cost, term)
                if cost is not None and (best is None or compare(cost, best, stats) < 0):
                    best, choice = cost, value
            if best is not None:
                table[assignment], back[assignment] = best, choice
        stats['maximum_table_entries'] = max(stats['maximum_table_entries'], len(table))
        factors = [z for z in factors if node not in z[0]]
        if others:
            factors.append((tuple(others), table))
        else:
            constant = add(constant, table[()])
        backs.append((node, others, back))
        remaining.remove(node)
    assignment = {}
    for node, others, back in reversed(backs):
        assignment[node] = back[tuple(assignment[j] for j in others)]
    for i, k in assignment.items():
        word['A'][i][-1] = list(domains[i][k])
    profile, inventory = s.pm.frame_report(word)
    word['report']['local_profile'] = profile
    s.require(inventory == word['report']['width_inventory'], 'unchanged inventory')
    stats['optimized_variable_profile'] = list(constant)
    return word, stats
