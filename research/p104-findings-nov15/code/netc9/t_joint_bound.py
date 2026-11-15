"""NETC9 joint-supply relaxation of NETC8 t_fbound_all (own code). MODE=A orig; B frames F<=E (any, other carriers at E supply their own picks); C = B and no lower validity bound (picks any time < t_r).
Original doc: G2 re-plan bound for F-MIX (own code, mod 2^61-1 screen): a TRIM-END carrier with F-MIX must retract its token from
the receiver r before r's next kept read, at a frame E that r occupies then (E != V).  So its whole post-delivery tail
(-v) must come from snapshots at frames G <= F <= E valid inside (t1, t_r).  Optimistic: chain order ignored, compiled
readers of r ignored, the tail costs one stop (E).  Reports how many eligible carriers pass and the D0 they could save."""
import sys, os, time, collections, math
sys.path.insert(0, 'inputs/NETC6')
from core6 import *
sys.path.insert(0, 'inputs/NETC7')
from run_netc5 import relay_phase
from settle import replay
from decomp import tomod, ordered_solve
import trim
MODE=os.environ.get('MODE','A')
t0 = time.time(); log = lambda *a: print('[%4.0fs]' % (time.time() - t0), *a, flush=True)
N = load(log); N.build(); W1, lz = relay_phase(N, lambda *a: None)
rows = replay(W1)[0]; n = N.w.n; V = N.V; Z = N.Z; bW = N.w.W; sp = N.w.sp; dim = N.w.dim
W0p0 = [y for y in N.W0 if not (y < n and bW['final'][y] == V)]
trim.choose(N, W1, rows, W0p0, log=log)
snaps = N.snaps; byframe = collections.defaultdict(list)
for i, s in enumerate(snaps): byframe[s[3]].append(i)
nf = len(bW['frames']); W0s = set(N.W0)
st = collections.Counter(); sv_ok = 0.0; sv_all = 0.0; okE = collections.Counter()
for i in (range(len(N.H)) if os.environ.get("ALL") else sorted(N._eligE)):
    h = N.H[i]; b = h.get('block')
    if b is None: st['no block'] += 1; continue
    b = b; r, G, t1, v = b['r'], b['frame'], b['t1'], b['v']
    c0 = N.hcost(h)[0]
    vis = sorted(h['visits'], key=lambda x: x[0]); pre = [x for x in vis if x[0][0] < t1 or (x[0][0] == t1 and x[0][1] <= 0.5)]
    if r in W0s and bW['final'][r] != V: st['receiver W0p (pre-pay class)'] += 1; continue
    nxt = min([t for t in N.reads[r] if t > t1] + [10 ** 9])
    Es = []
    for j, (t, fr, pi) in enumerate(N.traj[r]):
        te = N.traj[r][j + 1][0] if j + 1 < len(N.traj[r]) else 10 ** 9
        if te <= t1 or t >= nxt or fr is None or fr == V: continue
        if sp[G] <= sp[fr]: Es.append((dim[fr], fr, min(te, nxt)))
    if not Es: st['r leaves for V / never at a frame >= G before its next read'] += 1; continue
    found = None
    for dE, E, tr in sorted(set(Es)):
        C = [k for F in range(nf) if (sp[G] <= sp[F] if MODE=='A' else True) and sp[F] <= sp[E] and F != V for k in byframe[F]
             if snaps[k][0] != r and snaps[k][1] < tr and (snaps[k][2] > t1 or MODE=='C')]
        if C and ordered_solve(tomod(v), [tomod(snaps[k][4]) for k in C]) is not None: found = E; break
    if found is None: st['tail -v not in window span'] += 1; continue
    h2 = dict(h, visits=pre + [((t1, 0.9), found, ('pick', None, 0))], end=found)
    s = c0 - N.hcost(h2)[0]; st['PASS'] += 1; sv_ok += s; okE[dim[found]] += 1
log('eligible END carriers', len(N._eligE), dict(st))
log('F-MIX re-plan bound: %d pass, optimistic saving %.1f D0/call (of 40,351.8); end dims %s' % (st['PASS'], sv_ok, dict(okE)))
