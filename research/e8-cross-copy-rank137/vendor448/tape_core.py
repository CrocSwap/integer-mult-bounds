"""Cross-copy idle-axis hosting.  A child advancing pair j by rank r has, per replica, C copies (data families) with r
pending coordinates each; they share one window.  Concatenate the C pending sets into a tape of C*r coordinates and
place whole residuals (stage in window, width w) contiguously; a residual may straddle a copy boundary, in which case
its two pieces are owned by two families of the same child.  Integer programme: maximise saved idle cost (first-order
r ln(m/r) proxy) subject to residual availability and exact bank tiling of what is left.  Standard library plus scipy
for the solve; a frozen selection replays without scipy."""
import math, json
from collections import Counter, defaultdict
from pathlib import Path

def windows(schedule):
    last = {}; out = {}; locals_ = []
    for pos, e in enumerate(schedule):
        k = e['kind']
        if k == 'local': locals_.append((pos, e['stage'], e['pair'])); last[e['pair']] = pos
        elif k == 'bridge': last[e['dst']] = pos; last[e['src']] = pos
        elif k == 'idle':
            p = e['pair']; lo = last.get(p, -1)
            out[e['idx']] = (p, e['rank'], frozenset(s for q, s, pp in locals_ if lo < q < pos and pp != p))
    return out

def cost(r, m): return r * math.log(m / r) if r else 0.0

def solve(win, copies, avail, m, widths, tiling):
    """win: {idx: (pair, rank, stages)}; copies per child per replica; avail: {(stage, width): count per replica};
    tiling: function(leftover counts per stage as dict width->var expressions) -> list of (row, lo, hi) built by caller.
    Returns counts {(idx, stage, width): n} maximising sum_i ln(m/r_i) * used_i  (used_i = coordinates hosted on child i)."""
    import numpy as np
    from scipy.optimize import milp, LinearConstraint, Bounds
    var = []; index = {}
    for idx, (p, r, st) in win.items():
        for s in sorted(st):
            for w in widths:
                if avail.get((s, w), 0): index[(idx, s, w)] = len(var); var.append(('n', idx, s, w))
    stages = sorted({s for (s, _) in avail})
    extra = tiling['vars'](stages)                     # list of names of integer slack vars
    for name in extra: index[name] = len(var); var.append(name)
    n = len(var); c = np.zeros(n); lb = np.zeros(n); ub = np.full(n, np.inf)
    for key in list(index):
        if isinstance(key, tuple) and len(key) == 3 and key[0] in win:
            idx, s, w = key; r = win[idx][1]; c[index[key]] = -math.log(m / r) * w
    rows, lo, hi = [], [], []
    for idx, (p, r, st) in win.items():                # capacity of the tape
        row = np.zeros(n)
        for key, j in index.items():
            if isinstance(key, tuple) and len(key) == 3 and key[0] == idx: row[j] = key[2]
        rows.append(row); lo.append(0); hi.append(copies * r)
    for (s, w), a in avail.items():                    # availability and tiling of the leftover
        row = np.zeros(n)
        for key, j in index.items():
            if isinstance(key, tuple) and len(key) == 3 and key[0] in win and key[1] == s and key[2] == w: row[j] = 1
        rows.append(row); lo.append(0); hi.append(a)
    for row, l, h in tiling['rows'](index, n, avail, win):
        rows.append(row); lo.append(l); hi.append(h)
    res = milp(c, constraints=LinearConstraint(np.array(rows), lo, hi), integrality=np.ones(n), bounds=Bounds(lb, ub),
               options=dict(time_limit=600, disp=False))
    assert res.x is not None, res.message
    x = [int(round(t)) for t in res.x]
    counts = {key: x[j] for key, j in index.items() if isinstance(key, tuple) and len(key) == 3 and key[0] in win and x[j]}
    return counts, -res.fun

def expand(win, counts, helpers, copies):
    """helpers: {stage: [(helper, width), ...]} for one replica (sorted).  Lay the residuals of each child along the tape
    in (stage, helper) order.  Returns pieces {(stage, helper): (idx, [(copy, off, w), ...])} and the remainder rank of
    every (idx, copy)."""
    pool = defaultdict(list)
    for s, hs in helpers.items():
        for h, w in hs: pool[s, w].append(h)
    for k in pool: pool[k].sort()
    pieces = {}; rem = {}
    for idx in sorted(win):
        p, r, st = win[idx]; pos = 0
        items = []
        for (i2, s, w), cnt in sorted(counts.items()):
            if i2 != idx: continue
            for _ in range(cnt): items.append((s, w, pool[s, w].pop(0)))
        items.sort(key=lambda t: (-t[1], t[0], t[2]))      # wide first: fewer straddles
        for s, w, h in items:
            a, b = pos, pos + w; segs = []
            while a < b:
                cp = a // r; end = min(b, (cp + 1) * r); segs.append((cp, a - cp * r, end - a)); a = end
            pieces[s, h] = (idx, segs); pos = b
        assert pos <= copies * r
        for cp in range(copies):
            used = max(0, min(r, pos - cp * r)); rem[idx, cp] = r - used
    return pieces, rem

def save(path, key, counts, val):
    p = Path(path); d = json.loads(p.read_text()) if p.exists() else {}
    d[key] = dict(counts=sorted([[i, s, w, n] for (i, s, w), n in counts.items()]), proxy_saving=val)
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + '\n')

def load(path, key):
    d = json.loads(Path(path).read_text())[key]
    return {(i, s, w): n for i, s, w, n in d['counts']}, d['proxy_saving']
