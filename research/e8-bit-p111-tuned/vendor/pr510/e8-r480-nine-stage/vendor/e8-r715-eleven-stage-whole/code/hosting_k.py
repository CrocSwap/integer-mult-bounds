"""Idle-axis hosting integer programme with two optional extensions; the windows/expand/selection helpers are
imported unchanged from DaysSky's PR #442 (research/idle-axis-hosting/hosting_core.py).

solve() is PR #442's HC.solve with
  * host_all:      every helper residual of every stage must be hosted (no bank is left; used when the compressed
                   window m is not tileable by the residual widths, e.g. m = 78);
  * max_remainder: every idle child must keep at most this many coordinates (halving-depth control).
With both options off it is the same programme as HC.solve (same variables, rows and objective), so --discover at
the nine-stage defaults reproduces the frozen PR #442/#444 selections.
Generalised by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '../../idle-axis-hosting'))
import hosting_core as HC
windows, patterns, cost, expand, save_selection, load_selection = HC.windows, HC.patterns, HC.cost, HC.expand, HC.save_selection, HC.load_selection

def solve(win, copies, avail, m, pad_value=0.0, group=None, host_all=False, max_remainder=None, maxk=12, time_limit=600):
    import numpy as np
    from scipy.optimize import milp, LinearConstraint, Bounds
    widths = sorted({w for (_, w) in avail})
    var = []; index = {}
    for idx, (p, r, st) in win.items():
        for pat in patterns(r, widths, maxk):
            if max_remainder is not None and r - sum(pat) > max_remainder: continue
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
        elif host_all:
            rows.append(row); lo.append(a); hi.append(a)
        else:
            rows.append(row); lo.append(0); hi.append(a)
    res = milp(c, constraints=LinearConstraint(np.array(rows), lo, hi), integrality=integ, bounds=Bounds(lb, ub),
               options=dict(time_limit=time_limit, disp=False))
    assert res.x is not None, res.message
    assert res.status == 0, ('integer programme not solved to optimality', res.status, res.message)
    x = [int(round(t)) for t in res.x]
    ys = {(k[1], k[2]): x[j] for k, j in index.items() if k[0] == 'y' and x[j]}
    zs = {(k[1], k[2], k[3]): x[j] for k, j in index.items() if k[0] == 'z' and x[j]}
    return ys, zs, -res.fun
