"""Count band incidences by rank. Generate the labelled operations at their point of use."""

from collections import Counter
from dataclasses import dataclass
from functools import cache


def multiply_counts(left, right):
    result = Counter()
    for a, count_a in left.items():
        for b, count_b in right.items():
            result[a * b] += count_a * count_b
    return result


def power_counts(grades, exponent):
    result = {1: 1}
    for _ in range(exponent):
        result = multiply_counts(result, grades)
    return result


def split_runs(rank, cap):
    """Return (length, repetitions) in the order of the disjoint physical slices."""
    if rank <= cap:
        yield rank, 1
        return
    full, tail = divmod(rank, cap)
    yield cap, full
    while tail:
        length = 1 << (tail.bit_length() - 1)
        yield length, 1
        tail -= length


class GradeRule:
    def __init__(self, word):
        if word.low_cut != word.high_cut:
            raise ValueError("This construction uses one paid cap")
        self.word = word
        self.ambient = word.ambient**word.power
        self.cap = word.low_cut**word.power

    @cache
    def grades(self):
        word = self.word
        paid = Counter()
        full = power_counts(Counter(x.rank for x in word.paid), word.power)
        for rank, count in full.items():
            for size, repeat in split_runs(rank, self.cap):
                paid[size] += count * repeat
        floor = word.floor**word.power
        full = power_counts(Counter(x.rank for x in word.targets), word.power)
        targets = {k: count for k, count in full.items() if k >= floor}
        return targets, paid

    def target_ranks(self):
        return (port.rank for port, keep in self.word.target_paths() if keep)

    def paid_ranks(self):
        return (block.rank for block in self.word.paid_paths())


@dataclass(frozen=True)
class Band:
    height: int
    denominator: int
    floor: int
    limit: int
    terminal: int
    fringe: int


@dataclass(frozen=True)
class Plan:
    rank: int
    active: int
    forest: Band | None
    rounds: int
    owners_per_copy: int
    width: int
    copies: int
    leaves: int


def period(rank, size):
    return 1 << (((rank + size - 1) // size) - 1).bit_length()


def census(rule, rank, floor):
    if rank < 1 or floor < 2:
        raise ValueError("Supply a positive rank and a column floor of at least two")
    active = rank - rank % 4
    limit = active // 4
    ambient = rule.ambient
    stopped = Plan(rank, rank, None, 0, 1, 1, 0, rank)
    if limit < ambient * floor:
        return stopped
    targets, paid = rule.grades()
    high, low = min(targets), max(paid)
    if high < 2 * low:
        raise ValueError("The target floor must reach twice the largest paid cut")
    numerator = denominator = 1
    height = 0
    while ambient * numerator <= limit * denominator:
        numerator *= high
        denominator *= low
        height += 1
    periods = Counter()
    terminal = fringe = 0
    prefix = {1: 1}
    for depth in range(1, height):
        rest = power_counts(targets, height - depth - 1)
        middle = multiply_counts(prefix, rest)
        for interior, multiplicity in middle.items():
            for last, lenders in paid.items():
                for first, consumers in targets.items():
                    x = interior * last * first
                    if x < floor * denominator or ambient * x > limit * denominator:
                        continue
                    copies = multiplicity * lenders * consumers
                    columns = x // denominator - 1
                    for k, ports in targets.items():
                        if ambient * x * k > limit * denominator * last:
                            periods[period(active, k * columns)] += copies * ports
                        else:
                            other = x * k // (denominator * last) - 1
                            fringe += copies * ports * (last * other - k * columns)
                    for r, cuts in paid.items():
                        if x * r < floor * denominator * first:
                            terminal += copies * cuts * r * columns
        prefix = multiply_counts(prefix, paid)
    if not periods:
        return stopped
    rounds = max(periods)
    slots = sum(count * (rounds // q) for q, count in periods.items())
    width = 1 << (15 * slots - 1).bit_length()
    copies = (width + slots - 1) // slots
    leaves = (rank - active) * width + rounds * copies * (terminal + fringe)
    return Plan(rank, active, Band(height, denominator, floor, limit, terminal, fringe),
                rounds, slots, width, copies, leaves)
