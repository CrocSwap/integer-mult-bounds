#!/usr/bin/env python3
"""Exact source contacts and whole-job positive endpoints, with no old imports."""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
import hashlib
import json

from gauss_trace import Quadratic, adjoint, equal, require
from native_check import transpose


DIMENSION = 265
AXES = tuple(1 << i for i in range(DIMENSION))


def terms(entries):
    coefficients = Counter()
    for axis, value in entries:
        require(type(axis) is int and 0 < axis < 1 << DIMENSION and type(value) is int, 'spectral term domain')
        coefficients[axis] += value
    return tuple(sorted((axis, value % 4) for axis, value in coefficients.items() if value % 4))


@lru_cache(maxsize=None)
def phase(entries):
    polynomial = Quadratic.zero(DIMENSION)
    for axis, coefficient in entries:
        polynomial.add_affine(coefficient, (axis, 0))
    return tuple(polynomial.linear), frozenset(polynomial.pairs), polynomial.constant


def apply(columns, value):
    result = 0
    while value:
        low = value & -value
        result ^= columns[low.bit_length()-1]
        value ^= low
    return result


def positive(vectors):
    return terms((axis, 1) for axis in vectors)


def stage_terms(stage, q):
    require(type(stage) is int and 0 <= stage <= 32, 'controller stage domain')
    return terms([(axis, 1) for axis in AXES[:9]]+[(q, -1)]) if stage == 0 else positive(AXES[9+8*(stage-1):9+8*stage])


def orthogonal_base(q, recipe):
    basis = tuple(recipe['idle_children'][0]['orthogonal_axes'][:8])
    complete = (q,)+basis
    require(len(set(complete)) == 9 and all(type(v) is int and 0 < v < 512 for v in complete),
            'complete nine-axis port basis')
    require(all((a & b).bit_count() % 2 == int(i == j)
                for i, a in enumerate(complete) for j, b in enumerate(complete)), 'orthonormal port basis')
    return basis


def route(stage, q, basis):
    """Swap eight orthonormal pairs; fix their orthogonal complement."""
    if stage == 0:
        return AXES
    fresh = AXES[9+8*(stage-1):9+8*stage]
    differences = tuple(a ^ b for a, b in zip(basis, fresh, strict=True))
    columns = tuple(axis ^ apply(differences, sum(((axis & v).bit_count() % 2) << j
                                                for j, v in enumerate(differences))) for axis in AXES)
    require(all(apply(columns, a) == b and apply(columns, b) == a
                for a, b in zip(basis, fresh, strict=True)), 'actual eight swaps')
    require(apply(columns, q) == q and all(apply(columns, columns[j]) == AXES[j] for j in range(DIMENSION)),
            'complete involutive route and central port')
    # The checked two orthonormal families are disjoint. Their eight swaps and
    # fixed orthogonal complement prove orthogonality, without a 265^2 replay.
    return columns


