#!/usr/bin/env python3
"""Build one incidence-separated Y0/Y1/Y2 correction. ywz65 + OpenAI Codex, Apache-2.0.

The two-independent-total shear is credited to Ross Richardson / PR2445.
This file is not imported by either checker.
"""
import argparse
from fractions import Fraction as Q
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / 'p104-native-channel' / 'inputs'


def space(vectors):
    out = {0}
    for v in vectors:
        out |= {u ^ v for u in tuple(out)}
    return out


def basis(vectors):
    out, covered = [], {0}
    for v in sorted(vectors):
        if v not in covered:
            out.append(v)
            covered |= {u ^ v for u in tuple(covered)}
    return out


def build():
    word = json.loads((INPUT / 'LOWRANK-WITNESS.json').read_text())
    f = json.loads((INPUT / 'P104-FIXTURE.json').read_text())['section4_explicit_P104']
    roots = {tuple(2 if k == i else 2*sgn if k == j else 0 for k in range(8))
             for i, j in combinations(range(8), 2) for sgn in (-1, 1)}
    roots |= {(1, *s) for s in product((-1, 1), repeat=7) if s.count(-1) % 2 == 0}
    roots = sorted(roots - set(map(tuple, f['F0'] + f['C'])))
    c = [[Q(t == s) - Q(sum(a*b for a, b in zip(roots[t], roots[s])), 8)
          for s in range(104)] for t in range(3)]
    groups = {}
    for s in range(104):
        key = tuple(t for t in range(3) if c[t][s])
        if key:
            groups.setdefault(key, []).append(s)
    ends = [basis(space(word['final_frames'][f'Y{t}'])) for t in range(3)]
    full = [1 << i for i in range(9)]
    before, after, gather, deliveries, records = [], [], [], [], []
    frames, capture = {}, {}

    def add(dst, src, q, f):
        return ['add', dst, src, str(q), f]

    def move(events, reg, f):
        old = frames[reg]
        if old != f:
            if not space(old) < space(f):
                raise ValueError('nonmonotone move')
            events.append(['transport', reg, old, f, len(f)-len(old)])
            frames[reg] = f

    for key, sources in sorted(groups.items()):
        common = basis(set.intersection(*(space(ends[t]) for t in key)))
        regs = [f'N{s}' for s in sources]
        for s, reg in zip(sources, regs):
            frames[reg] = []
            capture[s] = c[key[0]][s]
            line = word['initial_frames'][f'X{s}']
            move(before, reg, line)
            before.append(add(reg, f'X{s}', capture[s], line))
            move(before, reg, common)
        if key == (0, 1):
            ratios = {s: c[1][s]/capture[s] for s in sources}
            a = next(s for s in sources if ratios[s] == -1)
            b = next(s for s in sources if ratios[s] == 1)
            gather.extend([add(f'N{a}', f'N{b}', 1, common),
                           add(f'N{b}', f'N{a}', Q(-1, 2), common)])
            for s in sources:
                if s not in (a, b):
                    gather.extend([add(f'N{a}', f'N{s}', 1, common),
                                   add(f'N{b}', f'N{s}', ratios[s]/2, common)])
            output = [(0, f'N{a}', 1), (1, f'N{b}', 2)]
            extra = []
        else:
            if any(c[t][s] != capture[s] for t in key for s in sources):
                raise ValueError('rank-one group no longer has identical rows')
            collector = regs[0]
            gather.extend(add(collector, reg, 1, common) for reg in regs[1:])
            output, extra = [(key[0], collector, 1)], []
            for t in key[1:]:
                reg = 'E' + ''.join(map(str, key)) + '_' + str(t)
                frames[reg] = []
                move(before, reg, common)
                gather.append(add(reg, collector, 1, common))
                output.append((t, reg, 1))
                extra.append(reg)
        deliveries.extend(output)
        records.append({'targets': list(key), 'sources': sources, 'common_frame': common,
                        'extra_helpers': extra, 'collectors': [[t, r, str(q)] for t, r, q in output]})

    # Compute dirty compensation from the gather word, not from source samples.
    dirty = {r: {r: Q(1)} for r in frames}
    for _, dst, src, q, _ in gather:
        for r, v in dirty[src].items():
            dirty[dst][r] = dirty[dst].get(r, Q(0)) + Q(q)*v
    compensation = []
    for t, reg, q in deliveries:
        compensation.extend(add(f'Y{t}', src, -q*v, [])
                            for src, v in sorted(dirty[reg].items()) if v)
    before = compensation + before + gather
    collectors = {reg for _, reg, _ in deliveries}
    for reg in frames:
        if reg not in collectors:
            move(before, reg, full)
    for t, reg, q in deliveries:
        move(after, reg, ends[t])
        after.append(add(f'Y{t}', reg, q, ends[t]))
        move(after, reg, full)
    after.extend(add(dst, src, -Q(q), full) for _, dst, src, q, _ in reversed(gather))
    after.extend(add(f'N{s}', f'X{s}', -q, full) for s, q in sorted(capture.items()))
    return {'schema_version': 1, 'targets': [0, 1, 2], 'groups': records,
            'initial_frames': {r: [] for r in frames}, 'final_frames': {r: full for r in frames},
            'insertions': [{'completed_cut': 0, 'events': before},
                           {'completed_cut': len(word['program']), 'events': after}]}


def render(x, level=0):
    indent = '  ' * (level+1)
    if isinstance(x, dict):
        return '{\n' + ',\n'.join(indent + json.dumps(k) + ': ' + render(v, level+1)
                                  for k, v in x.items()) + '\n' + '  '*level + '}'
    if isinstance(x, list) and x and isinstance(x[0], (dict, list)):
        return '[\n' + ',\n'.join(indent + render(v, level+1) for v in x) + '\n' + '  '*level + ']'
    return json.dumps(x)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    with args.out.open('x', encoding='utf-8', newline='\n') as out:
        out.write(render(build()) + '\n')
