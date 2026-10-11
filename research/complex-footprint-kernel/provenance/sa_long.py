import sys
from kern5 import *
seed=int(sys.argv[1]);iters=int(sys.argv[2])
w=load();w['R']=w['report']['R'];col,first=setup(w);R=len(col)
cand={}
for h,F in first.items():
    for E in subspaces(F):cand.setdefault(E,[]).append(h)
C=np.zeros((v,R))
for h in range(R):
    for t,x in col[h].items():C[t,h]=float(x)
Es=[E for E,G in cand.items() if len(G)>=2 and len(G)-np.linalg.matrix_rank(C[:,G])>0]
init=pickle.load(open('kern4_best.pkl','rb'))
best,asg=sa(col,first,C,cand,Es,iters=iters,seed=seed,init=init,T0=0.5)
print('seed',seed,'best',best,flush=True)
pickle.dump((best,asg),open('sa_long_%d.pkl'%seed,'wb'))
