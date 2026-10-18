#!/usr/bin/env python3
"""Exact low-cost screen of a full Cartesian tensor lift of the112 E8 ports.

Prepared with OpenAI Codex assistance. Apache-2.0. The clique obstruction is
for odd binary labels orthogonal on every nonzero off-diagonal tensor Gram
entry. It is not a bound for all alternative geometries or a kappa certificate.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = row
                break
            row ^= pivots[bit]
    return len(pivots)


def rational_rank(rows):
    pivots = {}
    for values in rows:
        row = list(map(Q, values))
        for position, pivot in sorted(pivots.items()):
            if row[position]:
                scale = row[position]
                row = [x - scale * y for x, y in zip(row, pivot)]
        position = next((i for i, value in enumerate(row) if value), None)
        if position is not None:
            scale = row[position]
            pivots[position] = [value / scale for value in row]
    return len(pivots)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prototype', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert __debug__ and not args.out.exists()
    raw = args.prototype.read_bytes()
    source = json.loads(raw)
    ports, roots = source['binary_ports'][8:], source['root_lines'][8:]
    assert len(ports) == len(roots) == 112
    gram = [[sum(a * b for a, b in zip(left, right)) // 2 for right in roots] for left in roots]
    for i, p in enumerate(ports):
        for j, q in enumerate(ports):
            assert (p & q).bit_count() % 2 == (1 + gram[i][j]) % 2
    rank = binary_rank(ports)
    binary_gram_rank = binary_rank([sum(((p & q).bit_count() % 2) << j for j, q in enumerate(ports))
                                    for p in ports])
    assert rank == binary_gram_rank == 9 and rational_rank(roots) == 8
    center_support_ranks = [binary_rank([p for p, root in zip(ports, roots) if root[i]])
                            for i in range(8)]
    assert center_support_ranks == [8] * 8
    clique = [63, 110, 111, 97, 96, 61, 31, 29]
    for i in clique:
        for j in clique:
            assert (ports[i] & ports[j]).bit_count() % 2 == int(i == j)
            assert gram[i][j] != 0
    adjacent = next((i, j) for i in range(112) for j in range(i) if abs(gram[i][j]) == 1)
    i, j = adjacent
    # Constant-augmented direct sum has odd diagonal, but two adjacent factors
    # yield a nonzero real tensor entry and binary dot1, an illegal pair.
    assert (1 + 2 * ((ports[i] & ports[j]).bit_count() % 2)) % 2 == 1
    scaling = []
    for power in range(1, 5):
        count, centers = 112 ** power, 8 ** power
        lower_dimension, literal_dimension = 8 ** power, 9 ** power
        scaling.append(dict(power=power, ports=count, real_center_rank=centers,
                            clique_binary_dimension_lower_bound=lower_dimension,
                            literal_tensor_binary_dimension=literal_dimension,
                            literal_tensor_binary_gram_rank=9 ** power,
                            arbitrary_encoding_data_mass_lower_bound=str(2 * (lower_dimension - 1)),
                            literal_center_frame_rank=8 ** power,
                            literal_center_mass=centers * 8 ** power,
                            literal_data_center_mass_per_port=str(2 * (literal_dimension - 1) +
                                                                  Q(centers * 8 ** power, count))))
    record = dict(status='PASS_EXACT_TENSOR_GEOMETRY_SCREEN',
                  source_sha256=hashlib.sha256(raw).hexdigest(), binary_gram_rank=rank,
                  real_center_rank=8, base_center_support_ranks=center_support_ranks,
                  clique_port_indices=clique,
                  clique_binary_ports=[ports[index] for index in clique],
                  direct_sum_counterexample=dict(base_pair=adjacent,
                                                 real_tensor_coefficient=str(Q(gram[i][j] ** 2, 4)),
                                                 augmented_direct_sum_binary_dot=1),
                  tensor_identity='dot(p1 tensor ... tensor ps, q1 tensor ... tensor qs) '
                                  '= product_i dot(pi,qi) in F2',
                  rank_proof='The literal tensor binary Gram is B tensor ... tensor B; '
                             'field rank multiplies, so its rank is9^s. The eight-clique '
                             'tensors to8^s mutually orthogonal odd labels; these labels '
                             'are independent, requiring h>=8^s for any compatible encoding.',
                  scaling=scaling,
                  scope='Full Cartesian tensor port set with the inherited odd-label and '
                        'orthogonality contract. For arbitrary compatible encodings only data '
                        'frame mass is bounded. Literal tensor center supports have rank8^s, '
                        'not h-1. No helper or compiler charges are included. This explains '
                        'the depth tradeoff; it does not prove that '
                        'every tensor supplier has a worse exact recurrence.')
    args.out.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
