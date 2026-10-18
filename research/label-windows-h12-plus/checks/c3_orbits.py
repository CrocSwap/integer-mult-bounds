"""c3: symmetry facts behind the reduction of the census to 47 x 440,880 pairs and of the SAT queries to 6 exceptional orbits (pynauty; OPTIONAL: SKIP without it).
  c3.a  |Aut(orthogonality graph of P112)| = 172,032 and its generators map the family of 440,880 sections to itself (no violations)
  c3.b  the 144 exceptional pairs form exactly 6 orbits under Aut and transposition, and these are exactly the 6 pairs of data/pairsX.json (the queried orbits)
  c3.c  (FULL=1, slow) the 47 representatives have 47 distinct certificates and EVERY one of the 440,880 sections has the certificate of a representative."""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
try: import pynauty
except ImportError:
    for k in 'abc': print('SKIP c3.%s  pynauty not installed' % k)
    sys.exit(0)
import common
D = common.load(); Z, NO, reps, P = D['Z'], D['NO'], D['reps'], D['P']
adj = {i: [j for j in range(112) if j != i and not NO[i, j]] for i in range(112)}      # orthogonality graph
fail = 0
gens, g1, g2, orb, norb = pynauty.autgrp(pynauty.Graph(112, adjacency_dict=adj))
order = round(g1 * 10 ** g2); keys = {bytes(r) for r in np.packbits(Z, axis=1)}; viol = 0
for g in gens:
    g = np.array(g); Zi = np.zeros_like(Z); Zi[:, g] = Z
    viol += sum(bytes(r) not in keys for r in np.packbits(Zi, axis=1))
ok = order == 172032 and viol == 0
print(('PASS' if ok else 'FAIL') + ' c3.a  |Aut| = %d (%d generators); all generators map the 440,880 sections to sections (%d violations)' % (order, len(gens), viol)); fail += not ok
def cert(A, B):
    a, b = set(A), set(B); cl = [c for c in (a & b, a - b, b - a, set(range(112)) - a - b) if c]
    return pynauty.certificate(pynauty.Graph(112, adjacency_dict=adj, vertex_coloring=cl))
def sec(i): return list(np.nonzero(Z[i])[0])
ex = json.load(open(os.path.join(HERE, '..', 'data', 'exceptional_pairs.json'))); orbits = {}
for r, i, w in ex:
    A, B = sec(reps[r]), sec(i); orbits.setdefault(min(cert(A, B), cert(B, A)), []).append((r, i, w))
px = json.load(open(os.path.join(HERE, '..', 'data', 'pairsX.json')))
mine = set(); wx = []
cw = {k: v[0][2] for k, v in orbits.items()}
for H1, H2 in px:
    a = [P.index(v) for v in H1]; b = [P.index(v) for v in H2]; k = min(cert(a, b), cert(b, a)); mine.add(k); wx.append(cw.get(k))
ok = len(orbits) == 6 and mine == set(orbits) and wx == [6, 6, 6, 6, 5, 6]
print(('PASS' if ok else 'FAIL') + ' c3.b  144 exceptional pairs = %d orbits (sizes %s), identical to the 6 queried pairs of data/pairsX.json; omega of pairsX[0..5] = %s (pair 4 is the omega-5 orbit)' %
      (len(orbits), sorted(len(v) for v in orbits.values()), wx)); fail += not ok
if os.environ.get('FULL') == '1':
    t = time.time(); rc = set()
    def cs(i):
        a = set(sec(i)); return pynauty.certificate(pynauty.Graph(112, adjacency_dict=adj, vertex_coloring=[a, set(range(112)) - a]))
    rc = {cs(i) for i in reps}; bad = sum(cs(i) not in rc for i in range(440880))
    ok = len(rc) == 47 and bad == 0
    print(('PASS' if ok else 'FAIL') + ' c3.c  47 distinct representative certificates; sections outside the 47 classes: %d (%ds)' % (bad, time.time() - t)); fail += not ok
else: print('SKIP c3.c  FULL=1 only (certificate of all 440,880 sections)')
sys.exit(1 if fail else 0)
