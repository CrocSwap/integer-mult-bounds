"""Remove one carrier after checking its source and frame lifetime.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction

WORD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
BASE = '8bddbee377e2f3ce1f1247196c4b290d55767d20'
HELPER, SOURCE, RECEIVER = 470, 77, 444
BIRTH, READ, FRAME = 230, 1993, 186


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def load(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def save(path, word):
    path.write_bytes(gzip.compress(canonical(word), mtime=0))


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def rank(rows):
    basis = {}
    for values in rows:
        row = list(map(Fraction, values))
        for pivot, old in sorted(basis.items()):
            value = row[pivot]
            row = [a - value * b for a, b in zip(row, old)]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is not None:
            value = row[pivot]
            basis[pivot] = [x / value for x in row]
    return len(basis)


def lifetime(word):
    v = word['v']
    require(word['R'] == 439 and v == 111, 'Wrong source word dimensions')
    require(word['A'][BIRTH] == [79, HELPER, [SOURCE]], 'Carrier birth changed')
    require(word['A'][READ] == [79, RECEIVER, [HELPER]], 'Carrier read changed')
    occurrences = [(phase, i) for phase in ('A', 'B')
                   for i, (_, dst, sources) in enumerate(word[phase])
                   if HELPER in [dst, *sources]]
    require(occurrences == [('A', BIRTH), ('A', READ)], 'Carrier has another live use')
    require(HELPER not in word['ret'], 'Carrier is a retained copy source')
    masks = [sum(1 << x for x in frame) for frame in word['frames']]
    current = word['start'][:]
    values = [1 << i for i in range(2 * v + word['R'])]
    for frame, dst, sources in word['A'][:READ]:
        for row in [dst, *sources]:
            current[row] = frame
        for source in sources:
            values[dst] ^= values[source]
    require(values[SOURCE] == 1 << SOURCE, 'Source changed before the late read')
    require(values[HELPER] == (1 << SOURCE) ^ (1 << HELPER), 'Carrier contents changed')
    require(current[SOURCE] == FRAME, 'Source boundary frame changed')
    used = [SOURCE, RECEIVER]
    before = {str(row): current[row] for row in used}
    following = {}
    for row in used:
        next_frame = next(frame for frame, dst, sources in word['A'][READ + 1:] + word['B']
                          if row in [dst, *sources])
        require(masks[current[row]] & ~masks[FRAME] == 0, 'Illegal source access frame')
        require(masks[FRAME] & ~masks[next_frame] == 0, 'Illegal later frame')
        following[str(row)] = next_frame
    return {'birth': BIRTH, 'read': READ, 'helper': HELPER, 'source': SOURCE,
            'receiver': RECEIVER, 'new_frame': FRAME, 'before': before,
            'next_frame': following, 'source_unchanged': True,
            'retained_copy_uses': 0}


def rebuild_compensation(word):
    v = word['v']
    count = 2 * v + word['R']
    values = [1 << i for i in range(count)]
    for frame, dst, sources in word['A']:
        for source in sources:
            values[dst] ^= values[source]
    copied = [values[row] for row in word['ret']]
    for target, row in enumerate(word['scatter']):
        for index in row:
            values[v + target] ^= copied[index]
    for frame, dst, sources in word['B']:
        for source in sources:
            values[dst] ^= values[source]
    result = []
    for target in range(v):
        residue = values[v + target] ^ (1 << (v + target)) ^ (1 << target)
        require(residue & ((1 << (2 * v)) - 1) == 0, 'Raw DATA map changed')
        if residue:
            result.append([0, v + target, list(bits(residue))])
    return result


def build(word):
    lifetime(word)
    result = copy.deepcopy(word)
    result['A'] = [[FRAME, RECEIVER, [SOURCE]] if i == READ else gate
                   for i, gate in enumerate(word['A']) if i != BIRTH]
    result['C'] = [[1, dst, sources[:]] for _, dst, sources in reversed(result['A'] + result['B'])
                   if dst < word['v'] or dst >= 2 * word['v']]
    remap = lambda row: row - (row > HELPER)
    for phase in ('A', 'B', 'C'):
        result[phase] = [[frame, remap(dst), [remap(row) for row in sources]]
                         for frame, dst, sources in result[phase]]
    result['start'].pop(HELPER)
    result['final'].pop(HELPER)
    result['ret'] = [remap(row) for row in result['ret']]
    result['R'] -= 1
    result['stats']['extra_carriers'] -= 1
    result['D'] = rebuild_compensation(result)
    return result


def replay(word):
    v = word['v']
    count = 2 * v + word['R']
    masks = [sum(1 << x for x in frame) for frame in word['frames']]
    dimensions = [rank(word['lines'][i] for i in frame) for frame in word['frames']]
    values = [1 << i for i in range(count)]
    current = word['start'][:]
    profile, paths, records = Counter(), [[frame] for frame in current], []
    def move(row, frame):
        previous = current[row]
        require(masks[previous] & ~masks[frame] == 0, 'Frame descent')
        if previous != frame:
            delta = dimensions[frame] - dimensions[previous]
            require(delta > 0, 'Invalid frame change')
            profile[delta] += 1
            records.append([0, row, previous, frame, delta, 0])
            current[row] = frame
            paths[row].append(frame)
    def gates(phase, number):
        for frame, dst, sources in word[phase]:
            require(len(set([dst, *sources])) == 1 + len(sources), 'Invalid ADD operands')
            for row in [dst, *sources]:
                move(row, frame)
            for source in sources:
                values[dst] ^= values[source]
                records.append([1, dst, source, 1, frame, number])
    gates('D', 1)
    gates('A', 2)
    for index, row in enumerate(word['ret']):
        frame = current[row]
        profile[dimensions[frame]] += 1
        records.append([2, row, count, frame, 0, dimensions[frame]])
        for target, subset in enumerate(word['scatter']):
            if index in subset:
                require(current[v + target] == 0, 'Scatter target frame changed')
                values[v + target] ^= values[row]
                records.append([1, v + target, count, 1, 0, 3])
        records.append([3, row, count, frame, 0, 0])
    gates('B', 4)
    gates('C', 5)
    for row, frame in enumerate(word['final']):
        move(row, frame)
    expected = [((1 << i) ^ (1 << (i - v))) if v <= i < 2 * v else (1 << i)
                for i in range(count)]
    require(values == expected, 'Wrong arbitrary-dirty endpoint')
    bounds = []
    for reverse in (False, True):
        positive = [1] * count + [0]
        maximum = 1
        for op, dst, src, coefficient, frame, phase in reversed(records) if reverse else records:
            if op == 1:
                positive[dst] += positive[src]
                maximum = max(maximum, positive[dst])
            elif op == (3 if reverse else 2):
                positive[count] = positive[dst]
                maximum = max(maximum, positive[count])
            elif op == (2 if reverse else 3):
                positive[count] = 0
        bounds.append(maximum)
    local = 64 * bounds[0] ** 3 * bounds[1] ** 2
    nine = 2 ** 18 * bounds[0] ** 5 * bounds[1] ** 4
    return {'registers': count, 'helpers': word['R'], 'adds': sum(z[0] == 1 for z in records),
            'records': len(records), 'profile': dict(sorted(profile.items())),
            'rank_mass': sum(k * value for k, value in profile.items()),
            'copies': len(word['ret']), 'forward_bound': bounds[0], 'reverse_bound': bounds[1],
            'local_bits': local.bit_length(), 'nine_stage_bits': nine.bit_length(),
            'paths': paths, 'word_sha256': hashlib.sha256(canonical(word)).hexdigest()}, records
