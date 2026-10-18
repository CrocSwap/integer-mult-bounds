"""Truth-table oracle: permutations of literal bit assignments, no row algebra.

Does not import the constructor, matrix products, factors or shortest-path code.
"""
from collections import deque
import hashlib
import json


def check(condition, message):
    if not condition:
        raise ValueError(message)


def step(value, destination, source):
    return value ^ (((value >> source) & 1) << destination)


def evaluate(n, word):
    images = []
    for value in range(1 << n):
        for d, s in word:
            value = step(value, d, s)
        images.append(value)
    return tuple(images)


def from_rows(rows):
    # Only translates a claimed matrix to its literal truth table for comparison.
    return tuple(sum(((r & x).bit_count() % 2) << i for i, r in enumerate(rows)) for x in range(1 << len(rows)))


def joint_census(n, z, representatives):
    unit = tuple(range(1 << n))
    gates = [(d, s) for d in range(n) for s in range(n) if d != s]
    distance = {(unit, unit): 0}
    queue = deque([(unit, unit)])
    while queue:
        a, b = queue.popleft()
        for d, s in gates:
            aa = tuple(step(x, d, s) for x in a)
            bb = tuple(step(x, d, s) for x in b) if d < z else b
            if (aa, bb) not in distance:
                distance[aa, bb] = distance[a, b]+1
                queue.append((aa, bb))
    check(len(distance) == len(representatives), 'truth-table census size')
    for (raw, projected), word in representatives:
        a, b = evaluate(n, word), evaluate(n, [g for g in word if g[0] < z])
        check(a == from_rows(raw) and b == from_rows(projected), 'literal representative mismatch')
        check(distance[a, b] == len(word), 'independent shortest distance mismatch')
    payload = json.dumps([[list(a), list(b), d] for (a, b), d in sorted(distance.items())], separators=(',', ':')).encode()
    return dict(states=len(distance), diameter=max(distance.values()),
                complete_assignments=len(distance)*(1 << n),
                permutation_distance_sha256=hashlib.sha256(payload).hexdigest())


def source_columns(n, stream):
    """Execute each dirty input separately as an n+1-bit state; one clean temp."""
    columns = []
    for original in range(n):
        value = 1 << original
        for kind, dst, src in stream:
            if kind == 'add':
                value = step(value, dst, src)
            elif kind == 'copy':
                check(not (value >> dst & 1), 'copy into nonzero temporary')
                value |= ((value >> src) & 1) << dst
            elif kind == 'erase':
                check((value >> dst & 1) == (value >> src & 1), 'erase mismatch')
                value &= ~(1 << dst)
            else:
                raise ValueError('unknown operation')
        check(value < 1 << n, 'copy temporary remains live')
        columns.append(value)
    return columns


def transpose_columns(columns):
    return [sum(((c >> r) & 1) << j for j, c in enumerate(columns)) for r in range(len(columns))]
