#!/usr/bin/env python3
"""Exact controls and constructive compression; the universal proof is PROOF.md.
JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import itertools
import json
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
PERMS = list(itertools.permutations(range(4)))
INDEX = {p: i for i, p in enumerate(PERMS)}
LABELS = [INDEX[p] for p in ((1, 0, 2, 3), (0, 2, 1, 3), (0, 1, 3, 2))]
POS = [(a, b) for a in range(4) for b in range(a + 1, 4)]
NEG = {(b, a): i for i, (a, b) in enumerate(POS)}


def need(test, message):
    if not test:
        raise ValueError(message)


def parity(x):
    return x.bit_count() & 1


def bits(x):
    while x:
        bit = x & -x
        yield bit.bit_length() - 1
        x ^= bit


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def combine(columns, coordinates):
    value = 0
    for j in bits(coordinates):
        value ^= columns[j]
    return value


def coordinates(columns, value):
    pivots = {}
    for j, column in enumerate(columns):
        coefficient = 1 << j
        while column:
            pivot = column.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (column, coefficient)
                break
            row, word = pivots[pivot]
            column ^= row
            coefficient ^= word
        need(column != 0, 'basis must be independent')
    result = 0
    while value:
        pivot = value.bit_length() - 1
        need(pivot in pivots, 'vector outside basis span')
        row, word = pivots[pivot]
        value ^= row
        result ^= word
    return result


def split(q, a, b):
    """Columns of S=U+S', with a in U and b zero on S'; U comes first."""
    need(0 <= a < 1 << q and 0 <= b < 1 << q, 'split dimensions')
    if not b:
        kept = [a] if a else []
        candidates = [1 << j for j in range(q)]
    else:
        pivot = next(bits(b))
        t = 1 << pivot
        kept = ([a] if parity(a & b) else [a, t]) if a else [t]
        candidates = [(1 << j) ^ (t if b >> j & 1 else 0)
                      for j in range(q) if j != pivot]
    columns = kept[:]
    for vector in candidates:
        if rank(columns + [vector]) > len(columns):
            columns.append(vector)
    need(len(columns) == q, 'split must give a complete basis')
    need(coordinates(columns, a) < 1 << len(kept), 'split lost image vector')
    need(all(not parity(b & x) for x in columns[len(kept):]), 'split lost kernel')
    need(len(kept) <= bool(a) + bool(b), 'split over budget')
    return columns, len(kept)


def identity(r):
    return tuple(tuple(int(i == j) for j in range(r)) for i in range(r))


@lru_cache(maxsize=8192)
def shift(mask, label):
    s = PERMS[LABELS[label]]
    answer = 0
    for g in bits(mask):
        p = PERMS[g]
        answer ^= 1 << INDEX[tuple(p[s[j]] for j in range(4))]
    return answer


def gate(matrix, item):
    label, u, v = item
    r = len(matrix)
    need(label in (0, 1, 2) and 0 < u < 1 << r and 0 < v < 1 << r
         and parity(u & v), 'illegal paid factor')
    result = []
    for row in matrix:
        value = 0
        for j in bits(u):
            value ^= row[j]
        correction = value ^ shift(value, label)
        result.append(tuple(entry ^ correction if v >> j & 1 else entry
                            for j, entry in enumerate(row)))
    return tuple(result)


def endpoint(r, word):
    result = identity(r)
    for item in word:
        result = gate(result, item)
    return result


def phi(matrix):
    r = len(matrix)
    rows = [0] * (6 * r)
    for i, row in enumerate(matrix):
        for j, mask in enumerate(row):
            for g in bits(mask):
                p = PERMS[g]
                for k, (a, b) in enumerate(POS):
                    out = (p[a], p[b])
                    if out in NEG:
                        rows[6 * i + NEG[out]] ^= 1 << (6 * j + k)
    return rank(rows)


def conjugate(matrix, columns):
    """B^-1 M B, scalar bitset columns and formal coefficient entries."""
    r = len(matrix)
    inverse_columns = [coordinates(columns, 1 << i) for i in range(r)]
    result = [[0] * r for _ in range(r)]
    for j, col in enumerate(columns):
        old = [0] * r
        for k in bits(col):
            for i in range(r):
                old[i] ^= matrix[i][k]
        for i, value in enumerate(old):
            for k in bits(inverse_columns[i]):
                result[k][j] ^= value
    return tuple(map(tuple, result))


def block_identity(matrix, active):
    r = len(matrix)
    return all(matrix[i][j] == int(i == j)
               for i in range(r) for j in range(r) if i >= active or j >= active)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def compress(case):
    r, w, word = case['roles'], case['active'], case['word']
    need(0 <= w <= r <= 12 and len(word) <= 24, 'fixture capacity')
    target = endpoint(r, word)
    need(block_identity(target, w), 'full restored spectator endpoint required')
    columns, active, current = [1 << j for j in range(r)], w, target
    length, charges = phi(target), []
    for item in reversed(word):
        label, u, v = item
        old_phi = phi(current)
        next_current = gate(current, item)
        new_phi = phi(next_current)
        uc = coordinates(columns, u)
        vc = sum(parity(v & col) << j for j, col in enumerate(columns))
        a, b = uc >> active, vc >> active
        eta = int(bool(a)) + int(bool(b))
        need(eta <= 1 + new_phi - old_phi, 'local charge exceeds inversion defect')
        tail, added = split(r - active, a, b)
        old_tail = columns[active:]
        columns = columns[:active] + [combine(old_tail, x) for x in tail]
        active += added
        need(block_identity(conjugate(next_current, columns), active), 'residual block invariant')
        charges.append({'eta': eta, 'phi_before': old_phi, 'phi_after': new_phi, 'added': added})
        current = next_current
    need(current == identity(r), 'right peeling did not end at identity')
    need(active - w <= len(word) - length, 'global slack bound')
    need(columns[:w] == [1 << j for j in range(w)]
         and all(not (x & ((1 << w) - 1)) for x in columns[w:]), 'basis must fix original active block')
    reduced = []
    for label, u, v in word:
        uc = coordinates(columns, u)
        vc = sum(parity(v & col) << j for j, col in enumerate(columns))
        need(uc < 1 << active and vc < 1 << active and parity(uc & vc), 'global factor support')
        reduced.append([label, uc, vc])
    transformed = conjugate(target, columns)
    reduced_endpoint = endpoint(active, reduced)
    need(block_identity(transformed, active), 'discarded block not identity')
    need(reduced_endpoint == tuple(tuple(row[:active]) for row in transformed[:active]), 'formal endpoint restriction')
    need(tuple(tuple(row[:w]) for row in reduced_endpoint[:w]) == tuple(tuple(row[:w]) for row in target[:w]), 'original active endpoint changed')
    return {'name': case['name'], 'roles': r, 'active': w, 'calls': len(word),
            'crossing_rank': length, 'slack': len(word) - length, 'retained_roles': active,
            'basis_columns': columns, 'reduced_word': reduced, 'peel_charges': charges,
            'original_endpoint_sha256': digest(target), 'reduced_endpoint_sha256': digest(reduced_endpoint)}


def gl4(prefix=(), span=frozenset((0,))):
    if len(prefix) == 4:
        yield prefix
        return
    for row in range(1, 16):
        if row not in span:
            yield from gl4(prefix + (row,), span | frozenset(x ^ row for x in span))


def local_controls():
    projectors = [(u, v) for u in range(1, 16) for v in range(1, 16) if parity(u & v)]
    expanded = [(u, v, sum(3 << (2*j) for j in bits(u)), sum(3 << (2*j) for j in bits(v)))
                for u, v in projectors]
    mask = 0b01010101
    crossing = lambda matrix: rank(matrix[j] & mask for j in (1, 3, 5, 7))
    distribution, total = {}, 0
    for active in gl4():
        matrix = active + (16, 32, 64, 128)
        before = crossing(matrix)
        for u, v, um, vm in expanded:
            after = tuple(row ^ vm if parity(row & um) else row for row in matrix)
            change = crossing(after) - before
            eta = int(bool(u >> 2)) + int(bool(v >> 2))
            need(eta <= 1 + change, 'quantitative local charge failed')
            key = str(eta) + ':' + str(change)
            distribution[key] = distribution.get(key, 0) + 1
            total += 1
    need(total == 2419200 and distribution.get('2:1', 0) > 0, 'complete local control domain')
    need(all(key == '2:1' for key in distribution if key.startswith('2:')), 'two-sided sharp charge')
    return {'active_GL4_matrices': 20160, 'projectors': 120, 'peels': total,
            'address_dimension': 2, 'active_roles': 2, 'spectator_roles': 2, 'eta_delta_phi_counts': distribution}


def compute():
    cases = json.loads((HERE / 'CASES.json').read_text())
    splits = 0
    for q in range(5):
        for a in range(1 << q):
            for b in range(1 << q):
                split(q, a, b)
                splits += 1
    return {'scope': 'finite controls for the written dimension-independent proof',
            'local_charge': local_controls(), 'split_pairs': splits,
            'fixtures': [compress(case) for case in cases]}


def main():
    result = compute()
    saved = json.loads((HERE / 'RESULT.json').read_text())
    need(json.dumps(result, sort_keys=True) == json.dumps(saved, sort_keys=True), 'constructive receipt mismatch')
    print('PASS_S4_SLACK_BOUND peels=2419200 split_pairs=341 fixtures=' + str(len(result['fixtures'])))


if __name__ == '__main__':
    main()
