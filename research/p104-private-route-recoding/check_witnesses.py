"""Separate two independent source coordinates and a spatially disjoint side input."""
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import A, B, C, E, check_causality, read_word, released, require, span


def evaluate(word, forms, x):
    state = {~j:x.get(j,0) for j in range(len(word['initial']))}
    for k in word['schedule']:
        state[k] = sum(q*state[j] for j,q in forms[k].items())
    return state


def main():
    w, old, routes, ends = read_word()
    tests = [{674:1}, {722:1}, {674:1,722:1,1288:-Fraction(1,845660160)}]
    spaces = [span(frame) for frame in w['frames']]
    interval = {i for i,s in enumerate(spaces) if spaces[278] <= s <= spaces[127]}
    require(len(interval) == 56 and len(set(spaces[i] for i in interval)) == 56, 'interval')
    require(routes[C] == (278,288) and routes[E] == (288,127), 'released private slots')
    before = [evaluate(w,old,x) for x in tests]
    require([(a[155442],a[155490]) for a in before] == [(1,0),(0,1),(1,1)],
            'two information coordinates and side witness at the receiver')
    require(ends[155442] == ends[155490] == 127, 'receiver ownership')
    require(before[2][A] == before[2][B] == 0, 'side probe kills both original exterior payloads')
    side_sets = []
    for retired in (A, B):
        word, forms, moves = released(w,old,routes,retired)
        check_causality(word,forms,moves,ends)
        require(len(moves)==5706 and len(word['schedule'])==6995, 'three released transfers')
        for i,x in enumerate(tests):
            values = evaluate(word,forms,x)
            nonzero = {k for k in moves if values[k]}
            live = {moves[k][1] for k in nonzero} | {w['initial'][j] for j in x}
            # Collapse all copies of the same binary span before testing free sharing.
            live = {j for j,s in enumerate(spaces) if s in {spaces[a] for a in live}}
            require(127 not in live, 'empty receiver observation')
            if i<2:
                require(live == ({11,278} if i==0 else {58,278}) and
                        nonzero == ({94217} if i==0 else {94218}), 'plane support')
            else:
                side_sets.append(live)
                require(len(live)==26 and live & interval == {288}, 'side support')
            require(all(values[k] == before[i][k] for k,c in ends.items() if c!=127),
                    'exterior witness control')
    require(side_sets[0] == side_sets[1], 'common side cut for mixed merger orientations')
    print('PASS both triple releases, exact rank-two demand on the two-atom plane, '
          '26 side-live charts, sole interval pickup 288, and complete free-sharing closure.')


if __name__ == '__main__':
    main()
