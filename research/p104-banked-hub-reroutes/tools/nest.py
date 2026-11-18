"""GF(2) chart nesting: rank of transfer a->b = |dim b - dim a| only when spans are nested (else None)."""
def _basis(vs):
    B = []
    for v in vs:
        for b in B: v = min(v, v ^ b)
        if v: B.append(v)
    return B
def _in(v, B):
    for b in sorted(B, reverse=True): v = min(v, v ^ b)
    return v == 0
_cache = {}
def span(fr, c):
    if c not in _cache:
        B = []
        for v in fr[c]:
            for b in B:
                if v ^ b < v: v ^= b
            if v: B.append(v); B.sort(reverse=True)
        _cache[c] = B
    return _cache[c]
def red(v, B):
    for b in B:
        if v ^ b < v: v ^= b
    return v
def nested(fr, a, b):
    A, Bb = span(fr, a), span(fr, b)
    small, big = (A, Bb) if len(A) <= len(Bb) else (Bb, A)
    return all(red(v, big) == 0 for v in small)
def trank(fr, a, b):
    return abs(len(fr[b]) - len(fr[a])) if nested(fr, a, b) else None
