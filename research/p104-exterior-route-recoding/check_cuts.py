"""Two-atom separator, all minimum-grade routes, and rank-cut charges."""
from collections import Counter
from fractions import Fraction
from functools import cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_mergers import A, B, compare, merge, repair
from word import read_word, require


def evaluate(word, forms, point):
    values = {~j: point.get(j, 0) for j in range(len(word['initial']))}
    for k in word['schedule']:
        values[k] = sum(q * values[j] for j, q in forms[k].items())
    return values


def span(frame):
    space = {0}
    for v in frame:
        space |= {x ^ v for x in space}
    require(len(space) == 1 << len(frame), 'independent binary frame')
    return frozenset(space)


# Rigorous price intervals adapted from the rational checks in #7808 and #7814.
@cache
def price(d):
    if d == 0:
        return Fraction(0), Fraction(0)

    def log_bounds(x):
        z = (x - 1) / (x + 1)
        u, total = z, Fraction(0)
        for j in range(45):
            total += 2 * u / (2 * j + 1)
            u *= z * z
        return total, total + 2 * u / (91 * (1 - z*z))

    def exp_neg_bounds(x):
        require(0 <= x < Fraction(1, 50), 'alternating exponential terms decrease')
        u = total = Fraction(1)
        for j in range(1, 14):
            u *= -x / j
            total += u
        return total, total - u * x / 14

    k = d.bit_length() - 1
    base, rest = log_bounds(Fraction(2)), log_bounds(Fraction(d, 1 << k))
    low, high = (Fraction('0.00387981257853') * (k*base[i] + rest[i]) for i in (0, 1))
    return d * exp_neg_bounds(high)[0], d * exp_neg_bounds(low)[1]


def check_price():
    seven = price(7)
    for a in range(10):
        for b in range(10):
            grade = abs(b - a)
            crossed = sum(a <= t < b for t in range(2, 9))
            if not grade or (a, b) == (2, 9):
                require((grade, crossed) in ((0, 0), (7, 7)), 'equality grades')
            else:
                require(7 * price(grade)[0] > crossed * seven[1], 'strict cut tariff inequality')
    for d, text in [(1, '285.472830172972358520270568'), (5, '94.966797106425725799489376')]:
        low, high = price(d)
        expected = Fraction(text)
        require(expected < 48*(seven[0] - high) <= 48*(seven[1] - low) <
                expected + Fraction(1, 10**24), '48-call signed surcharge')
    print('PASS all 100 oriented rank pairs satisfy the seven-cut tariff bound.')
    print('PASS 48-call surcharges 285.472830172972358520270568… and 94.966797106425725799489376….')


def main():
    w, forms, moves, ends = read_word()
    point = {674: 1, 722: -1}
    original = evaluate(w, forms, point)
    require(original[A] == 2 and original[B] == -2 and original[155442] == 1 and
            ends[155442] == 127, 'incumbent required output separates the witness from zero')
    require([w['initial'][j] for j in point] == [11, 58] and
            [len(w['frames'][j]) for j in (11, 58, 278, 127)] == [1, 1, 2, 9], 'source ranks')
    for retired in (A, B):
        word, merged, routes = merge(w, forms, moves, retired)
        values = evaluate(word, merged, point)
        require({k: values[k] for k in routes if values[k]} == {94217: 1, 94218: -1},
                'complete list of nonzero surviving paid arrivals')
        require(routes[94217] == (11, 278) and routes[94218] == (58, 278), 'live stock owners')
        require(all(values[k] == 0 for k in ends if ends[k] == 127), 'receiver sees the zero vector')
    print('PASS each merger kills every fixed paid observation at every chart of rank three or higher.')

    spaces = [span(frame) for frame in w['frames']]
    interval = [i for i, s in enumerate(spaces) if spaces[278] <= s <= spaces[127]]
    require(len(spaces) == 1103 and len({spaces[i] for i in interval}) == len(interval) and
            Counter(len(w['frames'][i]) for i in interval) == {2:1, 3:3, 4:4, 5:3, 6:6, 7:14, 8:24, 9:1},
            'complete interval of existing charts with unique spans')
    require(all(spaces[c] != spaces[i] for c in (11, 58) for i in range(len(spaces)) if i != c),
            'live public sources have no hidden equal-span peers')

    @cache
    def paths(u):
        if u == 127:
            return [(127,)]
        return [(u,) + path for v in interval if spaces[u] < spaces[v] for path in paths(v)]

    chains = paths(278)
    require(Counter(len(p) - 1 for p in chains) == {1:1, 2:54, 3:229, 4:325, 5:226, 6:86, 7:12},
            '933 strictly ascending chains by number of legs')
    require(all(sum(len(w['frames'][b]) - len(w['frames'][a]) for a, b in zip(p, p[1:])) == 7
                for p in chains), 'minimum grade on every recovered chain')
    longest = max(chains, key=len)
    for retired in (A, B):
        word, new, routes, ids = repair(w, forms, moves, retired, longest)
        compare(w, forms, word, new, routes, ends, retired, ids)
    print('PASS all 933 minimum-grade paths on 56 charts; seven-hop causal reconstruction in both orientations.')
    check_price()


if __name__ == '__main__':
    main()
