"""Generalized (Dylan Crow, with Anthropic Claude assistance): h, m = 5h and the replica count are arguments
(defaults h = 20, m = 100, 60 replicas: the original).  Bridged word B_K (DaysSky, assisted with Claude): the bank
width is m = (2K + 1) h; K = 2 is tile_g.py.  usage: tile_k.py WORDDIR K h replicas
Exact zero-padding width-m bank tiling of the word's entrance residuals (PR #315's bank_template.tile, verbatim logic)."""
import json, sys
from collections import Counter
def tile(blocks, m):
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
    used = Counter()
    for widths, count in out:
        assert sum(widths) == m and count > 0
        for x in widths: used[x] += count
    assert used == Counter(blocks), 'every block used exactly once'
    return tuple(out)
d = sys.argv[1]; K = int(sys.argv[2]); h = int(sys.argv[3]); m = (2*K + 1)*h; replicas = int(sys.argv[4])
s = json.load(open(d + '/249-states.json')); fr = json.load(open(d + '/frames.json'))
dim = {int(k): len(v['B']) for k, v in fr['frames'].items()}; v = s['v']; n = s['n']
res = Counter(h - dim[s['initial'][str(r)]] for r in range(2*v, n))
pat = tile({r: replicas*c for r, c in res.items() if r > 0}, m)
print('residual census', dict(sorted(res.items())), '| freed roles (r = 0) are deleted, not banked')
print('PASS exact width-%d tiling with %d replicas:' % (m, replicas), pat)
