#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Close the other A8 simplex P112 frame orbit using pinned PR1304 lemmas.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
The exact predecessor implementation is retained unmodified and credited.
"""

import argparse
from collections import Counter, deque
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FANO_FRAME = (0, 85, 94, 99, 105, 108, 112, 113)
MATCHING_FRAME = (0, 15, 26, 33, 42, 89, 112, 119)
VENDOR_SHA256 = 'c8dff5ebf75511bf7c5e962a42189977ef5b20ce02e6f9734e4648e695ca3148'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def predecessor(path=HERE / 'vendor/pr1304_verify.py'):
    require(hashlib.sha256(path.read_bytes()).hexdigest() == VENDOR_SHA256,
            'PR1304 source bytes changed')
    spec = importlib.util.spec_from_file_location('pinned_pr1304', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frame_census(p, rows):
    """Enumerate all orthogonal eight-cliques, with increasing root indices."""
    adjacency = [sum(1 << j for j in range(i + 1, 120)
                     if p.dot(rows[i][1], rows[j][1]) == 0) for i in range(120)]
    frames = set()

    def visit(prefix, candidates):
        if len(prefix) == 8:
            frames.add(prefix)
            return
        while candidates:
            bit = candidates & -candidates
            candidates ^= bit
            i = bit.bit_length() - 1
            rest = candidates & adjacency[i]
            if len(prefix) + 1 + rest.bit_count() >= 8:
                visit(prefix + (i,), rest)

    visit((), (1 << 120) - 1)
    require(len(frames) == 2025, 'complete E8 frame census count')
    return frames


def coordinate_orbit(rows, start):
    """Adjacent transpositions generate S9; signs of pair roots are immaterial."""
    lookup = {}
    for i, (_, v) in enumerate(rows):
        lookup[v] = lookup[tuple(-x for x in v)] = i
    actions = []
    for k in range(8):
        action = []
        for _, v in rows:
            w = list(v)
            w[k], w[k + 1] = w[k + 1], w[k]
            action.append(lookup[tuple(w)])
        require(len(set(action)) == 120, 'coordinate action is a permutation')
        actions.append(action)
    orbit, queue = {start}, deque([start])
    while queue:
        f = queue.popleft()
        for action in actions:
            image = tuple(sorted(action[i] for i in f))
            if image not in orbit:
                orbit.add(image)
                queue.append(image)
    return orbit


def active_witness(p, live):
    require(live[0][1] == (3, 0, -3, 0, 0, 0, 0, 0, 0), 'witness root is e0-e2')
    coefficients = [tuple(2 * (x - v[2 if i == 0 else 0]) for x in v)
                    for i, (_, v) in enumerate(live)]
    p.check_identity(live, coefficients)
    costs = [p.rank(u for (u, _), c in zip(live, coefficients) if c[k])
             for k in range(9)]
    require(costs == [1, 8, 8, 9, 9, 9, 9, 9, 9], 'active witness cost vector')
    return coefficients, costs


def controls(p, rows, live, coefficients):
    names = []

    def rejects(name, action):
        try:
            action()
        except ValueError:
            names.append(name)
            return
        raise ValueError('control unexpectedly accepted: ' + name)

    bad = list(coefficients)
    bad[0] = (bad[0][0] + 1,) + bad[0][1:]
    rejects('coefficient_error', lambda: p.check_identity(live, bad))
    bad_term = [(0,) + c[1:] for c in coefficients]
    rejects('active_term_removed', lambda: p.check_identity(live, bad_term))
    labels = list(rows)
    labels[1] = (labels[1][0] ^ 1, labels[1][1])
    rejects('label_pairing_error', lambda: p.check_model(labels, FANO_FRAME))
    rejects('nonorthogonal_puncture',
            lambda: p.check_model(rows, (1,) + FANO_FRAME[1:]))
    words, unequal = p.tables(live)
    others, allowed, forced = p.compatibility_spaces(live, words, unequal, 0)
    configs, _ = p.plane_configurations(others, allowed)
    for hs, data in configs.items():
        relaxed = p.enumerate_configuration(others, hs, forced, words, unequal, False)[0]
        if relaxed > 10:
            checked = p.enumerate_configuration(others, hs, forced, words, unequal)[0]
            require(checked == 10, 'mutual compatibility control')
            names.append('mutual_compatibility_needed')
            control_plane = list(data['first_plane'])
            break
    else:
        raise ValueError('missing relaxation counterexample')
    # Exact real and imaginary parts of a generic complex kernel shift.
    p.check_identity(live, [tuple(2 * x for x in v) for _, v in live])
    require(all(sum(v) == 0 for _, v in live), 'imaginary all-ones kernel')
    require(p.rank(u for u, _ in live) == 9, 'generic complex shift cost 81')
    names.append('nonreal_shift_positive')
    return {'passed': names, 'relaxation_plane': control_plane,
            'relaxed_deficiency_bound': relaxed, 'checked_deficiency_bound': checked}


def compute():
    p = predecessor()
    rows = p.model()
    frames = frame_census(p, rows)
    matching = coordinate_orbit(rows, MATCHING_FRAME)
    fano = coordinate_orbit(rows, FANO_FRAME)
    require(len(matching) == 945 and len(fano) == 1080, 'coordinate orbit sizes')
    require(not matching & fano and matching | fano == frames, 'two orbits cover every frame')
    require(all(sum(i < 36 for i in f) == 4 for f in matching), 'matching root types')
    require(all(sum(i < 36 for i in f) == 1 for f in fano), 'Fano root types')
    orbit_results = []
    for name, frame, size in [('matching', MATCHING_FRAME, 945), ('fano', FANO_FRAME, 1080)]:
        live = p.check_model(rows, frame)
        words, unequal = p.tables(live)
        anchors = p.census(live, words, unequal)
        coefficients, costs = active_witness(p, live)
        result = {'name': name, 'frame': list(frame), 'orbit_size': size,
                  'anchors': anchors, 'active_witness_costs': costs,
                  'identity_entries': 112 * 112, 'column_label_ranks': [9] * 9}
        if name == 'fano':
            result['controls'] = controls(p, rows, live, coefficients)
        orbit_results.append(result)
    return json.loads(json.dumps({
        'schema_version': 1,
        'scope': 'Fixed A8 simplex, all orthogonal eight-frame punctures, all-pairs, separate copies',
        'frames': len(frames), 'frame_pair_root_counts': dict(Counter(sum(i < 36 for i in f) for f in frames)),
        'orbits': orbit_results, 'total_planes': 2 * 9 * 43435,
        'deficiency_upper_bound': 10, 'sharp_copy_cost': 71,
        'all_nine_terms_active': True, 'predecessor_verifier_sha256': VENDOR_SHA256}))


def compare_certificate(expected, actual):
    require(expected == actual, 'certificate differs from complete exact replay')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--certificate', type=Path, default=HERE / 'CERTIFICATE.json')
    args = parser.parse_args()
    expected = None if args.write else json.loads(args.certificate.read_text())
    result = compute()
    if args.write:
        args.certificate.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        compare_certificate(expected, result)
    print('PASS_A8_P112_ALL_FRAME_FLOOR frames=2025 orbits=945,1080 '
          'planes=781830 sharp_cost=71 active_terms=9')


if __name__ == '__main__':
    main()
