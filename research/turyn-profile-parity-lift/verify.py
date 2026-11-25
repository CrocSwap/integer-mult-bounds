#!/usr/bin/env python3
"""Direct integer checker for actual-port characteristic-two parity covers.

No producer, predecessor geometry module, or numerical package is imported.
"""
from collections import Counter
from pathlib import Path
import argparse
import copy
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(value, message):
    if not value:
        raise ValueError(message)


def load(name):
    return json.loads((HERE/name).read_text())


def source_check():
    source = load('SOURCES.json')
    for name, expected in source['files'].items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected,
                'Pinned source mismatch: '+name)
    return source


def turyn_code():
    generators = []
    for word in (255, 170, 204, 240):
        generators += [word | (word << 16), (word << 8) | (word << 16)]
    permutation = (0, 1, 2, 4, 3, 6, 7, 5)
    for word in (255, 170, 204, 240):
        other = sum(((word >> permutation[i]) & 1) << i for i in range(8))
        generators.append(other | (other << 8) | (other << 16))
    code = {0}
    for row in generators:
        code |= {word ^ row for word in code}
    require(len(code) == 4096, 'Turyn code dimension 12')
    require(Counter(word.bit_count() for word in code) ==
            {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}, 'Turyn code weights')
    return code


def actual_port(row, profile, code):
    require(len(row) == 24 and all(type(x) is int for x in row), 'Integer 24-vector')
    require(sum(x*x for x in row) == 32, 'Integer squared norm 32')
    require(all((x-row[0]) % 2 == 0 for x in row), 'Common coordinate parity')
    require((sum(row)-4*row[0]) % 8 == 0, 'Leech sum condition')
    magnitudes = Counter(map(abs, row))
    if magnitudes == {0: 16, 2: 8}:
        support = sum(1 << i for i, x in enumerate(row) if x)
        require(support in code and sum(x < 0 for x in row) % 2 == 0,
                'Octad shell family with even minus signs')
    elif magnitudes == {1: 23, 3: 1}:
        signs = [-x//3 if abs(x) == 3 else x for x in row]
        word = sum(1 << i for i, x in enumerate(signs) if x == -1)
        require(word in code, 'Exceptional-coordinate shell family')
    else:
        raise ValueError('Not a full-port shell vector')
    for residue in range(4):
        word = sum(1 << i for i, x in enumerate(row) if x % 4 == residue)
        require(word in code, 'Residue code condition')
    norms = [sum(row[8*k+i]**2 for i in range(8)) for k in range(3)]
    require(norms == [16 if k == profile else 8 for k in range(3)], 'Exact profile')
    require(all(next(x for x in row[8*k:8*k+8] if x) > 0 for k in range(3)),
            'Canonical block signs')


def active(a, b):
    return all(sum(a[8*k+i]*b[8*k+i] for i in range(8)) != 0 for k in range(3))


def binary_rank(rows):
    remaining = [list((row >> k) & 1 for k in range(9)) for row in rows]
    pivot = 0
    for column in range(9):
        selected = next((i for i in range(pivot, len(remaining)) if remaining[i][column]), None)
        if selected is None:
            continue
        remaining[pivot], remaining[selected] = remaining[selected], remaining[pivot]
        for i in range(len(remaining)):
            if i != pivot and remaining[i][column]:
                remaining[i] = [x ^ y for x, y in zip(remaining[i], remaining[pivot])]
        pivot += 1
    return pivot


def verify_profile(record, code, quotient_cliques):
    profile = record['profile']
    require(type(profile) is int and profile in (0, 1, 2), 'Profile range')
    coordinates = record['coordinates']
    require(len(coordinates) == 20 and len({tuple(row) for row in coordinates}) == 20,
            'Twenty distinct actual ports')
    for row in coordinates:
        actual_port(row, profile, code)
    graph = {(i, j) for i in range(20) for j in range(i) if active(coordinates[i], coordinates[j])}
    cliques = record['cliques']
    require(len(cliques) == 9, 'Nine cliques')
    incidences = Counter()
    clique_edges = set()
    for clique in cliques:
        require(len(clique) == 8 and len(set(clique)) == 8, 'Eight distinct clique vertices')
        require(all(type(v) is int and 0 <= v < 20 for v in clique), 'Clique vertex range')
        incidences.update(clique)
        for i, a in enumerate(clique):
            for b in clique[:i]:
                edge = (max(a, b), min(a, b))
                require(edge in graph, 'Clique pair is an actual active port edge')
                clique_edges.add(edge)
    require(set(incidences) == set(range(20)), 'Every supplied port is used')
    require(Counter(incidences.values()) == {2: 12, 6: 8}, 'Exact even incidence histogram')
    require(clique_edges == graph and len(graph) == 124, 'All 124 actual edges are covered')
    labels = record['nine_bit_labels']
    require(len(labels) == 20 and all(type(x) is int and 0 <= x < 512 for x in labels),
            'Twenty nine-bit labels')
    require(all(x.bit_count() % 2 == 1 for x in labels), 'Odd label diagonals')
    require(all((labels[a] & labels[b]).bit_count() % 2 == 0 for a, b in graph),
            'Nine-bit fitting on every actual graph edge')
    require(binary_rank(labels) == 9, 'Explicit label rank nine')
    classes = record['classes']
    require(len(classes) == len(set(classes)) == 20 and classes == sorted(classes),
            'Twenty ordered source class IDs')
    require(all(type(c) is int and c//960 == profile for c in classes), 'Source class profiles')
    inherited = [[c for c in clique if c//960 == profile] for clique in quotient_cliques]
    require(record['clique_classes'] == inherited, 'Exact inherited quotient restrictions')
    require([[classes[v] for v in clique] for clique in cliques] == inherited,
            'Literal local-index to source-clique correspondence')
    require(len(record['selected_ports']) == len(set(record['selected_ports'])) == 20,
            'Twenty distinct recorded source port IDs')
    require(all(type(v) is int and 0 <= v < 23040 for v in record['selected_ports']),
            'Recorded source port ID range')
    reference = json.loads((ROOT/'research/leech-lattice/evidence/TURYN-GEOMETRY.json').read_text())
    require(record['all_ports_sha256'] == reference['integer_representatives_sha256'],
            'Generation receipt full-array hash')
    return {'profile': profile, 'ports': 20, 'cliques': 9, 'clique_size': 8,
            'ordered_clique_edge_checks': 9*8*7, 'distinct_actual_edges': len(graph),
            'incidence_histogram': {'2': 12, '6': 8}, 'explicit_binary_label_rank': 9,
            'block_rank_lower_bound_per_d': 9, 'scalar_and_normalized_block_rank': 9}


def corruption_controls(record, code, quotient):
    rejected = []
    def rejection(name, altered):
        try:
            verify_profile(altered, code, quotient)
        except (ValueError, IndexError, KeyError, TypeError):
            rejected.append(name)
        else:
            raise ValueError('Accepted corruption: '+name)
    missing = copy.deepcopy(record)
    missing['cliques'].pop()
    rejection('missing_clique', missing)
    duplicated = copy.deepcopy(record)
    duplicated['cliques'][0][0] = duplicated['cliques'][0][1]
    rejection('repeated_clique_vertex', duplicated)
    coordinate = copy.deepcopy(record)
    coordinate['coordinates'][0][0] += 1
    rejection('changed_coordinate', coordinate)
    even = copy.deepcopy(record)
    even['nine_bit_labels'][0] = 0
    rejection('even_diagonal_label', even)
    collision = copy.deepcopy(record)
    a, b = collision['cliques'][0][:2]
    collision['nine_bit_labels'][a] = collision['nine_bit_labels'][b]
    rejection('equal_labels_on_clique_edge', collision)
    wrong_source = copy.deepcopy(record)
    wrong_source['clique_classes'][0][0] += 1
    rejection('changed_source_clique', wrong_source)
    control = load('SAME-CLASS-CONTROL.json')
    require(control['profile'] == record['profile'], 'Same-class control profile')
    actual_port(control['replacement_coordinates'], record['profile'], code)
    position = control['position']
    require(type(position) is int and 0 <= position < 20, 'Same-class replacement position')
    require(control['source_class'] == record['classes'][position], 'Same source class ID')
    require(control['original_port'] == record['selected_ports'][position], 'Original source port ID')
    require(all(control['replacement_coordinates'][8*k:8*k+8] ==
                record['coordinates'][position][8*k:8*k+8]
                for k in range(3) if k != record['profile']), 'Identical two low roots')
    a, b = control['broken_required_edge']
    require(a == position and type(b) is int and 0 <= b < 20 and a != b,
            'Broken-edge control endpoints')
    require(any(a in clique and b in clique for clique in record['cliques']),
            'Control edge is required by a literal clique')
    require(not active(control['replacement_coordinates'], record['coordinates'][b]),
            'Valid same-class replacement loses the required actual edge')
    replaced = copy.deepcopy(record)
    replaced['coordinates'][position] = control['replacement_coordinates']
    rejection('valid_same_class_port_breaks_actual_clique', replaced)
    return rejected


def global_scope_check(profiles, quotient, control):
    chosen = {c: row for record in profiles
              for c, row in zip(record['classes'], record['coordinates'])}
    reports = []
    require(len(control['cliques']) == 9, 'Nine global scope controls')
    for index, clique in enumerate(quotient):
        missing = []
        for i, a in enumerate(clique):
            for b in clique[i+1:]:
                if a//960 == b//960:
                    continue
                dots = [sum(chosen[a][8*k+j]*chosen[b][8*k+j] for j in range(8))
                        for k in range(3)]
                if any(dot == 0 for dot in dots):
                    missing.append({'classes': [a, b], 'integer_block_dots': dots})
        require(missing, 'These specific profile choices fail a global required edge')
        report = {'clique_index': index, 'missing_cross_profile_edges': len(missing),
                  'first_missing_edge': missing[0]}
        require(report == control['cliques'][index], 'Exact global scope control')
        reports.append(report)
    return reports


def run():
    source = source_check()
    data = load('CERTIFICATE.json')
    require([r['profile'] for r in data['profiles']] == [0, 1, 2], 'Exactly all three profiles')
    quotient = json.loads((ROOT/'research/turyn-code-space/evidence/PARITY-CERTIFICATE.json').read_text())['cliques']
    code = turyn_code()
    reports = [verify_profile(r, code, quotient) for r in data['profiles']]
    controls = corruption_controls(data['profiles'][0], code, quotient)
    global_scope = global_scope_check(data['profiles'], quotient, load('GLOBAL-SCOPE-CONTROL.json'))
    return {'status': 'PASS_ACTUAL_TURYN_PROFILE_BLOCK_RANK_9', 'base_commit': source['base_commit'],
            'profiles': reports, 'corruption_controls': controls,
            'global_scope_controls': global_scope,
            'scope': 'Each 20-port witness has rank exactly 9d for minimum-rank asymmetric d-block fittings over every characteristic-two field. No global 27-dimensional or new-kappa claim.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    report = run()
    if args.write:
        args.write.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    else:
        require(report == load('EXPECTED.json'), 'Exact deterministic receipt')
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
