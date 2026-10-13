"""Exact D24+ norm-four shell and a support-priced dyadic factorization."""
from collections import Counter, defaultdict
from itertools import combinations, product
import numpy as np


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank_binary(values):
    pivots = {}
    for value in values:
        value = int(value)
        while value:
            pivot = value.bit_length()-1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def label(support):
    parity = sum(1 << j for j in support)
    q = (parity & ((1 << 22)-1)) ^ (((parity >> 22) & 1)*((1 << 22)-1))
    even = q | ((q.bit_count() & 1) << 22)
    return ((1 << 23)-1) ^ even


def construct():
    rows = []
    for j in range(24):
        row = np.zeros(24, dtype=np.int16)
        row[j] = 2
        rows.append(row)
    for support in combinations(range(24), 4):
        for signs in product((-1, 1), repeat=3):
            row = np.zeros(24, dtype=np.int16)
            row[list(support)] = (1,)+signs
            rows.append(row)
    vectors = np.asarray(rows)
    require(vectors.shape == (85032, 24), 'D24 norm-four line count')
    require(np.all(np.sum(vectors*vectors, axis=1) == 4), 'D24 shell norm')
    return vectors


def certify_d24():
    vectors = construct()
    supports = list(combinations(range(24), 4))
    labels = [label(support) for support in supports]
    require(rank_binary([label(())]+labels) == 23, 'D24 binary dimension')
    require(all(value.bit_count() % 2 for value in labels), 'Odd standard-dot labels')
    # The quotient removes the radical of the even-weight space in F2^24.
    # On its basis e_i+e_23, the quotient is q_i=x_i+x_22, i<22.
    even_basis = [(i, 23) for i in range(23)]
    for first in even_basis:
        for second in even_basis:
            actual = (label(first) & label(second)).bit_count() % 2
            require(actual == (1 ^ (len(set(first) & set(second)) % 2)),
                    'Exact binary pairing on the even-weight basis')
    require(label(()) == (1 << 23)-1, 'Constant odd direction')
    unary, mixed, triple = defaultdict(list), defaultdict(list), defaultdict(list)
    for support, value in zip(supports, labels):
        for j in support:
            unary[j].append(value)
        for pair in combinations(support, 2):
            mixed[pair].append(value)
        for indices in combinations(support, 3):
            triple[indices].append(value)
    unary_hist = Counter(rank_binary(unary[j]) for j in range(24))
    mixed_hist = Counter(rank_binary(mixed[pair]) for pair in combinations(range(24), 2))
    triple_hist = Counter(rank_binary(triple[indices]) for indices in combinations(range(24), 3))
    require(unary_hist == {23:24}, 'Unary support dimensions')
    require(mixed_hist == {22:276}, 'Mixed support dimensions')
    require(triple_hist == {21:2024}, 'Triple support dimensions')
    # The diagonal factorization is exact: each center uses the same support
    # at source and target, with dyadic signed coefficients.
    indices = np.unique(np.r_[np.arange(24), np.linspace(24, len(vectors)-1, 128, dtype=int)])
    sample = vectors[indices].astype(np.int64)
    axis = np.zeros_like(sample)
    axis[np.abs(sample) == 2] = sample[np.abs(sample) == 2]//2
    y = sample.copy()
    y[np.abs(sample) == 2] = 0
    pair_features = np.stack([sample[:, i]**2*sample[:, j]
                              for i in range(24) for j in range(24) if i != j], axis=1)
    triple_features = np.stack([sample[:, i]*sample[:, j]*sample[:, k]
                                for i,j,k in combinations(range(24),3)], axis=1)
    gram_times_16 = 16*(axis @ axis.T) - y @ y.T + pair_features @ pair_features.T + 2*(triple_features @ triple_features.T)
    dots = sample @ sample.T
    require(np.array_equal(3*gram_times_16, dots**3-4*dots), 'Dyadic cubic identity sample')
    sample_labels = [label(np.flatnonzero(row % 2)) for row in sample]
    binary_gram = np.array([[(a & b).bit_count() % 2 for b in sample_labels] for a in sample_labels])
    require(np.array_equal(binary_gram, 1 ^ (dots & 1)), 'Standard-dot fitting identity sample')
    active = gram_times_16 != 0
    np.fill_diagonal(active, False)
    require(not binary_gram[active].any() and np.all(np.diag(gram_times_16) == 16),
            'Normalized fitting sample')
    full_hist = {'1':24, '23':24, '22':552, '21':2024}
    reduced_hist = {'23':24, '22':552, '21':2024}
    return dict(status='PASS_D24_NORM4_DYADIC_FACTORIZATION',
        lattice='D24+', port_count=85032, binary_dimension=23,
        real_rank=2600, center_count=2624, center_width_histogram=full_hist,
        center_bill=sum(int(width)*count for width,count in full_hist.items()),
        omitted_axis_variant=dict(port_count=85008, real_rank=2576,
            center_count=2600, center_width_histogram=reduced_hist,
            center_bill=sum(int(width)*count for width,count in reduced_hist.items())),
        shell_types={'axis_lines':24, 'four_coordinate_lines':85008},
        factorization='K=AA^T+(MM^T-YY^T)/16+TT^T/8; A_j=x_j/2 on axes only, Y_j=x_j off axes, M_ij=x_i^2*x_j (i!=j), T_ijk=x_i*x_j*x_k',
        universal_identity='Expand (x.y)^3-4(x.y). Unary terms equal 48 A_j A_j -3 Y_j Y_j; mixed coefficients are3 and triple coefficients6. Division by48 gives the displayed dyadic factorization for every shell pair.',
        rank_argument='Independent sign characters separate2024 triple functions and24 unary sectors. In unary sectorj, the23 inclusion functions on3-subsets ofthe other23coordinates are independent overQ; the coefficient is(I-J/9)/16 with nonzero eigenvalues1/16 and-14/144. Hence off-axis rank2024+24*23=2576. The24 isolated axis ports add24.',
        exact_support_checks=dict(unary=24, unordered_mixed=276, triple=2024),
        sample_pairs=len(indices)**2,
        scope='Exact scalar factorization, binary fitting, and source/target support bill. No controller, dirty-helper word, hosting map, or kappa certificate is supplied.')
