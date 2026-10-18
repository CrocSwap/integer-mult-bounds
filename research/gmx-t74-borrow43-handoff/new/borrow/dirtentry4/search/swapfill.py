"""Same-call swap local search: within one call, exchanging the bins of two roles of different width keeps windows (same time)
and the call's family set; it only moves idle between the two bins. Also equal-time moves of a role into a hole of another bin
(window/family/capacity checked) - evac-style.  Minimise sum_bins g(idle).  argv: FILL_IN PROV FILL_OUT [passes]
Run with FILLPKG=<package>."""
import sys, json, gzip, collections, random, os
sys.path.insert(0, os.path.join(os.environ['FILLPKG'], 'new/borrow-fill/search'))
from fillbase import *
pv = json.load(open(sys.argv[2])); widths = pv['widths']; paid = {k: {int(a): b for a, b in v.items()} for k, v in pv['paid'].items()}
rows = [list(x) for x in read(sys.argv[1])['rows']]
passes = int(sys.argv[4]) if len(sys.argv) > 4 else 6
win = {}
for key, (cap_, times) in windows.items():
    r, ch = map(int, key.split(',')); ts = sorted(times); win[r, ch] = (cap_, ts[0], ts[-1])
wid = [widths[dispatch[tuple(order[x[0]])]][x[1]] for x in rows]
B = lambda i: tuple(rows[i][2:5])
cap = lambda b: win[b[:2]][0]
used = collections.Counter(); bytime = collections.defaultdict(list); members = collections.defaultdict(set)
fam_t = collections.defaultdict(collections.Counter)
for i in range(len(rows)):
    used[B(i)] += wid[i]; bytime[rows[i][0]].append(i); members[B(i)].add(i); fam_t[rows[i][0]][family(*B(i))] += 1
K = 0.0017157; g = lambda f: 0.0 if f <= 0 else f * (73 / f) ** K
allbins = [(r, ch, p) for (r, ch) in win for p in range(112)]
for b in allbins: used[b] += 0
def obj(): return sum(g(cap(b) - used[b]) for b in allbins)
print('start', obj(), flush=True)
rng = random.Random(1)
for ps in range(passes):
    acc = 0
    ts = list(bytime); rng.shuffle(ts)
    for t in ts:
        idx = bytime[t]
        small = [i for i in idx if wid[i] in (7, 8)]; big = [j for j in idx if wid[j] == 9]
        for i in small:
            for j in big:
                bi, bj = B(i), B(j)
                if bi == bj: continue
                d = wid[j] - wid[i]   # moving the bigger role j into bi, i into bj
                if used[bi] + d > cap(bi): continue
                before = g(cap(bi) - used[bi]) + g(cap(bj) - used[bj])
                after = g(cap(bi) - used[bi] - d) + g(cap(bj) - used[bj] + d)
                if after < before - 1e-12:
                    rows[i][2:5], rows[j][2:5] = list(bj), list(bi)
                    used[bi] += d; used[bj] -= d
                    members[bi].discard(i); members[bi].add(j); members[bj].discard(j); members[bj].add(i)
                    acc += 1
    # single moves into holes (same time; window, family, capacity)
    mv = 0
    for i in ([] if os.environ.get('NOMOVE') else rng.sample(range(len(rows)), len(rows))):
        t = rows[i][0]; bi = B(i)
        if used[bi] == wid[i]: pass
        best = None; bestd = 0
        for b in allbins:
            if b == bi: continue
            lo, hi = win[b[:2]][1:]
            if not (lo <= t <= hi) or cap(b) - used[b] < wid[i] or fam_t[t][family(*b)]: continue
            dlt = g(cap(b) - used[b] - wid[i]) + g(cap(bi) - used[bi] + wid[i]) - g(cap(b) - used[b]) - g(cap(bi) - used[bi])
            if dlt < bestd - 1e-12: bestd = dlt; best = b
        if best:
            fam_t[t][family(*bi)] -= 1; fam_t[t][family(*best)] += 1
            used[bi] -= wid[i]; used[best] += wid[i]; members[bi].discard(i); members[best].add(i); rows[i][2:5] = list(best); mv += 1
    print('pass', ps, 'swaps', acc, 'moves', mv, 'obj', obj(), flush=True)
    if not acc and not mv: break
rows = compact(rows, lambda r: widths[dispatch[tuple(order[r[0]])]][r[1]])
idle, Hh = check(rows, widths, paid); print('idle', dict(sorted(idle.items())), 'kappa', kappa(Hh), flush=True)
open(sys.argv[3], 'wb').write(gzip.compress(json.dumps(dict(columns=fill['columns'], dispatch_overrides=fill['dispatch_overrides'], rows=rows), separators=(',', ':')).encode()))
