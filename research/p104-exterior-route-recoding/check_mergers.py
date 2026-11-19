"""Build each port retirement and two complete repaired words, comparing every output."""
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_rigidity import A, B, add
from word import check_causality, read_word, require


READER = {155442: Fraction(1, 2), 155490: Fraction(-1, 2)}


def merge(w, old, routes, retired):
    survivor = B if retired == A else A
    fused = dict(old[survivor])
    add(fused, old[retired], 1)
    require(fused == {100334: 1}, 'the two payloads sum to one earlier arrival')
    forms = {k: {j: q for j, q in row.items() if j != retired}
             for k, row in old.items() if k != retired}
    forms[survivor] = fused
    moves = {k: e for k, e in routes.items() if k != retired}
    word = w | {'schedule': [k for k in w['schedule'] if k != retired]}
    return word, forms, moves


def repair(w, old, routes, retired, path):
    require(path[0] == 278 and path[-1] == 127, 'correct repair endpoints')
    word, forms, moves = merge(w, old, routes, retired)
    pos = w['schedule'].index(retired)
    new_ids = list(range(max(old) + 1, max(old) + len(path)))
    word['schedule'][pos:pos] = new_ids
    for i, k in enumerate(new_ids):
        forms[k] = old[retired] if i == 0 else {new_ids[i - 1]: 1}
        moves[k] = (path[i], path[i + 1])
    sign = 1 if retired == A else -1
    for k, q in READER.items():
        forms[k][new_ids[-1]] = sign * q
    return word, forms, moves, new_ids


def pullback(order, forms, key):
    row = {key: 1}
    for k in reversed(order):
        q = row.pop(k, 0)
        if q:
            add(row, forms[k], q)
    require(all(j < 0 for j in row), 'adjoint terminates on public atoms')
    return row


def compare(w, old, new, forms, moves, ends, retired, new_ids):
    check_causality(new, forms, moves, ends)
    survivor = B if retired == A else A
    # The scalar difference of each common row is a multiple of the retired
    # value. The coefficient is propagated simultaneously on all public inputs.
    delta = {}
    for k in new['schedule']:
        if k == survivor:
            joint = dict(old[survivor])
            add(joint, old[retired], 1)
            require(forms[k] == joint and not any(delta.get(j, 0) for j in joint),
                    'survivor receives the sum of the two original payloads')
            delta[k] = 1
        elif k in new_ids:
            if k == new_ids[0]:
                require(forms[k] == old[retired] and not any(delta.get(j, 0) for j in forms[k]),
                        'first leg sends the retired payload')
                delta[k] = 1
            else:
                delta[k] = sum(q * delta[j] for j, q in forms[k].items())
        else:
            originals = {j: q for j, q in forms[k].items() if j not in new_ids}
            require(originals == {j: q for j, q in old[k].items() if j != retired},
                    'all other original coefficients preserved')
            delta[k] = sum(q * delta.get(j, 0) for j, q in forms[k].items()) - old[k].get(retired, 0)
    errors = {k: delta[k] for k in ends if delta[k]}
    sign = -1 if retired == A else 1
    expected = {} if new_ids else {k: sign * q for k, q in READER.items()}
    require(errors == expected, 'whole-word terminal operator comparison')
    for k in READER:
        orig = pullback(w['schedule'], old, k)
        add(orig, pullback(w['schedule'], old, retired), expected.get(k, 0))
        require(pullback(new['schedule'], forms, k) == orig, 'independent public-coordinate adjoint')


def main():
    w, old, routes, ends = read_word()
    require(routes[A] == (278, 561) and routes[B] == (278, 660) and
            [len(w['frames'][c]) for c in (278, 561, 660, 127)] == [2, 3, 7, 9],
            'original port endpoints and grades')
    require(old[A] == {94217: 1, 94218: -1, 95884: -1} and
            old[B] == {94217: -1, 94218: 1, 95884: 1, 100334: 1}, 'native pair on ingress')
    for retired in (A, B):
        word, forms, moves = merge(w, old, routes, retired)
        compare(w, old, word, forms, moves, ends, retired, [])
        word, forms, moves, ids = repair(w, old, routes, retired, (278, 127))
        compare(w, old, word, forms, moves, ends, retired, ids)
    print('PASS both funded-port deletions preserve 387 exterior outputs and change exactly two receiver rows.')
    print('PASS two direct repairs are causal and recover all 1,289 exact terminal operators.')


if __name__ == '__main__':
    main()
