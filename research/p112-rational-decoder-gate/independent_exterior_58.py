#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact finite checks for the at-most-58-term exterior floor.

Subspaces are explicit sets of binary vectors; pairing ranks are calculated
through annihilator intersections. No primary/predecessor executable imports,
generated receipts, Git, third-party modules, or output-file writes are used.
The rational linear-algebra argument is in EXTERIOR-58-PROOF.md.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import io
import json
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CANDIDATE_SHA = 'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b'
ARCHIVE_SHA = 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
PAYLOAD_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rejects(fn, message):
    try:
        fn()
    except ValueError:
        return message
    raise ValueError('negative control accepted: ' + message)


def extend(space, vectors):
    result = set(space)
    for v in vectors:
        if v not in result:
            result.update([x ^ v for x in result])
    return frozenset(result)


def dimension(space):
    n = len(space)
    need(n > 0 and n & (n - 1) == 0, 'binary subspace cardinality')
    return n.bit_length() - 1


def perpendicular(space):
    # Independent directions are extracted by vector-set membership.
    generated = frozenset({0})
    directions = []
    for v in sorted(space):
        if v not in generated:
            directions.append(v)
            generated = extend(generated, [v])
    need(generated == space, 'annihilator input span')
    return frozenset(a for a in range(512)
                     if all((a & v).bit_count() % 2 == 0 for v in directions))


def closure_check(spaces, seeds):
    need(frozenset({0}) in spaces, 'missing zero space')
    need(all(extend({0}, g) in spaces for g in seeds), 'missing generator')
    need(all(extend(s, g) in spaces for s in spaces for g in seeds),
         'missing generated join')


def forest_check(neighbors):
    need(all(v in neighbors[v] for v in neighbors), 'missing loop')
    need(all(v in neighbors[u] for v in neighbors for u in neighbors[v]),
         'asymmetric support graph')
    visited = set()

    def visit(v, parent):
        need(v not in visited, 'support graph contains cycle')
        visited.add(v)
        for u in neighbors[v] - {v, parent}:
            visit(u, v)

    for v in neighbors:
        if v not in visited:
            visit(v, None)


