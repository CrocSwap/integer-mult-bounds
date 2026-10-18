"""Strict moment descent by single whole-helper transfers after evacuation.

FILLPKG fixes immutable window/dispatch inputs; argv: FILL PROVIDERS OUT.
Apache-2.0. OpenAI Codex assistance. PR2559 fillbase supplies literal checks.
Floating nomination only; original reconstruction and full replay are gates.
"""
import collections
import gzip
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent/'vendor'))
from fillbase import read, windows, dispatch, order, family, compact, check, kappa

pv = read(sys.argv[2]); widths = pv['widths']
paid = {k: {int(r): n for r, n in h.items()} for k, h in pv['paid'].items()}
original = read(sys.argv[1]); rows = [list(x) for x in original['rows']]
win = {tuple(map(int, key.split(','))): (cap, set(times)) for key, (cap, times) in windows.items()}
wid = [widths[dispatch[tuple(order[x[0]])]][x[1]] for x in rows]
members = collections.defaultdict(set); used = collections.Counter(); cf = collections.Counter()
def owner(i): return tuple(rows[i][2:5])
def cap(b): return win[b[:2]][0]
for i in range(len(rows)):
    b = owner(i); members[b].add(i); used[b] += wid[i]; cf[rows[i][0], family(*b)] += 1
holes = collections.defaultdict(set)
for (r, ch), (capacity, _) in win.items():
    for port in range(112):
        b = r, ch, port
        if capacity-used[b]: holes[capacity-used[b]].add(b)
trace = []
for round in range(3):
    count = 0
    jobs = [i for b in sorted(members, key=lambda b: (-cap(b)+used[b], b))
            if 0 < used[b] < cap(b) for i in sorted(members[b])]
    for i in jobs:
        b = owner(i); fs = cap(b)-used[b]; w = wid[i]; t = rows[i][0]
        if not fs: continue
        chosen = None
        # For p=1-a in (0,1), moving w decreases f^p exactly when the
        # destination's remaining hole is smaller than the source's old hole:
        # fd-w < fs, with fd>=w. Total residual rank stays fixed.
        for fd in range(w, min(49, fs+w)):
            for dest in sorted(holes[fd]):
                if dest == b or t not in win[dest[:2]][1]: continue
                df, sf = family(*dest), family(*b)
                if cf[t, df]-int(df == sf): continue
                chosen = dest; break
            if chosen: break
        if chosen is None: continue
        dest = chosen; fd = cap(dest)-used[dest]
        before = fs**0.9982861 + fd**0.9982861
        after = (fs+w)**0.9982861 + (fd-w)**0.9982861
        assert after < before
        holes[fs].discard(b); holes[fd].discard(dest)
        members[b].remove(i); members[dest].add(i)
        used[b] -= w; used[dest] += w
        cf[t, family(*b)] -= 1; cf[t, family(*dest)] += 1
        rows[i][2:5] = dest
        holes[fs+w].add(b)
        if fd-w: holes[fd-w].add(dest)
        trace.append([i, list(b), list(dest), fs, fd, w]); count += 1
    print('CONCENTRATION_ROUND', round, 'moves', count, flush=True)
    if not count: break
rows = compact(rows, lambda r: widths[dispatch[tuple(order[r[0]])]][r[1]])
idle, profile = check(rows, widths, paid)
out = Path(sys.argv[3])
out.write_bytes(gzip.compress(json.dumps(dict(original, rows=rows), separators=(',', ':')).encode(), mtime=0))
out.with_suffix('.profile.json').write_bytes(json.dumps(dict(sorted(profile.items()))).encode())
out.with_suffix('.moves.json').write_bytes(json.dumps(trace, separators=(',', ':')).encode())
print('CONCENTRATED', len(trace), 'idle', dict(sorted(idle.items())), 'endpoint', kappa(profile), flush=True)
