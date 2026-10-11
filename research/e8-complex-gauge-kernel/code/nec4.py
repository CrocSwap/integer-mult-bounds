import sys,json,gzip,pickle,os
import os
sys.path.insert(0,os.environ['CXG_REPO']+'/research/split-centres-global/vendor')
from clifford_exact import *
from iso1 import *
from gauge import prep,span
n=9;FULL=tuple(1<<i for i in range(n))
# (1) relaxed strictness: E nondegenerate with orthonormal basis (ignore 1 in E)
def relaxed(E):
    return det2(gram(E)) and any(bin(x).count('1')%2 for x in spanvecs(E))
w=load();col,first=setup(w);R=len(col)
cand={}
for h,F in first.items():
    for E in subspaces(F):cand.setdefault(E,[]).append(h)
C=np.zeros((v,R))
for h in range(R):
    for t,x in col[h].items():C[t,h]=float(x)
kp=0
for E,G in cand.items():
    if relaxed(E) and len(G)>=2:
        kp+=max(0,len(G)-np.linalg.matrix_rank(C[:,G]))*len(E)
print('relaxed-isometric kernel potential',kp)
col2,first2,cap,cands,P=prep(w)
ge=0
for E in cand:
    if relaxed(E):
        sE=span(E);el=[h for h in range(R) if sE<=span(first2[h]) and all(sE<=cap[t] for t in col2[h])]
        ge=max(ge,len(el)*len(E))
print('relaxed-isometric gauge best eps',ge)
# (2) adapter factorisation for every entrance used in v4
d=json.load(gzip.open(os.path.join(os.environ['CXG_PKG'],'data/words/gauge80-kernel42/FULL-WORD.json.gz')))
Es={tuple(E) for E in d['start_extra'].values()}
print('distinct entrance frames in v4',len(Es))
ok=0
for E in sorted(Es,key=lambda e:(len(e),e)):
    op=canonical_frame(n,tuple(E)).adjoint().then(canonical_frame(n,FULL))
    rec,compiled=lower_child(op)
    assert rec['rank']==n-len(E) and compiled.tab==op.tab and compiled.zero_state()==op.zero_state()
    ok+=1
print('E->FULL composite = monomial . C_[9-e] . monomial exactly for',ok,'frames (adapters entrance/exit give C_[w] on w coordinates)')
