#!/usr/bin/env python3
"""Literal copied-query program with owned recoding workspace.

OpenAI-assisted, Apache-2.0. Uses PHYSICAL.md's eight-mode code.
Exact operator/resource replay; physical frame and tape admission are separate.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

import p19_recoding_program as code

HERE = Path(__file__).resolve().parent
N = 112
WORK = 2 * N
MODES = 3 * N
SIZE = MODES + 8
QUERY = N + 1
need = code.need


def emit(modes):
    events = [('copy', WORK + i, i) for i in range(N)]
    events += [('query', WORK + i, -QUERY) for i in range(N)]
    role = lambda i: WORK + i if i < N else MODES + i - N
    for event in code.program(modes, True):
        kind = event[0]
        if kind == 'add':
            events.append((kind, role(event[1]), role(event[2]), *event[3:]))
        else:
            events.append((kind, role(event[1]), *event[2:]))
    events += [('add', N + i, WORK + i, 1, 1) for i in range(N)]
    events += [('clear', WORK + i) for i in range(N)]
    return events


def replay(events):
    rows = [{(i, ()): Q(1)} for i in range(SIZE)]
    initialized = set()
    for event in events:
        kind, target = event[:2]
        need(0 <= target < SIZE, 'target range')
        if kind == 'copy':
            need(WORK <= target < MODES and 0 <= event[2] < N, 'owned source copy')
            rows[target] = dict(rows[event[2]])
            initialized.add(target)
        elif kind == 'clear':
            need(target >= WORK, 'clear only owned work')
            rows[target] = {}
            initialized.add(target)
        elif kind in ('map', 'query'):
            need(WORK <= target < MODES and target in initialized, 'map initialized query work')
            symbol = event[2]
            need(abs(symbol) == (QUERY if kind == 'query' else target - WORK + 1),
                 'source-bound operator label')
            rows[target] = code.mapped(rows[target], symbol)
        else:
            need(kind == 'add' and len(event) == 5, 'known scalar event')
            _, _, source, num, den = event
            need(N <= target < SIZE and 0 <= source < SIZE and target != source,
                 'source preservation and valid add operands')
            need(target < WORK or target in initialized, 'initialized add destination')
            need(source < WORK or source in initialized, 'initialized add source')
            result = dict(rows[target])
            for key, value in rows[source].items():
                result[key] = result.get(key, Q(0)) + Q(num, den) * value
                if not result[key]:
                    del result[key]
            rows[target] = result
    return rows


def precision_envelope(events, require_clean=True):
    magnitudes = [Q(1)] * WORK + [Q(0)] * (SIZE - WORK)
    errors = [Q(0)] * SIZE
    peak_magnitude, peak_error = Q(1), Q(0)
    for event in events:
        kind, target = event[:2]
        if kind == 'clear':
            magnitudes[target] = errors[target] = Q(0)
        elif kind == 'copy':
            magnitudes[target] = magnitudes[event[2]]
            errors[target] = errors[event[2]]
        elif kind == 'query':
            # A normalized complex Gaussian has infinity norm sqrt(2) < 2.
            magnitudes[target] *= 2
            errors[target] = 2 * errors[target] + 1
        elif kind == 'add':
            _, _, source, num, den = event
            coefficient = abs(Q(num, den))
            magnitudes[target] += coefficient * magnitudes[source]
            errors[target] += coefficient * errors[source] + 1
        else:
            need(kind == 'map', 'precision event vocabulary')
        peak_magnitude = max(peak_magnitude, magnitudes[target])
        peak_error = max(peak_error, errors[target])
    if require_clean:
        need(not any(magnitudes[WORK:]) and not any(errors[WORK:]),
             'precision envelope ends with exact cleared work')
    return {
        'max_component_prefix_bound': str(peak_magnitude),
        'max_component_error_per_local_epsilon': str(peak_error),
        'output_error_per_local_epsilon': str(max(errors[:WORK])),
        'convention': 'Complex coefficient modulus; input components <= 1, initial errors zero. '
                      'Each query and rational ADD has absolute local error <= epsilon; '
                      'COPY, signed permutation maps and owned CLEAR are exact. '
                      'The local error budgets must still be supplied by physical implementations.',
    }


def calculate():
    local = code.calculate()
    normalizers = json.loads((code.SOURCE / 'NORMALIZERS.json').read_text())
    a = [[Q(v) for v in row] for row in json.loads((code.SOURCE / 'CODE.json').read_text())['A']]
    inverse = [[Q(i == j) + (a[i][j] - Q(i == j)) / 13 for j in range(N)] for i in range(N)]
    expected = [{(i, ()): Q(1)} for i in range(2 * N)] + [{} for _ in range(N + 8)]
    for i in range(N):
        for j in range(N):
            if inverse[i][j]:
                word = (-QUERY,) if i == j else (-(i + 1), j + 1, -QUERY)
                expected[N + i][j, word] = inverse[i][j]
    events = emit(normalizers['mode_columns'])
    need(replay(events) == expected, 'all-input copied-query endpoint including scratch')
    counts = Counter(e[0] for e in events)
    need(counts == {'copy': 112, 'query': 112, 'map': 224, 'clear': 128, 'add': 1008},
          'complete literal forward bill')
    envelope = precision_envelope(events)
    need(precision_envelope([('add', N, 0, -1, 2)], False)['max_component_prefix_bound'] == '3/2',
         'absolute coefficient precision control')
    need(precision_envelope([('query', WORK, -QUERY), ('clear', WORK)])
         ['output_error_per_local_epsilon'] == '0', 'cleared error does not survive')
    wrong_order = events[:N] + events[2*N:2*N+1136] + events[N:2*N] + events[2*N+1136:]
    no_cleanup = events[:-N]
    no_copy = events[1:]
    controls = []
    for label, mutant in [('wrong_query_code_order', wrong_order),
                          ('missing_work_erasure', no_cleanup), ('missing_source_copy', no_copy)]:
        try:
            result = replay(mutant)
        except ValueError:
            controls.append(label)
        else:
            need(result != expected, 'mutation rejected: ' + label)
            controls.append(label)
    return {'status': 'PASS_LITERAL_FORWARD_QUERY_PROGRAM', 'input_columns': SIZE,
            'persistent_fields': 224, 'owned_fields': 120, 'events': len(events),
            'source_unchanged': True, 'owned_work_final_zero': True,
            'operator': 'X unchanged; Y += C^-1 Q^-1 X; all owned work zero',
            'bill': dict(counts), 'rank_one_query_calls': N,
            'p19_forward_calls': 20, 'p19_rank_one_query_calls': 20*N,
            'p19_extra_work_beyond_recoding_bill': {'copy': 20*N, 'add': 20*N, 'clear': 20*N},
            'precision_envelope': envelope,
            'controls': controls, 'source_sha256': local['source_sha256'],
            'recoding_generator_sha256': sha256((HERE / 'p19_recoding_program.py').read_bytes()).hexdigest(),
            'scope': 'Exact rational free-operator identity on independent owner and work columns. '
                     'Existing physical K and Q interfaces, common field layout, rational rounding '
                     'and full p19 resource admission are not proved by this finite replay.',
            'program': events}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = calculate()
    if args.write:
        (HERE / 'P19_FORWARD_PROGRAM.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'program'}, indent=2))


if __name__ == '__main__':
    main()
