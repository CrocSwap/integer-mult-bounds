"""Generate the late-capture Y2 word; ywz65 + OpenAI Codex, Apache-2.0."""
import argparse
from collections import defaultdict
from fractions import Fraction as Q
from itertools import combinations, product
import json
from pathlib import Path

P = Path(__file__).resolve().parent
INPUT = P.parent / 'p104-native-channel/inputs'


def span(vs):
    out = {0}
    for v in vs:
        out |= {x ^ v for x in tuple(out)}
    return out


def build():
    w = json.loads((INPUT / 'LOWRANK-WITNESS.json').read_text())
    fixture = json.loads((INPUT / 'P104-FIXTURE.json').read_text())['section4_explicit_P104']
    roots = {tuple(2 if k == i else 2*s if k == j else 0 for k in range(8))
             for i, j in combinations(range(8), 2) for s in (-1, 1)}
    roots |= {(1, *s) for s in product((-1, 1), repeat=7) if s.count(-1) % 2 == 0}
    roots = sorted(roots - set(map(tuple, fixture['F0'] + fixture['C'])))
    coeff = {s: Q(s == 2) - Q(sum(a*b for a, b in zip(roots[2], roots[s])), 8)
             for s in range(104)}
    coeff = {s: q for s, q in coeff.items() if q}
    exceptional = {0, 1, 3, 6, 7, 12, 15, 20, 24, 29, 96, 100}
    chains = [[(502, 3), (618, 7), (681, 20), (681, 29), (842, 0), (842, 96)],
              [(559, 6), (627, 12)],
              [(541, 15), (669, 1), (669, 24), (669, 100)]]
    chains += [[(0, s)] for s in sorted(set(coeff) - exceptional)]
    full = [1 << i for i in range(9)]
    endpoint = w['final_frames']['Y2']
    source_frames = dict(w['initial_frames'])
    at = defaultdict(dict)
    for ci, chain in enumerate(chains):
        for cut, s in chain:
            at[cut][s] = ci
    captures, frames, events = [], {}, defaultdict(list)
    for ci in range(len(chains)):
        reg = f'L{ci}'
        frames[reg] = []
        events[0].append(['add', 'Y2', reg, '-1', []])

    def move(cut, reg, new):
        old = frames[reg]
        if span(old) != span(new):
            if not span(old) < span(new):
                raise ValueError('nonmonotone generated acquisition')
            events[cut].append(['transport', reg, old, new, len(new)-len(old)])
            frames[reg] = new

    for cut in range(len(w['program'])+1):
        for s, ci in sorted(at[cut].items()):
            reg = f'L{ci}'
            frame = source_frames[f'X{s}']
            move(cut, reg, frame)
            events[cut].append(['add', reg, f'X{s}', str(coeff[s]), frame])
            captures.append({'cut': cut, 'source': s, 'helper': reg, 'frame': frame,
                             'coefficient': str(coeff[s])})
        if cut < len(w['program']):
            e = w['program'][cut]
            if e[0] == 'transport':
                source_frames[e[1]] = e[3]
    end = len(w['program'])
    for ci, chain in enumerate(chains):
        reg = f'L{ci}'
        move(end, reg, endpoint)
        events[end].append(['add', 'Y2', reg, '1', endpoint])
        move(end, reg, full)
        for _, s in chain:
            events[end].append(['add', reg, f'X{s}', str(-coeff[s]), full])
    return {'schema_version': 1, 'targets': [2], 'captures': captures,
            'initial_frames': {r: [] for r in frames},
            'final_frames': {r: full for r in frames},
            'insertions': [{'completed_cut': cut, 'events': ev}
                           for cut, ev in sorted(events.items()) if ev]}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    with args.out.open('x', encoding='utf-8', newline='\n') as out:
        json.dump(build(), out, indent=2)
        out.write('\n')
