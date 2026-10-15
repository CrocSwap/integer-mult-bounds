"""Chain form: M(a,b) = Pre(b) o Pre(a)^-1, Pre(t) = time-ordered complete-phase transvections
along the ancestor chain of the leaf ending at cut t. Each transvection (src,dst,monomial,sign)."""
import sys

def prefixes(n, sign=1, x=0, y=1, depth=2, off=0, acc=()):
    """Yield, for each leaf in time order, the tuple of complete-phase transvections ending with it."""
    if n == 1:
        yield acc + ((x, y, (off,), sign),)
        return
    mid = n // 2
    ops = [(x, depth, off, mid, 1), (depth, y, off + mid, n - mid, 1),
           (x, depth, off, mid, -1), (depth, y, off + mid, n - mid, -1)]
    if sign == -1:
        ops = [(s, d, o, k, -g) for s, d, o, k, g in reversed(ops)]
    done = acc
    for s, d, o, k, g in ops:
        yield from prefixes(k, g, s, d, depth + 1, o, done)
        done = done + ((s, d, tuple(range(o + k - 1, o - 1, -1)), g),)

def apply(col, ops, inverse=False):
    seq = reversed(ops) if inverse else ops
    for s, d, m, g in seq:
        g = -g if inverse else g
        cs = col.get(s)
        if not cs: continue
        cd = col.setdefault(d, {})
        for mm, c in list(cs.items()):
            k = m + mm; v = cd.get(k, 0) + g * c
            if v: cd[k] = v
            else: del cd[k]
    return col

def countpaths(R, r, ops_inv, ops_fwd):
    N = [0]*R; N[r] = 1
    for s, d, m, g in list(reversed(ops_inv)) + list(ops_fwd):
        if N[s]: N[d] += N[s]
    return N

def strip(pa, pb):
    i = 0
    while i < min(len(pa), len(pb)) and pa[i] == pb[i]: i += 1
    return pa[i:], pb[i:]

if __name__ == '__main__':
    for n in map(int, sys.argv[1:]):
        R = (n - 1).bit_length() + 2
        mass_pk = 0; path_pk = 0; ivs = 0
        for o in (1, -1):
            P = list(prefixes(n, o))
            for a in range(len(P)):
                r = P[a][-1][1]
                for b in range(a, len(P)):
                    ia, fb = strip(P[a], P[b])
                    col = apply({r: {(): 1}}, ia, inverse=True)
                    col = apply(col, fb)
                    ivs += 1
                    m = max(sum(abs(c) for c in v.values()) for v in col.values() if v) if any(col.values()) else 0
                    mass_pk = max(mass_pk, m)
                    path_pk = max(path_pk, max(countpaths(R, r, ia, fb)))
        print(n, 'mass', mass_pk, 'paths_nocancel', path_pk, 'intervals', ivs, flush=True)
