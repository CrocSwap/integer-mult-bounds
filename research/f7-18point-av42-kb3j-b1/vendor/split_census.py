"""Fast reduced-covering census for one split (a, b) in F2^m, with a
precomputed XOR-translate table.  Reports covering count, a first witness,
and a breakdown of WHICH condition fails (cross-only, self-only, both) so the
obstruction to a split is localized.  Exact integer arithmetic (int masks).

Reduced covering (PR 2911 lemma): (A,B) covers G=F2^m iff
    cross:  A+B = G
    self:   (A+A) u (B+B) = G
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
    # XOR table: xors[a][b] = 1 << (a ^ b)
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


def census_split(m, a, b, stop_on_witness=False):
    gsize, allg, sumset = build(m)
    Alist = [mask_of(c) for c in combinations(range(gsize), a)]
    Blist = [mask_of(c) for c in combinations(range(gsize), b)]
    count = 0
    witness = None
    cross_only = 0  # cross covers but self fails
    self_only = 0   # self covers but cross fails
    both_fail = 0
    for am in Alist:
        # precompute selfsum(A) once per A
        ssa = sumset(am, am)
        for bm in Blist:
            cross = sumset(am, bm) == allg
            selfs = (ssa | sumset(bm, bm)) == allg
            if cross and selfs:
                count += 1
                if witness is None:
                    witness = (elems(am), elems(bm))
                if stop_on_witness:
                    return count, witness, (cross_only, self_only, both_fail)
            elif cross and not selfs:
                cross_only += 1
            elif selfs and not cross:
                self_only += 1
            else:
                both_fail += 1
    return count, witness, (cross_only, self_only, both_fail)


if __name__ == "__main__":
    m = int(sys.argv[1])
    a = int(sys.argv[2])
    b = int(sys.argv[3])
    stop = len(sys.argv) > 4 and sys.argv[4] == "stop"
    cnt, wit, brk = census_split(m, a, b, stop_on_witness=stop)
    print("F2^%d split (%d,%d): covers=%d  cross_only=%d self_only=%d both_fail=%d"
          % (m, a, b, cnt, brk[0], brk[1], brk[2]))
    if wit:
        print("  witness A=%s B=%s" % (wit[0], wit[1]))
