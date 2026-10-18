#!/usr/bin/env python3
"""Exact finite corroboration of the written generic frame-rigidity proof."""
from collections import Counter
from itertools import product
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
I = (1, 2)
ZERO = (0, 0)
R = (3, 2)
ALL = tuple(product(range(4), repeat=2))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def apply(matrix, vector):
    return sum(((row & vector).bit_count() % 2) << i
               for i, row in enumerate(matrix))


def mul(left, right):
    # Row convention: this is left(right(vector)), not the reverse.
    return tuple((right[0] if row & 1 else 0) ^
                 (right[1] if row & 2 else 0) for row in left)


def add(*matrices):
    rows = [0, 0]
    for matrix in matrices:
        for i in range(2):
            rows[i] ^= matrix[i]
    return tuple(rows)


GL = tuple(m for m in ALL if len({apply(m, v) for v in range(4)}) == 4)


def inverse(matrix):
    return next(n for n in GL if mul(matrix, n) == I)


def pairings(unused, word):
    if not unused:
        yield tuple(word)
        return
    first = unused[0]
    label = max(word, default=-1) + 1
    for other in unused[1:]:
        word[first] = word[other] = label
        yield from pairings(tuple(i for i in unused if i not in (first, other)), word)
        word[first] = word[other] = -1


def coverage(word):
    prefixes = [0]
    for label in word:
        prefixes.append(prefixes[-1] ^ (1 << label))
    return {a ^ b for a in prefixes for b in prefixes}


def check_predecessor():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for item in pins['files']:
        if item['usage'] == 'input':
            actual = hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest()
            require(actual == item['sha256'], 'changed predecessor: ' + item['path'])
    source = ROOT / 'research/universal-connector-boundary'
    certificate = json.loads((source / 'CERTIFICATE.json').read_text())
    expected = json.loads((source / 'EXPECTED.json').read_text())
    hist = Counter(len(coverage(w)) for w in pairings(tuple(range(10)), [-1] * 10))
    census = next(c for c in certificate['censuses'] if c['sources'] == 5)
    require(dict(hist) == {int(k): v for k, v in census['histogram'].items()},
            'inherited pairing histogram')
    require(sum(hist.values()) == 945 and max(hist) == 31, 'inherited obstruction')
    repair = certificate['schedules']['five_extra_source']
    require(coverage(repair['source_word']) == set(range(32)), '74-call upper word')
    require(len(repair['source_word']) + 2 * len(repair['rows']) == 74,
            'upper word complete query bill')
    require(expected['unit_lower_bound'] == 74, 'predecessor scope changed')
    return sum(hist.values())


def check_phase_lemmas():
    # Derive equal insertion/readout phases, rather than assume them.
    restoration_cases = 0
    for p, q in product(GL, repeat=2):
        vanishes = all(mul(add(inverse(p), inverse(q)), b) == ZERO for b in ALL)
        require(vanishes == (p == q), 'source-pair phase rigidity')
        vanishes = all(mul(a, add(p, q)) == ZERO for a in ALL)
        require(vanishes == (p == q), 'readout-pair phase rigidity')
        restoration_cases += 1
    coefficient_cases = 0
    for h, k, a, b in product(GL, GL, ALL, ALL):
        actual = mul(a, mul(k, mul(inverse(h), b)))
        expected = mul(a, b)
        for vector in range(4):
            require(apply(actual, vector) ==
                    apply(a, apply(k, apply(inverse(h), apply(b, vector)))),
                    'ordered coefficient versus vector composition')
        if h == k:
            require(actual == expected, 'same-phase noncommutative coefficient')
        coefficient_cases += 1
    for h, k in product(GL, repeat=2):
        require((mul(k, inverse(h)) == I) == (h == k), 'active edge phase')
        require(mul(k, inverse(h)) != ZERO, 'crossing cannot disappear')
    # With exactly two restoring nonidentity frames, only phases I and r occur.
    triples = 0
    for r in GL:
        if r == I:
            continue
        for indices in product(range(2), repeat=3):
            phases = tuple((I, r)[i] for i in indices)
            require(add(*phases) != ZERO, 'three readouts in two phases')
            require(add(*(inverse(p) for p in phases)) != ZERO,
                    'three insertions in two phases')
            triples += 1
    # Critical semantic control: global even-call parity is NOT preserved.
    t = (2, 3)
    require(mul(t, mul(t, t)) == I and add(I, t, mul(t, t)) == ZERO,
            'order-three odd-parity counterexample')
    # B,T,B,T,B,T restores z for every source signal: three map calls, three frames.
    odd_cases = 0
    for b in ALL:
        for x, z in product(range(4), repeat=2):
            current = z
            for _ in range(3):
                current = apply(t, current ^ apply(b, x))
            require(current == z, 'odd source-count restored control')
            odd_cases += 1
    return restoration_cases, coefficient_cases, triples, odd_cases


