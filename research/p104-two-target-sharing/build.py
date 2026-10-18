#!/usr/bin/env python3
"""Generate the fixed two-target witness; verify.py does not import this file.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def span(basis):
    result = {0}
    for v in basis:
        result |= {x ^ v for x in tuple(result)}
    return result


def basis(values):
    out, seen = [], {0}
    for v in sorted(values):
        if v not in seen:
            out.append(v)
            seen |= {x ^ v for x in tuple(seen)}
    if seen != values:
        raise ValueError("not a binary subspace")
    return out


def roots(fixture):
    rows = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            rows.add(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            rows.add((1, *signs))
    puncture = fixture['section4_explicit_P104']
    return sorted(rows - set(map(tuple, puncture['F0'] + puncture['C'])))


def build():
    source = ROOT / 'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'
    word = json.loads(source.read_text())
    ports = roots(json.loads((source.parent / 'P104-FIXTURE.json').read_text()))
    correction = [[Fraction(int(t == s)) - Fraction(sum(a*b for a, b in
                   zip(ports[t], ports[s])), 8) for s in range(104)] for t in (0, 1)]
    supports = [{s for s, c in enumerate(row) if c} for row in correction]
    shared = sorted(supports[0] & supports[1])
    union = sorted(supports[0] | supports[1])
    exclusive = [sorted(supports[t] - set(shared)) for t in (0, 1)]
    capture = {s: correction[0][s] or correction[1][s] for s in union}
    ratios = {s: correction[1][s] / capture[s] for s in shared}
    a = next(s for s in shared if ratios[s] == -1)
    b = next(s for s in shared if ratios[s] == 1)
    full = [1 << i for i in range(9)]
    ends = [basis(span(word['final_frames'][f'Y{t}'])) for t in (0, 1)]
    common = basis(span(ends[0]) & span(ends[1]))
    before, after, gather = [], [], []
    frames = {f'N{s}': [] for s in union}

    def add(events, dst, src, coefficient, frame):
        events.append(['add', dst, src, str(coefficient), frame])

    def move(events, s, to):
        reg = f'N{s}'
        old = frames[reg]
        if not span(old) <= span(to):
            raise ValueError('nonmonotone correction transport')
        events.append(['transport', reg, old, to, len(to)-len(old)])
        frames[reg] = to

    for t in (0, 1):
        for s in sorted(supports[t]):
            add(before, f'Y{t}', f'N{s}', -correction[t][s] / capture[s], [])
    for s in union:
        line = word['initial_frames'][f'X{s}']
        move(before, s, line)
        add(before, f'N{s}', f'X{s}', capture[s], line)
        room = common if s in shared else ends[0 if s in supports[0] else 1]
        move(before, s, room)
    for t, group in enumerate(exclusive):
        for s in group[1:]:
            add(gather, f'N{group[0]}', f'N{s}', 1, ends[t])
    add(gather, f'N{a}', f'N{b}', 1, common)
    add(gather, f'N{b}', f'N{a}', Fraction(-1, 2), common)
    for s in shared:
        if s not in (a, b):
            add(gather, f'N{a}', f'N{s}', 1, common)
            add(gather, f'N{b}', f'N{s}', ratios[s] / 2, common)
    before.extend(gather)
    collectors = [exclusive[0][0], exclusive[1][0], a, b]
    for s in union:
        if s not in collectors:
            move(before, s, full)
    for t in (0, 1):
        add(after, f'Y{t}', f'N{exclusive[t][0]}', 1, ends[t])
    for t, s, coefficient in [(0, a, 1), (1, b, 2)]:
        move(after, s, ends[t])
        add(after, f'Y{t}', f'N{s}', coefficient, ends[t])
    for s in collectors:
        move(after, s, full)
    for _, dst, src, coefficient, _ in reversed(gather):
        add(after, dst, src, -Fraction(coefficient), full)
    for s in union:
        add(after, f'N{s}', f'X{s}', -capture[s], full)
    return {
        'schema_version': 1,
        'source_witness_sha256': sha256(source.read_bytes()).hexdigest(),
        'targets': [0, 1], 'shared': shared, 'exclusive': exclusive,
        'shared_pivots': [a, b], 'shared_frame': common,
        'capture_coefficients': {str(s): str(capture[s]) for s in union},
        'initial_frames': {f'N{s}': [] for s in union},
        'final_frames': {f'N{s}': full for s in union},
        'insertions': [{'completed_cut': 0, 'events': before},
                       {'completed_cut': len(word['program']), 'events': after}],
    }


def separate():
    """Literal no-sharing comparison: one dirty helper per nonzero entry."""
    source = ROOT / 'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'
    word = json.loads(source.read_text())
    ports = roots(json.loads((source.parent / 'P104-FIXTURE.json').read_text()))
    full = [1 << i for i in range(9)]
    before, after, initial, final = [], [], {}, {}
    for t in (0, 1):
        end = basis(span(word['final_frames'][f'Y{t}']))
        for s in range(104):
            c = Fraction(int(t == s)) - Fraction(sum(a*b for a, b in zip(ports[t], ports[s])), 8)
            if not c:
                continue
            reg, line = f'N{t}_{s}', word['initial_frames'][f'X{s}']
            initial[reg], final[reg] = [], full
            before.extend([
                ['add', f'Y{t}', reg, '-1', []],
                ['transport', reg, [], line, 1],
                ['add', reg, f'X{s}', str(c), line],
                ['transport', reg, line, end, 7],
            ])
            after.extend([
                ['add', f'Y{t}', reg, '1', end],
                ['transport', reg, end, full, 1],
                ['add', reg, f'X{s}', str(-c), full],
            ])
    return {
        'schema_version': 1, 'targets': [0, 1],
        'source_witness_sha256': sha256(source.read_bytes()).hexdigest(),
        'initial_frames': initial, 'final_frames': final,
        'insertions': [{'completed_cut': 0, 'events': before},
                       {'completed_cut': len(word['program']), 'events': after}],
    }


def render(value, depth=0):
    """One literal event per line, while retaining readable object structure."""
    indent = '  ' * (depth+1)
    if isinstance(value, dict):
        fields = [indent + json.dumps(k) + ': ' + render(v, depth+1)
                  for k, v in sorted(value.items())]
        return '{\n' + ',\n'.join(fields) + '\n' + '  '*depth + '}'
    if isinstance(value, list) and value and isinstance(value[0], (dict, list)):
        return '[\n' + ',\n'.join(indent + render(v, depth+1) for v in value) + '\n' + '  '*depth + ']'
    return json.dumps(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--separate', action='store_true', help='emit the no-sharing comparison')
    args = parser.parse_args()
    with args.out.open('x') as out:
        out.write(render(separate() if args.separate else build()) + '\n')


if __name__ == '__main__':
    main()
