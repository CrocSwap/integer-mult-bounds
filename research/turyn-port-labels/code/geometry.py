"""Finite raw-port witnesses; no full pairwise graph construction."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT.parent
SOURCE = RESEARCH / 'leech-lattice'
sys.path.insert(0, str(SOURCE/'code'))
from turyn_checks import construct_turyn, profile_labels, encode_rows, rank_rows, insert_binary
from binary_labels import inverse


def require(value, message):
    if not value:
        raise ValueError(message)


def load(name):
    return json.loads((ROOT/'evidence'/name).read_text())


def source_check():
    sources = json.loads((ROOT/'sources/SOURCES.json').read_text())
    for name, digest in sources['inherited_files'].items():
        require(hashlib.sha256((RESEARCH/name).read_bytes()).hexdigest() == digest,
                f'Pinned inherited file: {name}')
    for key in ('frontier', 'accounting_source'):
        specification = sources[key]
        pr = json.loads((ROOT/'sources'/f"PR{specification['pr']}.json").read_text())
        require(pr['headRefOid'] == specification['head'], f'Pinned PR {specification["pr"]} head')
    require(sources['frontier']['declared_kappa'] in
            json.loads((ROOT/'sources/PR592.json').read_text())['title'], 'Pinned frontier value')
    retained = sources['accounting_source']['retained_file']
    require(hashlib.sha256((ROOT/retained['local_path']).read_bytes()).hexdigest() == retained['sha256'],
            'Pinned upstream accounting source')
    return sources


def dots(vectors, source, target):
    return [int(vectors[source, b:b+8] @ vectors[target, b:b+8]) for b in (0, 8, 16)]


def sign_certificate(vectors, certificate, directed):
    equations = []
    for edge in certificate['edges']:
        if directed:
            source, target = edge['source'], edge['target']
            names = [('source', source, b) for b in range(3)] + [('target', target, b) for b in range(3)]
        else:
            source, target = edge['ports']
            names = [('port', source, b) for b in range(3)] + [('port', target, b) for b in range(3)]
        actual = dots(vectors, source, target)
        require(actual == edge['raw_block_dots'] and all(actual), 'Sign-switch active raw edge')
        require(all(value % 4 == 0 for value in actual) and sum(actual) % 8 == 0,
                'Sign-switch integer normalization')
        alpha = [(value//4) % 2 for value in actual]
        rhs = 1 ^ ((sum(actual)//8) % 2)
        require(alpha == edge['alpha'] and rhs == edge['lambda'], 'Sign-switch parity equation')
        equations.append(({name for name, value in zip(names, alpha+alpha) if value}, rhs))
    lhs, rhs = set(), 0
    for names, value in equations:
        lhs.symmetric_difference_update(names)
        rhs ^= value
    require(not lhs and rhs == 1, 'Sign-switch equations sum to 0=1')
    return dict(edges=len(equations), contradiction='0=1', directed=directed)


def symmetric_bits(x, y):
    a, b = np.triu_indices(25)
    row = (x[a]*y[b]) ^ (x[b]*y[a])
    diagonal = a == b
    row[diagonal] = x[a[diagonal]]*y[b[diagonal]]
    return encode_rows(row.reshape(1, -1))[0]


def add_affine(basis, value):
    mask = (1 << 325)-1
    while value & mask:
        pivot = (value & mask).bit_length()-1
        if pivot in basis:
            value ^= basis[pivot]
        else:
            basis[pivot] = value
            return
    require(value >> 325 == 0, 'Consistent within-profile witness equations')


def affine_certificate(vectors, profiles, features, cross, within):
    require(set(cross) == {'01', '02', '12'} and set(within) == {'0', '1', '2'},
            'All three cross blocks and three within-profile blocks are present')
    cross_receipts = []
    for key, certificate in sorted(cross.items()):
        first, second = map(int, key)
        basis = {}
        require(len(certificate['witness_edges']) == 625, 'Cross witness count')
        for source, target in certificate['witness_edges']:
            require(profiles[source] == first and profiles[target] == second,
                    'Cross witness profiles')
            require(source != target and all(dots(vectors, source, target)), 'Cross witness active edge')
            row = encode_rows(np.outer(features[source], features[target]).reshape(1, -1))[0]
            require(insert_binary(basis, row), 'Independent cross witness')
        require(len(basis) == 625, 'Full cross-Gram constraint rank')
        cross_receipts.append(dict(profiles=[first, second], constraint_rank=625))
    within_receipts = []
    for key, certificate in sorted(within.items()):
        high = int(key)
        basis = {}
        require(len(certificate['witness_constraints']) == 324, 'Within witness count')
        for source, target, rhs in certificate['witness_constraints']:
            require(profiles[source] == high and profiles[target] == high, 'Within witness profiles')
            require(rhs in (0, 1), 'Binary witness RHS')
            if rhs:
                require(source == target, 'Diagonal fitting witness')
            else:
                require(source != target and all(dots(vectors, source, target)), 'Within active-edge witness')
            add_affine(basis, symmetric_bits(features[source], features[target]) | (rhs << 325))
        require(len(basis) == 324, 'Within witness rank')
        free = [p for p in range(325) if p not in basis]
        require(len(free) == 1, 'Within witness nullity')
        ranks, solutions = [], []
        a, b = np.triu_indices(25)
        for value in (0, 1 << free[0]):
            for pivot in sorted(basis):
                row = basis[pivot]
                value |= ((row >> 325) ^ ((value & row).bit_count() & 1)) << pivot
            matrix = np.zeros((25, 25), dtype=np.uint8)
            upper = np.array([(value >> bit) & 1 for bit in range(325)], dtype=np.uint8)
            matrix[a, b] = matrix[b, a] = upper
            for source, target, rhs in certificate['witness_constraints']:
                require(int(features[source] @ matrix @ features[target]) % 2 == rhs,
                        'Independent within witness solution replay')
            ranks.append(len(rank_rows(encode_rows(matrix))[0]))
            solutions.append(hex(value))
        require(ranks == [9, 9], 'Every within witness solution has rank 9')
        within_receipts.append(dict(profile=high, constraint_rank=324,
            remaining_dimension=1, solution_ranks=ranks, solution_upper_triangles=solutions))
    return dict(cross=cross_receipts, within=within_receipts,
        minimum_rank_in_this_feature_family=27,
        scope='Symmetric fitting matrices from profile-dependent linear maps of the full 25 Leech affine coordinates; unrestricted nonlinear full-port labels remain outside this certificate')


def features_from_ports(vectors, profiles):
    specification = load('FEATURES.json')
    indices = specification['lattice_basis_indices']
    require(len(indices) == len(set(indices)) == 24, 'Twenty-four distinct lattice basis ports')
    require(vectors[indices].tolist() == specification['lattice_basis_vectors'], 'Exact lattice basis vectors')
    pairings = vectors @ vectors[indices].T
    require(not (pairings % 8).any(), 'Integral full-port lattice pairings')
    binary_gram = ((pairings[indices]//8) & 1).astype(np.uint8)
    require(len(rank_rows(encode_rows(binary_gram))[0]) == 24, 'Nondegenerate lattice coordinate basis')
    features = np.concatenate((np.ones((len(vectors), 1), dtype=np.uint8),
                               ((pairings//8) & 1).astype(np.uint8)), axis=1)
    fitting = json.loads((SOURCE/'evidence/TURYN-FITS.json').read_text())
    old, _ = profile_labels(vectors, profiles, fitting['profile_fit_independent_rows'])
    ranks = []
    for high in range(3):
        indices = np.flatnonzero(profiles == high)
        z = features[indices]
        p = old[indices, 9*high:9*(high+1)]
        _, rows = rank_rows(encode_rows(z))
        require(len(rows) == 25, 'Full-port feature rank per profile')
        change = (inverse(z[rows]) @ p[rows]) & 1
        require(np.array_equal((z @ change) & 1, p), 'Old profile labels contained in full feature span')
        ranks.append(25)
    return features, dict(profile_ranks=ranks, features_sha256=hashlib.sha256(features.tobytes()).hexdigest())


def negative_controls(vectors, profiles, features, cross, within):
    rejected = []
    sign = load('SIGN-ASYMMETRIC.json')
    sign['edges'][0]['lambda'] ^= 1
    variants = [('sign_rhs', lambda: sign_certificate(vectors, sign, True))]
    altered = json.loads(json.dumps(cross))
    altered['01']['witness_edges'][0] = altered['01']['witness_edges'][1]
    variants.append(('dependent_cross_witness', lambda: affine_certificate(vectors, profiles, features, altered, within)))
    even = json.loads(json.dumps(within))
    even['0']['witness_constraints'][0][2] = 0
    variants.append(('diagonal_as_edge', lambda: affine_certificate(vectors, profiles, features, cross, even)))
    for name, action in variants:
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError(f'Corruption accepted: {name}')
    return rejected


def run():
    from support import certify_support
    from profile import certify_profile
    from features import certify_projection
    source_check()
    vectors, profiles, _ = construct_turyn()
    features, feature_receipt = features_from_ports(vectors, profiles)
    cross, within = load('AFFINE-CROSS.json'), load('AFFINE-WITHIN.json')
    projection = certify_projection(vectors, profiles)
    require(projection == load('FEATURE-PROJECTION.json'), 'Exact combined-feature projection receipt')
    result = dict(status='PASS_FINITE_FULL_PORT_LABEL_CERTIFICATES',
        ports=len(vectors), feature_receipt=feature_receipt,
        symmetric_sign=sign_certificate(vectors, load('SIGN-SYMMETRIC.json'), False),
        asymmetric_sign=sign_certificate(vectors, load('SIGN-ASYMMETRIC.json'), True),
        affine=affine_certificate(vectors, profiles, features, cross, within),
        combined_features=projection,
        fixed_label_encoder_support=certify_support(vectors, profiles),
        arbitrary_profile_h8=certify_profile(vectors, profiles),
        negative_controls=negative_controls(vectors, profiles, features, cross, within))
    return result
