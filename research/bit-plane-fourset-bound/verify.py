#!/usr/bin/env python3
"""Complete four-port, ten-term cost relaxation; no predecessor code imports.

Prepared for commdata2338, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('fourset_geometry', HERE / 'geometry.py')
geo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geo)
need = geo.need
TYPES = ((0, 0), (1, 0), (0, 1))
DUAL_PAIRS = ((96, 18), (17, 119), (11, 38), (103, 63), (12, 87),
              (94, 49), (50, 95), (86, 90), (2, 73))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def authenticate(data, pin):
    need(hashlib.sha256(data).hexdigest() == pin['sha256'], 'source SHA256 mismatch')
    blob = b'blob ' + str(len(data)).encode() + b'\0' + data
    need(hashlib.sha1(blob).hexdigest() == pin['git_blob'], 'source Git blob mismatch')


def check_sources():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage'] == 'input':
            authenticate((geo.ROOT / row['path']).read_bytes(), row)
    for row in pins['predecessor_files']:
        authenticate((HERE / row['local_path']).read_bytes(), row)
    return pins


def pair_graph(indices, gram, pairing):
    """Vertices and edges are the necessary pair conditions in tenneed.py."""
    pairs = [(x, y) for x in indices for y in indices if x != y and gram[x][y] == 0]
    vertices = [(v, w, x, y) for v, w in TYPES for x, y in pairs]
    adjacent = [0] * len(vertices)
    for i, (v, w, x, y) in enumerate(vertices):
        for j in range(i):
            vv, ww, xx, yy = vertices[j]
            if (x != xx and y != yy and pairing[x][yy] == (vv & w)
                    and pairing[xx][y] == (v & ww)):
                adjacent[i] |= 1 << j
                adjacent[j] |= 1 << i
    return vertices, adjacent


def clique_at_least(adjacent, target, stats=None):
    """Exhaustive branching with proper-coloring upper bounds; no cutoff.

    Each color class is an independent set. Reverse removal means colors[i]
    bounds the clique size of the remaining prefix at each branch.
    """
    if stats is None:
        stats = Counter()

    def search(possible, chosen):
        stats['nodes'] += 1
        if len(chosen) == target:
            return chosen
        if possible.bit_count() < target - len(chosen):
            stats['cardinality_prunes'] += 1
            return None
        order, colors = [], []
        remaining, color = possible, 0
        while remaining:
            color += 1
            available = remaining
            while available:
                bit = available & -available
                vertex = bit.bit_length() - 1
                order.append(vertex)
                colors.append(color)
                remaining ^= bit
                available ^= bit
                available &= ~adjacent[vertex]
        for i in range(len(order) - 1, -1, -1):
            if len(chosen) + colors[i] < target:
                stats['color_prunes'] += 1
                return None
            vertex = order[i]
            found = search(possible & adjacent[vertex], chosen + [vertex])
            if found is not None:
                return found
            possible &= ~(1 << vertex)
        return None

    return search((1 << len(adjacent)) - 1, [])


def literal_pair_witness(terms, gram, pairing):
    """Separate predicate, without graph masks or search state."""
    need(all((v, w) in TYPES and x != y and gram[x][y] == 0
             for v, w, x, y in terms), 'invalid reduced pair term')
    need(len({x for _, _, x, _ in terms}) == len(terms), 'repeated reader')
    need(len({y for _, _, _, y in terms}) == len(terms), 'repeated source')
    for i, (v, w, x, y) in enumerate(terms):
        for j, (vv, ww, xx, yy) in enumerate(terms):
            need(pairing[x][yy] == ((1 if i == j else 0) ^ (vv & w)),
                 'pair-term cross equation')


def reject(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError('negative control accepted')


def controls(data, pins):
    lines, gram, pairing, labels, form = data
    # A separate subset-enumeration oracle on all 1,024 labeled five-vertex graphs.
    edges = list(itertools.combinations(range(5), 2))
    for mask in range(1 << len(edges)):
        edge_set = {e for k, e in enumerate(edges) if mask >> k & 1}
        adjacent = [sum(1 << j for j in range(5)
                        if tuple(sorted((i, j))) in edge_set) for i in range(5)]
        omega = max(len(subset) for k in range(6) for subset in itertools.combinations(range(5), k)
                    if all(tuple(sorted(e)) in edge_set for e in itertools.combinations(subset, 2)))
        need(clique_at_least(adjacent, omega) is not None, 'clique oracle false negative')
        need(clique_at_least(adjacent, omega + 1) is None, 'clique oracle false positive')
    # Actual nine-pair E8 dual system from the predecessor's positive control.
    terms = [(0, 0, x, y) for x, y in DUAL_PAIRS]
    literal_pair_witness(terms, gram, pairing)
    vertices, adjacent = pair_graph(sorted({x for pair in DUAL_PAIRS for x in pair}), gram, pairing)
    found = clique_at_least(adjacent, 9)
    need(found is not None, 'positive nine-pair system missed')
    literal_pair_witness([vertices[i] for i in found], gram, pairing)
    total = 0
    for x, y in DUAL_PAIRS:
        total ^= geo.outer2(geo.matvec2(form, labels[x]), geo.matvec2(form, labels[y]))
    need(total == sum(row << (9 * i) for i, row in enumerate(form)), 'dual system target')
    wrong = terms[:]
    wrong[0] = (1, 0, *DUAL_PAIRS[0])
    wrong[1] = (0, 1, *DUAL_PAIRS[1])
    reject(lambda: literal_pair_witness(wrong, gram, pairing))
    reject(lambda: literal_pair_witness(terms + [terms[0]], gram, pairing))
    reject(lambda: literal_pair_witness([(1, 1, *DUAL_PAIRS[0])], gram, pairing))
    reject(lambda: literal_pair_witness([(0, 0, 0, 0)], gram, pairing))
    pin = next(row for row in pins['files'] if row['path'] == geo.WORD)
    raw = (geo.ROOT / geo.WORD).read_bytes()
    reject(lambda: authenticate(raw[:-1] + bytes([raw[-1] ^ 1]), pin))
    reject(lambda: geo.inverse2([1, 1]))
    # Rational pairing convention control: the retained nine COPY charges.
    copy_costs = []
    for i in range(9):
        left = [j for j in range(111) if labels[j] >> i & 1]
        right = [j for j in range(111) if (labels[j] & form[i]).bit_count() % 2]
        lb = geo.basis_mod3(left, lines, 8)
        rb = geo.basis_mod3(right, lines, 8)
        need(geo.rank_q([lines[j] for j in left]) == len(lb), 'reader basis incomplete')
        need(geo.rank_q([lines[j] for j in right]) == len(rb), 'source basis incomplete')
        copy_costs.append(geo.rank_q([[geo.dot(lines[x], lines[y]) for y in rb] for x in lb]))
    need(copy_costs == [7] * 9, 'incumbent rational pairing tariff')
    return {'all_five_vertex_graphs': 1024, 'nine_pair_positive_control': [list(p) for p in DUAL_PAIRS],
            'negative_controls': 6, 'incumbent_copy_costs': copy_costs}


def census(data, progress=False):
    _, gram, pairing, _, _ = data
    cases = geo.foursets(gram)
    need(len(cases) == 49648, 'four-set coverage count')
    stats, sizes = Counter(), Counter()
    graphs = hashlib.sha256()
    for number, subset in enumerate(sorted(cases), 1):
        vertices, adjacent = pair_graph(list(range(111, 120)) + list(subset), gram, pairing)
        sizes[len(vertices)] += 1
        found = clique_at_least(adjacent, 8, stats)
        need(found is None, 'eight-pair witness found at ' + repr(subset))
        graphs.update(canonical([subset, adjacent]) + b'\n')
        if progress and number % 10000 == 0:
            print(f'checked {number}/49648 four-sets', flush=True)
    return {'effective_punctures': len(cases), 'r_subset_incidences': sum(map(len, cases.values())),
            'common_r_multiplicities': dict(sorted(Counter(map(len, cases.values())).items())),
            'ordered_cases_sha256': digest([[list(s), cases[s]] for s in sorted(cases)]),
            'ordered_graphs_sha256': graphs.hexdigest(), 'vertex_counts': dict(sorted(sizes.items())),
            'search': dict(sorted(stats.items())), 'eight_pair_witnesses': 0,
            'pair_count_upper_bound': 7, 'ten_term_savings_upper_bound': 17,
            'ten_term_rational_cost_lower_bound': 63,
            'conditional_class_u_total_cost_lower_bound': 67}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', action='store_true')
    parser.add_argument('--controls-only', action='store_true')
    parser.add_argument('--progress', action='store_true')
    args = parser.parse_args()
    pins = check_sources()
    data = geo.reconstruct()
    checked_controls = controls(data, pins)
    reader_bases = geo.robust_reader_bases(data[0], data[1], data[3], data[4])
    target_blocks = geo.robust_target_blocks(data[1], data[3])
    if args.controls_only:
        print('PASS_BIT_PLANE_FOURSET_CONTROLS graphs=1024 controls=6 reader_functions=511')
        return
    result = {'schema_version': 1, 'source_commit': pins['predecessor_commit'],
              'scope': 'four-port ten-two-sided-term reduced-pair relaxation; no new kappa',
              'geometry_sha256': digest(data[0]), 'controls': checked_controls,
              'reader_bases_sha256': digest(reader_bases), 'reader_basis_count': 2555,
              'target_blocks': target_blocks, 'census': census(data, args.progress)}
    path = HERE / 'CERTIFICATE.json'
    if args.write_certificate:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), 'certificate mismatch')
    print('PASS_BIT_PLANE_FOURSET_BOUND sets=49648 eight_pair_witnesses=0 '
          'pair_cap=7 savings_cap=17 conditional_cost_floor=67 no_new_kappa')


if __name__ == '__main__':
    main()
