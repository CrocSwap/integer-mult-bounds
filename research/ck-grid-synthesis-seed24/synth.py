"""Finite CK single-scratch grid synthesis. Eva Ayala / ToikY + Codex; Apache-2.0."""
from collections import deque


def edges(x, denominator, bound):
    options = [('add', x + denominator), ('subtract', x - denominator),
               ('double', 2 * x), ('negate', -x), ('clear', 0),
               ('copy', denominator)]
    if x % 2 == 0:
        options.append(('halve', x // 2))
    return [(tag, y) for tag, y in options if abs(y) <= bound]


def solve(a, denominator):
    if type(a) is not int or type(denominator) is not int or a <= 0 or denominator <= 0:
        raise ValueError('positive integer parameters required')
    if denominator & (denominator - 1):
        raise ValueError('dyadic denominator required')
    bound = a * denominator
    distance, parent = {denominator: 0}, {}
    pending = deque([denominator])
    while pending:
        x = pending.popleft()
        for tag, y in edges(x, denominator, bound):
            if y not in distance:
                distance[y] = distance[x] + 1
                parent[y] = (x, tag)
                pending.append(y)
    goal = min((a, -a), key=lambda x: distance[x])
    word, x = [], goal
    while x != denominator:
        x, tag = parent[x]
        word.append(tag)
    return {'a': a, 'D': denominator, 'bound': bound,
            'states': [{'x': x, 'distance': distance[x]} for x in sorted(distance)],
            'word': word[::-1], 'terminal_sign': 1 if goal > 0 else -1,
            'cost': distance[goal] + 3}
