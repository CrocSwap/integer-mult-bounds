# AUDIT-IQ: D4 (all pairs), D6 (all pairs), E7 failing type. Independent of gen.py/orbits.
import itertools, numpy as np, sys, os
from collections import Counter
from satB import *
from lib import nonorth_clique as clique_det
def Dn(n):
    Ls=[]
    for i,j in itertools.combinations(range(n),2):
        for s in (1,-1):
            v=[0]*n; v[i]=1; v[j]=s; Ls.append(v)
    return np.array(Ls)
def normals_of(Lm,dim,vals=(0,1,-1,2,-2)):
    out=set()
    for v in itertools.product(vals,repeat=dim):
        v=np.array(v)
        if not v.any(): continue
        g=np.gcd.reduce(np.abs(v)); v=v//g; f=np.nonzero(v)[0][0]; v=v if v[f]>0 else -v
        Z=Lm[(Lm@v)==0]
        if len(Z) and np.linalg.matrix_rank(Z.astype(float))==dim-1: out.add(tuple(int(x) for x in v))
    return sorted(out)
def allpairs(Lm,Nm,name,brute_cap=22):
    G=(Lm@Lm.T).tolist(); Mk=(Nm@Lm.T)!=0; Ds={}
    for a in range(len(Nm)):
        for b in range(a,len(Nm)):
            if Nm[a]@Nm[b]==0: continue
            D=tuple(np.nonzero(Mk[a]&Mk[b])[0]); Ds.setdefault(D,(a,b))
    print(name,'lines',len(Lm),'normals',len(Nm),'distinct nonorth D',len(Ds),flush=True)
    return G,Ds
mode=sys.argv[1]; FULL=len(sys.argv)>2 and sys.argv[2]=='full'
ok=True
if mode=='D4':
    Lm=Dn(4); Nm=np.array(normals_of(Lm,4)); print('D4 normal supports',Counter(int((v!=0).sum()) for v in Nm))
    G,Ds=allpairs(Lm,Nm,'D4'); m=[]
    for D in Ds:
        x=brute_mr(G,list(D),cap=22)
        if x is None: x=('>=3' if solve(G,list(D),2,seed=1)==('UNSAT',True) else 'FAIL')
        m.append(x)
    c=Counter(m); print('D4 mr2 over ALL nonorth pairs',c)
    ok=len(Ds)==192 and set(c)<= {3,'>=3'} and c[3]+c['>=3']==192 and Counter(int((v!=0).sum()) for v in Nm)=={1:4,2:12,4:8}
    print('PASS D4: 24 normals, 192 distinct nonorthogonal D-sets, every one has mr2 >= 3 (so 4 terms x 3 = 12)' if ok else 'FAIL D4')
if mode=='D6':
    Lm=Dn(6); Nm=np.array(normals_of(Lm,6)); G,Ds=allpairs(Lm,Nm,'D6')
    small=sorted(Ds,key=len); low=Counter(); target={10,15,16,19}; got=set()
    for D in small:
        D=list(D)
        if len(D)>19: break
        if len(D)<=8:
            m=brute_mr(G,D,cap=24)
            if m is not None and m<5: low[(len(D),m,'brute')]+=1
        elif FULL or (len(D) in target and len(D) not in got):
            if solve(G,D,4,seed=1)==('SAT',True): low[(len(D),'<=4','SATverified')]+=1; got.add(len(D))
    print('D6 nonorth D-sets (|D|<=19 ONLY) with mr2<5:',dict(low))
    ok=low[(7,3,'brute')]>=1 and got==target and (not FULL or (low[(7,3,'brute')]==240 and len(Ds)==26096))
    print('PASS D6: counterexamples to the per-term claim (|D|=7 mr2=3; SAT-verified rank<=4 at |D|=10,15,16,19); scan limited to |D|<=19' if ok else 'FAIL D6')
if mode=='E7':
    Z=np.load(sys.argv[2]); L8=Z['L']; N=Z['N']; E7=L8[(L8@L8[0])==0]; print('E7 lines',len(E7))
    N=N[(N@L8[0])==0]
    keep=[k for k in range(len(N)) if np.linalg.matrix_rank(E7[(E7@N[k])==0].astype(float))==6]; N=N[keep]
    G=((E7@E7.T)//4).tolist(); Mk=(N@E7.T)!=0
    n1s=np.nonzero((~Mk).sum(1)==36)[0]; seen=set(); out=[]; npairs=0
    for a in n1s:
        nz=(N@N[a])!=0; sz=(Mk[a][None,:]&Mk).sum(1)
        for b in np.nonzero(nz&(sz<=12))[0]:
            D=tuple(np.nonzero(Mk[a]&Mk[b])[0]); npairs+=1
            if D in seen: continue
            seen.add(D)
            if len(out)<4:
                Dl=list(D); dr=rk2([sum((1 if G[t][s]%2==0 else 0)<<i for i,s in enumerate(Dl)) for i2,t in enumerate(Dl)])
                S=clique_det(G,Dl,5)
                out.append((len(D),dr,solve(G,Dl,5,S),solve(G,Dl,4,clique_det(G,Dl,4))))
                print('E7 type |D|,dense,rank5,rank4:',out[-1],flush=True)
    print('E7 normals',len(N),'E6-flat normals',len(n1s),'(n1,n2) pairs with |D|<=12',npairs,'distinct D',len(seen))
    ok=len(out)==4 and all(o[0]==11 and o[1]==5 and o[2]==('SAT',True) and o[3]==('UNSAT',True) for o in out)
    print('PASS E7: |D|=11 nonorthogonal type has mr2 = 5 (rank 5 SAT verified, rank 4 UNSAT DRAT-verified) -- per-term claim fails for E7' if ok else 'FAIL E7')
sys.exit(0 if ok else 1)
