"""Necessary nonrectangular call/width cuts. ywz65 / OpenAI Codex; Apache-2.0."""
from itertools import product


def need(ok, message):
    if not ok:
        raise ValueError(message)


def normalize_cells(cells, widths, calls):
    need(type(cells) is list, 'cells list')
    out = []
    for cell in cells:
        need(type(cell) is list and len(cell) == 2, 'cell pair')
        t, w = cell
        need(type(t) is int and type(w) is int and t in calls and w in widths, 'cell coordinate')
        need((t,w) not in out, 'duplicate cell')
        out.append((t,w))
    return tuple(sorted(out))


def coefficient(pattern, widths, cells):
    """Upper bound from a width subset and its selected call neighborhood.

    Inputs are validated by inspect(). Calls not selected by cells never enter
    the neighborhood. No integrality/realizability conclusion is made here.
    """
    best = None
    for mask in range(1 << len(widths)):
        chosen = [w for i,w in enumerate(widths) if mask >> i & 1]
        neighbors = {t for t,w in cells if w in chosen}
        value = sum(n for i,n in enumerate(pattern) if not (mask >> i & 1)) + len(neighbors)
        if best is None or value < best[0]:
            best = value, chosen, sorted(neighbors)
    return best


def all_patterns(widths, capacity, call_count, bin_count):
    return [p for p in product(*(range(capacity//w+1) for w in widths))
            if sum(p) <= call_count and max(p,default=0) <= bin_count
            and sum(n*w for n,w in zip(p,widths)) <= capacity]


def inspect(patterns, flows, widths, capacity, bin_count, cells, validate):
    validate(patterns, flows, widths, capacity, bin_count)
    z = normalize_cells(cells, widths, flows)
    universe = all_patterns(widths, capacity, len(flows), bin_count)
    need(set(patterns) <= set(universe), 'pattern not in source universe')
    coefficients = {p:coefficient(p,widths,z) for p in universe}
    lhs = sum(flows[t][widths.index(w)] for t,w in z)
    rhs = sum(n*coefficients[p][0] for p,n in patterns.items())
    return dict(cells=[list(c) for c in z],lhs=lhs,rhs=rhs,deficit=max(0,lhs-rhs),
                violated=lhs>rhs,
                pattern_coefficients=[dict(pattern=list(p),coefficient=v[0],cover_widths=v[1],cover_calls=v[2])
                                      for p,v in coefficients.items()],
                scope='One supplied-cell necessary inequality; no complete separation or realization certificate')
