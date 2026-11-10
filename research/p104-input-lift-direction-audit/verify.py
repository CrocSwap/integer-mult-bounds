#!/usr/bin/env python3
"""Independent scalar audit of the four PR6349 helper-input lifts.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The audited word and proof are Ali Romman's. The source word is
DreamingOfClouds' PR6314 compression of PR6167. This verifier does not import
those packages or their checker chain.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STATUS = 'PASS_P104_INPUT_LIFT_DIRECTION_AUDIT'
SOURCE = 'research/p104-frontier-compression-2/WORD.json.gz'
LIFT = 'research/p104-native-input-lifting/WORD.json.gz'
PROOF = 'research/p104-native-input-lifting/PROOF.md'
PRIMARIES = (496, 649, 663, 508)
DIRECTIONS = (
    (496, {496: Q(1), 639: Q(-1), 643: Q(-1, 2)},
     {496: Q(1), 639: Q(-1), 643: Q(-1, 2)}, 595, (52,)),
    (649, {649: Q(1), 648: Q(-1)},
     {649: Q(1), 648: Q(-1), 198: Q(1)}, 597, (82,)),
    (663, {663: Q(1), 665: Q(-1)},
     {663: Q(1), 665: Q(-1), 179: Q(1, 2)}, 105, (51,)),
    (508, {508: Q(1), 631: Q(-1), 635: Q(-1, 2)},
     {508: Q(1), 631: Q(-1), 635: Q(-1, 2)}, 1093, (30, 42, 384)),
)
RESTORE = (
    ['ADD', 639, 496, '1', 127],
    ['ADD', 643, 496, '1/2', 127],
    ['ADD', 648, 649, '1', 127],
    ['ADD', 665, 663, '1', 127],
    ['ADD', 631, 508, '1', 127],
    ['ADD', 635, 508, '1/2', 127],
)
PROOF_PHRASES = (
    'e496 - e639 - e643/2',
    'e649 - e648',
    'e663 - e665',
    'e508 - e631 - e635/2',
    '639 += 496; 643 += 496/2; 648 += 649;',
    '665 += 663; 631 += 508; 635 += 508/2.',
    'H1 + H2 + H3 + 2 H4 - 4 H5',
    'H6 + 3 H8 - 4 H9',
    'Frame 1093 is the intersection of frames 118 and 733.',
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_words():
    pins = {row['path']: row for row in json.loads((HERE / 'SOURCES.json').read_text())['files']
            if row['usage'] == 'input'}
    need(set(pins) == {SOURCE, LIFT, PROOF}, 'Pinned input inventory')
    raw = {}
    for path, pin in pins.items():
        data = (ROOT / path).read_bytes()
        need(sha256(data).hexdigest() == pin['sha256'], 'SHA256 ' + path)
        raw[path] = data
    proof = raw[PROOF].decode()
    for phrase in PROOF_PHRASES:
        need(phrase in proof, 'Proof phrase ' + phrase)
    source = json.loads(gzip.decompress(raw[SOURCE]))
    lifted = json.loads(gzip.decompress(raw[LIFT]))
    return source, lifted


def span(basis):
    out = {0}
    for value in basis:
        need(type(value) is int and 0 < value < 512 and value not in out,
             'Independent binary basis')
        out |= {item ^ value for item in tuple(out)}
    return frozenset(out)


def replay(word):
    """Scalar endpoint, MOVE-rank histogram and helper ranks.

    Helper rank is dim(final frame) - dim(initial frame) for every public role
    outside the 104 live ports and their +112 copies. A MOVE of rank
    |dim(destination) - dim(source)| is one paid job. Both rules are the
    finite GF(2) frame model: a later public frame must strictly contain the
    earlier one, and a private owned move must strictly shrink it.
    """
    public = word['public']
    owned = word['owned_fields']
    need(public == 770 and owned == 29, 'Public and owned inventory')
    frames = [span(basis) for basis in word['frames']]
    rows = [{role: Q(1)} for role in range(public + owned)]
    current = list(word['initial']) + [None] * owned
    paid = Counter()
    scalar = 0
    live = set()
    peak = 0
    lifetimes = 0
    for event in word['program']:
        op, role = event[:2]
        need(0 <= role < public + owned, 'Role index')
        if op == 'MOVE':
            _, role, start, end, private = event
            need(current[role] == start and (role in live) is private,
                 'Transport source and ownership')
            if private:
                need(frames[end] < frames[start], 'Nested private transport')
            else:
                need(frames[start] < frames[end], 'Nested public transport')
            paid[abs(len(word['frames'][end]) - len(word['frames'][start]))] += 1
            current[role] = end
            continue
        if op == 'INIT':
            need(role >= public and role not in live, 'Owned initialization')
            live.add(role)
            lifetimes += 1
            peak = max(peak, len(live))
            rows[role] = {}
            current[role] = event[2]
            scalar += 2
            continue
        if op == 'CLEAR':
            need(role in live and current[role] == event[2], 'Owned erasure')
            rows[role] = {}
            current[role] = None
            live.remove(role)
            scalar += 2
            continue
        coefficient, frame = Q(event[-2]), event[-1]
        need(coefficient and current[role] == frame, 'Scalar destination and coefficient')
        numerator, denominator = abs(coefficient.numerator), coefficient.denominator
        need(denominator & (denominator - 1) == 0, 'Dyadic scalar coefficient')
        if op == 'SCALE':
            need(numerator & (numerator - 1) == 0, 'Dyadic unit SCALE')
            rows[role] = {key: coefficient * value for key, value in rows[role].items()}
            scalar += 2 * (abs(numerator.bit_length() - denominator.bit_length())
                           + int(coefficient < 0))
            continue
        source = event[2]
        need(source != role and current[source] == frame, 'Common scalar chart')
        if op == 'COPY':
            need(role in live and not rows[role], 'COPY into a cleared owned field')
            rows[role] = {key: coefficient * value for key, value in rows[source].items()}
        else:
            need(op == 'ADD', 'Scalar opcode')
            row = rows[role]
            for key, value in rows[source].items():
                total = row.get(key, 0) + coefficient * value
                if total:
                    row[key] = total
                else:
                    row.pop(key, None)
        scalar += 2 * (3 + numerator.bit_length() - 1 + numerator.bit_count()
                       + denominator.bit_length() - 1)
    need(not live and peak == 13 and lifetimes == 32 and current[:public] == word['final'],
         'Public exits and owned lifetimes')
    ports = set(word['live'])
    for role, row in enumerate(rows):
        expected = {role: Q(1)} if role < public else {}
        if role - 112 in ports:
            expected[role - 112] = Q(1)
        need(row == expected, 'Endpoint row ' + str(role))
    main = ports | {role + 112 for role in ports}
    need(len(ports) == 104 and len(main) == 208, 'Port and main inventory')
    helpers = Counter(len(word['frames'][word['final'][role]])
                      - len(word['frames'][word['initial'][role]])
                      for role in range(public) if role not in main)
    need(min(helpers) > 0, 'Positive helper ranks')
    return {'paid': dict(paid), 'helpers': dict(helpers), 'scalar': scalar,
            'paid_rank_mass': sum(rank * count for rank, count in paid.items())}


def difference(after, before):
    ranks = set(after) | set(before)
    return {rank: after.get(rank, 0) - before.get(rank, 0)
            for rank in ranks if after.get(rank, 0) != before.get(rank, 0)}


def departures(program, direction, public, owned):
    values = [Q(0)] * (public + owned)
    for role, coefficient in direction.items():
        values[role] = coefficient
    first = {}
    response = {}
    for event in program:
        op, role = event[:2]
        if op == 'MOVE' and event[2] == 3 and event[4] is False:
            need(role not in first, 'One departure from the zero chart')
            first[role] = event[3]
            if values[role]:
                response[role] = values[role]
        elif op in ('INIT', 'CLEAR'):
            values[role] = Q(0)
        elif op == 'SCALE':
            values[role] *= Q(event[2])
        elif op == 'COPY':
            values[role] = Q(event[3]) * values[event[2]]
        elif op == 'ADD':
            values[role] += Q(event[3]) * values[event[2]]
    return response, first


def apply_update(vector, direction, primary, sign):
    updated = dict(vector)
    factor = sign * vector.get(primary, 0)
    for role, coefficient in direction.items():
        if role == primary:
            continue
        total = updated.get(role, 0) + factor * coefficient
        if total:
            updated[role] = total
        else:
            updated.pop(role, None)
    return updated


def check_bases(source):
    occupied = set()
    for primary, direction, response, frame, basis in DIRECTIONS:
        need(direction[primary] == response[primary] == 1, 'Unit primary coordinate')
        need(not occupied.intersection(direction), 'Disjoint input supports')
        occupied.update(direction)
        need(apply_update(apply_update(
            {primary: Q(3), 700: Q(5)}, direction, primary, 1), direction, primary, -1)
            == {primary: Q(3), 700: Q(5)}, 'Inverse basis')
        update = {role: coefficient for role, coefficient in direction.items() if role != primary}
        need(all(apply_update({role: amount}, direction, primary, 1) == {role: amount}
                 for role, amount in update.items()),
             'Carrier update is nilpotent')
        found, first = departures(source['program'], direction, source['public'],
                                  source['owned_fields'])
        need(found == response, 'Departure response of primary ' + str(primary))
        common = span(basis)
        for role in direction:
            need(source['initial'][role] == 3 and source['final'][role] == 127,
                 'Full helper before the lift')
        for role in response:
            need(common <= span(source['frames'][first[role]]),
                 'Common native input subspace')


def index(program, event):
    hits = [position for position, item in enumerate(program) if item == event]
    need(len(hits) == 1, 'Unique event ' + str(event))
    return hits[0]


def carrier_sandwich(program, opening, closing, primary, wide, narrow):
    start, end = index(program, opening), index(program, closing)
    need(start < end, 'Carrier subtraction precedes its closing addition')
    values = {wide: {'v': Q(1)}, narrow: {'z': Q(1)}, primary: {'x': Q(1)}}

    def coefficient(role):
        return values.setdefault(role, {('external', role): Q(1)})

    for event in program[start:end + 1]:
        if event[0] != 'ADD':
            continue
        destination, source, scale = event[1], event[2], Q(event[3])
        if destination not in (primary, wide, narrow) and source not in (primary, wide, narrow):
            continue
        row = dict(coefficient(destination))
        for key, amount in coefficient(source).items():
            row[key] = row.get(key, 0) + scale * amount
            if row[key] == 0:
                del row[key]
        values[destination] = row
    need(values[wide].get('v') == 1 and values[wide].get('x') == -1
         and values[wide].get('z', 0) == 0, 'Wide carrier loses one primary input')
    need(values[narrow].get('z') == 1 and values[narrow].get('x') == Q(-1, 2)
         and values[narrow].get('v', 0) == 0, 'Narrow carrier loses half a primary input')
    need(values[primary] == {'x': Q(1)}, 'Primary input is unchanged inside the sandwich')


def check_schedule(source, lifted):
    need(len(source['program']) == 17445 and len(lifted['program']) == 17452,
         'Event counts')
    need(lifted['frames'][:-1] == source['frames'], 'Inherited frames')
    need(lifted['frames'][1093] == [30, 42, 384], 'Appended three-dimensional frame')
    need(span(lifted['frames'][1093]) == span(source['frames'][118]) & span(source['frames'][733]),
         'Frame 1093 is the span intersection of frames 118 and 733')
    need(source['frames'][1091:1093] == lifted['frames'][1091:1093],
         'Frames 1091 and 1092 are unchanged')
    need(source['final'] == lifted['final'], 'Final frames unchanged')
    initial = [role for role, (before, after) in enumerate(zip(source['initial'], lifted['initial']))
               if before != after]
    need(initial == [496, 508, 649, 663], 'Only the four lifted inputs change chart')
    for primary, _direction, _response, frame, basis in DIRECTIONS:
        need(source['initial'][primary] == 3 and lifted['initial'][primary] == frame, 'New chart')
        need(tuple(lifted['frames'][frame]) == basis, 'Chart basis')
        source_rank = (len(source['frames'][source['final'][primary]])
                       - len(source['frames'][source['initial'][primary]]))
        lifted_rank = (len(lifted['frames'][lifted['final'][primary]])
                       - len(lifted['frames'][lifted['initial'][primary]]))
        expected = {496: 8, 649: 8, 663: 8, 508: 6}[primary]
        need(source_rank == 9 and lifted_rank == expected, 'Individual target rank')
    omitted = [event for event in source['program']
               if event[0] == 'ADD' and event[-1] == 3 and event[2] in PRIMARIES]
    need(len(omitted) == 10 and all(event not in lifted['program'] for event in omitted),
         'Ten initial-chart uses of the lifted inputs are removed')
    need(not any(event[0] == 'ADD' and event[-1] == 3 and event[2] in PRIMARIES
                 for event in lifted['program']),
         'No lifted input is read in the zero chart')
    need(tuple(lifted['program'][-6:]) == RESTORE, 'Six inverse-basis output additions')
    carrier_sandwich(lifted['program'], ['ADD', 639, 643, '-2', 3],
                     ['ADD', 639, 643, '2', 1027], 496, 639, 643)
    carrier_sandwich(lifted['program'], ['ADD', 631, 635, '-2', 3],
                     ['ADD', 631, 635, '2', 118], 508, 631, 635)
    block = (
        ['MOVE', 179, 3, 105, False],
        ['ADD', 179, 663, '1/2', 105],
        ['MOVE', 665, 3, 1051, False],
        ['MOVE', 663, 105, 1051, False],
        ['ADD', 665, 663, '-1', 1051],
    )
    need(any(tuple(lifted['program'][pos:pos + 5]) == block
             for pos in range(len(lifted['program']) - 4)),
         'Contiguous 663 injection and carrier subtraction')
    move_648 = index(lifted['program'], ['MOVE', 648, 3, 120, False])
    move_649 = index(lifted['program'], ['MOVE', 649, 597, 120, False])
    subtract_649 = index(lifted['program'], ['ADD', 648, 649, '-1', 120])
    need(move_648 < move_649 < subtract_649, '648 receives 649 after both arrive at frame 120')
    need(['MOVE', 649, 3, 120, False] not in lifted['program'], '649 no longer departs from zero')
    need(['MOVE', 663, 3, 1051, False] not in lifted['program'], '663 no longer departs from zero')
    need(index(lifted['program'], ['MOVE', 198, 3, 597, False])
         < index(lifted['program'], ['ADD', 198, 649, '1', 597]),
         '198 receives 649 at its first frame')


def reject(mutator):
    _source, lifted = load_words()
    mutated = deepcopy(lifted)
    mutator(mutated)
    try:
        replay(mutated)
    except ValueError as error:
        return str(error)
    raise ValueError('Mutated word was accepted')


def controls():
    def drop(event):
        def mutate(word):
            position = word['program'].index(event)
            del word['program'][position]
        return mutate

    messages = {
        'missing first carrier subtraction': reject(drop(['ADD', 639, 643, '-2', 3])),
        'missing output correction': reject(drop(['ADD', 635, 508, '1/2', 127])),
        'wrong 649 injection': reject(lambda word: word['program'].__setitem__(
            word['program'].index(['ADD', 198, 649, '1', 597]),
            ['ADD', 198, 649, '-1', 597])),
    }

    def wrong_intersection(word):
        word['frames'][1093] = [1, 2, 4]

    messages['wrong intersection'] = reject(wrong_intersection)
    for label, message in messages.items():
        need('Endpoint row' in message or 'Nested public transport' in message
             or 'Nested private transport' in message or 'Transport source' in message,
             'Control did not fail closed: ' + label + ': ' + message)
    return messages


def main():
    source, lifted = load_words()
    check_bases(source)
    check_schedule(source, lifted)
    before, after = replay(source), replay(lifted)
    need(difference(after['paid'], before['paid']) == {1: 1, 2: 1, 3: 1, 4: 2, 5: -4},
         'Local paid change')
    need(difference(after['helpers'], before['helpers']) == {6: 1, 8: 3, 9: -4},
         'Native target debit')
    need((before['scalar'], before['paid_rank_mass'], after['scalar'], after['paid_rank_mass'])
         == (127042, 5952, 127088, 5946), 'Scalar allowance and paid rank mass')
    failed = controls()
    need(len(failed) == 4, 'Four failure controls')
    print(STATUS)


if __name__ == '__main__':
    main()
