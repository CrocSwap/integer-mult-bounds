#!/usr/bin/env python3
"""Verify main-only separators by literal scalar replay, without elimination."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
WORD = HERE / 'inputs/WORD.json.gz'
PROBES = HERE / 'MAIN-PROBES.json'
WORD_PIN = 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
PROBE_PIN = '440b45249eb28596d2dbcfcff5e13dd9c9f435c6f6303aff22e2207a6b1a5aa5'
EXPECTED = (30529,30537,30551,32939,33125,33133,33140,33142,33149,
            34524,34528,35443,36324,36328,36336,39553,39581,39727,
            39785,39814,39820,39853,40538,40556,40563,40567,41491,
            42005,42477,42482,44244,44251,45638)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def frame_key(vectors):
    """Canonical GF(2) row space; high-pivot Gauss-Jordan, not source IDs."""
    rows = [int(v) for v in vectors if int(v)]
    k = 0
    for bit in range(8, -1, -1):
        hit = next((j for j in range(k, len(rows)) if rows[j] >> bit & 1), None)
        if hit is None:
            continue
        rows[k], rows[hit] = rows[hit], rows[k]
        for j in range(len(rows)):
            if j != k and rows[j] >> bit & 1:
                rows[j] ^= rows[k]
        k += 1
    need(all(0 <= v < 512 for v in vectors), 'frame outside nine axes')
    return tuple(sorted(rows[:k]))


def bind(word, probes, complete=True):
    need(word['public'] == 1501 and len(word['program']) == 76475,
         'literal source dimensions')
    mains = set(word['live']) | {i + 112 for i in word['live']}
    mains |= set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    need(len(mains) == 400 and mains <= set(range(word['public'])),
         'actual 400-main partition')
    keys = [frame_key(v) for v in word['frames']]
    need(all(len(keys[i]) == len(v) for i, v in enumerate(word['frames'])),
         'independent source frame bases')
    ids = [p['event'] for p in probes]
    need(len(set(ids)) == len(ids), 'duplicate probe cut')
    if complete:
        need(tuple(sorted(ids)) == EXPECTED, 'complete 33-cut coverage')
    else:
        need(set(ids) <= set(EXPECTED), 'control cut is in certificate scope')
    for p in probes:
        e = word['program'][p['event']]
        need(e[0] == 'MOVE' and e[4] is True and e[1] >= word['public'],
             'probe must bind actual owned MOVE')
        need((p['owner'], p['source_frame'], p['destination_frame']) == tuple(e[1:4]),
             'probe owner/source/destination binding')
        need(tuple(p['destination_key']) == keys[e[3]], 'actual destination coframe binding')
        indices = [h for h, _ in p['main_separator']]
        need(len(indices) == len(set(indices)) and set(indices) <= mains,
             'separator has unique main-only coordinates')
        need(all(Q(c).denominator == 1 for _, c in p['main_separator']),
             'integer main separator')
        need(Q(p['target_dot']) != 0, 'advertised target must be nonzero')
    return keys, mains


def replay(word, probes, *, complete=True, include_candidate_arrival=False):
    keys, mains = bind(word, probes, complete)
    count = len(probes)
    by_event = {p['event']: q for q, p in enumerate(probes)}
    by_frame = {}
    inputs = {}
    for q, p in enumerate(probes):
        by_frame.setdefault(keys[p['destination_frame']], []).append((p['event'], q))
        for h, coefficient in p['main_separator']:
            inputs.setdefault(h, [Q(0)] * count)[q] = Q(coefficient)
    vals = [inputs.get(h, [Q(0)] * count) for h in range(word['public'])]
    vals += [None] * word['owned_fields']
    charts = word['initial'].copy() + [None] * word['owned_fields']
    stats = Counter()
    observations = [0] * count
    targets = [None] * count

    def check_bank(owner, frame, clock, label, arrival=False):
        for event, q in by_frame.get(keys[frame], ()):
            before = clock < event or (include_candidate_arrival and arrival and clock == event)
            if before:
                need(vals[owner][q] == 0, 'nonzero history observation: ' + label)
                stats['bank_checks'] += 1
                if arrival:
                    observations[q] += 1

    for h, f in enumerate(word['initial']):
        check_bank(h, f, -1, 'initial', arrival=True)
    for clock, e in enumerate(word['program']):
        op, a = e[:2]
        stats[op] += 1
        if op == 'MOVE':
            old, new = e[2:4]
            need(vals[a] is not None and charts[a] == old, 'literal MOVE chronology')
            need(e[4] == (a >= word['public']), 'literal MOVE owner flag')
            check_bank(a, old, clock, 'departure')
            if clock in by_event:
                q = by_event[clock]
                targets[q] = vals[a][q]
                need(targets[q] == Q(probes[q]['target_dot']) and targets[q] != 0,
                     'nonzero target replay')
            # In normalized coordinates a completed MOVE preserves the row.
            # The physical whole-array frame map is invertible and common to B.
            check_bank(a, new, clock, 'arrival', arrival=True)
            charts[a] = new
        elif op == 'INIT':
            need(a >= word['public'] and charts[a] is None and vals[a] is None,
                 'literal fresh INIT')
            charts[a], vals[a] = e[2], [Q(0)] * count
            check_bank(a, e[2], clock, 'INIT')
        elif op == 'CLEAR':
            need(a >= word['public'] and charts[a] == e[2] and vals[a] is not None,
                 'literal owned CLEAR')
            check_bank(a, e[2], clock, 'CLEAR')
            charts[a], vals[a] = None, None
        elif op == 'SCALE':
            need(vals[a] is not None and charts[a] == e[-1], 'literal SCALE coframe')
            check_bank(a, e[-1], clock, 'SCALE before')
            coefficient = Q(e[2])
            need(coefficient != 0, 'literal nonzero SCALE')
            vals[a] = [coefficient * v for v in vals[a]]
            check_bank(a, e[-1], clock, 'SCALE after')
        elif op in ('COPY', 'ADD'):
            b = e[2]
            need(a != b and vals[a] is not None and vals[b] is not None and
                 charts[a] == charts[b] == e[-1], 'literal scalar coframe')
            check_bank(a, e[-1], clock, op + ' destination')
            check_bank(b, e[-1], clock, op + ' source')
            if op == 'COPY':
                need(a >= word['public'] and not any(vals[a]), 'fresh-zero COPY under probes')
            coefficient = Q(e[3])
            vals[a] = [x + coefficient * y for x, y in zip(vals[a], vals[b])]
            check_bank(a, e[-1], clock, op + ' result')
        else:
            raise ValueError('unknown native opcode')
    need(charts == word['final'] + [None] * word['owned_fields'], 'literal final charts')
    need(all(x is not None and x != 0 for x in targets), 'all advertised targets reached')
    need(all(x > 0 for x in observations), 'nonempty earlier histories')
    return {'cuts': len(probes), 'events': len(word['program']),
            'main_coordinates': len(mains), 'bank_checks': stats['bank_checks'],
            'earlier_arrivals': observations, 'target_values': [str(x) for x in targets]}


def run(source=WORD, probes_path=PROBES):
    raw = source.read_bytes()
    need(sha256(raw).hexdigest() == WORD_PIN, 'main-probe source hash pin')
    data = probes_path.read_bytes()
    need(sha256(data).hexdigest() == PROBE_PIN, 'main-probe certificate hash pin')
    word = json.loads(gzip.decompress(raw))
    doc = json.loads(data)
    need(doc['source_sha256'] == WORD_PIN, 'certificate source identity')
    probes = doc['candidate_probes']
    result = replay(word, probes)
    bad_cases = []
    one = deepcopy(probes[:1]); one[0]['destination_frame'] = one[0]['source_frame']
    bad_cases.append(('wrong destination', one, False, 'probe owner/source/destination binding'))
    one = deepcopy(probes[:1]); one[0]['destination_key'] = []
    bad_cases.append(('wrong coframe', one, False, 'actual destination coframe binding'))
    _, mains = bind(word, probes)
    helper = min(set(range(word['public'])) - mains)
    one = deepcopy(probes[:1]); one[0]['main_separator'] = [[helper, 1]]
    bad_cases.append(('helper-supported probe', one, False, 'separator has unique main-only coordinates'))
    one = deepcopy(probes[:1]); one[0]['main_separator'] = [[one[0]['main_separator'][0][0], 0]]
    bad_cases.append(('zero separator', one, False, 'nonzero target replay'))
    bad_cases.append(('own arrival incorrectly earlier', deepcopy(probes[:1]), True,
                      'nonzero history observation: arrival'))
    rejected = []
    for label, mutant, inclusive, message in bad_cases:
        try:
            replay(word, mutant, complete=False, include_candidate_arrival=inclusive)
        except ValueError as exc:
            need(str(exc) == message, 'specific failure control: ' + label + ': ' + str(exc))
            rejected.append(label)
        else:
            raise ValueError('accepted mutant: ' + label)
    result.update(status='PASS_MAIN_ONLY_HISTORY_SEPARATORS', source_sha256=WORD_PIN,
                  certificate_sha256=PROBE_PIN, negative_controls=rejected,
                  method='direct simultaneous rational scalar inputs; no span elimination')
    return result


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
