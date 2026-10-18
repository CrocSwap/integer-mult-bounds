"""Retimed rank-eight coded helper over four pinned PR855 embeddings.

PR781/855 by NeoKazuya supply the coded core and full provider embeddings.
This endpoint/premix construction is prepared for nightangelflowerwin-ops
with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json

HELPER = 448


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    payload = path.read_bytes()
    return json.loads(gzip.decompress(payload) if path.suffix == '.gz' else payload)


def encode(word):
    return json.dumps(word, sort_keys=True, separators=(',', ':')).encode()


def basis(vectors):
    pivots = {}
    for x in vectors:
        require(type(x) is int and 0 <= x < 512, 'Frame domain')
        for k in sorted(pivots, reverse=True):
            if x >> k & 1:
                x ^= pivots[k]
        if x:
            k = x.bit_length() - 1
            for j in list(pivots):
                if pivots[j] >> k & 1:
                    pivots[j] ^= x
            pivots[k] = x
    return [pivots[k] for k in sorted(pivots, reverse=True)]


def inverse_helper_row(word):
    # A row times P^-1: multiply inverse elementary matrices in chronological
    # order. No dense native-auditor state maps or its GF(2) routines are used.
    row = {HELPER: Q(1)}
    for event in word['A'] + word['cut'] + word['B']:
        if event[0] == 'add':
            source = event[2]
            row[source] = row.get(source, 0) - Q(event[3], event[4]) * row.get(event[1], 0)
            if not row[source]:
                row.pop(source, None)
        elif event[1] in row:
            require(event[0] == 'scale', 'Scalar primitive')
            row[event[1]] *= Q(event[3], event[2])
    require(row.get(HELPER) == 1 and len(row) == 3 and
            all(not 112 <= r < 224 for r in row), 'Unexpected coded-helper inverse row')
    # The target-only precondition and generated compensation have zero row
    # coefficients here. The helper never receives a target-row value.
    require(all(not (112 <= event[2] < 224) for event in word['A'] + word['B']
                if event[0] == 'add' and not 112 <= event[1] < 224), 'Target-to-helper dependency')
    require(all(112 <= event[1] < 224 for event in word['precondition']), 'Non-target precondition')
    replay = dict(row)
    for event in reversed(word['precondition'] + word['A'] + word['cut'] + word['B']):
        if event[0] == 'add':
            source = event[2]
            replay[source] = replay.get(source,0) + Q(event[3],event[4])*replay.get(event[1],0)
            if not replay[source]:
                replay.pop(source,None)
        elif event[1] in replay:
            replay[event[1]] *= Q(event[2],event[3])
    require(replay == {HELPER: Q(1)}, 'Independent inverse-row identity')
    return row


def response(word):
    # Forward basis column on the main word, followed by the target-chart
    # inverse precondition. Non-target rows of the latter dirty response are
    # zero, matching the explicit scalar compensation contract.
    column = {HELPER: Q(1)}
    for event in word['A'] + word['cut'] + word['B']:
        if event[0] == 'add':
            target, source = event[1:3]
            column[target] = column.get(target, 0) + Q(event[3], event[4]) * column.get(source, 0)
        else:
            require(event[0] == 'scale', 'Scalar primitive')
            column[event[1]] = column.get(event[1], 0) * Q(event[2], event[3])
    column = {r: q for r, q in column.items() if 112 <= r < 224 and q}
    for event in word['precondition']:
        if event[0] == 'add':
            target, source = event[1:3]
            column[target] = column.get(target, 0) + Q(event[3], event[4]) * column.get(source, 0)
        else:
            column[event[1]] = column.get(event[1], 0) * Q(event[2], event[3])
    return {r: q for r, q in column.items() if q}


def construct(source):
    word = read(source)
    require(word['report']['v'] == 112 and word['report']['h'] == 9 and
            HELPER not in word['centers'] and str(HELPER) not in word.get('start_extra', {}),
            'Pinned coded helper interface')
    row = inverse_helper_row(word)
    frames = {}
    for event in word['A'] + word['B']:
        for role in ([event[1], event[2]] if event[0] == 'add' else [event[1]]):
            frames[role] = event[-1]
    endpoint = basis(x for role in row for x in frames[role])
    require(len(endpoint) == 8, 'Expected rank-eight cleanup join')
    corrections = [['add', HELPER, role, coefficient.numerator, coefficient.denominator, endpoint]
                   for role, coefficient in sorted(row.items()) if role != HELPER]
    touches = [i for i, event in enumerate(word['cleanup'])
               if HELPER in ([event[1], event[2]] if event[0] == 'add' else [event[1]])]
    require(len(touches) == 2 and all(word['cleanup'][i][1] == HELPER for i in touches),
            'Unexpected helper cleanup dependency')
    require(all(i not in touches for i, _ in word['early_cleanup']), 'Helper already ends early')
    old_cleanup = word['cleanup']
    new_index = {i: 2 + i - sum(j < i for j in touches) for i in range(len(old_cleanup)) if i not in touches}
    word['cleanup'] = corrections + [event for i, event in enumerate(old_cleanup) if i not in touches]
    word['early_cleanup'] = [[0, endpoint], [1, endpoint]] + [
        [new_index[i], frame] for i, frame in word['early_cleanup']]
    word['helper_final'][str(HELPER)] = endpoint
    word['refactored_cleanup'] = True
    col = response(word)
    premix = [['add', role, HELPER, -q.numerator, q.denominator, []] for role, q in sorted(col.items())]
    word['A'] = premix + word['A']
    proof = dict(input_content_sha256=sha256(gzip.decompress(source.read_bytes())).hexdigest(),
                 helper=HELPER, inverse_row={str(r): str(q) for r, q in sorted(row.items())},
                 end_of_B_frames={str(r): basis(frames[r]) for r in sorted(row)},
                 endpoint=endpoint, endpoint_rank=8, removed_cleanup_indexes=touches,
                 early_corrections=corrections, internal_premix=premix)
    return word, proof
