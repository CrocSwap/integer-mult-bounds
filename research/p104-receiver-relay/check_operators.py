"""Lift the native incumbent to each of the ten paths and compare terminal operators."""
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from word import check_causality, read_word, require

IN, OUT = 95914, 88


def subdivide(word, forms, routes, first_mid, last_mid):
    new_forms, new_routes = forms.copy(), routes.copy()
    insertions = {}
    for old, mid in ((IN, first_mid), (OUT, last_mid)):
        if mid is None:
            continue
        # Use an unoccupied paid identifier below the terminal range.
        new = next(i for i in range(word['first_output']) if i not in new_forms)
        source, dest = routes[old]
        new_forms[new] = forms[old]
        new_forms[old] = {new: 1}
        new_routes[new], new_routes[old] = (source, mid), (mid, dest)
        insertions[old] = new
    schedule = []
    for key in word['schedule']:
        if key in insertions:
            schedule.append(insertions[key])
        schedule.append(key)
    return schedule, new_forms, new_routes, insertions


def pullback(schedule, forms, key):
    row = {key: 1}
    for k in reversed(schedule):
        a = row.pop(k, 0)
        if a:
            for t, q in forms[k].items():
                total = row.get(t, 0) + a*q
                if total:
                    row[t] = total
                else:
                    row.pop(t, None)
    require(all(t < 0 for t in row), 'all terminal coefficients are public')
    return row


def main():
    word, forms, routes, terminals = read_word()
    y = {k: pullback(word['schedule'], forms, k) for k in (155442, 155490)}
    require(y[155442] == {~674: 1, ~780: -1}, 'literal protected difference')
    grades = Counter()
    for first in (None, 561):
        for last in (None, 239, 267, 477, 1100):
            order, modified, wires, ins = subdivide(word, forms, routes, first, last)
            check_causality(word | {'schedule': order}, modified, wires, terminals)
            legs = [a for old in (IN, OUT) for a in ([ins[old], old] if old in ins else [old])]
            ds = tuple(len(word['frames'][wires[k][1]]) - len(word['frames'][wires[k][0]])
                       for k in legs)
            require(all(d > 0 for d in ds) and sum(ds) == 7, 'seven increasing grades')
            grades[ds] += 1
            # Eliminate each new degree-two copy and compare every original row,
            # its destination and source, and the original chronological sequence.
            require([k for k in order if k in forms] == word['schedule'], 'source timing')
            for old, new in ins.items():
                require(modified[old] == {new: 1} and modified[new] == forms[old]
                        and wires[new][1] == wires[old][0]
                        and (wires[new][0], wires[old][1]) == routes[old], 'contracted leg')
            require(all(modified[k] == forms[k] and wires.get(k) == routes.get(k)
                        for k in forms if k not in ins), 'all other local operators')
            require(all(pullback(order, modified, k) == row for k, row in y.items()),
                    'exact expansion of both receiver terminals')
            if first and not last:
                broken = modified | {IN: {ins[IN]: -1}}
                require(pullback(order, broken, 155442) != y[155442], 'sign-flip control')
    require(grades == {(2, 5): 1, (1, 1, 5): 1, (2, 4, 1): 4, (1, 1, 4, 1): 4},
            'exact histogram by paid grade sequence')
    print('PASS: ten chronological paid words, 1,289 terminal operators each,')
    print('one wrong-sign rejection, verified path counts:', dict(grades))


if __name__ == '__main__':
    main()
