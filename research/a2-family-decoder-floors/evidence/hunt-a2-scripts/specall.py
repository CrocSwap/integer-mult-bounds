# HUNT-A2: unit-generic special-locus analysis for the A2 family (run with UNIT=..., PYTHONPATH=..).
# Killed sets K = one class, or a 2-dim subspace (union of 3 classes). For each:
#  rows: special iff d=dim r(K\X)^perp in [1,|S|-1], |S|>=2  (else generic or never)
#  cols b=1: V_K = {(g2,g3)=(n1-n2, n1-n3) in PxP, n_i in r(K cap O_i)^perp} (theta coords); special iff V_K != K^4 and not inside B-locus;
#            if V_K == K^4 and S != {}: z-special, requirement z_{u_k} = -r_k.y, y solving the system (affine in theta).
import pickle, itertools
from a2lib import *
P=(1<<61)-1
def rank_modp(rows,n):
    A=[[int(x.numerator*pow(x.denominator,-1,P))%P for x in r] for r in rows]; rk=0
    for c in range(n):
        p=next((i for i in range(rk,len(A)) if A[i][c]),None)
        if p is None: continue
        A[rk],A[p]=A[p],A[rk]; iv=pow(A[rk][c],-1,P); A[rk]=[x*iv%P for x in A[rk]]
        for i in range(len(A)):
            if i!=rk and A[i][c]:
                f=A[i][c]; A[i]=[(a-f*b)%P for a,b in zip(A[i],A[rk])]
        rk+=1
    return rk
r3v=R[X[2]]
# B-locus in theta coords: g2 = a r1 + b r2, g3 = a r1 + c r3 ; express r3 in (r1,r2)
co3=nullspace([[r1[k],r2[k],-r3v[k]] for k in range(8)],3)[0]; co3=[x/co3[2] for x in co3]  # r3 = co3[0] r1 + co3[1] r2
Bloc=[[Fr(1),Fr(0),Fr(1),Fr(0)],[Fr(0),Fr(1),Fr(0),Fr(0)],[Fr(0),Fr(0),co3[0],co3[1]]]
Bnorm=nullspace(Bloc,4)
def inB(V): return all(dot(n,x)==0 for n in Bnorm for x in V)
def Vsub(Kl):
    Ni=[]
    for i in range(3):
        rows=[R[t] for t in Kl if t in Oset[i]]
        Ni.append(nullspace(rows,8) if rows else [[Fr(int(a==b)) for a in range(8)] for b in range(8)])
    nv=sum(len(n) for n in Ni)+4; rows=[]
    for k in range(8):
        for which in (1,2):
            row=[Fr(0)]*nv
            for m,b_ in enumerate(Ni[0]): row[m]=b_[k]
            o=len(Ni[0])
            if which==1:
                for m,b_ in enumerate(Ni[1]): row[o+m]=-b_[k]
            o+=len(Ni[1])
            if which==2:
                for m,b_ in enumerate(Ni[2]): row[o+m]=-b_[k]
            o+=len(Ni[2])
            if which==1: row[o]=-r1[k]; row[o+1]=-r2[k]
            else: row[o+2]=-r1[k]; row[o+3]=-r2[k]
            rows.append(row)
    proj=[x[-4:] for x in nullspace(rows,nv)]
    proj=[p for p in proj if any(a!=0 for a in p)]
    return nullspace(nullspace(proj,4),4) if proj else []
Oset=[set(o) for o in O]; Xs=set(X)
def zreq(Kl,th):
    g=gvecs(th); S=[i for i in range(3) if X[i] in Kl]
    rows=[R[s]+[-dot(R[s],g[i])] for i in range(3) for s in Kl if s in Oset[i]]
    ns=nullspace(rows,9); part=[x for x in ns if x[8]!=0]
    if not part: return 'none'
    p0=part[0]; homs=[[a-b*x[8]/p0[8] for a,b in zip(x,p0)][:8] for x in ns]
    homs=[hh for hh in homs if any(a!=0 for a in hh)]
    p=[a/p0[8] for a in p0][:8]
    if homs and rank([[ -dot(R[X[k]],hh) for hh in homs] for k in S],len(homs))>0: return 'free'
    return {k:-dot(R[X[k]],p) for k in S}
cl=sorted(cls.items()); seen=set(); sets=[]
for (c1,w1) in cl: sets.append(((c1,),w1))
for a in range(len(cl)):
    for b in range(a+1,len(cl)):
        key=tuple(sorted((cl[a][0],cl[b][0],cl[a][0]^cl[b][0])))
        if key in seen: continue
        seen.add(key); sets.append((key,cl[a][1]|cl[b][1]))
rowspec=[]; colspec=[]; zspec=[]
ths=[tuple(Fr(int(i==e)) for i in range(4)) for e in range(4)]+[(Fr(0),)*4]
gth=[tuple(Fr(x) for x in (3,-7,5,2)),tuple(Fr(x) for x in (-4,1,6,-3))]
for key,w in sets:
    Kl=bits(w); S=[i for i in range(3) if X[i] in Kl]; rest=[t for t in Kl if t not in Xs]
    d=8-rank_modp([R[t] for t in rest],8)
    if d>=1 and len(S)>=2 and d<=len(S)-1: rowspec.append((key,len(Kl),tuple(S),d))
    dims=[8-rank_modp([R[t] for t in Kl if t in Oset[i]],8) for i in range(3)]
    if all(dd<=1 for dd in dims) and not S: continue
    V=Vsub(Kl)
    if len(V)==4:
        if S:
            r=[zreq(Kl,th) for th in gth]
            if all(isinstance(x,dict) for x in r): zspec.append((key,len(Kl),tuple(S)))
        continue
    if V and not inB(V): colspec.append((key,len(Kl),tuple(S),tuple(dims),len(V)))
print(UNIT,'sets',len(sets),'row-special',len(rowspec),rowspec[:5])
print('col theta-special (not in B-locus)',len(colspec),colspec[:10])
print('z-special',len(zspec),zspec[:20])
pickle.dump((rowspec,colspec,zspec),open('specall.pkl','wb'))
