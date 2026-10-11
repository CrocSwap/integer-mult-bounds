"""Residual census (endpoint - sigma per helper; freed roles r = 0 are deleted, not banked) and an exact zero-padding
width-100 bank tiling with explicitly selected replicas (tile(): the filler search of our PR #329 bank_template.py, verbatim).
usage: tile.py WORD REPLICAS"""
import sys,json,collections
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
    assert out is not None, ('no exact zero-padding tiling', blocks, m)
    assert all(sum(widths) == m and count > 0 for widths, count in out)
    used = Counter()
    for widths, count in out:
        for x in widths: used[x] += count
    assert used == Counter(blocks), 'every block used exactly once'
    return tuple(out)
d=sys.argv[1];replicas=int(sys.argv[2]);assert replicas>0;st=json.load(open(d+'/249-states.json'));fr=json.load(open(d+'/frames.json'))['frames'];dim={int(k):len(x['B']) for k,x in fr.items()}
v,n=st['v'],st['n'];res=collections.Counter(dim[st['final'][str(r)]]-dim[st['initial'][str(r)]] for r in range(2*v,n))
print('residual census',dict(sorted(res.items())),'sum',sum(k*c for k,c in res.items()))
pat=tile({r:replicas*c for r,c in res.items() if r>0},100);print('PASS exact width-100 tiling,',replicas,'replicas:',pat)
