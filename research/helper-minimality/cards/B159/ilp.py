import sys,pickle
sys.path.insert(0,'.')
from mdl import *
from ortools.sat.python import cp_model
from pairsio import load_pairs
M2,sg,pv=load_pairs(__import__('os').environ['HM_ROOT']+'/inputs/derived/pairs.json.gz');assert M2==M
n=len(M)
# bundles: full pair move sets (h2r+r2h) with exact V
bund=[]
for pi,p in enumerate(pairs):
    ms=[m for m in moves(p)]
    if len(ms)>=2 and valid(ms):
        v,_=V(ms)
        bund.append((ms,v))
print('bundles',len(bund),'legal',sum(1 for _,v in bund if not v))
npre=Counter(e[1] for e in B[:120] if e[0]=='add' and tgt(e[1]) and e[2]>=224)
print('touched targets',len(npre),'preads',sum(npre.values()))
def solve(mode,cuts=()):
    m=cp_model.CpModel()
    x=[m.NewBoolVar(f'x{i}') for i in range(n)]
    bx=[m.NewBoolVar(f'b{i}') for i in range(len(bund))]
    bad=lambda a,b:(a,b) not in pv
    legalx=lambda i:True
    for a in range(n):
        for b in range(a+1,n):
            if (a,b) not in pv: m.Add(x[a]+x[b]<=1)
    if mode=='full':
        for i in range(n):
            for c in sg[i]:
                R=[b for b in range(n) if b!=i and (min(i,b),max(i,b)) in pv and c not in pv[(min(i,b),max(i,b))]]
                m.Add(x[i]<=sum(x[b] for b in R))
    elif mode=='single':  # only violation-free moves
        for i in range(n):
            if sg[i]: m.Add(x[i]==0)
    # bundles exclusive with members; only legal bundles allowed in 'full'/'single'
    for k,(ms,v) in enumerate(bund):
        if v: m.Add(bx[k]==0)
        for mm in ms:
            for i in range(n):
                if M[i]==mm: m.Add(x[i]+bx[k]<=1)
    # touched targets
    ts=set(npre)|{mm[3] for mm in M}
    z={}
    def cnt(t,mv_x):  # linear expr of preread count change
        e=npre.get(t,0)
        terms=[]
        for i,mm in enumerate(M):
            if mm[3]!=t:continue
            if mm[0]=='h2r': terms.append(-x[i])
            elif mm[0]=='r2h': terms.append(x[i])
        for k,(ms,v) in enumerate(bund):
            for mm in ms:
                if mm[3]==t: terms.append((-1 if mm[0]=='h2r' else 1)*bx[k])
        return e+sum(terms)
    for t in ts:
        z[t]=m.NewBoolVar(f'z{t}');m.Add(cnt(t,0)<=200*z[t])
    for S in cuts: m.Add(sum(x[i] for i in S)<=len(S)-1)
    m.Minimize(sum(z.values()))
    sv=cp_model.CpSolver();sv.parameters.num_workers=2;sv.parameters.max_time_in_seconds=120
    st=sv.Solve(m)
    S=[i for i in range(n) if sv.Value(x[i])];BS=[k for k in range(len(bund)) if sv.Value(bx[k])]
    return sv.StatusName(st),int(sv.ObjectiveValue()),sv.BestObjectiveBound(),S,BS
if __name__=='__main__':
    print('noop',len(npre))
    for mode in ('free','single','full'):
        st,obj,bd,S,BS=solve(mode);print(mode,st,'min touched',obj,'bound',bd,'moves',len(S),'bundles',len(BS),flush=True)
        mv=[M[i] for i in S]+[mm for k in BS for mm in bund[k][0]]
        if mv and valid(mv):
            v,r=V(mv);print('  exact: legal',r['legal'],'viol',len(v),'dk',float(r['kappa']-K0),'touched',len(pre_targets(build_all(mv)['B'])),'replay exact',O.replay_rows(build_all(mv))==R0,flush=True)
