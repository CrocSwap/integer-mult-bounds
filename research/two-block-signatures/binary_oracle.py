"""Exhaustive ordered complementary row spaces over F2, independent of the signature criterion."""
from collections import Counter
from itertools import combinations


def spaces(n, d):
    """Every d-space once in reduced row-echelon form, with all its vectors."""
    for pivots in combinations(range(n), d):
        free = [(i,j) for i,p in enumerate(pivots) for j in range(p+1,n) if j not in pivots]
        for assignment in range(1 << len(free)):
            basis = [1 << j for j in pivots]
            for k,(i,j) in enumerate(free):
                if assignment >> k & 1:
                    basis[i] |= 1 << j
            words = [0]
            for row in basis:
                words += [x ^ row for x in words]
            support = 0
            elements = 0
            for word in words:
                support |= word
                elements |= 1 << word
            axes = sum(1 << j for j in range(n) if (1 << j) in words)
            yield elements, support, axes


def spread(mask, n):
    return sum(((mask >> j) & 1) << (4*j) for j in range(n))


def enumerate_pairs(n, p):
    """A source mask reads block columns. A reader mask reads opposite axes."""
    full = (1 << n)-1
    # Separate the bit positions that each plane contributes to each nibble.
    left = [(elements, 4*spread(s,n) + 2*spread(full^e,n)) for elements,s,e in spaces(n,p)]
    right = [(elements, 8*spread(s,n) + spread(full^e,n)) for elements,s,e in spaces(n,n-p)]
    tally = Counter()
    for vectors, x in left:
        for other, y in right:
            if vectors & other == 1:  # The all-zero vector is the only common vector.
                tally[x+y] += 1
    return len(left), len(right), tally
