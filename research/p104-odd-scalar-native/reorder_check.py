#!/usr/bin/env python3
"""The reordering of commuting events and the final rewrite (standard library).  python3 -I -B reorder_check.py
Compares data/stage_before_stops.json.gz (A) with data/stage_stops_untuned.json.gz (B) and data/word.json.gz (C).
A -> B: events are matched by content, k-th occurrence to k-th occurrence.  For every register, every pair of matched events that share it with at least one writer (MOVE, INIT, CLEAR, SCALE or ADD destination write;
ADD source read; write-write counted as a conflict, stricter than needed) must keep its order; events on disjoint registers commute.  The unmatched events (rewritten by the retiming) are listed and are covered by the exact replay only.
data/stop_groups.json lists 20 groups (P, F, N) with two registers a, b: in A both follow the nested chain P < F < N; in B both rest at P and at N together and a skips F, so a's two single-rank MOVEs P -> F -> N
are replaced by one MOVE P -> N.  B -> C: only same-frame runs of ADD and SCALE events are rewritten; the other events and the frame of every maximal run are identical.
A control: swapping one MOVE of a register with a neighbouring ADD that touches it must be reported as a conflict.  Ends PASS_REORDER."""
import gzip, json, sys, os, bisect
from collections import defaultdict, Counter
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); d = lambda n: os.path.join(HERE, 'data', n)
L = lambda n: json.load(gzip.open(d(n), 'rt'))
A, B, C = L('stage_before_stops.json.gz'), L('stage_stops_untuned.json.gz'), L('word.json.gz'); groups = json.load(open(d('stop_groups.json')))
def need(ok, msg):
    if not ok: raise SystemExit('FAIL ' + msg)
    print('PASS', msg, flush=True)
PA, PB = A['program'], B['program']
def match(PA, PB):
    occ = defaultdict(list)
    for i, e in enumerate(PB): occ[json.dumps(e)].append(i)
    cnt = Counter(); m = {}
    for i, e in enumerate(PA):
        k = json.dumps(e); c = cnt[k]; cnt[k] += 1
        if c < len(occ[k]): m[i] = occ[k][c]
    return m
def rw(e): return ({e[2]}, {e[1]}) if e[0] in ('ADD', 'COPY') else (set(), {e[1]})
def conflicts(PA, m):
    reg = defaultdict(list)
    for i, j in m.items():
        R, Wr = rw(PA[i])
        for r in R: reg[r].append((i, j, 0))
        for r in Wr: reg[r].append((i, j, 1))
    bad = 0
    for r, Lr in reg.items():
        Lr.sort(); b = [x[1] for x in Lr]; m_ = len(b)
        pre = [0] * m_; cur = -1
        for k in range(m_): pre[k] = cur; cur = max(cur, b[k])
        suf = [0] * m_; cur = 1 << 60
        for k in range(m_ - 1, -1, -1): suf[k] = cur; cur = min(cur, b[k])
        for k in range(m_):
            if Lr[k][2] and not (pre[k] < b[k] < suf[k]): bad += 1
    return bad
mAB = match(PA, PB)
need(len(PA) < len(PB) and len(C['program']) < len(PB), 'stage words: %d events before, %d after the stops, %d in the final word' % (len(PA), len(PB), len(C['program'])))
bad = conflicts(PA, mAB)
need(bad == 0, 'A -> B: %d of %d events matched by content; writers whose order against some other event on a shared register changed: %d (no conflicting pair reordered)' % (len(mAB), len(PA), bad))
ctrl = list(PB); k = next(i for i in range(len(ctrl) - 1) if ctrl[i][0] == 'MOVE' and ctrl[i + 1][0] == 'ADD' and ctrl[i + 1][1] == ctrl[i][1])
ctrl[k], ctrl[k + 1] = ctrl[k + 1], ctrl[k]
need(conflicts(PA, match(PA, ctrl)) > 0, 'control: swapping a MOVE with the next ADD into the same register (event %d of the stop word) is reported as a conflict' % k)
unA = len(PA) - len(mAB); unB = len(PB) - len(mAB)
print('  unmatched (rewritten) events: %d of A, %d new in B; covered by the exact replay of the final word only' % (unA, unB))
ja = [mAB[i] for i in sorted(mAB)]; tails = []; idx = []; prev = [-1] * len(ja)
for t, x in enumerate(ja):
    p = bisect.bisect_left(tails, x)
    if p == len(tails): tails.append(x); idx.append(t)
    else: tails[p] = x; idx[p] = t
    prev[t] = idx[p - 1] if p > 0 else -1
