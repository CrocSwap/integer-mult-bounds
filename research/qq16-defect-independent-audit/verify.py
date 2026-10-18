#!/usr/bin/env python3
"""Independent QQ16 reverse-covector audit; no predecessor code execution.

Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.
The unitary/logical-frame implication is credited to ywz65, PR2628.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
METRICS = ('P', 'A', 'K', 'native', 'cover')
FAULT_OPS = {'add', 'line', 'stage', 'current_map'}
IDENTITY = tuple(1 << i for i in range(73))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def authenticate():
    """Authenticate declarative bytes before interpreting them."""
    raw = {}
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    for item in sources['files']:
        if item['usage'] == 'input':
            data = (ROOT / item['path']).read_bytes()
            require(sha(data) == item['sha256'], 'source hash: ' + item['path'])
            raw[item['path']] = data
    for item in sources['pending_sources']:
        data = (HERE / item['path']).read_bytes()
        require(sha(data) == item['sha256'], 'snapshot hash: ' + item['path'])
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == item['git_blob'], 'snapshot Git blob: ' + item['path'])
        raw[item['path']] = data
    return (json.loads(raw['sources/PR2540-WORD.json']),
            json.loads(gzip.decompress(raw['research/joint-query/certificate.json.gz'])),
            json.loads(raw['sources/PR2628-RESULT.json']))


def apply_columns(columns, vector):
    result = 0
    for i in range(vector.bit_length()):
        if vector >> i & 1:
            result ^= columns[i]
    return result


@lru_cache(None)
def product(left, right):
    return tuple(apply_columns(left, column) for column in right)


def owner_maps(packet):
    result = {}
    for p in packet['U_ports'] + packet['T_ports']:
        names = [e[2] for e in packet['programs']['B_1_2']
                 if e[0] == 'cover_map' and e[1] == ['L', 112 + p]]
        require(len(names) == 4, 'four retained route records')
        first, second = (packet['map_registry'][n] for n in names[2:])
        g = tuple(first['owner_right_matrix_columns'])
        require(g == tuple(second['owner_right_matrix_columns']), 'route pair')
        require(len(g) == 73 and product(g, g) == IDENTITY, 'involutive owner')
        require(apply_columns(g, first['payload_translation_at_identity_owner'])
                == second['payload_translation_at_identity_owner'], 'inverse shift')
        result[p] = g
    return result


def timeline(word, packet):
    """Enumerate initialized changed fields, including zero CLEAR results."""
    early = {'X' + str(p) for p in packet['A_ports'] + packet['T_ports']}
    owned = {s + str(p) for s in ('Z', 'W') for p in range(112)}
    owned |= {'R' + name[1:] for name in early}
    initialized, active, boundary, cuts = set(early), set(), False, []
    for index, event in enumerate(word):
        op, changed = event['op'], []
        if op == 'history_boundary':
            require(not boundary and not active, 'one outside-private history boundary')
            require(all('R' + name[1:] in initialized for name in early), 'capture initialized')
            changed = [s + str(p) for p in range(112) for s in ('X', 'Y')]
            initialized.update(changed)
            boundary = True
        elif op == 'private_begin':
            require(boundary and not active, 'private begin')
            active = set(event['fields'])
            require(not (active & (owned | initialized)), 'fresh private names')
        elif op == 'private_end':
            require(active == set(event['fields']) and active <= initialized, 'private end')
            initialized.difference_update(active)
            active = set()
        elif op == 'checkpoint':
            require(not active, 'checkpoint outside private scope')
        elif op == 'clear':
            field = event['field']
            require(field in owned | active, 'CLEAR only owned storage')
            initialized.add(field)
            changed = [field]
        elif op == 'add':
            dst, src = event['dst'], event['src']
            require(dst in owned | active, 'ADD only owned destination')
            require(dst != src and {dst, src} <= initialized, 'initialized ADD operands')
            require(Q(event['coefficient']) in (1, -1, Q(1, 4), Q(-1, 4)), 'ADD alphabet')
            changed = [dst]
        elif op in ('line', 'stage', 'current_map'):
            field = event['field']
            require(boundary and field in initialized, 'initialized native/map operand')
            if op == 'line':
                require(field == 'Y' + str(event['port']) and event['sign'] in (-1, 1), 'line')
            elif op == 'stage':
                require(field.startswith('Z') and event['rank'] == 8 and event['sign'] == 1, 'stage')
            else:
                require(not active and field == 'Z' + str(event['port']), 'map outside private')
                require(type(event['inverse']) is bool, 'map direction')
            changed = [field]
        else:
            raise ValueError('unknown opcode: ' + op)
        cuts.extend((index, field) for field in changed)
    require(boundary and not active, 'complete timeline')
    return cuts, initialized


def plus(target, source, scale=Q(1)):
    for route, coefficient in source.items():
        value = target.get(route, Q(0)) + scale * coefficient
        if value:
            target[route] = value
        else:
            target.pop(route, None)


def absolute(row):
    return sum(map(abs, row.values()), Q(0))


def reverse_row(word, cut, field, maps, early, save=False):
    """One output covector; distinct defect sites are encountered once each.

    Combine equal owner terms before taking absolute values. At an owner
    operation h, a covector g becomes g*h, the reverse chronological order.
    """
    covectors = {field: {IDENTITY: Q(1)}}
    totals = dict.fromkeys(METRICS, Q(0))
    coefficients = {} if save else None
    for index in range(cut, -1, -1):
        event, op = word[index], word[index]['op']
        if op == 'history_boundary':
            for name in [s + str(p) for p in range(112) for s in ('X', 'Y')]:
                totals['P'] += absolute(covectors.pop(name, {}))
            continue
        if op in ('private_begin', 'private_end', 'checkpoint'):
            if op == 'private_begin':
                require(not any(covectors.get(n) for n in event['fields']), 'no pre-CLEAR private dirt')
            continue
        dst = event.get('dst', event.get('field'))
        row = covectors.get(dst)
        if not row:
            continue
        if op in FAULT_OPS:
            weight = absolute(row)
            totals['A'] += weight
            totals['K'] += weight * (1 + abs(Q(event['coefficient'])) if op == 'add' else 1)
            if op in ('line', 'stage'):
                totals['native'] += weight
            if op == 'current_map':
                totals['cover'] += weight
            if save:
                coefficients[index] = dict(row)
        if op == 'clear':
            covectors.pop(dst)
        elif op == 'add':
            plus(covectors.setdefault(event['src'], {}), row, Q(event['coefficient']))
        elif op == 'current_map':
            h = maps[event['port']]
            covectors[dst] = {product(g, h): a for g, a in row.items()}
        elif op not in ('line', 'stage'):
            raise ValueError('unknown reverse opcode')
    require(set(n for n, row in covectors.items() if row) <= early, 'no initial owned dirt')
    totals['P'] += sum((absolute(row) for row in covectors.values()), Q(0))
    return totals, coefficients


def feedback_guard(P, K):
    """Solve PK*u/(1-K*u) <= 2^-b uniformly for integer b>=0."""
    require(P >= 1 and K > 0, 'positive feedback constants')
    threshold, guard = K * (P + 1), 0  # b=0 is the strongest condition.
    while 2 ** guard < threshold:
        guard += 1
    require(K < 2 ** guard and P * K <= 2 ** guard - K, 'guard sufficient at b=0')
    require(P * K > 2 ** (guard - 1) - K, 'previous guard fails same inequality at b=0')
    return dict(P=str(P), K=str(K), uniform_guard_bits=guard,
                exact_threshold=str(threshold),
                previous_guard_error_ratio=str(P * K / (2 ** (guard - 1) - K)),
                guard_error_ratio=str(P * K / (2 ** guard - K)))


def calculate(word, packet, expected, progress=False):
    maps = owner_maps(packet)
    early = {'X' + str(p) for p in packet['A_ports'] + packet['T_ports']}
    cuts, final_names = timeline(word, packet)
    peaks = {k: dict(value=Q(-1), event=None, field=None) for k in METRICS}
    trace, last = [], {}
    for count, (cut, field) in enumerate(cuts):
        values, _ = reverse_row(word, cut, field, maps, early)
        last[field] = values
        trace.append([cut, field, {k: str(v) for k, v in values.items()}])
        for key, value in values.items():
            if value > peaks[key]['value']:
                peaks[key] = dict(value=value, event=cut, field=field)
        if progress and count % 400 == 0:
            print('audited', count, '/', len(cuts), flush=True)
    for key in METRICS:
        want = expected['peaks'][key]
        require(peaks[key] == dict(value=Q(want['value']), event=want['event'], field=want['field']),
                'all-cut peak: ' + key)
    final = {name: {k: str(v) for k, v in last[name].items()} for name in sorted(final_names)}
    require(final == expected['final'], 'all final field envelopes')
    faults = Counter(e['op'] for e in word if e['op'] in FAULT_OPS)
    require(len(word) == expected['events'] and len(cuts) == expected['changed_field_boundaries'], 'coverage')
    require(dict(faults) == expected['fault_ops'], 'all defect sites')
    return dict(status='PASS_QQ16_INDEPENDENT_DEFECT_AUDIT', events=len(word),
                changed_field_boundaries=len(cuts), fault_ops=dict(faults), fault_sites=sum(faults.values()),
                peaks={k: dict(v, value=str(v['value'])) for k, v in peaks.items()},
                final_fields_checked=len(final), final_sha256=sha(canonical(final)),
                reverse_trace_sha256=sha(canonical(trace)),
                feedback=feedback_guard(peaks['P']['value'], peaks['K']['value']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='create absent local receipt')
    parser.add_argument('--progress', action='store_true')
    args = parser.parse_args()
    word, packet, expected = authenticate()
    result = calculate(word, packet, expected, args.progress)
    path = HERE / 'RESULT.json'
    if args.write:
        with path.open('x') as out:
            json.dump(result, out, indent=2, sort_keys=True)
            out.write('\n')
    else:
        require(json.loads(path.read_text()) == result, 'complete local receipt')
    print(result['status'], 'all_cut_A=' + result['peaks']['A']['value'],
          'uniform_guard_bits=' + str(result['feedback']['uniform_guard_bits']))


if __name__ == '__main__':
    main()
