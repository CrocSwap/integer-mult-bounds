#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent four-source projection and fixed-reader cut certificate.

No predecessor checker or generator is imported. See README.md for the
quantified family and, especially, the additional zero-reader hypothesis.
"""

import copy
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARTNERS = (33, 55, 74, 85)
LENDERS = (49, 83, 98, 101, 68, 80, 88, 31)
TARGETS = (23, 34, 50, 108)
NUMERATORS = ((-1, 1, -1, 2), (1, 1, 1, -2),
              (-1, 1, 1, 2), (1, 1, 1, 2))
FORCED_CENTRES = {9, 92, 224, 240}
MAX_EVENTS = 20_000
MAX_TERMS = 4096


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_words():
    pins = json.loads((HERE / 'INPUTS.json').read_text())
    require(len(pins['files']) == 6, 'input inventory')
    words = {}
    for item in pins['files']:
        raw = (HERE / item['path']).read_bytes()
        require(len(raw) <= 110_000, 'compressed input capacity')
        require(hashlib.sha256(raw).hexdigest() == item['sha256'], 'source hash')
        if item['path'].endswith('.gz'):
            # Authenticate the small fixed input before decompression or parsing.
            payload = gzip.decompress(raw)
            require(len(payload) <= 2_000_000, 'word capacity')
            require(hashlib.sha256(payload).hexdigest() == item['payload_sha256'],
                    'payload hash')
            tag = 'extra' if 'extra' in item['path'] else 'base'
            words[tag] = json.loads(payload)
    require(set(words) == {'base', 'extra'}, 'both providers')
    return words


def determinant(matrix):
    rows = [list(row) for row in matrix]
    result = Fraction(1)
    for col in range(4):
        pivot = next((r for r in range(col, 4) if rows[r][col]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            rows[pivot], rows[col] = rows[col], rows[pivot]
            result = -result
        value = rows[col][col]
        result *= value
        for r in range(col + 1, 4):
            factor = rows[r][col] / value
            for c in range(col, 4):
                rows[r][c] -= factor * rows[col][c]
    return result


def apply(rows, gate):
    kind, destination = gate[:2]
    require(0 <= destination < 704, 'register range')
    if kind == 'warp':
        operator = gate[2]
        changed = {}
        for (source, word), value in rows[destination].items():
            new = word[:-1] if word and word[-1] == -operator else word + (operator,)
            require(len(new) <= 128, 'operator-word capacity')
            changed[source, new] = value
        rows[destination] = changed
    elif kind == 'scale':
        factor = Fraction(gate[2], gate[3])
        require(factor != 0, 'invertible scale')
        rows[destination] = {key: factor * value
                             for key, value in rows[destination].items()}
    else:
        require(kind == 'add', 'known gate')
        source = gate[2]
        require(0 <= source < 704 and source != destination, 'ADD endpoints')
        factor = Fraction(gate[3], gate[4])
        for key, value in rows[source].items():
            value = rows[destination].get(key, Fraction(0)) + factor * value
            if value:
                rows[destination][key] = value
            else:
                rows[destination].pop(key, None)
    require(len(rows[destination]) <= MAX_TERMS, 'sparse-row capacity')
    require(all(value.numerator.bit_length() <= 256 and
                value.denominator.bit_length() <= 256
                for value in rows[destination].values()), 'rational capacity')


def continuation(word):
    """Literal operations after the prelude, including implicit B warps."""
    events = word['A'][word['prelude_events']:] + word['cut']
    by_position = defaultdict(list)
    require(len(word['warps']) == 58, 'operator inventory')
    for operator, record in enumerate(word['warps'], 1):
        require(0 <= record[0] <= len(word['B']), 'warp position')
        by_position[record[0]].append(['warp', record[1], operator])
    for position in range(len(word['B']) + 1):
        events.extend(by_position[position])
        if position < len(word['B']):
            events.append(word['B'][position])
    events.extend(word['restore'])
    require(len(events) <= MAX_EVENTS, 'continuation capacity')
    for gate in events:
        kind, destination = gate[:2]
        target = 112 <= destination < 224
        if kind == 'warp':
            require(not target, 'no target chart changes')
        elif kind == 'scale':
            require(Fraction(gate[2], gate[3]) != 0, 'invertible continuation')
        else:
            require(kind == 'add' and gate[2] != destination, 'elementary ADD')
            require(target or not 112 <= gate[2] < 224,
                    'target feedback into non-target')
    return events


def prelude_matrix(word):
    rows = [{} for _ in range(704)]
    for source in PARTNERS:
        rows[source][source, ()] = Fraction(1)
    for gate in word['A'][:word['prelude_events']]:
        apply(rows, gate)
    for i, source in enumerate(PARTNERS):
        require(rows[source] == {(source, ()): Fraction(1)}, 'prelude restoration')
        record = word['warps'][46 + i]
        columns = record[2]
        require(record[1] == source and len(columns) == 9 and
                len(span(columns)) == 512, 'invertible partner chart')
        image = 0
        for bit, column in enumerate(columns):
            if (word['ports'][source] >> bit) & 1:
                image ^= column
        require(image == 30, 'partner chart carries its port to line 30')
    matrix = []
    for target in TARGETS:
        expected_keys = {(source, (47 + i,)) for i, source in enumerate(PARTNERS)}
        require(set(rows[112 + target]) == expected_keys, 'partner correction support')
        matrix.append([rows[112 + target][source, (47 + i,)]
                       for i, source in enumerate(PARTNERS)])
    require(all(not row for t, row in enumerate(rows[112:224])
                if t not in TARGETS), 'no other partner correction rows')
    expected = [[Fraction(n, 4) for n in row] for row in NUMERATORS]
    require(matrix == expected, 'literal correction matrix')
    require(determinant(matrix) == Fraction(-1, 16), 'rank-four correction')
    return matrix


def projection(word, omit=False):
    rows = [{} for _ in range(704)]
    for source in PARTNERS:
        rows[source][source, ()] = Fraction(1)
    prefix = word['precondition'] + word['compensation']
    require(len(prefix) <= MAX_EVENTS, 'prefix capacity')
    for gate in prefix:
        require(112 <= gate[1] < 224, 'prefix only writes targets')
        apply(rows, gate)
    for gate in word['A'][:word['prelude_events']]:
        if not (omit and gate[0] == 'add' and gate[2] in PARTNERS):
            apply(rows, gate)
    observed_lenders = []
    for gate in continuation(word):
        if gate[0] == 'warp' and gate[2] > 50:
            require(gate[1] in LENDERS and not rows[gate[1]],
                    'new lender has a partner-source component')
            observed_lenders.append(gate[1])
        apply(rows, gate)
    require(tuple(observed_lenders) == LENDERS, 'eight lender observations')
    residual = {}
    for target in range(112):
        row = dict(rows[112 + target])
        if target in PARTNERS:
            key = (target, ())
            row[key] = row.get(key, Fraction(0)) - 1
            if not row[key]:
                del row[key]
        if row:
            residual[target] = row
    return residual


def span(vectors):
    require(len(vectors) <= 9, 'binary dimension capacity')
    result = {0}
    for vector in vectors:
        require(0 <= vector < 512, 'binary vector range')
        result |= {value ^ vector for value in result}
    return result


def cut_certificate(word):
    levels = {int(t): span(frame) for t, frame in word['target_levels'].items()}
    for target in TARGETS:
        require(levels.get(target) == {0, 30}, 'forced line-30 reader')
    # Reconstruct target frame monotonicity through A, not just its final label.
    frames = [{0} for _ in range(112)]
    for gate in word['A']:
        if gate[0] == 'warp':
            require(not 112 <= gate[1] < 224, 'no target chart changes')
            continue
        roles = gate[1:3] if gate[0] == 'add' else gate[1:2]
        for role in roles:
            if 112 <= role < 224:
                frame = span(gate[-1])
                require(frames[role - 112] <= frame, 'monotone target frame')
                frames[role - 112] = frame
    require(all(frame == levels.get(t, {0}) for t, frame in enumerate(frames)),
            'target cut frame binding')
    readers = defaultdict(set)
    for gate in word['cut']:
        require(gate[0] == 'add' and 112 <= gate[1] < 224, 'cut target ADD')
        require(Fraction(gate[3], gate[4]) != 0, 'nonzero reader')
        readers[gate[2]].add(gate[1] - 112)
    require(len(word['centers']) == 8 and set(readers) == set(word['centers']),
            'complete centre inventory')
    forced = {c for c, targets in readers.items() if set(TARGETS) & targets}
    require(forced == FORCED_CENTRES, 'four forced centre incidences')
    invoice, witnesses = Counter(), {}
    for centre, basis in zip(word['centers'], word['center_frames'], strict=True):
        frame = span(basis)
        require(len(frame) == 256, 'rank-eight producer')
        targets = readers[centre]
        zeros = sorted(t for t in targets if levels.get(t, {0}) == {0})
        require(bool(zeros), 'zero-reader contract')
        witnesses[str(centre)] = zeros[0]
        proper = {tuple(sorted(levels.get(t, {0}))) for t in targets}
        for reader in sorted(proper, key=lambda values: -len(values)):
            reader = set(reader)
            require(reader <= frame, 'nested private copy')
            rank = (len(frame).bit_length() - len(reader).bit_length())
            if rank:
                invoice[rank] += 1
            frame = reader
    require(dict(invoice) == {1: 4, 7: 4, 8: 4}, 'sharp fixed-reader cut bill')
    return {'invoice': dict(sorted(invoice.items())),
            'forced_centres': sorted(forced), 'zero_reader_witnesses': witnesses}


def check_word(word):
    require(word['report']['v'] == 112 and word['report']['h'] == 9 and
            word['report']['R'] == 480, 'word geometry')
    require(sum(len(word[s]) for s in ('precondition', 'compensation', 'A',
                                      'cut', 'B', 'restore', 'cleanup')) <= MAX_EVENTS,
            'event capacity')
    require(word['initial_corrections'] == [] and
            0 <= word['prelude_events'] <= len(word['A']), 'prelude boundary')
    require(all(not 112 <= gate[1] < 224 for gate in word['cleanup']),
            'cleanup leaves targets untouched')
    matrix = prelude_matrix(word)
    require(not projection(word), 'four-source target identity')
    residual = projection(word, omit=True)
    require(set(residual) == set(TARGETS), 'omitted correction residual support')
    require(sum(len(row) for row in residual.values()) == 8,
            'eight nonzero residual coefficients')
    result = cut_certificate(word)
    result['matrix'] = [[str(x) for x in row] for row in matrix]
    result['determinant'] = '-1/16'
    result['omitted_residual'] = {
        str(t): [[s, list(op), str(q)] for (s, op), q in sorted(row.items())]
        for t, row in sorted(residual.items())}
    return result


def controls(word):
    outcomes = []
    for name in ('correction_sign', 'operator', 'target_feedback',
                 'singular_target_scale', 'lowered_target', 'producer_frame',
                 'zero_readers'):
        changed = copy.deepcopy(word)
        if name in ('correction_sign', 'operator'):
            index = next(i for i, g in enumerate(changed['A'])
                         if g[0] == 'add' and g[2] == 33)
            if name == 'correction_sign':
                changed['A'][index][3] *= -1
            else:
                changed['A'][index - 1][2] = 46
        elif name == 'target_feedback':
            changed['B'].append(['add', 0, 112, 1, 1, []])
        elif name == 'singular_target_scale':
            changed['B'].append(['scale', 112, 0, 1, []])
        elif name == 'lowered_target':
            changed['target_levels']['23'] = []
        elif name == 'producer_frame':
            changed['center_frames'][0] = changed['center_frames'][0][1:]
        else:
            zero_targets = {g[1] - 112 for g in changed['cut']
                            if not changed['target_levels'].get(str(g[1] - 112))}
            for target in zero_targets:
                changed['target_levels'][str(target)] = [30]
            # Test the zero-reader premise directly, before A-frame consistency.
            changed['A'] = [['scale', 112 + t, 1, 1, frame]
                            for t, frame in ((int(t), f) for t, f in
                                             changed['target_levels'].items())]
        try:
            cut_certificate(changed) if name == 'zero_readers' else check_word(changed)
        except ValueError as error:
            outcomes.append({'control': name, 'rejection': str(error)})
        else:
            raise ValueError('accepted fault: ' + name)
    return outcomes


def main():
    results = {}
    for tag, word in sorted(load_words().items()):
        results[tag] = check_word(word)
        results[tag]['controls'] = controls(word)
    print(json.dumps({'status': 'PASS_T74_INHERITED_CENTRE_FLOOR',
                      'providers': results}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
