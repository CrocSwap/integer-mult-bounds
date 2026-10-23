# impl A cover search: DFS over flats meeting the most-constrained line, dynamic usefulness filter, memo, greedy probe.
from sa import *
_cache = {}
def prep(O, w, FL, mn=1):
    k = (O, w, mn)
    if k in _cache: return _cache[k]
    ms = sorted({x for x in (m & O for m in FL[w]) if pc(x) >= mn}, key=pc, reverse=True)
    per = {}
    for idx, m in enumerate(ms):
        x = m
        while x:
            b = x & -x; x ^= b
            per.setdefault(b, []).append(idx)
    _cache[k] = (ms, per)
    if len(_cache) > 40: _cache.pop(next(iter(_cache)))
    return _cache[k]
def cover2(O, ws, FL, limit=None):
    ws = tuple(sorted(ws, reverse=True))
    gmax = {w: max(pc(m & O) for m in FL[w]) for w in set(ws)}
    tot0 = sum(gmax[w] for w in ws)
    if tot0 < pc(O): return None
    C = {w: prep(O, w, FL, max(1, pc(O) - (tot0 - gmax[w]))) for w in set(ws)}
    G = {w: (pc(C[w][0][0]) if C[w][0] else 0) for w in C}   # true max restricted size
    seen = set(); cnt = [0]
    def rec(U, rem):
        if U == 0: return []
        if not rem: return None
        key = (U, rem)
        if key in seen: return None
        cnt[0] += 1
        if limit and cnt[0] > limit: raise TimeoutError
        tot = sum(G[w] for w in rem); u = pc(U)
        if tot < u: seen.add(key); return None
        x = U; bl = None; bc = 10**9
        while x:
            b = x & -x; x ^= b
            c = sum(len(C[w][1].get(b, ())) for w in set(rem))
            if c < bc: bc, bl = c, b
        for w in sorted(set(rem), reverse=True):
            r2 = list(rem); r2.remove(w); r2 = tuple(r2)
            need = u - (tot - G[w])
            ms = C[w][0]; tried = set()
            for idx in C[w][1].get(bl, ()):
                m = ms[idx] & U
                if pc(m) < need or m in tried: continue
                tried.add(m)
                res = rec(U & ~m, r2)
                if res is not None: return [(w, ms[idx])] + res
        seen.add(key); return None
    return rec(O, ws)
