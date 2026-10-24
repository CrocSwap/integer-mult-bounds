#!/usr/bin/env python3
"""Enumerate actual binary subspace sets, without the primary rank engine.

Nick Petalas. Apache-2.0.
"""
from itertools import permutations


def check(ok, message):
    if not ok:
        raise ValueError(message)


def send(value, permutation, addresses):
    out = 0
    for i, (a, b) in enumerate(addresses):
        if value >> i & 1:
            target = addresses.index((permutation[a], permutation[b]))
            out ^= 1 << target
    return out


def controlled(value, g, u, v, addresses):
    width = len(addresses)
    mask = (1 << width)-1
    read = 0
    for role in range(3):
        if v >> role & 1:
            read ^= (value >> (role*width)) & mask
    delta = read ^ send(read, g, addresses)
    out = value
    for role in range(3):
        if u >> role & 1:
            out ^= delta << (role*width)
    return out


def dimension(size):
    check(size > 0 and size & (size-1) == 0, "not a binary subspace size")
    return size.bit_length()-1


def main():
    address = [(i, j) for i in range(3) for j in range(3) if i != j]
    positive = [r*6+i for r in range(3) for i, (a, b) in enumerate(address) if a < b]
    h = {sum(((bits >> j) & 1) << i for j, i in enumerate(positive))
         for bits in range(1 << 9)}
    total, kinds = 0, set()
    for active in permutations(range(3)):
        pi = tuple(active.index(i) for i in range(3))
        z = {(value & ~63) | send(value & 63, pi, address) for value in h}
        before = 9-dimension(len(h & z))
        for g in permutations(range(3)):
            d = sum(g[i] > g[j] for i in range(3) for j in range(i+1, 3))
            if d == 0:
                continue
            gi = tuple(g.index(i) for i in range(3))
            for u in range(1, 8):
                for v in range(1, 8):
                    if (u & v).bit_count() % 2 != 1:
                        continue
                    y = {controlled(value, gi, u, v, address) for value in h}
                    after = 9-dimension(len(y & z))
                    eta = int(u >> 1 != 0)+int(v >> 1 != 0)
                    check(d*eta <= d+after-before, "enumerated subspace charge failed")
                    kinds.add((d, eta))
                    total += 1
    check(total == 840, "incomplete finite domain")
    check(kinds == {(d, eta) for d in (1, 2, 3) for eta in (0, 1, 2)}, "missing boundary case")
    print("PASS_SUBSPACE_SET_ORACLE", total, "literal subspace intersections")


if __name__ == "__main__":
    main()
