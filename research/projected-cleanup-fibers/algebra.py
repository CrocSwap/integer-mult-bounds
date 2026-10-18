"""Binary row matrices, constructive joint-range theorem and small exact census.

Gareth Davidson with substantial OpenAI Codex assistance; Apache-2.0.
See PROOF.md for the all-dimension argument and predecessor attribution.
"""
from collections import Counter, deque
import hashlib
import itertools
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return tuple(1 << i for i in range(n))


def valid(a):
    n = len(a)
    need(n > 0 and all(type(r) is int and 0 <= r < 1 << n for r in a), 'invalid binary matrix')


def apply(rows, gate):
    d, s = gate
    need(type(d) is int and type(s) is int and 0 <= d < len(rows) and 0 <= s < len(rows) and d != s,
         'invalid CNOT')
    out = list(rows)
    out[d] ^= out[s]
    return tuple(out)


def product(a, b):
    need(len(a) == len(b), 'matrix dimensions')
    out = []
    for row in a:
        value = 0
        while row:
            bit = row & -row
            value ^= b[bit.bit_length()-1]
            row ^= bit
        out.append(value)
    return tuple(out)


def word_matrix(n, word, projected_z=None):
    a = identity(n)
    for gate in word:
        if projected_z is None or gate[0] < projected_z:
            a = apply(a, gate)
    return a


def factor(a, z=None):
    """Chronological CNOT factorization; z restricts destinations and fixed rows."""
    valid(a)
    n = len(a)
    k = n if z is None else z
    need(type(k) is int and 1 <= k <= n, 'invalid active dimension')
    if z is not None:
        need(a[k:] == identity(n)[k:], 'matrix does not fix target rows')
    rows = tuple(a)
    reduction = []

    def gate(d, s):
        nonlocal rows
        reduction.append((d, s))
        rows = apply(rows, (d, s))

    for col in range(k):
        pivot = next((i for i in range(col, k) if rows[i] >> col & 1), None)
        need(pivot is not None, 'singular matrix')
        if pivot != col:
            gate(col, pivot)
            gate(pivot, col)
            gate(col, pivot)
        for i in range(k):
            if i != col and rows[i] >> col & 1:
                gate(i, col)
    for i in range(k):
        for j in range(k, n):
            if rows[i] >> j & 1:
                gate(i, j)
    need(rows == identity(n), 'incomplete reduction')
    return list(reversed(reduction))


def inverse(a):
    return word_matrix(len(a), reversed(factor(a)))


def loop(n, z, d, s):
    """Raw identity with projected effect E_ds, with sharp elementary length."""
    need(type(n) is int and type(z) is int and 1 <= z < n, 'both coordinate classes required')
    need(0 <= d < z and 0 <= s < n and d != s, 'projected elementary gate required')
    target = next((t for t in range(z, n) if t != s), None)
    if target is None:
        # Exactly one target, and it is the source. (E_ds E_sd)^3=I.
        return [(d, s), (s, d)]*3
    return [(d, target), (target, s), (d, target), (target, s), (d, s)]


def joint_word(raw, projected, z):
    """Any (raw, projected) in GL(n,2) x H_z is attained, no clean work."""
    n = len(raw)
    need(1 <= z < n and len(projected) == n, 'joint dimensions')
    prefix = factor(raw)
    factor(projected, z)  # Explicitly validate membership, including invertibility.
    initial = word_matrix(n, prefix, z)
    correction = product(projected, inverse(initial))
    suffix = [g for d, s in factor(correction, z) for g in loop(n, z, d, s)]
    return prefix+suffix


def order_gl(n):
    return __import__('math').prod((1 << n)-(1 << j) for j in range(n))


def all_gl(n):
    result = []
    for rows in itertools.product(range(1, 1 << n), repeat=n):
        try:
            factor(rows)
        except ValueError:
            continue
        result.append(rows)
    need(len(result) == order_gl(n), 'GL enumeration count')
    return result


def all_parabolic(n, z):
    for a in all_gl(z):
        for b in itertools.product(range(1 << (n-z)), repeat=z):
            yield tuple(a[i] | (b[i] << z) for i in range(z))+identity(n)[z:]


def census(n, z):
    """Complete paired-state graph; construct every endpoint independently too."""
    gates = [(d, s) for d in range(n) for s in range(n) if d != s]
    unit = identity(n)
    start = (unit, unit)
    parents = {start: None}
    distance = {start: 0}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        for gate in gates:
            nxt = (apply(state[0], gate), apply(state[1], gate) if gate[0] < z else state[1])
            if nxt not in parents:
                parents[nxt] = (state, gate)
                distance[nxt] = distance[state]+1
                queue.append(nxt)
    expected = order_gl(n)*order_gl(z)*(1 << (z*(n-z)))
    need(len(parents) == expected, 'joint range census')
    raw_values = all_gl(n)
    projected_values = list(all_parabolic(n, z))
    need(set(parents) == set(itertools.product(raw_values, projected_values)), 'joint range not full product')
    representatives = []
    construction_max = 0
    for state in sorted(parents):
        word = []
        here = state
        while parents[here] is not None:
            here, gate = parents[here]
            word.append(gate)
        word.reverse()
        built = joint_word(*state, z)
        need(word_matrix(n, built) == state[0] and word_matrix(n, built, z) == state[1], 'joint constructor')
        construction_max = max(construction_max, len(built))
        representatives.append((state, word))
    elementary = []
    for d in range(z):
        for s in range(n):
            if s == d:
                continue
            projected = apply(unit, (d, s))
            short = loop(n, z, d, s)
            need(distance[unit, projected] == len(short), 'elementary loop not shortest')
            elementary.append(dict(destination=d, source=s, minimum=len(short)))
    blob = json.dumps([[list(a), list(b), distance[a, b]] for a, b in sorted(parents)], separators=(',', ':')).encode()
    return dict(n=n, z=z, states=len(parents), edges=len(parents)*len(gates),
                diameter=max(distance.values()), layers=dict(sorted(Counter(distance.values()).items())),
                distance_sha256=hashlib.sha256(blob).hexdigest(), elementary=elementary,
                constructor_max_gates=construction_max), representatives


def short_relations():
    """Complete two-product classification on four labels, supporting the proof."""
    n = 4
    gates = [(d, s) for d in range(n) for s in range(n) if d != s]
    pairs = {}
    for first, second in itertools.product(gates, repeat=2):
        m = word_matrix(n, (first, second))
        pairs.setdefault(m, []).append((first, second))
    checks = 0
    for m, words in pairs.items():
        for a, b in itertools.product(words, repeat=2):
            if m == identity(n):
                need(a[0] == a[1] and b[0] == b[1], 'nontrivial two-gate identity')
            else:
                need(a == b or (a == b[::-1] and word_matrix(n, a) == word_matrix(n, a[::-1])),
                     'unexpected two-product relation')
            relator = list(a)+list(reversed(b))
            for z in range(1, n):
                need(word_matrix(n, relator, z) == identity(n), 'short identity has projected defect')
                checks += 1
    # GL(2,2) local-block fact used in the unique-target six-gate lower bound.
    block_words = 0
    for length in range(6):
        for choices in itertools.product(((0, 1), (1, 0)), repeat=length):
            if word_matrix(2, choices) == identity(2):
                need(sum(g == (0, 1) for g in choices) % 2 == 0, 'short two-row odd crossing')
            block_words += 1
    return dict(two_products=len(gates)**2, distinct_products=len(pairs),
                projected_relation_checks=checks, two_row_words_through_length5=block_words)
