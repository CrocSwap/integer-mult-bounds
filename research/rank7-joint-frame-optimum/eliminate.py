# SPDX-License-Identifier: Apache-2.0
"""Finite min-sum variable elimination, including exact assignment counts."""

from dataclasses import dataclass
from itertools import product
from math import prod

from costs import certificate, compare
from graph import profile
from spaces import domain, rank, require


@dataclass(frozen=True)
class Value:
    profile: tuple[int, ...]
    optimal: int = 1
    feasible: int = 1


@dataclass
class Factor:
    scope: tuple[int, ...]
    table: dict[tuple[int, ...], Value]


def edge_factor(edge, choices):
    _, a, before, b, after = edge
    scope = tuple(sorted(i for i in (a, b) if i in choices))
    require(len(scope) in (1, 2) and len(set(scope)) == len(scope), "variable edge")
    table = {}
    for values in product(*(range(len(choices[i])) for i in scope)):
        assignment = {i: choices[i][v] for i, v in zip(scope, values, strict=True)}
        lo, hi = assignment.get(a, before), assignment.get(b, after)
        if lo <= hi:
            paid = [0] * 10
            paid[rank(hi) - rank(lo)] = 1
            table[values] = Value(tuple(paid))
    return Factor(scope, table)


def combine(values):
    return Value(tuple(map(sum, zip(*(v.profile for v in values), strict=True))),
                 prod(v.optimal for v in values), prod(v.feasible for v in values))


def projected_factor(variable, neighbours, factors, choices, proof_vectors):
    scope = tuple(sorted(neighbours))
    variables = (variable, *scope)
    positions = [tuple(variables.index(i) for i in f.scope) for f in factors]
    attempts = prod(len(choices[i]) for i in variables)
    require(attempts <= 4096, "at most 4096 elimination candidates")
    table = {}
    feasible_candidates = 0
    for labels in product(*(range(len(choices[i])) for i in variables)):
        values = [f.table.get(tuple(labels[j] for j in indexes))
                  for f, indexes in zip(factors, positions, strict=True)]
        if any(v is None for v in values):
            continue
        feasible_candidates += 1
        candidate, key = combine(values), labels[1:]
        if key not in table:
            table[key] = candidate
            continue
        previous = table[key]
        order = compare(candidate.profile, previous.profile)
        delta = tuple(x - y for x, y in
                      zip(candidate.profile, previous.profile, strict=True))
        proof_vectors.add(delta if order >= 0 else tuple(-x for x in delta))
        winner = candidate if order < 0 else previous
        optimal = winner.optimal if order else candidate.optimal + previous.optimal
        table[key] = Value(winner.profile, optimal, candidate.feasible + previous.feasible)
    require(len(table) <= 4096, "bounded projected factor")
    return Factor(scope, table), attempts, feasible_candidates


def solve_component(component, edges, lower, upper):
    require(len(component) <= 128, "component capacity")
    members = set(component)
    owned = [e for e in edges if e[1] in members or e[3] in members]
    require(len(owned) <= 512, "component edge capacity")
    choices = {i: domain(lower[i], upper[i]) for i in component}
    factors = [edge_factor(e, choices) for e in owned]
    graph = {i: set() for i in component}
    for factor in factors:
        for i in factor.scope:
            graph[i].update(set(factor.scope) - {i})
    proof_vectors, order = set(), []
    attempts = candidates = states = max_attempts = max_width = 0
    for _ in range(len(component)):
        require(sum(len(f.table) for f in factors) <= 32768, "live factor capacity")
        variable = min(graph, key=lambda i: (
            prod(len(choices[j]) for j in graph[i] | {i}), len(graph[i]), i))
        neighbours = graph[variable]
        touched = [f for f in factors if variable in f.scope]
        factors = [f for f in factors if variable not in f.scope]
        new, count, valid = projected_factor(variable, neighbours, touched,
                                             choices, proof_vectors)
        require(new.table, "nonempty projected factor")
        factors.append(new)
        order.append(variable)
        attempts += count
        candidates += valid
        states += len(new.table)
        max_attempts, max_width = max(max_attempts, count), max(max_width, len(neighbours))
        for j in neighbours:
            graph[j].update(neighbours - {j})
            graph[j].remove(variable)
        del graph[variable]
    require(all(not f.scope for f in factors), "all component variables eliminated")
    optimum = combine([f.table[()] for f in factors])
    baseline = profile(owned, {})
    return {"variables": list(component), "order": order,
            "domain_sizes": [len(choices[i]) for i in component],
            "edges": len(owned), "attempts": attempts, "candidates": candidates,
            "states": states, "max_bucket": max_attempts, "max_width": max_width,
            "feasible": optimum.feasible, "optimal": optimum.optimal,
            "source_profile": baseline, "optimum_profile": optimum.profile,
            "source_comparison": compare(baseline, optimum.profile)}, proof_vectors


def proof_summary(vectors):
    types = {}
    exceptional = []
    for delta in sorted(vectors):
        proof = certificate(delta)
        require(proof is not None, "every stored comparison proved")
        kind, value = proof
        types[kind] = types.get(kind, 0) + 1
        if kind == "taylor":
            floor = value.numerator * 10**6 // value.denominator
            exceptional.append({"delta": delta, "positive_margin_floor_millionths": floor})
    return {"distinct_comparisons": len(vectors), "methods": types,
            "taylor_inequalities": exceptional}
