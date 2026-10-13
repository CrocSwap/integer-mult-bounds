"""expand an aggregated MIP solution to a literal owner map + PLAN (PR569 nominator expansion logic)."""
import json,sys,gzip,hashlib,random,pickle,copy
import numpy as np
from collections import Counter,defaultdict
from scipy.optimize import milp,LinearConstraint,Bounds
from scipy.sparse import coo_matrix,csr_matrix
from scipy.sparse.csgraph import maximum_flow
PKG='/Users/joelpulikkan/imb-r1b/research/complex-571-cold14-b3'
PLAN=json.load(open(PKG+'/data/PLAN.json'));reg=PLAN['provider_registry']
S=pickle.load(open(sys.argv[1],'rb'));OUT=sys.argv[2]
groups,x,disp=S['groups'],S['x'],{int(k):v for k,v in S['disp'].items()}
WID=[4,5,7,8,9]
def expand(plist,flows,seed):
    times=sorted({t for t,w in flows});counts=[Counter(p) for p in plist];rng=random.Random(seed)
    for attempt in range(60):
        used=[set() for _ in plist];result=[[] for _ in plist]
        colors=sorted(WID,key=lambda w:(sum(w in p for p in plist),w))
        if attempt:rng.shuffle(colors)
        ok=True
        for width in colors:
            active=[p for p in range(len(counts)) if counts[p][width]]
            if not active:continue
            rng.shuffle(active);start=1+len(times);sink=start+len(active);rr,cc,vv=[],[],[]
            for ti,t in enumerate(times):
                d=flows.get((t,width),0)
                if d:
                    rr.append(0);cc.append(1+ti);vv.append(d)
                    for pi,port in enumerate(active):
                        if t not in used[port]:rr.append(1+ti);cc.append(start+pi);vv.append(1)
            for pi,port in enumerate(active):rr.append(start+pi);cc.append(sink);vv.append(counts[port][width])
            f=maximum_flow(csr_matrix((vv,(rr,cc)),shape=(sink+1,sink+1),dtype=np.int64),0,sink)
            if f.flow_value!=sum(flows.get((t,width),0) for t in times):ok=False;break
            F=f.flow.tocoo() if hasattr(f.flow,'tocoo') else coo_matrix(f.flow)
            for a,b,v in zip(F.row,F.col,F.data):
                if v>0 and 1<=a<start and start<=b<sink:
                    port=active[b-start];t=times[a-1];used[port].add(t);result[port].append((t,width))
        if ok:return result
    # exact fallback
    keys=[];tv=defaultdict(dict);pvr=defaultdict(dict);tp=defaultdict(dict)
    for port,c in enumerate(counts):
        for width,n in c.items():
            for t in times:
                if flows.get((t,width),0):
                    i=len(keys);keys.append((port,t,width));tv[t,width][i]=1;pvr[port,width][i]=1;tp[t,port][i]=1
    R=[];lo=[];hi=[]
    for k,row in tv.items():R.append(row);lo.append(flows[k]);hi.append(flows[k])
    for (port,width),row in pvr.items():R.append(row);lo.append(counts[port][width]);hi.append(counts[port][width])
    for row in tp.values():R.append(row);lo.append(0);hi.append(1)
    rr,cc,vv=[],[],[]
    for i,row in enumerate(R):
        for j,v in row.items():rr.append(i);cc.append(j);vv.append(v)
    res=milp(np.zeros(len(keys)),integrality=np.ones(len(keys)),bounds=Bounds(0,1),constraints=LinearConstraint(coo_matrix((vv,(rr,cc)),shape=(len(R),len(keys))).tocsr(),lo,hi),options={'time_limit':120})
    assert res.x is not None,'expansion infeasible'
    result=[[] for _ in counts]
    for i,(port,t,width) in enumerate(keys):
        if round(res.x[i]):result[port].append((t,width))
    return result
pools=defaultdict(list);calls=[];pcw=[];paid=Counter()
for t,(stage,replica) in enumerate(PLAN['order']):
    p=disp[t];orig=PLAN['provider_calls'][t];assert (orig['time'],orig['stage'],orig['replica'])==(t,stage,replica)
    o=orig['orientation'];calls.append(dict(time=t,stage=stage,replica=replica,provider=p,orientation=o,local_program_sha256=reg[p]['orientation_program_sha256'][o]))
    pcw.append(dict(stage=stage,replica=replica,widths=reg[p]['widths']));paid.update({int(k):v for k,v in reg[p]['actual_paid_profile'].items()})
    for h,wd in enumerate(reg[p]['widths']):pools[t,wd].append(h)
rows=[]
for gi,(key,g) in enumerate(sorted(groups.items())):
    plist=[q for q,i in zip(g['ps'],g['pv']) for _ in range(x[i])];assert len(plist)==112
    flows={k:x[i] for k,i in g['fl'].items() if x[i]}
    slots=expand(plist,flows,gi)
    assert Counter((t,w) for s in slots for t,w in s)==Counter(flows)
    r,c=map(int,key.split(','))
    for port,s in enumerate(slots):
        assert Counter(w for _,w in s)==Counter(plist[port]) and len({t for t,_ in s})==len(s)
        off=0
        for t,wd in sorted(s):
            h=pools[t,wd].pop();stage,replica=PLAN['order'][t]
            rows.append(dict(child=c,copy=r*112+port,family=r*896+(2*PLAN['pairs'][str(c)]+PLAN['sides'][str(c)])*112+port,helper=h,offset=off,owner_replica=r,port=port,replica=replica,stage=stage,time=t,width=wd));off+=wd
assert not any(pools.values())
occ=defaultdict(set);fam=defaultdict(set)
for z in rows:
    assert z['family'] not in fam[z['time']];fam[z['time']].add(z['family'])
    cap,win=PLAN['windows']['%d,%d'%(z['owner_replica'],z['child'])];assert z['time'] in win and z['offset']+z['width']<=cap
    k=(z['owner_replica'],z['child'],z['port']);cells=set(range(z['offset'],z['offset']+z['width']));assert not occ[k]&cells;occ[k]|=cells
rem=Counter()
for key,(cap,_) in PLAN['windows'].items():
    r,c=map(int,key.split(','))
    for port in range(112):
        cl=occ[r,c,port];assert cl==set(range(len(cl)))
        if len(cl)<cap:rem[cap-len(cl)]+=1
paid.update(rem);assert sum(k*v for k,v in paid.items())==520704
rows.sort(key=lambda z:(z['time'],z['helper']))
packed=gzip.compress(json.dumps(rows,sort_keys=True,separators=(',',':')).encode(),mtime=0);packed=packed[:9]+b'\xff'+packed[10:]
open(OUT+'/OWNERS.json.gz','wb').write(packed)
plan=copy.deepcopy(PLAN);plan.update(profile={str(k):v for k,v in sorted(paid.items())},provider_calls=calls,per_call_widths=pcw,solver_status=sys.argv[3] if len(sys.argv)>3 else 'free_dispatch_exact_window_pattern_milp',gap=None,
  source_plan_sha256=hashlib.sha256(open(PKG+'/data/PLAN.json','rb').read()).hexdigest(),source_owners_sha256=hashlib.sha256(open(PKG+'/data/OWNERS.json.gz','rb').read()).hexdigest(),assignment_sha256=hashlib.sha256(packed).hexdigest())
open(OUT+'/PLAN.json','w').write(json.dumps(plan,indent=2)+'\n')
print('profile',dict(sorted(paid.items())),'remainders',dict(rem),'dispatch',Counter(disp.values()))
