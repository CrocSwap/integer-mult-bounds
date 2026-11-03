"""Exact main-signal obstruction for three paid-hop bypasses. Apache-2.0."""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
FILES = ('INPUT.json', 'PR6621-WORD.json.gz', 'PREDECESSOR-NOTICE',
         'PROOF.md', 'README.md', 'SOURCES.json', 'TASK.json',
         'VERIFY.json', 'verify.py')
WORD_SHA = '25b350a56ce11436fccf4c987da466cb002fa28dfc9b7e9d88e8b1b748b79df3'
PUBLIC, ROLES, EVENTS = 770, 799, 18561
READS = ((9013,), (9162,), (9164, 9165))
EXPECTED_READS = {
    9013: ['ADD', 497, 772, '-4', 520],
    9162: ['ADD', 231, 771, '4', 534],
    9164: ['ADD', 629, 771, '2', 117],
    9165: ['ADD', 732, 771, '1', 117],
}
PATHS = ((772, (529, 520, 595)), (771, (541, 534, 117, 594)))
STOPS = (520, 534, 117)
EXPECTED = (
    (1, 1, 2, 104, (145, 0, '-1/2')),
    (2, 1, 2, 104, (131, 2, '-1/2')),
    (3, 2, 4, 208, (131, 2, '-1/2')),
    (4, 1, 3, 156, (130, 2, '-1/2')),
    (5, 2, 5, 260, (130, 2, '-1/2')),
    (6, 1, 5, 260, (130, 2, '-1/2')),
    (7, 2, 7, 364, (130, 2, '-1/2')),
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_bound(name):
    with (HERE / name).open('rb') as handle:
        raw = handle.read((1 << 20) + 1)
    need(len(raw) <= 1 << 20, 'Package file size bound')
    return raw


def authenticate(raw):
    need(len(raw) == 91086 and sha256(raw).hexdigest() == WORD_SHA,
         'Exact retained PR6621 word bytes')
    return raw


def load_word():
    provenance = json.loads(read_bound('INPUT.json'))
    need(provenance['sha256'] == WORD_SHA and provenance['bytes'] == 91086,
         'Input metadata agrees with the retained bytes')
    raw = authenticate(read_bound('PR6621-WORD.json.gz'))
    payload = gzip.decompress(raw)
    need(len(payload) == 482221, 'Bounded decoded input')
    word = json.loads(payload)
    need(len(word['initial']) == len(word['final']) == PUBLIC, 'Public size')
    need(word['owned_fields'] == ROLES - PUBLIC
         and len(word['program']) == EVENTS
         and len(word['frames']) == 1095, 'Bounded word domain')
    need(len(word['live']) == len(set(word['live'])) == 104, 'Distinct main inputs')
    need(word['frames'][3] == [] and len(word['frames'][127]) == 9,
         'Preparation and cleanup charts')
    for role in word['live']:
        need(len(word['frames'][word['initial'][role]]) == 1,
             'A main input cannot participate in initial frame-3 preparation')
        need(len(word['frames'][word['final'][role + 112]]) == 8,
             'A main output cannot participate in terminal frame-127 cleanup')
    for index, event in EXPECTED_READS.items():
        need(word['program'][index] == event, 'Exact removed read')
    return word


def removed_reads(mask):
    need(type(mask) is int and 0 <= mask < 8, 'Three-bit bypass mask')
    return {index for bit, group in enumerate(READS)
            if mask >> bit & 1 for index in group}


def bypass(word, mask, keep_reads=False):
    removed = {stop for bit, stop in enumerate(STOPS) if mask >> bit & 1}
    skip = set() if keep_reads else removed_reads(mask)
    next_frame = {}
    for role, path in PATHS:
        for position, frame in enumerate(path[:-1]):
            target = next(f for f in path[position + 1:] if f not in removed)
            next_frame[role, frame] = target
    program = []
    for index, original in enumerate(word['program']):
        if index in skip:
            continue
        event = list(original)
        if event[0] == 'MOVE' and event[1] in (771, 772):
            if event[2] in removed:
                continue
            if event[3] in removed:
                event[3] = next_frame[event[1], event[2]]
        program.append(event)
    candidate = dict(word)
    candidate['program'] = program
    return candidate


def spans(word):
    result = []
    for basis in word['frames']:
        span = {0}
        for vector in basis:
            need(0 < vector < 512 and vector not in span, 'Independent frame basis')
            span |= {x ^ vector for x in span}
        result.append(frozenset(span))
    return result


def chart_profile(word):
    frame_spans = spans(word)
    current = list(word['initial']) + [None] * (ROLES - PUBLIC)
    paid = Counter()
    for event in word['program']:
        op, role = event[:2]
        if op == 'MOVE':
            _, _, old, new, owned = event
            need(current[role] == old and owned == (role >= PUBLIC),
                 'Transport source and ownership')
            a, b = frame_spans[old], frame_spans[new]
            need(b < a if owned else a < b, 'Strict nested transport')
            paid[abs(len(word['frames'][new]) - len(word['frames'][old]))] += 1
            current[role] = new
        elif op == 'INIT':
            need(role >= PUBLIC and current[role] is None, 'Owned initialization')
            current[role] = event[2]
        elif op == 'CLEAR':
            need(role >= PUBLIC and current[role] == event[2], 'Owned exit chart')
            current[role] = None
        else:
            need(op in ('ADD', 'COPY', 'SCALE'), 'Known scalar operation')
            need(current[role] == event[-1], 'Scalar destination chart')
            if op in ('ADD', 'COPY'):
                need(current[event[2]] == event[-1], 'Common scalar chart')
    need(current[:PUBLIC] == word['final']
         and current[PUBLIC:] == [None] * (ROLES - PUBLIC), 'Unchanged frame exits')
    return paid


def add_row(target, source, coefficient):
    result = dict(target)
    for column, value in source.items():
        result[column] = result.get(column, Q(0)) + coefficient * value
        if not result[column]:
            del result[column]
    return result


def main_map(word):
    """Primary engine: propagate all 104 symbolic main-input columns together."""
    rows = [{role: Q(1)} if role in word['live'] else {} for role in range(ROLES)]
    for event in word['program']:
        op, role = event[:2]
        if op in ('INIT', 'CLEAR'):
            rows[role] = {}
        elif op == 'SCALE':
            rows[role] = {key: Q(event[-2]) * value for key, value in rows[role].items()}
        elif op in ('ADD', 'COPY'):
            old = rows[role] if op == 'ADD' else {}
            rows[role] = add_row(old, rows[event[2]], Q(event[-2]))
        else:
            need(op == 'MOVE', 'Known operation in primary engine')
    return [rows[role + 112] for role in word['live']]


def prefix_row(word, index):
    """Second engine: pull one source functional backward through the prefix."""
    coefficients = [Q(0)] * ROLES
    coefficients[word['program'][index][2]] = Q(1)
    for event in reversed(word['program'][:index]):
        op, role = event[:2]
        if op in ('INIT', 'CLEAR'):
            coefficients[role] = Q(0)
        elif op == 'SCALE':
            coefficients[role] *= Q(event[-2])
        elif op in ('ADD', 'COPY'):
            value = coefficients[role]
            if op == 'COPY':
                coefficients[role] = Q(0)
            coefficients[event[2]] += Q(event[-2]) * value
        else:
            need(op == 'MOVE', 'Known operation in reverse engine')
    return {role: coefficients[role] for role in word['live'] if coefficients[role]}


def suffix_column(word, index):
    """Propagate one destination perturbation and check every later read coupling."""
    values = [Q(0)] * ROLES
    values[word['program'][index][1]] = Q(1)
    couplings = []
    for position in range(index + 1, EVENTS):
        event = word['program'][position]
        op, role = event[:2]
        if position in EXPECTED_READS:
            couplings.append(values[event[2]])
        if op in ('INIT', 'CLEAR'):
            values[role] = Q(0)
        elif op == 'SCALE':
            values[role] *= Q(event[-2])
        elif op in ('ADD', 'COPY'):
            source = values[event[2]]
            values[role] = (values[role] if op == 'ADD' else Q(0)) + Q(event[-2]) * source
        else:
            need(op == 'MOVE', 'Known operation in impulse engine')
    need(not any(couplings), 'Deleted reads have no interaction term')
    return [values[role + 112] for role in word['live']]


def responses(word):
    result, sources, columns = {}, {}, {}
    for index in EXPECTED_READS:
        source = prefix_row(word, index)
        column = suffix_column(word, index)
        coefficient = -Q(word['program'][index][-2])
        result[index] = [{key: coefficient * value * column[row]
                          for key, value in source.items()} if column[row] else {}
                         for row in range(104)]
        sources[index] = source
        columns[index] = [coefficient * value for value in column]
    need(sources[9162] == sources[9164] == sources[9165],
         'The two register-771 stops carry the same main functional')
    need(all(len(source) == 52 for source in sources.values()), 'Main-functional supports')
    need(sources[9013][0] == Q(1, 4) and sources[9013].get(2, 0) == 0
         and sources[9162][2] == Q(-1, 4) and sources[9162].get(0, 0) == 0,
         'Independent functional witnesses')
    expected_columns = (
        {145: Q(-2), 161: Q(-2)},
        {131: Q(2), 152: Q(2)},
        {130: Q(2), 166: Q(-2), 214: Q(-2)},
    )
    for group, expected in zip(READS, expected_columns):
        actual = {role + 112: sum(columns[index][row] for index in group)
                  for row, role in enumerate(word['live'])
                  if sum(columns[index][row] for index in group)}
        need(actual == expected, 'Explicit outer-product output vectors')
    return result


def rational_rank(rows):
    pivots = {}
    for original in rows:
        row = dict(original)
        for column, pivot in pivots.items():
            if column in row:
                row = add_row(row, pivot, -row[column])
        if row:
            column = min(row)
            scale = row[column]
            pivots[column] = {key: value / scale for key, value in row.items()}
    return len(pivots)


def record(word, mask, before, response, paid_before):
    candidate = bypass(word, mask)
    after, paid_after = main_map(candidate), chart_profile(candidate)
    difference = [add_row(a, b, Q(-1)) for a, b in zip(after, before)]
    factorized = [{} for _ in range(104)]
    for index in sorted(removed_reads(mask)):
        factorized = [add_row(a, b, Q(1)) for a, b in zip(factorized, response[index])]
    need(difference == factorized, 'All main coefficients agree across both engines')
    entries = [(role + 112, key, str(value))
               for role, row in zip(word['live'], difference)
               for key, value in sorted(row.items())]
    rank = rational_rank(difference)
    need(rank == bool(mask & 1) + bool(mask & 6), 'Sharp rank formula')
    summary = (mask, rank, sum(bool(row) for row in difference), len(entries), entries[0])
    need(summary == EXPECTED[mask - 1], 'Complete seven-case certificate')
    delta = Counter(paid_after)
    delta.subtract(paid_before)
    need(sum(key * count for key, count in delta.items()) == 0, 'Unchanged paid rank mass')
    if mask == 7:
        need({key: value for key, value in delta.items() if value}
             == {1: -3, 4: -1, 5: -1, 6: 2}, 'Exact maximal saving profile')
    return {'mask': mask, 'defect_rank': rank, 'changed_rows': summary[2],
            'changed_entries': len(entries), 'witness': entries[0],
            'paid_delta': {str(key): value for key, value in sorted(delta.items()) if value}}


def rejected(action):
    try:
        action()
    except ValueError:
        return True
    return False


def run():
    word = load_word()
    before, paid = main_map(word), chart_profile(word)
    response = responses(word)
    records = [record(word, mask, before, response, paid) for mask in range(1, 8)]
    raw = read_bound('PR6621-WORD.json.gz')
    need(rejected(lambda: authenticate(raw[:-1] + bytes([raw[-1] ^ 1]))),
         'A source-byte mutation must reject')
    need(bypass(word, 0) == word, 'Identity transformation positive control')
    for bit in range(3):
        need(rejected(lambda bit=bit: chart_profile(bypass(word, 1 << bit, True))),
             'A retained read at a bypassed chart must reject')
    bad = deepcopy(response)
    bad[9013] = [{key: -value for key, value in row.items()} for row in bad[9013]]
    need(rejected(lambda: record(word, 1, before, bad, paid)),
         'A reversed response sign must reject')
    hashes = {name: sha256(read_bound(name)).hexdigest() for name in FILES}
    return {'status': 'PASS_REMAINING_HOP_MAIN_SIGNAL', 'cases': records,
            'main_shape': [104, 104], 'source_sha256': WORD_SHA,
            'controls': 6, 'package_sha256': hashes,
            'scope': 'Seven bypasses; initial frame-3 and terminal frame-127 corrections; no new kappa'}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
    print('PASS_REMAINING_HOP_MAIN_SIGNAL')
