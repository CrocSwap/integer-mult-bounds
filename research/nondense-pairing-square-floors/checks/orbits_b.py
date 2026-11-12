# Orbit code B (independent re-implementation; usage orbits_b.py OUT.json.gz) (ambient coords, ALL root reflections, scipy components).
# Builds E8 root lines, all root-spanned hyperplane normals, Stab(n1)-orbits of normal lines, D-sets.
import numpy as np, itertools, sys, json, gzip
from fractions import Fraction as Fr
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
# doubled E8 roots (integer): 2*(+-e_i +- e_j) and (+-1)^8 even # of minus
R=[]
for i,j in itertools.combinations(range(8),2):
    for a in (2,-2):
        for b in (2,-2):
            v=[0]*8; v[i]=a; v[j]=b; R.append(v)
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: R.append(list(s))
R=np.array(R,dtype=np.int64); assert len(R)==240 and set((R*R).sum(1))=={8}
def canon(v):
    v=np.asarray(v); g=np.gcd.reduce(np.abs(v)); v=v//g; nz=np.nonzero(v)[0][0]; return tuple(int(x) for x in (v if v[nz]>0 else -v))
def sgn(v):
    v=np.asarray(v); nz=np.nonzero(v)[0][0]; return tuple(int(x) for x in (v if v[nz]>0 else -v))
Lset=sorted({sgn(r) for r in R}); L=np.array(Lset,dtype=np.int64); assert len(L)==120
G=(L@L.T)//4   # true inner products
# simple roots (Bourbaki), doubled
simple=np.array([[1,-1,-1,-1,-1,-1,-1,1],[2,2,0,0,0,0,0,0],[-2,2,0,0,0,0,0,0],[0,-2,2,0,0,0,0,0],[0,0,-2,2,0,0,0,0],[0,0,0,-2,2,0,0,0],[0,0,0,0,-2,2,0,0],[0,0,0,0,0,-2,2,0]])
C=(simple@simple.T)//4
assert all(C[i,i]==2 for i in range(8)) and sorted(int(x) for x in C[np.triu_indices(8,1)]).count(-1)==7
# fundamental weights: w_j with <w_j,a_i>=delta_ij ; solve exactly
def solve(A,b):
    A=[[Fr(int(x)) for x in row]+[Fr(int(y))] for row,y in zip(A,b)]; n=len(A)
    for c in range(n):
        p=next(r for r in range(c,n) if A[r][c]!=0); A[c],A[p]=A[p],A[c]
        A[c]=[x/A[c][c] for x in A[c]]
        for r in range(n):
            if r!=c and A[r][c]!=0: A[r]=[x-A[r][c]*y for x,y in zip(A[r],A[c])]
    return [A[r][n] for r in range(n)]
