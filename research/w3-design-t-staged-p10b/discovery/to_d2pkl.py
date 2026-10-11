"""PR249 snapshot -> descent2_search pickle (records, A, B, dimf, chi, h, v, nregs, initial, final, ZERO, FULL, cats). usage: to_d2pkl.py SNAP LABELS(graph_p10.json) OUT.pkl"""
import sys, json, pickle, collections
import numpy as np
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'code'))
import stagelib as w3t
snap = w3t.load_snapshot(sys.argv[1]); s = snap['s']; rec = snap['rec']; F = snap['fr']['frames']
lab = json.load(open(sys.argv[2]))['labels']; v = s['v']; n = s['n']
chi = [[1 if j in l else 0 for j in range(20)] for l in lab]
A = {int(k): [list(map(int, r)) for r in x['A']] for k, x in F.items()}
B = {int(k): [list(map(int, r)) for r in x['B']] for k, x in F.items()}
dimf = {k: len(b) for k, b in B.items()}
init = {r: s['initial'][str(r)] for r in range(n)}; final = {r: s['final'][str(r)] for r in range(n)}
# consistency: just-in-time chain histogram == record MOVE histogram
chain = {r: [] for r in range(n)}
for o, a, b, c, f, z in rec.tolist():
    if o == 1:
        chain[a].append(f)
        if b != n: chain[b].append(f)
    elif o == 2: chain[a].append(c)
H = collections.Counter()
for r in range(n):
    bef = init[r]
    for f in chain[r] + [final[r]]:
        d = dimf[f] - dimf[bef]; assert d >= 0, (r, bef, f)
        if d: H[d] += 1
        bef = f
HR = collections.Counter(int(x) for x in rec[(rec[:, 0] == 0) & (rec[:, 4] > 0), 4])
print('JIT hist == record MOVE hist:', H == HR, sum(H.values()), sum(HR.values()))
pickle.dump(dict(records=np.ascontiguousarray(rec, dtype='<i4').tobytes(), initial=init, final=final, A=A, B=B, dimf=dimf, chi=chi, cov=None, h=20, v=v,
                 ZERO=s['ZERO'], FULL=s['FULL'], cats=['c%d' % i for i in range(64)], nregs=n), open(sys.argv[3], 'wb'))
