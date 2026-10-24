#!/usr/bin/env python3
"""Literal owned-work recodings from PHYSICAL.md, sections 39--49.

Uses the source's eight-mode construction and signed normalizers. Apache-2.0;
OpenAI assistance. Exact rational free-word replay, not a tape-cost certificate.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'coded-native-caller'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def program(modes, inverse):
    denominator = 52 if inverse else 4
    events = [('map', i, i + 1) for i in range(112)]
    events += [('clear', 112 + k) for k in range(8)]
    for k, column in enumerate(modes):
        for i, value in enumerate(column):
            if value:
                events.append(('add', 112 + k, i, value, 1))
    for i in range(112):
        for k in range(8):
            if modes[k][i]:
                events.append(('add', i, 112 + k, -modes[k][i], denominator))
    events += [('clear', 112 + k) for k in range(8)]
    events += [('map', i, -(i + 1)) for i in range(112)]
    return events


def mapped(row, symbol):
    result = {}
    for (origin, word), value in row.items():
        path = word[1:] if word and word[0] == -symbol else (symbol,) + word
        result[origin, path] = value
    return result


def replay(events, initial=None):
    rows = ([{(i, ()): Q(1)} for i in range(120)] if initial is None
            else [dict(row) for row in initial])
    for event in events:
        kind, target = event[:2]
        need(type(target) is int and 0 <= target < 120, 'target range')
        if kind == 'clear':
            need(112 <= target < 120 and len(event) == 2, 'only owned work cleared')
            rows[target] = {}
        elif kind == 'map':
            need(target < 112 and len(event) == 3, 'owner monomial shape')
            symbol = event[2]
            need(abs(symbol) == target + 1, 'owner-specific K map')
            rows[target] = mapped(rows[target], symbol)
        else:
            need(kind == 'add' and len(event) == 5, 'known scalar event')
            _, _, source, numerator, denominator = event
            need(0 <= source < 120 and source != target, 'distinct source')
            coefficient = Q(numerator, denominator)
            result = dict(rows[target])
            for key, value in rows[source].items():
                result[key] = result.get(key, Q(0)) + coefficient * value
                if not result[key]:
                    del result[key]
            rows[target] = result
    return rows


def expected(matrix):
    rows = []
    for i, coefficients in enumerate(matrix):
        row = {}
        for j, value in enumerate(coefficients):
            if value:
                row[j, () if i == j else (-(i + 1), j + 1)] = value
        rows.append(row)
    return rows + [{} for _ in range(8)]


def calculate():
    paths = [SOURCE / name for name in ('NORMALIZERS.json', 'CODE.json', 'PHYSICAL.md')]
    pins = {p.name: sha256(p.read_bytes()).hexdigest() for p in paths}
    normalizers = json.loads(paths[0].read_text())
    need(normalizers['code_sha256'] == pins['CODE.json'], 'normalizer/code source binding')
    modes = normalizers['mode_columns']
    need(len(modes) == 8 and all(len(c) == 112 for c in modes), 'mode dimensions')
    need(all(v in (-1, 0, 1) for c in modes for v in c), 'signed mode coefficients')
    need(all(sum(bool(v) for v in c) == 56 for c in modes), 'mode support sizes')
    a = [[Q(x) for x in row] for row in json.loads(paths[1].read_text())['A']]
    identity = [[Q(i == j) for j in range(112)] for i in range(112)]
    reports, programs, outputs = {}, {}, {}
    controls = []
    for inverse, label in ((False, 'C'), (True, 'C_inverse')):
        denominator = 52 if inverse else 4
        matrix = [[identity[i][j] - Q(sum(c[i] * c[j] for c in modes), denominator)
                   for j in range(112)] for i in range(112)]
        target = ([[Q(i == j) + (a[i][j] - Q(i == j)) / 13 for j in range(112)]
                   for i in range(112)] if inverse else a)
        need(matrix == target, label + ' source matrix equality')
        events = program(modes, inverse)
        actual = replay(events)
        want = expected(target)
        need(actual == want, label + ' all owner and dirty-work input columns')
        need(not any(actual[112:]), label + ' final owned work zero')
        need(all(origin < 112 for row in actual[:112] for origin, _ in row),
             label + ' arbitrary work input removed')
        counts = Counter(e[0] for e in events)
        need(counts == {'map': 224, 'clear': 16, 'add': 896}, label + ' literal bill')
        mutations = {
            'missing_initial_clear': events[:112] + events[113:],
            'missing_terminal_clear': events[:1016] + events[1017:],
            'missing_output_map': events[:-1],
        }
        changed = list(events)
        index = next(i for i, e in enumerate(events) if e[0] == 'add' and e[1] < 112)
        e = changed[index]
        changed[index] = (*e[:3], -e[3], e[4])
        mutations['wrong_update_sign'] = changed
        for name, mutant in mutations.items():
            need(replay(mutant) != want, label + ' control ' + name)
            controls.append(label + ':' + name)
        programs[label], outputs[label] = events, actual
        reports[label] = {'events': len(events), 'bill': dict(counts),
                          'input_columns': 120, 'output_rows': 120,
                          'work_input_independent': True, 'work_final_zero': True}
    for first, second in (('C', 'C_inverse'), ('C_inverse', 'C')):
        need(replay(programs[second], outputs[first]) == expected(identity),
             'composed recodings restore owners and erase work')
    return {'status': 'PASS_LITERAL_OWNED_RECODING_PROGRAM', 'source_sha256': pins,
            'orientations': reports, 'controls': controls, 'programs': programs,
            'scope': 'Exact arbitrary-input operator and owned scalar-work endpoint over formal K maps. '
                     'K implementation uses the pinned normalizer contract; full p19 native admission '
                     'and fixed-denominator precision/tape costs are not established here.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = calculate()
    if args.write:
        (HERE / 'P19_RECODING_PROGRAM.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'programs'}, indent=2))


if __name__ == '__main__':
    main()
