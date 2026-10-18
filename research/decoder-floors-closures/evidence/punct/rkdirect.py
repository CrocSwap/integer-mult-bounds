"""PUNCT5 target (3), exact direct encoding. rank N <= 7 needs: good lines inside one rank-7 flat F* (type TYPE rep), i.e. every live
line s outside F* is BAD: K ∩ s^perp lies in a hyperplane of s^perp, i.e. S ⊇ s^perp ∖ F' for some rank-7 flat F' ∋ s
(F' = closure of that hyperplane + s). Options with |s^perp ∖ F'| > P are impossible. Also every orthogonal 8-frame must be hit
(a frame in K gives rank N = 8). CNF: vars S_t = t+1; z_(s,F') ; S_s ∨ OR z ; z -> S_t ; frames ; |S| <= P (seqcounter).
UNSAT => for every S with |S| <= P the good lines are not inside any flat of this type."""
import sys, pickle, numpy as np
sys.path.insert(0,'/Users/mason/repo_clones/intmult-work/cards/PUNCT4')
from p4lib import G, FLATREP
from pysat.card import CardEnc, EncType
typ=int(sys.argv[1]); P=int(sys.argv[2])
sides=pickle.load(open('/Users/mason/repo_clones/intmult-work/cards/PUNCT4/sides.pkl','rb'))
M=np.array([m for n,m in sides if n not in ('E6','D6')])
assert len(M)==440880
flat=FLATREP[typ][1]; out=[s for s in range(120) if not flat[s]]
card=CardEnc.atmost(lits=list(range(1,121)),bound=P,top_id=120,encoding=EncType.seqcounter)
cls=list(card.clauses); nv=card.nv
orth=[set(t2 for t2 in range(120) if G[t,t2]==0) for t in range(120)]
FR=[]
def dfs(cur,cand):
    if len(cur)==8: FR.append(cur); return
    for s in sorted(cand):
        if s>cur[-1]: dfs(cur+[s],cand&orth[s])
for t in range(120): dfs([t],orth[t])
assert len(FR)==2025
for f in FR: cls.append([t+1 for t in f])
nopt=0
for s in out:
    perp=(G[s]==0)
    Ms=M[M[:,s]]
    need=perp[None,:]&~Ms
    sz=need.sum(1)
    sets=set(frozenset(np.flatnonzero(r).tolist()) for r in need[sz<=P])
    # keep inclusion-minimal
    sets=sorted(sets,key=len); mins=[]
    for e in sets:
        if not any(m<=e for m in mins): mins.append(e)
    head=[s+1]
    for e in mins:
        nv+=1; z=nv; head.append(z); nopt+=1
        for t in e: cls.append([-z,t+1])
    cls.append(head)
fn=f'cnf/rkd_{typ}_{P}.cnf'
with open(fn,'w') as f:
    f.write(f'p cnf {nv} {len(cls)}\n')
    for c in cls: f.write(' '.join(map(str,c))+' 0\n')
print('type',typ,'|F*|',int(flat.sum()),'P',P,'outside',len(out),'options',nopt,'vars',nv,'clauses',len(cls),'->',fn,flush=True)
