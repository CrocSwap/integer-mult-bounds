"""Probe the (5,5) self-obstruction at m=4: every cross-covering (A,B) pair
(|A|=|B|=5, A+B=F2^4) fails the self condition (A+A) u (B+B) = F2^4.  This
records WHY (the self-union deficit and the selfsum sizes / ranks), to see
whether the mechanism generalizes to the (9,9) split at m=6.  Exact integer
arithmetic (int masks).
"""

import sys
from itertools import combinations

sys.stdout.reconfigure(encoding="utf-8")


def mask_of(idxs):
    m = 0
    for i in idxs:
        m |= 1 << i
    return m


def elems(mask):
    out = []
    while mask:
        lsb = mask & -mask
        out.append(lsb.bit_length() - 1)
        mask ^= lsb
    return out


def build(m):
    gsize = 1 << m
    allg = (1 << gsize) - 1
    xors = [[1 << (i ^ j) for j in range(gsize)] for i in range(gsize)]

    def trans(mask, a):
        out = 0
        x = mask
        while x:
            lsb = x & -x
            out |= xors[lsb.bit_length() - 1][a]
            x ^= lsb
        return out

    def sumset(mx, my):
        out = 0
        x = mx
        while x:
            lsb = x & -x
            out |= trans(my, lsb.bit_length() - 1)
            x ^= lsb
        return out

    return gsize, allg, sumset


def rank_of(mask):
    """Linear rank over F2 of the elements of mask (as vectors)."""
    els = elems(mask)
    basis = []
    for e in els:
        v = e
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
            basis.sort(reverse=True)
    return len(basis)


def probe(m, a, b):
    gsize, allg, sumset = build(m)
    Alist = [mask_of(c) for c in combinations(range(gsize), a)]
    Blist = [mask_of(c) for c in combinations(range(gsize), b)]
    # For cross-covering pairs, record self-union size and per-side selfsum size.
    selfcover = 0
    crosscover = 0
    max_selfunion = -1
    selfunion_hist = {}
    selfsumA_hist = {}
    selfsumB_hist = {}
    example = None
    for am in Alist:
        ssa = sumset(am, am)
        for bm in Blist:
            if sumset(am, bm) != allg:
                continue
            crosscover += 1
            ssb = sumset(bm, bm)
            su = ssa | ssb
            su_sz = su.bit_count()
            selfunion_hist[su_sz] = selfunion_hist.get(su_sz, 0) + 1
            selfsumA_hist[ssa.bit_count()] = selfsumA_hist.get(ssa.bit_count(), 0) + 1
            selfsumB_hist[ssb.bit_count()] = selfsumB_hist.get(ssb.bit_count(), 0) + 1
            if su == allg:
                selfcover += 1
            if su_sz > max_selfunion:
                max_selfunion = su_sz
                example = (elems(am), elems(bm), ssa.bit_count(), ssb.bit_count(),
                           elems(allg ^ su))
    print("F2^%d (%d,%d): cross_covering=%d, of those self_covering=%d"
          % (m, a, b, crosscover, selfcover))
    print("  max |(A+A) u (B+B)| over cross-covering pairs = %d (of %d)"
          % (max_selfunion, gsize))
    print("  self-union size histogram:", dict(sorted(selfunion_hist.items())))
    print("  |A+A| histogram:", dict(sorted(selfsumA_hist.items())))
    print("  |B+B| histogram:", dict(sorted(selfsumB_hist.items())))
    if example:
        print("  max example: A=%s B=%s |A+A|=%d |B+B|=%d missed=%s"
              % (example[0], example[1], example[2], example[3], example[4]))


if __name__ == "__main__":
    m = int(sys.argv[1])
    a = int(sys.argv[2])
    b = int(sys.argv[3])
    probe(m, a, b)
