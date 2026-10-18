"""C3: the 112 ports of the ck provider word form a cap in F2^9 (no three XOR to 0) and every hyperplane misses at least 48 of them."""
import math
from common import *
P = load_json('derived', 'ck-CANONICAL-WORD.json.gz')['ports']; S = set(P)
check('C3 112 distinct nonzero ports in F2^9', len(P) == 112 and len(S) == 112 and 0 not in S and max(P) < 512)
trip = sum(1 for i in range(112) for j in range(i + 1, 112) if (P[i] ^ P[j]) in S)
check('C3 cap: no three ports XOR to 0', trip == 0, trip)
miss = min(sum(1 for p in P if bin(p & h).count('1') & 1) for h in range(1, 512))
check('C3 every hyperplane (511) misses at least 48 ports, and some hyperplane misses exactly 48', miss == 48, miss)
# consequence used in the notes (ARGUED, short proof in README): k readers' ports have rank r with k <= 2^(r-1) (a cap of F2^r has <= 2^(r-1) points),
# so an operand frame inside the common perp has dim <= 9 - r <= 8 - ceil(log2 k).  Numerical instance: rank of 8 ports of a cap is >= 4.
def rank(vs):
    b = {}
    for x in vs:
        for p in sorted(b, reverse=True):
            if x >> p & 1: x ^= b[p]
        if x: b[x.bit_length() - 1] = x
    return len(b)
import random
random.seed(1)
mn = min(rank(random.sample(P, 8)) for _ in range(20000))
check('C3 sampled 8-subsets of ports (20000): rank >= 4, so dim of the common perp <= 5', mn >= 4, mn)
finish()
