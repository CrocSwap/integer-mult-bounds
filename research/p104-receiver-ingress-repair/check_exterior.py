"""Pull the exterior pulse equations back to the six core inputs at chart 278."""
from fractions import Fraction
from functools import cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from word import read_word, check_causality, require


def add(row, source, scalar):
    for i, a in source.items():
        q = row.get(i, 0) + scalar*a
        if q:
            row[i] = q
        else:
            row.pop(i, None)


def rank(rows):
    pivots = {}
    for source in rows:
        row = dict(source)
        while row:
            col = min(row)
            if col not in pivots:
                pivots[col] = {k: Fraction(a)/row[col] for k, a in row.items()}
                break
            add(row, pivots[col], -row[col])
    return len(pivots)


def main():
    w, forms, moves, terminals = read_word()
    check_causality(w, forms, moves, terminals)
    schedule = w['schedule']
    ins = [k for k in schedule if k in moves and moves[k][1] == 278]
    outs = [k for k in schedule if k in moves and moves[k][0] == 278 and k != 95914]
    core = [k for k in ins if moves[k][0] == 3]
    require(core == [94953, 95493, 95884, 95982, 96109, 100334]
            and len(ins) == 10 and len(outs) == 9, 'full chart port counts')
    require(278 not in w['initial'] and 278 not in terminals.values(), 'chart 278 local boundary')
    require(127 not in w['initial'] and all(a != 127 for a,b in moves.values()),
            'receiver has no primary stock or paid outputs')
    require({a for a,b in moves.values() if b == 278} == {3, 11, 58}, 'three original senders')
    require(all(b != 3 for a,b in moves.values()), 'core sender has only public stock')
    edges = {k for k,(a,b) in moves.items() if b in (11, 58)}
    require(max(schedule.index(k) for k in edges) < min(schedule.index(k) for k in outs),
            'all edge-sender inputs arrive before first surviving outgoing move')
    require(max(schedule.index(k) for k in ins) < min(schedule.index(k) for k in outs),
            'all original ingress precedes the surviving egress')
    require(all(set(forms[k]) <= set(ins) for k in outs), 'native egress has only chart ingress')
    require({k for k,row in forms.items() if 95914 in row} == {88} and
            {k for k,row in forms.items() if 88 in row} == {155442,155490},
            'deleted route has no exterior readers')

    @cache
    def expand(k):
        if k < 0:
            return {~k: 1}
        row = {}
        for source, q in forms[k].items():
            add(row, expand(source), q)
        return row

    edge_stock = sorted(edges) + [~j for j,c in enumerate(w['initial']) if c in (11,58)]
    require(len(edge_stock) == 12 and rank([expand(k) for k in edge_stock + core]) == 18,
            'edge stock and old core messages are jointly independent')
    require(set().union(*(expand(k).keys() for k in core)) <=
            {j for j,c in enumerate(w['initial']) if c == 3}, 'public core coordinates')

    # Give the nine outgoing values independent tags. Outside chart 278 all
    # surviving operations are fixed. A tag at a paid egress overwrites its
    # original definition, so each column is the response to a change there.
    response = {}
    for k in schedule:
        row = {}
        if k in outs:
            row[k] = 1
        elif k not in (88,95914):
            for j, q in forms[k].items():
                add(row, response.get(j, {}), q)
        response[k] = row
    exterior = [k for k,c in terminals.items() if c != 127]
    require(len(exterior) == 387 and rank([response[k] for k in exterior]) == 8,
            'rank of all exterior observations on nine egresses')
    require(all(response[k].get(95887,0) == response[k].get(100336,0) for k in exterior),
            'unique unobserved opposite egress shifts')
    test = (154880,154881,154887,154895,154950,154959)
    expected = [
        [0,-1,0,0,0,0], [0,-1,1,0,1,0], [Fraction(-1,4),0,0,0,0,0],
        [0,0,-1,0,-1,-1], [0,-1,Fraction(-1,4),0,0,0], [Fraction(-1,4),1,0,1,0,0],
    ]
    projected = []
    for t, values in zip(test, expected, strict=True):
        require(t in exterior, 'all six witnesses are exterior')
        row = {}
        for k, coefficient in response[t].items():
            add(row, forms[k], coefficient)
        require([row.get(c,0) for c in core] == values, 'wrong projected row')
        projected.append({i: row[i] for i in core if i in row})
    require(rank(projected) == 6, 'six independent requirements modulo the two edge senders')
    print('PASS 387 exterior outputs, full pulse rank 8/9, unique opposite-shift kernel.')
    print('PASS six explicit exterior terminals force rank six modulo the 12-dimensional edge stock.')


if __name__ == '__main__':
    main()
