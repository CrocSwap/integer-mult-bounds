# F3 facts (special 3-circuits): analysis of the minimal leftovers of root targets (left_root.txt), transported to all 112 roots by G.
# (numpy re-implementation of the first version: same quantities (a)-(f); the rank / 4-flat tests are G-invariant, so they are done on the base sets.)
import numpy as np, itertools
from collections import Counter, defaultdict
import p112 as p
G=np.load('G.npy'); inv={g:i for i,g in enumerate(p.P)}; PL=p.PL; Pidx=np.array(p.P)
r0=p.P[0]; r0p=inv[r0]
L=[]
for line in open('left_root.txt'):
    if line.startswith('#'): print(line.strip()); continue
    lo,hi=line.split(); L.append(int(lo,16)|(int(hi,16)<<64))
pcnt=lambda x:bin(x).count('1')
L=sorted(set(L),key=pcnt)
M64=(1<<64)-1
mins=[]; _lo=np.zeros(len(L),dtype=np.uint64); _hi=np.zeros(len(L),dtype=np.uint64); _n=0
for x in L:
    xl=np.uint64(x&M64); xh=np.uint64(x>>64)
    if _n and (((_lo[:_n]&~xl)==0)&((_hi[:_n]&~xh)==0)).any(): continue
    mins.append(x); _lo[_n]=xl; _hi[_n]=xh; _n+=1
print('distinct leftovers',len(L),' minimal',len(mins),' size hist of minimal',sorted(Counter(map(pcnt,mins)).items()))
assert all(not (x>>r0p)&1 for x in mins)
def lines(x): return [i for i in range(112) if x>>i&1]
rank=lambda ls:p.f2rank([PL[i] for i in ls])
print('(a) min |L| =',min(map(pcnt,mins)))
m4=[x for x in mins if pcnt(x)==4]; print('(b) #4-leftovers per root',len(m4),' ranks',Counter(rank(lines(x)) for x in m4))
rep={}
for g in G:
    r=int(g[r0])
    if r not in rep: rep[r]=g
    if len(rep)==112: break
assert len(rep)==112
roots=sorted(rep)
# column permutation of the 112 P-bits induced by each coset representative
perms={r:np.array([inv[int(rep[r][Pidx[i]])] for i in range(112)]) for r in roots}
N=len(mins)
Bm=np.zeros((N,112),dtype=np.uint8)
for k,x in enumerate(mins):
    for i in lines(x): Bm[k,i]=1
sz=np.array([pcnt(x) for x in mins])
w=np.uint64(1)<<np.arange(64,dtype=np.uint64)
def pack(Y):
    return (Y[:,:64].astype(np.uint64)*w).sum(1,dtype=np.uint64),(Y[:,64:].astype(np.uint64)*w[:48]).sum(1,dtype=np.uint64)
keys=[];rid=[]
for r in roots:
    Y=np.zeros_like(Bm); Y[:,perms[r]]=Bm
    lo,hi=pack(Y); keys.append(np.stack([lo,hi,sz.astype(np.uint64)],1)); rid.append(np.full(N,inv[r],dtype=np.int64))
K=np.concatenate(keys); R=np.concatenate(rid)
# distinct (set, root) pairs, then roots per set
U=np.unique(np.concatenate([K,R[:,None].astype(np.uint64)],1),axis=0)
S_,cnt=np.unique(U[:,:3],axis=0,return_counts=True)
n_by={}
for s in np.unique(S_[:,2]): n_by[int(s)]=int(cnt[S_[:,2]==s].max())
print('max #roots per minimal leftover set, by size:',dict(sorted(n_by.items())))
# (c) 5-sets
def ints(lo,hi): return int(lo)|(int(hi)<<64)
roots_of=defaultdict(set)
for lo,hi,s,r in U[U[:,2]<=5]: roots_of[(ints(lo,hi),int(s))].add(int(r))
served=defaultdict(set)
for (x,s),rs in roots_of.items():
    if s==5: served[x]|=rs
    else:
        for l in range(112):
            if not x>>l&1: served[x|1<<l]|=rs
best5=max(len({r for r in rs if not X>>r&1}) for X,rs in served.items())
print('(c) max #roots r not in X served by a 5-set X:',best5)
print('(d) 6-set bound 15*n4+6*n5+n6 =',15*n_by[4]+6*n_by[5]+n_by[6])
# (e),(f): 4-flats
def span(vs):
    S={0}
    for v in vs:
        if v not in S: S|={s^v for s in S}
    return S
def flats4_containing(vs):
    S=span(vs); k=len(S).bit_length()-1
    if k>4: return []
    if k==4: return [frozenset(S)]
    out=set()
    def ext(S):
        if len(S)==16: out.add(frozenset(S)); return
        for v in range(1,512):
            if v not in S: ext(S|{s^v for s in S})
    if k==3:
        for v in range(1,512):
            if v not in S: out.add(frozenset(S|{s^v for s in S}))
    else: ext(S)
    return list(out)
lam=lambda F: sum(1<<i for i in range(112) if PL[i] in F)
def img(r,x):
    y=0
    for i in lines(x): y|=1<<perms[r][i]
    return y
qual=[]   # base sets with rank<=4 (type A) or with a line l whose removal leaves rank<=4 (type B), size<=9; ranks are invariant under G (label-linear)
for x in mins:
    if pcnt(x)>9: continue
    ls=lines(x); a=rank(ls)<=4
    bl=[l for l in ls if rank([i for i in ls if i!=l])<=4]
    if a or bl: qual.append((x,a,bl))
print('base minimal sets of type A/B:',len(qual))
A=defaultdict(set); B=defaultdict(set)
for x,a,bl in qual:
    for r in roots:
        ri=inv[r]; pm=perms[r]
        ls=[int(pm[i]) for i in lines(x)]
        if a:
            for F in flats4_containing([PL[i] for i in ls]): A[F].add(ri)
        for l in bl:
            lm=int(pm[l]); rest=[i for i in ls if i!=lm]
            for F in flats4_containing([PL[i] for i in rest]):
                if PL[lm] not in F: B[(F,lm)].add(ri)
bestE=0
for F,rs in A.items():
    X=lam(F); bestE=max(bestE,len({r for r in rs if not X>>r&1}))
print('(e) max #roots outside X served, X = 4-flat set:',bestE, ' #4-flats serving some root:',len(A))
bestF=bestE
# keys (F,l), l outside F: not in B -> served set is A[F]; the max over such l is <= max_F |A[F]\X_F| (some l outside A[F] and F always exists)
for (F,l),v in B.items():
    X=lam(F)|1<<l
    rs=A.get(F,set())|v
    bestF=max(bestF,len({r for r in rs if not X>>r&1}))
print('(f) max #roots outside X served, X = 4-flat set + 1 line:',bestF)
