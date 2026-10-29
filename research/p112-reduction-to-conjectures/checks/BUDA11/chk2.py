# BUDA11 impl 2: independent E8 rebuild (AUDIT-IMP ind_e8.py objects: L doubled coords, F0 frame, LAB, beta), own exact elimination.
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../AUDIT-IMP'))
exec(open('ind_e8.py').read().split("# directions:")[0])
from fractions import Fraction as Fr
def rref_null(rows,d):
    M=[[Fr(x) for x in r] for r in rows]; piv=[]; r=0
    for c in range(d):
        p=next((i for i in range(r,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]; pv=M[r][c]; M[r]=[x/pv for x in M[r]]
        for i in range(len(M)):
            if i!=r and M[i][c]!=0:
                f=M[i][c]; M[i]=[a-f*b for a,b in zip(M[i],M[r])]
        piv.append(c); r+=1
    free=[c for c in range(d) if c not in piv]; basis=[]
    for f in free:
        x=[Fr(0)]*d; x[f]=Fr(1)
        for i,c in enumerate(piv): x[c]=-M[i][f]
        basis.append(x)
    return basis
rank=lambda rows,d: d-len(rref_null(rows,d))
par=lambda a,b: rank([list(a),list(b)],8)<=1
wt=lambda S: rk([LAB[s] for s in S])
Z=lambda t: [s for s in range(v) if s==t or ip(L[s],L[t])==0]
# (A) e_t outside col of the 112x8 line matrix
for t in range(v): assert rank([list(L[s])+[1 if s==t else 0] for s in range(v)],9)==9
print('A ok')
# (B) q = My + y2 e_t' (M = line matrix) vanishing on Z_t: full solution spaces
cnt=Counter()
for t in range(v):
    Zt=Z(t)
    for tp in range(v):
        N=rref_null([list(L[s])+[4 if s==tp else 0] for s in Zt],9)
        for x in N:
            q=[sum(L[s][i]*x[i] for i in range(8))+(4*x[8] if s==tp else 0) for s in range(v)]
            S=[s for s in range(v) if q[s]!=0]; ww=wt(S)
            if ww==8: cnt['w8',tp==t, len(N)==1 and par(x[:8],L[t])]+=1
            else: cnt['w',ww,len(N)]+=1
print('B solution kinds',dict(cnt))
# (C) x with Off(x)\{t} inside a hyperplane (phi): kernel classification
kinds=Counter(); viol=0
for t in range(v):
    for phi in range(1,512):
        O=[s for s in range(v) if s!=t and bin(phi&LAB[s]).count('1')%2]
        N=rref_null([list(L[s]) for s in O],8)
        if not N: kinds['0']+=1; continue
        if len(N)==1 and par(N[0],L[t]): kinds['root_t']+=1
        elif len(N)==1 and any(par(N[0],f) for f in F0): kinds['frame']+=1
        else: viol+=1; print('VIOL',t,phi,len(N))
print('C kinds',dict(kinds),'viol',viol)
# (D) frame/frame terms cost (F2 rank of beta matrix) >= 8 at weight 8; control root column
def bdr(R,A):
    return rk([sum(1<<j for j,s in enumerate(A) if beta(LAB[r],LAB[s])) for r in R])
mn=99; c7=0
for t in range(v):
    Rs=[]
    for f in F0:
        Of=set(s for s in range(v) if ip(L[s],f)!=0)
        for R in (sorted(Of-{t}),sorted(Of|{t})):
            if wt(R)==8: Rs.append(R)
    for R in Rs:
        for A in Rs: mn=min(mn,bdr(R,A))
    A=[s for s in range(v) if s!=t and ip(L[s],L[t])!=0]
    c7+=sum(1 for R in Rs if bdr(R,A)==7)
print('D min frame/frame cost',mn,'control cost-7 (frame,root) pairs',c7)
print('E every line has a frame coordinate 0:',all(sum(1 for f in F0 if ip(L[t],f)!=0)<8 for t in range(v)))
