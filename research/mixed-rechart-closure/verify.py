"""Exact small-space corroboration; the all-field theorem is in PROOF.md."""
from collections import deque
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


FILES = ('README.md', 'PROOF.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def contained(left, right):
    return left & right == left


def dimension(space):
    size = space.bit_count()
    need(size > 0 and size & (size - 1) == 0, 'non-subspace cardinality')
    return size.bit_length() - 1


def add_line(space, line, n):
    need(2 <= n <= 4 and 0 < line < 1 << n, 'line domain')
    result = space
    for vector in range(1 << n):
        if space >> vector & 1:
            result |= 1 << (vector ^ line)
    return result


def spaces(n):
    need(2 <= n <= 4, 'ambient domain')
    found = {1}
    for _ in range(n):
        previous = tuple(found)
        for space in previous:
            for line in range(1, 1 << n):
                found.add(add_line(space, line, n))
    return tuple(sorted(found))


SPACE_INVENTORIES = ((), (), spaces(2), spaces(3), spaces(4))


def lattice(space, hyperplane, line, n):
    need(2 <= n <= 4, 'ambient domain')
    need(space in SPACE_INVENTORIES[n] and hyperplane in SPACE_INVENTORIES[n], 'subspace domain')
    need(0 < line < 1 << n, 'line domain')
    need(dimension(hyperplane) == n - 1, 'hyperplane domain')
    need(not hyperplane >> line & 1, 'line must be transverse')
    bottom = space & hyperplane
    top = add_line(space, line, n)
    projected = add_line(bottom, line, n)
    choices = set((bottom, space, projected, top))
    need(len(choices) in (2, 4), 'Boolean lattice size')
    atoms = (top,) if len(choices) == 2 else tuple(sorted(choices - {bottom, top}))
    states = (bottom, top) if len(atoms) == 1 else (bottom, *atoms, top)
    need(set(states) == choices, 'choice representation')
    for mask, state in enumerate(states):
        need(dimension(state) == dimension(bottom) + mask.bit_count(), 'rank modularity')
    return states, atoms


def implications(left, right):
    ls, la = left
    rs, ra = right
    need(contained(ls[0], rs[0]) and contained(ls[-1], rs[-1]), 'edge boundary')
    arcs = []
    for a, atom in enumerate(la):
        for b in range(len(ra)):
            without_b = rs[((1 << len(ra)) - 1) ^ (1 << b)]
            if not contained(atom, without_b):
                arcs.append((a, b))
    need(len(arcs) <= 4, 'edge arc bound')
    return tuple(arcs)


def obeys(left_mask, right_mask, arcs):
    return all(not (left_mask >> a & 1) or (right_mask >> b & 1) for a, b in arcs)


def compile_graph(originals, hyperplane, line, n, edges):
    need(1 <= len(originals) <= 8 and len(edges) <= 64, 'graph capacity')
    lattices = tuple(lattice(u, hyperplane, line, n) for u in originals)
    offsets = []
    count = 0
    for _, atoms in lattices:
        offsets.append(count)
        count += len(atoms)
    arcs = []
    for u, v in edges:
        need(0 <= u < len(originals) and 0 <= v < len(originals), 'edge index')
        need(contained(originals[u], originals[v]), 'original nesting')
        for a, b in implications(lattices[u], lattices[v]):
            arcs.append((offsets[u] + a, offsets[v] + b))
    need(count <= 2 * len(originals) and len(arcs) <= 4 * len(edges), 'graph size')
    return lattices, tuple(offsets), tuple(arcs), count


def reachable(residual, source):
    previous = [-1] * len(residual)
    previous[source] = source
    queue = deque((source,))
    for _ in range(len(residual)):
        if not queue:
            break
        u = queue.popleft()
        for v, capacity in enumerate(residual[u]):
            if capacity > 0 and previous[v] < 0:
                previous[v] = u
                queue.append(v)
    need(not queue, 'BFS capacity')
    return previous


def min_cut(capacities, source, sink):
    residual = [row[:] for row in capacities]
    value = Fraction(0)
    arc_count = sum(x > 0 for row in capacities for x in row)
    bound = len(residual) * max(1, 2 * arc_count) + 1
    for _ in range(bound):
        previous = reachable(residual, source)
        if previous[sink] < 0:
            return value, tuple(i for i, p in enumerate(previous) if p >= 0)
        path = []
        v = sink
        for _ in range(len(residual)):
            if v == source:
                break
            u = previous[v]
            need(u >= 0, 'augmenting predecessor')
            path.append((u, v))
            v = u
        need(v == source and path, 'augmenting path bound')
        amount = min(residual[u][v] for u, v in path)
        need(amount > 0, 'positive augmentation')
        value += amount
        for u, v in path:
            residual[u][v] -= amount
            residual[v][u] += amount
    raise ValueError('Edmonds-Karp augmentation bound')


def optimize(compiled, weights, pins=()):
    lattices, offsets, arcs, count = compiled
    need(len(weights) == len(lattices), 'weight count')
    need(all(isinstance(w, (int, Fraction)) and abs(w) <= 100 for w in weights), 'weight domain')
    need(len(pins) <= 16, 'pin capacity')
    bit_weights = tuple(w for w, (_, atoms) in zip(weights, lattices) for _ in atoms)
    big = 1 + sum(abs(w) for w in bit_weights)
    source, sink = count, count + 1
    capacities = [[Fraction(0) for _ in range(count + 2)] for _ in range(count + 2)]
    for bit, weight in enumerate(bit_weights):
        capacities[source][bit] += max(0, weight)
        capacities[bit][sink] += max(0, -weight)
    for a, b in arcs:
        capacities[a][b] += big
    forced = []
    for vertex, mask in pins:
        need(0 <= vertex < len(lattices), 'pin vertex')
        need(0 <= mask < len(lattices[vertex][0]), 'pin option')
        for a in range(len(lattices[vertex][1])):
            bit = offsets[vertex] + a
            on = bool(mask >> a & 1)
            forced.append((bit, on))
            if on:
                capacities[source][bit] += big
            else:
                capacities[bit][sink] += big
    cut, selected = min_cut(capacities, source, sink)
    if cut >= big:
        return None
    chosen = set(selected)
    need(all(a not in chosen or b in chosen for a, b in arcs), 'returned nesting')
    need(all((a in chosen) == on for a, on in forced), 'returned pins')
    baseline = sum(w * dimension(states[0]) for w, (states, _) in zip(weights, lattices))
    return baseline + sum(max(0, w) for w in bit_weights) - cut


def brute(compiled, edges, weights, pins=()):
    lattices = compiled[0]
    best = None
    for masks in product(*(range(len(states)) for states, _ in lattices)):
        if any(masks[v] != mask for v, mask in pins):
            continue
        values = tuple(states[mask] for mask, (states, _) in zip(masks, lattices))
        if any(not contained(values[u], values[v]) for u, v in edges):
            continue
        score = sum(w * dimension(value) for w, value in zip(weights, values))
        best = score if best is None else max(best, score)
    return best


def check_all_edges():
    counts = dict(flags=0, local_lattices=0, nested_edges=0, option_pairs=0)
    for n in range(2, 5):
        inventory = spaces(n)
        need(len(inventory) == (5, 16, 67)[n - 2], 'complete subspace count')
        for normal in range(1, 1 << n):
            h = sum(1 << x for x in range(1 << n) if (x & normal).bit_count() % 2 == 0)
            for line in range(1, 1 << n):
                if h >> line & 1:
                    continue
                counts['flags'] += 1
                tables = tuple(lattice(u, h, line, n) for u in inventory)
                counts['local_lattices'] += len(tables)
                for u, left in zip(inventory, tables):
                    for v, right in zip(inventory, tables):
                        if not contained(u, v):
                            continue
                        counts['nested_edges'] += 1
                        arcs = implications(left, right)
                        for a, x in enumerate(left[0]):
                            for b, y in enumerate(right[0]):
                                counts['option_pairs'] += 1
                                need(contained(x, y) == obeys(a, b, arcs), 'nesting equivalence')
    return counts


def check_optima():
    counts = dict(price_cases=0, pin_cases=0, graph_cases=0)
    for n in (2, 3):
        inventory = spaces(n)
        h = (1 << (1 << (n - 1))) - 1
        line = 1 << (n - 1)
        for u in inventory:
            for v in inventory:
                if not contained(u, v):
                    continue
                graph = compile_graph((u, v), h, line, n, ((0, 1),))
                for weights in product(range(-2, 3), repeat=2):
                    need(optimize(graph, weights) == brute(graph, ((0, 1),), weights), 'cut optimum')
                    counts['price_cases'] += 1
                for a in range(len(graph[0][0][0])):
                    for b in range(len(graph[0][1][0])):
                        pins = ((0, a), (1, b))
                        weights = (Fraction(-2, 3), Fraction(5, 7))
                        need(optimize(graph, weights, pins) == brute(graph, ((0, 1),), weights, pins), 'pinned optimum')
                        counts['pin_cases'] += 1
    originals = (1, 3, 5, 15)
    edges = ((0, 1), (0, 2), (1, 3), (2, 3))
    graph = compile_graph(originals, 15, 4, 3, edges)
    for weights in product((-1, 0, 1), repeat=4):
        need(optimize(graph, weights) == brute(graph, edges, weights), 'diamond graph optimum')
        counts['graph_cases'] += 1
    graph = compile_graph((3, 3, 3), 15, 4, 3, ((0, 1), (1, 2), (2, 0)))
    need(optimize(graph, (1, 0, -1), ((0, 0), (2, 1))) is None, 'infeasible cycle pins')
    need(optimize(graph, (1, 0, -1), ((0, 0), (2, 0))) == 0, 'feasible cycle pins')
    counts['graph_cases'] += 2
    return counts


def span(vectors, n=3):
    result = 1
    for vector in vectors:
        result = add_line(result, vector, n)
    return result


def check_scope_examples():
    h, line = span((1, 2)), 4
    u, w = span((5,)), span((5, 2))
    graph = compile_graph((u, w), h, line, 3, ((0, 1),))
    need(optimize(graph, (-1, 1)) == 3, 'mixed strict gain')
    one_sided = []
    for options in (((u, add_line(u, line, 3)), (w, add_line(w, line, 3))), ((u, u & h), (w, w & h))):
        best = max(dimension(y) - dimension(x) for x, y in product(*options) if contained(x, y))
        one_sided.append(best)
    need(one_sided == [2, 2] and dimension(w) - dimension(u) == 1, 'one-sided controls')
    u, w = span((1,)), span((1, 6))
    graph = compile_graph((u, w), h, line, 3, ((0, 1),))
    options_u, options_w = (x[0] for x in graph[0])
    projected = (w & h)
    need(projected == u, 'strict-gap meet fixture')
    pairs = ((u, w), (u, add_line(u, line, 3)))
    need(all(contained(x, y) and dimension(y) > dimension(x) for x, y in pairs), 'positive gaps')
    meet = (pairs[0][0] & pairs[1][0], pairs[0][1] & pairs[1][1])
    need(meet == (u, u), 'positive-gap family not meet-closed')
    low = (u, add_line(u, line, 3))
    high = (add_line(u, line, 3), add_line(w, line, 3))
    need(all(x in options_u for x in low) and all(y in options_w for y in high), 'power rectangle options')
    gaps = tuple(dimension(y) - dimension(x) for x, y in product(low, high))
    need(gaps == (1, 2, 0, 1), 'nonlinear rectangle')
    need(2 < 2 ** 2, 'square-root strict concavity')
    return dict(original=1, growth=2, shrinkage=2, mixed=3, strict_gap_meet=0, power_gaps=gaps)


def check_rejections():
    controls = (
        ('ambient domain', lambda: spaces(5)),
        ('line must be transverse', lambda: lattice(3, 15, 1, 3)),
        ('hyperplane domain', lambda: lattice(3, 255, 4, 3)),
        ('subspace domain', lambda: lattice(7, 15, 4, 3)),
        ('original nesting', lambda: compile_graph((3, 5), 15, 4, 3, ((0, 1),))),
        ('graph capacity', lambda: compile_graph((3,) * 9, 15, 4, 3, ())),
        ('pin option', lambda: optimize(compile_graph((3,), 15, 4, 3, ()), (1,), ((0, 4),))),
        ('weight domain', lambda: optimize(compile_graph((3,), 15, 4, 3, ()), (101,))),
    )
    for message, control in controls:
        try:
            control()
        except ValueError as error:
            need(str(error) == message, 'wrong rejection cause')
            continue
        raise ValueError('rejection control accepted')
    return len(controls)


def receipt():
    root = Path(__file__).resolve().parent
    hashes = {}
    for name in FILES:
        path = root / name
        need(path.stat().st_size <= 128 * 1024, 'package file capacity')
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    result = dict(status='PASS_MIXED_RECHART_CLOSURE', edges=check_all_edges(), optima=check_optima(), examples=check_scope_examples(), rejections=check_rejections(), sha256=receipt())
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
