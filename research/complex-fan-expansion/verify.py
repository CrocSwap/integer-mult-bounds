#!/usr/bin/env python3
"""A bounded common-source fan expansion screen on the frozen round-three word.

Apache-2.0. Cinna Davis with substantial OpenAI Codex assistance.
Native source, transport synthesis and interval arithmetic retain their credit.
"""
import argparse
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SAVING = Q('0.0030217758')
PAYLOAD = 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def span(basis):
    points = {0}
    for vector in basis:
        points |= {u ^ vector for u in tuple(points)}
    return frozenset(points)


def row_map(events):
    rows = [[Q(i == j) for j in range(3)] for i in range(3)]
    for event in events:
        op = event[1]
        a, b, k = op[1][1], op[2][1], Q(*op[3:5])
        rows[a] = [x + k * y for x, y in zip(rows[a], rows[b])]
    return rows


def controls(T, E):
    a, b, c = ('L', 0), ('L', 1), ('L', 2)
    old = [T.add(b, c, Q(2), 1), T.add(a, c, Q(3), 1)]
    new = [T.add(a, b, Q(-3, 2), 0), old[0], T.add(a, b, Q(3, 2), 2)]
    need(row_map(old) == row_map(new), 'Three arbitrary-input columns of the fan identity')
    wrong = [new[0], old[0], T.add(a, b, Q(-3, 2), 2)]
    need(row_map(old) != row_map(wrong), 'Wrong correction sign rejected')
    canonical = {'frames': [[1], [1, 2, 4], [1, 2, 4, 8, 16]],
                 'start': [0] * 3, 'final': [2] * 3}
    spaces = list(map(span, canonical['frames']))
    before = T.paid(T.synthesize(canonical, old, spaces))
    after = T.paid(T.synthesize(canonical, new, spaces))
    need(before == Counter({2: 6}) and after == Counter({2: 4, 4: 1}),
         'Positive common-frame fixture: six H2 become four H2 plus H4')
    need(E.power(4, 1 - SAVING)[1] < 2 * E.power(2, 1 - SAVING)[0],
         'Strict paid-moment gain on the positive fixture')
    return {'dirty_columns': 3, 'positive_fixture_before': dict(before),
            'positive_fixture_after': dict(after), 'wrong_sign_rejected': True}


def census(canonical, full, T, E):
    program = [e for e in full if e[0] != 'climb']
    spaces = list(map(span, canonical['frames']))
    dimensions = list(map(len, canonical['frames']))
    positions = defaultdict(list)
    for i, event in enumerate(program):
        for role in T.roles(event):
            positions[role].append(i)

    def boundary(role, index, before):
        seq = positions[role]
        k = bisect_left(seq, index) - 1 if before else bisect_right(seq, index)
        if k < 0:
            return canonical['start'][role[1]]
        if k == len(seq):
            return canonical['final'][role[1]]
        event = program[seq[k]]
        return event[4 if before else 3] if event[0] == 'warp' else event[2]

    baseline = T.paid(full)
    need(T.paid(T.synthesize(canonical, program, spaces)) == baseline,
         'Unchanged word transport reconstruction')
    classes, witnesses, counts = Counter(), {}, Counter()
    for i, first in enumerate(program):
        if not T.is_add(first):
            continue
        b, source = map(tuple, first[1][1:3])
        for j in range(i + 1, min(i + 81, len(program))):
            second = program[j]
            if second[0] == 'phase':
                break
            if not T.is_add(second):
                continue
            a, other_source = map(tuple, second[1][1:3])
            if other_source != source or a in (b, source):
                continue

            def blocks(event):
                touched = T.roles(event)
                if a in touched:
                    return True
                if T.is_add(event):
                    return tuple(event[1][1]) in (b, source)
                return bool(touched & {b, source})

            if any(blocks(event) for event in program[i + 1:j]):
                continue
            counts['fan_pairs'] += 1
            fa, fb = boundary(a, i, True), boundary(b, i, True)
            ga, gb = boundary(a, j, False), boundary(b, j, False)
            f = first[2]
            if not spaces[fa] <= spaces[fb] <= spaces[f] <= spaces[gb] <= spaces[ga]:
                continue
            counts['nested_boundary_candidates'] += 1
            aa, bb, ff, hh, gg = (dimensions[x] for x in (fa, fb, f, gb, ga))
            fd = dimensions[second[2]]
            fc = dimensions[boundary(source, j, True)]
            gc = dimensions[boundary(source, j, False)]
            need(aa <= fd <= gg and fc <= fd <= gc, 'Old monotone frame dimensions')
            delta = Counter(r for r in (bb-aa, hh-bb, gg-hh, gc-fc) if r)
            delta.subtract(r for r in (fd-aa, gg-fd, fd-fc, gc-fd) if r)
            key = tuple(sorted((r, n) for r, n in delta.items() if n))
            need(sum(r*n for r, n in key) == 0, 'Fixed-boundary rank mass conserved')
            classes[key] += 1
            witnesses.setdefault(key, (i, j, a, b, fb, gb))

    results = []
    need(set(classes) <= {(), ((1, 2), (2, -1))},
         'Only equal tariffs or the universally losing 2H1-H2 tariff occur')
    powers = {r: E.power(r, 1-SAVING) for r in range(1, 10)}
    for key, number in sorted(classes.items()):
        low = sum(n * powers[r][0 if n > 0 else 1] for r, n in key)
        high = sum(n * powers[r][1 if n > 0 else 0] for r, n in key)
        if key:
            need(low > 0, 'A candidate improved or needs further exact classification')
        else:
            need(low == high == 0, 'Unchanged-profile class')
        # A complete transport reconstruction corroborates each distinct local tariff.
        i, j, a, b, pre, post = witnesses[key]
        alpha = -Q(*program[j][1][3:5]) / Q(*program[i][1][3:5])
        changed = (program[:i] + [T.add(a, b, alpha, pre)] + program[i:j]
                   + [T.add(a, b, -alpha, post)] + program[j+1:])
        actual = Counter(T.paid(T.synthesize(canonical, changed, spaces)))
        actual.subtract(baseline)
        need(tuple(sorted((r, n) for r, n in actual.items() if n)) == key,
             'Local formula agrees with whole-word paid reconstruction')
        results.append({'delta': dict(key), 'candidates': number,
                        'moment_delta': E.display((low, high)),
                        'witness_positions': [i, j]})
    return {'counts': dict(counts), 'tariff_classes': results,
            'profitable_candidates': 0, 'baseline_paid': dict(sorted(baseline.items()))}


def run():
    for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'Changed pinned input: ' + row['path'])
    raw = gzip.decompress((ROOT / 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz').read_bytes())
    need(sha256(raw).hexdigest() == PAYLOAD, 'Frozen actual native payload')
    source = json.loads(raw)
    T = load('research/scalar-trace-compression/verify.py', 'fan_trace_synthesis')
    E = load('research/higher-moment-strictification/verify.py', 'fan_exact_intervals')
    result = {'status': 'PASS_BOUNDED_COMPLEX_FAN_EXPANSION_NO_GAIN',
              'new_kappa': None, 'saving_tested': str(SAVING), 'lookahead': 80,
              'all_savings_between_zero_and_one': True,
              'controls': controls(T, E), 'directions': {}}
    for direction, word in source['programs'].items():
        result['directions'][direction] = census(source['canonical'], word, T, E)
    return E.encoded(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run()
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_text()) == result, 'Committed census receipt')
    print(result['status'], 'no_new_kappa')
