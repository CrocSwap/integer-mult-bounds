#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact four-block census and literal decoder checks; standard library only.

Prepared for DLamdata with substantial OpenAI Codex assistance.
No predecessor executable code is imported.
"""
import argparse
from collections import Counter, deque
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
SEED = 41


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)


def edges(p):
    return [
        (u, v) for u, v in combinations(range(2 * p), 2) if u // 2 != v // 2
    ]


def graph_orbits(p):
    """BFS under sign flips and adjacent pair swaps: generators of C2 wr S_p."""
    graph = edges(p)
    index = {edge: i for i, edge in enumerate(graph)}
    permutations = []
    for j in range(p):
        perm = list(range(2 * p))
        perm[2 * j], perm[2 * j + 1] = perm[2 * j + 1], perm[2 * j]
        permutations.append(perm)
    for j in range(p - 1):
        perm = list(range(2 * p))
        for sign in range(2):
            a, b = 2 * j + sign, 2 * j + 2 + sign
            perm[a], perm[b] = perm[b], perm[a]
        permutations.append(perm)
    maps = [[index[tuple(sorted((perm[u], perm[v])))] for u, v in graph]
            for perm in permutations]
    unseen = set(combinations(range(len(graph)), 3))
    result = []
    while unseen:
        first = min(unseen)
        unseen.remove(first)
        queue, size = deque([first]), 0
        while queue:
            triple = queue.popleft()
            size += 1
            for mapping in maps:
                transformed = tuple(sorted(mapping[i] for i in triple))
                if transformed in unseen:
                    unseen.remove(transformed)
                    queue.append(transformed)
        targets = [graph[i] for i in first]
        result.append({'targets': targets, 'orbit_size': size})
    require(sum(r['orbit_size'] for r in result) == comb(len(graph), 3),
            'incomplete orbit coverage')
    return result


def four_partitions(n):
    """Every unlabeled partition into four nonempty blocks, restricted growth order."""
    colors = [0] * n

    def visit(i, largest):
        if i == n:
            if largest == 3:
                yield tuple(colors)
            return
        for color in range(min(3, largest + 1) + 1):
            colors[i] = color
            yield from visit(i + 1, max(largest, color))
    yield from visit(1, 0)


def inverse_rows(matrix):
    """Coefficients expressing each unit row as a sum of the three supplied rows."""
    answer = []
    for i in range(3):
        found = []
        for mask in range(8):
            row = 0
            for j in range(3):
                if mask >> j & 1:
                    row ^= matrix[j]
            if row == 1 << i:
                found.append(mask)
        require(len(found) == 1, 'singular target evaluation matrix')
        answer.append(found[0])
    return answer


def literal_decoders(p, targets, deleted, coefficient_vertices):
    """Check all surviving source columns, not merely the target 3x3 matrix."""
    graph = edges(p)
    require(len(set(targets)) == 3 and all(t in graph for t in targets), 'bad targets')
    require(not set(targets) & set(deleted), 'a target was deleted')
    surviving = [e for e in graph if e not in deleted]
    for i, vertices in enumerate(coefficient_vertices):
        for edge in surviving:
            require(sum(v in edge for v in vertices) % 2 == (edge == targets[i]),
                    'decoder fails a surviving source column')


def bridges_decode(p, targets, deleted):
    """Each target's endpoints must disconnect when that target is removed."""
    for target in targets:
        adjacency = [[] for _ in range(2 * p)]
        for u, v in edges(p):
            if (u, v) not in deleted and (u, v) != target:
                adjacency[u].append(v)
                adjacency[v].append(u)
        seen, queue = {target[0]}, deque([target[0]])
        while queue:
            for v in adjacency[queue.popleft()]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        if target[1] in seen:
            return False
    return True


