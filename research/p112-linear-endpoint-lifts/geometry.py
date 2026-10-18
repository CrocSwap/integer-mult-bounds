# SPDX-License-Identifier: Apache-2.0
"""Construct the exact P112 graph and its binary label model."""
from itertools import combinations


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def model(ports):
    require(len(ports) == len(set(ports)) == 112, 'selected port count')
    require(all(0 < x < 512 and x.bit_count() % 2 == 1 for x in ports),
            'norm-one binary ports')
    require(rank(ports) == 9, 'port span')
    labels = [[(x >> j) & 1 for j in range(9)] for x in ports]
    form = [[int(i == j) for j in range(9)] for i in range(9)]
    edges = [[a, b] for a in range(112) for b in range(112)
             if a != b and (ports[a] & ports[b]).bit_count() % 2 == 0]
    require(len(edges) == 5824, 'ordered edge count')
    return labels, form, edges


def tensor_row(labels, edge):
    a, b = edge
    return sum((labels[a][i] * labels[b][j]) << (9 * i + j)
               for i in range(9) for j in range(9))


def basis_edges(labels, edges):
    pivots, chosen = {}, []
    for edge in edges:
        row = tensor_row(labels, edge)
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                chosen.append(edge)
                break
    return chosen


def verify_graph_certificate(certificate, labels, form, edges):
    edge_set = {tuple(edge) for edge in edges}
    chosen = certificate['basis_edges']
    require(len(chosen) == 80 and len({tuple(x) for x in chosen}) == 80,
            'basis has 80 distinct edges')
    require(all(tuple(edge) in edge_set for edge in chosen), 'basis edge membership')
    require(rank([tensor_row(labels, edge) for edge in chosen]) == 80, 'edge tensor rank')
    null = sum(form[i][j] << (9 * i + j) for i in range(9) for j in range(9))
    require(all((tensor_row(labels, e) & null).bit_count() % 2 == 0 for e in edges),
            'bilinear null form')
    anchors = certificate['anchors']
    pairs = certificate['edge_vertices']
    require(len(anchors) == 8 and len(pairs) == 24, 'anchor certificate size')
    require(len(set(anchors + [x['vertex'] for x in pairs])) == 32, 'distinct witness vertices')
    require(all((a, b) in edge_set for a, b in combinations(anchors, 2)), 'anchor clique')
    support = {tuple(x['pair']): x['vertex'] for x in pairs}
    require(len(support) == 24 and all(0 <= i < j < 8 for i, j in support),
            'edge-vertex indexing')
    missing = [p for p in combinations(range(8), 2) if p not in support]
    require(len(missing) == 4 and sorted(i for p in missing for i in p) == list(range(8)),
            'missing perfect matching')
    for pair, vertex in support.items():
        require(all(((vertex, a) in edge_set) == (k not in pair)
                    for k, a in enumerate(anchors)), 'anchor incidence')
    for (pair, a), (other, b) in combinations(support.items(), 2):
        require(((a, b) in edge_set) == bool(set(pair) & set(other)), 'edge incidence')
    return {'ordered_edges': len(edges), 'tensor_rank': 80, 'nullity': 1,
            'anchor_vertices': 8, 'edge_vertices': 24,
            'edge_vertex_undirected_edges': 120, 'minimum_two_plane_dimension': 18}
