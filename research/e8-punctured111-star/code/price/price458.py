"""Reprice under a stricter hosting than #442 / #472 / #493 / #503 use: every family copy hosts at most ONE helper per stage.
(PR #458's rule is per invocation = stage x replica; one helper per family copy per STAGE is stricter, so the c below is
a lower bound on the c of any #458-compliant hosting of the same word.)  Whole width-8 residuals only (frame-zero
entrances, ENT = 0).  Pattern = subset S of the window's stages with 8|S| <= rank; same objective as hosting_core.solve
(idle cost saved), same profile / mass identity / moment.certify as pricex.price.
Script written by the independent auditor of this package (star111 audit, 2026-10-11); only its CLI (a word instead of
V R hist cst) and the pricex import path were changed.
usage: price458.py WORD.json.gz s [s ...]"""
import gzip
import itertools
import json
import math
import os
import sys
from collections import Counter

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pricex as px  # noqa: E402

MOM = px.MOM


def cost(r, m): return r * math.log(m / r) if r else 0.0


def price458(V, R, hist, cst, s):
    K, L, M, T, win, idle = px.stage_cfg(s)
    C = 2 * V * T; need = R * T
    var = []
    for i, (p, r, st) in win.items():
        for k in range(0, min(r // 8, len(st)) + 1):
            for S in itertools.combinations(sorted(st), k):
                var.append((i, S))
    n = len(var); c = np.zeros(n)
    for j, (i, S) in enumerate(var):
        r = win[i][1]; c[j] = -(cost(r, M) - cost(r - 8 * len(S), M))
    rows, lo, hi = [], [], []
    for i in win:
        row = np.array([1.0 if vi == i else 0.0 for (vi, S) in var]); rows.append(row); lo.append(C); hi.append(C)
    for st in range(L):
        row = np.array([1.0 if st in S else 0.0 for (vi, S) in var]); rows.append(row); lo.append(need); hi.append(need)
    res = milp(c, constraints=LinearConstraint(np.array(rows), lo, hi), integrality=np.ones(n),
               bounds=Bounds(np.zeros(n), np.full(n, np.inf)), options=dict(time_limit=600, disp=False))
    if res.x is None: return dict(s=s, feasible=False, why=res.message)
    x = [int(round(t)) for t in res.x]
    # Treat the floating solver as a nomination only. Check the complete
    # rounded integer allocation, including every stage demand, exactly.
    assert all(t >= 0 for t in x), 'negative rounded allocation'
    for i in win:
        assert sum(x[j] for j, (vi, _) in enumerate(var) if vi == i) == C, 'stock'
    for st in range(L):
        assert sum(x[j] for j, (_, S) in enumerate(var) if st in S) == need, 'stage demand'
    paid = Counter({r: nn * L * T for r, nn in hist.items() if r})
    for i, r in idle:
        if i not in win: paid[r] += C; continue
        got = Counter()
        for j, (vi, S) in enumerate(var):
            if vi == i and x[j]: got[r - 8 * len(S)] += x[j]
        assert sum(got.values()) == C
        for rem, cnt in got.items():
            if rem: paid[rem] += cnt
    LIVE = 2 * K * V * T
    mass = sum(r * nn for r, nn in paid.items()); gap = M * LIVE - mass - (2 * K * V - L * cst) * T
    assert gap == 0, gap
    cert = MOM.certify(dict(paid), M, LIVE, True)
    return dict(s=s, feasible=True, c=cert['lower'], profile=dict(sorted(paid.items())),
                maxk=max(len(S) for j, (vi, S) in enumerate(var) if x[j]))


if __name__ == '__main__':
    w = json.loads(gzip.open(sys.argv[1], 'rt').read()); d = px.word_hist(w); assert d['ENT'] == 0
    for s in map(int, sys.argv[2:]):
        a = price458(d['V'], d['R'], d['hist'], d['cst'], s); b = px.price(d['V'], d['R'], d['hist'], d['cst'], s)
        print(json.dumps(dict(V=d['V'], R=d['R'], s=s, c458=a.get('c'), feasible458=a['feasible'], c_stock=b.get('c'), maxk=a.get('maxk'))), flush=True)
