"""Independent free-algebra census of single leaf-destination error transport
in the PR628 balanced dirty word (compose: mid=n//2, ops (x,z,B,+),(z,y,A,+),(x,z,B,-),(z,y,A,-)).

For every leaf p (both orientations), inject a unit error at the destination register of
leaf p right after it executes, and replay all later leaves in the free noncommutative
algebra (monomial = tuple of factor indices, newest leftmost).  The envelope is the maximum,
over all later cuts and all registers, of the absolute coefficient sum of the entry.
Usage: python3 census.py N [N2 ...]   -> prints n, envelope, intervals, witness (orientation,p,cut,row)
"""
import sys


def word(n, sign=1, x=0, y=1, depth=2, off=0):
    """Event list (src,dst,factor,sign) of compose(x,y,factors[off:off+n],...) with given sign."""
    if n == 1:
        return [(x, y, off, sign)]
    mid = n // 2
    ops = [(x, depth, off, mid, 1), (depth, y, off + mid, n - mid, 1),
           (x, depth, off, mid, -1), (depth, y, off + mid, n - mid, -1)]
    if sign == -1:
        ops = [(s, d, o, k, -g) for s, d, o, k, g in reversed(ops)]
    out = []
    for s, d, o, k, g in ops:
        out += word(k, g, s, d, depth + 1, o)
    return out


def census(n, word_list):
    peak = 1
    wit = None
    intervals = 0
    L = len(word_list)
    for p in range(L):
        dest = word_list[p][1]
        col = {dest: {(): 1}}
        intervals += 1
        for t in range(p + 1, L):
            x, y, j, s = word_list[t]
            intervals += 1
            cx = col.get(x)
            if not cx:
                continue
            cy = col.setdefault(y, {})
            for m, c in cx.items():
                k = (j,) + m
                v = cy.get(k, 0) + s * c
                if v:
                    cy[k] = v
                else:
                    del cy[k]
            mass = 0
            for c in cy.values():
                mass += c if c > 0 else -c
            if mass > peak:
                peak = mass
                wit = (p + 1, t + 1, dest, y, dict(cy))
    return peak, intervals, wit


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        n = int(arg)
        best = None
        tot = 0
        for orient in (1, -1):
            w = word(n, orient)
            pk, iv, wit = census(n, w)
            tot += iv
            if best is None or pk > best[0]:
                best = (pk, orient, wit)
        pk, orient, wit = best
        print(n, pk, tot, orient, None if wit is None else wit[:4],
              None if wit is None else sorted(wit[4].items()), flush=True)
