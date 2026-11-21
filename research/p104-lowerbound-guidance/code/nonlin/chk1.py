from ncore import *
# L1: for each t, {u in F2^9 : beta(u,h_s)=0 for all s in O_t} == {0, ctil_t}
bad=0
for t in range(n):
    O=np.nonzero(Q[t])[0]
    K=kernel((H[O]@Beta)%2)
    ok = K.shape[0]==1 and (K[0]==ctil(t)).all()
    bad+= (not ok)
print('L1 violations',bad)
# L2: linear span in F2^8 of c_s, s in O_t, has dim 7
print('L2 dims',set(f2rank(Cb[np.nonzero(Q[t])[0]]) for t in range(n)))
# L3: u with beta(u,h_t)beta(h_t,h_s)=0 for all t in P (fixed s): solutions
cnt=set()
allu=np.array(list(itertools.product([0,1],repeat=9)))
for s in range(n):
    A=(allu@Beta@H.T)%2            # beta(u,h_t)
    ok=~((A*Q[s][None,:]).any(1))
    sols=[tuple(u) for u in allu[ok]]
    cnt.add((len(sols), tuple(ctil(s)) in sols))
print('L3 (count, contains ctil):',cnt)
