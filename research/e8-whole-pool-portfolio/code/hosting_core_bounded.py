"""Idle-axis hosting: place whole dirty-helper residuals on the pending coordinates of an idle data family.

A data family that is advanced by an idle child from level a to level b receives the commuting coordinate factors of
that child.  If the family is untouched (no local invocation on its pair and no bridge naming its pair) during an
interval of local invocations ending at the child, a helper residual of width w from an invocation inside that
interval may own w of those pending coordinates instead of a bank slot.  The child keeps only the remaining
coordinates.  This module computes the windows from the recipe and chooses, per replica, how many residuals of each
width each child hosts (exact integer programme), then expands that choice into explicit slot assignments.
Standard library plus scipy for the integer programme; the emitted assignment is re-checked without scipy."""
import math
from collections import Counter, defaultdict

def windows(schedule):
    """schedule: ordered events dict(kind='local',stage,pair) | dict(kind='bridge',dst,src) | dict(kind='idle',pair,rank,idx).
    Returns {idx: (pair, rank, frozenset(stages))} - stages whose invocation lies strictly between the last touch of
    the pair and the idle child."""
    last = {}; out = {}; locals_ = []
    for pos, e in enumerate(schedule):
        k = e['kind']
        if k == 'local':
            locals_.append((pos, e['stage'], e['pair'])); last[e['pair']] = pos
        elif k == 'bridge':
            last[e['dst']] = pos; last[e['src']] = pos
        elif k == 'idle':
            p = e['pair']; lo = last.get(p, -1)
            st = frozenset(s for q, s, pp in locals_ if lo < q < pos and pp != p)
            out[e['idx']] = (p, e['rank'], st)      # an idle child acts on other coordinates (or the other member): not a touch
    return out

def patterns(rank, widths, maxk=12):
    """multisets of widths with sum <= rank (as sorted tuples)"""
    ws = sorted(set(widths), reverse=True); res = []
    def rec(i, cur, s):
        if i == len(ws): res.append(tuple(cur)); return
        w = ws[i]; k = 0
        while s + k * w <= rank and len(cur) + k <= maxk:
            rec(i + 1, cur + [w] * k, s + k * w); k += 1
    rec(0, [], 0)
    return res

def cost(r, m):
    return r * math.log(m / r) if r else 0.0

def solve(win, copies, avail, m, pad_value=0.0, group=None):
    """win: {idx: (pair, rank, stages)}; copies: piece copies per replica of each idx (2V);
    avail: {(stage, width): count per replica}; maximise saved idle cost (+ pad_value per hosted residual).
    group: optional {width: g} - remaining count of that width per stage must be a multiple of g (exact bank tiling).
    Returns {(idx, pattern): copies} and {(idx, width, stage): count}."""
    import numpy as np
    from scipy.optimize import milp, LinearConstraint, Bounds
    widths = sorted({w for (_, w) in avail})
    var = []; index = {}
    for idx, (p, r, st) in win.items():
        for pat in patterns(r, widths):
            index[('y', idx, pat)] = len(var); var.append(('y', idx, pat))
        for w in widths:
            for s in st:
                if avail.get((s, w), 0):
                    index[('z', idx, w, s)] = len(var); var.append(('z', idx, w, s))
    stages = sorted({s for (s, _) in avail})
    if group:
        for w, g in group.items():
            for s in stages:
                index[('g', w, s)] = len(var); var.append(('g', w, s))
    n = len(var); c = np.zeros(n); integ = np.ones(n); lb = np.zeros(n); ub = np.full(n, np.inf)
    for key, j in index.items():
        if key[0] == 'y':
            _, idx, pat = key; r = win[idx][1]; c[j] = -(cost(r, m) - cost(r - sum(pat), m) + pad_value * len(pat))
    rows, lo, hi = [], [], []
    for idx in win:
        row = np.zeros(n)
        for key, j in index.items():
            if key[0] == 'y' and key[1] == idx: row[j] = 1
        rows.append(row); lo.append(copies); hi.append(copies)
        for w in widths:
            row = np.zeros(n)
            for key, j in index.items():
                if key[0] == 'y' and key[1] == idx: row[j] = key[2].count(w)
                if key[0] == 'z' and key[1] == idx and key[2] == w: row[j] = -1
            rows.append(row); lo.append(0); hi.append(0)
    for (s, w), a in avail.items():
        row = np.zeros(n)
        for key, j in index.items():
            if key[0] == 'z' and key[2] == w and key[3] == s: row[j] = 1
        if group and w in group:
            row[index[('g', w, s)]] = group[w]; rows.append(row); lo.append(a); hi.append(a)   # used + g*k = avail
        else:
            rows.append(row); lo.append(0); hi.append(a)
    res = milp(c, constraints=LinearConstraint(np.array(rows), lo, hi), integrality=integ, bounds=Bounds(lb, ub),
               options=dict(time_limit=50, disp=False))
    assert res.x is not None, res.message
    x = [int(round(t)) for t in res.x]
    ys = {(k[1], k[2]): x[j] for k, j in index.items() if k[0] == 'y' and x[j]}
    zs = {(k[1], k[2], k[3]): x[j] for k, j in index.items() if k[0] == 'z' and x[j]}
    return ys, zs, -res.fun

def expand(win, ys, zs, helpers, V2):
    """helpers: {stage: [(helper, width), ...]} for ONE replica; returns list of
    (idx, copy, offset, width, stage, helper) and the remainder rank of every (idx, copy).
    Copies of a piece are the 2V (side, port) data families; residuals packed from offset 0 in decreasing width."""
    pool = defaultdict(list)                    # (stage, width) -> helpers
    for s, hs in helpers.items():
        for h, w in hs: pool[s, w].append(h)
    for k in pool: pool[k].sort()
    need = defaultdict(list)                    # (idx, width) -> stages multiset in deterministic order
    for (idx, w, s), cnt in sorted(zs.items()): need[idx, w] += [s] * cnt
    out = []; rem = {}
    for idx in sorted(win):
        pats = sorted([(pat, cnt) for (i, pat), cnt in ys.items() if i == idx], key=lambda t: (-sum(t[0]), t[0]))
        copy = 0; ptr = Counter()
        r = win[idx][1]
        for pat, cnt in pats:
            for _ in range(cnt):
                off = 0
                for w in sorted(pat, reverse=True):
                    s = need[idx, w][ptr[idx, w]]; ptr[idx, w] += 1
                    h = pool[s, w].pop(0)
                    out.append((idx, copy, off, w, s, h)); off += w
                rem[idx, copy] = r - off; copy += 1
        while copy < V2: rem[idx, copy] = r; copy += 1
    return out, rem

def save_selection(path, key, ys, zs, val):
    """freeze the integer-programme choice (patterns per child, residual stages per child) for stdlib-only replay"""
    import json
    from pathlib import Path
    p = Path(path); d = json.loads(p.read_text()) if p.exists() else {}
    d[key] = dict(patterns=sorted([[i, list(pat), n] for (i, pat), n in ys.items()]),
                  stages=sorted([[i, w, s, n] for (i, w, s), n in zs.items()]), proxy_saving=val)
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + '\n')

def load_selection(path, key):
    import json
    from pathlib import Path
    d = json.loads(Path(path).read_text())[key]
    ys = {(i, tuple(pat)): n for i, pat, n in d['patterns']}
    zs = {(i, w, s): n for i, w, s, n in d['stages']}
    return ys, zs, d['proxy_saving']
