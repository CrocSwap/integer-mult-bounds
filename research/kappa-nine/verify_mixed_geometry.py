"""Check graph hypotheses for the local block proof, without the generator.

The proof is in MIXED-GEOMETRY.md. This finite replay is not a formal proof
of the block theorem or of an integer multiplication theorem.
"""
from collections import deque
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import argparse
import json

BASE = 'abdc6a7002abdbcd9e21bfc5e1a795784deacfdf'
SOURCE_PATHS = (
    'research/kappa-nine/next-experiment-spec.json',
    'research/kappa-nine/LOCAL-ELIMINATION.md',
    'research/kappa-nine/LOCAL-RANK-TEST.md',
    'research/kappa-nine/MIXED-RANK-TEST.md',
    'research/kappa-nine/ONE-REGULAR-DIAGNOSTIC.md',
    'research/kappa-nine/ASSESSMENT.md',
    'research/kappa-nine/block_fano_obstruction.py',
    'research/kappa-nine/target_budget.py',
    'research/kappa-nine/local_support_elimination.py',
    'research/kappa-nine/local_rank_test.py',
    'research/kappa-nine/mixed_rank_obstruction.py',
    'research/kappa-nine/mixed-geometry-base-selection.json',
    'docs/research/community-batch952-review.md',
    'research/complex-t37-owners/PROOF.md',
)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def adjacent(t, u):
    return len(set(t) & set(u)) == 1


def key_edge(t, u):
    return tuple(sorted((tuple(t), tuple(u))))


def multiply(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)]
            for row in a]


def add(a, b):
    return [[x + y for x, y in zip(row, other)] for row, other in zip(a, b)]