W=[]
for j in range(8):
    w=solve((simple//1).tolist(),[2*int(i==j) for i in range(8)])  # simple doubled: (2a_i).(w)/... use doubled dot
    # simple rows are 2a_i ; (2a_i).w = 2 delta -> a_i.w = delta ; w in true coords
    den=1
    for x in w: den=den*x.denominator//np.gcd(den,x.denominator)
    v=[int(x*den) for x in w]; g=np.gcd.reduce(np.abs(v)); v=[x//g for x in v]
    W.append(v)
Wv=np.array(W,dtype=np.int64)
assert all(((simple@Wv[j])!=0).sum()==1 for j in range(8))
# BFS orbits of primitive integer normals under all 120 reflections: s_r(v)=v-2(v.r)/(r.r) r, r doubled -> v - (v.R)/4 * R ... keep integer by scaling
def vcanon(A):
    A=np.asarray(A,dtype=np.int64).copy(); g=np.gcd.reduce(np.abs(A),axis=1); A//=g[:,None]
    f=np.argmax(A!=0,axis=1); sg=np.sign(A[np.arange(len(A)),f]); A*=sg[:,None]; return A
def vkey(A):
    assert np.abs(A).max()<30000
    return np.ascontiguousarray(A.astype(np.int16)).view('S16').ravel()
def orbit(v0):
    cur=vcanon(np.array([v0])); seenk=np.sort(vkey(cur)); fr=cur; allv=[cur]
    while len(fr):
        newk=[];newv=[]
        for c in range(0,len(fr),1500):
            f=fr[c:c+1500]; d=f@L.T
            img=vcanon((4*f[:,None,:]-d[:,:,None]*L[None,:,:]).reshape(-1,8)); k=vkey(img)
            k,ii=np.unique(k,return_index=True); img=img[ii]
            m=~np.isin(k,seenk); newk.append(k[m]); newv.append(img[m])
        if newk:
            nk=np.concatenate(newk); nv=np.concatenate(newv); nk,ii=np.unique(nk,return_index=True); nv=nv[ii]
        else: nk=seenk[:0]; nv=fr[:0]
        seenk=np.sort(np.concatenate([seenk,nk])); fr=nv; allv.append(nv)
    return [tuple(int(x) for x in v) for v in np.concatenate(allv)]
normals=[]; typ=[]
for j in range(8):
    O=orbit(Wv[j]); normals+=O; typ+=[j]*len(O); print('type',j,'lines',len(O),file=sys.stderr,flush=True)
N=np.array(normals,dtype=np.int64); print('hyperplanes',len(N),'distinct',len(set(normals)),flush=True)
# verify each is root-spanned: rank of roots orthogonal = 7
Mk=(N@L.T)!=0   # (H,120) True = r_t . n != 0
for k in np.random.default_rng(1).choice(len(N),200,replace=False):
    Z=L[~Mk[k]]; assert np.linalg.matrix_rank(Z.astype(float))==7
allk=vkey(N); order=np.argsort(allk); sk=allk[order]
def idx_of(arr):
    k=vkey(vcanon(arr)); p=np.searchsorted(sk,k); assert (sk[p]==k).all(); return order[p]
key={tuple(v):k for k,v in enumerate(normals)}
res={}
for j in range(8):
    n1=Wv[j]; i1=key[canon(n1)]
    perp=[t for t in range(120) if (L[t]@n1)==0]
    rows=[];cols=[]
    for t in perp:
        num=N@L[t]; img=(4*N-num[:,None]*L[t][None,:])
        rows.append(np.arange(len(N))); cols.append(idx_of(img))
    rows=np.concatenate(rows); cols=np.concatenate(cols)
    nc,lab=connected_components(coo_matrix((np.ones(len(rows)),(rows,cols)),shape=(len(N),len(N))),directed=False)
    reps={}
    for k in range(len(N)): reps.setdefault(lab[k],k)
    non=[k for k in reps.values() if int(N[i1]@N[k])!=0]; orth=[k for k in reps.values() if int(N[i1]@N[k])==0]
    res[j]=(i1,non,orth); print('j',j,'roots perp',len(perp),'orbits',nc,'non',len(non),'orth',len(orth),flush=True)
print('TOTAL non',sum(len(r[1]) for r in res.values()),'orth',sum(len(r[2]) for r in res.values()),flush=True)
Mk=(N@L.T)!=0
types=[]
for j in range(8):
    i1,non,orth=res[j]
    for kind,lst in ((True,non),(False,orth)):
        for k in lst:
            D=[t for t in range(120) if Mk[i1,t] and Mk[k,t]]
            types.append(dict(j=j,k=int(k),nonorth=kind,D=D,orth=[sum(1<<c for c,s in enumerate(D) if G[t][s]==0) for t in D]))
print('hyperplanes',len(N),'types',len(types),'nonorth',sum(t['nonorth'] for t in types),'orth',sum(not t['nonorth'] for t in types),
      'min|D| nonorth',min(len(t['D']) for t in types if t['nonorth']))
json.dump(types,gzip.open(sys.argv[1],'wt'))
np.savez_compressed(sys.argv[1]+'.normals.npz',L=L,N=N)   # sidecar for small.py E7
print('PASS orbit table written')
