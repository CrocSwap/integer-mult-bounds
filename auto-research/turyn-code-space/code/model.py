"""Exact finite Turyn quotient and code-feature experiments."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT.parent
SOURCE = RESEARCH / 'leech-lattice'
sys.path.insert(0, str(SOURCE / 'code'))
from turyn_checks import construct_turyn, profile_labels, factor_odd_gram
from turyn_checks import encode_rows, insert_binary, rank_rows
from binary_labels import inverse


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_sources():
    source = json.loads((ROOT / 'sources/SOURCES.json').read_text())
    for name, digest in source['inherited_files'].items():
        require(hashlib.sha256((RESEARCH / name).read_bytes()).hexdigest() == digest,
                f'Inherited source hash: {name}')
    return source


def array_hash(value):
    array = np.ascontiguousarray(value)
    return hashlib.sha256(array.tobytes()).hexdigest()


def generate_geometry():
    vectors, profiles, geometry = construct_turyn()
    fitting = json.loads((SOURCE / 'evidence/TURYN-FITS.json').read_text())
    labels, _ = profile_labels(vectors, profiles, fitting['profile_fit_independent_rows'])
    classes, permutation, class_labels = [], [], []
    for high in range(3):
        ids = np.flatnonzero(profiles == high)
        low = [block for block in range(3) if block != high]
        keys = np.concatenate([vectors[ids, 8*b:8*b+8] for b in low], axis=1)
        _, assignment, counts = np.unique(keys, axis=0, return_inverse=True, return_counts=True)
        require(len(counts) == 960 and np.all(counts == 8), 'Eight-port glue fibers')
        for group in range(960):
            indices = ids[assignment == group]
            block = vectors[indices, 8*high:8*high+8]
            require(np.array_equal(block @ block.T, 16*np.eye(8, dtype=int)),
                    'Within-fiber orthogonal high lines')
            require(np.all(labels[indices] == labels[indices[0]]), 'Constant baseline fiber label')
            classes.append(indices)
            permutation.extend(map(int, indices))
            class_labels.append(labels[indices[0]])
    reordered = vectors[permutation]
    adjacency = np.zeros((2880, 2880), dtype=np.uint8)
    for start in range(0, 2880, 16):
        part = reordered[8*start:8*(start+16)]
        active = np.ones((len(part), len(reordered)), dtype=bool)
        for b in (0, 8, 16):
            active &= (part[:, b:b+8] @ reordered[:, b:b+8].T) != 0
        adjacency[start:start+16] = active.reshape(len(part)//8, 8, 2880, 8).any(axis=(1, 3))
    np.fill_diagonal(adjacency, 0)
    require(np.array_equal(adjacency, adjacency.T), 'Symmetric quotient')
    require(np.all(adjacency.sum(axis=1) == 1136), 'Quotient degree')
    require(int(adjacency.sum()) == 3271680, 'Quotient edge count')
    classes = np.array(classes, dtype=np.int32)
    class_labels = np.array(class_labels, dtype=np.uint8)
    return vectors, profiles, classes, adjacency, class_labels


def build_features(vectors, classes):
    fitting = json.loads((SOURCE / 'evidence/TURYN-FITS.json').read_text())
    selected = fitting['profile_fit_independent_rows'][0]
    base = vectors[selected, 8:16]
    gram = (1 ^ ((base @ base.T // 4) & 1)).astype(np.uint8)
    transform = (inverse(gram) @ factor_odd_gram(gram)) & 1
    pairs = []
    for index, indices in enumerate(classes):
        high = index // 960
        port = vectors[indices[0]]
        rows = []
        for low in range(3):
            if low != high:
                coordinate = (1 ^ ((port[8*low:8*low+8] @ base.T // 4) & 1)).astype(np.uint8)
                rows.append((coordinate @ transform) & 1)
        pairs.append(rows)
    pairs = np.array(pairs, dtype=np.uint8)
    z, q, p, receipt = [], [], [], []
    for high in range(3):
        full = pairs[960*high:960*(high+1)].reshape(960, 18)
        _, columns = rank_rows(encode_rows(full.T))
        affine = full[:, columns]
        require(affine.shape == (960, 13), 'Affine feature dimension')
        monomials = np.stack([affine[:, a]*affine[:, b] for a in range(13)
                             for b in range(a, 13)], axis=1)
        _, quadratic_columns = rank_rows(encode_rows(monomials.T))
        quadratic = monomials[:, quadratic_columns]
        require(quadratic.shape == (960, 77), 'Quadratic feature dimension')
        lows = [b for b in range(3) if b != high]
        p.append(pairs[960*high:960*(high+1), lows.index((high+1) % 3)])
        z.append(affine)
        q.append(quadratic)
        receipt.append(dict(profile=high, affine_columns=columns,
                            quadratic_monomial_columns=quadratic_columns,
                            affine_hash=array_hash(affine), quadratic_hash=array_hash(quadratic),
                            old_profile_label_hash=array_hash(p[-1])))
    return z, q, p, receipt


def neighboring_basis(features, adjacency, source):
    packed = encode_rows(features)
    for vertex in range(960):
        basis, selected = {}, []
        for target in np.flatnonzero(adjacency[source+vertex]):
            if insert_binary(basis, packed[int(target)]):
                selected.append(int(target))
        yield vertex, selected


def feature_neighbors(left_profile, right_profile, features, adjacency):
    block = adjacency[960*left_profile:960*(left_profile+1),
                      960*right_profile:960*(right_profile+1)]
    yield from neighboring_basis(features[right_profile], block, 0)


def symmetric_row(x, y, pairs):
    value = 0
    for bit, (a, b) in enumerate(pairs):
        coefficient = int(x[a]*y[b])
        if a != b:
            coefficient ^= int(x[b]*y[a])
        value |= coefficient << bit
    return value


def add_affine(basis, value, variables):
    mask = (1 << variables)-1
    while value & mask:
        pivot = (value & mask).bit_length()-1
        if pivot in basis:
            value ^= basis[pivot]
        else:
            basis[pivot] = value
            return True
    require(value >> variables == 0, 'Inconsistent affine fitting constraints')
    return False


def solve_affine(basis, freebits, variables, homogeneous=False):
    value = freebits
    for pivot in sorted(basis):
        row = basis[pivot]
        rhs = 0 if homogeneous else row >> variables
        value |= (rhs ^ ((row & value).bit_count() & 1)) << pivot
    return value


def affine_certificate(z, adjacency):
    result = {'cross': [], 'within': []}
    for first, second in ((0, 1), (0, 2), (1, 2)):
        basis, witnesses = {}, []
        for vertex, selected in feature_neighbors(first, second, z, adjacency):
            for target in selected:
                row = encode_rows(np.outer(z[first][vertex], z[second][target]).reshape(1, -1))[0]
                if insert_binary(basis, row):
                    witnesses.append([vertex, target])
            if len(basis) == 169:
                break
        require(len(basis) == 169, 'Full affine cross constraint rank')
        result['cross'].append(dict(profiles=[first, second], rank=169, variables=169,
                                    witness_edges=witnesses))
    pairs = [(a, b) for a in range(13) for b in range(a, 13)]
    for high in range(3):
        basis, witnesses = {}, []
        for vertex, selected in feature_neighbors(high, high, z, adjacency):
            rows = [(vertex, 1)] + [(target, 0) for target in selected]
            for target, rhs in rows:
                row = symmetric_row(z[high][vertex], z[high][target], pairs) | (rhs << 91)
                if add_affine(basis, row, 91):
                    witnesses.append([vertex, target, rhs])
        free = [bit for bit in range(91) if bit not in basis]
        require(len(basis) == 90 and len(free) == 1, 'Affine within-profile solution dimension')
        solutions, ranks = [], []
        for assignment in range(2):
            bits = solve_affine(basis, assignment << free[0], 91)
            matrix = np.zeros((13, 13), dtype=np.uint8)
            for bit, (a, b) in enumerate(pairs):
                matrix[a, b] = matrix[b, a] = (bits >> bit) & 1
            fitting = (z[high] @ matrix @ z[high].T) & 1
            block = adjacency[960*high:960*(high+1), 960*high:960*(high+1)]
            require(np.all(np.diag(fitting) == 1) and not (fitting & block).any(),
                    'Full affine solution diagonal and edge check')
            ranks.append(len(rank_rows(encode_rows(matrix))[0]))
            solutions.append(hex(bits))
        require(ranks == [9, 9], 'Affine solution ranks')
        result['within'].append(dict(profile=high, variables=91, constraint_rank=90,
            free_dimension=1, solution_ranks=ranks, solution_upper_triangles=solutions,
            witness_constraints=witnesses))
    return result


def validate_labels(labels, adjacency, maximum_dimension=None):
    labels = np.asarray(labels)
    require(labels.ndim == 2 and labels.shape[0] == 2880 and 0 < labels.shape[1] <= 512,
            'Candidate label shape')
    require(np.all((labels == 0) | (labels == 1)), 'Binary candidate entries')
    if maximum_dimension is not None:
        require(labels.shape[1] <= maximum_dimension, 'Candidate dimension target')
    labels = labels.astype(np.uint8)
    require(np.all(labels.sum(axis=1) % 2 == 1), 'Odd candidate diagonals')
    for start in range(0, 2880, 128):
        fitting = (labels[start:start+128] @ labels.T) & 1
        require(not (fitting & adjacency[start:start+128]).any(), 'Candidate active-edge fitting zeros')
    return dict(dimension=labels.shape[1], actual_binary_rank=len(rank_rows(encode_rows(labels))[0]),
                labels_sha256=array_hash(labels), unordered_active_edges_checked=1635840,
                scope='Labels constant on eight-port glue fibers; compatibility only, no scalar word or kappa')


def validate_parity_certificate(certificate, adjacency, vectors=None, classes=None):
    cliques = certificate['cliques']
    require(len(cliques) == 9, 'Nine-clique parity certificate')
    occurrences = Counter()
    for clique in cliques:
        require(len(clique) == len(set(clique)) == 24 and
                all(isinstance(v, int) and 0 <= v < 2880 for v in clique),
                'Parity clique vertices')
        require(np.array_equal(adjacency[np.ix_(clique, clique)],
                               1-np.eye(24, dtype=np.uint8)), 'Parity clique edges')
        occurrences.update(clique)
    require(len(occurrences) == 60 and Counter(occurrences.values()) == {2: 36, 6: 24},
            'Even vertex coverage in nine-clique certificate')
    require(all(count % 2 == 0 for count in occurrences.values()), 'Parity coverage')
    result = dict(cliques=9, clique_size=24, distinct_vertices=60,
                incidence_multiplicities={'2': 36, '6': 24}, ordered_edges_checked=4968,
                minimum_binary_fitting_rank=27,
                proof='r <= 9(r-24d), hence r/d >= 27 for every block width d')
    if vectors is not None:
        edges = sorted({tuple(sorted((v, w))) for clique in cliques
                        for v in clique for w in clique if v != w})
        require(len(edges) == 1176, 'Distinct parity-certificate edges')
        witnesses = []
        for first, second in edges:
            left, right = vectors[classes[first]], vectors[classes[second]]
            dots = [left[:, b:b+8] @ right[:, b:b+8].T for b in (0, 8, 16)]
            active = np.logical_and.reduce([value != 0 for value in dots])
            choices = np.argwhere(active)
            require(len(choices) > 0, 'Raw-coordinate parity edge witness')
            a, b = map(int, choices[0])
            witnesses.append([first, second, int(classes[first, a]), int(classes[second, b]),
                              *[int(value[a, b]) for value in dots]])
        result['distinct_edges_checked_from_raw_ports'] = len(edges)
        result['raw_edge_witnesses_hash'] = array_hash(np.array(witnesses, dtype=np.int32))
    return result


def validate_lift_scope(vectors, classes, parity):
    specification = json.loads((ROOT / 'evidence/LIFT-SCOPE.json').read_text())
    source = specification['class']
    clique = parity['cliques'][specification['clique_index']]
    require(source in clique, 'Lift source belongs to the recorded clique')
    common = set(range(8))
    for constraint in specification['constraints']:
        target = constraint['neighbor']
        require(target in clique, 'Lift target belongs to the same recorded clique')
        left, right = vectors[classes[source]], vectors[classes[target]]
        active = np.logical_and.reduce([(left[:, b:b+8] @ right[:, b:b+8].T) != 0
                                        for b in (0, 8, 16)])
        allowed = np.flatnonzero(active.any(axis=1)).tolist()
        require(allowed == constraint['allowed_source_choices'], 'Lift source choices')
        common.intersection_update(allowed)
    require(not common, 'Fixed parity certificate cannot choose one port per glue class')
    return specification


def candidate_labels(candidate, q, p):
    if candidate.get('kind') == 'explicit_quotient_labels':
        return np.asarray(candidate['labels'])
    require(candidate.get('kind') == 'quadratic_radical', 'Supported candidate kind')
    maps = candidate['coefficient_maps']
    require(len(maps) == 3, 'Three quadratic radical maps')
    f = []
    for high in range(3):
        matrix = np.asarray(maps[high])
        require(matrix.shape == (77, 8) and np.all((matrix == 0) | (matrix == 1)),
                'Quadratic radical coefficient dimensions')
        f.append((q[high] @ matrix.astype(np.uint8)) & 1)
    raw = np.zeros((2880, 25), dtype=np.uint8)
    for high in range(3):
        raw[high*960:(high+1)*960, :9] = p[high]
    raw[:960, 9:17] = f[0]
    raw[960:1920, 17:25] = f[1]
    raw[1920:, 9:17] = raw[1920:, 17:25] = f[2]
    isometry = json.loads((ROOT / 'evidence/HYPERBOLIC-ISOMETRY.json').read_text())
    change = np.asarray(isometry['Q'], dtype=np.uint8)
    gram = np.zeros((25, 25), dtype=np.uint8)
    gram[:9, :9] = np.eye(9, dtype=np.uint8)
    gram[9:17, 17:25] = gram[17:25, 9:17] = np.eye(8, dtype=np.uint8)
    require(change.shape == (25, 25) and np.array_equal((change @ change.T) & 1, gram),
            'Hyperbolic-to-standard-dot isometry')
    require(isometry['J'] == gram.tolist(), 'Serialized hyperbolic Gram')
    return (raw @ change) & 1


def negative_controls(labels, adjacency, q, p):
    rejected = []
    variants = [('zero_diagonal', np.zeros_like(labels)),
                ('all_pairs_one', np.ones((2880, 1), dtype=np.uint8))]
    edge = np.flatnonzero(adjacency[0])[0]
    copied = labels.copy()
    copied[edge] = copied[0]
    variants.append(('active_pair_same_odd_label', copied))
    for name, altered in variants:
        try:
            validate_labels(altered, adjacency)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError(f'Corruption accepted: {name}')
    zero_radical = dict(kind='quadratic_radical', coefficient_maps=[np.zeros((77, 8), dtype=int).tolist()]*3)
    try:
        validate_labels(candidate_labels(zero_radical, q, p), adjacency, 25)
    except ValueError:
        rejected.append('zero_quadratic_radical')
    else:
        raise ValueError('Corruption accepted: zero_quadratic_radical')
    parity = json.loads((ROOT / 'evidence/PARITY-CERTIFICATE.json').read_text())
    for name, altered in [('missing_parity_clique', dict(cliques=parity['cliques'][:-1])),
                          ('duplicate_parity_vertex', json.loads(json.dumps(parity)))]:
        if name == 'duplicate_parity_vertex':
            altered['cliques'][0][0] = altered['cliques'][0][1]
        try:
            validate_parity_certificate(altered, adjacency)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError(f'Corruption accepted: {name}')
    return rejected


def build(output=None):
    check_sources()
    vectors, profiles, classes, adjacency, labels = generate_geometry()
    z, q, p, features = build_features(vectors, classes)
    clique = json.loads((ROOT / 'evidence/CLIQUE.json').read_text())
    require(len(clique) == len(set(clique)) == 24, 'Clique size')
    require(np.array_equal(adjacency[np.ix_(clique, clique)], 1-np.eye(24, dtype=np.uint8)),
            'Quotient clique edges')
    affine = affine_certificate(z, adjacency)
    parity = json.loads((ROOT / 'evidence/PARITY-CERTIFICATE.json').read_text())
    parity_receipt = validate_parity_certificate(parity, adjacency, vectors, classes)
    lift_scope = validate_lift_scope(vectors, classes, parity)
    biclique = json.loads((ROOT / 'evidence/BICLIQUE.json').read_text())
    left, right = biclique['left'], biclique['right']
    require(len(left) == len(set(left)) == len(right) == len(set(right)) == 9,
            'Biclique side sizes')
    require(np.all(adjacency[np.ix_(left, [960+x for x in right])] == 1),
            'All biclique cross edges')
    require(len(rank_rows(encode_rows(p[0][left]))[0]) ==
            len(rank_rows(encode_rows(p[1][right]))[0]) == 9,
            'Biclique old-label ranks')
    require(len(rank_rows(encode_rows((p[0][left] @ p[1][right].T) & 1))[0]) == 9,
            'Biclique prescribed cross rank')
    baseline = validate_labels(labels, adjacency)
    receipt = dict(status='PASS_EXACT_CODE_SPACE_MODEL', geometry=dict(ports=len(vectors),
        classes=len(classes), fiber_size=8, quotient_degree=1136, unordered_edges=1635840,
        port_hash=array_hash(vectors.astype(np.int16)), class_hash=array_hash(classes),
        adjacency_hash=array_hash(adjacency)), features=features, baseline=baseline,
        affine_fit_rank=27, clique_lower_bound=24, parity_certificate=parity_receipt,
        lift_scope=lift_scope,
        fixed_profile_radical_lower_bound=9,
        negative_controls=negative_controls(labels, adjacency, q, p))
    state = dict(vectors=vectors, profiles=profiles, classes=classes, adjacency=adjacency,
                 labels=labels, z=z, q=q, p=p)
    if output is not None:
        output.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(output / 'model.npz', vectors=vectors, profiles=profiles,
            classes=classes, adjacency=adjacency, labels=labels,
            **{f'{key}{i}': state[key][i] for key in ('z', 'q', 'p') for i in range(3)})
        (output / 'MODEL.json').write_text(json.dumps(receipt, indent=2)+'\n')
        (output / 'AFFINE.json').write_text(json.dumps(affine, indent=2)+'\n')
    return state, receipt, affine
