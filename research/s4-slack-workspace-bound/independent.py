#!/usr/bin/env python3
"""Independent literal regular-action audit; imports no primary verifier.
JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GROUP = list(itertools.permutations(range(4)))
SIMPLE = [(1, 0, 2, 3), (0, 2, 1, 3), (0, 1, 3, 2)]
REGULAR = [[GROUP.index(tuple(s[p[i]] for i in range(4))) for p in GROUP] for s in SIMPLE]
PAIRS = [(i, j) for i in range(4) for j in range(4) if i != j]
PAIR_MAPS = [[PAIRS.index((s[i], s[j])) for i, j in PAIRS] for s in SIMPLE]


def require(test, message):
    if not test:
        raise ValueError(message)


def permute(value, mapping):
    answer = 0
    for j, destination in enumerate(mapping):
        if value & (1 << j):
            answer ^= 1 << destination
    return answer


def paid(state, item, maps):
    label, u, v = item
    require(label in (0, 1, 2) and 0 < u < 1 << len(state) and 0 < v < 1 << len(state), 'paid domain')
    require((u & v).bit_count() % 2 == 1, 'paid idempotence')
    source = 0
    for j, value in enumerate(state):
        if v & (1 << j):
            source ^= value
    change = source ^ permute(source, maps[label])
    return [value ^ change if u & (1 << j) else value for j, value in enumerate(state)]


def apply(word, state, maps=REGULAR):
    for item in reversed(word):
        state = paid(state, item, maps)
    return state


def embed(columns, state, r):
    output = [0] * r
    for j, value in enumerate(state):
        for i in range(r):
            if columns[j] & (1 << i):
                output[i] ^= value
    return output


def column_rank(columns):
    # Lowest-pivot column elimination, independent of the primary high-pivot rank.
    pivots = {}
    for column in columns:
        while column:
            bit = column & -column
            if bit not in pivots:
                pivots[bit] = column
                break
            column ^= pivots[bit]
    return len(pivots)


def crossing_rank(word, r):
    positive = [j for j, (a, b) in enumerate(PAIRS) if a < b]
    negative = [j for j, (a, b) in enumerate(PAIRS) if a > b]
    columns = []
    for register in range(r):
        for address in positive:
            state = [0] * r
            state[register] = 1 << address
            answer = apply(word, state, PAIR_MAPS)
            column = 0
            for i, value in enumerate(answer):
                for j, bit in enumerate(negative):
                    if value & (1 << bit):
                        column ^= 1 << (6 * i + j)
            columns.append(column)
    return column_rank(columns)


def digest_endpoint(word, r):
    rows = [[0] * r for _ in range(r)]
    for j in range(r):
        state = [int(i == j) for i in range(r)]  # identity group basis element
        result = apply(word, state)
        for i, value in enumerate(result):
            rows[i][j] = value
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def audit():
    cases = json.loads((HERE / 'CASES.json').read_text())
    receipt = json.loads((HERE / 'RESULT.json').read_text())
    require(len(cases) == len(receipt['fixtures']), 'fixture inventory')
    full_columns = factor_columns = 0
    for case, row in zip(cases, receipt['fixtures']):
        r, w, word = case['roles'], case['active'], case['word']
        kept, columns, reduced = row['retained_roles'], row['basis_columns'], row['reduced_word']
        require(row['name'] == case['name'] and row['roles'] == r and row['active'] == w, 'fixture identity')
        require(len(columns) == r and all(0 < x < 1 << r for x in columns)
                and column_rank(columns) == r, 'full scalar basis')
        require(columns[:w] == [1 << i for i in range(w)]
                and all(x >> w << w == x for x in columns[w:]), 'basis fixes active and preserves spectator space')
        require(w <= kept <= r and len(word) == len(reduced) == row['calls'], 'paid length and role domain')
        rank_value = crossing_rank(word, r)
        require(rank_value == row['crossing_rank'] and row['slack'] == len(word) - rank_value,
                'independent crossing rank')
        require(kept <= w + row['slack'], 'workspace budget')
        require(digest_endpoint(word, r) == row['original_endpoint_sha256'], 'original formal endpoint hash')
        require(digest_endpoint(reduced, kept) == row['reduced_endpoint_sha256'], 'reduced formal endpoint hash')
        for original, restricted in zip(word, reduced):
            require(original[0] == restricted[0], 'paid label order')
            # Every regular input basis column checks G B = B (G' + I).
            for j in range(r):
                for g in range(24):
                    input_state = [0] * r
                    input_state[j] = 1 << g
                    old_input = embed(columns, input_state, r)
                    old_result = paid(old_input, original, REGULAR)
                    new_result = paid(input_state[:kept], restricted, REGULAR) + input_state[kept:]
                    require(old_result == embed(columns, new_result, r), 'full factor intertwiner')
                    factor_columns += 1
        # Whole-word equality on every arbitrary dirty input column, including discarded roles.
        for j in range(r):
            for g in range(24):
                state = [0] * r
                state[j] = 1 << g
                old_input = embed(columns, state, r)
                old_result = apply(word, old_input)
                new_result = apply(reduced, state[:kept]) + state[kept:]
                require(old_result == embed(columns, new_result, r), 'full endpoint intertwiner')
                if j >= w:
                    require(old_result == old_input, 'original dirty endpoint not restored')
                full_columns += 1
    return {'fixtures': len(cases), 'whole_word_regular_columns': full_columns,
            'factor_regular_columns': factor_columns}


if __name__ == '__main__':
    answer = audit()
    print('PASS_S4_SLACK_INDEPENDENT ' + json.dumps(answer, sort_keys=True))
