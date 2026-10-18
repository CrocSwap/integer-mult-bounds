#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# David Arias, with substantial OpenAI Codex assistance.
"""Independent literal-word replay for the credited PR2733/PR2751 composition.

Uses only Python's standard library. No producer, predecessor checker, cached
profile, or native audit is imported. Frames use binary Gaussian elimination;
linear endpoints use sparse rational expressions in free noncommuting warp
symbols. This verifies a finite construction, not the conditional analytic or
fixed-tape assumptions of the complete multiplication theorem.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
from fractions import Fraction
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD_FRAME = [259, 132, 66, 36, 16, 9]
NEW_FRAME = [259, 148, 66, 36, 9]
GATE = 1151


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def normal(vectors):
    """Canonical reduced binary row basis, with descending pivots."""
    rows = {}
    for vector in vectors:
        require(isinstance(vector, int) and 0 <= vector < 512, 'binary coordinate')
        for pivot in sorted(rows, reverse=True):
            if vector >> pivot & 1:
                vector ^= rows[pivot]
        if vector:
            pivot = vector.bit_length() - 1
            for old in list(rows):
                if rows[old] >> pivot & 1:
                    rows[old] ^= vector
            rows[pivot] = vector
    return tuple(rows[p] for p in sorted(rows, reverse=True))


def contained(small, large):
    return normal((*large, *small)) == large


FULL = normal(1 << i for i in range(9))


def image(columns, vector):
    value = 0
    for i, column in enumerate(columns):
        if vector >> i & 1:
            value ^= column
    return value


def touched(gate):
    return gate[1:3] if gate[0] == 'add' else gate[1:2]


def endpoints(word):
    live = set(range(704)) - set(word['removed'])
    start = {r: normal([word['ports'][r]] if r < 112 else
                       word['start_extra'].get(str(r), [])) for r in live}
    finish = {r: FULL for r in live}
    for i, port in enumerate(word['ports']):
        require(port != 0, 'nonzero target port')
        pivot = (port & -port).bit_length() - 1
        finish[112 + i] = normal((1 << j) ^ (((port >> j) & 1) << pivot)
                                 for j in range(9) if j != pivot)
    for r, frame in word['helper_final'].items():
        finish[int(r)] = normal(frame)
    return start, finish


def frame_replay(word):
    start, finish = endpoints(word)
    current = dict(start)
    paid = Counter()
    history = defaultdict(list)

    def climb(r, frame, location):
        frame = normal(frame)
        require(contained(current[r], frame), f'frame inclusion at {location}/{r}')
        degree = len(frame) - len(current[r])
        if degree:
            paid[degree] += 1
        history[r].append((location, len(current[r]), len(frame)))
        current[r] = frame

    def warp(r, op, old, new, location):
        columns = word['warps'][abs(op) - 1][2]
        require(len(normal(columns)) == 9, f'invertible warp {op}')
        old, new = normal(old), normal(new)
        require(current[r] == old, f'warp entrance {location}/{r}')
        before, after = (old, new) if op > 0 else (new, old)
        require(normal(image(columns, v) for v in before) == after,
                f'warp transported frame {location}/{r}')
        current[r] = new
        history[r].append((location, len(old), len(new)))

    def gate(g, location):
        if g[0] == 'warp':
            warp(*g[1:], location)
        else:
            require(g[0] in ('add', 'scale'), 'known scalar operation')
            for r in touched(g):
                climb(r, g[-1], location)

    for i, g in enumerate(word['A']):
        gate(g, f'A{i}')
    levels = {int(t): normal(vs) for t, vs in word['target_levels'].items()}
    require(all(current[112 + t] == levels.get(t, ()) for t in range(112)),
            'all cut target entrances')
    # The native central child pays the nested descent once; its other side
    # retains the center's start chart for the B-side ascent representation.
    for r, frame in zip(word['centers'], word['center_frames']):
        previous = normal(frame)
        require(current[r] == previous, 'central source entrance')
        readers = {levels.get(g[1] - 112, ()) for g in word['cut'] if g[2] == r}
        for target in sorted(readers, key=lambda x: (-len(x), x)):
            require(contained(target, previous), 'nested central descent')
            if len(previous) != len(target):
                paid[len(previous) - len(target)] += 1
            previous = target
    warps = defaultdict(list)
    for op, entry in enumerate(word['warps'], 1):
        warps[entry[0]].append((op, entry))
    for i in range(len(word['B']) + 1):
        for op, (_, r, _, old, new) in warps[i]:
            warp(r, op, old, new, f'warp{op}')
        if i < len(word['B']):
            gate(word['B'][i], f'B{i}')
    for i, g in enumerate(word['restore']):
        gate(g, f'restore{i}')
    for r in sorted(current):
        climb(r, finish[r], 'endpoint')
    inventory = Counter(len(finish[r]) - len(start[r]) for r in current if r >= 224)
    require(dict(paid) == {int(k): v for k, v in word['report']['local_profile'].items()},
            'complete paid profile, including endpoint climbs')
    require(dict(inventory) == {int(k): v for k, v in word['report']['width_inventory'].items()},
            'helper endpoint width inventory')
    return paid, history


def reduced(left, right):
    """Multiply free-group words, stored with the newest operation first."""
    result = list(left)
    for symbol in right:
        if result and result[-1] == -symbol:
            result.pop()
        else:
            result.append(symbol)
    return tuple(result)


def scalar_replay(word, dual):
    live = set(range(704)) - set(word['removed'])
    cold = set(map(int, word['helper_final']))
    rows = {r: {(r, ()): Fraction(1)} for r in live}
    rows.update({704 + r: {} for r in cold})

    def add(target, source, coefficient, operator=()):
        for (origin, old), value in list(rows[source].items()):
            term = (origin, reduced(operator, old))
            total = rows[target].get(term, Fraction(0)) + coefficient * value
            if total:
                rows[target][term] = total
            else:
                rows[target].pop(term, None)

    def dual_symbol(symbol):
        return (abs(symbol) + 1000) * (1 if symbol > 0 else -1)

    def apply(g):
        kind = g[0]
        if kind == 'add':
            target, source, numerator, denominator = g[1:5]
            coefficient = Fraction(numerator, denominator)
            require(target != source, 'distinct ADD registers')
            if dual:
                target, source, coefficient = source, target, -coefficient
            add(target, source, coefficient)
        elif kind == 'scale':
            r, numerator, denominator = g[1:4]
            coefficient = Fraction(numerator, denominator)
            require(coefficient != 0, 'invertible scalar')
            if dual:
                coefficient = 1 / coefficient
            rows[r] = {term: coefficient * value for term, value in rows[r].items()}
        elif kind == 'warp':
            r, symbol = g[1:3]
            if not dual and 47 <= symbol <= 58:
                require(rows[r] == {(r, ()): Fraction(1)}, 'recovered source lender')
            if dual:
                symbol = dual_symbol(symbol)
            rows[r] = {(origin, reduced((symbol,), old)): value
                       for (origin, old), value in rows[r].items()}
        else:
            raise ValueError(f'unknown scalar operation {kind}')

    for correction in word['initial_corrections']:
        target, source = correction['target'], correction['source']
        coefficient = Fraction(correction['coefficient'])
        operator = tuple(correction['operator_word'])
        if dual:
            target, source, coefficient = source, target, -coefficient
            operator = tuple(-dual_symbol(x) for x in reversed(operator))
        add(target, source, coefficient, operator)
    for section in ('precondition', 'compensation', 'A', 'cut'):
        for g in word[section]:
            apply(g)
    warps = defaultdict(list)
    for op, entry in enumerate(word['warps'], 1):
        warps[entry[0]].append(['warp', entry[1], op])
    for i in range(len(word['B']) + 1):
        for g in warps[i]:
            apply(g)
        if i < len(word['B']):
            apply(word['B'][i])
    for g in word['restore']:
        apply(g)
    if not dual:
        for r in cold:
            require(rows[r] == {(r, ()): Fraction(1)}, 'dirty helper restored before cleanup')
        for t in range(112):
            require(rows[112 + t] == {(112 + t, ()): Fraction(1), (t, ()): Fraction(1)},
                    'forward target before cleanup')
    for g in word['cleanup']:
        apply(g)
    for r in live:
        expected = {(r, ()): Fraction(1)}
        if dual and r < 112:
            expected[(112 + r, ())] = Fraction(-1)
        if not dual and 112 <= r < 224:
            expected[(r - 112, ())] = Fraction(1)
        require(rows[r] == expected, f'complete {"dual" if dual else "forward"} endpoint {r}')
    require(all(not rows[704 + r] for r in cold), 'all cold outputs zero')


def check_change(source, candidate):
    require(source['B'][GATE] == ['add', 393, 515, 1, 1, OLD_FRAME], 'source refit gate')
    require(candidate['B'][GATE] == ['add', 393, 515, 1, 1, NEW_FRAME], 'candidate refit gate')
    expected = copy.deepcopy(source)
    expected['B'][GATE][-1] = NEW_FRAME
    expected['report']['local_profile'] = candidate['report']['local_profile']
    require(expected == candidate, 'only the credited frame and paid profile change')


def reject(callback, label):
    try:
        callback()
    except ValueError:
        return label
    raise ValueError(f'negative control accepted: {label}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=HERE / 'vendor/pr2751')
    parser.add_argument('--candidate', type=Path, default=HERE)
    args = parser.parse_args()
    source = args.source.resolve()
    candidate = args.candidate.resolve()
    candidate_inputs = candidate / 'inputs' if (candidate / 'inputs').is_dir() else candidate
    result = {'status': 'PASS_INDEPENDENT_CREDITED_FUSION', 'providers': {}}
    local_delta = Counter({1: -2, 2: 1})
    for tag in ('base', 'extra'):
        old = read(source / f'inputs/WORD-{tag}.json.gz')
        new = read(candidate_inputs / f'WORD-{tag}.json.gz')
        check_change(old, new)
        before, old_history = frame_replay(old)
        after, new_history = frame_replay(new)
        delta = Counter(after)
        delta.subtract(before)
        require({r: n for r, n in delta.items() if n} == dict(local_delta), 'exact local fusion charge')
        paths = {}
        for r, prior in ((393, 4), (515, 5)):
            a = old_history[r]
            b = new_history[r]
            index = next(i for i, entry in enumerate(a) if entry[0] == f'B{GATE}')
            require(a[index][1:] == (prior, 6) and a[index + 1][1:] == (6, 7), 'old local path')
            require(b[index][1:] == (prior, 5) and b[index + 1][1:] == (5, 7), 'new local path')
            paths[str(r)] = {'old': [prior, 6, 7], 'new': [prior, 5, 7]}
        scalar_replay(new, False)
        scalar_replay(new, True)
        bad_frame = copy.deepcopy(new)
        bad_frame['B'][GATE][-1] = [1]
        omitted = copy.deepcopy(new)
        omitted['report']['local_profile']['2'] -= 1
        controls = [reject(lambda: frame_replay(bad_frame), 'invalid frame'),
                    reject(lambda: check_change(old, old), 'unchanged identity candidate'),
                    reject(lambda: frame_replay(omitted), 'omitted child charge')]
        result['providers'][tag] = {'profile': dict(sorted(after.items())), 'paths': paths,
                                    'forward': 'PASS', 'dual': 'PASS', 'controls': controls}
    order = read(source / 'inputs/ORDER.json')
    require(len(order) == len({tuple(x) for x in order}) == 666, '666 distinct provider invocations')
    global_old = Counter({int(k): v for k, v in read(source / 'PROFILE.json').items()})
    expected = Counter(global_old)
    expected.update({r: 666 * n for r, n in local_delta.items()})
    claimed = {int(k): v for k, v in read(candidate / 'PROFILE.json').items()}
    require(dict(expected) == claimed, 'complete global profile includes fusion charge')
    require(sum(r * n for r, n in expected.items()) == sum(r * n for r, n in global_old.items()),
            'unchanged global rank mass')
    result['global_delta'] = {r: 666 * n for r, n in local_delta.items()}
    result['profile'] = claimed
    print(json.dumps(result, sort_keys=True, separators=(',', ':')))


if __name__ == '__main__':
    main()
