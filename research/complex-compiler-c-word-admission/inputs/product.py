"""Build a normalized single-grade word from a literal chronological native program."""

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from itertools import product
from math import prod

from schedule import Word, complete_order


@dataclass(frozen=True)
class Native:
    ambient: int
    targets: tuple[int, ...]
    paid: tuple[int, ...]
    run: Callable  # run(machine, owners, columns) yields the actual normalized requests.


def compose(outer, inner):
    """Suspend distinct outer instances and finish one inner word at each paid position."""
    def run(machine, owners, columns):
        width = len(outer.targets)
        instances = [iter(outer.run(machine, owners[j*width:(j+1)*width], h*columns))
                     for j, h in enumerate(inner.targets)]
        for rank in outer.paid:
            placements = []
            for target, instance in zip(inner.targets, instances):
                owner, axes = next(instance)
                if len(axes) != rank * target * columns:
                    raise ValueError("outer request does not match this inner target")
                order = complete_order(axes, machine.n)
                placements.append((owner, order))
            if len({owner for owner, _ in placements}) != len(placements):
                raise ValueError("outer instances alias a paid owner")
            for owner, order in placements:
                machine.move(owner, order, False)
            yield from inner.run(machine, [owner for owner, _ in placements], rank * columns)
            for owner, order in placements:
                machine.move(owner, order, True)
        end = object()
        if any(next(instance, end) is not end for instance in instances):
            raise ValueError("unfinished outer instance")

    return Native(outer.ambient * inner.ambient,
                  tuple(h * k for h in inner.targets for k in outer.targets),
                  tuple(r * s for r in outer.paid for s in inner.paid), run)


def specialize(raw, counts, cutoff):
    """Return a homogeneous Word and the native callback for schedule.expand."""
    typed = {}
    for key, number in counts.items():
        rank = int(key)
        if (type(key) is not int and str(rank) != key) or rank in typed or rank not in raw.targets:
            raise ValueError("invalid or duplicate native grade")
        if type(number) is not int or number < 0:
            raise ValueError("invalid type multiplicity")
        typed[rank] = number
    counts = {rank: n for rank, n in typed.items() if n}
    if not counts:
        raise ValueError("empty target type")
    if any(type(k) is not int or not 1 <= k <= raw.ambient for k in raw.targets + raw.paid):
        raise ValueError("a native rank exceeds its ambient")
    v = sum(counts.values())
    grade = prod(k**n for k, n in counts.items())
    if not 1 <= cutoff < grade:
        raise ValueError("the paid cutoff must be positive and below the type rank")
    source = raw
    for _ in range(1, v):
        source = compose(raw, source)
    keep = [Counter(path) == counts for path in product(raw.targets, repeat=v)]
    split_ranks = []
    for rank in source.paid:
        quotient, tail = divmod(rank, cutoff)
        split_ranks.extend([cutoff] * quotient)
        if tail:
            split_ranks.append(tail)
    word = Word(source.ambient, grade, sum(keep), tuple(split_ranks))

    def native(machine, owners, columns):
        public = iter(owners)
        discarded = []
        slots = []
        for retain in keep:
            if retain:
                slots.append(next(public))
            else:
                blank = machine.zero()
                discarded.append(blank)
                slots.append(blank)
        exhausted = object()
        if next(public, exhausted) is not exhausted or len(set(slots)) != len(slots):
            raise ValueError("specialization needs distinct complete source fields")
        if source.ambient * columns > machine.n:
            raise ValueError("missing source ambient")
        requests = iter(source.run(machine, slots, columns))
        for rank in source.paid:
            owner, axes = next(requests)
            if len(axes) != rank * columns or len(set(axes)) != len(axes):
                raise ValueError("invalid paid product boundary")
            size = cutoff * columns
            for start in range(0, len(axes), size):
                yield owner, axes[start:start + size]
        if next(requests, exhausted) is not exhausted:
            raise ValueError("unaccounted paid position")
        for blank in discarded:
            machine.retire_zero(blank)

    return word, native
