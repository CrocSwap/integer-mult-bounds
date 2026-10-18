"""B174 checks. usage: check.py FULL-WORD.json.gz
Verifies hypotheses H-CUT/H-PRE, the identity F=I, F0 (cut deleted) has zero odd entries,
Diff=F-F0 has rank |K|=8 and Diff o Odd = I o Odd; omega(odd graph)=8; centre-frame lemma."""
import sys,gzip,json
sys.path.insert(0,(__import__('os').environ['HM_ROOT']+'/inputs/pr799/independent'))
from audit_local import apply,basis,contained,registers
from fractions import Fraction as F
import numpy as np
from clique import odd_graph,max_clique
w=json.load(gzip.open(sys.argv[1]));v,h,R=w['report']['v'],w['report']['h'],w['report']['R'];n=2*v+R
ports=w['ports'];cen=w['centers'];cut=w['cut']
par=lambda a,b:bin(a&b).count('1')&1
odd=np.array([[par(ports[t],ports[u]) for u in range(v)] for t in range(v)])
# H-CUT
K=sorted({e[2] for e in cut})
print('H-CUT: all cut ops add target<-centre:',all(e[0]=='add' and v<=e[1]<2*v and e[2] in cen for e in cut),
      '| centres disjoint from targets:',not any(v<=c<2*v for c in cen),'| #centres',len(cen),'distinct',len(set(cen)),'| |K| read',len(K))
# H-PRE
print('H-PRE: precondition touches only target registers:',all(all(v<=r<2*v for r in registers(e)) for e in w['precondition']))
# build program as audit_local does (lines 81-105)
ident=lambda:[{k:F(1)} for k in range(n)]
main=w['A']+w['cut']+w['B']
raw=ident()
for e in main:apply(e,raw)
dirt=[{} for _ in range(n)]
for y in range(v,2*v):dirt[y]={k:a for k,a in raw[y].items() if k>=2*v}
for e in w['precondition']:apply(e,dirt)
comp=[['add',y,k,-a.numerator,a.denominator,[]] for y in range(v,2*v) for k,a in sorted(dirt[y].items())]
print('H-PRE: compensation reads only helpers into targets:',all(v<=e[1]<2*v and e[2]>=2*v for e in comp))
early=w.get('early_cleanup',[]);ids={i for i,U in early}
tail=[w['cleanup'][i][:-1]+[U] for i,U in early];cleanup=[e for i,e in enumerate(w['cleanup']) if i not in ids]
print('cleanup never touches a target:',all(not(v<=r<2*v) for e in cleanup for r in registers(e)))
def Fmat(skip_cut):
    prog=w['precondition']+comp+w['A']+([] if skip_cut else w['cut'])+w['B']+tail+cleanup
    rows=ident()
    for e in prog:apply(e,rows)
    M=np.zeros((v,v))
    for t in range(v):
        for k,x in rows[v+t].items():
            if k<v:M[t,k]=float(x)
    return M
Ffull=Fmat(False);F0=Fmat(True)
print('F == I:',np.allclose(Ffull,np.eye(v)))
print('F0 (cut deleted) entries on odd positions all zero:',np.abs(F0*odd).max()==0,'| nnz(F0)',np.count_nonzero(F0),'odd nnz in F0',np.count_nonzero(F0*odd))
D=Ffull-F0
rk=np.linalg.matrix_rank(D)
print('rank(F-F0) =',rk,'<= |K| =',len(K),'| (F-F0) o Odd == I o Odd:',np.allclose(D*odd,np.eye(v)*odd))
c=max_clique(odd_graph(ports))
print('omega(odd graph) =',len(c),c,'| principal submatrix of F-F0 on clique is I:',np.allclose(D[np.ix_(c,c)],np.eye(len(c))))
# centre-frame lemma: frame of centre q contains p_u for every u in support of its A-row
rowsA=ident()
for e in w['A']:apply(e,rowsA)
ok=True;dims=[]
for q,fi in zip(cen,w['center_frames']):
    U=basis(w['frames'][fi]) if 'frames' in w and isinstance(fi,int) else basis(fi)
    dims.append(len(U))
    supp=[u for u in range(v) if rowsA[q].get(u)]
    ok&=all(contained((ports[u],),U) for u in supp)
print('centre-frame lemma (p_u in U_q for u in supp of A-row of q):',ok,'| centre frame dims',dims)
L=np.array([[float(rowsA[q].get(u,0)) for u in range(v)] for q in cen])
print('rank of 8 centre A-rows over sources',np.linalg.matrix_rank(L),'| rank([Lambda;Diff]) =',np.linalg.matrix_rank(np.vstack([L,D])))
