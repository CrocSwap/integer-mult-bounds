"""P104 X-only correction: replay a complete 104-target relay word and the line fan-out floor.
Standard library only, read-only.  Usage:
  python3 -I -B check_p104_relay_construction.py REPO_ROOT WORD.json [--ledger PR2526_LEDGER.json]
Model (PR2353/PR2393/PR2445): new helper lifetimes start at ZERO with independent dirty values, move only
upward along nested frames, mix by rational ADDs only in equal frames, read immutable X only in X's retained
frame at that cut, write Y only additively in Y's frame at that cut, never read original helpers or Y."""
import collections, hashlib, json, os, sys
from fractions import Fraction as Q
from itertools import combinations, product
ROOT = os.path.abspath(sys.argv[1]); WORD = sys.argv[2]
LEDGER = sys.argv[sys.argv.index('--ledger') + 1] if '--ledger' in sys.argv else None
def need(ok, why):
    if not ok: raise SystemExit('FAIL: ' + why)
PKG = os.path.join(ROOT, 'research', 'p104-native-channel')
PINS = {'inputs/LOWRANK-WITNESS.json': '0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e',
        'inputs/P104-FIXTURE.json': '516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4'}
for p, h in PINS.items():
    need(hashlib.sha256(open(os.path.join(PKG, p), 'rb').read()).hexdigest() == h, 'pin ' + p)
W = json.load(open(os.path.join(PKG, 'inputs/LOWRANK-WITNESS.json')))
fx = json.load(open(os.path.join(PKG, 'inputs/P104-FIXTURE.json')))['section4_explicit_P104']
# geometry (as in check_p104_window_bill.py)
L8 = set()
for i, j in combinations(range(8), 2):
    for sg in (-1, 1):
        v = [0]*8; v[i] = 2; v[j] = 2*sg; L8.add(tuple(v))
for sg in product((-1, 1), repeat=7):
    if sg.count(-1) % 2 == 0: L8.add((1, *sg))