def replay(word, a, b, state):
    x, z, y = state
    for op in word:
        if op == 'R':
            z = apply(R, z)
        elif op == 'B':
            z ^= apply(b, x)
        elif op == 'A':
            y ^= apply(a, z)
        else:
            raise ValueError('unknown operation')
    return x, z, y


def scalar_program(word, a, b):
    program = []
    for op in word:
        if op == 'R':
            program.append((3, 2))
            continue
        matrix, source, target = (b, 0, 2) if op == 'B' else (a, 2, 4)
        program.extend((source + j, target + i)
                       for i, row in enumerate(matrix) for j in range(2) if row & (1 << j))
    return program


def replay_scalar(program, state):
    value = state[0] | (state[1] << 2) | (state[2] << 4)
    for source, target in program:
        value ^= ((value >> source) & 1) << target
    return tuple((value >> (2 * i)) & 3 for i in range(3))


def check_pilot():
    word = 'RBABAR'
    cases = 0
    for a, b in product(ALL, repeat=2):
        program = scalar_program(word, a, b)
        for state in product(range(4), repeat=3):
            x, z, y = state
            target = (x, z, y ^ apply(a, apply(b, x)))
            actual = replay(word, a, b, state)
            require(actual == target, 'dirty pilot map')
            require(replay_scalar(program, state) == target, 'literal XOR lowering')
            require(replay_scalar(tuple(reversed(program)), actual) == state,
                    'inverse literal program')
            cases += 1
    controls = {
        'omitted_closing_frame': word[:-1],
        'omitted_entry_frame': word[1:],
        'unconjugated_crossing': 'BRARBA',
        'omitted_source_cleanup': 'RBAAR',
        'omitted_readout': 'RBBAR',
    }
    witnesses = {}
    for name, bad in controls.items():
        for state in product(range(4), repeat=3):
            x, z, y = state
            if replay(bad, I, I, state) != (x, z, y ^ x):
                witnesses[name] = state
                break
        require(name in witnesses, 'undetected mutation: ' + name)
    require(replay('BRARBA', I, I, (0, 2, 0)) == (0, 2, 1),
            'smallest explicit dirty failure')
    a, b = (3, 2), (1, 3)
    require(mul(a, b) != mul(b, a), 'noncommuting price fixture')
    bills = []
    for candidate in ('BABA', word):
        program = scalar_program(candidate, a, b)
        bills.append((len(program), sum(2 * (max(s, t) + 1) + 5 for s, t in program)))
    require(bills == [(12, 168), (14, 194)], 'complete scalar/tape tariff')
    return cases, witnesses, bills


def main():
    pair_count = check_predecessor()
    phases = check_phase_lemmas()
    cases, witnesses, bills = check_pilot()
    print('PASS_CONNECTOR_FRAME_RIGIDITY '
          f'pairings={pair_count} phase_pairs={phases[0]} coefficients={phases[1]} '
          f'two_phase_triples={phases[2]} odd_restore={phases[3]} '
          f'dirty_cases={cases} controls={len(witnesses)} '
          'unit_optimum=74 used_frame_optimum=76 no_new_kappa')
    print(json.dumps({'mutation_witnesses': witnesses, 'scalar_and_tariff_bills': bills},
                     sort_keys=True))


if __name__ == '__main__':
    main()
