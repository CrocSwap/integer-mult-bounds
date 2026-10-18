"""KB3i probe: exact covering-split census for the reduced (A, B) problem,
to understand the even-split obstruction behind the m=5 ground truth
(F2^5 covers exist only in splits (2,8)(4,6)(6,4)(8,2)) and to test whether
it lifts to the both-odd splits (11,7)/(9,9) of the 18-point question.

Reduced covering object (PR 2911 reduction lemma, cover18.py docstring):
for a group G = F2^m (2^m elements, XOR), a pair (A, B) of subsets COVERS iff
    (i)   A + B = G                (cross sums reach every element)
    (ii)  (A+A) u (B+B) = G        (self sums reach every element)
where + is XOR.  The original P+P = F2^{m+1} cover with parity split (s, t)
corresponds to the reduced (A, B) cover of F2^m with |A| = s, |B| = t.

Everything is exact integer arithmetic (int bitmasks, no floats).  Brute
force is complete at m = 3 (2^8 x 2^8) and targeted-complete at m = 4 for
the splits that matter.  A found cover is a WITNESS (the split is possible);
an exhaustive empty scan PROVES the split impossible for that m.
"""

import sys
from itertools import combinations

sys.stdout.reconfigure(encoding="utf-8")


def popcount(x):
    return x.bit_count()


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


def trans(mask, a):
    """{x ^ a : x in mask} as a bitmask."""
    out = 0
    x = mask
    while x:
        lsb = x & -x
        out |= 1 << ((lsb.bit_length() - 1) ^ a)
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


def selfsum(mx):
    return sumset(mx, mx)


def covers_pair(amask, bmask, gsize):
    """Reduced covering test: A+B = G and (A+A) u (B+B) = G."""
    allg = (1 << gsize) - 1
    cross = sumset(amask, bmask)
    if cross != allg:
        return False, "cross"
    selfs = selfsum(amask) | selfsum(bmask)
    if selfs != allg:
        return False, "self"
    return True, "cover"


def census_m3():
    """Complete census of reduced covering pairs (A, B) in F2^3 (8 elements),
    by split (|A|, |B|).  Every subset pair is tested."""
    gsize = 8
    subsets = list(range(1 << gsize))
    # For each split (a, b) count covering pairs and record a witness.
    result = {}
    for a in range(gsize + 1):
        for b in range(gsize + 1):
            count = 0
            witness = None
            Alist = [s for s in subsets if popcount(s) == a]
            Blist = [s for s in subsets if popcount(s) == b]
            for am in Alist:
                for bm in Blist:
                    ok, _ = covers_pair(am, bm, gsize)
                    if ok:
                        count += 1
                        if witness is None:
                            witness = (elems(am), elems(bm))
            result[(a, b)] = (count, witness)
    return result


def census_m4_split(a, b):
    """Complete census of reduced covering pairs (A, B) in F2^4 (16 elements)
    for one split (a, b).  Returns (count, witness).  Complete: enumerates
    every A of size a and every B of size b."""
    gsize = 16
    Alist = [mask_of(c) for c in combinations(range(gsize), a)]
    Blist = [mask_of(c) for c in combinations(range(gsize), b)]
    count = 0
    witness = None
    for am in Alist:
        for bm in Blist:
            ok, _ = covers_pair(am, bm, gsize)
            if ok:
                count += 1
                if witness is None:
                    witness = (elems(am), elems(bm))
    return count, witness


def summarize_m3():
    res = census_m3()
    print("=== Reduced covering census, F2^3 (G has 8 elements), COMPLETE ===")
    print("split  covers  witness")
    for a in range(9):
        for b in range(9):
            cnt, wit = res[(a, b)]
            if cnt > 0:
                print("(%d,%d)  %d  A=%s B=%s" % (a, b, cnt, wit[0], wit[1]))
    print("--- empty (no cover) splits ---")
    empties = [(a, b) for a in range(9) for b in range(9) if res[(a, b)][0] == 0]
    # group by parity
    both_odd_empty = [s for s in empties if s[0] % 2 == 1 and s[1] % 2 == 1]
    both_even_empty = [s for s in empties if s[0] % 2 == 0 and s[1] % 2 == 0]
    mixed_empty = [s for s in empties if s[0] % 2 != s[1] % 2]
    print("both-odd empty:", both_odd_empty)
    print("both-even empty:", both_even_empty)
    print("mixed empty:", mixed_empty)
    nonempty = [(a, b) for a in range(9) for b in range(9) if res[(a, b)][0] > 0]
    print("nonempty splits:", nonempty)
    both_odd_nonempty = [s for s in nonempty if s[0] % 2 == 1 and s[1] % 2 == 1]
    print("both-odd NONEMPTY (any cover):", both_odd_nonempty)


def summarize_m4():
    print("=== Reduced covering census, F2^4 (G has 16 elements), targeted ===")
    # splits summing to 10 (the F2^5 k=10 analogue) and to 18's analogue.
    targets = [
        (1, 9), (2, 8), (3, 7), (4, 6), (5, 5), (6, 4), (7, 3), (8, 2), (9, 1),
        (2, 2), (3, 3), (4, 4),  # small both parity controls
    ]
    print("split  covers  witness")
    for (a, b) in targets:
        cnt, wit = census_m4_split(a, b)
        print("(%d,%d)  %d  %s" % (a, b, cnt, ("A=%s B=%s" % wit) if wit else "-"))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "m3"
    if mode == "m3":
        summarize_m3()
    elif mode == "m4":
        summarize_m4()
    else:
        raise SystemExit("usage: parity_census.py m3|m4")