def contact(before, after, columns):
    moved = terms((apply(columns, axis), coefficient) for axis, coefficient in before)
    left, right = phase(moved), phase(after)
    require(left[1:] == right[1:], 'contact full mixed and constant phase')
    difference = tuple((b-a) % 4 for a, b in zip(left[0], right[0], strict=True))
    require(all(value in (0, 2) for value in difference), 'contact even linear residual')
    translation = sum((value//2) << j for j, value in enumerate(difference))
    correction = [(translation, 2)] if translation else []
    require(phase(terms(list(moved)+correction)) == right, 'complete forward contact')
    inverse = apply(columns, translation)
    backward = [(apply(columns, axis), coefficient) for axis, coefficient in after]
    if inverse:
        backward.append((inverse, 2))
    require(phase(terms(backward)) == phase(before), 'complete inverse contact')
    return {'translation': translation, 'inverse_translation': inverse}


def transformed_path(local, entry, exit_, columns):
    """Exit * native * entry, including both actual address translations."""
    translation = exit_['translation'] ^ apply(columns, entry['translation'])
    entries = [(apply(columns, axis), coefficient) for axis, coefficient in local]
    if translation:
        entries.append((translation, 2))
    return phase(terms(entries))


def complete_positive_basis(base, active, retained):
    """Return a complete coordinate map, including all spectator columns."""
    require(len(base) == 9 and len(set(active)) == len(active)
            and all(type(j) is int and 0 <= j < DIMENSION for j in active), 'positive coordinate selection')
    require(all((a & b).bit_count() % 2 == int(i == j)
                for i, a in enumerate(base) for j, b in enumerate(base)), 'complete orthogonal local basis')
    require(set(active) <= set(retained), 'positive job uses retained source rows')
    order = (tuple(active)+tuple(j for j in retained if j not in set(active))
             +tuple(j for j in range(DIMENSION) if j not in set(retained)))
    require(sorted(order) == list(range(DIMENSION)), 'all spectator coordinates retained')
    columns = tuple(base)+AXES[9:]
    return tuple(columns[j] for j in order)


def check_caller(word, controller, phase_source, source_result):
    recipes = {entry['q']: entry for entry in phase_source['recipes']}
    require(len(recipes) == len(phase_source['recipes']) and set(word['ports']) <= set(recipes), 'original source port data')
    bases = {q: orthogonal_base(q, recipes[q]) for q in word['ports']}
    local_stages = sorted(event[1] for event in controller['physical_events'] if event[0] == 'LOCAL')
    require(local_stages == [0]+list(range(1, 32, 2))+[32], 'all selected actual stages')
    retained = tuple(range(9))+tuple(j for stage in local_stages if stage
                                   for j in range(9+8*(stage-1), 9+8*stage))
    require(len(retained) == len(set(retained)) == controller['ambient_rank'], 'actual 145-row retained support')
    retained_mask = sum(1 << j for j in retained)
    contacts = []
    paths = 0
    endpoint_records = []
    main_profile, idle_profile = Counter(), Counter()
    for _, stage, pair, backward in (event for event in controller['physical_events'] if event[0] == 'LOCAL'):
        require(not backward, 'actual forward source supplier')
        spectators = positive(AXES[9:9+8*stage])
        for q in word['ports']:
            columns = route(stage, q, bases[q])
            raw_x = ((q, 1),) if stage == 0 else positive(AXES[:9+8*(stage-1)])
            raw_y = () if stage == 0 else terms(list(raw_x)+[(q, -1)])
            entry_x = terms(list(spectators)+[(q, 1)])
            entry_y = spectators
            exit_x = terms(list(spectators)+[(axis, 1) for axis in AXES[:9]])
            exit_y = terms(list(exit_x)+[(q, -1)])
            out_x = positive(AXES[:9+8*stage])
            out_y = terms(list(out_x)+[(q, -1)])
            maps = [contact(a, b, columns) for a, b in
                    ((raw_x, entry_x), (raw_y, entry_y), (exit_x, out_x), (exit_y, out_y))]
            require(all(columns[j] == AXES[j] for j in range(DIMENSION) if j not in retained)
                    and all((item['translation'] | item['inverse_translation']) & ~retained_mask == 0 for item in maps),
                    'all actual contacts fix omitted spectator rows')
            expected = phase(stage_terms(stage, q))
            d0 = stage_terms(0, q)
            require(transformed_path(d0, maps[0], maps[2], columns) == expected, 'executed X diagonal D_s')
            require(transformed_path(d0, maps[1], maps[3], columns) == expected, 'executed Y diagonal D_s')
            require(transformed_path(terms(list(d0)+[(q, -1)]), maps[0], maps[3], columns)
                    == phase(terms(list(stage_terms(stage, q))+[(q, -1)])), 'executed cross D_s Q inverse')
            require(sum(columns[j] != AXES[j] for j in range(DIMENSION)) <= 17
                    and all(item['translation'].bit_count() <= 17 and item['inverse_translation'].bit_count() <= 17
                            for item in maps), 'source seventeen-axis contacts')
            contacts.append([stage, q, maps])
            paths += 3
    digest = hashlib.sha256(json.dumps(contacts, separators=(',', ':')).encode()).hexdigest()
    require(digest == source_result['physical_caller']['route_payload_sha256'], 'complete selected raw contact payload')

    for q in word['ports']:
        # A rank-one positive query plus its full ordinary normalizer gives Q^-1.
        query_basis = transpose((q,)+bases[q])
        query = (('P', tuple(query_basis)),)
        equal(9, adjoint(query)+(('C', 1, 1),)+query+(('X', q),), (('C', q, -1),), 'complete positive thin query')
        for output, diagonal in enumerate(controller['diagonal']):
            qp, selected = diagonal[0], diagonal[1:]
            require(qp in (-1, 1) and len(selected) == 33 and set(selected) <= {0, 1}, 'complete raw endpoint exponent grammar')
            raw = terms([(q, qp)]+[entry for stage, yes in enumerate(selected) if yes for entry in stage_terms(stage, q)])
            active = list(range(9)) if selected[0] else [0]
            active += [j for stage in range(1, 33) if selected[stage] for j in range(9+8*(stage-1), 9+8*stage)]
            base = AXES[:9] if selected[0] else (q,)+bases[q]
            canonicalizer = complete_positive_basis(base, active, retained)
            wanted = canonicalizer[:len(active)]
            translation = q if qp == -1 else 0
            corrected = terms(list(raw)+([(translation, 2)] if translation else []))
            require(phase(corrected) == phase(positive(wanted)), 'entire main endpoint with final translation')
            require(len(wanted) == 1+8*sum(selected), 'complete productive main rank')
            main_profile[len(wanted)] += 1
            endpoint_records.append([q, output, len(wanted), translation, list(canonicalizer)])
    idle_endpoints = []
    for event_index, event in enumerate(controller['physical_events']):
        if event[0] != 'IDLE':
            continue
        stages = event[2]
        require(stages and len(stages) == len(set(stages)) and set(stages) <= set(range(33)), 'entire idle window')
        for q in word['ports']:
            raw = terms(entry for stage in stages for entry in stage_terms(stage, q))
            active = list(range(1, 9)) if 0 in stages else []
            active += [j for stage in stages if stage for j in range(9+8*(stage-1), 9+8*stage)]
            canonicalizer = complete_positive_basis((q,)+bases[q], active, retained)
            wanted = positive(canonicalizer[:len(active)])
            adapter = contact(wanted, raw, AXES)
            require(len(active) == 8*len(stages), 'positive whole-idle rank')
            idle_profile[len(active)] += 2
            idle_endpoints.append([event_index, q, len(active), adapter, list(canonicalizer)])
    registered = source_result['physical_caller']
    require(dict(main_profile) == {int(k): v for k, v in registered['main_targets'].items()}, 'selected main output census')
    require(dict(idle_profile) == {int(k): v for k, v in registered['whole_idle_jobs'].items()}, 'selected whole-idle census')
    return {'source_dimension': DIMENSION, 'retained_source_rows': len(retained), 'omitted_identity_spectator_rows': DIMENSION-len(retained),
            'complete_raw_contacts': 4*len(contacts), 'composed_native_paths': paths,
            'source_route_payload_sha256': digest, 'thin_query_boundaries': len(word['ports']),
            'complete_main_endpoints': sum(main_profile.values()), 'main_profile': dict(sorted(main_profile.items())),
            'complete_idle_endpoints': sum(idle_profile.values()), 'idle_profile': dict(sorted(idle_profile.items())),
            'full_coordinate_bijections': len(endpoint_records)+len(idle_endpoints),
            'main_boundary_sha256': hashlib.sha256(json.dumps(endpoint_records, separators=(',', ':')).encode()).hexdigest(),
            'idle_boundary_sha256': hashlib.sha256(json.dumps(idle_endpoints, separators=(',', ':')).encode()).hexdigest(),
            'limits': 'algebraic whole-field bijections; physical scheduling and charged realization remain separate'}
