"""Whole-residual idle-axis hosting under PR #471's footprint rule (Dugongue): several helpers of one invocation may share a host
family when their complete nine-coordinate footprints (residual cells plus explicit spectators) are pairwise disjoint.
Capacity of one copy of an idle child of rank r: sum of widths <= r, 9 * (helpers) <= 73, spectators sum(9 - w) <= 73 - r.
Residuals are whole (one slot in one family); spectators are explicit B_q indices outside every residual cell of the copy and
distinct within one invocation.  Adapted from DreamingOfClouds' onehost_gk.py (PR #484) by Rohan Arun with Claude Opus 5.5
(Anthropic).  Apache-2.0."""
from collections import Counter, defaultdict
H, M = 9, 73


def capacity_ok(rank, pat):
    ws = [w for s, w in pat]
    return sum(ws) <= rank and H * len(ws) <= M and sum(H - w for w in ws) <= M - rank


def save(path, key, sel, val):
    import json
    from pathlib import Path
    p = Path(path); d = json.loads(p.read_text()) if p.exists() else {}
    d[key] = dict(rule='footprint', patterns=sorted(sel), proxy_saving=val)
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + '\n')


def load(path, key):
    import json
    from pathlib import Path
    d = json.loads(Path(path).read_text())[key]; assert d['rule'] == 'footprint'
    return d['patterns'], d['proxy_saving']


def expand(win, sel, widths, V, banked):
    """-> slots [idx, port, off, w, s, h] (one replica), rem {(idx, port): remaining pending rank}.
    banked {(s, w): count} residuals per replica left to banks."""
    R = len(widths); pool = defaultdict(list)
    for h in range(R): pool[widths[h]].append(h)
    pool = {(s, w): list(hs) for s in range(9) for w, hs in pool.items()}
    slots = []; rem = {}; used = Counter()
    for idx, pat, copies in sorted(sel, key=lambda e: (e[0], e[1])):
        r = win[idx][1]
        assert capacity_ok(r, pat), ('copy capacity', idx, pat)
        for _ in range(copies):
            cp = used[idx]; used[idx] += 1; assert cp < V; off = 0
            for s, w in pat:
                assert s in win[idx][2] and off + w <= r
                slots.append([idx, cp, off, w, s, pool[s, w].pop(0)]); off += w
            rem[idx, cp] = r - off
    assert all(n == V for n in used.values()) and len(used) == len(win)
    left = Counter((s, w) for (s, w), hs in pool.items() for _ in hs)
    assert {k: n for k, n in left.items() if n} == {k: n for k, n in banked.items() if n}, ('banked residuals', dict(left))
    return slots, rem


def chart(B, pend, copy_slots):
    """copy_slots: [(off, w, s)] of one copy; -> spectator index lists (into B) per slot.
    Spectators avoid every residual cell of the copy and the spectators of other same-stage helpers on the family."""
    cells = set()
    for off, w, s in copy_slots: cells |= {B.index(x) for x in pend[off:off + w]}
    taken = defaultdict(set); out = []
    for off, w, s in copy_slots:
        sp = [j for j in range(M) if j not in cells and j not in taken[s]][:H - w]
        assert len(sp) == H - w; taken[s] |= set(sp); out.append(sp)
    return out