def main():
    raw = (HERE / 'CANDIDATE.json').read_bytes().replace(b'\r\n', b'\n')
    need(sha256(raw).hexdigest() == CANDIDATE_SHA, 'candidate LF pin')
    groups = json.loads(raw)['groups']
    archive = (ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz').read_bytes()
    need(sha256(archive).hexdigest() == ARCHIVE_SHA, 'archive pin')
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as source:
        payload = source.extractfile(MEMBER).read()
    need(sha256(payload).hexdigest() == PAYLOAD_SHA, 'payload pin')
    recipes = sorted(json.loads(payload)['recipes'], key=lambda row: row['port'])
    need([r['port'] for r in recipes] == list(range(112)), 'port order')
    q = [r['q'] for r in recipes]
    need(len(groups) == 38 and len(groups[0]) == 1
         and all(len(g) == 3 for g in groups[1:]), 'group dimensions')
    need(sorted(i for g in groups for i in g) == list(range(112)), 'partition')
    seeds = [[q[i] for i in g] for g in groups]
    need(all((a & b).bit_count() % 2 == int(i == j)
             for g in seeds for i, a in enumerate(g) for j, b in enumerate(g)),
         'orthonormal group bases')
    E = [extend({0}, g) for g in seeds]
    H = [extend(E[2*i+1], seeds[2*i+2]) for i in range(18)]
    J = E[37]
    need(all(dimension(h) == 6 and h & perpendicular(h) == {0} for h in H),
         'paired six-spaces')

    empty = frozenset({0})
    spaces, pending = {empty}, [empty]
    while pending:
        a = pending.pop()
        for g in seeds[1:]:
            s = extend(a, g)
            if s not in spaces:
                spaces.add(s)
                pending.append(s)
    closure_check(spaces, seeds[1:])
    need(len(spaces) == 1750, 'physical reader closure size')
    expected_dimensions = {0: 1, 3: 37, 4: 2, 5: 59, 6: 599, 7: 657, 8: 394, 9: 1}
    need(Counter(map(dimension, spaces)) == expected_dimensions,
         'reader dimension census')
    controls = [rejects(lambda: closure_check(spaces - {E[1]}, seeds[1:]),
                        'missing physical generator rejected')]
    eight = next(s for s in spaces if dimension(s) == 8)
    controls.append(rejects(lambda: closure_check(spaces - {eight}, seeds[1:]),
                            'missing generated eight-space rejected'))

    allowed, eligible = {}, 0
    minimum_paired, minimum_J = 9, 9
    for T in spaces:
        covered = [i for i in range(18) if E[2*i+1] <= T or E[2*i+2] <= T]
        if len(covered) < 6:
            continue
        annihilator = perpendicular(T)
        ranks = [dimension(h) - dimension(h & annihilator) for h in H]
        jrank = dimension(J) - dimension(J & annihilator)
        minimum_paired = min(minimum_paired, min(ranks))
        minimum_J = min(minimum_J, jrank)
        need(min(ranks) >= 5 and jrank >= 2, 'large affected support tariff')
        cheap_sources = sum(1 << i for i, r in enumerate(ranks) if r < 6)
        if not cheap_sources:
            continue
        eligible += 1
        for n in range(6, len(covered) + 1):
            for subset in combinations(covered, n):
                f = sum(1 << i for i in subset)
                allowed[f] = allowed.get(f, 0) | cheap_sources
    need(eligible == 121 and len(allowed) == 2318, 'reader and affected-set census')
    maximum_union = max(mask.bit_count() for mask in allowed.values())
    need(maximum_union == 10, 'uniform cheap-source union')
    table = [{'F': f, 'L': allowed[f]} for f in sorted(allowed)]
    table_hash = sha256(json.dumps(table, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    def free(i, j):
        return all((a & b).bit_count() % 2 == 0 for a in seeds[i] for b in seeds[j])

    retained = list(range(1, 38, 2))
    outside = [0] + list(range(2, 37, 2))
    schur_edges = []
    neighbors = {i: {i} for i in outside}
    for n, i in enumerate(outside):
        for j in outside[n+1:]:
            if free(i, j) or any(free(i, k) and free(k, j) for k in retained):
                schur_edges.append([i, j])
                neighbors[i].add(j)
                neighbors[j].add(i)
    need(schur_edges == [[0, 2], [0, 8], [0, 10], [0, 16], [0, 20], [0, 28],
                         [4, 24], [8, 22], [12, 30]], 'exact Schur support graph')
    forest_check(neighbors)
    altered = {i: set(v) for i, v in neighbors.items()}
    altered[0].add(22)
    altered[22].add(0)
    controls.append(rejects(lambda: forest_check(altered),
                            'extra zero-to-22 edge creates rejected cycle'))

    # Any nonempty support rectangle has its row set within the closed
    # neighborhood of any one column. Enumerate all such row sets, then every
    # nonempty subset of their common columns: this covers all rectangles.
    rowsets = set()
    for adjacent in neighbors.values():
        adjacent = sorted(adjacent)
        for n in range(1, len(adjacent) + 1):
            rowsets.update(frozenset(c) for c in combinations(adjacent, n))
    rectangles, six_rectangles = Counter(), []
    for rows in rowsets:
        columns = set(outside)
        for i in rows:
            columns.intersection_update(neighbors[i])
        need(bool(columns), 'rectangle common neighbors')
        for n in range(1, len(columns) + 1):
            for subset in combinations(sorted(columns), n):
                cols = set(subset)
                if len(rows) >= 2 and len(cols) >= 2:
                    need(rows == cols and len(rows) == 2, 'looped forest rectangle rule')
                if 4 in rows or 4 in cols:
                    need(rows | cols <= {4, 24}, 'exceptional localization')
                    rectangles['exceptional4/24'] += 1
                elif rows == {0} or cols == {0}:
                    count = len(rows - {0}) + len(cols - {0})
                    need(count <= 6, 'residual six-neighbor bound')
                    rectangles['residual-only'] += 1
                    if count == 6:
                        need((rows | cols) - {0} == {2, 8, 10, 16, 20, 28}, 'six neighbors')
                        six_rectangles.append([sorted(rows), sorted(cols)])
                else:
                    need(len(rows - {0}) + len(cols - {0}) <= 4, 'ordinary compression bound')
                    rectangles['ordinary'] += 1
    need(rectangles == {'exceptional4/24': 8, 'residual-only': 253, 'ordinary': 53},
         'complete ordered rectangle census')
    need(len(six_rectangles) == 4, 'four six-neighbor rectangles')
    print(json.dumps(dict(candidate_lf_sha256=CANDIDATE_SHA, archive_sha256=ARCHIVE_SHA,
                          payload_sha256=PAYLOAD_SHA, reader_spaces=len(spaces),
                          dimension_histogram=expected_dimensions, eligible_readers=eligible,
                          affected_sets=len(allowed), maximum_cheap_source_union=maximum_union,
                          allowed_table_sha256=table_hash, minimum_paired_tariff=minimum_paired,
                          minimum_J_tariff=minimum_J, schur_edges=schur_edges,
                          support_rectangles=sum(rectangles.values()),
                          rectangle_classification=dict(rectangles),
                          six_neighbor_rectangles=sorted(six_rectangles), controls=controls,
                          scope='Independent finite premises for the fixed-mask at-most-58-term scalar floor; no native or exponent claim.'),
                     sort_keys=True))


if __name__ == '__main__':
    main()
