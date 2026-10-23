#!/usr/bin/env python3
"""Independent finite Turyn geometry and CNF certificate producer.

No predecessor module is imported. Standard library only; Apache-2.0.
"""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import argparse
import hashlib
import json
import random
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(vector):
    result = []
    for b in range(3):
        block = vector[8*b:8*b+8]
        first = next((v for v in block if v), 0)
        if not first:
            return None
        result.extend(block if first > 0 else [-v for v in block])
    return tuple(result)


def construct_ports():
    # Evaluate all affine Boolean functions on F_2^3. Turyn's second
    # Reed--Muller copy uses the pinned coordinate permutation.
    points = list(product((0, 1), repeat=3))
    affine = set()
    for coefficients in product((0, 1), repeat=4):
        row = tuple((coefficients[0] + sum(a*b for a, b in
                     zip(coefficients[1:], x))) % 2 for x in points)
        affine.add(row)
    permutation = (0, 1, 2, 4, 3, 6, 7, 5)
    second = {tuple(row[i] for i in permutation) for row in affine}
    code = {tuple(x ^ y for x, y in zip(a, c)) +
            tuple(x ^ y for x, y in zip(b, c)) +
            tuple(x ^ y ^ z for x, y, z in zip(a, b, c))
            for a in affine for b in affine for c in second}
    require(len(code) == 4096, 'Turyn code has dimension 12')
    require(Counter(map(sum, code)) == {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1},
            'Turyn weight enumerator')
    ports = set()
    # The two-coordinate shell family cannot meet all three blocks.
    # Generate only the other two families, directly modulo block signs.
    for word in code:
        if sum(word) == 8:
            support = [i for i, bit in enumerate(word) if bit]
            if all(any(8*b <= i < 8*b+8 for i in support) for b in range(3)):
                for bits in product((0, 1), repeat=7):
                    signs = bits + (sum(bits) % 2,)
                    vector = [0]*24
                    for index, sign in zip(support, signs):
                        vector[index] = -2 if sign else 2
                    ports.add(canonical(vector))
        for exceptional in range(24):
            vector = [1-2*bit for bit in word]
            vector[exceptional] *= -3
            ports.add(canonical(vector))
    require(None not in ports and len(ports) == 23040, '23,040 canonical ports')
    ordered = sorted(ports)
    digest = hashlib.sha256(bytes(v % 256 for row in ordered for v in row)).hexdigest()
    reference = json.loads((ROOT/'research/leech-lattice/evidence/TURYN-GEOMETRY.json').read_text())
    require(digest == reference['integer_representatives_sha256'],
            'Independent full coordinate array matches immutable predecessor digest')
    return ordered, digest


def adjacency(coordinates):
    return [(a, b) for a in range(len(coordinates)) for b in range(a)
            if all(sum(x*y for x, y in zip(coordinates[a][8*k:8*k+8],
                                          coordinates[b][8*k:8*k+8])) != 0
                   for k in range(3))]


def make_problem(coordinates, variable_edges=None, width=8):
    edges = set(adjacency(coordinates))
    require(all((i, j) in edges for i in range(7) for j in range(i)),
            'Seven orthogonal anchors')
    domains = [[label for label in range(1 << width) if label.bit_count() % 2
                and all(not(label >> j & 1) for j in range(7) if (i+7, j) in edges)]
               for i in range(len(coordinates)-7)]
    actual = [(a-7, b-7) for a, b in sorted(edges) if b >= 7]
    if variable_edges is None:
        variable_edges = actual
    require(set(map(tuple, variable_edges)) <= set(actual), 'Only actual variable edges')
    labels, identifiers = [], []
    for vertex, domain in enumerate(domains):
        row = []
        for label in domain:
            row.append(len(labels)+1)
            labels.append([vertex, label])
        identifiers.append(row)
    clauses = []
    for row in identifiers:
        clauses.append(row)
        clauses.extend([-a, -b] for a, b in combinations(row, 2))
    for a, b in variable_edges:
        clauses.extend([-i, -j] for i in identifiers[a] for j in identifiers[b]
                       if (labels[i-1][1] & labels[j-1][1]).bit_count() % 2)
    return {'width': width, 'domains': domains, 'labels': labels,
            'variable_edges': variable_edges, 'clauses': clauses}


