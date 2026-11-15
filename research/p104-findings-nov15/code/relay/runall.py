import collections, pickle
from drive import *
base_ops = [(float(i), e) for i, e in enumerate(W['program'])]
tl = timeline(base_ops, NP, W['owned_fields'], W['initial'])
res = {}; t0 = time.time()
for F in X['relay']:
    r, why = remove_frame(list(base_ops), F, X['stops'][F], tl)
    res[F] = (why, gainF(F))
c = collections.Counter(v[0].split()[0] for v in res.values()); print(c, '%.0fs' % (time.time() - t0))
ok = [F for F, v in res.items() if v[0] == 'ok']; print('ok frames', ok, 'gain', sum(res[F][1] for F in ok))
pickle.dump(res, open('runall.pkl', 'wb'))
