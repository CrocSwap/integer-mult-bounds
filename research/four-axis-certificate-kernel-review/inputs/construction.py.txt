"""A finite sum-preserving correction for the real Walsh-16 quotient.

Produced by Nick Petalas. Apache-2.0.
"""
from itertools import combinations, product

SIZE = 16
WALSH = tuple(tuple(1 if (r & s).bit_count() % 2 == 0 else -1
                    for s in range(SIZE)) for r in range(SIZE))
WEIGHTS = (tuple((1, 0, -1, 0)[j.bit_count() % 4] for j in range(SIZE)),
           tuple((0, -1, 0, 1)[j.bit_count() % 4] for j in range(SIZE)))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def walsh(values):
    need(len(values) == SIZE, "Sixteen real coordinates")
    return tuple(sum(a * b for a, b in zip(row, values)) for row in WALSH)


def quotient_keys():
    """Generate the entire column span modulo four, not sampled inputs."""
    keys = {(0,) * SIZE}
    for column in zip(*WALSH):
        keys = {tuple((a + t * b) % 4 for a, b in zip(key, column))
                for key in keys for t in range(4)}
        need(len(keys) <= 64, "Walsh quotient capacity")
    need(len(keys) == 64, "Complete Walsh quotient")
    return tuple(sorted(keys))


def corrections(key):
    """A sufficient candidate subset; no exhaustive closest-vector claim."""
    base = tuple((0, -1, 2, 1)[a] for a in key)
    if key[0] % 2:
        for size in range(7):
            for places in combinations(range(SIZE), size):
                value = list(base)
                for j in places:
                    value[j] = -3 * value[j]
                yield tuple(value)
    else:
        half = tuple(j for j, value in enumerate(key) if value == 2)
        for signs in product((-1, 1), repeat=len(half)):
            value = list(base)
            for j, sign in zip(half, signs):
                value[j] = 2 * sign
            yield tuple(value)


def correction_graph(keys):
    indices = {key: j for j, key in enumerate(keys)}
    graph = []
    for key in keys:
        edges = {}
        for value in corrections(key):
            if any(sum(a * b for a, b in zip(weight, value)) for weight in WEIGHTS):
                continue
            image = walsh(value)
            need(all(v % 4 == 0 for v in image), "Integral inverse offset")
            target = indices[tuple((v // 4) % 4 for v in image)]
            old = edges.get(target)
            if old is None or sum(v * v for v in value) < sum(v * v for v in old):
                edges[target] = value
        graph.append(edges)
    return tuple(graph)


def augment(source, graph, matched):
    """Breadth-first augmenting path, at most 64 sources and 4096 edges."""
    queue = [source]
    visited = {source}
    parent = {}
    for position in range(64):
        if position == len(queue):
            return False
        current = queue[position]
        for target in sorted(graph[current]):
            if target in parent:
                continue
            parent[target] = current
            previous = matched.get(target)
            if previous is not None:
                if previous not in visited:
                    visited.add(previous)
                    queue.append(previous)
                continue
            for _ in range(64):
                current = parent[target]
                old_target = next((t for t, s in matched.items() if s == current), None)
                matched[target] = current
                if old_target is None:
                    return True
                target = old_target
            raise ValueError("Augmenting path exceeds quotient capacity")
    return False


def build_tables():
    keys = quotient_keys()
    graph = correction_graph(keys)
    matched = {}
    for source in sorted(range(64), key=lambda s: (len(graph[s]), s)):
        need(augment(source, graph, matched), "Complete correction matching")
    need(len(matched) == 64 and len(set(matched.values())) == 64,
         "Bijective quotient matching")
    forward, backward = {}, {}
    for target, source in sorted(matched.items()):
        value = graph[source][target]
        forward[keys[source]] = value
        backward[keys[target]] = tuple(-v // 4 for v in walsh(value))
    return forward, backward
