#!/usr/bin/env python3
"""Build cross-incidence Y0/Y1/Y2 collectors. ywz65 + OpenAI Codex, Apache-2.0.

The two-independent-total shear is credited to Ross Richardson / PR2445.
Adapted from the PR2460 builder by ywz65. Its original groups and two-total shear remain credited. The late-exclusive component is retained literally from CubeJerry / PR2504. This file is not imported by either checker.
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


def cross_only():
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
            if key == (0, 1, 2):
                output = [(2, collector, 1)]
                for t in [0, 1]:
                    reg = 'C012_' + str(t)
                    frames[reg] = []
                    move(before, reg, common)
                    gather.append(add(reg, collector, 1, common))
                    extra.append(reg)
            elif key in [(0, 2), (1, 2)]:
                reg = 'C012_' + str(key[0])
                move(gather, reg, common)
                gather.append(add(collector, reg, 1, common))
                gather.append(add(reg, collector, -1, common))
                output = [(key[0], collector, 1), (2, reg, -1)]
            elif len(key) != 1:
                raise ValueError('unexpected group')
        deliveries.extend(output)
        records.append({'targets': list(key), 'sources': sources, 'common_frame': common,
                        'extra_helpers': extra, 'collectors': [[t, r, str(q)] for t, r, q in output]})

    # Compute dirty compensation from the gather word, not from source samples.
    dirty = {r: {r: Q(1)} for r in frames}
    for event in gather:
        if event[0] != 'add':
            continue
        _, dst, src, q, _ = event
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
    after.extend(add(e[1], e[2], -Q(e[3]), full) for e in reversed(gather) if e[0] == 'add')
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


def touches(event, registers):
    return event[1] in registers or event[0] == 'add' and event[2] in registers


def build():
    """Compose the new cross-group construction with PR2504's exact component."""
    from hashlib import sha256
    from copy import deepcopy
    manifest = json.loads((HERE / 'PREDECESSORS.json').read_text())
    for record in manifest['retained']:
        if sha256((HERE / record['path']).read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('retained predecessor changed')
    old = json.loads((HERE / 'inputs/PR2460-CIRCUIT.json').read_text())
    late = json.loads((HERE / 'inputs/PR2504-CIRCUIT.json').read_text())
    result = cross_only()
    exclusive = next(g['sources'] for g in old['groups'] if g['targets'] == [2])
    removed = {'N' + str(s) for s in exclusive}
    added = set(late['initial_frames']) - set(old['initial_frames'])
    for field in ('initial_frames', 'final_frames'):
        result[field] = {r: f for r, f in result[field].items() if r not in removed}
        result[field].update({r: deepcopy(late[field][r]) for r in sorted(added)})
    result['groups'] = [g for g in result['groups'] if g['targets'] != [2]]
    result['late_acquisition'] = deepcopy(late['late_acquisition'])
    insertions = {i['completed_cut']: [e for e in i['events'] if not touches(e, removed)]
                  for i in result['insertions']}
    for insertion in late['insertions']:
        insertions.setdefault(insertion['completed_cut'], []).extend(
            deepcopy(e) for e in insertion['events'] if touches(e, added))
    result['insertions'] = [{'completed_cut': cut, 'events': events}
                            for cut, events in sorted(insertions.items())]
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--cross-only', action='store_true')
    args = parser.parse_args()
    result = cross_only() if args.cross_only else build()
    with args.out.open('x', encoding='utf-8', newline='\n') as output:
        output.write(render(result) + '\n')
