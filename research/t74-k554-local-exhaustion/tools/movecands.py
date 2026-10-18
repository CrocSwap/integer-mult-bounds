"""Commutation-window move positions for every B read with a negative deletion relaxation. usage: movecands.py RELAX-B.json OUT.json"""
import json, gzip, sys
import _paths
w = json.load(gzip.open(_paths.BASE)); B = w['B']
res = {int(k): v for k, v in json.load(open(sys.argv[1])).items()}
regs = lambda e: e[1:3] if e[0] == 'add' else e[1:2]
def window(i):
    g = B[i]; t, s = g[1], g[2]
    def blocks(e):
        if e[0] == 'scale': return e[1] in (t, s)
        return e[1] == s or e[2] == t
    lo = i
    while lo - 1 >= 0 and not blocks(B[lo - 1]): lo -= 1
    hi = i
    while hi + 1 < len(B) and not blocks(B[hi + 1]): hi += 1
    return lo, hi
jobs = []
for i, v in res.items():
    if v.get('delta', 0) >= 0 or B[i][0] != 'add': continue
    lo, hi = window(i); t, s = B[i][1], B[i][2]
    pos = {lo, hi + 1}
    for j in range(lo, hi + 1):
        if j != i and (t in regs(B[j]) or s in regs(B[j])): pos.add(j); pos.add(j + 1)
    pos.discard(i); pos.discard(i + 1)
    if pos: jobs.append((v['delta'], i, lo, hi, sorted(pos)))
jobs.sort()
print(len(jobs), sum(len(j[4]) for j in jobs))
import collections
print(collections.Counter(len(j[4]) for j in jobs).most_common(10))
json.dump(jobs, open(sys.argv[2], 'w'))
for j in jobs[:10]: print(j[0], j[1], B[j[1]][:5], j[2], j[3], j[4][:10])
