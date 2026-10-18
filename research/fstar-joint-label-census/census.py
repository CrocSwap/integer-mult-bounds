"""Independent three-line joint-mask census. Standard library; no legacy imports.

An arc (t,s) constrains a(t).b(s) only when t precedes s in the kept order.
All permutations below are pullbacks: new line i is old line perm[i].
"""
from collections import Counter
from itertools import combinations_with_replacement, permutations, product
from math import factorial

PERMS = tuple(permutations(range(3)))
ARCS = tuple((t, s) for t in range(3) for s in range(3) if t != s)
ARC_INDEX = {edge: i for i, edge in enumerate(ARCS)}
TYPES = tuple((a, b) for a in range(8) for b in range(8) if a & b)


def dot(a, b):
    return (a & b).bit_count() % 2


def move_mask(mask, perm):
    return sum(1 << perm[j] for j in range(3) if mask & (1 << j))


TOTAL_MAPS = tuple(tuple(move_mask(x, p) for x in range(8)) for p in PERMS)
LINE_MAPS = tuple(tuple(sum(1 << i for i, (t, s) in enumerate(ARCS)
                           if z & (1 << ARC_INDEX[(p[t], p[s])]))
                       for z in range(64)) for p in PERMS)


def allowed_arcs(pairs):
    return sum(1 << i for i, (t, s) in enumerate(ARCS)
               if dot(pairs[t][0], pairs[s][1]) == 0)


def subsets(mask):
    value = mask
    while True:
        yield value
        if not value:
            return
        value = (value - 1) & mask


def relabel(pairs, z, line_perm, total_perm):
    """Definition-level joint S3 x S3 action; used by independent controls."""
    pp = tuple((move_mask(pairs[t][0], total_perm),
                move_mask(pairs[t][1], total_perm)) for t in line_perm)
    zz = sum(1 << i for i, (t, s) in enumerate(ARCS)
             if z & (1 << ARC_INDEX[(line_perm[t], line_perm[s])]))
    return pp, zz


def direct_canonical(pairs, z):
    return min(relabel(pairs, z, lp, tp) for lp in PERMS for tp in PERMS)


def pair_plan(pairs):
    """Minimize pair data first, retaining ALL attaining line permutations.

    A total permutation does not change Z. Therefore only line permutations
    attaining the smallest pair tuple need be tried for the secondary Z key.
    """
    best, attaining = None, set()
    for mapping in TOTAL_MAPS:
        moved = tuple((mapping[a], mapping[b]) for a, b in pairs)
        for i, p in enumerate(PERMS):
            key = tuple(moved[t] for t in p)
            if best is None or key < best:
                best, attaining = key, {i}
            elif key == best:
                attaining.add(i)
    return best, tuple(sorted(attaining))


def canonical_from_plan(plan, z):
    pairs, line_maps = plan
    return pairs, min(LINE_MAPS[i][z] for i in line_maps)


def enumerate_orbits():
    configurations = set()
    ordered_count = 0
    multiset_count = 0
    for pairs in combinations_with_replacement(TYPES, 3):
        multiset_count += 1
        available = allowed_arcs(pairs)
        multiplicity = factorial(3)
        for count in Counter(pairs).values():
            multiplicity //= factorial(count)
        ordered_count += multiplicity * (1 << available.bit_count())
        plan = pair_plan(pairs)
        configurations.update(canonical_from_plan(plan, z)
                              for z in subsets(available))
    return sorted(configurations), ordered_count, multiset_count


def burnside_count():
    """Separate orbit count: no canonicalization and no multiset reduction.

    For each group element, count fixed ordered pair data and invariant subsets
    of its allowed arcs. A subset is invariant exactly when it is a union of
    cycles of the induced permutation of the six arcs.
    """
    fixed = []
    for lp in PERMS:
        unseen = set(ARCS)
        cycles = []
        while unseen:
            e = next(iter(unseen))
            cycle = set()
            while e not in cycle:
                cycle.add(e)
                e = (lp[e[0]], lp[e[1]])
            unseen.difference_update(cycle)
            cycles.append(sum(1 << ARC_INDEX[e] for e in cycle))
        ways = [1 << sum(c & z == c for c in cycles) for z in range(64)]
        for tp in PERMS:
            n = 0
            for pairs in product(TYPES, repeat=3):
                if all((move_mask(pairs[lp[t]][0], tp),
                        move_mask(pairs[lp[t]][1], tp)) == pairs[t]
                       for t in range(3)):
                    n += ways[allowed_arcs(pairs)]
            fixed.append(n)
    if sum(fixed) % 36:
        raise ValueError("nonintegral Burnside orbit count")
    return sum(fixed) // 36, fixed


def submasks(mask):
    return tuple(x for x in range(8) if x & ~mask == 0)


SUBMASKS = tuple(submasks(mask) for mask in range(8))
OPTIONS = {(a, b): tuple((x, y) for x in SUBMASKS[a] for y in SUBMASKS[b]
                          if dot(x, y)) for a, b in TYPES}


def witness_valid(pairs, z, witness):
    if witness is None:
        return False
    a, b, order = witness
    if sorted(order) != [0, 1, 2] or len(a) != 3 or len(b) != 3:
        return False
    if any(a[t] & ~pairs[t][0] or b[t] & ~pairs[t][1]
           or dot(a[t], b[t]) != 1 for t in range(3)):
        return False
    pos = {t: i for i, t in enumerate(order)}
    return all(not (z & (1 << i)) or pos[t] > pos[s] or not dot(a[t], b[s])
               for i, (t, s) in enumerate(ARCS))


def singleton_witness(pairs, z):
    tied = [tuple(1 << j for j in range(3) if a & b & (1 << j))
            for a, b in pairs]
    for labels in product(*tied):
        # Conflict arcs have equal singleton labels. An order must put the
        # target of each such arc before its source.
        for order in PERMS:
            pos = {t: i for i, t in enumerate(order)}
            if all(not (z & (1 << i)) or labels[t] != labels[s]
                   or pos[t] > pos[s] for i, (t, s) in enumerate(ARCS)):
                return labels, labels, order
    return None


def exact_witness(pairs, z):
    """Search in chronological order. Once an a-label is chosen, b(t) only
    checks incoming constraints and never affects a later choice of b.
    Taking its first valid value is therefore exact, not a greedy relaxation.
    """
    a, b = [0] * 3, [0] * 3
    for order in PERMS:
        def visit(k):
            if k == 3:
                return tuple(a), tuple(b), order
            t = order[k]
            previous = [s for s in order[:k]
                        if z & (1 << ARC_INDEX[(s, t)])]
            for aa in SUBMASKS[pairs[t][0]]:
                for bb in SUBMASKS[pairs[t][1]]:
                    if dot(aa, bb) and all(not dot(a[s], bb) for s in previous):
                        a[t], b[t] = aa, bb
                        result = visit(k + 1)
                        if result is not None:
                            return result
                        # Other b(t) values have no effect on future tests.
                        break
            return None
        result = visit(0)
        if result is not None:
            return result
    return None


def brute_witness(pairs, z):
    """Definition-level oracle: all three local (a,b) pairs and all orders.
    This is deliberately separate from chronological search and singletons.
    """
    for labels in product(*(OPTIONS[p] for p in pairs)):
        a = tuple(p[0] for p in labels)
        b = tuple(p[1] for p in labels)
        for order in PERMS:
            if all(not (z & (1 << ARC_INDEX[(order[i], order[j])]))
                   or (a[order[i]] & b[order[j]]).bit_count() % 2 == 0
                   for i in range(3) for j in range(i + 1, 3)):
                return a, b, order
    return None
