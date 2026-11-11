"""Whole-residual idle-axis hosting with at most ONE helper per physical family per invocation (the rule of PR #458), plus the exact
host chart with explicit spectator coordinates.  Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
A copy (port) of an idle child hosts a PATTERN: residuals of pairwise distinct stages inside the child's window, offsets 0, w1, w1+w2, ...
(a residual is whole: one slot in one family).  The children of one (pair, side) have pairwise disjoint windows (checked), so the
families they share never host two helpers of one invocation, and the integer programme needs only the distinct-stage condition.
Chart: for the host's port q the parent's idle basis is B_q = U_q (+) I (PR #433 geometry; the construction is that of PR #458).  A hosted
residual of width w occupies the pending vectors b_off..b_(off+w-1) of its child; the other e = 9 - w coordinates of the local nine are
SPECTATORS: the first e basis indices of B_q not occupied by the residual, in increasing order.  The paid wrappers (adapters_gk.py) act on
these nine coordinates and restore the spectators identically."""
import math
from collections import Counter

H, M = 9, 73


def cost(r, m): return r * math.log(m / r) if r else 0.0


def patterns(rank, stages, widths):
    out = [()]
    ws = sorted(widths, reverse=True)
    def rec(i, cur, tot):
        for j in range(i, len(stages)):
            for w in ws:
                if tot + w <= rank:
                    c = cur + [(stages[j], w)]; out.append(tuple(c)); rec(j + 1, c, tot + w)
    rec(0, [], 0)
    return out


def solve(win, copies, avail, m, pad_value, time_limit=600):
    """win {idx: (pair, rank, stages)}, avail {(stage, width): helpers per replica}.  Maximise saved idle cost (+ pad_value per hosted residual)."""
    import numpy as np
    from scipy.optimize import milp, LinearConstraint, Bounds
    widths = sorted({w for (_, w) in avail}); var = []
    for idx, (p, r, st) in sorted(win.items()):
        for pat in patterns(r, sorted(st), widths): var.append((idx, pat))
    n = len(var); c = np.zeros(n)
    for j, (idx, pat) in enumerate(var):
        r = win[idx][1]; c[j] = -(cost(r, m) - cost(r - sum(w for _, w in pat), m) + pad_value * len(pat))
    rows, lo, hi = [], [], []
    by = {}
    for j, (idx, pat) in enumerate(var): by.setdefault(idx, []).append(j)
    for idx, js in by.items():
        row = np.zeros(n); row[js] = 1; rows.append(row); lo.append(copies); hi.append(copies)
    for (s, w), a in sorted(avail.items()):
        row = np.zeros(n)
        for j, (idx, pat) in enumerate(var): row[j] = sum(1 for sw in pat if sw == (s, w))
        rows.append(row); lo.append(0); hi.append(a)
    res = milp(c, constraints=LinearConstraint(np.array(rows), lo, hi), integrality=np.ones(n), bounds=Bounds(np.zeros(n), np.full(n, np.inf)),
               options=dict(time_limit=time_limit, disp=False))
    assert res.x is not None, res.message
    x = [int(round(t)) for t in res.x]
    return [[idx, [list(sw) for sw in pat], x[j]] for j, (idx, pat) in enumerate(var) if x[j]], -res.fun


def save(path, key, sel, val):
    import json
    from pathlib import Path
    p = Path(path); d = json.loads(p.read_text()) if p.exists() else {}
    d[key] = dict(rule='one-helper-per-family', patterns=sorted(sel), proxy_saving=val)
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + '\n')


def load(path, key):
    import json
    from pathlib import Path
    d = json.loads(Path(path).read_text())[key]; assert d['rule'] == 'one-helper-per-family'
    return d['patterns'], d['proxy_saving']


def check_disjoint_groups(win, pair_of, side_of):
    """children of one (pair, side) share their physical families; their windows must be disjoint"""
    seen = {}
    for idx, (p, r, st) in win.items():
        for s in st:
            k = (pair_of[idx], side_of[idx], s); assert k not in seen, ('windows of two children of one family group overlap', idx, seen[k], k); seen[k] = idx


def expand(win, sel, widths, V):
    """-> slots [idx, port, off, w, s, h] (one replica), rem {(idx, port): remaining pending rank}"""
    R = len(widths); pool = {}
    for h in sorted(range(R)): pool.setdefault(widths[h], []).append(h)
    pool = {(s, w): list(hs) for s in range(9) for w, hs in pool.items()}
    slots = []; rem = {}; used = Counter()
    for idx, pat, copies in sorted(sel, key=lambda e: (e[0], e[1])):
        r = win[idx][1]
        for _ in range(copies):
            cp = used[idx]; used[idx] += 1; assert cp < V; off = 0
            assert len({s for s, w in pat}) == len(pat)
            for s, w in pat:
                assert s in win[idx][2] and off + w <= r
                slots.append([idx, cp, off, w, s, pool[s, w].pop(0)]); off += w
            rem[idx, cp] = r - off
    assert all(n == V for n in used.values()) and len(used) == len(win)
    return slots, rem


def idle_basis(q):
    """PR #433 / #458: the parent's orthonormal idle basis U_q (+) I for port q (H = 9 local coordinates, M = 73)"""
    z = next(i for i in range(H) if not (q >> i & 1)); a = q ^ (1 << z); order = list(range(H)); order[0], order[z] = order[z], order[0]
    return [(1 << i) ^ (a if a >> i & 1 else 0) for i in order] + [1 << i for i in range(H, M)]


def spectators(q, pending, off, w):
    """indices (into B_q) of the e = 9 - w spectator coordinates of a residual at pending[off:off+w]"""
    B = idle_basis(q); occ = [B.index(x) for x in pending[off:off + w]]
    assert len(set(occ)) == w
    sp = [j for j in range(M) if j not in occ][:H - w]
    assert len(sp) == H - w
    return sp