removed = {tuple(r) for r in fx['F0'] + fx['C']}
ports = [r for r in sorted(L8) if r not in removed]; n = len(ports); need(n == 104, '104 ports')
G = [[sum(x*y for x, y in zip(a, b)) // 4 for b in ports] for a in ports]
C = [{s: (Q(1) if t == s else Q(0)) - Q(G[t][s], 2) for s in range(n) if (Q(1) if t == s else Q(0)) - Q(G[t][s], 2)} for t in range(n)]
def span(vs):
    s = {0}
    for b in vs:
        if b not in s: s |= {x ^ b for x in s}
    return frozenset(s)
cur = {r: span(f) for r, f in W['initial_frames'].items()}; path = {r: [(0, cur[r])] for r in cur}
for i, e in enumerate(W['program']):
    if e[0] == 'transport':
        need(cur[e[1]] == span(e[2]), 'transport entry'); cur[e[1]] = span(e[3]); path[e[1]].append((i + 1, cur[e[1]]))
    elif e[0] == 'zero': cur['C'] = span(e[2]); path['C'] = [(i + 1, cur['C'])]
NE = len(W['program']); FULL = frozenset(range(512)); ZERO = frozenset({0})
def frame_at(r, c):
    fr = None
    for st, f in path[r]:
        if st <= c: fr = f
    return fr
q = [W['initial_frames']['X%d' % s][0] for s in range(n)]
H = [cur['Y%d' % t] for t in range(n)]
need(all(frame_at('X%d' % s, NE) == FULL for s in range(n)), 'sources end FULL')
need(all(frame_at('Y%d' % t, 0) == ZERO for t in range(n)), 'targets start ZERO')
dot = lambda a, b: bin(a & b).count('1') & 1
# ---------- part A: line fan-out floor (exact) ----------
# A source's line read reaches target t only through a lifetime that leaves the line for a frame W ⊂ H_t;
# every such W contains a plane <q_s, w> ⊂ H_t.  kappa_s = min #planes through q_s covering T_s.
normal = [next(v for v in range(1, 512) if all(not dot(v, h) for h in H[t])) for t in range(n)]
need(all(H[t] == frozenset(v for v in range(512) if not dot(v, normal[t])) for t in range(n)), 'H_t hyperplanes')
supp = {t: set(C[t]) for t in range(n)}
need(all(supp[t] == {s for s in range(n) if q[s] in H[t]} for t in range(n)), 'supp C_t = lines in H_t')
kappa = {}
for s in range(n):
    Ts = [t for t in range(n) if s in supp[t]]
    ws = [w for w in range(1, 512) if w != q[s]]
    cov = {w: frozenset(t for t in Ts if not dot(normal[t], w)) for w in ws}
    one = any(len(c) == len(Ts) for c in cov.values())
    two = next(((a, b) for a, b in combinations(ws, 2) if len(cov[a] | cov[b]) == len(Ts)), None)
    need(not one and two is not None, 'kappa_s = 2'); kappa[s] = 2
LINE_FLOOR = sum(kappa.values()); need(LINE_FLOOR == 208, 'line fan-out floor 208')
# affine structure: one u* with <u*, q_s> = 1 for every source
ustar = [u for u in range(1, 512) if all(dot(u, x) for x in q)]; need(len(ustar) == 1, 'unique u*')
# ---------- part B: replay the word ----------
Wd = json.load(open(WORD)); ops = Wd['ops']; need(ops[0][0] == 'move_zero_all', 'header')
NL = ops[0][1]; fr = {L: ZERO for L in range(NL)}; val = {L: {('d', L): Q(1)} for L in range(NL)}
steps = {L: [] for L in range(NL)}; Y = {t: {} for t in range(n)}; now = 0
def add(dst, c, src):
    for k, v in src.items():
        z = dst.get(k, 0) + c*v
        if z: dst[k] = z
        else: dst.pop(k, None)
cnt = collections.Counter(); arrivals = 0
for o in ops[1:]:
    op = o[0]; cnt[op] += 1
    if op == 'move':
        L = o[1]; new = span(o[2])
        need(fr[L] < new, 'move must strictly enlarge a nested frame (op %r)' % (o[:2],))
        steps[L].append(len(bin(len(new))) - len(bin(len(fr[L])))); fr[L] = new
    elif op == 'read':
        L, s, c, cut = o[1], o[2], Q(o[3]), o[4]; need(cut >= now, 'cut order'); now = cut
        need(fr[L] == frame_at('X%d' % s, cut), 'read of X%d outside its retained frame at cut %d' % (s, cut))
        add(val[L], c, {('x', s): Q(1)})
    elif op == 'shear':
        i, j, c = o[1], o[2], Q(o[3]); need(i != j and fr[i] == fr[j], 'shear needs equal frames')
        add(val[i], c, dict(val[j]))
    elif op == 'write':
        t, L, c, cut = o[1], o[2], Q(o[3]), o[4]; need(cut >= now, 'cut order'); now = cut
        need(fr[L] == frame_at('Y%d' % t, cut), 'write to Y%d outside its frame at cut %d' % (t, cut))
        add(Y[t], c, val[L]); arrivals += (cut == NE)
    else: raise SystemExit('FAIL: unknown op ' + op)
for t in range(n):
    need(all(k[0] == 'x' for k in Y[t]), 'Y%d keeps dirty residue' % t)
    need({k[1]: v for k, v in Y[t].items()} == C[t], 'Y%d correction != (I - G/2) row' % t)
need(all(fr[L] == FULL for L in range(NL)), 'every lifetime ends at FULL')
need(all(val[L] == {('d', L): Q(1)} for L in range(NL)), 'every dirty helper restored')
prof = collections.Counter(r for L in range(NL) for r in steps[L])
need(all(sum(steps[L]) == 9 for L in range(NL)), 'ZERO-to-FULL lifetimes (9 rank units each)')
writes_per_target = collections.Counter(o[1] for o in ops if o[0] == 'write' and o[4] == NE)
OUT = dict(lifetimes=NL, arrivals_at_NE=arrivals, min_writes_per_target=min(writes_per_target.values()),
           ops=dict(cnt), profile=dict(sorted(prof.items())), rank_mass=sum(r*c for r, c in prof.items()),
           simultaneously_live_cuts_0_to_NE=NL, line_fanout_floor=LINE_FLOOR,
           per_target=round(NL / n, 2), versus_PR2445_sharing_39x104=39*n)
# ---------- part C: pricing against PR2526 ----------
sys.path.insert(0, os.path.join(ROOT, 'research', 'complex-local-word-ceiling'))
import ceiling as CE
chan = {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8}; m, fam, st, cen = 73, 832, 9, 56
idle = CE.model(chan, m, fam, st, cen)['idle_mass']; need(idle == 4344, 'idle mass')
OUT['idle_lifetime_cap'] = idle // 9
need(NL > idle // 9, 'construction exceeds the idle-mass lifetime cap (expected for this word)')
if LEDGER:
    led = json.load(open(LEDGER))['rows']['struct_boundary_radix_union']
    k0 = Q(led['kappa']['rational']); OUT['PR2526_kappa'] = float(k0)
print(json.dumps(OUT, indent=1))
print('PASS_P104_RELAY_CONSTRUCTION lifetimes=%d per_target=%.2f line_floor=%d idle_cap=%d' % (NL, NL / n, LINE_FLOOR, idle // 9))
