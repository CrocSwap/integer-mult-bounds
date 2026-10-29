# SERVE3 build: convert LEFT22 impl-B pickles (B's own E8/labels) into bitmask tables in SERVE2's line labelling.
import numpy as np, itertools, pickle, sys
sys.path.insert(0,'.')
# --- SERVE2 world (copied from setup2.py) ---
R=[]
for i,j in itertools.combinations(range(8),2):
    for a in (2,-2):
        for b in (2,-2):
            v=[0]*8; v[i]=a; v[j]=b; R.append(tuple(v))
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: R.append(s)
R=np.array(R); key=lambda v: max(tuple(v),tuple(-v))
L=np.array(sorted({key(v) for v in R}))
Bm=np.array([[1,-1,-1,-1,-1,-1,-1,1],[2,2,0,0,0,0,0,0],[-2,2,0,0,0,0,0,0],[0,-2,2,0,0,0,0,0],[0,0,-2,2,0,0,0,0],[0,0,0,-2,2,0,0,0],[0,0,0,0,-2,2,0,0],[0,0,0,0,0,-2,2,0]])
C2=np.rint(np.linalg.solve(Bm.T.astype(float),L.T.astype(float)).T).astype(int)
lab2=[1|sum(int(C2[t][k]%2)<<(k+1) for k in range(8)) for t in range(120)]
dat=open('data.txt').read().split('\n'); assert [int(x) for x in dat[0].split()]==lab2   # same labels as the file s2.c uses
perm=[[int(x) for x in dat[1+g].split()] for g in range(8)]
pos={key(v):t for t,v in enumerate(L)}
def canon(c):
    for x in c:
        if x: return tuple(c) if x>0 else tuple(-np.array(c))
c2pos={canon(C2[t]):t for t in range(120)}
# --- B world (copied from B.py) ---
edges=[(1,3),(3,4),(4,5),(5,6),(6,7),(7,8),(2,4)]
Ca=2*np.eye(8,dtype=int)
for a,b in edges: Ca[a-1,b-1]=Ca[b-1,a-1]=-1
def refl(x,i):
    y=x.copy(); y[i]-=int(x@Ca[:,i]); return y
roots={tuple(np.eye(8,dtype=int)[i]) for i in range(8)}; fr=list(roots)
while fr:
    nf=[]
    for r in fr:
        for i in range(8):
            y=tuple(refl(np.array(r),i))
            if y not in roots: roots.add(y); nf.append(y)
    fr=nf
roots=sorted(roots); lines=[]; seen=set()
for r in roots:
    if tuple(-np.array(r)) in seen: continue
    seen.add(r); lines.append(np.array(r))
LA=np.array(lines); G=LA@Ca@LA.T
labB=[1+sum(int(LA[t][k]%2)<<(k+1) for k in range(8)) for t in range(120)]
# map B line index -> SERVE2 line index via coefficient vector (up to sign); verify bijection, Gram, labels
mp=[c2pos[canon(LA[t])] for t in range(120)]
assert sorted(mp)==list(range(120))
assert all(labB[t]==lab2[mp[t]] for t in range(120))
IP2=(L@L.T)//4
assert all(abs(G[a,b])==abs(IP2[mp[a],mp[b]]) for a in range(120) for b in range(120))
# stronger: inner products with sign: C2-coefficients identical up to sign => Gram via Cartan matrix equal
assert all(abs(int(C2[mp[a]]@Ca@C2[mp[b]]))==abs(int(IP2[mp[a],mp[b]])) for a in range(120) for b in range(120))
print('map B->S2: bijection, labels and |Gram| preserved')
mp=np.array(mp)
# --- targets and transport ---
def refl2(x,g): return x-((x@Bm[g])//4)*Bm[g]
def linewords(h):  # BFS orbit of vector h (keyed up to sign) under simple reflections; w = line perm mapping h to key
    start=key(h); ident=list(range(120)); orb={start:ident}; fr=[(np.array(start),ident)]
    while fr:
        nf=[]
        for v,w in fr:
            for g in range(8):
                v2=refl2(v,g); k=key(v2)
                if k not in orb:
                    w2=[perm[g][w[t]] for t in range(120)]; orb[k]=w2; nf.append((v2,w2))
        fr=nf
    return orb
def tab(pkl,hB):
    lists=pickle.load(open(pkl,'rb')); n=len(lists)
    M=np.zeros((n,120),dtype=bool)
    for i,s in enumerate(lists): M[i,[mp[t] for t in s]]=True
    hv2=(hB@Bm)   # doubled coords of B's h
    orb=linewords(hv2); print(pkl,n,'targets',len(orb))
    return M,orb,hv2
def tomask(M,w):  # image of each set under line perm w: bit w[t] set if t in set
    P=np.zeros((M.shape[0],128),dtype=np.uint8)
    cols=np.array(w)
    Mi=np.zeros_like(M); Mi[:,cols]=M
    full=np.zeros((M.shape[0],128),dtype=bool); full[:,:120]=Mi
    b=np.packbits(full,axis=1,bitorder='little')  # n x16 bytes little-endian
    return b
hroot=LA[0]
sidx=[t for t in range(120) if G[0,t]==0][0]; hd7=LA[0]+LA[sidx]
assert hd7@Ca@hd7==4
Mr,orr,hr2=tab('../LEFT22/B_root22.pkl',hroot)
Md,ord7,hd2=tab('../LEFT22/B_d722.pkl',hd7)
assert len(orr)==120 and len(ord7)==1080
# D7 target index in SERVE2 d7 sorted-order: replicate setup2 list
IP=IP2; d7=set()
for i in range(120):
    for j in range(i+1,120):
        if IP[i,j]==0:
            for sg in (1,-1): d7.add(key(L[i]+sg*L[j]))
d7=sorted(d7); assert set(ord7)==set(d7)
# roots: target r = line r. orr keys are lines (as sign-normalised vectors)
out=open('tabs.bin','wb')
RT=np.zeros((120,len(Mr),16),dtype=np.uint8)
for k,w in orr.items(): RT[pos[k]]=tomask(Mr,w)
DT=np.zeros((1080,len(Md),16),dtype=np.uint8)
for h,k in enumerate(d7): DT[h]=tomask(Md,ord7[k])
out.write(RT.tobytes()); out.write(DT.tobytes()); out.close()
print('wrote tabs.bin',RT.shape,DT.shape)
# cross-check with implementation A's tables (A lines.txt same indexing as SERVE2's lines.txt)
A_R=np.fromfile('../SERVE/roots.bin',dtype=np.uint64).reshape(120,-1,2); A_D=np.fromfile('../SERVE/d7.bin',dtype=np.uint64).reshape(1080,-1,2)
rid=[int(x) for x in open('../SERVE/rootidx.txt').read().split()]
RT64=RT.view(np.uint64).reshape(120,-1,2); DT64=DT.view(np.uint64).reshape(1080,-1,2)
okr=all(set(map(tuple,A_R[r]))==set(map(tuple,RT64[rid[r]])) for r in range(120))
print('root tables equal to impl A (as sets, rootidx map):',okr)
# D7 index of A: unknown ordering; compare as multiset of sorted target-set signatures
sa=sorted(tuple(sorted(map(tuple,A_D[h]))) for h in range(1080)); sb=sorted(tuple(sorted(map(tuple,DT64[h]))) for h in range(1080))
print('D7 tables equal to impl A (multiset over targets):',sa==sb)
