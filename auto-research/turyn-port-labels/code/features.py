"""Finite rank-27 certificate for high-line indicator and glue features."""
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np

from geometry import ROOT, RESEARCH, SOURCE, require, load
from geometry import encode_rows, insert_binary, rank_rows, inverse, profile_labels


def nullspace(basis, dimension):
    rows = []
    for free in range(dimension):
        if free in basis:
            continue
        value = 1 << free
        for pivot in sorted(basis):
            if (value & basis[pivot]).bit_count() & 1:
                value |= 1 << pivot
        rows.append(value)
    return rows


def binary_array(rows, dimension):
    return np.array([[(value >> bit) & 1 for bit in range(dimension)]
                     for value in rows], dtype=np.uint8).reshape(len(rows), dimension)


def make_features(vectors, profiles):
    path = RESEARCH/'turyn-code-space/code/model.py'
    spec = importlib.util.spec_from_file_location('frozen_turyn_glue_model', path)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    ids, classes = [], []
    for high in range(3):
        selected = np.flatnonzero(profiles == high)
        ids.append(selected)
        lows = [b for b in range(3) if b != high]
        keys = np.concatenate([vectors[selected, 8*b:8*b+8] for b in lows], axis=1)
        _, assignment, counts = np.unique(keys, axis=0, return_inverse=True, return_counts=True)
        require(len(counts) == 960 and np.all(counts == 8), 'Eight-port feature fibers')
        classes.extend(selected[assignment == group] for group in range(960))
    classes = np.array(classes, dtype=np.int32)
    affine, _, _, _ = model.build_features(vectors, classes)
    features, local_classes, hashes = [], [], []
    for high in range(3):
        lookup = np.full(len(vectors), -1, dtype=np.int32)
        lookup[ids[high]] = np.arange(7680)
        local = lookup[classes[960*high:960*(high+1)]]
        local_classes.append(local)
        indicator = np.zeros((7680, 104), dtype=np.uint8)
        monomials = np.stack([affine[high][:, a]*affine[high][:, b]
                             for a in range(13) for b in range(a, 13)], axis=1)
        quadratic = np.zeros((7680, 91), dtype=np.uint8)
        for choice in range(8):
            indicator[local[:, choice], 13*choice:13*(choice+1)] = affine[high]
            quadratic[local[:, choice]] = monomials
        combined = np.concatenate((indicator, quadratic), axis=1)
        _, columns = rank_rows(encode_rows(combined.T))
        feature = np.ascontiguousarray(combined[:, columns])
        require(feature.shape == (7680, 168), 'Combined feature dimension')
        features.append(feature)
        hashes.append(hashlib.sha256(feature.tobytes()).hexdigest())
    return features, ids, classes, local_classes, hashes


def require_edges(vectors, ids_left, ids_right, source, targets):
    require(isinstance(source, int) and 0 <= source < 7680, 'Witness source range')
    require(all(isinstance(t, int) and 0 <= t < 7680 for t in targets), 'Witness target range')
    source_global = int(ids_left[source])
    targets_global = ids_right[targets]
    require(np.all(targets_global != source_global), 'Witness is off-diagonal')
    for block in (0, 8, 16):
        values = vectors[targets_global, block:block+8] @ vectors[source_global, block:block+8]
        require(np.all(values != 0), 'Witness is an active tensor edge')


def initial_parameters(vectors, features, ids, left, right, fixture):
    qleft, qright = features[left], features[right]
    sources = fixture['source_basis']
    require(len(sources) == len(set(sources)) == 168, 'Source basis cardinality')
    require(all(isinstance(s, int) and 0 <= s < 7680 for s in sources), 'Source basis indices')
    source_matrix = qleft[sources]
    source_inverse = inverse(source_matrix)
    require(len(fixture['neighbor_bases']) == 168, 'One neighbor basis per source')
    rows, offsets, counts = [], [0], []
    for source, neighbors in zip(sources, fixture['neighbor_bases']):
        require(len(neighbors) == len(set(neighbors)), 'Distinct neighbor witnesses')
        require_edges(vectors, ids[left], ids[right], source, neighbors)
        basis, selected = rank_rows(encode_rows(qright[neighbors]))
        require(len(selected) == len(neighbors), 'Independent neighbor witnesses')
        directions = nullspace(basis, 168)
        counts.append(len(directions))
        rows.extend(directions)
        offsets.append(len(rows))
    directions = binary_array(rows, 168)
    return source_matrix, source_inverse, directions, offsets, counts


def symmetry_constraints(source_matrix, directions, offsets):
    transformed = (directions @ source_matrix.T) & 1
    coefficient = []
    for first in range(168):
        coefficient.append([sum(int(transformed[row, second]) << row
                                for row in range(offsets[first], offsets[first+1]))
                            for second in range(168)])
    basis = {}
    for first in range(168):
        insert_binary(basis, coefficient[first][first])
        for second in range(first):
            insert_binary(basis, coefficient[first][second] ^ coefficient[second][first])
    return basis


def add_edge_constraints(vectors, features, ids, left, right, fixture,
                         source_inverse, directions, offsets, basis):
    masks, targets = {}, {}
    segments = [((1 << (end-start))-1) << start
                for start, end in zip(offsets, offsets[1:])]
    for source, target in fixture['extra_edges']:
        require_edges(vectors, ids[left], ids[right], source, [target])
        if source not in masks:
            coordinates = (features[left][source] @ source_inverse) & 1
            masks[source] = sum(segments[i] for i in np.flatnonzero(coordinates))
        if target not in targets:
            values = (directions @ features[right][target]) & 1
            targets[target] = encode_rows(values.reshape(1, -1))[0]
        require(insert_binary(basis, masks[source] & targets[target]),
                'Independent additional witness constraint')


