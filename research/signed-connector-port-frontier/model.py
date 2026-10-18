"""Exact free noncommutative circuit replay and explicit completed tariffs.
Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction

TARGET = ((1, 1, 1), (1, 1, -1), (1, -1, 0))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def initial():
    return [{(i, ()): 1} for i in range(8)]


def replay(word):
    state = initial()
    for kind, op, sign, root in word:
        require(kind in ('A', 'B', 'R'), 'operation kind')
        require(type(sign) is int and sign in (-1, 1), 'signed alphabet')
        require(type(root) is int and root in (0, 1), 'root port')
        if kind == 'R':
            require(op == 1 and root == 0, 'unit one-way shear')
            src, dst, letter = 7, 6, None
        else:
            require(type(op) is int and 0 <= op < 3, 'operator index')
            src, dst = (op, 6 + root) if kind == 'B' else (6 + root, 3 + op)
            letter = kind + str(op)
        for (origin, letters), coefficient in list(state[src].items()):
            key = (origin, letters + (letter,)) if letter else (origin, letters)
            value = state[dst].get(key, 0) + sign * coefficient
            if value:
                state[dst][key] = value
            else:
                state[dst].pop(key, None)
    return state


def expected(sign=1):
    state = initial()
    for i, row in enumerate(TARGET):
        for j, coefficient in enumerate(row):
            if coefficient:
                state[3 + i][j, ('B' + str(j), 'A' + str(i))] = sign * coefficient
    return state


def inverse(word):
    return [(kind, op, -sign, root) for kind, op, sign, root in reversed(word)]


def word_mask(word):
    require(len(word) == 16, 'sixteen instructions')
    transfers = Counter(sign for kind, _, sign, _ in word if kind == 'R')
    require(transfers == {-1: 2, 1: 2}, 'four balanced unit transfers')
    mask = 0
    for index, (kind, op) in enumerate((k, j) for k in ('B', 'A') for j in range(3)):
        calls = [(sign, root) for k, j, sign, root in word if (k, j) == (kind, op)]
        require(len(calls) == 2 and sorted(s for s, _ in calls) == [-1, 1], 'signed operator pair')
        require(calls[0][1] == calls[1][1], 'single pair port')
        mask |= calls[0][1] << index
    require(replay(word) == expected(), 'dirty-state endpoint')
    require(replay(inverse(word)) == expected(-1), 'literal inverse endpoint')
    return mask


def tariff(mask, pairs, transfers):
    """pairs[F][root] is the positive+negative COMPLETE child price."""
    require(type(mask) is int and 0 <= mask < 64, 'six-bit mask')
    require(len(pairs) == 6 and all(len(p) == 2 for p in pairs), 'six two-port pair prices')
    require(len(transfers) == 2, 'two transfer prices')
    pairs = [[Fraction(p) for p in pair] for pair in pairs]
    transfers = list(map(Fraction, transfers))
    require(all(p > 0 for pair in pairs for p in pair) and all(p > 0 for p in transfers), 'positive complete tariffs')
    return sum((pairs[i][(mask >> i) & 1] for i in range(6)), Fraction()) + 2 * sum(transfers)


def semantic_controls(word):
    rejected = 0
    for i in range(len(word)):
        removal = [list(e) for e in word]
        removal.pop(i)
        require(replay(removal) != expected(), 'removed instruction must fail')
        rejected += 1
        sign = [list(e) for e in word]
        sign[i][2] *= -1
        require(replay(sign) != expected(), 'sign mutation must fail')
        rejected += 1
    for kind in ('B', 'A'):
        for op in range(3):
            moved = [list(e) for e in word]
            for event in moved:
                if event[:2] == [kind, op]:
                    event[3] ^= 1
            require(replay(moved) != expected(), 'pair port mutation must fail')
            rejected += 1
    return rejected


def one_root_histogram():
    """Fresh integer prefix implementation of the credited PR944 obstruction."""
    from itertools import permutations
    histogram = [0] * 8
    for events in permutations(range(6)):
        q = [0, 0, 0]
        vertices = [tuple(q)]
        for event in events:
            q[event // 2] += 1 if event % 2 == 0 else -1
            vertices.append(tuple(q))
        differences = {tuple(b[j] - a[j] for j in range(3))
                       for a in vertices for b in vertices}
        mask = sum(1 << i for i, row in enumerate(TARGET) if row in differences)
        histogram[mask] += 1
    require(histogram == [72, 84, 84, 48, 264, 84, 84, 0], 'one-root exact obstruction histogram')
    return histogram
