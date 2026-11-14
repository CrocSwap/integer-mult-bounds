#!/usr/bin/env python3
"""Exact source-bound physical check of the one productive-helper315 fusion.

Hao Yan (@FanPUYen), with substantial OpenAI Codex assistance. Apache-2.0.
The exact Gaussian interpreter is retained from DreamingOfClouds' PR7601.
This checks the declared fixed delta, not arbitrary candidate input files.
"""
import gzip
import hashlib
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'retained/token-settled'
WORD_PATH = HERE / 'retained/two-contractions/word.json.gz'
CHART_SHA = 'd7c8041af006475ddd4aa6a884d2309984c63b17ee5baa81f16d9d2b7f266b50'
WORD_SHA = 'b3b991e9fc8d9eb684d2ee80ca477a04ad72106d6eee3f41f7b2284800c25d22'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def span(vectors):
    result = {0}
    for vector in vectors:
        require(type(vector) is int and 0 < vector < 512 and vector not in result,
                'invalid frame basis')
        result |= {x ^ vector for x in result}
    return result


def references(event):
    op = event[0]
    require(op in ('ADD', 'COPY', 'MOVE', 'SCALE', 'INIT', 'CLEAR'), 'unknown opcode')
    return [event[1], event[2]] if op in ('ADD', 'COPY') else [event[1]]


def eligible(word):
    last, pairs = {}, []
    frames = [span(f) for f in word['frames']]
    for i, event in enumerate(word['program']):
        r = event[1]
        if event[0] == 'MOVE' and r in last:
            j, old = last[r]
            if (old[0] == 'MOVE' and old[3] == event[2]
                    and frames[old[2]] < frames[old[3]] < frames[event[3]]):
                pairs.append((j, i, r))
        for register in references(event):
            last[register] = (i, event)
    return pairs


def normalize(result):
    values, denominator = result
    # Common denominator across an entire vector, exact and without floats.
    while denominator and values and all((a | b) % 2 == 0 for a, b in values.values()):
        values = {k: (a // 2, b // 2) for k, (a, b) in values.items()}
        denominator -= 1
    return values, denominator


def main():
    chart_path = SOURCE / 'chart.py'
    raw = WORD_PATH.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == WORD_SHA, 'source word SHA256')
    require(hashlib.sha256(chart_path.read_bytes()).hexdigest() == CHART_SHA,
            'source chart interpreter SHA256')
    word = json.loads(gzip.decompress(raw))
    program = word['program']
    require(program[42077] == ['MOVE', 315, 729, 789, False], 'first source event')
    require(program[42156] == ['MOVE', 315, 789, 808, False], 'second source event')
    require(all(315 not in references(e) for e in program[42078:42156]),
            'intermediate reference to315')
    require(eligible(word) == [(42077, 42156, 315)], 'unique source fusion')
    main_fields = (set(word['live']) | {x + 112 for x in word['live']}
                   | set(word['hosted']['X2']) | set(word['hosted']['Y2']))
    require(315 < word['public'] and 315 not in main_fields, 'productive public helper')
    require((word['initial'][315], word['final'][315]) == (3, 127),
            'unchanged helper endpoint charts')
    frames = [word['frames'][i] for i in (729, 789, 808)]
    require([len(f) for f in frames] == [4, 5, 6], 'frame dimensions')
    require(span(frames[0]) < span(frames[1]) < span(frames[2]), 'strict nesting')
    program[42156] = ['MOVE', 315, 729, 808, False]
    del program[42077]
    require(not eligible(word), 'remaining unobserved ascending fusion')

    # run_path executes the authenticated .py source, avoiding cached bytecode.
    engine = runpy.run_path(str(chart_path), run_name='retained_chart_interpreter')
    frame, inverse = engine['frame'], engine['inverse_circuit']
    compile_gate, run = engine['compile_gate'], engine['run']
    a, b, c = map(frame, frames)
    old = inverse(a) + b + inverse(b) + c
    new = inverse(a) + c
    for label, left, right in (
            ('forward', old, new), ('adjoint', inverse(old), inverse(new))):
        left, right = list(map(compile_gate, left)), list(map(compile_gate, right))
        for column in range(512):
            require(normalize(run(left, column)) == normalize(run(right, column)),
                    label + ' column ' + str(column))
    require(engine['child_rank'](frames[0], frames[2]) == 2, 'direct rank-two child')

    good = list(map(compile_gate, new))
    bad = list(map(compile_gate, inverse(a) + frame(frames[2], with_phase=False)))
    require(any(normalize(run(good, x)) != normalize(run(bad, x)) for x in range(512)),
            'removed quadratic phase control not rejected')
    values, denominator = run(good, 0)
    rotated = ({x: (-im, re) for x, (re, im) in values.items()}, denominator)
    require(normalize((values, denominator)) != normalize(rotated),
            'global phase control not rejected')

    print(json.dumps({
        'status': 'PASS_ROLE315_PHYSICAL',
        'source_word_sha256': WORD_SHA, 'chart_sha256': CHART_SHA,
        'forward_columns': 512, 'adjoint_columns': 512, 'rank_columns': 512,
        'direct_rank': 2, 'nonobserving_events': 78,
        'eligible_before': 1, 'eligible_after': 0,
        'controls': ['removed_quadratic_phase_rejected', 'global_phase_rejected'],
        'scope': 'Exact named native delta and finite sequential-fusion family only; '
                 'complete application and inherited framework premises remain separate.'
    }, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, AssertionError) as exc:
        print(json.dumps({'status': 'FAIL_ROLE315_PHYSICAL', 'error': str(exc)}), file=sys.stderr)
        raise SystemExit(1)