def verify(data):
    require(data['base_commit'] == BASE, 'base pin')
    require(set(data['source_sha256']) == set(SOURCE_PATHS), 'source coverage')
    for path, digest in data['source_sha256'].items():
        require(sha256((ROOT / path).read_bytes()).hexdigest() == digest,
                'source hash: ' + path)
    spec = json.loads((ROOT / SOURCE_PATHS[0]).read_text())
    lines = [tuple(t) for t in spec['fixed_clique']]
    require(len(lines) == 7 and all(len(t) == 3 for t in lines), 'anchor shape')
    require(all(adjacent(t, u) for t, u in combinations(lines, 2)), 'anchor clique')
    labels = [t for t in combinations(range(9), 3)
              if len(set(t) & {7, 8}) == 1]
    support = {t: {k for k, line in enumerate(lines) if not adjacent(t, line)}
               for t in labels}
    require(len(labels) == 42 and all(len(v) == 3 for v in support.values()),
            'Y support census')
    colors = {}
    require(len(data['normal_form_blocks']) == 7, 'block coverage')
    for k, block in enumerate(data['normal_form_blocks']):
        require(block['block'] == k and tuple(block['line']) == lines[k], 'block identity')
        vertices = {t for t in labels if k in support[t]}
        edges = {key_edge(t, u) for t, u in combinations(sorted(vertices), 2)
                 if adjacent(t, u) and support[t] & support[u] == {k}}
        saved = [key_edge(t, u) for t, u in block['edges']]
        require(len(saved) == len(set(saved)) == 54 and set(saved) == edges,
                'local edge coverage')
        partitions = {}
        for part in block['partitions']:
            p, z = part['point'], part['outside']
            require((p, z) not in partitions and p in lines[k] and z in (7, 8),
                    'partition identity')
            s = tuple(part['singleton'])
            others = [tuple(t) for t in part['others']]
            require(s == tuple(sorted((set(lines[k]) - {p}) | {z})), 'singleton label')
            clique = [s] + others
            expected = {t for t in labels if z in t and
                        support[t] == {j for j, line in enumerate(lines) if p in line}}
            require(len(others) == 2 and set(clique) == expected, 'clique membership')
            require(all(adjacent(t, u) for t, u in combinations(clique, 2)), 'clique edges')
            require(len(set.union(*(support[t] for t in clique))) * 2 == 6,
                    'clique saturation')
            partitions[p, z] = (s, others)
        require(set(partitions) == set(product(lines[k], (7, 8))), 'partition coverage')
        used = set()
        for p, q in product(lines[k], repeat=2):
            if p == q:
                continue
            for z in (7, 8):
                s, rest = partitions[p, z]
                same, same_rest = partitions[q, z]
                opposite, opposite_rest = partitions[q, 15 - z]
                required = [(s, t) for t in same_rest] + [(s, opposite)]
                required += list(product(rest, opposite_rest))
                for t, u in required:
                    edge = key_edge(t, u)
                    require(edge in edges, 'normal-form zero product')
                    used.add(edge)
        require(used == edges, 'normal-form edge coverage')
        color = {min(vertices): 0}
        queue = deque(color)
        while queue:
            t = queue.popleft()
            for u in vertices:
                if key_edge(t, u) not in edges:
                    continue
                if u not in color:
                    color[u] = 1 - color[t]
                    queue.append(u)
                require(color[t] != color[u], 'bipartition')
        require(set(color) == vertices, 'connected local graph')
        for s, rest in partitions.values():
            require(all(color[t] != color[s] for t in rest), 'singleton color')
        colors[k] = color
    pairs = set()
    for witness in data['regular_pair_witnesses']:
        pair = tuple(witness['regular_blocks'])
        require(len(pair) == 2 and pair == tuple(sorted(set(pair))) and
                set(pair) <= set(range(7)) and pair not in pairs, 'regular pair')
        pairs.add(pair)
        p, k = witness['point'], witness['forced_block']
        require(set(lines[pair[0]]) & set(lines[pair[1]]) == {p}, 'common point')
        star = {j for j, line in enumerate(lines) if p in line}
        require(star - set(pair) == {k}, 'forced block')
        forced = [tuple(t) for t in witness['forced_labels']]
        require(forced == [tuple(sorted((set(lines[k]) - {p}) | {z}))
                           for z in (7, 8)], 'paired forced labels')
        require(len(witness['cliques']) == 2, 'forcing clique coverage')
        for z, t, raw in zip((7, 8), forced, witness['cliques']):
            clique = [tuple(u) for u in raw]
            expected = {u for u in labels if z in u and support[u] == star}
            require(len(clique) == 3 and set(clique) == expected, 'forcing clique')
            singles = []
            for regular in pair:
                color = colors[regular]
                singleton = [u for u in clique
                             if sum(color[u] == color[v] for v in clique) == 1]
                require(len(singleton) == 1 and singleton[0] != t, 'complement singleton')
                singles += singleton
            require(set(singles) == set(clique) - {t}, 'independent complement rows')
    require(pairs == set(combinations(range(7), 2)), 'regular pair coverage')
    remaining = [tuple(c) for c in data['remaining_exception_sets']]
    expected = [c for n in (6, 7) for c in combinations(range(7), n)]
    require(remaining == expected, 'remaining pattern census')
    control = {tuple(x['label']): x['block'] for x in data['coordinate_control']}
    require(len(data['coordinate_control']) == 42 and set(control) == set(labels),
            'coordinate control coverage')
    require(all(control[t] in support[t] for t in labels), 'coordinate control support')
    require(all(control[t] != control[u] for t, u in combinations(labels, 2)
                if adjacent(t, u)), 'coordinate control annihilation')
    stars = [{j for j, line in enumerate(lines) if p in line} for p in range(7)]
    old_survivors = []
    for size in range(8):
        for exception_tuple in combinations(range(7), size):
            exception = set(exception_tuple)
            hits = all(exception & star for star in stars)
            conflict = any(sum(exception & stars[p] == {k} for p in lines[k]) >= 2
                           for k in exception)
            if hits and not conflict:
                old_survivors.append(exception_tuple)
    new_counts = {size: sum(len(c) == size for c in old_survivors) for size in (4, 5)}
    require(new_counts == {4: 28, 5: 21} and len(old_survivors) == 57 and
            [c for c in old_survivors if len(c) >= 6] == expected, 'source survivor census')
    budget = verify_budget(data['budget_context'])
    return {'normal_form_blocks': 7, 'local_zero_edges': 378,
            'regular_pairs_excluded': 21, 'new_four_exception_exclusions': new_counts[4],
            'new_five_exception_exclusions': new_counts[5], 'remaining_exception_sets': 8,
            'coordinate_Y_control': '42 exact rank-two coordinate projectors; no X extension',
            'budget_context': budget}


