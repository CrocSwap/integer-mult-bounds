#!/usr/bin/env python3
"""Check the pair modes and the positive metric certificate."""
import ast
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
from check_partial_orthogonal import SOURCE, add, encode, lift, need, product, transpose

HERE = Path(__file__).resolve().parent
PIN = '84e527589ab11fa59136e262c75511d9f71af1ba55504fb59b73ac789a350dff'


def dot(left, right):
    return sum((value * right.get(key, F(0)) for key, value in left.items()), F(0))


def apply(matrix, vector):
    return {i: value for i, row in enumerate(matrix) if (value := dot(row, vector))}


def main():
    raw = (SOURCE / 'SYMMETRIC-RESPONSE-SEARCH.json').read_bytes()
    need(sha256(raw).hexdigest() == PIN, 'Pinned symmetric family')
    source = json.loads(raw)
    matrices = []
    for direction in source['symmetric_directions']:
        matrix = [{} for _ in range(112)]
        for pair, value in direction['effect'].items():
            i, j = ast.literal_eval(pair)
            matrix[i][j] = lift(value)
        need(matrix == transpose(matrix), 'Symmetric direction')
        need(all(not row.get(i) for i, row in enumerate(matrix)), 'Zero diagonal')
        matrices.append(matrix)
    need(len(matrices) == 42, '42 specified directions')
    witness = [{} for _ in range(112)]
    factors = {i: F(2) if i in (32, 37) else F(-1) for i in range(32, 40)}
    for i, coefficient in factors.items():
        for target, row in zip(witness, matrices[i]):
            add(target, row, 1 / (6 * coefficient))
    large = [i for i, row in enumerate(witness) if row]
    small = sorted(set(range(112)) - set(large))
    need(len(large) == 48 and len(small) == 64, '48 and 64 port split')
    need(all(not row.get(i) for i, row in enumerate(witness)), 'Witness has zero diagonal')

    projectors, vertices = {}, []
    for index, coefficient in factors.items():
        adjacency = [{j: value / coefficient for j, value in row.items()}
                     for row in matrices[index]]
        square = product(adjacency, adjacency)
        projector = []
        for row, original in zip(square, adjacency):
            row = dict(row)
            add(row, original, -4)
            projector.append({j: value / 5 for j, value in row.items()})
        need(product(projector, projector) == projector, 'Range projector')
        need(product(projector, adjacency) == adjacency, 'Projector contains response')
        pairs = [(i, j, value) for i, row in enumerate(projector)
                 for j, value in row.items() if i < j]
        need(len(pairs) == 6, 'Six pair modes per vertex')
        columns = []
        for i, j, value in pairs:
            need(projector[i] == {i: F(1, 2), j: value}, 'Pair projector first row')
            need(projector[j] == {i: value, j: F(1, 2)}, 'Pair projector second row')
            need(abs(value) == F(1, 2), 'Pair sign')
            columns.append({i: F(1), j: 2 * value})
        reduced = [[dot(a, apply(adjacency, b)) / 2 for b in columns] for a in columns]
        signs = [F(1)] + reduced[0][1:]
        need(all(signs[i] * reduced[i][j] * signs[j] == (0 if i == j else 1)
                 for i in range(6) for j in range(6)), 'Exact K6 adjacency in pair modes')
        vertices.append({'direction': index, 'factor': str(coefficient),
                         'pair_columns': [{str(k): str(value * signs[i]) for k, value in column.items()}
                                          for i, column in enumerate(columns)]})
        projectors[index] = projector
    total = [{} for _ in range(112)]
    for projector in projectors.values():
        for target, row in zip(total, projector):
            add(target, row)
    need(total == [{i: F(1)} if i in large else {} for i in range(112)],
         'The eight ranges cover exactly 48 ports')
    need(all(not any(product(left, right)) for i, left in projectors.items()
             for j, right in projectors.items() if i != j), 'The eight ranges are orthogonal')

    pair_edges = []
    for port in large:
        incident = [i for i, projector in projectors.items() if projector[port]]
        need(len(incident) == 2, 'Two vertices per physical port')
        partners = [j for j in projectors[incident[0]][port] if j != port]
        need(len(partners) == 1, 'One physical partner')
        other = partners[0]
        need(other in projectors[incident[1]][port], 'Same physical pair at both vertices')
        if port < other:
            pair_edges.append({'ports': [port, other], 'vertices': [i - 32 for i in incident]})
    edges = {tuple(edge['vertices']) for edge in pair_edges}
    missing = [(i, j) for i in range(8) for j in range(i + 1, 8) if (i, j) not in edges]
    need(missing == [(0, 5), (1, 6), (2, 7), (3, 4)], 'K8 minus a matching')

    for port in range(112):
        columns = {i: {row: matrix[row][port] for row in range(112) if port in matrix[row]}
                   for i, matrix in enumerate(matrices)}
        active = [i for i, column in columns.items() if column]
        transformed = {i: apply(witness, columns[i]) for i in active}
        actual = {(i, j): dot(columns[i], transformed[j])
                  for i in active for j in active if dot(columns[i], transformed[j])}
        if port in small:
            expected = {(40, 40): F(1, 6), (40, 41): F(-1, 3),
                        (41, 40): F(-1, 3), (41, 41): F(7, 8)}
        else:
            incident = [i for i, projector in projectors.items() if projector[port]]
            expected = {(i, i): F(5, 3) * factors[i]**2 for i in incident}
        need(actual == expected, ('Exact positive certificate at column', port))

    orthogonal = [{} for _ in range(112)]
    for i in range(32):
        for target, row in zip(orthogonal, matrices[i]):
            add(target, row, 2 if i % 4 in (2, 3) else 1)
    squared = product(orthogonal, orthogonal)
    need(squared == [{i: F(4)} if i in small else {} for i in range(112)],
         'Sharp rank 64 example')
    result = {'status': 'PASS_SYMMETRIC_FAMILY_METRIC_OBSTRUCTION', 'source_sha256': PIN,
              'scope': 'The specified 42-dimensional real symmetric response family.',
              'metric_scope': 'Every positive diagonal input metric and every nonzero real row and column gauge.',
              'orthogonal_rank_bound': 64, 'bound_is_attained': True,
              'forced_zero_coefficients': list(range(32, 42)),
              'column_certificate_count': 112, 'small_ports': small, 'large_ports': large,
              'witness': encode(witness), 'vertices': vertices, 'pair_edges': pair_edges,
              'missing_vertex_edges': missing,
              'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / 'SYMMETRIC-FAMILY.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], 'sharp rank bound 64; all 112 column identities', flush=True)


if __name__ == '__main__':
    main()
