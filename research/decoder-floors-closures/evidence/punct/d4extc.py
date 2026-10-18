"""PUNCT7: chunked d4ext.py. usage d4extc.py P k n : as d4ext.py (case d_0 >= 4 at p = P; classes of d>=4 kernels of root 0 with |A| <= P mod Stab(0);
every extension by P-|A| lines; exact relaxF by integer min-cost flow), but only extensions with index = k mod n. Prints per class min and argmin."""
import sys, pickle, itertools, time
sys.path.insert(0,'/Users/mason/repo_clones/intmult-work/cards/PUNCT5')
from relaxFx import relaxF_exact
from kernels import kernels
from p4lib import G
P,k,n=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
D=pickle.load(open('kernels.pkl','rb')); PER=D['PER']
best,ks=kernels(0,4,slack=P-45); ks=[x for x in ks if len(x)<=P]
stab=[PER[a] for a in range(120) if G[0,a]==0]
rem=set(ks); reps=[]
while rem:
    x=rem.pop(); orb={x}; fr=[x]
    while fr:
        nf=[]
        for y in fr:
            for P_ in stab:
                w=frozenset(P_[t] for t in y)
                if w not in orb: orb.add(w); nf.append(w)
        fr=nf
    rem-=orb; reps.append(min(orb,key=sorted))
reps.sort(key=lambda r:(len(r),sorted(r)))
print('d>=4 kernels <=',P,len(ks),'classes',len(reps),[len(r) for r in reps],flush=True)
t0=time.time()
for ci,A in enumerate(reps):
    b=P-len(A); rest=[t for t in range(120) if t not in A]; best=None; cnt=0
    for i,E in enumerate(itertools.combinations(rest,b)):
        if i%n!=k: continue
        v,h=relaxF_exact(sorted(set(A)|set(E))); cnt+=1
        if best is None or v<best[0]: best=(v,E)
    print('class',ci,'|A|',len(A),'budget',b,'chunk',k,'/',n,'#S',cnt,'min exact relaxF',best,round(time.time()-t0),flush=True)
