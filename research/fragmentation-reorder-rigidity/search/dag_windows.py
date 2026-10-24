#!/usr/bin/env python3
"""Step A1: how much order freedom do the scalar operations of #4610 have, and does it let contacts move
across the climbs of their fields?

Dependency DAG on the 17,453 scalar ops (climbs/warps are frame bookkeeping and are left out; they will be
re-placed wherever the chosen order needs them).  Two ops conflict iff one writes a register the other reads,
or both write it, except that adds into the same destination commute.  ASAP/ALAP layers from the DAG.
For every field f and every consecutive pair of its contact frames F < G (in the chain), count the contacts at F
that could be scheduled after the earliest contact at G (ALAP(e) >= ASAP(e') for some e' at G) -- 'deferrable by
dependencies' -- and combine with the exact-frame partner test (partner chain contains G).  Stdlib only."""
import json, gzip, collections, os, time, sys
sys.setrecursionlimit(10000)
W3 = 'D:/Math/imb-docking/research/kappa-round3-warp-20261022/'
HERE = os.path.dirname(os.path.abspath(__file__)); LOG = open(os.path.join(HERE, 'progress.log'), 'a')
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s); LOG.write(s + '\n'); LOG.flush()
w = json.loads(gzip.decompress(open(W3 + 'ACTUAL-WORD.json.gz', 'rb').read()))
c = w['canonical']; frames = c['frames']; nf = len(c['start']); S = list(c['start']); T = list(c['final']); nm = 224
prog = w['programs']['forward']
# scalar ops with read/write sets
ops = []   # (idx_in_prog, kind, writes:set, reads:set, is_add, frame, roles)
cur = list(S); chain = [[S[f]] for f in range(nf)]; contact_of = {}   # op index -> (d, s, Fd, Fs)
for i, e in enumerate(prog):
    if e[0] == 'climb': f = e[2]; cur[f] = e[4]; chain[f].append(e[4])
    elif e[0] == 'warp':
        f = e[1][1]; cur[f] = e[4]
        if e[4] != e[3]: chain[f].append(e[4])
    elif e[0] == 'scalar':
        op = e[1]; kind = op[0]; roles = [tuple(r) for r in op[1:] if isinstance(r, list)]
        if kind == 'add':
            d, s = roles[0], roles[1]; ops.append((i, kind, {d}, {s}, True, e[2], roles))
        elif kind == 'copy':
            d, s = roles[0], roles[1]; ops.append((i, kind, {d}, {s}, False, e[2], roles))
        elif kind == 'scale': ops.append((i, kind, {roles[0]}, set(), False, e[2], roles))
        elif kind == 'clear': ops.append((i, kind, {roles[0]}, set(), False, e[2], roles))
        else: raise ValueError(kind)
        if kind in ('add', 'copy') and roles[0][0] == 'L' and roles[1][0] == 'L':
            contact_of[len(ops) - 1] = (roles[0][1], roles[1][1], cur[roles[0][1]])
n = len(ops); log(f'scalar ops {n}; two-field contacts {len(contact_of)}')
# DAG edges via last writer / readers per register
pred = [set() for _ in range(n)]
last_write = {}; readers_since = collections.defaultdict(list); adds_since = collections.defaultdict(list)
for j, (i, kind, W, Rd, is_add, F, roles) in enumerate(ops):
    for r in Rd:
        if r in last_write: pred[j].add(last_write[r])
        for a in adds_since.get(r, []): pred[j].add(a)       # reading r after adds into r
    for r in W:
        if is_add:
            # commutes with other adds into r; depends on last non-add writer and on readers since then
            if r in last_write: pred[j].add(last_write[r])
            for k in readers_since.get(r, []): pred[j].add(k)
            adds_since[r].append(j)
        else:
            if r in last_write: pred[j].add(last_write[r])
            for k in readers_since.get(r, []): pred[j].add(k)
            for a in adds_since.get(r, []): pred[j].add(a)
            last_write[r] = j; readers_since[r] = []; adds_since[r] = []
    for r in Rd: readers_since[r].append(j)
    pred[j].discard(j)
succ = [set() for _ in range(n)]
for j in range(n):
    for k in pred[j]: succ[k].add(j)
asap = [0] * n
for j in range(n): asap[j] = 1 + max((asap[k] for k in pred[j]), default=-1)
depth = max(asap) + 1
alap = [depth - 1] * n
for j in range(n - 1, -1, -1): alap[j] = min((alap[k] - 1 for k in succ[j]), default=depth - 1)
slack = [alap[j] - asap[j] for j in range(n)]
log(f'DAG depth {depth} (critical path) vs {n} ops; edges {sum(len(p) for p in pred)}; slack histogram (quantiles): '
    + str([sorted(slack)[int(q * (n - 1))] for q in (0, .1, .25, .5, .75, .9, 1)]))
# per field: contacts by frame with asap/alap
chainset = [set(ch) for ch in chain]
byf = collections.defaultdict(lambda: collections.defaultdict(list))   # f -> frame -> [(asap, alap, partner, opidx)]
for j, (d, s, F) in contact_of.items():
    byf[d][F].append((asap[j], alap[j], s, j)); byf[s][F].append((asap[j], alap[j], d, j))
levels = removable_dep = removable_both = 0; per_field_removable = collections.Counter()
for f in range(nf):
    ch = chain[f]
    for i in range(1, len(ch) - 1):
        F = ch[i]; cs = byf[f].get(F, [])
        if not cs: continue
        levels += 1
        G, E = ch[i+1], ch[i-1]
        later = [a for a, _, _, _ in byf[f].get(G, [])]; earlier = [b for _, b, _, _ in byf[f].get(E, [])]
        first_G = min(later) if later else 10**9; last_E = max(earlier) if earlier else -1
        ok_dep = all((al >= first_G) or (asp <= last_E) for asp, al, _, _ in cs)
        ok_both = all(((al >= first_G) and G in chainset[g]) or ((asp <= last_E) and E in chainset[g]) for asp, al, g, _ in cs)
        removable_dep += ok_dep; removable_both += ok_both
        if ok_both: per_field_removable[f] += 1
log(f'contact levels {levels}: removable by dependency windows alone {removable_dep}; by windows AND exact partner frames {removable_both}')
log(f'fields with >=1 jointly removable level: {len(per_field_removable)}; total removable levels {sum(per_field_removable.values())}')
json.dump({'ops': n, 'depth': depth, 'levels': levels, 'removable_dep': removable_dep, 'removable_both': removable_both,
           'slack_quantiles': [sorted(slack)[int(q * (n - 1))] for q in (0, .1, .25, .5, .75, .9, 1)]},
          open(os.path.join(HERE, 'dag_windows_result.json'), 'w'), indent=1)
log('done dag_windows')
