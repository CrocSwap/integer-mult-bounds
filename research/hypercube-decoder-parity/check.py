#!/usr/bin/env python3
"""Exhaustive check of the k-port decoder parity obstruction (README.md). Standard library only.

Ports: k-subsets taking one coordinate from each of k distinct pairs among p coordinate pairs (k = 3 is the
paired-cube port of research/paired-cube-bit/LEMMA.md). A decoder in the star family writes, for every port T,

    x_T = sum_{0<l<k} a_l sum_{L <= T, |L| = l} star_L + sum_{0<j<k} b_j sum_{|S cap T| = j} x_S   (mod 2),

with star_L = sum of x_S over ports S containing L. For each (k, p) below, every coefficient vector (a, b) is
tested against every column of every port, and the count of valid decoders is compared with the closed form:
valid decoders exist iff k is not a power of two.
Copyright 2026 Joel Pulikkan (GamingPuzzled). Apache-2.0. Prepared with Anthropic Claude assistance.
"""
import itertools
import sys
from math import comb

if sys.flags.optimize:
    raise SystemExit('refusing -O')


def ports(p, k):
    return [frozenset(2 * q + e for q, e in zip(pairs, sel))
            for pairs in itertools.combinations(range(p), k) for sel in itertools.product(range(2), repeat=k)]


def valid_decoders(p, k):
    P = ports(p, k)
    overlap = [[len(S & T) for S in P] for T in P]
    found = []
    for a in itertools.product(range(2), repeat=k - 1):
        for b in itertools.product(range(2), repeat=k - 1):
            def coeff(j):
                return (sum(al * comb(j, l) for l, al in enumerate(a, 1)) + (b[j - 1] if 0 < j < k else 0)) % 2
            table = {j: coeff(j) for j in range(k + 1)}
            if all(table[overlap[t][s]] == (1 if s == t else 0) for t in range(len(P)) for s in range(len(P))):
                found.append((a, b))
    return len(P), found


def power_of_two(k):
    return k & (k - 1) == 0


def main():
    for k, p in ((3, 6), (4, 6), (5, 7), (6, 7)):
        n, found = valid_decoders(p, k)
        parity = [comb(k, l) % 2 for l in range(1, k)]
        assert (len(found) == 0) == power_of_two(k) == (not any(parity)), (k, p, len(found), parity)
        print('PASS k=%d p=%d: %d ports, %d valid star-family decoders; C(k,l) mod 2 for 0<l<k = %s'
              % (k, p, n, len(found), parity))
    n, found = valid_decoders(6, 3)
    assert ((1, 0), (1, 0)) in found, 'the paired-cube identity (level-1 stars, overlap-1 corrections)'
    print('PASS k=3 includes the paired-cube identity x_T = sum_{c in T} star(c) + sum_{|S cap T|=1} x_S')


if __name__ == '__main__':
    main()
