#!/usr/bin/env python3
"""Bounded nomination only; verify.py checks the resulting circuit separately.

Prepared for alluri-ritual with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
from fractions import Fraction as Q
import json
from pathlib import Path
import random
from collections import Counter

N = 8


def identity():
    return [[Q(i == j) for j in range(N)] for i in range(N)]


def apply(a, e, positive=False):
    t = e[1]
    if e[0] == 'add':
        q = Q(e[3], e[4])
        q = abs(q) if positive else q
        a[t] = [u + q*v for u, v in zip(a[t], a[e[2]])]
    else:
        q = Q(e[2], e[3])
        q = abs(q) if positive else q
        a[t] = [q*u for u in a[t]]


def matrix(events, positive=False):
    a = identity()
    for e in events:
        apply(a, e, positive)
    return a


def inverse(events):
    result = []
    for e in reversed(events):
        e = copy.deepcopy(e)
        if e[0] == 'add':
            e[3] *= -1
        else:
            e[2], e[3] = e[3], e[2]
        result.append(e)
    return result


def power2(x):
    return x > 0 and x & (x-1) == 0


def allowed(events):
    for e in events:
        q = Q(e[3], e[4]) if e[0] == 'add' else Q(e[2], e[3])
        if not power2(q.denominator):
            return False
        if e[0] == 'scale' and not power2(abs(q.numerator)):
            return False
    return True


def eliminate(target, order, rng, frame):
    a, ops = copy.deepcopy(target), []

    def emit(e):
        apply(a, e)
        ops.append(e)

    left = set(range(N))
    for c in order:
        choices = [r for r in sorted(left) if a[r][c]
                   and power2(abs(a[r][c].numerator))
                   and power2(a[r][c].denominator)]
        if not choices:
            return None
        r = c if c in choices else rng.choice(choices)
        if r != c:
            emit(['add', c, r, 1, 1, frame])
            emit(['add', r, c, -1, 1, frame])
            emit(['add', c, r, 1, 1, frame])
            emit(['scale', r, -1, 1, frame])
        q = 1 / a[c][c]
        if q != 1:
            emit(['scale', c, q.numerator, q.denominator, frame])
        for r in range(N):
            if r != c and a[r][c]:
                q = -a[r][c]
                emit(['add', r, c, q.numerator, q.denominator, frame])
        left.remove(c)
    if a != identity():
        raise ValueError('Elimination did not reach identity')
    return inverse(ops)


def nominate(original, seed=33, trials=1024):
    rng = random.Random(seed)
    target, best, counts = matrix(original), original, Counter()
    original_positive = [matrix(original, True), matrix(inverse(original), True)]
    improvements = []
    for trial in range(trials):
        order = list(range(N))
        rng.shuffle(order)
        candidate = eliminate(target, order, rng, original[0][-1])
        if candidate is None:
            counts['no_binary_pivot'] += 1
            continue
        if not allowed(candidate):
            counts['non_dyadic'] += 1
            continue
        counts['admissible'] += 1
        if len(candidate) >= len(best):
            continue
        if matrix(candidate) != target:
            raise ValueError('Incorrect candidate')
        pairs = zip([matrix(candidate, True), matrix(inverse(candidate), True)],
                    original_positive)
        if all(x <= y for aa, bb in pairs for a, b in zip(aa, bb) for x, y in zip(a, b)):
            best = candidate
            counts['improvements'] += 1
            improvements.append({'trial_zero_based': trial, 'gates': len(best)})
    return best, dict(counts), improvements


def primitive_cost(events):
    total = 0
    for e in events:
        q = Q(e[3], e[4]) if e[0] == 'add' else Q(e[2], e[3])
        a, b = abs(q.numerator), q.denominator
        total += (3+a.bit_length()-1+a.bit_count()+b.bit_length()-1 if e[0] == 'add'
                  else abs(a.bit_length()-b.bit_length())+int(q < 0))
    return total


def commute(a, b):
    if a[0] == b[0] == 'add':
        return a[1] != b[2] and b[1] != a[2]
    if a[0] == b[0] == 'scale':
        return True
    scale, add = (a, b) if a[0] == 'scale' else (b, a)
    return scale[1] not in add[1:3]


def collect(events):
    """Merge equal generators through only commuting intervening gates."""
    events = copy.deepcopy(events)
    while True:
        changed = False
        for i, a in enumerate(events):
            ids = a[1:3] if a[0] == 'add' else a[1:2]
            for j in range(i+1, len(events)):
                b = events[j]
                other_ids = b[1:3] if b[0] == 'add' else b[1:2]
                if a[0] == b[0] and ids == other_ids:
                    qa = Q(a[3], a[4]) if a[0] == 'add' else Q(a[2], a[3])
                    qb = Q(b[3], b[4]) if b[0] == 'add' else Q(b[2], b[3])
                    q = qa+qb if a[0] == 'add' else qa*qb
                    if q == (0 if a[0] == 'add' else 1):
                        events.pop(j)
                        events.pop(i)
                    else:
                        start = 3 if a[0] == 'add' else 2
                        a[start:start+2] = [q.numerator, q.denominator]
                        events.pop(j)
                    changed = True
                    break
                if not commute(a, b):
                    break
            if changed:
                break
        if not changed:
            return events


def endpoint_dominates(events, original):
    pairs = zip([matrix(events, True), matrix(inverse(events), True)],
                [matrix(original, True), matrix(inverse(original), True)])
    return all(x <= y for aa, bb in pairs for a, b in zip(aa, bb) for x, y in zip(a, b))


def two_sided(target, rng, frame):
    """Reduce A by row and column shears, recording both sides exactly."""
    a, left, right = copy.deepcopy(target), [], []
    reductions = 0
    while True:
        choices = []
        for side, table in [(0, a), (1, list(map(list, zip(*a))))]:
            nnz = [sum(bool(x) for x in row) for row in table]
            for t in range(N):
                for r in range(N):
                    if t == r:
                        continue
                    qs = {-x/y for x, y in zip(table[t], table[r]) if x and y}
                    for q in sorted(qs):
                        if not power2(q.denominator):
                            continue
                        row = [x+q*y for x, y in zip(table[t], table[r])]
                        saved = nnz[t]-sum(bool(x) for x in row)
                        if saved <= 0:
                            continue
                        cost = primitive_cost([['add', t, r, q.numerator, q.denominator, frame]])
                        score = Q(saved, cost)*Q(rng.randint(8, 16), 16)
                        choices.append((score, saved, -cost, side, t, r, q, row))
        if not choices:
            break
        _, _, _, side, t, r, q, row = max(choices, key=lambda x: x[:3])
        e = ['add', t, r, q.numerator, q.denominator, frame]
        if side == 0:
            a[t] = row
            left.append(e)
        else:
            for i, x in enumerate(row):
                a[i][t] = x
            e[1], e[2] = e[2], e[1]
            right.append(e)
        reductions += 1
    best = None
    successful_orders = 0
    for _ in range(8):
        order = list(range(N))
        rng.shuffle(order)
        middle = eliminate(a, order, rng, frame)
        if middle is None:
            continue
        successful_orders += 1
        # A = L M R, hence M = L^-1 A R^-1. Lists are execution ordered.
        events = collect([inverse([e])[0] for e in right] + middle + inverse(left))
        if best is None or (primitive_cost(events), len(events)) < (primitive_cost(best), len(best)):
            best = events
    return best, reductions, successful_orders


def cross_scale(scale, other, right):
    scale, other = copy.deepcopy(scale), copy.deepcopy(other)
    if other[0] == 'scale':
        return other, scale
    q, d = Q(other[3], other[4]), Q(scale[2], scale[3])
    exponent = int(other[2] == scale[1])-int(other[1] == scale[1])
    if not right:
        exponent *= -1
    q *= d**exponent
    other[3:5] = [q.numerator, q.denominator]
    return other, scale


def transport_scales(events, original):
    history = []
    for step in range(16):
        best, choice = events, None
        for i, e in enumerate(events):
            if e[0] != 'scale':
                continue
            for direction in (-1, 1):
                current, pos = copy.deepcopy(events), i
                for _ in range(len(events)):
                    other = pos+direction
                    if not 0 <= other < len(current):
                        break
                    if direction == 1:
                        current[pos], current[other] = cross_scale(current[pos], current[other], True)
                    else:
                        b, a = cross_scale(current[pos], current[other], False)
                        current[other], current[pos] = a, b
                    pos = other
                    candidate = collect(current)
                    if (primitive_cost(candidate), len(candidate)) < (primitive_cost(best), len(best)):
                        if endpoint_dominates(candidate, original):
                            best, choice = candidate, [i, direction, pos]
        if choice is None:
            break
        if matrix(best) != matrix(original):
            raise ValueError('Scale transport changed the map')
        history.append({'step': step, 'move': choice, 'gates': len(best),
                        'primitives': primitive_cost(best)})
        events = best
    return events, history


def nominate_bilateral(original, initial, seed=33, trials=512):
    rng = random.Random(seed)
    target, best = matrix(original), initial
    improvements = []
    counts = Counter()
    for trial in range(trials):
        candidate, reductions, orders = two_sided(target, rng, original[0][-1])
        counts['two_sided_trials'] += 1
        counts['nonzero_decreasing_steps'] += reductions
        counts['middle_orders_attempted'] += 8
        counts['middle_orders_completed'] += orders
        if candidate is None:
            continue
        if (primitive_cost(candidate), len(candidate)) < (primitive_cost(best), len(best)):
            if not allowed(candidate) or matrix(candidate) != target:
                raise ValueError('Incorrect bilateral candidate')
            if endpoint_dominates(candidate, original):
                best = candidate
                improvements.append({'trial_zero_based': trial, 'gates': len(best),
                                     'real_primitives': primitive_cost(best)})
    best, scales = transport_scales(best, original)
    return best, dict(counts), improvements, scales


if __name__ == '__main__':
    here = Path(__file__).resolve().parent
    cert = json.loads((here / 'CIRCUIT.json').read_text())
    initial, counts, improvements = nominate(cert['original'])
    if (initial, counts, improvements) != (cert['previous_replacement'], cert['search']['counts'],
                                          cert['search']['improvements']):
        raise ValueError('Historical search did not reproduce')
    candidate, counts, improvements, scales = nominate_bilateral(cert['original'], initial)
    expected = cert['continuation_search']
    if (candidate, counts, improvements, scales) != (cert['replacement'], expected['counts'],
                                                    expected['improvements'], expected['scale_transport']):
        raise ValueError('Bilateral search did not reproduce')
    print('PASS_SEARCH_FACTORY trials=1024+512 gates=87->34 primitives=310->128')
