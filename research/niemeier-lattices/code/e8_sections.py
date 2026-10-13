"""Rank-minimal dyadic factorizations for the two- and three-block E8 shells."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import importlib.util
import json
import numpy as np

_spec = importlib.util.spec_from_file_location('niemeier_e8_cubed', Path(__file__).with_name('e8_cubed.py'))
e8 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e8)
require = e8.require


def transforms():
    lines = [list(line) for line in combinations(range(7), 3)
             if (line[0] + 1) ^ (line[1] + 1) ^ (line[2] + 1) == 0]
    fano = np.zeros((7, 8), dtype=np.int32)
    for row, line in enumerate(lines):
        fano[row, line] = 1
        fano[row, 7] = -1
    trace = np.array([-1] * 7 + [3], dtype=np.int32)
    target = 2 * np.diag([1] * 7 + [-1])
    require(np.array_equal(fano.T @ fano - np.outer(trace, trace), target),
            'Exact Fano-plane quadratic identity')
    hadamard = np.array([[1 if (row & col).bit_count() % 2 == 0 else -1
                          for col in range(8)] for row in range(8)], dtype=np.int32)
    require(np.array_equal(hadamard @ hadamard.T, 8 * np.eye(8, dtype=np.int32)),
            'Exact eight-coordinate Hadamard identity')
    # The three-block residual trace form is diag(1/8,1/8) - J/2.
    trace_diagonal = np.array([[-3, -4], [-4, -3]], dtype=np.int32)
    require(np.array_equal(-7 * np.ones((2, 2), dtype=np.int32)
                           + np.array([[1, -1], [-1, 1]], dtype=np.int32),
                           2 * trace_diagonal), 'Exact two-trace diagonalization')
    return lines, hadamard


def support(values, packed, name):
    selected = np.flatnonzero(values)
    basis, witnesses = {}, []
    for index in selected:
        if e8.insert_binary(basis, packed[index]):
            witnesses.append(int(index))
    return dict(name=name, support_size=len(selected), binary_span=len(basis),
                independent_ports=witnesses)


def fano_factorization(ports, packed, blocks):
    lines, hadamard = transforms()
    rows = ports.astype(np.int32)
    u = rows[:, 0]
    quotient = (u ** 3 - u) // 3
    f, g = 5 * u - quotient, quotient - u
    same = u[:, None] * rows[:, 1:8] ** 2
    other = [u[:, None] * rows[:, 8 * block:8 * (block + 1)] ** 2
             for block in range(1, blocks)]
    require(np.array_equal(3 * f, same.sum(axis=1) + sum(part.sum(axis=1) for part in other)),
            'Sphere relation removes the redundant unary center')
    transformed = [part @ hadamard.T for part in other]
    h = same[:, lines[0]].sum(axis=1) - f
    data = [('unary_g', g), ('fano_h', h),
            ('mixed_hadamard', transformed[0][:, 1]),
            ('pure_distinct', rows[:, 0] * rows[:, 1] * rows[:, 2]),
            ('mixed_distinct', rows[:, 0] * rows[:, 1] * rows[:, 8])]
    if blocks == 2:
        data.append(('trace', transformed[0][:, 0]))
        multiplicities = dict(unary_g=16, fano_h=112, mixed_hadamard=112,
                              pure_distinct=112, mixed_distinct=448, trace=16)
        expected_widths = [17, 17, 15, 17, 17, 17]
        expected_bill, expected_centers = 13648, 816
    else:
        data.extend([('trace_plus', transformed[0][:, 0] + transformed[1][:, 0]),
                     ('trace_minus', transformed[0][:, 0] - transformed[1][:, 0])])
        multiplicities = dict(unary_g=24, fano_h=168, mixed_hadamard=336,
                              pure_distinct=168, mixed_distinct=1344,
                              trace_plus=24, trace_minus=24)
        expected_widths = [25, 25, 15, 25, 17, 25, 25]
        expected_bill, expected_centers = 38088, 2088
    orbits = [support(values, packed, name) for name, values in data]
    require([orbit['binary_span'] for orbit in orbits] == expected_widths,
            'Exact support dimensions of all Fano factorization orbits')
    histogram = Counter()
    for orbit in orbits:
        orbit['multiplicity'] = multiplicities[orbit['name']]
        histogram[orbit['binary_span']] += orbit['multiplicity']
    bill = sum(width * count for width, count in histogram.items())
    require(bill == expected_bill and sum(histogram.values()) == expected_centers,
            'Complete rank-minimal center accounting')
    coefficients = dict(unary_g='1/256', fano_h='1/2048', mixed_hadamard='1/8192',
                        pure_distinct='1/512', mixed_distinct='1/512')
    coefficients.update(dict(trace='-3/8192') if blocks == 2 else
                        dict(trace_plus='-7/16384', trace_minus='1/16384'))
    return dict(center_count=expected_centers, center_bill=bill,
        center_width_histogram={str(width): count for width, count in sorted(histogram.items())},
        support_orbits=orbits, diagonal_coefficients=coefficients,
        fano_triples=lines, hadamard_matrix=hadamard.tolist(),
        definitions='For coordinate i, m_j=u_i*u_j^2 for the seven other coordinates in its E8 block; f=(16*u_i-u_i^3)/3; g=(u_i^3-4*u_i)/3. Let h_T=sum_{j in T}m_j-f for the seven Fano triples. In each other block let b_k=sum_j H[k,j]*u_i*u_j^2, k=0,...,7. Retain all distinct-coordinate cubic monomials supported on at most two blocks. Add g, the seven h_T, the seven b_k with k>0 per other block, and the listed trace center(s) b_0 or b_0+c_0 and b_0-c_0.',
        identity='3*f=sum_j m_j+sum_other_blocks b_0. The Fano identity is sum_j m_j*m_j_prime-f*f_prime = (sum_T h_T*h_T_prime-(sum_other_blocks b_0)*(sum_other_blocks b_0_prime))/2. Hadamard transforms give each other-block contribution sum_k b_k*b_k_prime/8. The displayed trace coefficients diagonalize the remaining one- or two-variable form.',
        support_proof='All support rows, including zero tests, are exhausted for one representative of each listed orbit. Block permutations and within-block coordinate permutations preserve the lattice and induce invertible binary label maps. They act transitively on the listed center supports: a Fano center chooses a three-subset among seven coordinates, and a nonconstant Hadamard row chooses a balanced four/four partition. Thus the representative support dimensions apply to every center. Encoder and decoder supports agree because this factorization is symmetric and diagonal.',
        scope='An exact scalar factorization and support bill, not a complete recursive circuit or a new kappa.')


def evaluate_operator_centers(ports):
    """Return actual integer encoder values and integer diagonal weights/Q."""
    rows = np.asarray(ports, dtype=np.int64)
    blocks = rows.shape[1] // 8
    require(blocks in (2, 3), 'Two or three E8 blocks')
    lines, _ = transforms()
    denominator = 8192 if blocks == 2 else 16384
    features, weights = [], []
    for block in range(blocks):
        for triple in combinations(range(8 * block, 8 * (block + 1)), 3):
            features.append(np.prod(rows[:, triple], axis=1))
            weights.append(denominator // 512)
    for block in range(blocks):
        for coordinate in range(8 * block, 8 * (block + 1)):
            u = rows[:, coordinate]
            f, g = (16 * u - u ** 3) // 3, (u ** 3 - 4 * u) // 3
            features.append(g)
            weights.append(denominator // 256)
            same = [j for j in range(8 * block, 8 * (block + 1)) if j != coordinate]
            repeated = u[:, None] * rows[:, same] ** 2
            for line in lines:
                features.append(repeated[:, line].sum(axis=1) - f)
                weights.append(denominator // 2048)
            traces = []
            for other_block in range(blocks):
                if other_block == block:
                    continue
                other = rows[:, 8 * other_block:8 * (other_block + 1)]
                traces.append(u * (other * other).sum(axis=1))
                for shift in range(8):
                    for character in range(8):
                        if (shift, character) == (0, 0) or (shift & character).bit_count() % 2:
                            continue
                        permutation = [j ^ shift for j in range(8)]
                        signs = [(-1) ** ((j & character).bit_count() % 2) for j in range(8)]
                        features.append(u * (other * other[:, permutation] * signs).sum(axis=1))
                        weights.append(denominator // 8192)
            if blocks == 2:
                features.append(traces[0])
                weights.append(-3)
            else:
                features.extend((traces[0] + traces[1], traces[0] - traces[1]))
                weights.extend((-7, 1))
    return np.stack(features, axis=1), np.array(weights, dtype=np.int64), denominator


def operator_factorization(ports, packed, blocks, coordinate_factor):
    operators, parameters = [], []
    for shift in range(8):
        for character in range(8):
            if (shift & character).bit_count() % 2:
                continue
            matrix = np.zeros((8, 8), dtype=np.int32)
            for column in range(8):
                matrix[column ^ shift, column] = (-1) ** ((column & character).bit_count() % 2)
            require(np.array_equal(matrix, matrix.T), 'Symmetric real Pauli operator')
            require(np.array_equal(matrix @ matrix, np.eye(8, dtype=np.int32)),
                    'Pauli involution identity')
            operators.append(matrix)
            parameters.append([shift, character])
    flattened = np.stack(operators).reshape(36, 64)
    require(np.array_equal(flattened @ flattened.T, 8 * np.eye(36, dtype=np.int32)),
            'Complete orthogonal basis of symmetric eight-by-eight operators')
    require(parameters[0] == [0, 0] and all(np.trace(matrix) == 0 for matrix in operators[1:]),
            'One trace direction and 35 traceless quadratic directions')
    rows = ports.astype(np.int32)
    other = rows[:, 8:16]
    receipts = []
    for parameter, matrix in zip(parameters[1:], operators[1:]):
        values = rows[:, 0] * np.sum((other @ matrix) * other, axis=1)
        entry = support(values, packed, 'mixed_pauli')
        require(entry['binary_span'] == 15 and entry['support_size'] == 3744,
                'Exhaustive support rank for every traceless Pauli center')
        entry['pauli_shift_character'] = parameter
        receipts.append(entry)
    narrow = 35 * 8 * blocks * (blocks - 1)
    high = 256 if blocks == 2 else 408
    high_width = 8 * blocks + 1
    bill = high * high_width + narrow * 15
    require(bill == (12752 if blocks == 2 else 35400), 'Operator-space center bill')
    require(high + narrow == coordinate_factor['center_count'], 'Rank-minimal operator factorization')
    diagnostic_rows = np.unique(np.concatenate((np.arange(64),
        np.linspace(0, len(ports) - 1, 128, dtype=int))))
    evaluated, weights, denominator = evaluate_operator_centers(ports[diagnostic_rows])
    require(evaluated.shape[1] == high + narrow, 'Explicit encoder column count')
    dots = ports[diagnostic_rows].astype(np.int64) @ ports[diagnostic_rows].astype(np.int64).T
    require(np.array_equal(3 * ((evaluated * weights) @ evaluated.T),
                           (denominator // 1024) * (dots ** 3 - 64 * dots)),
            'Exact integer diagnostic replay of the complete encoder-decoder factorization')
    retained = [entry for entry in coordinate_factor['support_orbits']
                if entry['name'] not in ('mixed_hadamard', 'mixed_distinct')]
    require(sum(entry['multiplicity'] for entry in retained) == high,
            'Unchanged pure and trace center multiplicities')
    return dict(center_count=high + narrow, center_bill=bill,
        full_factorization_diagnostic_rows=diagnostic_rows.tolist(),
        center_width_histogram={str(high_width): high, '15': narrow},
        retained_support_orbits=retained, pauli_support_orbits=receipts,
        mixed_center_coefficient='1/8192',
        retained_diagonal_coefficients={name: value for name, value in
            coordinate_factor['diagonal_coefficients'].items()
            if name not in ('mixed_hadamard', 'mixed_distinct')},
        operator_rule='P_(a,b)e_x=(-1)^(b dot x)e_(x+a), a,b,x in F2^3, a dot b=0. Omit (a,b)=(0,0).',
        mixed_center_rule='For each ordered pair of distinct E8 blocks A,B, each coordinate i in A, and each of the 35 operators P, use u_A,i * (u_B^T P u_B).',
        quadratic_identity='sum_{P nonidentity} (u^T P u)*(v^T P v) = 8*(u dot v)^2 - (u dot u)*(v dot v)',
        proof='The 36 explicitly checked symmetric Pauli matrices are an orthogonal basis of Sym_8 with squared Frobenius norm8; this proves the quadratic identity for all real u,v. The identity replaces the seven nonconstant diagonal Hadamard centers and 28 mixed off-diagonal cubic centers per ordered block/coordinate by35 Pauli centers, all with coefficient1/8192. The trace direction is unchanged, so the prior Fano trace diagonalization and the full kernel identity remain exact. All35 support sets are exhausted on actual ports; block permutations and permutations within the linear block cover all coordinate choices. Encoder and decoder supports agree in this symmetric dyadic diagonal factorization.',
        scope='Exact rank-minimal scalar factorization, binary support bill, and a genuine reduction versus the coordinate basis. Helper exits, a finite recursive word, and a new kappa remain separate obligations.')


def support_frames(ports, packed):
    """Exhaust the eight coordinate partners of every two-block Pauli frame."""
    rows = ports.astype(np.int32)
    frames, groups = Counter(), []
    for first, second in ((0, 1), (1, 0)):
        other = rows[:, 8 * second:8 * (second + 1)]
        for shift in range(8):
            for character in range(8):
                if (shift, character) == (0, 0) or (shift & character).bit_count() % 2:
                    continue
                permutation = [j ^ shift for j in range(8)]
                signs = [(-1) ** ((j & character).bit_count() % 2) for j in range(8)]
                quadratic = (other * other[:, permutation] * signs).sum(axis=1)
                partners = []
                for coordinate in range(8):
                    basis = {}
                    for index in np.flatnonzero(quadratic * rows[:, 8 * first + coordinate]):
                        e8.insert_binary(basis, packed[index])
                    for pivot in sorted(basis):
                        for higher in basis:
                            if higher > pivot and (basis[higher] >> pivot) & 1:
                                basis[higher] ^= basis[pivot]
                    canonical = tuple(basis[pivot] for pivot in sorted(basis))
                    require(len(canonical) == 15, 'Every Pauli partner support has dimension15')
                    partners.append(canonical)
                    frames[canonical] += 1
                require(len(set(partners)) == 1, 'All eight coordinate partners share one binary frame')
                gram_basis = {}
                for left in partners[0]:
                    gram_row = sum((((left & right).bit_count() & 1) << index)
                                   for index, right in enumerate(partners[0]))
                    e8.insert_binary(gram_basis, gram_row)
                require(len(gram_basis) == 13, 'Pauli support frame has a two-dimensional radical')
                groups.append(dict(linear_block=first, quadratic_block=second,
                    pauli_shift_character=[shift, character], binary_frame=list(partners[0]),
                    restricted_dot_rank=13, radical_dimension=2))
    require(len(frames) == 70 and set(frames.values()) == {8}, 'Exactly 70 shared Pauli frames')
    return dict(distinct_width15_frames=70, centers_per_width15_frame=8,
        full_width17_frame_centers=256, restricted_width15_dot_rank=13,
        width15_radical_dimension=2, groups=groups,
        scope='Exact binary support subspaces of the two-block Pauli factorization. The width15 subspaces are degenerate (restricted dot rank13), so any helper theorem must handle those subspaces. Sharing a frame nominates batches; no helper schedule or routing cost is inferred.')


def section_rank(roots, fourth, blocks):
    baseline = e8.real_rank(roots, fourth)
    dimension = 8 * blocks
    trace_norm = Fraction(dimension + 2, 768)
    eigenvalue = 1 - 64 * trace_norm
    expected = 120 * blocks + 288 * blocks * (blocks - 1)
    require(eigenvalue != 0, 'Nondegenerate real coefficient form')
    return dict(real_kernel_rank=expected, pure_cubic_features=120 * blocks,
                mixed_cubic_features=288 * blocks * (blocks - 1),
                finite_rank_witnesses=baseline['finite_rank_witnesses'],
                trace_correction_eigenvalue=str(eigenvalue),
                signature=[expected - dimension, dimension],
                proof='Pure sectors and opposite relative signs separate independent cubic spaces, using the displayed finite rank witnesses 120,36,8. For the retained cubic feature matrix F, K=F(D-64 L L^T)F^T/3072. Since the shell norm is16 in doubled coordinates, u_i=sum_j u_i*u_j^2/16, and L^T D^-1 L=((8*blocks+2)/768)I. The nonzero displayed correction eigenvalue proves the exact real rank.')


def walsh_sections():
    hadamard = np.array([[1, 1], [1, -1]], dtype=np.int32)
    require(np.array_equal(hadamard @ hadamard, 2 * np.eye(2, dtype=np.int32)),
            'Relative-sign Walsh inverse is H/2')
    return dict(matrix=hadamard.tolist(), inverse_denominator=2,
        same_label_identity='p(a,b)=p(a,-b), since all lattice pairings agree modulo two.',
        three_block_sectors=3, ports_per_three_block_sector=29880,
        real_rank_per_three_block_sector=696,
        two_block_sectors=2, ports_per_two_block_sector=15480,
        real_rank_per_two_block_sector=408,
        pair_kernel_after_transform='For two AB ports in the odd-A sector, s_A*(s_A^2+3*s_B^2-4)/24, where s_A and s_B are ordinary root inner products.',
        proof='Every retained cubic or linear feature is odd in exactly one block. Transform each present relative-sign pair (a,b),(a,-b) by H on inputs and H/2 on outputs. This same-label similarity preserves the binary labels and unit diagonal, and separates the odd-block characters. Pure ports already have one character. At a fixed root a, the same-sector pair kernel is s_B^2/4, whose real rank is36 by the exact root-quadratic witness; this is not an eight-dimensional E8 frame replication.',
        scope='An exact free change of basis within equal-label ports. It does not by itself supply improved helper exits or a complete recursive word.')


def certify_sections():
    roots, fourth, full, profiles = e8.construct_shell()
    results = []
    for blocks in (2, 3):
        ids = np.flatnonzero((profiles & (7 ^ ((1 << blocks) - 1))) == 0)
        ports = full[ids, :8 * blocks]
        expected = 1080 * blocks + 28800 * (blocks * (blocks - 1) // 2)
        require(len(ports) == expected, 'Exact E8 section shell count')
        _, packed, fitting = e8.binary_labels(roots, ports)
        coordinate_factor = fano_factorization(ports, packed, blocks)
        frames = support_frames(ports, packed) if blocks == 2 else None
        results.append(dict(blocks=blocks, port_count=len(ports), fitting=fitting,
            real_rank=section_rank(roots, fourth, blocks),
            coordinate_factorization=coordinate_factor,
            operator_factorization=operator_factorization(ports, packed, blocks, coordinate_factor),
            shared_support_frames=frames))
    return dict(status='PASS_EXACT_E8_SECTION_FACTORIZATIONS', cases=results,
                relative_sign_walsh=walsh_sections())


if __name__ == '__main__':
    print(json.dumps(certify_sections(), indent=2, sort_keys=True))
