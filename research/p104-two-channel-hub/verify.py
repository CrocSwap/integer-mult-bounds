"""Exact bounded S09 block obstruction on the reconstructed PR #6824 word.

Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Temporal pure-row method follows Ali Romman PR #5786; full dirty-axis and
retained-buffer obligations follow ToikY PR #5800 and atlas PR #5803.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
PAYLOAD = 'd3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(target, source, scalar):
    for key, value in source.items():
        result = target.get(key, 0) + scalar * value
        if result:
            target[key] = result
        else:
            target.pop(key, None)


def span(basis):
    result = {0}
    for vector in basis:
        need(vector not in result, 'Independent binary frame basis')
        result |= {entry ^ vector for entry in tuple(result)}
    return result


def pure_basis(vectors, group):
    """Basis for span(vectors) intersect Q^group, using outside-first pivots."""
    pivots, pure = {}, []
    for original in vectors:
        vector = dict(original)
        while vector:
            outside = [key for key in vector if key not in group]
            pivot = min(outside or vector)
            if pivot not in pivots:
                multiplier = Q(1) / vector[pivot]
                vector = {key: value * multiplier for key, value in vector.items()}
                pivots[pivot] = vector
                if not outside:
                    pure.append(vector)
                break
            add(vector, pivots[pivot], -vector[pivot])
    return pure


def pairing_rank(rows, columns):
    """Independent rank <= 1 test by all cross-minor identities, no Gram RREF."""
    gram = [[sum(value * column.get(key, 0) for key, value in row.items())
             for column in columns] for row in rows]
    pivot = next(((i, j) for i, row in enumerate(gram)
                  for j, value in enumerate(row) if value), None)
    if pivot is None:
        return 0, gram
    a, b = pivot
    for i, row in enumerate(gram):
        for j, value in enumerate(row):
            if value * gram[a][b] != gram[i][b] * gram[a][j]:
                return 2, gram
    return 1, gram


def trace(word):
    """All necessary prefix/suffix contacts, including arbitrary owned axes."""
    public, events = word['public'], word['program']
    size, length = public + word['owned_fields'], len(events)
    frames = list(map(span, word['frames']))
    ambient = max(map(len, word['frames']))
    zero = next(i for i, frame in enumerate(frames) if len(frame) == 1)
    full = next(i for i, basis in enumerate(word['frames']) if len(basis) == ambient)
    main = set(word['live']) | {role + 112 for role in word['live']}
    group = {role for role in range(public) if role not in main
             and (word['initial'][role], word['final'][role]) == (zero, full)}
    interiors = {}
    for i, event in enumerate(events):
        if event[0] == 'MOVE':
            a, b = event[2:4]
            interiors[i] = [f for f, value in enumerate(frames)
                            if frames[a] < value < frames[b]
                            or frames[b] < value < frames[a]]
    contacts = [defaultdict(list), defaultdict(list)]
    helpers = set(range(public)) - main
    intervals, births = defaultdict(list), {role: 0 for role in helpers}

    def record(side, frame, time, role, vector):
        if frame is not None and frame not in (zero, full) and vector:
            contacts[side][frame].append((time, role, dict(vector)))

    rows = [{role: Q(1)} for role in range(size)]
    current = word['initial'] + [None] * word['owned_fields']
    live_owned = set()
    for role in range(public):
        record(0, current[role], 0, role, rows[role])
    for i, event in enumerate(events):
        op, role = event[:2]
        if op == 'MOVE':
            a, b, private = event[2:]
            need(current[role] == a and private == (role in live_owned), 'Actual MOVE source and ownership')
            need(frames[b] < frames[a] if private else frames[a] < frames[b], 'Nested source MOVE')
            for frame in interiors[i]:
                record(0, frame, 2 * i + 1, role, rows[role])
                if role in helpers:
                    intervals[frame].append((2 * i + 1, 2 * i + 1, role))
            if role in helpers:
                intervals[current[role]].append((births[role], 2 * i, role))
                births[role] = 2 * i + 2
            current[role] = event[3]
        elif op in ('INIT', 'CLEAR'):
            if op == 'INIT':
                need(role >= public and role not in live_owned, 'Owned initialization')
                live_owned.add(role)
            else:
                need(role in live_owned and current[role] == event[2], 'Owned clear at its actual frame')
                live_owned.remove(role)
            rows[role] = {}
            current[role] = event[2] if op == 'INIT' else None
        elif op == 'SCALE':
            need(current[role] == event[-1] and Q(event[-2]) != 0, 'Actual SCALE chart')
            rows[role] = {key: value * Q(event[-2]) for key, value in rows[role].items()}
        else:
            need(op in ('ADD', 'COPY'), 'Known source opcode')
            need(current[role] == current[event[2]] == event[-1], 'Actual common scalar chart')
            if op == 'COPY':
                need(role in live_owned and not rows[role], 'COPY into zero owned field')
                rows[role] = {}
            add(rows[role], rows[event[2]], Q(event[-2]))
        record(0, current[role], 2 * i + 2, role, rows[role])
    for role in helpers:
        intervals[current[role]].append((births[role], 2 * length, role))
    need(current[:public] == word['final'] and not live_owned, 'Public/owned endpoint charts')
    for role, row in enumerate(rows):
        expected = {role: Q(1)} if role < public else {}
        if role - 112 in word['live']:
            expected[role - 112] = Q(1)
        need(row == expected, f'Complete arbitrary-input endpoint row {role}')
    columns = [{role: Q(1)} for role in range(size)]
    current = word['final'] + [None] * word['owned_fields']
    for role in range(public):
        record(1, current[role], 2 * length, role, columns[role])
    for i in reversed(range(length)):
        event = events[i]
        op, role = event[:2]
        changed = [role]
        if op == 'MOVE':
            for frame in interiors[i]:
                record(1, frame, 2 * i + 1, role, columns[role])
            current[role] = event[2]
        elif op in ('INIT', 'CLEAR'):
            columns[role] = {}
            current[role] = event[2] if op == 'CLEAR' else None
        elif op == 'SCALE':
            columns[role] = {key: value * Q(event[-2]) for key, value in columns[role].items()}
        else:
            add(columns[event[2]], columns[role], Q(event[-2]))
            changed.append(event[2])
            if op == 'COPY':
                columns[role] = {}
        for target in changed:
            record(1, current[target], 2 * i, target, columns[target])
    return contacts, intervals, group, (zero, full), interiors


def audit(word, require_obstruction=True, boundary=None, traced=None):
    contacts, intervals, group, boundaries, interiors = traced or trace(word)
    if boundary is not None:
        main = set(word['live']) | {role + 112 for role in word['live']}
        group = {role for role in range(word['public']) if role not in main
                 and (word['initial'][role], word['final'][role]) == boundary}
        boundaries = boundary
    frames = list(map(span, word['frames']))
    census, histogram, witness = [], Counter(), None
    for frame, lifetimes in sorted(intervals.items()):
        lifetimes = [(a, b, role) for a, b, role in lifetimes if role in group]
        if not frames[boundaries[0]] < frames[frame] < frames[boundaries[1]]:
            continue
        times = ({a for a, b, role in lifetimes} | {b for a, b, role in lifetimes}
                 | {time for time, role, row in contacts[0][frame]}
                 | {time for time, role, column in contacts[1][frame]})
        for cut in sorted(times):
            pivots = sorted({role for a, b, role in lifetimes if a <= cut <= b})
            if len(pivots) < 2:
                continue
            collection = pure_basis((row for time, role, row in sorted(
                contacts[0][frame], key=lambda item: (item[0], item[1])) if time <= cut), group)
            delivery = pure_basis((column for time, role, column in sorted(
                contacts[1][frame], key=lambda item: (item[0], item[1]), reverse=True)
                                   if time >= cut), group)
            rank, gram = pairing_rank(collection, delivery)
            if require_obstruction:
                need(rank <= 1, f'Rank-two candidate at frame {frame}, cut {cut}')
            histogram[rank] += 1
            census.append([frame, cut, pivots, len(collection), len(delivery), rank])
            if rank == 1 and witness is None:
                witness = dict(frame=frame, time2=cut, pivots=pivots,
                               collection=collection, delivery=delivery, gram=gram)
    return dict(boundary=list(boundaries), public=word['public'], owned=word['owned_fields'],
                axes=word['public'] + word['owned_fields'], events=len(word['program']),
                frames=len(word['frames']), eligible_helpers=len(group),
                interior_contacts=sum(map(len, interiors.values())),
                contact_records=sum(len(items) for side in contacts for items in side.values()),
                critical_cuts=len(census), tested_frames=len({row[0] for row in census}),
                rank_histogram=dict(sorted(histogram.items())),
                census=census, first_rank_one=witness)


def controls():
    # Two arbitrary helpers at one real intermediate frame must be detected.
    word = dict(public=2, owned_fields=1, live=[], frames=[[], [1], [1, 2]],
                initial=[0, 0], final=[2, 2], program=[
                    ['INIT', 2, 1], ['MOVE', 0, 0, 1, False],
                    ['MOVE', 1, 0, 1, False], ['MOVE', 0, 1, 2, False],
                    ['MOVE', 1, 1, 2, False], ['CLEAR', 2, 1]])
    positive = audit(word, False)
    need(positive['rank_histogram'].get(2, 0) > 0, 'Constructive rank-two positive control')
    try:
        audit(word)
    except ValueError:
        pass
    else:
        raise ValueError('Rank-two word incorrectly admitted to obstruction')
    # Outside helper contamination cannot be discarded as if it were zero.
    contaminated = pure_basis([{0: Q(1), 2: Q(1)}, {1: Q(1)}], {0, 1})
    need(len(contaminated) == 1 and contaminated[0] == {1: Q(1)}, 'Dirty-column exclusion')
    cancelled = pure_basis([{0: Q(1), 2: Q(1)}, {2: Q(1)}, {1: Q(1)}], {0, 1})
    need(len(cancelled) == 2, 'Cancellation can recover an actual second pure direction')
    need(pairing_rank([{0: Q(1)}, {1: Q(1)}], [{0: Q(1)}, {1: Q(1)}])[0] == 2,
         'Independent two-by-two minor control')
    # The first helper never occupies F in the unsplit word. Its legal MOVE
    # midpoint must nevertheless be eligible as the second simultaneous pivot.
    midpoint = dict(word)
    midpoint['program'] = [
        ['INIT', 2, 1], ['MOVE', 1, 0, 1, False],
        ['MOVE', 0, 0, 2, False], ['MOVE', 1, 1, 2, False], ['CLEAR', 2, 1]]
    mid = audit(midpoint, False)
    need(mid['rank_histogram'].get(2, 0) == 1, 'A paid query midpoint can be a pivot')
    return dict(rank_two_positive=True, rank_two_rejected=True,
                dirty_axis_not_free=True, exact_cancellation_recovers_direction=True,
                nonzero_minor_detected=True, interior_pivot_detected=True)


def audit_all(word):
    traced = trace(word)
    main = set(word['live']) | {role + 112 for role in word['live']}
    groups = Counter((word['initial'][role], word['final'][role])
                     for role in range(word['public']) if role not in main)
    results, skipped, histogram = [], [], Counter()
    for boundary, count in sorted(groups.items()):
        grade = len(word['frames'][boundary[1]]) - len(word['frames'][boundary[0]])
        if count < 2 or grade < 2:
            skipped.append(dict(boundary=list(boundary), helpers=count, grade=grade,
                                reason='fewer than two helpers' if count < 2 else 'no strict intermediate dimension'))
            continue
        result = audit(word, boundary=boundary, traced=traced)
        histogram.update(result['rank_histogram'])
        results.append(result)
    return dict(group_count=len(groups), checked_groups=len(results),
                skipped_groups=skipped, critical_cuts=sum(r['critical_cuts'] for r in results),
                rank_histogram=dict(sorted(histogram.items())), groups=results)


def encode(value):
    return json.loads(json.dumps(value, sort_keys=True, default=str))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    raw = gzip.decompress((HERE / 'inputs/WORD.json.gz').read_bytes())
    word = json.loads(raw)
    canonical = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
    need(sha256(canonical).hexdigest() == PAYLOAD, 'Exact reconstructed PR #6824 source')
    result = encode(dict(source_payload_sha256=PAYLOAD, audit=audit_all(word), controls=controls()))
    if args.emit:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(result == json.loads((HERE / 'RESULT.json').read_bytes()), 'Exact deterministic receipt')
    summary = result['audit'].copy()
    summary.pop('groups')
    summary.pop('skipped_groups')
    print(json.dumps(summary, sort_keys=True))
    print('PASS_P104_FROZEN_TWO_CHANNEL_OBSTRUCTION')


if __name__ == '__main__':
    main()
