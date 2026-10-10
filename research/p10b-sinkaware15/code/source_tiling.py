"""Exact tiling and economy fallback extracted without algorithm changes from PR320.
Source bank_template.py retained in frozen PR322 predecessor; source SHA256 1c124900095abfd0c06cba507c2ed804f5475bea1b3f698ef66d412417ad4264.
Original p10 port by DreamingOfClouds with Anthropic Claude assistance; economy fallback by Chafik Boukhalfa with Anthropic Claude assistance.
Extraction and downstream integration prepared with OpenAI Codex assistance; Apache-2.0.
"""
from collections import Counter

def tile(blocks, m):
    """Exact tiling of {width: number of blocks} into banks of total width m, as ((widths, banks), ...).

    A width dividing m fills pure banks. A width w not dividing m is mixed with a filler width f dividing m:
    banks w^a f^b with a maximal (w*a + f*b = m), then at most one bank w^r f^t for the remainder r. Fillers
    are tried in a fixed order (most blocks first) with backtracking until every pure width also divides out.
    Fails (AssertionError) unless every block is used and every bank is full; there is no padding."""
    blocks = {w: n for w, n in blocks.items() if n}
    assert all(0 < w <= m for w in blocks)
    mixed = sorted(x for x in blocks if m % x)

    def search(i, left, out):
        if i == len(mixed):
            if any(left[w] % (m // w) for w in left): return None
            return out + [(tuple([w]*(m // w)), left[w]//(m // w)) for w in sorted(left) if left[w]]
        w = mixed[i]; n = blocks[w]
        for f in sorted(left, key=lambda x: (-left[x], x)):
            a = next((a for a in range(m // w, 0, -1) if (m - w*a) % f == 0), None)
            if a is None: continue
            b = (m - w*a)//f; q, r = divmod(n, a)
            if r and (m - w*r) % f: continue
            t = (m - w*r)//f if r else 0
            if q*b + t > left[f]: continue
            rest = dict(left); rest[f] -= q*b + t
            found = search(i + 1, rest, out + ([(tuple([w]*a + [f]*b), q)] if q else []) + ([(tuple([w]*r + [f]*t), 1)] if r else []))
            if found is not None: return found
        return None
    out = search(0, {w: n for w, n in blocks.items() if not m % w}, [])
    if out is None: out = economy_tile(blocks, m)
    assert all(sum(widths) == m and count > 0 for widths, count in out)
    used = Counter()
    for widths, count in out:
        for x in widths: used[x] += count
    assert used == Counter(blocks), 'every block used exactly once'
    return tuple(out)


def economy_tile(blocks, m):
    """Exact zero-padding tiling used when the filler search of tile() runs out of filler blocks (the kernel pivots
    and early restorations of the stage stack add many residual widths that do not divide m; the PR #299 analogue at
    p = 12 was the (r^4, 24, 4^(24-r)) re-tiling). The fillers are the two most numerous widths dividing m (here the
    full helper width h and the rank-4 entrance residual). Each other width w, in decreasing order, gets the bank
    w^a F^c f^b (w*a + F*c + f*b = m) that spends the fewest narrow fillers f per w block (then the largest a), plus
    at most one bank w^r F^c' f^b' for the remainder r = n mod a. The leftover fillers fill pure banks F^(m/F),
    f^(m/f) and y residue banks F^j f^k. Every bank sums to m and every block is used exactly once (no padding)."""
    from fractions import Fraction
    blocks = {w: n for w, n in blocks.items() if n}
    div = sorted((w for w in blocks if m % w == 0), key=lambda w: (-blocks[w], w))
    assert len(div) >= 2, ('economy tiling needs two filler widths', blocks)
    F, f = sorted(div[:2], reverse=True)

    def fill(rest):
        """(c, b) with F*c + f*b = rest, c maximal (fewest narrow fillers); None if impossible."""
        return next(((c, (rest - F*c)//f) for c in range(rest//F, -1, -1) if (rest - F*c) % f == 0), None)

    left = {F: blocks[F], f: blocks[f]}; out = []
    for w in sorted((x for x in blocks if x not in (F, f)), reverse=True):
        n = blocks[w]
        opts = [(Fraction(cb[1], a), -a, a, cb) for a in range(m//w, 0, -1) for cb in [fill(m - w*a)] if cb]
        assert opts, ('no bank for width', w)
        _, _, a, (c, b) = min(opts); q, r = divmod(n, a)
        if q: out.append(((w,)*a + (F,)*c + (f,)*b, q)); left[F] -= q*c; left[f] -= q*b
        if r:
            cb = fill(m - w*r); assert cb, ('no remainder bank', w, r)
            out.append(((w,)*r + (F,)*cb[0] + (f,)*cb[1], 1)); left[F] -= cb[0]; left[f] -= cb[1]
    assert left[F] >= 0 and left[f] >= 0, ('fillers exhausted', left)
    pF, pf = m//F, m//f
    for y in range((pF*pf) + 1):
        for j in range(1 if y else 0, pF if y else 1):
            if (m - F*j) % f: continue
            k = (m - F*j)//f; aF, af = left[F] - y*j, left[f] - y*k
            if aF >= 0 and af >= 0 and aF % pF == 0 and af % pf == 0:
                out += ([((F,)*j + (f,)*k, y)] if y else []) + ([((F,)*pF, aF//pF)] if aF else []) + ([((f,)*pf, af//pf)] if af else [])
                return out
    raise AssertionError(('no exact zero-padding tiling', blocks, m))


