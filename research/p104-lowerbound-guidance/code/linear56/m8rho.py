"""LINEAR56 m8rho.py: rho_A, rho_B (GF(2^16) rank = lower bound w.h.p. exact; Rado greedy = upper bound) on the 8-row tight-A family."""
import numpy as np, itertools, sys
sys.path.insert(0,'../double56'); from lin import inv4
import rho as R
from lcore import *
T=np.load('tightX.npy'); tl={}
for x in T: tl.setdefault(tuple(x%2),x)
keys=sorted(tl); Tset=set(map(tuple,T)); seen={}
for sub in itertools.combinations(range(16),8):
    X=np.array([tl[keys[i]] for i in sub]).T; Xi=inv4(X)
    if Xi is None: continue
    Y=((Xi@G)%4).T; W=C104@X; V=C104@Y
    nt=sum(tuple(Y[:,k]) in Tset or tuple((-Y[:,k])%4) in Tset for k in range(8))
    if seen.get(nt,0)>=3: continue
    seen[nt]=seen.get(nt,0)+1
    rb,ra,RB,RA=R.rhos(W,V,Q,2); ub_b,_=R.rado_ub(RB,104); ub_a,_=R.rado_ub(RA,104)
    print('ntightB',nt,'cost',cost(W,V),'f',f_val(*UV(W,V))[0],'rhoA',ra,'(ub',ub_a,') rhoB',rb,'(ub',ub_b,') sum',ra+rb,flush=True)
