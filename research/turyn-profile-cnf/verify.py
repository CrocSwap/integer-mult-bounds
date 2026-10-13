#!/usr/bin/env python3
"""Check explicit coordinates, independently encode CNF, and replay a proof.

This file imports neither the producer nor any predecessor Python module.
The contradiction is checked by local rules, not by rerunning a SAT search.
Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from pathlib import Path
import argparse
import copy
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(name):
    return json.loads((HERE/name).read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_sources():
    source = read('SOURCES.json')
    for path, expected in source['files'].items():
        require(digest(ROOT/path) == expected, 'Source pin mismatch: '+path)
    return source


def codewords():
    # Span a fixed 12-row binary generator, instead of enumerating pairs
    # of affine evaluation tables as the independent producer does.
    rm_basis = (255, 170, 204, 240)
    perm = (0, 1, 2, 4, 3, 6, 7, 5)
    basis = [a | (a << 16) for a in rm_basis]
    basis += [(b << 8) | (b << 16) for b in rm_basis]
    for x in rm_basis:
        p = sum(((x >> perm[i]) & 1) << i for i in range(8))
        basis.append(p | (p << 8) | (p << 16))
    words = {0}
    for row in basis:
        words |= {word ^ row for word in words}
    require(len(words) == 4096, 'Independent generator rank 12')
    require(Counter(w.bit_count() for w in words) ==
            {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}, 'Code weight enumerator')
    return words


def geometry(witness):
    coordinates = witness['coordinates']
    require(len(coordinates) == 24, 'Exactly 24 coordinate vectors')
    require(all(len(row) == 24 and all(type(x) is int for x in row)
                for row in coordinates), 'Integer dimension 24')
    require(len({tuple(row) for row in coordinates}) == 24, 'Distinct coordinate vectors')
    words = codewords()
    profile = None
    for row in coordinates:
        require(sum(x*x for x in row) == 32, 'Norm squared 32')
        require(all((x-row[0]) % 2 == 0 for x in row), 'Uniform coordinate parity')
        require((sum(row)-4*row[0]) % 8 == 0, 'Leech coordinate-sum condition')
        magnitudes = Counter(map(abs, row))
        if magnitudes == {0: 16, 2: 8}:
            support = sum(1 << i for i, x in enumerate(row) if x)
            require(support in words and sum(x < 0 for x in row) % 2 == 0,
                    'Exact octad shell family: code support and even minus signs')
        elif magnitudes == {1: 23, 3: 1}:
            signs = [-x//3 if abs(x) == 3 else x for x in row]
            sign_word = sum(1 << i for i, x in enumerate(signs) if x == -1)
            require(sign_word in words, 'Exact exceptional-coordinate shell family')
        else:
            raise ValueError('Witness vector is outside the two full-port shell families')
        for residue in range(4):
            mask = sum(1 << i for i, x in enumerate(row) if x % 4 == residue)
            require(mask in words, 'Leech residue word belongs to Turyn code')
        norms = [sum(row[8*k+i]**2 for i in range(8)) for k in range(3)]
        require(sorted(norms) == [8, 8, 16], 'Actual three-block port profile')
        current = norms.index(16)
        if profile is None:
            profile = current
        require(current == profile, 'All witness ports belong to one profile')
        require(all(next(x for x in row[8*k:8*k+8] if x) > 0 for k in range(3)),
                'Canonical block signs')
    graph = [[False]*24 for _ in range(24)]
    for i in range(24):
        for j in range(i):
            nonzero = True
            for block in range(3):
                dot = 0
                for coordinate in range(8*block, 8*block+8):
                    dot += coordinates[i][coordinate]*coordinates[j][coordinate]
                nonzero = nonzero and dot != 0
            graph[i][j] = graph[j][i] = nonzero
    require(all(graph[i][j] for i in range(7) for j in range(i)), 'Anchor seven-clique')
    actual = [[i, j] for i in range(17) for j in range(i) if graph[i+7][j+7]]
    require(witness['original_variable_edges'] == actual, 'Every actual variable edge is recorded')
    require(len(actual) == 71, 'Predecessor finite variable graph size')
    source = json.loads((ROOT/'research/turyn-port-labels/evidence/PROFILE-H8.json').read_text())
    require(witness['port_ids'] == source['anchors']+source['vertices'], 'Predecessor witness IDs')
    reference = json.loads((ROOT/'research/leech-lattice/evidence/TURYN-GEOMETRY.json').read_text())
    require(witness['all_ports_sha256'] == reference['integer_representatives_sha256'],
            'Full-array generation receipt agrees with pinned reference')
    core = witness['core_variable_edges']
    require(len({tuple(edge) for edge in core}) == len(core), 'No duplicate core edges')
    require(all(edge in actual for edge in core), 'Core contains only actual edges')
    # A cyclic permutation preserves all block products and the Turyn code.
    # Check membership directly in the other two profiles, without asserting
    # that a graph isomorphism supplies a global rank-27 obstruction.
    for shift in (1, 2):
        for row in coordinates:
            rotated = row[8*shift:] + row[:8*shift]
            for residue in range(4):
                mask = sum(1 << i for i, x in enumerate(rotated) if x % 4 == residue)
                require(mask in words, 'Rotated actual port belongs to same Turyn code')
    return graph, profile


def encode(graph, edges):
    """Independent one-hot translation; IDs increase with vertex and label."""
    domain = []
    clauses = []
    next_id = 1
    for v in range(7, 24):
        candidates = []
        for label in range(256):
            parity = sum((label >> k) & 1 for k in range(8)) % 2
            if parity != 1:
                continue
            if any(graph[v][anchor] and ((label >> anchor) & 1) for anchor in range(7)):
                continue
            candidates.append((next_id, label))
            next_id += 1
        domain.append(candidates)
        clauses.append([item[0] for item in candidates])
        for a in range(len(candidates)):
            for b in range(a+1, len(candidates)):
                clauses.append([-candidates[a][0], -candidates[b][0]])
    for source, target in edges:
        for first_id, first in domain[source]:
            for second_id, second in domain[target]:
                dot = sum(((first >> k) & 1)*((second >> k) & 1) for k in range(8)) % 2
                if dot:
                    clauses.append([-first_id, -second_id])
    return clauses, next_id-1, [len(row) for row in domain]


def check_tree(clauses, variables, tree):
    counts = Counter()

    def visit(node, incoming):
        require(isinstance(node, dict), 'Proof node is an object')
        allowed = {'units', 'conflict'} if 'conflict' in node else {'units', 'branch', 'positive', 'negative'}
        require(set(node) == allowed, 'Proof node schema')
        values = incoming.copy()
        counts['nodes'] += 1
        for literal, reason in node['units']:
            require(type(literal) is int and 1 <= abs(literal) <= variables, 'Unit literal range')
            require(abs(literal) not in values, 'Unit assigns an unassigned variable')
            require(type(reason) is int and 0 <= reason < len(clauses), 'Unit reason range')
            clause = clauses[reason]
            require(not any(values.get(abs(lit)) == (lit > 0) for lit in clause),
                    'Unit reason is not satisfied already')
            require([lit for lit in clause if abs(lit) not in values] == [literal],
                    'Unit is exactly the sole unassigned literal of its reason')
            values[abs(literal)] = literal > 0
            counts['unit_steps'] += 1
        if 'conflict' in node:
            index = node['conflict']
            require(type(index) is int and 0 <= index < len(clauses), 'Conflict reason range')
            require(all(abs(lit) in values and values[abs(lit)] != (lit > 0)
                        for lit in clauses[index]), 'Leaf clause is completely false')
            counts['leaves'] += 1
            return
        branch = node['branch']
        require(type(branch) is int and 1 <= branch <= variables, 'Branch variable range')
        require(branch not in values, 'Branch variable is unassigned')
        visit(node['positive'], {**values, branch: True})
        visit(node['negative'], {**values, branch: False})

    visit(tree, {})
    return dict(counts)


def fitting(graph, edges, labels, width):
    require(len(labels) == 17, 'Seventeen positive-control labels')
    for i, label in enumerate(labels):
        require(type(label) is int and 0 <= label < (1 << width), 'Fitting label width')
        require(label.bit_count() % 2 == 1, 'Fitting odd diagonal')
        require(all(not(label >> j & 1) for j in range(7) if graph[i+7][j]),
                'Fitting anchor orthogonality')
    require(all((labels[a] & labels[b]).bit_count() % 2 == 0 for a, b in edges),
            'Fitting edge orthogonality')


def controls(witness, graph, clauses, variables, proof):
    data = read('CONTROLS.json')
    core = witness['core_variable_edges']
    require([item['removed_edge'] for item in data['core_single_edge_deletions']] == core,
            'Every core single-edge deletion has a positive witness')
    for item in data['core_single_edge_deletions']:
        remaining = [edge for edge in core if edge != item['removed_edge']]
        fitting(graph, remaining, item['labels'], 8)
        a, b = item['removed_edge']
        require((item['labels'][a] & item['labels'][b]).bit_count() % 2 == 1,
                'Deletion witness actually violates the missing edge')
    fitting(graph, [], data['relaxed_eight_bit_labels'], 8)
    fitting(graph, witness['original_variable_edges'], data['nine_bit_labels'], 9)
    rejected = []

    def rejection(name, action):
        try:
            action()
        except (ValueError, KeyError, IndexError, TypeError):
            rejected.append(name)
        else:
            raise ValueError('Corrupted control accepted: '+name)

    altered = copy.deepcopy(proof)
    leaf = altered
    while 'branch' in leaf:
        leaf = leaf['positive']
    require(leaf['units'], 'Leaf has a unit to mutate')
    leaf['units'][0][0] *= -1
    rejection('wrong_unit_sign', lambda: check_tree(clauses, variables, altered))
    altered_leaf = copy.deepcopy(proof)
    leaf = altered_leaf
    while 'branch' in leaf:
        leaf = leaf['negative']
    leaf['conflict'] = len(clauses)
    rejection('invalid_conflict_reference', lambda: check_tree(clauses, variables, altered_leaf))
    truncated = copy.deepcopy(proof)
    require('branch' in truncated, 'Nontrivial two-branch proof')
    del truncated['negative']
    rejection('missing_branch', lambda: check_tree(clauses, variables, truncated))
    repeated = copy.deepcopy(proof)
    repeated['negative'] = copy.deepcopy(repeated['positive'])
    rejection('repeated_positive_branch', lambda: check_tree(clauses, variables, repeated))
    no_edges, no_edge_variables, _ = encode(graph, [])
    rejection('proof_on_relaxed_graph', lambda: check_tree(no_edges, no_edge_variables, proof))
    bad_coordinates = copy.deepcopy(witness)
    bad_coordinates['coordinates'][0][0] += 1
    rejection('altered_coordinate', lambda: geometry(bad_coordinates))
    bad_label = data['nine_bit_labels'].copy()
    bad_label[0] = 0
    rejection('even_label', lambda: fitting(graph, witness['original_variable_edges'], bad_label, 9))
    return {'rejected': rejected, 'satisfiable_single_edge_deletions': len(core),
            'relaxed_eight_bit_fitting': True, 'full_nine_bit_fitting': True}


def run():
    source = check_sources()
    witness = read('WITNESS.json')
    graph, profile = geometry(witness)
    clauses, variables, domain_sizes = encode(graph, witness['core_variable_edges'])
    dimacs = (HERE/'CORE.cnf').read_text().splitlines()
    require(dimacs[0].split() == ['p', 'cnf', str(variables), str(len(clauses))],
            'DIMACS header agrees with independently encoded CNF')
    stored_clauses = [list(map(int, line.split())) for line in dimacs[1:]]
    require(all(row and row[-1] == 0 and 0 not in row[:-1] for row in stored_clauses),
            'One properly terminated DIMACS clause per line')
    require([row[:-1] for row in stored_clauses] == clauses,
            'DIMACS clauses agree with independently encoded CNF')
    proof = read('PROOF.json')
    proof_counts = check_tree(clauses, variables, proof)
    control_report = controls(witness, graph, clauses, variables, proof)
    return {'status': 'PASS_TURYN_PROFILE_CNF', 'base_commit': source['base_commit'],
            'profile': profile, 'ports': 24, 'anchors': 7,
            'original_variable_edges': len(witness['original_variable_edges']),
            'core_variable_edges': len(witness['core_variable_edges']),
            'cnf_variables': variables, 'cnf_clauses': len(clauses),
            'domain_sizes': domain_sizes, 'proof': proof_counts, 'controls': control_report,
            'scope': 'Exact finite standard-dot fitting dimension is nine for this 24-port witness; cyclic copies occur in all three profiles. No global dimension-27 or new-kappa claim.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path, help='write a new receipt instead of comparing EXPECTED.json')
    args = parser.parse_args()
    result = run()
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        require(result == read('EXPECTED.json'), 'Deterministic expected receipt')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
