#!/usr/bin/env python3
"""Exact finite corroboration of the new low-overhead lower-bound lemmas."""

import hashlib
import itertools
import json
import platform
from pathlib import Path


FILES = ('README.md', 'PROOF.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def replay(initial, word):
    """Bounded formal-row interpreter, with explicit checks under -O."""
    n = len(initial)
    require(2 <= n <= 8, 'row capacity')
    require(len(word) <= 12, 'word capacity')
    require(all(type(x) is int and 0 < x < 1 << n for x in initial), 'row domain')
    require(rank(initial, n) == n, 'initial coefficient matrix')
    rows = list(initial)
    states = [tuple(rows)]
    for gate in word:
        require(type(gate) is tuple and len(gate) == 2, 'gate shape')
        d, s = gate
        require(type(d) is int and type(s) is int, 'gate type')
        require(0 <= d < n and 0 <= s < n and d != s, 'gate indices')
        rows[d] ^= rows[s]
        states.append(tuple(rows))
    return states


def rank(rows, n):
    require(1 <= n <= 8 and len(rows) <= 8, 'rank capacity')
    pivots = [0] * n
    result = 0
    for original in rows:
        x = original
        for bit in range(n - 1, -1, -1):
            if not x >> bit & 1:
                continue
            if pivots[bit]:
                x ^= pivots[bit]
            else:
                pivots[bit] = x
                result += 1
                break
    return result


def one_write_check():
    """Every nonzero CNOT input changes its destination in all GL3 bases."""
    bases = transitions = 0
    for rows in itertools.product(range(1, 8), repeat=3):
        if rank(rows, 3) != 3:
            continue
        bases += 1
        for d, s in itertools.permutations(range(3), 2):
            end = replay(rows, ((d, s),))[-1]
            require(end[d] != rows[d], 'single incoming write returned unchanged')
            transitions += 1
    require(bases == 168 and transitions == 1008, 'GL3 enumeration')
    return {'bases': bases, 'transitions': transitions}


def fixed_source_check():
    """Complete words through six gates on two sources and two dirty rows."""
    alphabet = tuple((d, s) for d in (2, 3) for s in range(4) if s != d)
    words = cuts = 0
    for length in range(7):
        for word in itertools.product(alphabet, repeat=length):
            states = replay((1, 2, 4, 8), word)
            for rows in states:
                require(rows[:2] == (1, 2), 'source changed')
                x, y = rows[2] >> 2, rows[3] >> 2
                determinant = (x & 1) * (y >> 1 & 1) ^ (x >> 1 & 1) * (y & 1)
                require(determinant == 1, 'dirty block not invertible')
                require(x != 0 and y != 0, 'pure source row appeared')
                cuts += 1
            words += 1
    require(words == sum(6 ** j for j in range(7)), 'word coverage')
    return {'words': words, 'cuts': cuts}


def twice_written_check():
    """All 2+2 writes on A,T, with three frozen external rows."""
    words = restored = pure = 0
    orders = tuple(sorted(set(itertools.permutations((0, 0, 1, 1)))))
    source_choices = tuple(tuple(s for s in range(5) if s != d) for d in (0, 1))
    for p in range(8):
        source_part = (p & 1) | ((p >> 1 & 1) << 2) | ((p >> 2 & 1) << 3)
        initial = (1, 2, 4, 8, 16 | source_part)
        for order in orders:
            for choices in itertools.product(range(4), repeat=4):
                word = tuple((d, source_choices[d][q]) for d, q in zip(order, choices))
                states = replay(initial, word)
                words += 1
                if states[-1][0] != 1:
                    continue
                restored += 1
                after_first_t = states[order.index(1) + 1][1]
                if after_first_t & 18 == 0:
                    require(after_first_t == 1, 'twice-written target supplied a parity')
                    pure += 1
    require(words == 8 * 6 * 4 ** 4, 'two-write coverage')
    require(pure > 0, 'pure-intermediate case was not exercised')
    return {'words': words, 'restored_source': restored, 'pure_intermediates': pure}


def budget_check():
    """Enumerate surplus allocations for nine targets, three sources, two extras."""
    profiles = valid = with_source = 0
    for surplus in range(4):
        for destinations in itertools.combinations_with_replacement(range(14), surplus):
            counts = [0] * 14
            for d in destinations:
                counts[d] += 1
            profiles += 1
            if any(counts[d] == 1 for d in range(9, 14)):
                continue
            valid += 1
            changed_sources = [d for d in range(9, 12) if counts[d]]
            if not changed_sources:
                require(sum(counts[:9]) <= 3, 'no-source surplus')
                continue
            with_source += 1
            require(len(changed_sources) == 1, 'two changed sources fit the budget')
            m = counts[changed_sources[0]]
            require(m in (2, 3) and counts[12:] == [0, 0], 'source case classification')
            require(sum(counts[:9]) <= 3 - m, 'remaining target writes')
    return {'profiles': profiles, 'valid_profiles': valid, 'source_profiles': with_source}


def itinerary_check():
    """Relaxation allows every pure source mask, including zero, at each cut."""
    required = {3, 5, 7}
    cases = 0
    for anchor in (1, 2, 4):
        for writes in (1, 2, 3):
            for middle in itertools.product(range(8), repeat=writes - 1):
                states = (anchor,) + middle + (anchor,)
                require(not required.issubset(states), 'short closed itinerary covered all parities')
                cases += 1
    require(cases == 219, 'itinerary coverage')
    require(required.issubset((1, 3, 7, 5, 1)), 'four-write boundary control')
    return {'closed_itineraries': cases, 'four_write_control': 1}


def controls():
    bad = (
        ((1,), ()),
        ((1, 2), ((0, 0),)),
        ((1, 2), ((2, 0),)),
        ((1, 2), ((True, 0),)),
        ((1, 0), ()),
        ((1, 1), ()),
        ((1, 2), ((0, 1, 0),)),
        ((1, 2), ((0, 1),) * 13),
    )
    rejected = 0
    for initial, word in bad:
        try:
            replay(initial, word)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('invalid interpreter input accepted')
    require(rejected == len(bad), 'rejection count')
    leaking = replay((1, 2, 4, 8), ((0, 1), (0, 2), (1, 0), (1, 3)))
    require(leaking[-1][0] != 1 and leaking[3][1] == 5, 'restoration discriminator')
    coded = replay((1, 2, 4), ((0, 1), (2, 0)))
    require(coded[-1][2] == 7, 'fixed-source premise discriminator')
    require(rank((1, 1), 2) == 1, 'dirty singularity discriminator')
    return {'invalid_inputs_rejected': rejected, 'semantic_controls': 3}


def receipt_hashes():
    root = Path(__file__).resolve().parent
    hashes = {}
    for name in FILES:
        with (root / name).open('rb') as stream:
            payload = stream.read(262145)
        require(len(payload) <= 262144, 'receipt file capacity')
        hashes[name] = hashlib.sha256(payload).hexdigest()
    return hashes


def main():
    counts = {
        'one_write': one_write_check(),
        'fixed_sources': fixed_source_check(),
        'twice_written': twice_written_check(),
        'surplus': budget_check(),
        'itineraries': itinerary_check(),
        'controls': controls(),
    }
    print(json.dumps({
        'status': 'PASS_GLOBAL_THIRTEEN_ADD_LOWER_BOUND',
        'claim_type': 'scoped written proof; finite lemma corroboration',
        'lower_bound': 13,
        'counts': counts,
        'python': platform.python_version(),
        'sha256': receipt_hashes(),
    }, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
