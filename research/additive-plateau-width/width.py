"""Exact small chronological libraries and the additive plateau divisor.

New refinement produced by Nick Petalas. Apache-2.0.
The numerical recurrence is credited in README.md; no source code is imported.
"""
from collections import Counter
from itertools import product
from math import gcd, lcm, prod

MAX_N = 256
MAX_ROLES = 4


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_rule(ambient, targets, paid, maximum):
    require(type(ambient) is int and type(maximum) is int,
            "ambient and maximum must be integers")
    require(2 <= ambient <= MAX_N and 1 <= maximum <= MAX_N,
            "bounded checker requires 2 <= ambient <= 256 and 1 <= N <= 256")
    for roles in (targets, paid):
        require(isinstance(roles, tuple) and 1 <= len(roles) <= MAX_ROLES,
                "supply one to four explicit roles")
        require(all(type(x) is int and x > 0 for x in roles),
                "role ranks must be positive integers")
    require(2 <= min(targets) and max(targets) <= ambient,
            "productive ranks must lie in [2, ambient]")
    require(max(paid) < min(targets), "paid ranks must be separated")


def semigroup(generators, cap):
    """Integer-by-integer membership, with an explicit cap."""
    require(type(cap) is int and 1 <= cap <= MAX_N * MAX_N,
            "semigroup cap out of range")
    require(isinstance(generators, tuple) and 1 <= len(generators) <= 2 * MAX_ROLES
            and all(type(g) is int and g >= 2 for g in generators),
            "semigroup generators must be at least two")
    present = [False] * (cap + 1)
    present[1] = True
    for value in range(2, cap + 1):
        present[value] = any(value % g == 0 and present[value // g]
                             for g in generators)
    return tuple(i for i in range(1, cap + 1) if present[i])


def literal_census(ambient, targets, paid, gamma):
    """Expand role words and paid paths, without pooling chronological exits."""
    validate_rule(ambient, targets, paid, ambient)
    require(type(gamma) is int and 1 <= gamma <= MAX_N // ambient,
            "census cap exceeds the bounded library")
    height = max(j for j in range(gamma.bit_length()) if min(targets) ** j <= gamma)
    sources = Counter()
    for depth in range(height + 1):
        for path in product(paid, repeat=depth):
            rho = prod(path)
            for word in product(targets, repeat=height - depth):
                column = rho * prod(word)
                if column > gamma:
                    continue
                for rank in targets:
                    sources[column * rank] += 1
                if depth < height:
                    for rank in paid:
                        sources[column * rank] -= 1
    require(all(t >= 0 for t in sources.values()), "negative source multiplicity")
    sources = {s: t for s, t in sorted(sources.items()) if t}
    exits = tuple(prod(path) for path in product(paid, repeat=height + 1))
    require(bool(sources) and min(sources) > gamma, "missing fresh-source floor")
    require(max(sources) <= ambient * gamma, "source exceeds its parent")
    require(all(0 < e < ambient * gamma for e in exits), "exit stays on plateau")
    return sources, exits


def plateaus(ambient, targets, paid, maximum):
    validate_rule(ambient, targets, paid, maximum)
    if maximum < ambient:
        return ()
    cap = maximum // ambient
    generators = tuple(sorted(set(targets + paid) - {1}))
    points = semigroup(generators, min(targets) * cap)
    tau = ambient * (min(targets) - 1).bit_length()
    rows = []
    for gamma, successor in zip(points, points[1:]):
        if gamma > cap:
            break
        sources, exits = literal_census(ambient, targets, paid, gamma)
        low, high = ambient * gamma, min(maximum, ambient * successor - 1)
        delta = min(sources)
        additive = 1 + (high - low) // delta
        visits = additive
        require(1 <= visits <= ambient - 1 < tau, "invalid visit budget")
        rows.append((low, high, sources, exits, visits, tau))
    require(rows and rows[-1][1] == maximum, "incomplete plateau cover")
    return tuple(rows)


def library(ambient, targets, paid, maximum):
    """Evaluate only widths and their actual directed child graph."""
    rows = plateaus(ambient, targets, paid, maximum)
    widths = [1] * (maximum + 1)
    children = [()] * (maximum + 1)
    new_divisor, old_divisor = 1, 1
    for low, high, sources, exits, visits, tau in rows:
        total = sum(sources.values())
        new_divisor *= total ** visits
        old_divisor *= total ** tau
        for rank in range(low, high + 1):
            replication = 1
            edges = []
            for source, count in sources.items():
                child = rank - source
                if child:
                    replication = lcm(replication, widths[child] // gcd(widths[child], count))
                    edges.append(child)
            for child in exits:
                replication = lcm(replication, widths[child])
                edges.append(child)
            widths[rank] = total * replication
            children[rank] = tuple(edges)
    return rows, tuple(widths), tuple(children), new_divisor, old_divisor


def maximum_visits(children, low, high):
    """Longest visits found by dynamic programming on the literal child DAG."""
    require(0 < low <= high < len(children) <= MAX_N + 1, "invalid plateau interval")
    visits = [0] * (high + 1)
    for rank in range(low, high + 1):
        require(all(0 <= child < rank for child in children[rank]), "nondecreasing child")
        visits[rank] = 1 + max((visits[c] for c in children[rank] if c >= low), default=0)
    return max(visits)
