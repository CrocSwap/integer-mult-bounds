"""Explicit optional construction; the verifier never imports this file."""
import argparse
import json
from fractions import Fraction
from pathlib import Path

H = Path(__file__).resolve().parent


def construct(clean=False):
    w = json.loads((H.parent / 'p104-native-channel/inputs/LOWRANK-WITNESS.json').read_text())
    c = json.loads((H / 'inputs/CIRCUIT.json').read_text())
    cuts = {r['completed_cut']: r['events'] for r in c['insertions']}
    events = []
    for cut in range(len(w['program']) + 1):
        events.extend(cuts.get(cut, []))
        if cut < len(w['program']):
            events.append(w['program'][cut])
    initial = w['final_frames'] | c['final_frames']
    final = w['initial_frames'] | c['initial_frames']
    dual = [['sign', 'X' + str(i), '-1', initial['X' + str(i)]] for i in range(104)]
    for e in reversed(events):
        if e[0] == 'transport':
            dual.append(['transport', e[1], e[3], e[2], e[4]])
        elif e[0] == 'add':
            dual.append(['add', e[2], e[1], e[3], e[4]])
        elif e[0] == 'copy':
            dual.append(['add', e[2], e[1], '1', e[3]])
        elif e[0] == 'zero':
            dual.append(['erase', e[1], e[2]])
        elif e[0] == 'erase':
            dual.append(['zero', e[1], e[2]])
        else:
            raise ValueError(e)
    dual.extend(['sign', 'X' + str(i), '-1', final['X' + str(i)]] for i in range(104))
    if clean:
        completed, gathers, climb = [], [], None
        for event in dual:
            if event[0] == 'zero':
                gathers, climb = [], None
            elif event[0] == 'add' and event[1] == 'C':
                gathers.append(event)
            elif event[0] == 'transport' and event[1] == 'C':
                climb = event
            elif event[0] == 'erase':
                _, reg, line, cap, rank = climb
                completed.append(['transport',reg,cap,line,rank])
                for _,reg,source,coefficient,frame in reversed(gathers):
                    completed.append(['add',reg,source,str(-Fraction(coefficient)),frame])
                event = ['erase','C',line]
            completed.append(event)
        dual = completed
    return dict(schema_version=1, initial_frames=initial, final_frames=final, program=dual)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--clean', action='store_true')
    a = p.parse_args()
    with a.out.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(construct(a.clean), f, separators=(',', ':'))
        f.write('\n')
