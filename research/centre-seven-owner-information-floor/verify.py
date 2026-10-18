#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact length-six route-relator census for the selected centre interface.

This extends the pinned blocks-1..6 information audit by testing the first
possible support size, seven.  Python's tuple hash is used only to bucket
candidate equal matrices; every bucket collision is resolved by exact matrix
comparison, so hashing cannot hide a relation.
"""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
from functools import reduce
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = ROOT / 'research/centre-block-repair-information/verify.py'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_predecessor():
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    for row in manifest['files']:
        if row['usage'] == 'input':
            raw = (ROOT / row['path']).read_bytes()
            need(digest(raw) == row['sha256'], 'source pin: ' + row['path'])

    # Compile authenticated bytes directly; do not import a timestamp-selected
    # bytecode cache from a predecessor directory.
    source_bytes = PREDECESSOR.read_bytes()
    module = types.ModuleType('pinned_centre_block_repair')
    module.__file__ = str(PREDECESSOR)
    exec(compile(source_bytes, module.__file__, 'exec'), module.__dict__)

    source, data = module.load(ROOT)
    prior = module.build(ROOT)
    retained = json.loads((ROOT / 'research/centre-block-repair-information/RESULT.json').read_bytes())
    need(canonical(prior) == canonical(retained), 'predecessor receipt mismatch')
    return source, data


def compose_with_supports(left, right_supports):
    """Return the GF(2) matrix left*right, represented by its 73 columns."""
    return tuple(reduce(int.__xor__, (left[k] for k in support), 0)
                 for support in right_supports)


def braid_graph_edges(route_matrices):
    """Independent direct check of the braid-edge interpretation."""
    edges = []
    for a in range(len(route_matrices)):
        for b in range(a + 1, len(route_matrices)):
            ab = tuple(_act(route_matrices[a], c) for c in route_matrices[b])
            aba = tuple(_act(ab, c) for c in route_matrices[a])
            ba = tuple(_act(route_matrices[b], c) for c in route_matrices[a])
            bab = tuple(_act(ba, c) for c in route_matrices[b])
            if aba == bab:
                edges.append((a, b))
    return edges


def _act(columns, vector):
    out = 0
    while vector:
        bit = (vector & -vector).bit_length() - 1
        out ^= columns[bit]
        vector &= vector - 1
    return out


def exact_reduced_triple_products(route_matrices):
    """Exhaust reduced words and exact-resolve every hash bucket collision."""
    n = len(route_matrices)
    supports = [[[k for k in range(len(route_matrices[0])) if (column >> k) & 1]
                 for column in route] for route in route_matrices]
    pairs = [[None] * n for _ in range(n)]
    for a in range(n):
        for b in range(n):
            if a != b:
                pairs[a][b] = compose_with_supports(route_matrices[a], supports[b])

    # Map a fingerprint to exact representatives by route labels.  Equal
    # matrices necessarily have the same tuple hash; distinct matrices that
    # collide are retained as separate representatives after exact comparison.
    # Retain every member of each exact class so every pairwise relator is
    # checked, including classes with more than two words.
    buckets = {}
    duplicate_pairs = []
    fingerprint_collisions = 0
    total = 0
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            ab = pairs[a][b]
            for c in range(n):
                if c == b:
                    continue
                word = (a, b, c)
                matrix = compose_with_supports(ab, supports[c])
                fingerprint = hash(matrix)
                representatives = buckets.get(fingerprint)
                if representatives is None:
                    buckets[fingerprint] = [[word, [word]]]
                else:
                    matched = False
                    for representative, members in representatives:
                        old = compose_with_supports(
                            pairs[representative[0]][representative[1]],
                            supports[representative[2]])
                        if matrix == old:
                            members.append(word)
                            matched = True
                            break
                    if not matched:
                        if len(representatives) == 1:
                            fingerprint_collisions += 1
                        representatives.append([word, [word]])
                total += 1

    classes = [members for representatives in buckets.values()
               for _, members in representatives]
    relation_pairs = [(left, right) for members in classes
                      for i, left in enumerate(members)
                      for right in members[i + 1:]]
    class_size_histogram = Counter(map(len, classes))
    return total, relation_pairs, fingerprint_collisions, class_size_histogram


def build():
    source, data = load_predecessor()
    route_matrices = [source.route(record) for record in data['phases']['recipes']]
    need(len(route_matrices) == 112, 'route count')
    need(len(set(route_matrices)) == 112, 'duplicate route matrices')

    (reduced_words, duplicate_pairs, fingerprint_collisions,
     product_class_sizes) = exact_reduced_triple_products(route_matrices)
    cyclic_relations = []
    braid_edges = set()
    non_braid = []
    for left, right in duplicate_pairs:
        a, b, c = left
        d, e, f = right
        # The equality abc=def gives the six-letter identity abc fed.
        # These inequalities say that it is cyclically reduced.
        if a != b and b != c and c != f and f != e and e != d and d != a:
            word = (a, b, c, f, e, d)
            cyclic_relations.append([list(left), list(right), list(word)])
            if len(set(word)) == 2 and all(word[i] != word[(i + 1) % 6]
                                           for i in range(6)):
                braid_edges.add(tuple(sorted(set(word))))
            else:
                non_braid.append([list(left), list(right), list(word)])

    direct_edges = braid_graph_edges(route_matrices)
    need(set(direct_edges) == braid_edges, 'relator edges differ from direct braid check')
    adjacency = [set() for _ in route_matrices]
    for a, b in braid_edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    triangles = [[a, b, c]
                 for a in range(112)
                 for b in adjacency[a] if a < b
                 for c in adjacency[a] & adjacency[b] if b < c]

    need(reduced_words == 1_379_952, 'reduced triple count')
    need(len(duplicate_pairs) == 50, 'exact duplicate product count')
    need(product_class_sizes == Counter({1: 1_379_852, 2: 50}),
         'reduced product class-size histogram')
    need(len(cyclic_relations) == 50, 'cyclically reduced relation count')
    need(not non_braid, 'non-braid cyclic relation')
    need(len(braid_edges) == 50, 'braid edge count')
    need(not triangles, 'braid graph has a triangle')

    degree_histogram = Counter(map(len, adjacency))
    return {
        'status': 'PASS_CENTRE_SEVEN_OWNER_INFORMATION_FLOOR',
        'source_base': '864290c2b9c8cde72e89ff34f5678081fb4cad42',
        'predecessor': 'centre-block-repair-information',
        'route_count': len(route_matrices),
        'route_dimension': 73,
        'reduced_triple_products': reduced_words,
        'exact_duplicate_pairs': len(duplicate_pairs),
        'exact_product_class_size_histogram': {
            str(k): v for k, v in sorted(product_class_sizes.items())},
        'cyclically_reduced_length6_relations': len(cyclic_relations),
        'all_cyclic_relations_are_braids': True,
        'braid_edge_count': len(braid_edges),
        'braid_edges': [list(edge) for edge in sorted(braid_edges)],
        'braid_degree_histogram': {str(k): v for k, v in sorted(degree_histogram.items())},
        'braid_graph_triangle_count': len(triangles),
        'support_floor': 8,
        'information_repair': {
            'all_blocks_proved': {'minimum_size': 1, 'maximum_size': 7,
                                  'extra_scalar_linear_observations_exact': '104*block_size'},
            'scope': 'selected PR1094 calls 0/4; entire later query field; scalar linear repair observations; arbitrary global decoder',
        },
        'collision_handling': 'tuple-hash buckets; every matching fingerprint is resolved by exact 73-column matrix comparison',
        'fingerprint_collision_buckets': fingerprint_collisions,
        'cyclic_relation_sha256': hashlib.sha256(canonical(cyclic_relations)).hexdigest(),
        'scope': 'written support-7/Fano implication plus exhaustive exact binary route-matrix enumeration; no native tariff, supplier admission or new kappa',
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path)
    parser.add_argument('--receipt', type=Path, default=HERE / 'RESULT.json')
    args = parser.parse_args()
    result = build()
    if args.write:
        with args.write.open('xb') as stream:
            stream.write(canonical(result))
    else:
        need(canonical(result) == canonical(json.loads(args.receipt.read_bytes())),
             'receipt mismatch')
    print('PASS_CENTRE_SEVEN_OWNER_INFORMATION_FLOOR support>=8 blocks=1..7 repair=104*b '
          'length6_relations=50 braid_triangles=0 no_new_kappa')


if __name__ == '__main__':
    main()
