#!/usr/bin/env python3
"""Read-only finite premises for the full-group exterior 58-term cost floor.

F2 is used only for physical group spaces and tariffs. Rational decoder
coefficients are never reduced modulo two. Standard library only.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
CANDIDATE_SHA = 'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b'
ARCHIVE_SHA = 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
PAYLOAD_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def basis(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            column = vector.bit_length() - 1
            if column in pivots:
                vector ^= pivots[column]
            else:
                pivots[column] = vector
                break
    for column in sorted(pivots):
        for higher in pivots:
            if higher > column and ((pivots[higher] >> column) & 1):
                pivots[higher] ^= pivots[column]
    return tuple(pivots[column] for column in sorted(pivots))


def rho(left, right):
    rows = [sum(((x & y).bit_count() % 2) << j
                for j, y in enumerate(right)) for x in left]
    return len(basis(rows))


def contained(small, large):
    return basis(small + large) == large


def rejected(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('negative control accepted: ' + label)


def load_spaces():
    candidate = (PACKAGE / 'CANDIDATE.json').read_bytes().replace(b'\r\n', b'\n')
    need(sha256(candidate).hexdigest() == CANDIDATE_SHA, 'candidate pin')
    groups = json.loads(candidate)['groups']
    archive = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
    need(sha256(archive.read_bytes()).hexdigest() == ARCHIVE_SHA, 'archive pin')
    with tarfile.open(archive) as stream:
        payload = stream.extractfile(MEMBER).read()
    need(sha256(payload).hexdigest() == PAYLOAD_SHA, 'payload pin')
    recipes = sorted(json.loads(payload)['recipes'], key=lambda row: row['port'])
    need([row['port'] for row in recipes] == list(range(112)), 'port order')
    labels = [row['q'] for row in recipes]
    need(sorted(port for group in groups for port in group) == list(range(112)),
         'complete group partition')
    raw_spaces = [tuple(labels[port] for port in group) for group in groups]
    need(len(groups) == 38 and len(groups[0]) == 1
         and all(len(group) == 3 for group in groups[1:]), 'one line and37 triads')
    need(all((x & y).bit_count() % 2 == (i == j)
             for group in raw_spaces for i, x in enumerate(group)
             for j, y in enumerate(group)), 'orthonormal physical groups')
    return [basis(group) for group in raw_spaces]


def check_closure(spaces, seeds):
    need(() in spaces and all(seed in spaces for seed in seeds), 'missing generator')
    need(all(basis(space + seed) in spaces for space in spaces for seed in seeds),
         'not closed under physical triad generators')


def check_large_coverage(spaces, coverage, paired, singleton):
    for space in spaces:
        if len(coverage[space]) >= 6:
            need(all(rho(component, space) >= 5 for component in paired),
                 'six affected pairs require paired tariff at least5')
            need(rho(singleton, space) >= 2,
                 'six affected pairs require J tariff at least2')


def reader_geometry(physical):
    paired = [basis(physical[2*i+1] + physical[2*i+2]) for i in range(18)]
    singleton = physical[37]
    need(all(len(space) == rho(space, space) == 6 for space in paired),
         'paired spaces are nondegenerate of rank6')
    seeds = physical[1:]
    spaces, pending = {()}, [()]
    while pending:
        space = pending.pop()
        for seed in seeds:
            larger = basis(space + seed)
            if larger not in spaces:
                spaces.add(larger)
                pending.append(larger)
    check_closure(spaces, seeds)
    need(len(spaces) == 1750, 'complete physical reader closure has1750 spaces')
    dimension_histogram = Counter(map(len, spaces))
    need(dict(dimension_histogram) == {0:1, 3:37, 4:2, 5:59, 6:599, 7:657, 8:394, 9:1},
         'exact reader-space dimension histogram')
    controls = [rejected(lambda: check_closure(spaces - {physical[1]}, seeds),
                         'missing physical triad generator')]
    generated = next(space for space in spaces if len(space) == 8)
    controls.append(rejected(lambda: check_closure(spaces - {generated}, seeds),
                             'missing generated eight-space'))

    # Every active reader must touch at least one full triad of each affected
    # pair. Containment in its physical span is necessary, not merely overlap.
    coverage = {space: tuple(i for i in range(18)
                            if contained(physical[2*i+1], space)
                            or contained(physical[2*i+2], space)) for space in spaces}
    check_large_coverage(spaces, coverage, paired, singleton)
    weak_coverage = {space: tuple(i for i in range(18)
                                 if len(basis(space + physical[2*i+1]))
                                 < len(space) + 3
                                 or len(basis(space + physical[2*i+2]))
                                 < len(space) + 3) for space in spaces}
    controls.append(rejected(lambda: check_large_coverage(
        spaces, weak_coverage, paired, singleton),
        'replacing whole-triad containment with nonzero intersection'))

    # OR across ALL reader spans compatible with the SAME affected set F.
    # Every absent F has an empty union: its appearance would require one of
    # the eligible readers enumerated here and would have been generated.
    allowed, eligible = {}, 0
    for space in spaces:
        covered = coverage[space]
        if len(covered) < 6:
            continue
        source_mask = sum(1 << i for i, component in enumerate(paired)
                          if rho(component, space) < 6)
        if not source_mask:
            continue
        eligible += 1
        for size in range(6, len(covered) + 1):
            for affected in combinations(covered, size):
                affected_mask = sum(1 << i for i in affected)
                allowed[affected_mask] = allowed.get(affected_mask, 0) | source_mask
    need(eligible == 121 and len(allowed) == 2318, 'eligible reader and affected-set census')
    need(max(mask.bit_count() for mask in allowed.values()) == 10,
         'uniform cheap-source union has at most10 paired components')
    histogram = Counter((affected.bit_count(), sources.bit_count())
                        for affected, sources in allowed.items())
    expected = {(6,1):308, (6,2):765, (6,3):243, (6,4):170, (6,5):28,
                (6,6):24, (6,7):7, (6,8):1, (6,9):2, (6,10):1,
                (7,1):103, (7,2):351, (7,3):85, (7,4):39, (7,5):3,
                (7,6):7, (7,7):1, (8,1):21, (8,2):108, (8,3):19,
                (8,4):4, (8,6):1, (9,1):2, (9,2):21, (9,3):2, (10,2):2}
    need(dict(histogram) == expected, 'exact affected-set/source-union histogram')
    table = [{'F': affected, 'L': sources} for affected, sources in sorted(allowed.items())]
    table_digest = sha256(json.dumps(table, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    need(table_digest == 'fdcf97070f3a70f994651dcfa81bd7d87757d266b6c1e7c6d969f31d5aed24ae',
         'exact affected-set union table agrees with independent certificate')
    worst = next(affected for affected, sources in allowed.items()
                 if sources.bit_count() == 10)
    return {'reader_spaces': len(spaces),
            'dimension_histogram': dict(sorted(dimension_histogram.items())),
            'eligible_reader_spans': eligible, 'nonempty_affected_set_unions': len(allowed),
            'maximum_cheap_source_pair_union': 10,
            'affected_set_union_table_sha256': table_digest,
            'affected_size_source_union_size_histogram': {
                str(key): value for key, value in sorted(histogram.items())},
            'worst_affected_pairs': [i+1 for i in range(18) if worst >> i & 1],
            'worst_source_pair_union': [i+1 for i in range(18) if allowed[worst] >> i & 1],
            'controls': controls}


def nonempty_subsets(vertices):
    vertices = tuple(sorted(vertices))
    for mask in range(1, 1 << len(vertices)):
        yield frozenset(vertices[i] for i in range(len(vertices)) if mask >> i & 1)


def check_forest(neighbors):
    visited = set()
    def visit(vertex, parent):
        need(vertex not in visited, 'Schur graph contains a cycle')
        visited.add(vertex)
        for other in neighbors[vertex] - {vertex, parent}:
            visit(other, vertex)
    for vertex in neighbors:
        if vertex not in visited:
            visit(vertex, None)


def schur_geometry(physical):
    remainder = [0] + list(range(2, 37, 2))
    retained = list(range(1, 38, 2))
    odd_neighbors = {i: {j for j in retained if rho(physical[i], physical[j]) == 0}
                     for i in remainder}
    # Original K freedom OR a possible BA two-step path. No rank57 normal
    # form is used when determining this rank58 Schur support restriction.
    neighbors = {i: {j for j in remainder if i == j
                     or rho(physical[i], physical[j]) == 0
                     or odd_neighbors[i] & odd_neighbors[j]} for i in remainder}
    edges = sorted((i, j) for i in remainder for j in neighbors[i] if i < j)
    expected = [(0,2), (0,8), (0,10), (0,16), (0,20), (0,28),
                (4,24), (8,22), (12,30)]
    need(edges == expected, 'exact nine-edge Schur support forest')
    check_forest(neighbors)
    mutated = {i: set(values) for i, values in neighbors.items()}
    mutated[0].add(22)
    mutated[22].add(0)
    control = rejected(lambda: check_forest(mutated),
                       'granting an extra0/22 Schur edge creates a triangle')

    # Every nonempty rectangle has a column vertex v, so its entire row set
    # lies in N(v). Enumerating these row sets and every nonempty subset of
    # their common column neighbors is a complete, deduplicated census.
    left_sets = set()
    for vertex in remainder:
        left_sets.update(nonempty_subsets(neighbors[vertex]))
    rectangles = set()
    for left in left_sets:
        common = set.intersection(*(neighbors[vertex] for vertex in left))
        for right in nonempty_subsets(common):
            rectangles.add((left, right))
    classification, six_even = Counter(), []
    for left, right in rectangles:
        if len(left) >= 2 and len(right) >= 2:
            need(left == right and len(left) == 2, 'forest rectangle property')
        even_count = len(left - {0}) + len(right - {0})
        if 4 in left or 4 in right:
            need(left | right <= {4,24}, 'exceptional4/24 support localization')
            classification['exceptional4/24'] += 1
        elif left == {0} or right == {0}:
            need(even_count <= 6, 'residual-only six-neighbor limit')
            classification['residual-only'] += 1
            if even_count == 6:
                need((left - {0}) | (right - {0}) == {2,8,10,16,20,28},
                     'exact six-neighbor support')
                six_even.append((sorted(left), sorted(right)))
        else:
            need(even_count <= 4, 'ordinary compression loses at most4 coordinates')
            classification['ordinary'] += 1
    need(len(rectangles) == 314 and dict(classification) == {
        'exceptional4/24':8, 'ordinary':53, 'residual-only':253}, 'exact rectangle census')
    need(len(six_even) == 4, 'four oriented six-even-block rectangles')
    return {'edges': edges, 'nonempty_ordered_rectangles': len(rectangles),
            'classification': dict(sorted(classification.items())),
            'six_even_block_rectangles': sorted(six_even), 'controls': [control]}


def main():
    physical = load_spaces()
    reader = reader_geometry(physical)
    schur = schur_geometry(physical)
    need(7 * 52 - 67 == 297 and 6 * 58 - 34 - 4 * 4 == 298,
         'compression and large-affected-support invoices')
    need(297 * 9 > 2672, 'excludes the positive-saving allowance')
    result = {'candidate_lf_sha256': CANDIDATE_SHA, 'archive_sha256': ARCHIVE_SHA,
              'payload_sha256': PAYLOAD_SHA, 'reader_geometry': reader,
              'schur_geometry': schur, 'lower_bound': 297,
              'scope': 'At most58 nonzero rational scalar rank-one terms on the pinned full-group mask; no sharpness claim.',
              'symbolic_proof': 'EXTERIOR-58-PROOF.md',
              'predecessor_premises': 'RANK-TIGHT-PROOF.md: principal I57 and40-space acyclic tariff lemma',
              'exclusions': ['59 or more terms', 'changed mask or tariff',
                             'block-valued messages', 'native supplier or exponent claims']}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