def solve(clauses):
    """Plain Boolean DPLL; retain explicit unit reasons and full split tree."""
    statistics = Counter()

    def visit(assignment, depth):
        statistics['nodes'] += 1
        statistics['maximum_depth'] = max(statistics['maximum_depth'], depth)
        units = []
        while True:
            residual = []
            unit = None
            for index, clause in enumerate(clauses):
                if any(assignment.get(abs(lit)) == (lit > 0) for lit in clause):
                    continue
                unassigned = [lit for lit in clause if abs(lit) not in assignment]
                if not unassigned:
                    statistics['conflicts'] += 1
                    return None, {'units': units, 'conflict': index}
                if len(unassigned) == 1:
                    unit = (unassigned[0], index)
                    break
                residual.append(unassigned)
            if unit is None:
                break
            literal, reason = unit
            assignment[abs(literal)] = literal > 0
            units.append([literal, reason])
            statistics['unit_steps'] += 1
        if not residual:
            return assignment, None
        # Branch in a shortest remaining clause. Prefer positive choice
        # literals, so a multi-valued domain is not the branching object.
        shortest = min(residual, key=lambda clause: (len(clause), clause[0] < 0))
        occurrences = Counter(abs(lit) for clause in residual for lit in clause)
        branch = max(map(abs, shortest), key=lambda lit: (occurrences[lit], -lit))
        solution, positive = visit({**assignment, branch: True}, depth+1)
        if solution is not None:
            return solution, None
        solution, negative = visit({**assignment, branch: False}, depth+1)
        if solution is not None:
            return solution, None
        return None, {'units': units, 'branch': branch, 'positive': positive, 'negative': negative}

    solution, proof = visit({}, 0)
    return solution, proof, dict(statistics)


def selected_labels(problem, assignment):
    return [next(label for index, (which, label) in enumerate(problem['labels'], 1)
                 if which == vertex and assignment.get(index) is True)
            for vertex in range(len(problem['domains']))]


def write(name, value):
    (HERE/name).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reduce', action='store_true', help='one deterministic edge deletion pass')
    args = parser.parse_args()
    start = time.monotonic()
    ports, digest = construct_ports()
    source = json.loads((ROOT/'research/turyn-port-labels/evidence/PROFILE-H8.json').read_text())
    ids = source['anchors'] + source['vertices']
    coordinates = [ports[i] for i in ids]
    problem = make_problem(coordinates)
    print('Geometry OK; CNF', len(problem['labels']), 'variables,', len(problem['clauses']),
          'clauses;', len(problem['variable_edges']), 'variable edges', flush=True)
    solution, proof, stats = solve(problem['clauses'])
    require(solution is None, 'Predecessor full graph is UNSAT')
    print('Full graph UNSAT', stats, flush=True)
    full_edges = problem['variable_edges']
    core_edges = full_edges.copy()
    if args.reduce:
        order = core_edges.copy()
        random.Random(78).shuffle(order)
        for step, edge in enumerate(order, 1):
            candidate = [e for e in core_edges if e != edge]
            trial = make_problem(coordinates, candidate)
            solution, _, _ = solve(trial['clauses'])
            if solution is None:
                core_edges = candidate
            print('Reduction', step, '/', len(order), 'retained', len(core_edges), flush=True)
    problem = make_problem(coordinates, core_edges)
    solution, proof, stats = solve(problem['clauses'])
    require(solution is None, 'Core remains UNSAT')
    deletion_controls = []
    if args.reduce:
        for edge in core_edges:
            trial = make_problem(coordinates, [e for e in core_edges if e != edge])
            solution, _, _ = solve(trial['clauses'])
            require(solution is not None, 'Every retained core edge is essential')
            deletion_controls.append({'removed_edge': edge,
                                      'labels': selected_labels(trial, solution)})
    relaxed = make_problem(coordinates, [])
    relaxed_solution, _, _ = solve(relaxed['clauses'])
    require(relaxed_solution is not None, 'Relaxed positive control')
    # A ninth coordinate supplies a positive boundary control for this exact
    # finite graph, independently of the inherited global label generator.
    nine = make_problem(coordinates, width=9)
    nine_solution, _, nine_stats = solve(nine['clauses'])
    require(nine_solution is not None, 'Nine-bit graph has a fitting')
    write('WITNESS.json', {'port_ids': ids, 'coordinates': coordinates,
                         'all_ports_sha256': digest, 'original_variable_edges': full_edges,
                         'core_variable_edges': core_edges})
    write('PROOF.json', proof)
    write('CONTROLS.json', {'core_single_edge_deletions': deletion_controls,
                            'relaxed_eight_bit_labels': selected_labels(relaxed, relaxed_solution),
                            'nine_bit_labels': selected_labels(nine, nine_solution)})
    write('BUILD.json', {'status': 'UNSAT', 'seed': 78,
                        'cnf_variables': len(problem['labels']), 'cnf_clauses': len(problem['clauses']),
                        'full_variable_edges': len(full_edges), 'core_variable_edges': len(core_edges),
                        'solver_statistics': stats, 'nine_bit_solver_statistics': nine_stats})
    dimacs = 'p cnf '+str(len(problem['labels']))+' '+str(len(problem['clauses']))+'\n'
    dimacs += ''.join(' '.join(map(str, clause))+' 0\n' for clause in problem['clauses'])
    (HERE/'CORE.cnf').write_text(dimacs)
    print('Artifacts written in', round(time.monotonic()-start, 3), 'seconds', flush=True)


if __name__ == '__main__':
    main()