def verify_budget(data):
    """Check the inherited relaxed profile and exact root intervals."""
    d, ell, n, r, roles = 15, 2, 560, 16, Q(5)
    m, volume = d * d, 2 + 2 * roles
    expected = {(d - ell) ** 2: Q(2), ell ** 2: Q(1),
                ell * (d - ell): Q(4),
                d * ell: 2 * roles + Q(2 * r * ell * (d - ell), n * d * ell),
                m - d * ell: 2 * roles}
    require(data['dimension'] == m and Q(data['volume_per_label']) == volume and
            Q(data['roles_per_label_per_axis']) == roles, 'relaxed profile parameters')
    moments = {}
    for check in data['moment_checks']:
        degree = check['degree']
        require(degree in (511, 99) and degree not in moments, 'moment degree')
        rows = check['roots']
        require(len(rows) == len(expected) and
                {row['child']: Q(row['count']) for row in rows} == expected,
                'relaxed profile charges')
        lower = upper = Q(0)
        for row in rows:
            child = row['child']
            lo, hi = map(Q, row['interval'])
            require(0 < lo <= hi and lo ** degree <= Q(m, child) <= hi ** degree,
                    'root enclosure')
            weight = expected[child] * child / (volume * m)
            lower += weight * lo
            upper += weight * hi
        moments[degree] = (lower, upper)
    require(set(moments) == {511, 99}, 'moment coverage')
    require(moments[511][1] < 1 and moments[99][0] > 1, 'relaxed moment conclusions')
    b, c = Q(data['complex_coarse']), Q(data['bit_coarse'])
    require(b == Q('0.001664727258740678855772') and
            c == Q('0.001733427039589844234749'), 'selected coarse endpoints')
    require(0 < b < c < Q(1, 511), 'current coarse comparison')
    selected = json.loads((HERE / 'mixed-geometry-base-selection.json').read_text())
    kappa = Q(selected['kappa'])
    cap = b / (1 + b)
    require(kappa <= cap < kappa + Q(1, 10 ** 18), 'unchanged-complex ceiling')
    return {'scope': 'Inherited optimistic profile, not an emitted construction',
            'moment_intervals': {str(Q(1, d)): list(map(str, v))
                                 for d, v in sorted(moments.items())},
            'bit_only_next_kappa_grid_point_excluded': True}


def local_controls(data):
    """Test all three local ranks in a rational basis that is not orthogonal."""
    identity = [[Q(1), Q(0)], [Q(0), Q(1)]]
    zero = [[Q(0), Q(0)], [Q(0), Q(0)]]
    change = [[Q(1), Q(1)], [Q(0), Q(1)]]
    inverse = [[Q(1), Q(-1)], [Q(0), Q(1)]]
    block = data['normal_form_blocks'][0]
    for rank in (0, 1, 2):
        c = multiply(multiply(change, [[Q(rank > 0), 0], [0, Q(rank > 1)]]), inverse)
        d = [[identity[i][j] - c[i][j] for j in range(2)] for i in range(2)]
        parts = {7: c, 8: d}
        factors = {}
        for partition in block['partitions']:
            z = partition['outside']
            factors[tuple(partition['singleton'])] = (parts[z], parts[z])
            for label in partition['others']:
                x = parts[15 - z]
                factors[tuple(label)] = (x, [[v / 2 for v in row] for row in x])
        for left, right in block['edges']:
            for t, u in ((tuple(left), tuple(right)), (tuple(right), tuple(left))):
                require(multiply(factors[t][1], factors[u][0]) == zero,
                        'local zero-product control')
        for partition in block['partitions']:
            total = zero
            for label in [partition['singleton']] + partition['others']:
                total = add(total, multiply(*factors[tuple(label)]))
            require(total == identity, 'local saturation control')
            require(multiply(*factors[tuple(partition['singleton'])]) == parts[partition['outside']],
                    'local decomposition control')
    return 3


def negative_controls(data):
    cases = []
    bad = deepcopy(data)
    bad['regular_pair_witnesses'].pop()
    cases.append(('regular pair coverage', bad))
    bad = deepcopy(data)
    bad['regular_pair_witnesses'][0]['forced_labels'][1] = bad['regular_pair_witnesses'][0]['forced_labels'][0]
    cases.append(('paired forced labels', bad))
    bad = deepcopy(data)
    bad['normal_form_blocks'][0]['edges'].pop()
    cases.append(('local edge coverage', bad))
    bad = deepcopy(data)
    part = bad['normal_form_blocks'][0]['partitions'][0]
    part['singleton'], part['others'][0] = part['others'][0], part['singleton']
    cases.append(('singleton label', bad))
    bad = deepcopy(data)
    bad['remaining_exception_sets'].append([0, 1, 2, 3, 4])
    cases.append(('remaining pattern census', bad))
    bad = deepcopy(data)
    bad['budget_context']['moment_checks'][0]['roots'][0]['interval'] = ['1', '1']
    cases.append(('root enclosure', bad))
    bad = deepcopy(data)
    bad['budget_context']['moment_checks'][0]['roots'][0]['count'] = '0'
    cases.append(('relaxed profile charges', bad))
    for reason, bad in cases:
        try:
            verify(bad)
        except ValueError as error:
            require(str(error) == reason, 'wrong rejection: ' + str(error))
        else:
            raise ValueError('accepted negative control: ' + reason)
    return len(cases)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('certificate', type=Path, nargs='?', default=HERE / 'mixed-geometry-certificate.json')
    args = parser.parse_args()
    data = json.loads(args.certificate.read_text())
    result = verify(data)
    result['local_rational_controls'] = local_controls(data)
    result['negative_controls_rejected'] = negative_controls(data)
    print(json.dumps(result, indent=2))
