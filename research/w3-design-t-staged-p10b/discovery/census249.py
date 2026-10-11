"""Kernel census on a PR249 snapshot: sigma-0 helpers (initial ZERO, final FULL) with their frame-ZERO completion
reads (cat 4), F2 response, last read, first touch and first frame. Output in coll/census.py's pickle format.
usage: census249.py SNAPDIR OUT.pkl"""
import sys, json, collections, pickle
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'code'))
import stagelib as w3t
snap = w3t.load_snapshot(sys.argv[1]); s = snap['s']; rec = snap['rec']; fr = snap['fr']['frames']
n, v, ZERO, FULL = s['n'], s['v'], s['ZERO'], s['FULL']
init = {r: s['initial'][str(r)] for r in range(n)}; final = {r: s['final'][str(r)] for r in range(n)}
cand = [r for r in range(2 * v, n) if init[r] == ZERO and final[r] == FULL]
C = set(cand); reads = collections.defaultdict(list); touch = {}; ff = {}; firstmove = {}
for i, (op, a, b, c, f, z) in enumerate(rec.tolist()):
    if op == 1:
        if b in C and z == 4 and f == ZERO and v <= a < 2 * v and c % 2: reads[b].append((i, a)); continue
        for x in (a, b):
            if x in C and x not in touch: touch[x] = i; ff[x] = f
    elif op == 2:
        if a in C and a not in touch: touch[a] = i; ff[a] = c
    elif op == 0:
        if a in C and a not in firstmove: firstmove[a] = (i, b, c)
hel = [x for x in cand if x in touch]
resp = {}; lastread = {}
for x in hel:
    cnt = collections.Counter(a for i, a in reads[x])
    resp[x] = sum(1 << (a - v) for a, c in cnt.items() if c % 2)
    lastread[x] = reads[x][-1][0] if reads[x] else -1
    assert lastread[x] < touch[x]
    assert firstmove[x][1] == ZERO and firstmove[x][0] < touch[x]
# the first touch frame must be the first MOVE's target (single entrance move), otherwise use the first MOVE target
nm = 0
for x in hel:
    if firstmove[x][2] != ff[x]: ff[x] = firstmove[x][2]; nm += 1
print('candidates', len(cand), 'touched', len(hel), 'with reads', sum(1 for x in hel if reads[x]), 'zero response', sum(1 for x in hel if resp[x] == 0), 'first move != first touch frame', nm)
dimc = collections.Counter(len(fr[str(ff[x])]['B']) for x in hel); print('first-frame dims', sorted(dimc.items()))
ftab = {f: dict(B=fr[str(f)]['B'], A=fr[str(f)]['A'], dim=len(fr[str(f)]['B'])) for f in set(ff.values())}
pickle.dump(dict(n=n, v=v, ZERO=ZERO, FULL=FULL, helpers=hel, resp=resp, lastread=lastread, touch=touch, firstframe=ff,
                 ftab=ftab, nreads={x: len(reads[x]) for x in hel}), open(sys.argv[2], 'wb'))
