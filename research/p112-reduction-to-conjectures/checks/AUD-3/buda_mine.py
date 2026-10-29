# AUD-3 third check of BUDA11 (B),(C),(D),(E): own linear algebra mod p (p=2^31-1) and own F2 ranks; data = TWINSWAP lib raw C, LAB, G.
import sys,os; sys.path.insert(0,'../TWINSWAP'); os.chdir('../TWINSWAP')
import lib
P=2147483647; n=lib.n; C=lib.C; LAB=lib.LAB; G=lib.G
def rref(M):
    M=[[x%P for x in r] for r in M]; piv=[]; r=0; nc=len(M[0]) if M else 0
    for c in range(nc):
        k=next((i for i in range(r,len(M)) if M[i][c]),None)
        if k is None: continue
        M[r],M[k]=M[k],M[r]; iv=pow(M[r][c],P-2,P); M[r]=[x*iv%P for x in M[r]]
        for i in range(len(M)):
            if i!=r and M[i][c]: f=M[i][c]; M[i]=[(a-f*b)%P for a,b in zip(M[i],M[r])]
        piv.append(c); r+=1
    return M[:r],piv
def rank(M): return len(rref(M)[1]) if M else 0
def null(M,nc=8):
    if not M: return [[1 if i==j else 0 for i in range(nc)] for j in range(nc)]
    R,piv=rref(M); free=[c for c in range(nc) if c not in piv]; out=[]
    for f in free:
        v=[0]*nc; v[f]=1
        for i,c in enumerate(piv): v[c]=(-R[i][f])%P
        out.append(v)
    return out
def f2r(vs):
    b=[]
    for v in vs:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return len(b)
Bd=[[1 if (t==s or abs(G[t][s])<1e-9) else 0 for s in range(n)] for t in range(n)]
def bdr(R,A):  # F2 rank of Bd[R,A] via bitmasks
    return f2r([sum(Bd[t][s]<<i for i,s in enumerate(A)) for t in R])
def off(x): return {s for s in range(n) if sum(C[s][i]*x[i] for i in range(8))%P}
# E
print('E: every c_t has a zero coord:',all(any(v==0 for v in C[t]) for t in range(n)), 'n=',n)
# B
okB=True
for t in range(n):
    Z=[s for s in range(n) if Bd[t][s]]
    okB&= rank([C[s] for s in Z])==8 and rank([C[s] for s in Z if s!=t])==7
    okB&= all(rank([C[s] for s in Z if s!=u])==8 for u in Z if u!=t)
    K=null([C[s] for s in Z if s!=t]); okB&= len(K)==1 and rank([K[0],C[t]])==1
print('B ok (incl. kernel of C[Z\\t] = <c_t>):',okB)
# C
from collections import Counter; kinds=Counter(); viol=0
for t in range(n):
    for phi in range(1,512):
        O=[C[s] for s in range(n) if s!=t and bin(phi&LAB[s]).count('1')%2]
        K=null(O)
        if not K: kinds['0']+=1
        elif len(K)==1 and rank([K[0],C[t]])==1: kinds['c_t']+=1
        elif len(K)==1 and sum(1 for v in K[0] if v)==1: kinds['frame']+=1
        else: viol+=1
print('C',dict(kinds),'viol',viol)
# D: frame/frame both weight 8 -> min cost; plus all weights listing
mn=99
for t in range(n):
    Rs=[]
    for i in range(8):
        Of=off([1 if k==i else 0 for k in range(8)])
        for R in (sorted(Of-{t}),sorted(Of|{t})):
            if f2r([LAB[s] for s in R])==8: Rs.append(R)
    for R in Rs:
        for A in Rs: mn=min(mn,bdr(R,A))
print('D min frame/frame cost (both w=8):',mn)
