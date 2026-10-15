"""Alias pairs (helper h -> retired lender L) on a BORROW-WORD, classified:
  live    : liveness OK in mkalias sense (L's last event < h's first B gate; L not in restore; L no later warp)
  fixed   : frame rule holds with the word's own frames (dim U_L <= dim F1_h)
  refit   : frame rule holds in SOME refit: dim lo(L_last) <= dim hi(h_first)   (exact, lattice argument)
usage: pairs.py WORD.json.gz OUT.json
"""
import sys, json
from collections import Counter, defaultdict
from bounds import Bounds, basis, contained, regs

b = Bounds(sys.argv[1]); Wd = b.Wd; w = Wd.w; v = Wd.v; ev = b.ev
restored = {int(q) for q in w.get('helper_final', {})}
lenders_now = {rec[1] for rec in w['warps']}
B0 = min(t for t, (sec, e) in enumerate(ev) if sec in ('B', 'Bwarp'))
# touches (all sections, incl. cut / pre / comp) per register
touch = defaultdict(list)
for t, (sec, e) in enumerate(ev):
    if e[0] == 'warp':
        touch[e[1]].append((t, sec))
    else:
        for q in regs(e):
            touch[q].append((t, sec))
# followers
fol = {}
why_not_f = Counter()
for h in Wd.helpers:
    T = touch.get(h, [])
    if h in restored:
        why_not_f['restored-cold'] += 1; continue
    if any(sec not in ('B', 'restore', 'Bwarp') for t, sec in T):
        why_not_f['touched-before-B'] += 1; continue
    if h in lenders_now:
        why_not_f['already-a-lender'] += 1; continue
    gs = [t for t, sec in T if sec in ('B', 'restore')]
    if not gs:
        why_not_f['untouched'] += 1; continue
    first = gs[0]
    fol[h] = dict(first=first, F1=len(Wd.gateframe[first]), hi=len(b.hi[first]), S=len(Wd.start[h]),
                  width=len(Wd.end[h]) - len(Wd.start[h]))
# lenders
lend = {}
why_not_l = Counter()
for L in Wd.live:
    if v <= L < 2 * v:
        continue
    if L in restored:
        why_not_l['restored-cold'] += 1; continue
    T = touch.get(L, [])
    if any(sec == 'restore' for t, sec in T):
        why_not_l['touched-in-restore'] += 1; continue
    last = T[-1][0] if T else -1
    # frame after last event: last framed gate or warp E or start
    lastf = [x for x in b.byreg.get(L, [])]
    if lastf and lastf[-1][1] == 'warp':
        U = len(lastf[-1][3]); lo = U; kind = 'warpE'
    elif lastf:
        g = lastf[-1][0]; U = len(Wd.gateframe[g]); lo = len(b.lo[g]); kind = 'gate'
    else:
        U = len(Wd.start[L]); lo = U; kind = 'start'
    lend[L] = dict(last=last, U=U, lo=lo, kind=kind, src=L < v)
cnt = Counter(); rows = []
for h, f in fol.items():
    for L, l in lend.items():
        if L == h:
            continue
        if not l['last'] < f['first']:
            continue
        cnt['live'] += 1
        if l['U'] <= f['F1']:
            cnt['fixed-ok'] += 1; rows.append((h, L, 'fixed')); continue
        if l['lo'] <= f['hi']:
            cnt['refit-ok'] += 1; rows.append((h, L, 'refit'))
        else:
            # reason
            r = []
            if l['lo'] > f['F1']: r.append('lender-floor>F1')
            if l['U'] > f['hi']: r.append('U>follower-ceiling')
            cnt['blocked'] += 1
            cnt['blocked:' + ('both' if len(r) == 2 else (r[0] if r else 'joint'))] += 1
out = dict(word=sys.argv[1], followers=len(fol), followers_excluded=dict(why_not_f), lenders=len(lend),
           lenders_excluded=dict(why_not_l), counts=dict(cnt),
           follower_F1_hist=dict((str(k),c) for k,c in Counter((f['F1'], f['hi']) for f in fol.values()).most_common()),
           lender_U_lo_hist={str(k): c for k, c in Counter((l['U'], l['lo'], l['kind']) for l in lend.values()).most_common()},
           pairs=[(h, L, k, fol[h], lend[L]) for h, L, k in rows])
json.dump(out, open(sys.argv[2], 'w'), indent=0, default=str)
print(json.dumps({k: out[k] for k in out if k != 'pairs'}, default=str))
print('fixed-ok', [(h, L) for h, L, k in rows if k == 'fixed'][:40])
print('refit-ok', [(h, L) for h, L, k in rows if k == 'refit'][:80])
