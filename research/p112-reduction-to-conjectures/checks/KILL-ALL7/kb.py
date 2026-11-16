# impl B (independent): own E8 roots, own Z-basis (greedy unimodular), own labels, own flats/orbits/candidates; numpy prefilter.
# For each W-orbit rep A: B's with span(qualifying h) >= 7, and (602 variant) >= 8 allowing one extra line l0.
import itertools, numpy as np, sys
R=[]
for i,j in itertools.combinations(range(8),2):
    for s in (2,-2):
        for u in (2,-2):
            v=[0]*8; v[i]=s; v[j]=u; R.append(v)
for m in range(256):
    v=[1 if m>>k&1 else -1 for k in range(8)]
    if v.count(-1)%2==0: R.append(v)
R=np.array(R); Lines=R[[i for i in range(240) if tuple(R[i])>tuple(-R[i])]]; n=len(Lines); assert n==120
G=Lines@Lines.T//4
# greedy Z-basis: pick roots until Gram det 1 with rank 8
basis=[]
for t in range(n):
    if np.linalg.matrix_rank(Lines[basis+[t]])==len(basis)+1:
        basis.append(t)
        if len(basis)==8:
            if round(abs(np.linalg.det(G[np.ix_(basis,basis)])))!=1: basis.pop()
            else: break
assert len(basis)==8
Bm=Lines[basis].astype(float); X=np.linalg.solve(Bm.T,Lines.T.astype(float)).T; Xi=np.rint(X).astype(int); assert np.allclose(X,Xi)
lab=[1|sum(((int(Xi[t,k])%2)<<(k+1)) for k in range(8)) for t in range(n)]; assert len(set(lab))==120
bits=np.array([[(l>>k)&1 for k in range(9)] for l in lab])
F=set()
for a in range(1,512):
    for b in range(a+1,512):
        av=np.array([(a>>k)&1 for k in range(9)]); bv=np.array([(b>>k)&1 for k in range(9)])
        F.add(tuple(np.nonzero(((bits@av)%2==0)&((bits@bv)%2==0))[0]))
F=sorted(F); nF=len(F); Fm=np.zeros((nF,n),bool)
for i,f in enumerate(F): Fm[i,list(f)]=True
print('flats',nF,'max',Fm.sum(1).max())
# reflections -> orbits
LI={tuple(l):i for i,l in enumerate(Lines)}
def cn(v): v=tuple(v); return v if v>tuple(-x for x in v) else tuple(-x for x in v)
perms=[np.array([LI[cn(l-((l@s)//4)*s)] for l in Lines]) for s in Lines[basis]]
key={f:i for i,f in enumerate(F)}; orb=[-1]*nF; reps=[]
for i in range(nF):
    if orb[i]>=0: continue
    reps.append(i); orb[i]=i; st=[i]
    while st:
        j=st.pop()
        for p in perms:
            k=key[tuple(sorted(p[list(F[j])]))]
            if orb[k]<0: orb[k]=i; st.append(k)
print('orbits',len(reps))
# candidates: roots; A2 planes (pairs at 60 deg, as 2 vectors); E6A1 = plane vector orth to one root of the A2
C=[]; seenA2=set()
for i in range(n): C.append([Lines[i]])
for i,j in itertools.combinations(range(n),2):
    if abs(G[i,j])==1:
        k=LI[cn(Lines[i]-np.sign(G[i,j])*Lines[j])]; key3=tuple(sorted((i,j,k)))
        if key3 in seenA2: continue
        seenA2.add(key3); a,b,c=(Lines[x] for x in key3); C.append([a,b])
        for w,(x,y) in ((c,(a,b)),(a,(b,c)),(b,(a,c))): C.append([(y@w)*x-(x@w)*y])
OFFc=np.array([np.any(np.array([v for v in vs])@Lines.T!=0,axis=0) for vs in C]); print('cands',len(C),sorted(set(OFFc.sum(1))))
def rk(ix):
    b=[]
    for t in ix:
        v=lab[t]
        for y in b: v=min(v,v^y)
        if v: b.append(v)
    return len(b)
# check: no candidate (so no h, by T3) has Off inside two flats  [no parallel pairs]
mode=sys.argv[1] if len(sys.argv)>1 else 'plain'
import os
NS=int(os.environ.get("KB_NS","1")); SL=int(os.environ.get("KB_SL","0"))   # optional slicing of the orbit-rep loop (chunking for the 20-min cap)
for r in [x for j,x in enumerate(reps) if j%NS==SL]:
    A=Fm[r]; OA=OFFc&~A; need=OA.sum(1)-(36 if mode=='plain' else 37)
    cnt=Fm.astype(np.float32)@OA.T.astype(np.float32)          # |Off_c\A ∩ B|
    Bs,Cs=np.nonzero(cnt>=need[None,:]-0.5)
    out={}; two=0
    for B,c in zip(Bs,Cs):
        Lx=np.nonzero(OA[c]&~Fm[B])[0]
        if len(Lx)==0: two+=1
        if mode=='plain':
            if len(Lx)<=36 and rk(Lx)<=7: out.setdefault(B,{}).setdefault(-1,[]).append(c)
        else:
            if len(Lx)<=36 and rk(Lx)<=7: out.setdefault(B,{}).setdefault(-1,[]).append(c)
            elif rk(Lx)==8:
                for l in Lx:
                    if rk([t for t in Lx if t!=l])<=7: out.setdefault(B,{}).setdefault(l,[]).append(c)
    thr=7 if mode=='plain' else 8; N=[]
    for B,d in out.items():
        base=[v for c in d.get(-1,[]) for v in C[c]]
        best=np.linalg.matrix_rank(np.array(base)) if base else 0
        for l,cs in d.items():
            if l>=0: best=max(best,np.linalg.matrix_rank(np.array(base+[v for c in cs for v in C[c]])))
        if best>=thr: N.append((B,int(Fm[B].sum()),int((A&Fm[B]).sum()),int(best)))
    print('rep',r,'|A|',int(A.sum()),'two-flat covers',two,'N:',N,'|A u N|',int((A|np.any(Fm[[x[0] for x in N]],0)).sum()) if N else int(A.sum()),flush=True)
