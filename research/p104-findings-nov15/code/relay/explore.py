import sys, collections, pickle
from lib import *
W = load(); NP, mains, fixed, dim = setup(W); P = W['program']; ch = chains(W)
# frames ever held by a fixed register (mains: their chains; owned: INIT/CLEAR/op frames)
fixedF = set()
for r in mains:
    for fr, _ in ch[r]: fixedF.add(fr)
for e in P:
    fr = evframe(e)
    if fr is not None and (fixed(e[1]) or (e[0] in ('ADD','COPY') and fixed(e[2]))): fixedF.add(fr)
for r in range(NP): fixedF.add(W['final'][r]) if r in mains else None
stops = collections.defaultdict(list)   # frame -> [(helper, arrive_idx, leave_idx, prev frame, next frame)]
for h in range(NP):
    if h in mains: continue
    c = ch[h]
    for k in range(1, len(c) - 1):
        stops[c[k][0]].append((h, c[k][1], c[k + 1][1], c[k - 1][0], c[k + 1][0]))
ops = collections.defaultdict(list)
for i, e in enumerate(P):
    fr = evframe(e)
    if fr is not None: ops[fr].append(i)
relay = sorted(F for F in stops if F not in fixedF)
print('frames with interior helper stops', len(stops), 'never-fixed', len(relay), 'stops there', sum(len(stops[F]) for F in relay))
rows = []
for F in relay:
    S = stops[F]; hs = {s[0] for s in S}
    o = [P[i] for i in ops[F]]
    nadd = sum(1 for e in o if e[0] == 'ADD'); nsc = sum(1 for e in o if e[0] == 'SCALE')
    inter = sum(1 for e in o if e[0] == 'ADD' and not (e[1] in hs and e[2] in hs))
    # gain if F removed from all stopping helpers (hop-cost only)
    g = sum(f(dim[s[4]] - dim[s[3]]) - f(dim[F] - dim[s[3]]) - f(dim[s[4]] - dim[F]) for s in S)
    # who stays simultaneous: max overlap
    rows.append((F, dim[F], len(S), nadd, nsc, inter, g, len(ops[F])))
rows.sort(key=lambda x: x[6])
print('F dim nstops nadd nscale nonhh gain')
for r in rows[:15]: print(r)
print('dist nstops', collections.Counter(r[2] for r in rows))
print('dist nadd', sorted(collections.Counter(min(r[3], 30) for r in rows).items()))
print('total gain all', sum(r[6] for r in rows))
pickle.dump(dict(relay=relay, stops=dict(stops), rows=rows, fixedF=fixedF), open('explore.pkl', 'wb'))
