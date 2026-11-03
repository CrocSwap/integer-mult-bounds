"""Exact elementary mirror windows from interval endpoint events.

Window semantics: zxv PR4483 and Ryanson Jonathan PR4459, Apache-2.0.
The new implementation classifies each target/paid rank pair once.
"""

from collections import Counter
from fractions import Fraction

MAX_SUPPORT = 64
MAX_INTEGER = 10**12


def checked(histogram):
    if not isinstance(histogram, dict) or not 1 <= len(histogram) <= MAX_SUPPORT:
        raise ValueError("bounded nonempty histogram required")
    if any(type(k) is not int or type(v) is not int
           or not 1 <= k <= MAX_INTEGER or not 1 <= v <= MAX_INTEGER
           for k, v in histogram.items()):
        raise ValueError("positive bounded integer ranks and counts required")


def apply_events(active, delta):
    for rank, change in delta.items():
        value = active.get(rank, 0) + change
        if value < 0:
            raise ValueError("negative active multiplicity")
        if value:
            active[rank] = value
        else:
            active.pop(rank, None)


def mirror_windows(targets, paid, stats=None):
    """Return the original (left,right,exits,sources) cells, independently owned.

    A pair contributes on (1/max(k,r),1/min(k,r)]. Optional stats counts
    classifications and endpoint updates, not elapsed time or total work.
    """
    checked(targets)
    checked(paid)
    if stats is not None and not isinstance(stats, dict):
        raise ValueError("stats must be a dictionary or None")
    cuts = sorted({Fraction(0), *(Fraction(1, k) for k in targets),
                   *(Fraction(1, r) for r in paid)})
    position = {cut: i for i, cut in enumerate(cuts)}
    events = [(Counter(), Counter()) for _ in cuts]
    pairs = updates = 0
    for k, weight in targets.items():
        for r, count in paid.items():
            pairs += 1
            if k == r:
                continue
            side = 0 if r > k else 1
            start = position[Fraction(1, max(k, r))]
            stop = position[Fraction(1, min(k, r))]
            events[start][side][k*r] += weight*count
            events[stop][side][k*r] -= weight*count
            updates += 2
    exits, sources, cells = Counter(), Counter(), []
    for index, (left, right) in enumerate(zip(cuts, cuts[1:])):
        apply_events(exits, events[index][0])
        apply_events(sources, events[index][1])
        if exits:
            if not sources:
                raise ValueError("boundary mirror window without source funding")
            cells.append((left, right, exits.copy(), sources.copy()))
    apply_events(exits, events[-1][0])
    apply_events(sources, events[-1][1])
    if exits or sources:
        raise ValueError("unclosed mirror interval")
    if stats is not None:
        stats.update(pair_classifications=pairs, endpoint_updates=updates,
                     elementary_cells=len(cuts)-1, emitted_cells=len(cells))
    return cells
