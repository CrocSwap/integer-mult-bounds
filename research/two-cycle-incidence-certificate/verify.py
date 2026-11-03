#!/usr/bin/env python3
"""Check the complete incidence class and exact formal endpoint controls.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
JoyboyBrian supplied the released connected-incidence lemma and fixture.
"""
import argparse
from collections import Counter, deque
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
I2, Z2 = (1, 2), (0, 0)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate(root):
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((root/row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'Source mismatch: '+row['path'])


def identity(n):
    return tuple(1 << j for j in range(n))


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def mul(a, b):
    out = []
    for row in a:
        value = 0
        for j, other in enumerate(b):
            if row >> j & 1:
                value ^= other
        out.append(value)
    return tuple(out)


def gate(n, target, source):
    rows = list(identity(n))
    rows[target] ^= 1 << source
    return tuple(rows)


PROJECTORS = [p for p in product(range(4), repeat=2)
              if p not in (Z2, I2) and mul(p, p) == p]


def formal(word, n):
    state = {identity(n): I2}
    for label, p in word:
        out = {}
        for h, coefficient in state.items():
            for g, q in ((identity(n), add(I2, p)), (label, p)):
                key = mul(h, g)
                out[key] = add(out.get(key, Z2), mul(coefficient, q))
        state = {k: v for k, v in out.items() if v != Z2}
    return state


def permutation(matrix):
    return tuple(sum(((row & x).bit_count() & 1) << j
                     for j, row in enumerate(matrix))
                 for x in range(1 << len(matrix)))


def independent_formal(word, n):
    """Use complete permutations as group labels and dense scalar matrices."""
    zero, one = (0, 0, 0, 0), (1, 0, 0, 1)
    ident = tuple(range(1 << n))
    state = {ident: one}
    def dense(p):
        return tuple(p[i] >> j & 1 for i in range(2) for j in range(2))
    def dot(a, b):
        return tuple(sum(a[2*i+k]*b[2*k+j] for k in range(2)) % 2
                     for i in range(2) for j in range(2))
    for label, projector in word:
        g, p = permutation(label), dense(projector)
        q = tuple(x ^ y for x, y in zip(one, p))
        out = {}
        for h, a in state.items():
            for k, b in ((h, q), (tuple(h[g[x]] for x in range(len(g))), p)):
                old, value = out.get(k, zero), dot(a, b)
                out[k] = tuple(x ^ y for x, y in zip(old, value))
        state = {k: v for k, v in out.items() if v != zero}
    return state


def compare_engines(word, n):
    primary = formal(word, n)
    converted = {permutation(k): tuple(v[i] >> j & 1 for i in range(2) for j in range(2))
                 for k, v in primary.items()}
    need(converted == independent_formal(word, n), 'Independent full formal coefficients')
    return primary


def ordinary_bfs():
    ident = identity(3)
    generators = [(i, j) for i in range(3) for j in range(3) if i != j]
    paths, queue = {ident: []}, deque([ident])
    while queue:
        h = queue.popleft()
        for i, j in generators:
            nxt = mul(h, gate(3, i, j))
            if nxt not in paths:
                paths[nxt] = paths[h]+[(i, j)]
                queue.append(nxt)
    need(len(paths) == 168, 'Complete GL3')
    cycles = ((2, 4, 1), (4, 1, 2))
    need(all(len(paths[c]) == 6 for c in cycles), 'Both ordinary cycle minima')
    # A rank enumeration gives a separate inventory of the group.
    invertible = set()
    for rows in product(range(8), repeat=3):
        if len({0, rows[0], rows[1], rows[2], rows[0]^rows[1],
                rows[0]^rows[2], rows[1]^rows[2], rows[0]^rows[1]^rows[2]}) == 8:
            invertible.add(rows)
    need(invertible == set(paths), 'Independent complete group inventory')
    return paths, cycles


def edges(labels):
    need(len(labels) == 10 and all(i != j for i, j in labels), 'Ten loop-free calls')
    result = []
    for side in (0, 1):
        for coordinate in range(5):
            positions = [j for j, pair in enumerate(labels) if pair[side] == coordinate]
            need(len(positions) == 2, 'Two reads and writes per coordinate')
            result.append((*positions, int(coordinate < 3)))
    return result


def graph_check(relations):
    adjacent = [[] for _ in range(10)]
    for x, y, parity in relations:
        adjacent[x].append((y, parity))
        adjacent[y].append((x, parity))
    need(all(len(row) == 2 for row in adjacent), 'Alternating degree two')
    colors, components, ok = {}, 0, True
    for root in range(10):
        if root in colors:
            continue
        components += 1
        colors[root] = 0
        queue = [root]
        while queue:
            x = queue.pop()
            for y, parity in adjacent[x]:
                value = colors[x] ^ parity
                if y in colors:
                    ok &= colors[y] == value
                else:
                    colors[y] = value
                    queue.append(y)
    return ok, components, [colors[x] for x in range(10)]


def linear_check(relations):
    pivots, ok = {}, True
    for x, y, parity in relations:
        row = (1 << x) ^ (1 << y) ^ (parity << 10)
        for bit in range(10):
            if not row >> bit & 1:
                continue
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
        else:
            if row:
                ok = False
    return ok, 10-len(pivots)


def assignments():
    remaining = [2]*5
    values = []
    def walk():
        if len(values) == 10:
            yield tuple(values)
            return
        target = len(values)//2
        for source in range(5):
            if source != target and remaining[source]:
                remaining[source] -= 1
                values.append(source)
                yield from walk()
                values.pop()
                remaining[source] += 1
    yield from walk()


def incidence_census():
    histogram, total, digest = Counter(), 0, sha256()
    for sources in assignments():
        labels = [(j//2, source) for j, source in enumerate(sources)]
        relations = edges(labels)
        ok, components, _ = graph_check(relations)
        need((ok, components) == linear_check(relations), 'Graph and GF2 elimination')
        histogram[(ok, components)] += 1
        digest.update(bytes(sources))
        total += 1
    # Independent coefficient DP counts the loop-free reader assignments.
    counts = {(0, 0, 0, 0, 0): 1}
    for position in range(10):
        nxt = Counter()
        for state, multiplicity in counts.items():
            for source in range(5):
                if source != position//2 and state[source] < 2:
                    changed = list(state)
                    changed[source] += 1
                    nxt[tuple(changed)] += multiplicity
        counts = nxt
    need(counts == {(2, 2, 2, 2, 2): total}, 'Independent assignment count')
    parity_rejections = sum(v for (ok, _), v in histogram.items() if not ok)
    connected_rejections = histogram[(True, 1)]
    survivors = sum(v for (ok, count), v in histogram.items() if ok and count > 1)
    noncommuting = sum(v*(6**count-3*2**count)
                      for (ok, count), v in histogram.items() if ok)
    need(total == parity_rejections+connected_rejections+survivors, 'Complete partition')
    return dict(assignments=total, assignment_sha256=digest.hexdigest(),
                parity_rejections=parity_rejections, connected_rejections=connected_rejections,
                unresolved_incidence_assignments=survivors,
                unresolved_noncommuting_projector_assignments=noncommuting,
                histogram=[dict(consistent=k[0], components=k[1], count=v)
                           for k, v in sorted(histogram.items())])


def projector_checks():
    need(len(PROJECTORS) == 6, 'All binary rank-one projectors')
    pairs = 0
    for p, q in product(PROJECTORS, repeat=2):
        commute = mul(p, q) == mul(q, p)
        need(commute == (p == q or add(p, q) == I2), 'Common complementary pair')
        pairs += int(commute)
    counts = []
    for components in range(1, 6):
        commuting = sum(all(mul(p, q) == mul(q, p) for p in choices for q in choices)
                        for choices in product(PROJECTORS, repeat=components))
        need(commuting == 3*2**components, 'Exact commuting component assignments')
        counts.append([components, 6**components, commuting, 6**components-commuting])
    return dict(commuting_pairs=pairs, component_assignments=counts)


def formal_checks(paths, cycles):
    positive = omitted = separated = 0
    rng = random.Random(60906012)
    for n in (3, 4, 5):
        for c in cycles:
            route = paths[c]
            for p in PROJECTORS:
                q = add(I2, p)
                word = [(gate(n, i, j), r) for r in (p, q) for i, j in route]
                target = {tuple(c)+identity(n)[3:]: I2}
                need(compare_engines(word, n) == target, 'Sharp twelve-call attainer')
                positive += 1
                for j in range(12):
                    need(formal(word[:j]+word[j+1:], n) != target, 'Deleted attaining call')
                    omitted += 1
                for length in (0, 1, 5, 10, 11, 12):
                    generated = []
                    lane = {p: identity(n), q: identity(n)}
                    for _ in range(length):
                        i, j = rng.sample(range(n), 2)
                        r = rng.choice((p, q))
                        g = gate(n, i, j)
                        lane[r] = mul(lane[r], g)
                        generated.append((g, r))
                    expected = {}
                    for r, label in lane.items():
                        expected[label] = add(expected.get(label, Z2), r)
                    expected = {k: v for k, v in expected.items() if v != Z2}
                    need(compare_engines(generated, n) == expected, 'Formal lane decomposition')
                    separated += 1
    labels = [(i, (i+1) % 5) for i in range(5)]+[(i, (i+2) % 5) for i in range(5)]
    relations = edges(labels)
    ok, components, colors = graph_check(relations)
    need(ok and components == 1 and Counter(colors) == {0: 5, 1: 5},
         'Published connected fixture')
    connected_colors = list(colors)
    target = {tuple(cycles[0])+identity(5)[3:]: I2}
    connected = []
    for p in PROJECTORS:
        word = [(gate(5, i, j), p if color == 0 else add(I2, p))
                for (i, j), color in zip(labels, colors)]
        result = compare_engines(word, 5)
        need(result != target, 'Pair constraints are insufficient for endpoint')
        connected.append(len(result))
    bad = list(relations)
    x, y, parity = bad[0]
    bad[0] = (x, y, 1-parity)
    need(not graph_check(bad)[0] and not linear_check(bad)[0], 'Wrong edge parity')
    disconnected = [(i, (i+1) % 3) for i in range(3)]+[(3, 4), (4, 3)]
    disconnected = [pair for pair in disconnected for _ in range(2)]
    ok, components, colors = graph_check(edges(disconnected))
    need(ok and components == 5, 'Disconnected cases survive the graph filter')
    p, q = next((p, q) for p, q in product(PROJECTORS, repeat=2) if mul(p, q) != mul(q, p))
    need(formal([(gate(3, 0, 1), p), (gate(3, 1, 2), q)], 3)
         != formal([(gate(3, 1, 2), q), (gate(3, 0, 1), p)], 3),
         'Do not commute noncommuting calls')
    # The selected middle label must be conjugated, not only retained.
    p = PROJECTORS[0]
    g, h = gate(3, 2, 1), gate(3, 0, 2)
    relabeled = compare_engines([(g, p), (h, p), (g, p)], 3)
    need(relabeled == {identity(3): add(I2, p), mul(mul(g, h), g): p}
         and relabeled != {identity(3): add(I2, p), h: p}, 'Middle label relabeling')
    # A natural matrix image can vanish while four formal labels remain.
    g, h = gate(4, 0, 1), gate(4, 2, 3)
    labels = (identity(4), g, h, mul(g, h))
    need(len(set(labels)) == 4 and add(add(labels[0], labels[1]),
         add(labels[2], labels[3])) == (0, 0, 0, 0), 'Unfaithful natural quotient control')
    return dict(attainers=positive, omitted_attaining_calls=omitted,
                lane_decompositions=separated, connected_fixture_colors=connected_colors,
                connected_formal_supports=connected, parity_control=True,
                disconnected_components=components, noncommuting_control=True,
                middle_relabel_control=True, natural_quotient_control=True)


def source_controls():
    rows = [r for r in json.loads((HERE/'SOURCES.json').read_text())['files'] if r['usage'] == 'input']
    with tempfile.TemporaryDirectory(prefix='incidence-source-') as folder:
        root = Path(folder)
        for row in rows:
            path = root/row['path']
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT/row['path']).read_bytes())
        authenticate(root)
        for row in rows:
            path = root/row['path']
            original = path.read_bytes()
            path.write_bytes(original+b'\nchanged\n')
            try:
                authenticate(root)
            except ValueError as error:
                need(str(error) == 'Source mismatch: '+row['path'], 'Source rejection')
            else:
                raise ValueError('Changed predecessor accepted')
            path.write_bytes(original)
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    authenticate(ROOT)
    paths, cycles = ordinary_bfs()
    result = dict(schema_version=1,
                  ordinary_bfs=dict(states=len(paths),
                                    distance_histogram=dict(sorted(Counter(map(len, paths.values())).items())),
                                    cycle_paths=[paths[c] for c in cycles]),
                  incidence=incidence_census(), projectors=projector_checks(),
                  formal=formal_checks(paths, cycles), source_mutation_controls=source_controls())
    result = json.loads(json.dumps(result))
    if args.output:
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        need(result == json.loads((HERE/'RESULT.json').read_text()), 'Stored receipt mismatch')
    print('PASS_TWO_CYCLE_INCIDENCE', result['incidence']['assignments'],
          'incidence assignments;', result['formal']['attainers'], 'formal attainers;',
          result['formal']['omitted_attaining_calls'], 'deletion controls')


if __name__ == '__main__':
    main()
