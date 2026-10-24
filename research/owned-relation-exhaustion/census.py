#!/usr/bin/env python3
"""Fixed-relation zero and literal/proportional snapshot census.

New independent source traversal, with the free-word convention credited to
Cinna Davis/zxv and Cao Yifan's retained PR4610 word. Relations and their first
physical realization are Ali Romman's PR5383. Prepared with OpenAI Codex
assistance, Apache-2.0. This census does not import predecessor evaluators.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'source/ACTUAL-WORD.json.gz'
WITNESS = HERE / 'WITNESS.json'
PAYLOAD = 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
WITNESS_SHA = '24599011da06325e1012619b2b84a4dd3aceb90ab42d3caaf6414879e7d16591'
EXPECTED_PROFILE = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(destination, source, coefficient):
    for key, value in source.items():
        value = destination.get(key, Q(0)) + coefficient * value
        if value:
            destination[key] = value
        else:
            destination.pop(key, None)


def relation_basis(witnesses):
    basis = {}
    for witness in witnesses:
        pairs = witness['relation']
        row = {h: Q(value) for h, value in pairs}
        need(len(row) == len(pairs) and all(224 <= h < 632 for h in row), 'Helper-only relation')
        for pivot, previous in sorted(basis.items()):
            add(row, previous, -row.get(pivot, Q(0)))
        need(row, 'Independent relation')
        pivot = min(row)
        coefficient = row[pivot]
        row = {h: value / coefficient for h, value in row.items()}
        for previous in basis.values():
            add(previous, row, -previous.get(pivot, Q(0)))
        basis[pivot] = row
    need(len(basis) == 8, 'Exactly eight fixed independent relations')
    return dict(sorted(basis.items()))


def normal(row):
    """Exact projective key, retaining signs separately as the leading value."""
    need(row, 'Nonzero projective row')
    first = row[min(row)]
    return tuple((key, value / first) for key, value in sorted(row.items())), first


def traverse(source, witnesses, direction, omit_scalar=None):
    basis = relation_basis(witnesses)
    rows = {('L', i): {(('L', i), ()): Q(1)} for i in range(632)}
    rows['C', 0] = {(('C', 0), ()): Q(1)}
    if direction == 'backward':
        for pivot, row in basis.items():
            rows['L', pivot] = {(('L', h), ()): -value for h, value in row.items() if h != pivot}
    frames = {('L', i): f for i, f in enumerate(source['canonical']['start'])}
    frames['C', 0] = None
    # Keeping every historical boundary value favors the putative replacement:
    # it ignores snapshot slots, liveness, COPY, scalar and restoration costs.
    seen = defaultdict(list)
    def remember(event, role, frame):
        if rows[role]:
            key, coefficient = normal(rows[role])
            seen[frame, key].append((event, role, coefficient))
    for i, frame in enumerate(source['canonical']['start']):
        remember(-1, ('L', i), frame)
    paid, events = Counter(), Counter()
    zero_rows, matches = [], []
    for position, event in enumerate(source['programs'][direction]):
        kind = event[0]
        events[kind] += 1
        role, frame = None, None
        if kind == 'scalar':
            operation, frame = event[1:]
            role = tuple(operation[1])
            if position == omit_scalar:
                need(operation[0] == 'add', 'Omission control names an ADD')
                continue
            if operation[0] == 'clear':
                rows[role] = {}
                frames[role] = frame
            else:
                need(frames[role] == frame, 'Scalar destination frame')
                if operation[0] in ('copy', 'add'):
                    other = tuple(operation[2])
                    need(frames[other] == frame, 'Scalar source frame')
                    if operation[0] == 'copy':
                        rows[role] = dict(rows[other])
                    else:
                        add(rows[role], rows[other], Q(operation[3], operation[4]))
                else:
                    need(operation[0] == 'scale', 'Known scalar opcode')
                    rows[role] = {key: Q(operation[2], operation[3]) * value for key, value in rows[role].items()}
        elif kind == 'warp':
            _, target, operator, old, frame = event
            role = tuple(target)
            need(frames[role] == old, 'Native input frame')
            symbol = (1 if operator > 0 else -1) * (abs(operator) + (10**6 if direction == 'backward' else 0))
            rows[role] = {(variable, word[1:] if word and word[0] == -symbol else (symbol,) + word): value
                          for (variable, word), value in rows[role].items()}
            frames[role] = frame
        elif kind in ('climb', 'center'):
            if kind == 'climb':
                _, _, index, old, frame, rank = event
                role = 'L', index
            else:
                _, index, old, frame, rank = event
                role = 'C', index
            need(frames[role] == old, 'Paid input frame')
            need(rank == abs(len(source['canonical']['frames'][old]) - len(source['canonical']['frames'][frame])), 'Paid rank')
            paid[rank] += 1
            if not rows[role]:
                zero_rows.append({'event': position, 'source_event': event})
            else:
                key, coefficient = normal(rows[role])
                prior = seen.get((frame, key), [])
                if prior:
                    matches.append({'event': position, 'source_event': event, 'row_terms': len(rows[role]),
                        'earlier_snapshots': [{'event': i, 'role': list(r), 'factor': str(coefficient / c)} for i, r, c in prior]})
            frames[role] = frame
        else:
            need(kind in ('phase', 'adapter'), 'Known source event')
        if role is not None and frame is not None:
            remember(position, role, frame)
    need([frames['L', i] for i in range(632)] == source['canonical']['final'], 'All final frames')
    need(dict(paid) == EXPECTED_PROFILE, 'Complete source paid census')
    return {'paid_profile': dict(sorted(paid.items())), 'paid_total': sum(paid.values()),
            'event_counts': dict(events), 'zero_paid_rows': zero_rows,
            'nonzero_proportional_snapshot_matches': matches,
            'historical_snapshots_favorably_retained': True,
            'entry_relation_applied': direction == 'backward'}


def verify_census(result, witnesses, direction):
    need(result['paid_total'] == 3298, 'All paid events visited')
    zeros = [row['event'] for row in result['zero_paid_rows']]
    expected_zeros = sorted(w['zero_event'] for w in witnesses) if direction == 'backward' else []
    need(zeros == expected_zeros, 'Exactly the known zero paid rows')
    matches = result['nonzero_proportional_snapshot_matches']
    need([m['event'] for m in matches] == ([w['event'] for w in witnesses] if direction == 'backward' else []), 'Exactly the known matched paid sites')
    for match, witness in zip(matches, witnesses):
        need(match['earlier_snapshots'] == [{'event': witness['cached_event'], 'role': ['L', witness['cached_role']],
                                         'factor': str(Q(witness['copy_factor']))}], 'Unique exact chronological same-frame snapshot, including sign')


def run(controls=True):
    raw = SOURCE.read_bytes()
    need(sha256(gzip.decompress(raw)).hexdigest() == PAYLOAD, 'Pinned complete source payload')
    source = json.loads(gzip.decompress(raw))
    witness_raw = WITNESS.read_bytes()
    need(sha256(witness_raw).hexdigest() == WITNESS_SHA, 'Exact PR5383 witness bytes')
    witnesses = json.loads(witness_raw)
    directions = {}
    for direction in ('forward', 'backward'):
        directions[direction] = traverse(source, witnesses, direction)
        verify_census(directions[direction], witnesses, direction)
    rejected = {}
    if controls:
        mutated = deepcopy(witnesses)
        mutated[0]['relation'][1][1] = str(-Q(mutated[0]['relation'][1][1]))
        altered = traverse(source, mutated, 'backward')
        try:
            verify_census(altered, witnesses, 'backward')
        except ValueError as error:
            rejected['wrong_relation_sign'] = str(error)
        else:
            raise ValueError('Wrong relation accepted')
        altered = traverse(source, witnesses, 'backward', omit_scalar=11331)
        try:
            verify_census(altered, witnesses, 'backward')
        except ValueError as error:
            rejected['omitted_source_ADD_11331'] = str(error)
        else:
            raise ValueError('Omitted source ADD accepted')
        mutated = deepcopy(witnesses)
        mutated[0]['copy_factor'] = '-1'
        try:
            verify_census(directions['backward'], mutated, 'backward')
        except ValueError as error:
            rejected['wrong_cached_global_sign'] = str(error)
        else:
            raise ValueError('Wrong cached sign accepted')
    return {'status': 'PASS_FIXED_EIGHT_RELATION_FREE_WORD_ZERO_SNAPSHOT_SATURATION',
            'source_compressed_sha256': sha256(raw).hexdigest(), 'source_payload_sha256': PAYLOAD,
            'witness_sha256': sha256(WITNESS.read_bytes()).hexdigest(), 'pivots': list(relation_basis(witnesses)),
            'orientations': directions, 'negative_controls': rejected,
            'scope': 'Fixed eight entry relations, unchanged source event boundaries and free-word grammar. Unlimited historical scalar snapshots in the same physical output frame are allowed. No extra paid zero row or proportional single-snapshot equality remains beyond the eight known backward centre/zero pairs. New relations, scalar linear combinations, native identities beyond free reduction, changed event graph and physical admission are not covered.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-controls', action='store_true')
    parser.add_argument('--out', type=Path)
    arguments = parser.parse_args()
    result = run(not arguments.no_controls)
    output = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if arguments.out:
        arguments.out.write_text(output)
    else:
        print(output, end='')
