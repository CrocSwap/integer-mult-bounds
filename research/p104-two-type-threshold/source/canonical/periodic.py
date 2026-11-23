"""Compile finite-order tensor jobs from a strict chronological mixed rule."""

from dataclasses import dataclass
from functools import cache
from itertools import product
from math import prod


@dataclass(frozen=True)
class Rule:
    ambient: int
    targets: tuple
    paid: tuple

    def __post_init__(self):
        if not self.targets or not self.paid:
            raise ValueError("Supply positive target and paid occurrence lists")
        if not 1 <= min(self.paid) <= max(self.paid) < min(self.targets) <= max(self.targets) <= self.ambient:
            raise ValueError("The paid ceiling must be below the productive floor")


def power_ceiling(x):
    return 1 << (x - 1).bit_length()


def period(length, rank):
    """Return the power-of-two number of full rank-rank jobs for one field."""
    if length <= 0 or length % 4 or not 1 <= rank <= length // 4:
        raise ValueError("Use a positive multiple of four with four rank blocks")
    return power_ceiling((length + rank - 1) // rank)


def row_axes(length, rank, rounds, row):
    """Emit the actual ordered axis subset for this complete invocation."""
    if rounds != period(length, rank) or not 0 <= row < rounds:
        raise ValueError("Invalid period or invocation")
    five = (rounds * rank - length) // 4
    for ticket in range(row, rounds * rank, rounds):
        yield ticket // 5 if ticket < 5 * five else ticket - 4 * five


@dataclass(frozen=True)
class Unit:
    future: tuple
    columns: int
    # Each port is (source, source-id) or (parent, future of the paying unit).
    ports: tuple


@dataclass(frozen=True)
class Forest:
    # The key is a chronological path of individual paid occurrence labels.
    layers: dict
    sources: tuple
    exits: dict
    height: int


def forest(rule, limit):
    """Enumerate the source ports and the separate paid cuts of the live forest."""
    if limit < rule.ambient:
        raise ValueError("The live forest needs one full working ambient")
    height, smallest = 0, rule.ambient
    while smallest * min(rule.targets) <= limit:
        smallest *= min(rule.targets)
        height += 1
    layers, sources, exits = {}, [], {}
    target_ids = range(len(rule.targets))
    paid_ids = range(len(rule.paid))
    for depth in range(height + 1):
        for path in product(paid_ids, repeat=depth):
            history = prod(rule.paid[i] for i in path)
            units = []
            for future in product(target_ids, repeat=height - depth):
                columns = history * prod(rule.targets[i] for i in future)
                if columns * rule.ambient > limit:
                    continue
                ports = []
                for i, rank in enumerate(rule.targets):
                    parent = (i,) + future
                    if path and columns // rule.paid[path[-1]] * rank * rule.ambient <= limit:
                        ports.append(("parent", parent))
                    else:
                        ports.append(("source", len(sources)))
                        sources.append((path, future, i, rank * columns))
                units.append(Unit(future, columns, tuple(ports)))
            layers[path] = tuple(units)
            if depth == height:
                if len(units) != 1:
                    raise ArithmeticError("The final paid cut lost its only unit")
                for j, rank in enumerate(rule.paid):
                    exits[path + (j,)] = rank * history
    return Forest(layers, tuple(sources), exits, height)


@dataclass(frozen=True)
class Plan:
    rank: int
    active: int
    forest: object
    periods: tuple
    offsets: tuple
    rounds: int
    copies: int
    owners_per_copy: int
    width: int
    leaves: int


def make_planner(rule):
    @cache
    def plan(n):
        if n < 1:
            raise ValueError("A positive rank is required")
        active = n - n % 4
        if active // 4 < rule.ambient:
            return Plan(n, n, None, (), (), 0, 0, 1, 1, n)
        f = forest(rule, active // 4)
        periods = tuple(period(active, item[-1]) for item in f.sources)
        rounds = max(periods)
        offsets, slots = [], 0
        for k in periods:
            offsets.append(slots)
            slots += rounds // k
        divisor = max(plan(e).width for e in f.exits.values())
        raw = divisor * slots
        width = power_ceiling(15 * raw)
        copies = ((width + raw - 1) // raw) * divisor
        if not 15 * width <= 15 * copies * slots < 16 * width:
            raise ArithmeticError("Incorrect dyadic batch padding")
        leaves = (n - active) * width
        for e in f.exits.values():
            smaller = plan(e)
            if copies % smaller.width:
                raise ArithmeticError("A chronological child lost a full group")
            leaves += rounds * (copies // smaller.width) * smaller.leaves
        return Plan(n, active, f, periods, tuple(offsets), rounds, copies, slots, width, leaves)
    return plan


@dataclass(frozen=True)
class Job:
    """Use an ordered active basis on this field. Store full adapters at the boundary."""

    owner: object
    axes: tuple

    def select(self, indices):
        return Job(self.owner, tuple(self.axes[i] for i in indices))


def run(rule, n, fields, machine, *, planner=None):
    """Run all root, native, adapter, leaf, guard and cleanup operations in order.

    The native iterator supplied by the source performs its local instructions.
    It yields one actual paid job at each chronological source position.
    A full-data adapter may instead open a rank job in its canonical basis,
    run the resulting subcall, and close the adapter after it returns.
    """
    plan = make_planner(rule) if planner is None else planner

    def satisfy(rank, lanes):
        p = plan(rank)
        if (len(lanes) != p.width or len({j.owner for j in lanes}) != len(lanes)
                or any(len(j.axes) != rank for j in lanes)):
            raise ValueError("Expected one independent full field per live lane")
        if p.forest is None:
            for job in lanes:
                for axis in job.axes:
                    machine.leaf(Job(job.owner, (axis,)))
            return
        # Every slot beyond the dyadic productive width has its own owned field.
        expanded = list(lanes)
        for _ in range(p.copies * p.owners_per_copy - p.width):
            expanded.append(machine.zero(lanes[0]))
        for iteration in range(p.rounds):
            def process(path, previous):
                units = p.forest.layers[path]
                frames = []
                for u in units:
                    per_copy = []
                    for replica in range(p.copies):
                        ports = []
                        for kind, label in u.ports:
                            if kind == "parent":
                                ports.append(previous[label][replica])
                            else:
                                k = p.periods[label]
                                index = (replica * p.owners_per_copy + p.offsets[label]
                                         + iteration // k)
                                s = p.forest.sources[label][-1]
                                subset = row_axes(p.active, s, k, iteration % k)
                                ports.append(expanded[index].select(subset))
                        per_copy.append(iter(machine.native(tuple(ports), u.columns)))
                    frames.append(per_copy)
                for j, paid in enumerate(rule.paid):
                    requests = {}
                    for u, group in zip(units, frames, strict=True):
                        jobs = [next(frame) for frame in group]
                        if any(len(job.axes) != paid * u.columns for job in jobs):
                            raise ValueError("The actual native request has a different rank")
                        requests[u.future] = jobs
                    cut = path + (j,)
                    if len(path) < p.forest.height:
                        process(cut, requests)
                    else:
                        e = p.forest.exits[cut]
                        width = plan(e).width
                        group = requests[()]
                        for i in range(0, len(group), width):
                            satisfy(e, group[i:i + width])
                sentinel = object()
                for group in frames:
                    for frame in group:
                        if next(frame, sentinel) is not sentinel:
                            raise ValueError("An unserved native request remained")
            process((), {})
        for job in lanes:
            for axis in job.axes[p.active:]:
                machine.leaf(Job(job.owner, (axis,)))
        for job in reversed(expanded[len(lanes):]):
            machine.retire_zero(job)
    satisfy(n, fields)
