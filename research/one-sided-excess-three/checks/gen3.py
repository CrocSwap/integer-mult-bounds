# SIX3IND data generator. Independent of SIX/: standard D8+ E8 coordinates (x2 scaled), labels = (1, coords in a Z-basis of E8 mod 2),
# frame = 8 orthogonal root pairs e1+-e2,..., c-coordinates c_j=<r,f_j> only used to derive the frame-stabiliser, directions/pencils from scratch.
import itertools, numpy as np, random, sys
from math import gcd
random.seed(12345)
# E8 roots scaled by 2
R=[]
for i,j in itertools.combinations(range(8),2):
    for si in (2,-2):
        for sj in (2,-2):
            v=[0]*8; v[i]=si; v[j]=sj; R.append(tuple(v))
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: R.append(tuple(s))
R=np.array(R,dtype=np.int64); assert len(R)==240
ip=lambda a,b: int(np.dot(a,b))//4     # true inner product
G=(R@R.T)//4
assert set(np.unique(G))=={-2,-1,0,1,2}
def key(v): return tuple(int(x) for x in v)
# frame
F=[]
for k in range(4):
    for sg in (1,-1):
        v=[0]*8; v[2*k]=2; v[2*k+1]=2*sg; F.append(np.array(v))
F=np.array(F); assert all(ip(F[a],F[b])==(2 if a==b else 0) for a in range(8) for b in range(8))
Fk={key(f) for f in F}|{key(-f) for f in F}
lines=[]; seen=set()
for r in R:
    if key(r) in Fk: continue
    if key(-r) in seen: continue
    seen.add(key(r)); lines.append(r)
lines=np.array(lines); assert len(lines)==112
LI={key(r):i for i,r in enumerate(lines)}
for i,r in enumerate(lines): LI[key(-r)]=i
# labels via Z-basis coordinates
while True:
    idx=random.sample(range(240),8); B=R[idx]
    if abs(round(np.linalg.det(B.astype(float))))==256: break
Binv=np.linalg.inv(B.astype(float))
LAB=[]
for r in lines:
    x=r.astype(float)@Binv; xi=np.rint(x).astype(int); assert np.abs(x-xi).max()<1e-6
    lab=1
    for k in range(8): lab|=(int(xi[k])&1)<<(k+1)
    LAB.append(lab)
assert len(set(LAB))==112
# directions: roots (up to sign), n4, n6 from orthogonal sums
canon=lambda v: max(key(v),key(-np.array(v)))
dirs={}
for r in R: dirs[canon(r)]=1
nr=len(dirs)
orth=[[j for j in range(240) if G[i,j]==0] for i in range(240)]
n4=set(); n6=set()
for i in range(240):
    for j in orth[i]:
        if j>i: n4.add(canon(R[i]+R[j]))
        for k in orth[i]:
            if k>j>i and G[j,k]==0: n6.add(canon(R[i]+R[j]+R[k]))
# sums of 2 orth roots give norm 4 only; 3 orth give norm 6 only (check)
nn=lambda v: int(np.dot(v,v))//4
assert all(nn(np.array(v))==4 for v in n4) and all(nn(np.array(v))==6 for v in n6)
print('dirs: roots',nr,'n4',len(n4),'n6',len(n6),'(expect 120 1080 3360)'); assert (nr,len(n4),len(n6))==(120,1080,3360)
allv=[np.array(v) for v in dirs]+[np.array(v) for v in n4]+[np.array(v) for v in n6]
M=lines@np.array(allv).T      # 112 x nd
offc=(M!=0).sum(axis=0)
LIM=80
out=[]
for d,v in enumerate(allv):
    if offc[d]<=LIM:
        m=0
        for t in np.nonzero(M[:,d])[0]: m|=1<<int(t)
        out.append((1,v,v,m,int(offc[d])))
# A2 pencils
pens={}
for i in range(240):
    for j in range(240):
        if G[i,j]==-1:
            Rk={key(x):k for k,x in enumerate(R)}
            roots=frozenset(Rk[key(x)] for x in (R[i],R[j],R[i]+R[j],-R[i],-R[j],-R[i]-R[j]))
            assert len(roots)==6
            if roots in pens: continue
            gen=((lines@R[i])!=0)|((lines@R[j])!=0)
            pens[roots]=(R[i],R[j],gen)
print('A2 planes',len(pens),'(expect 1120)')
gc=collections=None
import collections
cnt=collections.Counter()
for roots,(a,b,gen) in pens.items():
    c=int(gen.sum()); cnt[c]+=1
    if c<=LIM:
        m=0
        for t in np.nonzero(gen)[0]: m|=1<<int(t)
        out.append((2,a,b,m,c))
print('pencil generic Off counts',dict(cnt))
print('direction counts by |Off| (kind1):',sorted(collections.Counter(o[4] for o in out if o[0]==1).items()))
# frame stabiliser: c-coordinates
C=(lines@F.T)//4   # c_j(r)=<r,f_j>
Cset={tuple(c) for c in C}|{tuple(-c) for c in C}
supports={frozenset(np.nonzero(c)[0]) for c in C if np.count_nonzero(c)==4}
perms=[]
for pi in itertools.permutations(range(8)):
    ok=all(frozenset(pi[j] for j in s) in supports for s in supports)
    if ok: perms.append(pi)
print('support-preserving perms',len(perms),'(expect 1344)')
Cidx={tuple(c):i for i,c in enumerate(C)}
for i,c in enumerate(C): Cidx[tuple(-c)]=i
def act(sign,pi):
    res=[]
    for c in C:
        c2=[0]*8
        for j in range(8): c2[pi[j]]=int(c[j])*sign[j]
        res.append(Cidx[tuple(c2)])
    return res
ident=tuple(range(8))
gens=[]
for j in range(8):
    sg=[1]*8; sg[j]=-1; gens.append(act(sg,ident))
for pi in random.sample(perms,6): gens.append(act([1]*8,pi))
# closure to verify group order
gt=[tuple(g) for g in gens]; seenp={tuple(range(112))}; fr=[tuple(range(112))]
while fr:
    nf=[]
    for p in fr:
        for g in gt:
            q=tuple(g[x] for x in p)   # compose
            if q not in seenp: seenp.add(q); nf.append(q)
    fr=nf
print('group order on lines',len(seenp),'(expect 172032)')
# invariance: each generator must permute direction Off sets among the list
offsets={o[3] for o in out}
def mapm(m,g):
    r=0
    for t in range(112):
        if m>>t&1: r|=1<<g[t]
    return r
for g in gens:
    for o in out: assert mapm(o[3],g) in offsets
print('direction-list Off sets invariant under generators: OK')
with open('data3.txt','w') as f:
    f.write(' '.join(map(str,LAB))+'\n')
    f.write('%d\n'%len(gens))
    for g in gens: f.write(' '.join(map(str,g))+'\n')
    f.write('%d\n'%len(out))
    for kind,a,b,m,c in out:
        f.write('%d %s %s %d %d %d\n'%(kind,' '.join(map(str,a)),' '.join(map(str,b)),m&((1<<64)-1),m>>64,c))
print('wrote data3.txt',len(out))
