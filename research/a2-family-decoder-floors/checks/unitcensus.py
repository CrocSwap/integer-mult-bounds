# Unit-generic structural census for the A2 family (UNIT env). All exact (Fractions; ranks mod 2^31-1, exact by the Hadamard note below).
# (R) row side: classes by (|O∩X|, rank r(O\X)); normals of rank-7 classes; X-avoiding classes must have rank 8 (=> only e9).
# (C) column side off X: S_U = {(w,g2,g3): r_s.w = g_i (r1.r_s) on U∩O_{u_i}}, info (dimS, dimK, proj); generic-killable classes; co-killable 2-dim subspaces.
import sys,itertools,collections
from a2lib import *
X=find_a2(); print(UNIT,'v',v,'X',X)
E6=[s for s in range(v) if all(dot(R[s],R[x])==0 for x in X)]
# spanning checks
for u in X:
    Ou=[s for s in range(v) if s not in X and dot(R[s],R[u])==0 and s not in E6]
    print(' span O_u\\E6',rank([R[s] for s in Ou],8),'(7)', 'lines non-orth to all of X off X:',sum(1 for s in range(v) if s not in X and all(dot(R[s],R[x])!=0 for x in X)))
C=collections.Counter(); rk7=[]
for co,w in cls.items():
    O=bits(w); S=tuple(t for t in O if t in X)
    ns=nullspace([R[t] for t in O if t not in X],8); rk=8-len(ns)
    C[(len(S),rk)]+=1
    if rk<8: rk7.append((co,S,len(O),[str(a) for a in ns[0]] if len(ns)==1 else len(ns)))
print('row census (|S|,rank r(O\\X)):',sorted(C.items()))
for t in rk7: print('  rank<8:',t)
Ri=[[int(2*x) for x in r] for r in L]; r1=Ri[X[0]]
idot=lambda a,b: sum(x*y for x,y in zip(a,b))
rows={}
for s in range(v):
    if s in X: continue
    ii=[i for i in range(3) if idot(Ri[X[i]],Ri[s])==0]; i=ii[0]; g=[0,0]; c=idot(r1,Ri[s])
    if len(ii)>1: assert c==0
    if i==1: g[0]=-c
    if i==2: g[1]=-c
    rows[s]=Ri[s]+g
p=2**31-1
# Hadamard note: the integer rows used with rkp have entries <= 4 in absolute value and 10 columns; each row has squared norm <= 24 (doubled root: 8; one g-entry: <= 16), so every minor is <= 24^5 < 2^31 - 1
# in absolute value and the ranks mod p = 2^31 - 1 are EXACT (equal to the ranks over Q).
def rkp(M,n):
    M=[[x%p for x in r] for r in M]; r=0
    for c in range(n):
        q=next((i for i in range(r,len(M)) if M[i][c]),None)
        if q is None: continue
        M[r],M[q]=M[q],M[r]; inv=pow(M[r][c],p-2,p); M[r]=[x*inv%p for x in M[r]]
        for i in range(len(M)):
            if i!=r and M[i][c]:
                f=M[i][c]; M[i]=[(a-f*b)%p for a,b in zip(M[i],M[r])]
        r+=1
    return r
def info(U):
    M=[rows[s] for s in U]; r=rkp(M,10); rg=rkp([x[:8] for x in M],8)
    dimS=10-r; dimK=8-rg; return dimS,dimK,dimS-dimK
single={co:info([s for s in bits(w) if s not in X]) for co,w in cls.items()}
print('col off-X single info:',collections.Counter(single.values()))
gen=[co for co in cls if single[co][2]==2]
print('generic-gamma killable:',[(co,len(bits(cls[co])),[t for t in bits(cls[co]) if t in X],single[co]) for co in gen])
gram=[co for co in cls if single[co][1]>0]
print('Gram-deficient (eta=0) classes:',len(gram))
good=[]
gs=set(gen)
for a,b in itertools.combinations(gen,2):
    c3=a^b
    if c3 in gs and c3>b:
        U=sorted(set(s for co in (a,b) for s in bits(cls[co]) if s not in X)); t=info(U)
        if t[2]==2: good.append((a,b,c3,t))
print('co-killable 2-dim off cocycle:',good)
for tri in itertools.combinations(gen,3):
    U=sorted(set(s for co in tri for s in bits(cls[co]) if s not in X)); t=info(U)
    if t[2]==2: print(' 3 gen classes co-killable:',tri,t)