print('  matched events that moved relative to the rest (least number): %d' % (len(ja) - len(tails)))
def frames_of(W, r):
    cur = W['initial'][r]; out = [cur]
    for e in W['program']:
        if e[0] == 'MOVE' and e[1] == r: cur = e[3]; out.append(cur)
    return out
def span(b):
    s = {0}
    for v in b: s |= {x ^ v for x in s}
    return frozenset(s)
sp = [span(b) for b in A['frames']]; ok = 0
for (P_, F_, N_), a, b, _ in groups:
    fa, fb, ga, gb = frames_of(A, a), frames_of(A, b), frames_of(B, a), frames_of(B, b)
    ok += sp[P_] < sp[F_] < sp[N_] and all(x in fa and x in fb for x in (P_, F_, N_)) and F_ not in ga and F_ in gb and P_ in ga and N_ in ga and P_ in gb and N_ in gb
need(len(groups) == 20 and ok == 20, '20 groups: in the word before the stops both registers follow a nested chain P < F < N; after it both rest at P and at N and one of them skips F')
mv = lambda W: Counter(json.dumps(e) for e in W['program'] if e[0] == 'MOVE')
rem, add = sum((mv(A) - mv(B)).values()), sum((mv(B) - mv(A)).values())
need((rem, add) == (40, 20) and mv(B) == mv(C), 'MOVEs: %d removed and %d added by the 20 stops (%d to %d); the final word has the same MOVE multiset as the stop word' % (rem, add, sum(mv(A).values()), sum(mv(B).values())))
ic = lambda W: [e for e in W['program'] if e[0] in ('INIT', 'CLEAR')]
def peak(W):
    o = set(); p_ = 0
    for e in W['program']:
        if e[0] == 'INIT': o.add(e[1]); p_ = max(p_, len(o))
        elif e[0] == 'CLEAR': o.discard(e[1])
    return p_
need(ic(A) == ic(B) == ic(C) and peak(A) == peak(B) == peak(C) == 36 and A['frames'] == C['frames'] and A['initial'] == C['initial'] and A['final'] == C['final'], 'owned INIT and CLEAR subsequence (%d events), peak %d, initial, final and frame lists are identical in the three words' % (len(ic(A)), peak(C)))
def skel(W):
    out = []
    for e in W['program']:
        if e[0] in ('ADD', 'SCALE'):
            f = e[3] if e[0] == 'SCALE' else e[4]
            if out and out[-1][0] == 'B' and out[-1][1] == f: out[-1][2] += 1
            else: out.append(['B', f, 1])
        else: out.append([e[0]] + list(e[1:]))
    return out
sb, sc = skel(B), skel(C)
need([x if x[0] != 'B' else ('B', x[1]) for x in sb] == [x if x[0] != 'B' else ('B', x[1]) for x in sc], 'stop word -> final word: the non-gate events and the frame of every maximal ADD/SCALE run are identical; only same-frame runs are rewritten')
ch = [(x[2], y[2]) for x, y in zip(sb, sc) if x[0] == 'B' and x[2] != y[2]]
print('  runs of ADD and SCALE: %d; changed length: %d; events removed in them: %d (validated by the exact replay only)' % (sum(x[0] == 'B' for x in sb), len(ch), sum(a - b for a, b in ch)))
print('PASS_REORDER')
