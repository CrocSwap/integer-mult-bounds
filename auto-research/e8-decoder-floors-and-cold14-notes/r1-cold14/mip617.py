"""free-dispatch exact-window pattern MIP (first-order mass-neutral values), Hall masks, then literal expansion."""
import json,sys,gzip,hashlib,random,time,itertools
import numpy as np
from collections import Counter,defaultdict
from scipy.optimize import milp,LinearConstraint,Bounds
from scipy.sparse import coo_matrix,csr_matrix
from scipy.sparse.csgraph import maximum_flow
V={int(k):v for k,v in json.load(open('V617.json')).items()}
PKG='/Users/joelpulikkan/imb-r1b/research/complex-571-cold14-b3'
PLAN=json.load(open(PKG+'/data/PLAN.json'))
reg=PLAN['provider_registry'];provs=['jp8','atm3']
TIGHT=int(sys.argv[1]);SECS=float(sys.argv[2]);OUT=sys.argv[3]
inv={p:Counter(reg[p]['widths']) for p in provs}
val={p:sum(V[int(r)]*c for r,c in reg[p]['actual_paid_profile'].items()) for p in provs}
WID=[4,5,7,8,9]
def pats(cap,L):
    out=[]
    def rec(pre,i,tot):
        r=cap-tot
        if r<=TIGHT or (r==cap==48): out.append(tuple(pre))
        for j in range(i,len(WID)):
            w=WID[j]
            if tot+w<=cap and len(pre)<L: rec(pre+[w],j,tot+w)
    rec([],0,0);return out
ub=[];cost=[];integ=[];R=[];lo=[];hi=[]
def var(c,u=np.inf):
    ub.append(u);cost.append(-c);return len(ub)-1
def con(row,l,h):R.append(row);lo.append(l);hi.append(h)
sel={(t,p):var(val[p],1) for t in range(72) for p in provs}
for t in range(72):con({sel[t,p]:1 for p in provs},1,1)
groups={};invrow=defaultdict(dict)
for key,(cap,times) in PLAN['windows'].items():
    ps=pats(cap,len(times));cnts=[Counter(q) for q in ps]
    pv=[var(V[cap-sum(q)],112) for q in ps]
    con({i:1 for i in pv},112,112)
    fl={}
    for t in times:
        for w in WID:
            if not any(c[w] for c in cnts):continue
            i=var(0,112);fl[t,w]=i;invrow[t,w][i]=1
        # Hall masks
        seen=set()
        for mask in range(1,32):
            cols={w for b,w in enumerate(WID) if mask>>b&1}
            req=tuple(i for (tt,w),i in fl.items() if tt==t and w in cols)
            pres=tuple(j for j,c in zip(pv,cnts) if any(c[w] for w in cols))
            if req and (req,pres) not in seen:
                seen.add((req,pres));row={i:1 for i in req}
                for j in pres:row[j]=row.get(j,0)-1
                con(row,-np.inf,0)
    for w in WID:
        row={i:1 for (t,ww),i in fl.items() if ww==w}
        for j,c in zip(pv,cnts):
            if c[w]:row[j]=row.get(j,0)-c[w]
        if row:con(row,0,0)
    groups[key]=dict(cap=cap,times=times,ps=ps,pv=pv,fl=fl)
for t in range(72):
    for w in WID:
        row=dict(invrow[t,w])
        for p in provs:
            if inv[p][w]:row[sel[t,p]]=-inv[p][w]
        con(row,0,0)
rr,cc,vv=[],[],[]
for i,row in enumerate(R):
    for j,x in row.items():rr.append(i);cc.append(j);vv.append(x)
A=coo_matrix((vv,(rr,cc)),shape=(len(R),len(ub))).tocsr()
print('vars',len(ub),'cons',len(R),flush=True)
t0=time.time()
res=milp(np.array(cost),integrality=np.ones(len(ub)),bounds=Bounds(np.zeros(len(ub)),np.array(ub)),constraints=LinearConstraint(A,lo,hi),options={'time_limit':SECS,'mip_rel_gap':1e-9,'disp':False})
print(res.status,res.message,'obj',-res.fun if res.x is not None else None,'secs',time.time()-t0,flush=True)
x=np.round(res.x).astype(int)
disp={t:p for (t,p),i in sel.items() if x[i]}
rem=Counter()
for key,g in groups.items():
    for q,i in zip(g['ps'],g['pv']):
        if x[i]:rem[g['cap']-sum(q)]+=x[i]
print('dispatch',Counter(disp.values()),'remainders',dict(rem))
json.dump(dict(disp=disp,x=x.tolist(),obj=-res.fun),open(OUT+'-sol.json','w'))
# profile
prof=Counter()
for t,p in disp.items():prof.update({int(r):c for r,c in reg[p]['actual_paid_profile'].items()})
prof.update(rem)
print('profile',dict(sorted(prof.items())),'mass',sum(r*c for r,c in prof.items()))
json.dump({str(k):v for k,v in sorted(prof.items())},open(OUT+'-profile.json','w'))
import pickle;pickle.dump(dict(groups=groups,x=x,disp=disp),open(OUT+'.pkl','wb'))
