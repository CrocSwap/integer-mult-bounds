"""Independent arithmetic and permutation oracles; no predecessor imports.

Apache-2.0. @CubeJerry, with substantial OpenAI Codex assistance.
"""
from itertools import permutations


def raw_scalar(target, dirty, source_bit, K, G, rho):
    """Execute four displayed scalar updates with their actual moduli."""
    wide, compact, unit = 1 << (2*K), 1 << G, 1 << rho
    target = (target + 2*source_bit*dirty*unit) % wide
    dirty = (dirty + ((target // unit) % 2)) % compact
    target = (target + source_bit*(1-2*dirty)*unit) % wide
    dirty = (dirty - (((target // unit) % 2) ^ source_bit)) % compact
    return target, dirty


def inverse_table(forward):
    """Invert by complete image, not by reversing an operation word."""
    if sorted(forward) != list(range(len(forward))):
        raise ValueError("oracle requires a permutation")
    inverse = [None] * len(forward)
    for source, destination in enumerate(forward):
        inverse[destination] = source
    return inverse


def cycles(mapping):
    unseen, answer = set(range(len(mapping))), []
    while unseen:
        start, orbit = min(unseen), []
        x = start
        while x in unseen:
            unseen.remove(x)
            orbit.append(x)
            x = mapping[x]
        if x != start:
            raise ValueError("noncyclic component")
        answer.append(tuple(orbit))
    return answer


def partitions(n):
    """Restricted-growth strings: each set partition exactly once."""
    if n == 0:
        yield ()
        return

    def extend(labels, largest):
        if len(labels) == n:
            yield tuple(labels)
        else:
            for value in range(largest + 2):
                yield from extend(labels + [value], max(largest, value))

    yield from extend([0], 0)


def executable_local_repair(mapping, labels):
    """Try keyed reinsertion of unique tokens in each cell.

    No call to an edge-invariance predicate: unmatched keys fail execution.
    """
    output = [None] * len(mapping)
    groups = {}
    for i, label in enumerate(labels):
        groups.setdefault(label, []).append(i)
    for holes in groups.values():
        records = sorted((mapping[i], i) for i in holes)
        for hole, (destination, token) in zip(holes, records):
            if destination != hole:
                return None
            output[hole] = token
    return tuple(output)


def all_small_cases(maximum=5):
    for size in range(1, maximum + 1):
        for mapping in permutations(range(size)):
            for labels in partitions(size):
                yield mapping, labels
