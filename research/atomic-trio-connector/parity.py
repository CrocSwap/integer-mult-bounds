#!/usr/bin/env python3
"""Exact parity supplement to Riquelme Soares's atomic-TRIO exclusion.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
No ten odd-weight steps can cover F2^5 by boundary differences: ten closed
steps leave at most five prefixes in each parity class. See PARITY.md.
"""
from collections import Counter, deque
from itertools import combinations


def require(ok, message):
    if not ok:
        raise ValueError(message)


def generators():
    maps = [tuple(x ^ (1 << i) for x in range(16)) for i in range(4)]
    maps += [tuple(x ^ (((x >> i) & 1) << j) for x in range(16))
             for i in range(4) for j in range(4) if i != j]
    for mapping in maps:
        require(set(mapping) == set(range(16)), 'generator must be bijective')
        # Every translated map is affine, checked on the complete domain.
        require(all(mapping[x ^ y] == mapping[x] ^ mapping[y] ^ mapping[0]
                    for x in range(16) for y in range(16)), 'generator must be affine')
    return maps


def orbit(seed, maps):
    seen = {seed}
    queue = deque([seed])
    while queue:
        current = queue.popleft()
        for mapping in maps:
            target = tuple(sorted(mapping[x] for x in current))
            require(len(set(target)) == 5, 'lost a point')
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def differences(A, B):
    even = {x ^ y for x in A for y in A} | {x ^ y for x in B for y in B}
    odd = {x ^ y for x in A for y in B}
    return len(even), len(odd)


def full_difference_bitset(A, B):
    # Independent full F2^5 representation: low four bits parameterize a parity
    # coset; bit4 records parity. This is a linear coordinate chart, not weight.
    points = tuple(A) + tuple(16 | x for x in B)
    bits = 0
    for i, x in enumerate(points):
        bits |= 1
        for y in points[i + 1:]:
            bits |= 1 << (x ^ y)
    return bits


EXPECTED = [
    {(8,8):112,(12,13):1312,(12,14):384,(12,16):768,
     (14,14):768,(14,15):256,(14,16):768},
    {(11,11):16,(12,13):560,(13,13):480,(14,14):1440,(14,15):160,
     (14,16):480,(15,15):960,(15,16):80,(16,15):192},
]
SEEDS = ((0,1,2,3,4), (0,1,2,4,8))


def check_histogram(observed, expected):
    require(dict(observed) == expected, 'histogram mismatch')
    require(sum(observed.values()) == 4368, 'missing five-subsets')
    require(observed.get((16,16),0) == 0, 'full parity cover')


def main():
    universe = set(combinations(range(16),5))
    maps = generators()
    orbits = [orbit(seed,maps) for seed in SEEDS]
    require([len(x) for x in orbits] == [1680,2688], 'orbit counts')
    require(orbits[0].isdisjoint(orbits[1]), 'overlapping representatives')
    require(orbits[0] | orbits[1] == universe, 'unclassified five-subset')
    for seed,expected in zip(SEEDS,EXPECTED):
        hist = Counter()
        for B in sorted(universe):
            pair = differences(seed,B)
            bits = full_difference_bitset(seed,B)
            require(pair == ((bits & 65535).bit_count(), (bits >> 16).bit_count()),
                    'independent full difference set disagrees')
            hist[pair] += 1
        check_histogram(hist,expected)
    # Mutation controls exercise the actual acceptance predicates.
    bad = dict(EXPECTED[0]);bad[(16,16)]=1
    try:
        check_histogram(bad,EXPECTED[0])
    except ValueError as error:
        require(str(error)=='histogram mismatch','wrong corruption rejection')
    else:
        raise ValueError('accepted extra covering row')
    bad = dict(EXPECTED[0]);bad[(8,8)]-=1
    try:
        check_histogram(bad,bad)
    except ValueError as error:
        require(str(error)=='missing five-subsets','wrong missing-row rejection')
    else:
        raise ValueError('accepted incomplete inventory')
    # Positive control uses the unchanged twelve-toggle predecessor word.
    import verify as original
    steps=[1 << j for j in original.twelve_toggle_word()]
    require(original.difference_mask(steps)==(1<<32)-1,'positive covering control')
    require(original.prefixes(steps)[-1]==0,'positive restoration control')
    print('PASS_PARITY_TEN_ODD_STEPS orbits=1680,2688 cases=8736 max_coverage=30,31 full_covers=0')


if __name__ == '__main__':
    main()
