"""B72: pure SAT (cadical153) for B52's support-level relaxation. usage: sat.py n orbit timeout [proof]
Vars x_f (1120 flats). cover each line; each even-ip pair i<j: covered by 0 or >=2 chosen flats (x_f -> OR of others in C_ij);
sum x = n (totalizer); orbit reduction: rep of orbit o chosen, no lower-orbit flat."""
import numpy as np, sys, time, threading
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType
import model as m
F=np.load('F.npy').astype(bool); orb=np.load('orb.npy'); N=len(F); n=int(sys.argv[1]); o=int(sys.argv[2]); TL=float(sys.argv[3])
Eo=(m.G%2==0)
cl=[]
for j in range(112): cl.append([int(f)+1 for f in np.nonzero(F[:,j])[0]])
Fi=F.astype(np.int32); co=Fi.T@Fi  # co[i,j]=#flats containing both
ncl=0
for i in range(112):
  for j in range(i+1,112):
    if Eo[i,j]:
      C=[int(f)+1 for f in np.nonzero(F[:,i]&F[:,j])[0]]
      for f in C:
        cl.append([-f]+[g for g in C if g!=f])
rep=int(np.nonzero(orb==o)[0][0]); cl.append([rep+1])
for f in range(N):
    if orb[f]<o: cl.append([-(f+1)])
enc=CardEnc.equals(lits=list(range(1,N+1)),bound=n,top_id=N,encoding=EncType.totalizer)
cl+=enc.clauses
print("vars",enc.nv,"clauses",len(cl),"lits",sum(map(len,cl)),flush=True)
s=Solver(name='cadical153',bootstrap_with=cl)
t=time.time()
timer=threading.Timer(TL,lambda: s.interrupt()) if False else None
r=s.solve()
print("RESULT n",n,"orbit",o,"SAT" if r else "UNSAT",round(time.time()-t,1),flush=True)
if r:
    mdl=s.get_model(); print("flats",[i for i in range(N) if mdl[i]>0],flush=True)
