"""Independent bounded explicit-occurrence and prime-valuation oracle.

No import from the production evaluator. Each productive role, paid site,
word and path is materialized. Widths use prime exponents; expanded costs
use independent rational per-array recurrences. Apache-2.0; OpenAI-assisted.
"""
from collections import Counter
from fractions import Fraction
from itertools import product
from math import prod


def demand(ok, message):
    if not ok:
        raise ValueError(message)


def literal_flow(ambient, targets, paid, rank):
    roles = tuple(k for k, count in targets for _ in range(count))
    sites = tuple(r for r, count in paid for _ in range(count))
    demand(rank >= ambient, "nonbase literal flow required")
    demand(len(roles) + len(sites) <= 32, "literal alphabet budget")
    degree, minimum_power = 0, min(roles)
    while minimum_power <= rank // ambient:
        degree += 1
        minimum_power *= min(roles)
    units, slots = {}, {}
    for depth in range(degree + 1):
        for path in product(range(len(sites)), repeat=depth):
            for word in product(range(len(roles)), repeat=degree - depth):
                column = prod(sites[j] for j in path) * prod(roles[i] for i in word)
                if ambient * column > rank:
                    continue
                unit = (path, word)
                units[unit] = column
                demand(len(units) <= 200000, "literal unit budget")
                for role, k in enumerate(roles):
                    slots[(unit, role)] = column * k
    consumed, cuts = set(), []
    for (path, word), column in units.items():
        for site, r in enumerate(sites):
            if word:
                child = (path + (site,), word[1:])
                port = (child, word[0])
                demand(child in units, "missing demanded literal child")
                demand(port not in consumed, "literal parent alias")
                demand(slots[port] == column * r, "literal rank mismatch")
                consumed.add(port)
            else:
                cuts.append((path + (site,), column * r))
    sources = Counter(value for port, value in slots.items() if port not in consumed)
    exits = Counter(value for _, value in cuts)
    demand(sources and all(rank < ambient * s and s <= rank for s in sources),
           "literal source band")
    demand(all(0 < e < rank for _, e in cuts), "literal exit descent")
    return {"height": degree, "units": len(units),
            "sources": tuple(sorted(sources.items())),
            "exits": tuple(sorted(exits.items())), "cuts": tuple(sorted(cuts))}


def factor_integer(value):
    demand(value >= 1 and value.bit_length() <= 64, "oracle factor budget")
    factors, divisor = {}, 2
    while divisor * divisor <= value:
        while value % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            value //= divisor
        divisor += 1
    if value > 1:
        factors[value] = factors.get(value, 0) + 1
    return factors


def explicit_library(ambient, targets, paid, maximum):
    rows, valuations, leaf_ratios, unit_ratios = [None], [None], [None], [None]
    flows, raw_cuts, raw_units, constraints = {}, 0, 0, 0
    for n in range(1, maximum + 1):
        if n < ambient:
            rows.append((1, 1, n, 0))
            valuations.append({})
            leaf_ratios.append(Fraction(n))
            unit_ratios.append(Fraction(0))
            continue
        flow = literal_flow(ambient, targets, paid, n)
        flows[n] = flow
        raw_cuts += len(flow["cuts"])
        raw_units += flow["units"]
        sources = flow["sources"]
        total = sum(count for _, count in sources)
        requirements = {}
        leaf = Fraction(0)
        unit = Fraction(flow["units"])
        for s, count in sources:
            if s == n:
                continue
            constraints += 1
            removed = factor_integer(count)
            for prime, exponent in valuations[n - s].items():
                requirements[prime] = max(requirements.get(prime, 0),
                                          exponent - removed.get(prime, 0))
            leaf += count * leaf_ratios[n - s]
            unit += count * unit_ratios[n - s]
        for _, e in flow["cuts"]:
            constraints += 1
            for prime, exponent in valuations[e].items():
                requirements[prime] = max(requirements.get(prime, 0), exponent)
            leaf += leaf_ratios[e]
            unit += unit_ratios[e]
        a = prod(prime ** exponent for prime, exponent in requirements.items())
        current = factor_integer(total)
        for prime, exponent in requirements.items():
            current[prime] = current.get(prime, 0) + exponent
        width = prod(prime ** exponent for prime, exponent in current.items())
        leaf /= total
        unit /= total
        leaves, occurrences = width * leaf, width * unit
        demand(leaves.denominator == occurrences.denominator == 1,
               "literal rational cost not integral")
        rows.append((a, width, int(leaves), int(occurrences)))
        valuations.append(current)
        leaf_ratios.append(leaf)
        unit_ratios.append(unit)
    return {"rows": tuple(rows), "flows": flows, "cuts": raw_cuts,
            "units": raw_units, "constraints": constraints}


def semigroup(generators, cap):
    """Explicit bounded multiplication closure, not an exponent-box estimate."""
    seen, todo = {1}, [1]
    while todo:
        value = todo.pop()
        for generator in generators:
            new = value * generator
            if new <= cap and new not in seen:
                seen.add(new)
                todo.append(new)
    return tuple(sorted(seen))
