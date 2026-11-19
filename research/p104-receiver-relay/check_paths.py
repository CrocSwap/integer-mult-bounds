"""Reconstruct the observable stock, span quotient and complete grade-seven path set."""
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from word import check_causality, read_word, require

DONOR, RELAY, RECEIVER = 278, 288, 127
OLD_IN, OLD_OUT = 95914, 88
TERMINALS = {155442, 155490}

# Four rational separators from #7807, in A,B,C,D order.
COLUMNS = (
    {674: 1, 722: 1},
    {722: 1, 780: -1},
    {674: 1, 825: -1},
    {674: 1, 722: 1, 1288: -Fraction(1, 845660160)},
)


def span(frame):
    points = {0}
    for v in frame:
        require(0 < v < 512 and v not in points, 'dependent or out-of-range frame')
        points |= {x ^ v for x in points}
    return frozenset(points)


def live_stocks(word, forms, routes, public):
    atoms = {~j: public.get(j, 0) for j in range(len(word['initial']))}
    live = {word['initial'][j] for j in public}
    for k in word['schedule']:
        if k not in routes and k not in TERMINALS:
            continue
        atoms[k] = sum(a * atoms[s] for s, a in forms[k].items())
        if k in routes and k not in {OLD_IN, OLD_OUT} and atoms[k]:
            live.add(routes[k][1])
    require(atoms[155442] == 1, 'the protected output distinguishes zero')
    require(RECEIVER not in live, 'unmodified receiver deposits vanish')
    return live


def classify(word, forms, routes, terminals):
    check_causality(word, forms, routes, terminals)
    require(routes[OLD_IN] == (DONOR, RELAY) and routes[OLD_OUT] == (RELAY, RECEIVER),
            'removed path')
    dependants = {s: {k for k, row in forms.items() if s in row} for s in (OLD_IN, OLD_OUT)}
    require(dependants == {OLD_IN: {OLD_OUT}, OLD_OUT: TERMINALS}, 'frozen stock closure')
    require(RECEIVER not in word['initial'] and all(a != RECEIVER for a, b in routes.values()),
            'receiver has no initial stock or outgoing leg')
    require(sum(b == RECEIVER for a, b in routes.values()) - 1 == 901,
            'surviving receiver deposits')

    spaces = list(map(span, word['frames']))
    require(len(spaces) == 1103 and len(spaces[RECEIVER]) == 512, 'original atlas and receiver')
    require(all(spaces[a] <= spaces[b] or spaces[b] <= spaces[a] for a, b in routes.values()),
            'every unmodified paid transfer joins nested chart spans')
    classes = defaultdict(list)
    for chart, space in enumerate(spaces):
        classes[space].append(chart)
    require([ids for ids in classes.values() if len(ids) > 1] == [[1091, 1092]],
            'unique free communication between distinct chart labels')
    hits = [live_stocks(word, forms, routes, v) for v in COLUMNS]
    require([len(x) for x in hits] == [3, 293, 295, 26] and hits[0] == {11, 58, DONOR},
            'all-time four-column census')
    require(not any({1091, 1092} & x for x in hits), 'free class silent on every witness')
    require(not set.intersection(*hits), 'one paid sender cannot distinguish all tests')
    require([len(spaces[j]) for j in (11, 58, DONOR)] == [2, 2, 4],
            'first witness sources have ranks one, one and two')

    between = {j for j, space in enumerate(spaces) if spaces[DONOR] <= space <= spaces[RECEIVER]}
    require(between & hits[3] == {RELAY}, 'mandatory waypoint for witness D')
    lower = [j for j in between if spaces[DONOR] < spaces[j] < spaces[RELAY]]
    upper = sorted(j for j in between if spaces[RELAY] < spaces[j] < spaces[RECEIVER])
    require(lower == [561] and upper == [239, 267, 477, 1100], 'strict interval census')
    require(len(spaces[561]) == 8 and len(spaces[RELAY]) == 16
            and all(len(spaces[j]) == 256 for j in upper), 'intermediate ranks')
    paths = []
    for first in ((), tuple(lower)):
        for chart in [None, *upper]:
            last = () if chart is None else (chart,)
            paths.append((DONOR, *first, RELAY, *last, RECEIVER))
    return paths


if __name__ == '__main__':
    paths = classify(*read_word())
    require(len(paths) == len(set(paths)) == 10, 'complete positive route family')
    print('PASS: 1,103 labels, 1,102 span classes, 901 receiver deposits, four exact probes.')
    print('Necessary grade-seven paths:')
    for path in paths:
        print(' -> '.join(map(str, path)))
