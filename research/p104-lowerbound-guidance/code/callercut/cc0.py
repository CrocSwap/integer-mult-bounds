"""CALLERCUT cc0: exact soundness check of the relay-cut laws on built frames.
RC_l (per stage t):  sigma_l(t) := #{r in E_t : D_r>=l, |piece_r(t)|<l}  >=  2 - min_{s!=t} #{r in E_s cap E_t : D_r<l}
HULL (per ordered pair s!=t): |E_s cap E_t| - #{multi pieces q at t : every role with mask >= P_q contains s} >= 2
Frames: C1, c33 (pieces from rescuebuild rb1/rb9), c12, c22 (json, degree-1 roles dropped, all idle pieces singletons)."""
import json,itertools
F=frozenset
BASE='<research-tree>/cards/WILD/'
A=F(range(6))
C33=[(A,[]),(A,[]),(F({0,1,2}),[F({0}),F({1,2})]),(F({0,1,2}),[F({0}),F({1,2})]),(F({1,2}),[F({1}),F({2})]),(F({1,2}),[F({1}),F({2})]),
     (F({3,4}),[F({3,4})]),(F({3,4}),[F({3,4})]),(F({3,4,5}),[F({3}),F({4}),F({5})]),(F({3,4,5}),[F({3}),F({4}),F({5})])]
C1=[(F({1,2}),[]),(F({1,2}),[]),(F({0,1,2}),[F({1}),F({2})]),(F({0,1,2}),[F({1}),F({2})])]
def pieces(R):  # role -> dict stage -> piece (frozenset); unlisted stages are singleton mains
    out=[]
    for M,P in R:
        d={}
        for p in P:
            for t in p:d[t]=p
        for t in M:d.setdefault(t,F({t}))
        out.append((M,d))
    return out
def fromjson(fn):
    W=json.load(open(fn));k=W['stages'];n=W['roles']
    order=[];[order.append(e[1]) for e in W['events'] if e[0]=='HOST' and e[1] not in order]
    pos={st:i for i,st in enumerate(order)}
    masks=[F(pos[i+1] for i,b in enumerate(W['diagonal'][r][2:]) if b) for r in range(n)]
    return k,[(m,[]) for m in masks if len(m)>=2]
def check(name,k,R):
    Rs=pieces(R);worst_rc=None;worst_h=None;nrc=0;nh=0
    E=[[i for i,(M,d) in enumerate(Rs) if t in M] for t in range(k)]
    for t in range(k):
        for l in range(2,k+1):
            sig=sum(1 for i in E[t] if len(Rs[i][0])>=l and len(Rs[i][1][t])<l)
            msh=min(sum(1 for i in E[t] if s in Rs[i][0] and len(Rs[i][0])<l) for s in range(k) if s!=t)
            sl=sig-(2-msh);nrc+=1
            if worst_rc is None or sl<worst_rc[0]:worst_rc=(sl,t,l)
        for s in range(k):
            if s==t:continue
            W=[i for i in E[t] if s in Rs[i][0]]
            dead=0
            for i in E[t]:
                P=Rs[i][1][t]
                if len(P)<2:continue
                Eq=[j for j,(M,d) in enumerate(Rs) if P<=M]
                if all(s in Rs[j][0] for j in Eq):dead+=1
            sl=len(W)-dead-2;nh+=1
            if worst_h is None or sl<worst_h[0]:worst_h=(sl,s,t)
    print('%-8s k=%d n=%d  RC min slack %s over %d (t,l)   HULL min slack %s over %d (s,t)'%(name,k,len(R),worst_rc,nrc,worst_h,nh))
check('C1',3,C1);check('c33',6,C33)
for nm in ['c12_tm1o2','c22_tm1o2','c11_tm2','B11_core']:
    k,R=fromjson(BASE+'UNIMODEL/arm1/caller_%s.json'%nm);check(nm,k,R)
k,R=fromjson(BASE+'UNIMODEL/swarm/d3star/caller_C1.json');check('C1json',k,R)
# RC2 (pair form): for every s != t and every l:
#   #{r in E_s : D_r>=l, |P_r(s)|<l, t notin P_r(s)} + #{r in E_s cap E_t : D_r<l, t notin P_r(s)}  >= 2
def check2(name,k,R):
    Rs=pieces(R);worst=None;cnt=0
    for s in range(k):
        for t in range(k):
            if s==t:continue
            for l in range(2,k+2):
                a=sum(1 for M,d in Rs if s in M and len(M)>=l and len(d[s])<l and t not in d[s])
                b=sum(1 for M,d in Rs if s in M and t in M and len(M)<l and t not in d[s])
                cnt+=1;sl=a+b-2
                if worst is None or sl<worst[0]:worst=(sl,s,t,l)
    print('%-8s RC2 pair form min slack %s over %d (s,t,l)'%(name,worst,cnt))
check2('C1',3,C1);check2('c33',6,C33)
for nm in ['c12_tm1o2','c22_tm1o2','c11_tm2','B11_core']:
    k,R=fromjson(BASE+'UNIMODEL/arm1/caller_%s.json'%nm);check2(nm,k,R)
