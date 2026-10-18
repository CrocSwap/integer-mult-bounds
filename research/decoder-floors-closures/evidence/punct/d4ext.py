"""PUNCT5: case d_0 >= 4 at p = P (46..48): S ⊇ a d>=4 kernel of root 0 (size <= P). Classes of such kernels mod Stab(0); for each rep A
and every extension by P-|A| further lines (all subsets when P-|A| <= 1, else reported), exact relaxF (integer min-cost flow).
Lower bound valid for every decoder with >= 8 terms after merging."""
import sys, pickle, itertools, time
sys.path.insert(0,'/Users/mason/repo_clones/intmult-work/cards/PUNCT5')
from relaxFx import relaxF_exact
from kernels import kernels
from p4lib import G
P=int(sys.argv[1])
D=pickle.load(open('kernels.pkl','rb')); PER=D['PER']
best,ks=kernels(0,4,slack=P-45); ks=[k for k in ks if len(k)<=P]
stab=[PER[a] for a in range(120) if G[0,a]==0]
rem=set(ks); reps=[]
while rem:
    k=rem.pop(); orb={k}; fr=[k]
    while fr:
        nf=[]
        for x in fr:
            for P_ in stab:
                y=frozenset(P_[t] for t in x)
                if y not in orb: orb.add(y); nf.append(y)
        fr=nf
    rem-=orb; reps.append(k)
print('d>=4 kernels <=',P,len(ks),'classes',len(reps),sorted(len(r) for r in reps),flush=True)
for A in reps:
    b=P-len(A); rest=[t for t in range(120) if t not in A]; vals=[]
    for E in itertools.combinations(rest,b):
        v,h=relaxF_exact(sorted(set(A)|set(E))); vals.append(v)
    print('|A|',len(A),'budget',b,'#S',len(vals),'min exact relaxF',min(vals),flush=True)