def project_family(source_inverse, directions, offsets, basis, left_values, right_values):
    parameters = binary_array(nullspace(basis, len(directions)), len(directions))
    target_values = (directions @ right_values.T) & 1
    partial = np.zeros((len(parameters), 168, len(right_values)), dtype=np.uint8)
    for index in range(168):
        start, end = offsets[index:index+2]
        partial[:, index, :] = (parameters[:, start:end] @ target_values[start:end]) & 1
    projected = ((left_values @ source_inverse) @ partial) & 1
    return projected, len(parameters)


def certify_projection(vectors, profiles):
    with gzip.open(ROOT/'evidence/FEATURE-PROJECTION-WITNESSES.json.gz', 'rt') as file:
        fixture = json.load(file)
    features, ids, classes, local_classes, hashes = make_features(vectors, profiles)
    require(hashes == fixture['feature_hashes'], 'Pinned combined feature arrays')
    parity = json.loads((RESEARCH/'turyn-code-space/evidence/PARITY-CERTIFICATE.json').read_text())
    cliques = parity['cliques']
    require(len(cliques) == 9 and all(len(c) == len(set(c)) == 24 for c in cliques),
            'Nine distinct-vertex 24-cliques')
    occurrences = Counter(vertex for clique in cliques for vertex in clique)
    require(len(occurrences) == 60 and Counter(occurrences.values()) == {2: 36, 6: 24},
            'Even incidence parity cover')
    selected = [sorted(v-960*h for v in occurrences if v//960 == h) for h in range(3)]
    require(all(len(values) == 20 for values in selected), 'Twenty projected vertices per profile')
    lookup = [{v: i for i, v in enumerate(values)} for values in selected]
    values = [features[h][local_classes[h][selected[h], 0]] for h in range(3)]
    masks = {}
    for first in range(3):
        for second in range(first, 3):
            mask = np.zeros((20, 20), dtype=bool)
            for clique in cliques:
                a = [lookup[first][v-960*first] for v in clique if v//960 == first]
                b = [lookup[second][v-960*second] for v in clique if v//960 == second]
                mask[np.ix_(a, b)] = True
            if first == second:
                np.fill_diagonal(mask, False)
            masks[first, second] = mask
    fitting = json.loads((SOURCE/'evidence/TURYN-FITS.json').read_text())
    old, _ = profile_labels(vectors, profiles, fitting['profile_fit_independent_rows'])
    for high in range(3):
        sources = fixture['blocks'][str(high)+str(high)]['source_basis']
        coefficients = (inverse(features[high][sources]) @ old[ids[high][sources]]) & 1
        require(np.array_equal((features[high] @ coefficients) & 1, old[ids[high]]),
                'Known fitting offset belongs to combined feature family')
    for key, data in fixture['blocks'].items():
        left, right = map(int, key)
        for source, targets in zip(data['source_basis'], data['neighbor_bases']):
            require(not ((old[ids[right][targets]] @ old[ids[left][source]]) & 1).any(),
                    'Known offset satisfies every initial edge witness')
        for source, target in data['extra_edges']:
            require(int(old[ids[left][source]] @ old[ids[right][target]]) % 2 == 0,
                    'Known offset satisfies every additional edge witness')
    base = [old[classes[960*h+np.array(selected[h]), 0]] for h in range(3)]
    for first, second in masks:
        gram = (base[first] @ base[second].T) & 1
        require(not gram[masks[first, second]].any(), 'Known projected offset has clique zeros')
        if first == second:
            require(np.all(np.diag(gram) == 1), 'Known projected offset has odd diagonal')
    receipts = []
    for left, right in ((0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)):
        data = fixture['blocks'][str(left)+str(right)]
        source_matrix, source_inverse, directions, offsets, counts = initial_parameters(
            vectors, features, ids, left, right, data)
        basis = symmetry_constraints(source_matrix, directions, offsets) if left == right else {}
        initial_rank = len(basis)
        add_edge_constraints(vectors, features, ids, left, right, data,
                             source_inverse, directions, offsets, basis)
        projected, dimension = project_family(source_inverse, directions, offsets,
                                              basis, values[left], values[right])
        require(dimension == (399 if left == right else 46), 'Certified finite family dimension')
        require(not projected[:, masks[left, right]].any(),
                'Every homogeneous direction preserves all projected clique zeros')
        if left == right:
            require(not np.diagonal(projected, axis1=1, axis2=2).any(),
                    'Every homogeneous direction preserves projected diagonal')
        receipts.append(dict(profiles=[left, right], feature_dimension=168,
            source_basis_size=168, neighbor_witnesses=sum(map(len, data['neighbor_bases'])),
            parameter_count=len(directions), initial_constraint_rank=initial_rank,
            additional_independent_edges=len(data['extra_edges']),
            remaining_dimension=dimension,
            projected_direction_hash=hashlib.sha256(projected.tobytes()).hexdigest(),
            projected_clique_zeros=True))
    return dict(status='PASS_COMBINED_168_PROJECTION_CERTIFICATE',
        feature_definition='Eight high-line indicators times 13 affine glue features, plus all quadratic glue features; span dimension 168 per profile',
        feature_hashes=hashes, blocks=receipts, projected_vertices=60,
        parity_cliques=9, parity_clique_size=24, minimum_binary_fitting_rank=27,
        proof='Restriction cannot increase rank and produces nine 24-cliques with even incidence; h<=9(h-24), hence h>=27',
        scope='Symmetric binary fitting matrices / standard-dot labels from profile-dependent linear maps of this combined 168 feature family; unrestricted nonlinear high-line-dependent labels remain outside the certificate')
