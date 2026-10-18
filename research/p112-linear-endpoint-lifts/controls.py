# SPDX-License-Identifier: Apache-2.0
"""Check rejected premises and small exact controls for the proof lemmas."""
from copy import deepcopy
from itertools import combinations_with_replacement
from accounting import check_local, distance
from geometry import model, rank, require, verify_graph_certificate


def reject(name, operation, expected):
    try:
        operation()
    except ValueError as error:
        require(str(error) == expected, 'unexpected rejection: ' + name)
    else:
        raise ValueError('control accepted: ' + name)
    return name


def run(certificate, word, programs):
    labels, form, edges = model(word['ports'])
    rejected = []
    bad = deepcopy(certificate)
    bad['basis_edges'][0] = [0, 0]
    rejected.append(reject('nonedge in tensor basis',
        lambda: verify_graph_certificate(bad, labels, form, edges), 'basis edge membership'))
    bad = deepcopy(certificate)
    bad['basis_edges'].pop()
    rejected.append(reject('missing tensor basis edge',
        lambda: verify_graph_certificate(bad, labels, form, edges), 'basis has 80 distinct edges'))
    bad = deepcopy(certificate)
    bad['edge_vertices'][0]['vertex'] = bad['anchors'][0]
    rejected.append(reject('aliased anchor witness',
        lambda: verify_graph_certificate(bad, labels, form, edges), 'distinct witness vertices'))
    bad = deepcopy(programs)
    next(e for e in bad['forward'] if e[0] == 'center')[-1] = 7
    rejected.append(reject('rank-seven charge for rank-eight centre',
        lambda: check_local(word, bad), 'minimum Fourier rank'))
    bad = deepcopy(programs)
    next(e for e in bad['forward'] if e[0] == 'climb')[-1] += 1
    rejected.append(reject('overcharged reference edge',
        lambda: check_local(word, bad), 'minimum Fourier rank'))

    # If nondegeneracy is removed, every endpoint can be one isotropic plane.
    isotropic = [0b0011, 0b1100]
    require(rank(isotropic) == 2 and all((x & y).bit_count() % 2 == 0
            for x in isotropic for y in isotropic), 'degenerate endpoint counterexample')

    # This control includes an alternating fibre and a coupled non-diagonal fibre.
    forms = [[[1, 0], [0, 1]], [[0, 1], [1, 0]], [[1, 1], [1, 0]]]
    for fibre in forms:
        gram = [[form[i // 2][j // 2] * fibre[i % 2][j % 2]
                 for j in range(18)] for i in range(18)]
        require(rank([sum(x << j for j, x in enumerate(row)) for row in gram]) == 18,
                'sharp dimension tensor witness')
        require(rank([sum(x << j for j, x in enumerate(row)) for row in fibre]) == 2,
                'nondegenerate fibre')

    updates = 0
    positions = list(combinations_with_replacement(range(4), 2))
    for code in range(1 << len(positions)):
        matrix = [0] * 4
        for bit, (i, j) in enumerate(positions):
            if code >> bit & 1:
                matrix[i] |= 1 << j
                matrix[j] |= 1 << i
        old_rank = rank(matrix)
        for u in range(1, 16):
            if rank(matrix + [u]) == old_rank:
                continue
            updated = [row ^ (u if u >> i & 1 else 0) for i, row in enumerate(matrix)]
            require(rank(updated) >= old_rank, 'rank-one update outside the image')
            updates += 1

    # Enumerate all subspaces in four dimensions, including slanted subspaces.
    spaces = {frozenset({0})}
    pending = list(spaces)
    while pending:
        space = pending.pop()
        for v in range(1, 16):
            other = space | frozenset(x ^ v for x in space)
            if other not in spaces:
                spaces.add(other)
                pending.append(other)
    require(len(spaces) == 67, 'four-dimensional subspace census')
    pairs = 0
    for first in spaces:
        for second in spaces:
            core_first = [x for x in first if x < 4]
            core_second = [x for x in second if x < 4]
            q_first = rank(first) - rank(core_first)
            q_second = rank(second) - rank(core_second)
            require(distance(list(first), list(second)) >=
                    distance(core_first, core_second) + abs(q_first - q_second),
                    'padding quotient distance')
            pairs += 1
    return {'rejected_mutations': rejected, 'degenerate_dimension_four_counterexample': True,
            'dimension_eighteen_fibre_forms': forms, 'rank_one_update_cases': updates,
            'padding_subspace_pairs': pairs,
            'scope': 'Finite controls for the stated premises; the all-size proofs are in PROOF.md.'}
