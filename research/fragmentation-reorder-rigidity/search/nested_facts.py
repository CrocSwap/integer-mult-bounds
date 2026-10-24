#!/usr/bin/env python3
"""Facts needed for an order-free, frame-exact chain relaxation of #4610:
 (1) is every frame of a field's chain a superspace of its start frame (nestedness through warps)?
 (2) at every contact, do both start frames lie in the common frame, and does the common frame lie in both final frames?
 (3) interval per contact: lower = S_d + S_s, upper = T_d & T_s; dims of lower/current/upper.
 (4) per main field: number of distinct other ports it contacts directly (main-main) and via helpers."""
import json, gzip, collections, os, time
W3 = 'D:/Math/imb-docking/research/kappa-round3-warp-20261022/'
HERE = os.path.dirname(os.path.abspath(__file__)); LOG = open(os.path.join(HERE, 'progress.log'), 'a')
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s); LOG.write(s + '\n'); LOG.flush()
w = json.loads(gzip.decompress(open(W3 + 'ACTUAL-WORD.json.gz', 'rb').read()))
c = w['canonical']; frames = c['frames']; nf = len(c['start']); S = list(c['start']); T = list(c['final']); nm = 224
SP = {}
def sp(fi):
    if fi not in SP:
        s = {0}
        for v in frames[fi]: s |= {x ^ v for x in s}
        SP[fi] = frozenset(s)
    return SP[fi]
def dim(s): return len(s).bit_length() - 1
cur = list(S); chain = [[S[f]] for f in range(nf)]; cont = []
for e in w['programs']['forward']:
    if e[0] == 'climb': f = e[2]; cur[f] = e[4]; chain[f].append(e[4])
    elif e[0] == 'warp':
        f = e[1][1]; cur[f] = e[4]
        if e[4] != e[3]: chain[f].append(e[4])
    elif e[0] == 'scalar':
        op = e[1]; roles = [r for r in op[1:] if isinstance(r, list) and r[0] == 'L']
        if op[0] in ('add', 'copy') and len(roles) == 2: cont.append((roles[0][1], roles[1][1], e[2]))
# (1) nestedness
viol = 0; warpviol = 0
for f in range(nf):
    s0 = sp(S[f])
    for i, fr in enumerate(chain[f]):
        if not s0 <= sp(fr): viol += 1
        if i and not sp(chain[f][i-1]) <= sp(fr): warpviol += 1
log(f'(1) chain frames not containing the start frame: {viol}; non-nested consecutive chain steps (warps): {warpviol} of {sum(len(ch)-1 for ch in chain)}')
# (2),(3)
lo_ok = up_ok = 0; room = collections.Counter(); exact_lower = exact_upper = 0
for d, s, F in cont:
    lower = sp(S[d]) | sp(S[s]); lowspan = set(lower)
    for v in list(lower):
        lowspan |= {x ^ v for x in lowspan}
    lowspan = frozenset(lowspan); upper = sp(T[d]) & sp(T[s]); cf = sp(F)
    if lowspan <= cf: lo_ok += 1
    if cf <= upper: up_ok += 1
    room[(dim(lowspan), dim(cf), dim(upper))] += 1
    if dim(lowspan) == dim(cf): exact_lower += 1
    if dim(upper) == dim(cf): exact_upper += 1
log(f'(2) contacts {len(cont)}: start frames inside common frame {lo_ok}; common frame inside both finals {up_ok}')
log(f'(3) contacts at the interval bottom (dim F = dim(S_d+S_s)): {exact_lower}; at the top (dim F = dim(T_d & T_s)): {exact_upper}; strictly inside: {len(cont)-exact_lower-exact_upper + sum(1 for (a,b,c_),n in room.items() if a==b==c_ for _ in range(n))}')
log('(3) (dim lower, dim F, dim upper) histogram, top 25: ' + str(sorted(room.items(), key=lambda kv: -kv[1])[:25]))
# (4) ports per main
port_of = {}
for p, line in enumerate(c['ports']):
    for f in range(nm):
        if frames[S[f]] == [line] or (len(frames[S[f]]) == 0 and False): port_of.setdefault(f, p)
# mains: X_p starts at q_p (dim 1); Y_p starts at 0 -> identify by final frame = q_p^perp? use pairing: assume field index f<112 -> X, 112<=f<224 -> Y with same port order
mm = collections.defaultdict(set); mh = collections.defaultdict(set); hm = collections.defaultdict(set)
for d, s, F in cont:
    for a, b in ((d, s), (s, d)):
        if a < nm and b < nm: mm[a].add(b % 112)
        elif a < nm: mh[a].add(b)
        else: hm[a].add(b % 112)
pm = collections.Counter(len(v - {f % 112}) for f, v in mm.items()); ph = collections.Counter(len(v) for v in hm.values())
log(f'(4) distinct other ports contacted main-main per main: {dict(sorted(pm.items()))}; distinct ports contacted per helper: {dict(sorted(ph.items()))}')
log(f'    mains with no main-main contact: {nm - len(mm)}; mean helpers per main {sum(len(v) for v in mh.values())/nm:.1f}')
