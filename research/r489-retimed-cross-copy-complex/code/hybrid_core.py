"""Hybrid idle-axis hosting on PR #433/#442's compressed nine-stage complex template (m = 73, eight replicas).

Two kinds of host copies (a copy = one data family of an idle child, i.e. one port of one side of one idle pair):
* PATTERN copies (rule of PR #458 / #495): whole residuals of pairwise distinct stages of the child's window, packed from
  offset 0.  Each residual on a pattern copy is the only helper on that physical family in its invocation.  Entering
  residuals (width w < 9, PR #495's paid two-sided residual adapters) are hosted on pattern copies only.
* TAPE copies (rule of PR #442 / #448): the remaining copies of the child are concatenated into one tape on which width-9
  residuals are laid contiguously; a residual may straddle two consecutive copies (PR #448's cross-copy slot).

Every residual is hosted (equality rows), so there are no helper banks.  Objective: the saved idle cost, exact on pattern
copies and the first-order r ln(m/r) proxy on the tape (as #448).  The solve (scipy/HiGHS) is used only to discover the
frozen selection; expand() is deterministic standard library code."""
import math
from collections import Counter, defaultdict

def cost(r, m): return r * math.log(m / r) if r else 0.0

def patterns(rank, stages, widths):
    out = []; ws = sorted(widths, reverse=True)
    def rec(i, cur, tot):
        for j in range(i, len(stages)):
            for w in ws:
                if tot + w <= rank:
                    c = cur + [(stages[j], w)]; out.append(tuple(c)); rec(j + 1, c, tot + w)
    rec(0, [], 0)
    return out

def solve(win, copies, avail, m, time_limit=1800):
    """win {idx: (pair, rank, stages)}; avail {(stage, width): helpers per replica}.  All residuals hosted.
    Returns (pattern selection [[idx, [[stage, width], ...], count]], tape selection [[idx, stage, count]], objective)."""
    import numpy as np
    from scipy.optimize import milp, LinearConstraint, Bounds
    from scipy.sparse import lil_matrix
    widths = sorted({w for (_, w) in avail}); var = []
    for idx, (p, r, st) in sorted(win.items()):
        for pat in patterns(r, sorted(st), widths): var.append(('p', idx, pat))
        if 9 in widths:
            for s in sorted(st): var.append(('t', idx, s))
    n = len(var); c = np.zeros(n)
    for j, v in enumerate(var):
        r = win[v[1]][1]
        c[j] = -(cost(r, m) - cost(r - sum(w for _, w in v[2]), m)) if v[0] == 'p' else -9 * math.log(m / r)
    A = lil_matrix((len(win) + len(avail), n)); lo = []; hi = []; k = 0
    byidx = defaultdict(list)
    for j, v in enumerate(var): byidx[v[1]].append(j)
    for idx in sorted(win):                    # r * (pattern copies) + 9 * (tape residuals) <= r * copies
        r = win[idx][1]
        for j in byidx[idx]: A[k, j] = r if var[j][0] == 'p' else 9
        lo.append(0); hi.append(r * copies); k += 1
    for (s, w) in sorted(avail):               # every residual hosted exactly once
        for j, v in enumerate(var):
            if v[0] == 'p':
                z = sum(1 for sw in v[2] if sw == (s, w))
                if z: A[k, j] = z
            elif w == 9 and v[2] == s: A[k, j] = 1
        lo.append(avail[s, w]); hi.append(avail[s, w]); k += 1
    res = milp(c, constraints=LinearConstraint(A.tocsr(), lo, hi), integrality=np.ones(n), bounds=Bounds(np.zeros(n), np.full(n, np.inf)),
               options=dict(time_limit=time_limit, disp=False))
    assert res.x is not None and res.status == 0, res.message
    x = [int(round(t)) for t in res.x]
    psel = sorted([[v[1], [list(sw) for sw in v[2]], x[j]] for j, v in enumerate(var) if v[0] == 'p' and x[j]])
    tsel = sorted([[v[1], v[2], x[j]] for j, v in enumerate(var) if v[0] == 't' and x[j]])
    return psel, tsel, -res.fun

def expand(win, psel, tsel, widths, stages, V):
    """Deterministic layout for one replica.  Pattern copies are the first ports of a child, in sorted selection order;
    the tape uses the following ports.  Helpers of each (stage, width) are taken in increasing index order, patterns first.
    Returns slots {(stage, helper): (idx, kind, [(copy, offset, width), ...])} and rem {(idx, copy): remaining rank}."""
    pool = {(s, w): [h for h in range(len(widths)) if widths[h] == w] for s in range(stages) for w in set(widths)}
    slots = {}; rem = {}; used = Counter()
    for idx, pat, cnt in sorted(psel, key=lambda e: (e[0], e[1])):
        r = win[idx][1]; assert len({s for s, w in pat}) == len(pat)
        for _ in range(cnt):
            cp = used[idx]; used[idx] += 1; assert cp < V; off = 0
            for s, w in pat:
                assert s in win[idx][2] and off + w <= r
                h = pool[s, w].pop(0); slots[s, h] = (idx, 'pattern', [(cp, off, w)]); off += w
            rem[idx, cp] = r - off
    for idx in sorted(win):
        r = win[idx][1]; first = used[idx]; pos = first * r
        for i2, s, cnt in sorted(tsel):
            if i2 != idx: continue
            for _ in range(cnt):
                h = pool[s, 9].pop(0); a, b = pos, pos + 9; segs = []
                while a < b:
                    cp = a // r; end = min(b, (cp + 1) * r); segs.append((cp, a - cp * r, end - a)); a = end
                assert segs[-1][0] < V and len(segs) <= 2
                slots[s, h] = (idx, 'tape', segs); pos = b
        for cp in range(first, V): rem[idx, cp] = r - max(0, min(r, pos - cp * r))
    assert all(not hs for hs in pool.values()), 'every residual must be hosted'
    return slots, rem
