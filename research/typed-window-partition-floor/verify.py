#!/usr/bin/env python3
"""Exact optimal subdivision and certified floor for PR2626 fixed-reader windows."""
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COST = (0, 20, 16, 20)
EMPTY = (-1, -1, -1)
PERIOD = (0, 1, 2, 2, 0, 1, 1, 2, 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def typed(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def authenticated_source():
    for item in json.loads((HERE / 'SNAPSHOTS.json').read_text())['files']:
        raw = (HERE / item['snapshot']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item['sha256'], 'snapshot SHA256')
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blob == item['git_blob'], 'snapshot Git blob')
    for item in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if item['usage'] == 'input':
            raw = (ROOT / item['path']).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == item['sha256'], 'input SHA256')
            require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == item['git_blob'], 'input Git blob')
    spec = importlib.util.spec_from_file_location('pinned2626', HERE / 'vendor/pr2626/verify.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = ROOT
    return module


def checked(word, required=()):
    word = tuple(word)
    require(all(type(x) is int and 0 <= x < 3 for x in word), 'invalid octet')
    required = frozenset(required)
    require(all(type(x) is int and 0 < x < len(word) for x in required), 'invalid mandatory cut')
    return word, required


def transition(state, letter, cut=False):
    if cut:
        state = EMPTY
    advanced = [((x + 1) % 4 if x >= 0 else -1) for x in state]
    price = 16 if advanced[letter] < 0 else 2 * COST[-advanced[letter] % 4]
    advanced[letter] = 0
    return tuple(advanced), price


def graph():
    states = [EMPTY]
    seen = {EMPTY}
    for state in states:
        for letter in range(3):
            target, _ = transition(state, letter)
            if target not in seen:
                seen.add(target)
                states.append(target)
    edges = [(s, letter, cut, *transition(s, letter, cut))
             for s in states for letter in range(3) for cut in (False, True)]
    require(all(edge[3] in seen for edge in edges), 'graph closure')
    return states, edges


def optimal(word, required=(), witness=False):
    """O(62*n) transitions, O(62) price cells; optional O(62*n) backpointers."""
    word, required = checked(word, required)
    costs, history = {EMPTY: 0}, []
    for i, letter in enumerate(word):
        following, parents = {}, {}
        for state, value in costs.items():
            for cut in ((True,) if i in required else (False, True)):
                target, price = transition(state, letter, cut)
                candidate = value + price
                if target not in following or candidate < following[target]:
                    following[target] = candidate
                    if witness:
                        parents[target] = (state, cut)
        costs = following
        if witness:
            history.append(parents)
    last = min(costs, key=costs.get)
    price = 136 * len(word) + costs[last]
    if not witness:
        return price
    starts = []
    for i in reversed(range(len(word))):
        previous, cut = history[i][last]
        if cut and i:
            starts.append(i)
        last = previous
    return price, tuple(sorted(starts))


def window_price(word):
    """Independent position-list formula, with no automaton state."""
    if not word:
        return 0
    gap = 0
    for letter in set(word):
        positions = [i for i, value in enumerate(word) if value == letter]
        gap += sum(COST[(a - b) % 4] for a, b in itertools.pairwise(positions))
    return 136 * len(word) + 16 * len(set(word)) + 2 * gap


def segments(word, cuts):
    boundaries = (0,) + tuple(cuts) + (len(word),)
    return [word[a:b] for a, b in itertools.pairwise(boundaries) if b > a]


def interval_optimal(word, required=()):
    # A separate interval recurrence, deliberately using direct whole-window costs.
    word, required = checked(word, required)
    best = [0]
    for end in range(1, len(word) + 1):
        best.append(min(best[start] + window_price(word[start:end])
                        for start in range(end)
                        if not any(start < boundary < end for boundary in required)))
    return best[-1]


def certificate():
    """Produce an integer potential; verification below checks every inequality."""
    states, edges = graph()
    infinity = 10**9
    values = {s: (0 if s == EMPTY else infinity) for s in states}
    for _ in states:
        changed = False
        for source, _, _, target, price in edges:
            candidate = values[source] + 3 * price - 40
            if candidate < values[target]:
                values[target] = candidate
                changed = True
        if not changed:
            break
    return [{'state': list(s), 'potential': values[s]} for s in states]


def check_certificate(rows):
    states, edges = graph()
    require(type(rows) is list and len(rows) == len(states), 'potential coverage')
    values = {}
    for row in rows:
        require(type(row) is dict and set(row) == {'state', 'potential'}, 'potential schema')
        require(type(row['state']) is list and len(row['state']) == 3 and all(type(x) is int for x in row['state']), 'state schema')
        state = tuple(row['state'])
        require(state not in values and state in states, 'potential state')
        require(type(row['potential']) is int and row['potential'] >= 0, 'potential nonnegative integer')
        values[state] = row['potential']
    require(values[EMPTY] == 0, 'initial potential')
    for source, _, _, target, price in edges:
        require(values[target] <= values[source] + 3 * price - 40, 'potential edge inequality')
    return len(states), len(edges)


def check_map(word, blocks):
    """Independent row-matrix replay of all56 basis columns, including dirty input."""
    matrix = [[int(i == j) for j in range(56)] for i in range(56)]
    for kind, target, source, sign in word:
        require(type(target) is int and 0 <= target < 56, 'target')
        if kind == 'ADD':
            require(type(source) is int and 0 <= source < 56 and source != target and type(sign) is int and sign in (-1, 1), 'ADD')
            matrix[target] = [a + sign * b for a, b in zip(matrix[target], matrix[source])]
        else:
            require(kind == 'NEG' and source is None and type(sign) is int and sign == 0, 'NEG')
            matrix[target] = [-a for a in matrix[target]]
    expected = [[int(i == j) for j in range(56)] for i in range(56)]
    for block in blocks:
        for row in range(8):
            expected[row][8 + 8 * block + row] += 1
    require(matrix == expected, 'full dirty endpoint')


def build_result(write=False):
    source = authenticated_source()
    previous = source.build_result()
    require(typed(previous) == typed(json.loads((HERE / 'vendor/pr2626/RESULT.json').read_text())), 'predecessor replay')
    rows = certificate() if write else json.loads((HERE / 'POTENTIAL.json').read_text())
    state_count, edge_count = check_certificate(rows)
    word_count = 0
    constrained_count = 0
    for length in range(1, 8):
        for word in itertools.product(range(3), repeat=length):
            price, cuts = optimal(word, witness=True)
            require(price == interval_optimal(word), 'interval recurrence')
            require(price == sum(window_price(x) for x in segments(word, cuts)), 'witness price')
            require(3 * price >= 448 * length, 'certified floor')
            word_count += 1
            if length <= 5:
                all_parts = [(tuple(i + 1 for i in range(length - 1) if mask & (1 << i)), None)
                             for mask in range(1 << (length - 1))]
                all_parts = [(c, sum(window_price(x) for x in segments(word, c))) for c, _ in all_parts]
                for required, _ in all_parts:
                    expected = min(p for c, p in all_parts if set(required) <= set(c))
                    actual, witness = optimal(word, required, True)
                    require(actual == expected == interval_optimal(word, required), 'mandatory-cut exhaustive optimum')
                    require(set(required) <= set(witness), 'mandatory boundary preserved')
                    constrained_count += 1
    periods = []
    for k in (1, 2, 3, 7, 20, 100):
        word = PERIOD * k
        require(window_price(word) == 1344 * k + 8, 'period price')
        value = optimal(word)
        require(3 * value >= 448 * len(word) and value <= window_price(word), 'period squeeze')
        periods.append({'repetitions': k, 'one_window': window_price(word), 'optimal': value})
    short = (0, 1, 2, 2, 0, 1)
    require(window_price(short) == 904 and optimal(short) == 904, 'six-child witness')
    require(all(304 - window_price(short[i:i + 2]) <= 0 for i in range(5)), 'no strict first greedy merge')
    fixtures = [(short, ()), (PERIOD * 2, ()), ((0,) * 7, ()),
                ((0, 1, 2, 0, 1) * 2, (5,)), (PERIOD * 3, (9, 18)),
                ((2, 1, 0, 2, 2, 1, 0, 0), (2, 5))]
    invoices = []
    for word, required in fixtures:
        price, cuts = optimal(word, required, True)
        parts = segments(word, cuts)
        records = []
        prefix = ()
        for part in parts:
            emitted = source.schedule(part)
            require(len(emitted) == window_price(part), 'compiler price')
            check_map(emitted, part)
            records += emitted
            prefix += tuple(part)
            check_map(records, prefix)
        require(len(records) == price, 'compiled optimum')
        check_map(records + source.inverse(records), ())
        invoices.append({'word': list(word), 'mandatory_cuts': list(required), 'optimal_cuts': list(cuts), 'invoice': source.invoice(records, len(parts))})
    controls = 0
    for bad in ((True,), (3,), (-1,), (0.0,)):
        try:
            optimal(bad)
        except ValueError:
            controls += 1
        else:
            raise ValueError('accepted invalid word')
    for required in ((0,), (2,), (True,)):
        try:
            optimal((0, 1), required)
        except ValueError:
            controls += 1
        else:
            raise ValueError('accepted invalid cut')
    altered = json.loads(json.dumps(rows)); altered[1]['potential'] += 1000
    try:
        check_certificate(altered)
    except ValueError:
        controls += 1
    else:
        raise ValueError('accepted invalid potential')
    bad_word = source.schedule(short)
    bad_word[0] = (*bad_word[0][:3], -1)
    try:
        check_map(bad_word, short)
    except ValueError:
        controls += 1
    else:
        raise ValueError('accepted wrong COPY sign')
    result = dict(states=state_count, edges=edge_count, words=word_count,
                  constrained_instances=constrained_count, negative_controls=controls,
                  floor_numerator=448, floor_denominator=3, period=list(PERIOD),
                  period_checks=periods, compiled_fixtures=invoices,
                  predecessor_words=previous['words_checked'], predecessor_pairs=previous['ordered_pairs_checked'])
    return rows, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='create absent receipts only')
    args = parser.parse_args()
    targets = [HERE / 'POTENTIAL.json', HERE / 'RESULT.json']
    if args.write:
        require(not any(p.exists() for p in targets), 'refusing to overwrite receipt')
    rows, result = build_result(args.write)
    if args.write:
        for path, data in zip(targets, (rows, result)):
            path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')
    else:
        require(typed(result) == typed(json.loads(targets[1].read_text())), 'stored result mismatch')
    print('PASS_TYPED_WINDOW_PARTITION ' + typed({k: result[k] for k in ('states', 'edges', 'words', 'constrained_instances', 'negative_controls')}))


if __name__ == '__main__':
    main()
