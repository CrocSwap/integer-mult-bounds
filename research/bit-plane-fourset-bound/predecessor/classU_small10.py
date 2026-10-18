"""Class U, r punctured, |S| <= 4: n1 = 10 branch.  Need: no 10-term configuration with savings >= 81 - Theta + 2 g(s-1)."""
import json, itertools, sys, time
from collections import Counter
import tenneed
P = list(range(111, 120))
def g(m): return m - 1 if m >= 2 else (1 if m == 1 else 0)
def theta(s): return 64 + (8 * s) // 9
s = int(sys.argv[1]); stride = int(sys.argv[2]) if len(sys.argv) > 2 else 1
sets = json.load(open('sets_all.json'))
subs = sorted({c for r, S, rk in sets if r >= 111 for c in itertools.combinations(S, s)})[::stride]
need = 81 - theta(s) + 2 * g(s - 1)
t = time.time(); res = Counter()
for c in subs:
    ok = not tenneed.exists_need(P + list(c), need)
    res[ok] += 1
    if not ok: print('OPEN', c, flush=True)
print('s', s, 'need', need, 'sets', len(subs), dict(res), round(time.time() - t), 's', flush=True)
