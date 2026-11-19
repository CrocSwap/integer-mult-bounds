"""Retire one exterior egress and both transfers in the private route."""
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from word import check_causality, read_word, require

A, B, C, E = 95887, 100336, 95914, 88
RECEIVER = 127
Y = {155442: Fraction(1, 2), 155490: Fraction(-1, 2)}


def add(row, src, factor):
    for j, v in src.items():
        q = row.get(j, 0) + factor * v
        if q:
            row[j] = q
        else:
            row.pop(j, None)


def released(w, old, routes, retired):
    require(retired in (A, B), 'expected one of the two exterior slots')
    surviving = B if retired == A else A
    removed = {retired, C, E}
    forms = {k:{j:q for j,q in row.items() if j not in removed}
             for k,row in old.items() if k not in removed}
    add(forms[surviving], old[retired], 1)
    require(forms[surviving] == {100334:1}, 'sum merger')
    moves = {k:p for k,p in routes.items() if k not in removed}
    word = w | {'schedule':[k for k in w['schedule'] if k not in removed]}
    return word, forms, moves


def construct(w, old, moves, retired, direct, private, slope):
    """Realize any admissible pair of chains. Insert transfers at the three released times."""
    word, forms, routes = released(w, old, moves, retired)
    require(direct[0] == private[0] == 278 and direct[-1] == private[-1] == RECEIVER and
            private.count(288) == 1, 'chain endpoints and pickup')
    # h is the shift at A, independent of which member of the pair was retired.
    sign = -1 if retired == A else 1
    h = {j:sign*q for j,q in old[retired].items()}
    private_payload = dict(old[C])
    add(private_payload, h, slope)
    events = {retired:[], C:[], E:[]}
    fresh = max(old) + 1

    def relay(event, path, initial):
        nonlocal fresh
        row = initial
        for a,b in zip(path, path[1:]):
            k = fresh
            fresh += 1
            forms[k], routes[k] = row, (a,b)
            events[event].append(k)
            row = {k:1}
        return k

    receiver_h = relay(retired, direct, h)
    i = private.index(288)
    local = relay(C, private[:i+1], private_payload)
    side = {j:q for j,q in old[E].items() if j != C}
    require(old[E][C] == 1, 'private relay coefficient')
    side[local] = 1
    receiver_private = relay(E, private[i:], side)
    for k, response in Y.items():
        require(old[k][E] == 1, 'original reader weight')
        forms[k][receiver_private] = 1
        add(forms[k], {receiver_h:1}, -slope-response)
    word['schedule'] = [j for k in w['schedule'] for j in events.get(k,[k])]
    return word, forms, routes


def span(frame):
    space = {0}
    for x in frame:
        space |= {v ^ x for v in space}
    require(len(space) == 1 << len(frame), 'independent chart labels')
    return frozenset(space)