def case(p):
    graph, n = edges(p), 2 * p
    records = graph_orbits(p)
    for record in records:
        record['acyclic'] = rank((1 << u) ^ (1 << v) for u, v in record['targets']) == 3
        record['minimum_deletions'] = None
        record['partition'] = None
    histogram, partition_count = Counter(), 0
    for colors in four_partitions(n):
        partition_count += 1
        sizes = Counter(colors)
        crossing = (n * n - sum(s * s for s in sizes.values())) // 2
        crossing -= sum(colors[2 * j] != colors[2 * j + 1] for j in range(p))
        histogram[crossing] += 1
        for record in records:
            old = record['minimum_deletions']
            if not record['acyclic'] or (old is not None and crossing - 3 >= old):
                continue
            target_columns = [(1 << colors[u]) ^ (1 << colors[v])
                              for u, v in record['targets']]
            if rank(target_columns) == 3:
                record['minimum_deletions'] = crossing - 3
                record['partition'] = colors
    # S(n,4), computed independently from the surjection inclusion-exclusion formula.
    expected_partitions = (4**n - 4 * 3**n + 6 * 2**n - 4) // 24
    require(partition_count == expected_partitions, 'partition coverage mismatch')
    restorations, scalar_columns = 0, 0
    for record in records:
        targets = record['targets']
        vertices = set(v for edge in targets for v in edge)
        exceptional = len(vertices) == 4 and len({v // 2 for v in vertices}) == 2
        expected = 6 * p - 12 + int(exceptional) if record['acyclic'] else None
        require(record['minimum_deletions'] == expected, 'classification fails')
        if not record['acyclic']:
            # The three target edges themselves form an undecodable cycle.
            require(not bridges_decode(p, targets, set(graph) - set(targets)), 'cycle control')
            record['classification'] = 'triangle: impossible'
            continue
        record['classification'] = 'two-pair path' if exceptional else 'other forest'
        # Construct a separate singleton-star witness, instead of using census colors.
        candidates = []
        for chosen in combinations(range(n), 3):
            matrix = [sum((v in edge) << i for i, edge in enumerate(targets)) for v in chosen]
            if rank(matrix) == 3:
                cost = 6 * p - 12 + 3 - len({v // 2 for v in chosen})
                candidates.append((cost, chosen, matrix))
        cost, chosen, matrix = min(candidates)
        require(cost == expected, 'singleton witness does not attain census minimum')
        colors = [3] * n
        for i, vertex in enumerate(chosen):
            colors[vertex] = i
        deleted = {e for e in graph if colors[e[0]] != colors[e[1]] and e not in targets}
        require(len(deleted) == expected, 'wrong deletion count')
        coefficients = [[v for j, v in enumerate(chosen) if mask >> j & 1]
                        for mask in inverse_rows(matrix)]
        literal_decoders(p, targets, deleted, coefficients)
        require(bridges_decode(p, targets, deleted), 'bridge witness failed')
        scalar_columns += 3 * (len(graph) - len(deleted))
        for edge in deleted:
            require(not bridges_decode(p, targets, deleted - {edge}), 'restoration falsely accepted')
            restorations += 1
        record.update(singleton_vertices=chosen, deleted=sorted(deleted),
                      decoder_vertices=coefficients)
    return {'p': p, 'ports': len(graph), 'target_triples': comb(len(graph), 3),
            'partition_count': partition_count,
            'crossing_histogram': {str(k): v for k, v in sorted(histogram.items())},
            'literal_source_columns': scalar_columns, 'restoration_controls': restorations,
            'orbits': records}


def rejection_controls(records):
    first = records[0]['orbits'][0]
    p, targets = records[0]['p'], first['targets']
    deleted = set(first['deleted'])
    controls = 0
    bad = [list(v) for v in first['decoder_vertices']]
    bad[0] = []
    for d, coefficients in [(deleted, bad), (deleted | {targets[0]}, first['decoder_vertices'])]:
        try:
            literal_decoders(p, targets, d, coefficients)
        except ValueError:
            controls += 1
        else:
            raise ValueError('invalid literal decoder accepted')
    try:
        inverse_rows([1, 2, 3])
    except ValueError:
        controls += 1
    else:
        raise ValueError('dependent targets accepted')
    # Granting the excluded empty star changes the triangle conclusion.
    triangle = [(0, 2), (0, 4), (2, 4)]
    for i, target in enumerate(triangle):
        opposite = next(v for v in (0, 2, 4) if v not in target)
        require(all((1 + int(opposite in edge)) % 2 == (j == i)
                    for j, edge in enumerate(triangle)), 'empty-star positive control')
    return {'rejections': controls, 'empty_star_triangle_escape': True}


def source_checks():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    for name, pin in sources['retained_reference_files'].items():
        content = (HERE / name).read_bytes()
        require(sha256(content).hexdigest() == pin['sha256'], 'source SHA256 mismatch: ' + name)
        from hashlib import sha1
        blob = b'blob ' + str(len(content)).encode() + b'\0' + content
        require(sha1(blob).hexdigest() == pin['git_blob_sha1'], 'source Git blob mismatch: ' + name)
    return sources['base_commit'], sources['predecessor_head']


def build_report():
    base, predecessor = source_checks()
    cases = [case(p) for p in (5, 6)]
    controls = rejection_controls(cases)
    illustration = random.Random(SEED).choice([i for i, r in enumerate(cases[0]['orbits'])
                                               if r['classification'] == 'other forest'])
    return {'schema': 'prescribed-star-triples-v1', 'base_commit': base,
            'predecessor_head': predecessor, 'assignment_seed': SEED,
            'illustrative_regular_orbit_p5': illustration,
            'theorem_scope': 'nonempty proper stars, k=2, p>=5; no new kappa',
            'cases': cases, 'controls': controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, default=HERE / 'CERTIFICATE.json')
    parser.add_argument('--output', type=Path, help='write verified receipt to a new file')
    args = parser.parse_args()
    if args.output:
        require(not args.output.exists(), 'refusing to overwrite output receipt')
    result = build_report()
    normalized = json.loads(json.dumps(result))
    require(normalized == json.loads(args.certificate.read_text()), 'certificate mismatch')
    if args.output:
        with args.output.open('x') as out:
            out.write(json.dumps(result, indent=2) + '\n')
    print('PASS_PRESCRIBED_STAR_TRIPLES: 44100 target triples; 37 orbits; '
          '645606 partitions; budgets 18/19 and 24/25; triangles impossible; no new kappa')
    print('Literal columns:', sum(c['literal_source_columns'] for c in result['cases']),
          'restoration rejections:', sum(c['restoration_controls'] for c in result['cases']),
          'other rejection controls:', result['controls']['rejections'])


if __name__ == '__main__':
    main()
