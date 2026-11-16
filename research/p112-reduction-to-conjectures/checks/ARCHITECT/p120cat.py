# P120 analogue of kpr15 Lemma 3.1 and WALL catalogue. Exact integer/F2 arithmetic.
# Lines = 120 E8 roots up to sign. Bd[t,s] = [t==s or t⊥s]. Label span rank of a set A = rank_F2 Bd[all,A] (labels span F2^9, beta nondegenerate).
import json, itertools, numpy as np
from collections import Counter
D=json.load(open('../OS-CHARGE2/data.json'))
E8=np.rint(np.array(D['E8'])*2).astype(int)   # doubled coords -> integers
lines=[]
for r in E8:
    if not any((r==l).all() or (r==-l).all() for l in lines): lines.append(r)
lines=np.array(lines); v=len(lines); print('lines',v)
G=lines@lines.T   # = 4*inner
Bd=((G==0)|np.eye(v,dtype=bool)).astype(int)
def f2rank_rows(rows):
    basis=[]
    for x in rows:
        for b in basis: x=min(x,x^b)
        if x: basis.append(x)
    return len(basis)
colmask=[sum(int(Bd[t,s])<<t for t in range(v)) for s in range(v)]   # column s as bitmask over t
def w(A): return f2rank_rows([colmask[s] for s in A])
print('rank Bd',w(range(v)))
# label functionals: vectors phi in rowspace of Bd? Instead enumerate classes z as subsets O_z = {s: beta(z,l_s)=1}.
# Build labels: choose 9 lines whose Bd-columns are independent -> coordinates of every label in that dual basis.
basis=[];idx=[]
for s in range(v):
    tmp=basis+[colmask[s]]
    if f2rank_rows(tmp)>len(basis): basis.append(colmask[s]); idx.append(s)
    if len(basis)==9: break
# label of line t: vector of beta(l_t, l_b) for b in idx  (coords in dual basis) -> beta(l_t,l_s) = lab_t^T M lab_s ... simpler: O_z for z in span of labels:
# z = sum_{b in S} l_b (S subset idx) gives O_z = {s : sum_b Bd[b,s] = 1 mod 2}; idx labels form a basis so this enumerates all 511 nonzero z.
O={}
for k in range(1,512):
    S=[idx[j] for j in range(9) if k>>j&1]
    vec=np.zeros(v,dtype=int)
    for b in S: vec^=Bd[b]
    O[k]=frozenset(np.nonzero(vec)[0].tolist())
print('|O_z| range',min(map(len,O.values())),max(map(len,O.values())))
# (a) Lemma 3.1 analogue: a hyperplane z^perp contains all labels of Off(y) iff O_z ⊆ y^perp; need real rank of O_z lines <= 7
rr=Counter()
for k,S in O.items():
    rk=np.linalg.matrix_rank(lines[sorted(S)].astype(float)) if S else 0
    rr[rk]+=1
print('(a) real rank of O_z over 511 classes:',dict(rr), '=> no y!=0 has Off(y) label-deficient' if min(rr)>=8 else '=> deficient Off exist')
# (b) catalogue: directions h with small |Off|
allr=list(E8)
def off(h): return frozenset(np.nonzero(lines@h)[0].tolist())
dirs={}
for r in E8: dirs.setdefault(off(r),('root',))
for a,b in itertools.combinations(range(len(allr)),2):
    s=allr[a]+allr[b]
    if s@s==16: dirs.setdefault(off(s),('n4',))
print('directions',len(dirs),Counter(len(o) for o in dirs))
cat=Counter()
for o,(kind,) in dirs.items():
    vals=sorted(len(S&o) for S in O.values())
    cat[(kind,len(o),vals[0],vals[1],vals[2])]+=1
for k in sorted(cat): print('(b) kind,|Off|,min,2nd,3rd:',k,cat[k])
