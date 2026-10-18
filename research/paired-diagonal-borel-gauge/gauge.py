"""Paired-diagonal analytic gauges; exact rational difference constraints."""
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def valuation(value):
    value = Q(value)
    need(value != 0, 'valuation requires nonzero entry')
    n, d = abs(value.numerator), value.denominator
    return (n & -n).bit_length() - (d & -d).bit_length()


def constraints(m, matrices):
    need(type(m) is int and m > 0, 'positive width')
    edges = []
    for k, matrix in enumerate(matrices):
        need(len(matrix) == 2*m and all(len(row) == 2*m for row in matrix),
             'square H/D matrix dimension')
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                value = Q(value)
                if value:
                    edges.append({'from': j % m, 'to': i % m,
                                  'weight': valuation(value),
                                  'matrix': k, 'row': i, 'column': j})
    return edges


def solve(m, matrices):
    """Bellman-Ford with an implicit zero-weight source to every coordinate."""
    edges = constraints(m, matrices)
    distance, predecessor = [0]*m, [None]*m
    for _ in range(m):
        changed = None
        for index, edge in enumerate(edges):
            u, v, weight = edge['from'], edge['to'], edge['weight']
            if distance[v] > distance[u] + weight:
                distance[v] = distance[u] + weight
                predecessor[v], changed = index, v
        if changed is None:
            return {'kind': 'potential', 'weights': [x-distance[0] for x in distance]}
    vertex = changed
    for _ in range(m):
        vertex = edges[predecessor[vertex]]['from']
    start, backward = vertex, []
    while True:
        index = predecessor[vertex]
        backward.append(index)
        vertex = edges[index]['from']
        if vertex == start:
            break
        need(len(backward) <= m, 'predecessor cycle bound')
    return {'kind': 'negative-cycle', 'edge_indices': list(reversed(backward))}


def conjugate(matrix, weights):
    m = len(weights)
    return [[Q(value)*Q(2)**(weights[j % m]-weights[i % m])
             for j, value in enumerate(row)] for i, row in enumerate(matrix)]
