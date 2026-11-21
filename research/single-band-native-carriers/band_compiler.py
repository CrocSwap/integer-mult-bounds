"""Compile one finite chronological band of a strict tensor rule."""

from dataclasses import dataclass
from functools import cache
from itertools import product
from math import prod

from periodic import Plan, Unit, period, power_ceiling


@dataclass(frozen=True)
class Band:
    layers: dict
    sources: tuple
    prefixes: frozenset
    height: int
    terminal_axes: int
    fringe_axes: int


def forest(rule, limit, floor):
    if floor < 2:
        raise ValueError("The virtual column floor must be at least two")
    if limit < rule.ambient * floor:
        return None
    high, low = min(rule.targets), max(rule.paid)
    if high < 2 * low:
        raise ValueError("Use a twofold gap between target and paid ranks")
    numerator, denominator, height = 1, 1, 0
    while rule.ambient * numerator <= limit * denominator:
        numerator *= high
        denominator *= low
        height += 1

    paid_ids = range(len(rule.paid))
    target_ids = range(len(rule.targets))
    layers, sources = {}, []
    terminal, fringe = 0, 0
    for depth in range(1, height):
        for path in product(paid_ids, repeat=depth):
            prefix = prod(rule.paid[i] for i in path)
            previous_rank = rule.paid[path[-1]]
            units = []
            for future in product(target_ids, repeat=height - depth):
                x = prefix * prod(rule.targets[i] for i in future)
                if x < floor * denominator or rule.ambient * x > limit * denominator:
                    continue
                columns = x // denominator - 1
                ports = []
                for i, rank in enumerate(rule.targets):
                    if rule.ambient * x * rank > limit * denominator * previous_rank:
                        ports.append(("source", len(sources)))
                        sources.append((path, future, i, rank * columns))
                    else:
                        parent_columns = x * rank // (previous_rank * denominator) - 1
                        residue = previous_rank * parent_columns - rank * columns
                        if not 0 <= residue < 2 * rank:
                            raise ArithmeticError("The paying native unit cannot fund the input")
                        fringe += residue
                        ports.append(("parent", (i,) + future))
                consumer_target = rule.targets[future[0]]
                for paid in rule.paid:
                    if x * paid < floor * denominator * consumer_target:
                        terminal += paid * columns
                units.append(Unit(future, columns, tuple(ports)))
            if units:
                layers[path] = tuple(units)
    if not sources:
        return None
    prefixes = {path[:d] for path in layers for d in range(len(path) + 1)}
    return Band(layers, tuple(sources), frozenset(prefixes), height, terminal, fringe)


def make_planner(rule, floor):
    @cache
    def plan(n):
        if n < 1:
            raise ValueError("A positive rank is required")
        active = n - n % 4
        band = forest(rule, active // 4, floor)
        if band is None:
            return Plan(n, n, None, (), (), 0, 0, 1, 1, n)
        periods = tuple(period(active, root[-1]) for root in band.sources)
        rounds = max(periods)
        offsets, slots = [], 0
        for q in periods:
            offsets.append(slots)
            slots += rounds // q
        width = power_ceiling(15 * slots)
        copies = (width + slots - 1) // slots
        leaves = (n - active) * width + rounds * copies * (band.terminal_axes + band.fringe_axes)
        return Plan(n, active, band, periods, tuple(offsets), rounds, copies, slots, width, leaves)

    return plan
