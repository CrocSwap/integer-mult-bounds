"""Aggregate allocation with lazy nomination cuts. Usage: loop.py PLAN.json WIDTHS OUT-AGG.json [secs/iter] [max_iters]
Each iteration: solve the aggregate model (with all cuts so far, hinted by the previous solution), then try the literal
per-child nomination; for every child that fails, add top-k Hall cuts: for a width subset S and the k calls with most
S-roles on that child, sum of those roles <= sum_P y_P * min(k, #S-slots of P)."""
import json,math,sys,itertools,time
from collections import Counter,defaultdict
from ortools.sat.python import cp_model
PLAN,WID,OUT=sys.argv[1:4];LIM=float(sys.argv[4])if len(sys.argv)>4 else 300;ITERS=int(sys.argv[5])if len(sys.argv)>5 else 12
plan=json.load(open(PLAN));nw={int(k):v for k,v in json.loads(WID).items()};M=73
if not nw or any(w<=0 or not isinstance(n,int) or n<0 for w,n in nw.items()):
    raise SystemExit('Widths must be positive integers with nonnegative integer counts')
if ITERS<=0:
    raise SystemExit('max_iters must be positive')
order=[tuple(x)for x in plan['order']];T=len(order)
win={tuple(map(int,k.split(','))):(v[0],sorted(v[1]))for k,v in plan['windows'].items()}
ranks=sorted({r for r,_ in win.values()});W=sorted(nw);SUBS=[S for k in range(1,len(W)+1)for S in itertools.combinations(W,k)]
g=lambda r:0 if r==0 else r*math.log(M/r)
def patterns(r):
    out=set()
    def rec(rem,start,cur):
        out.add(tuple(cur))
        for j in range(start,len(W)):
            if W[j]<=rem:rec(rem-W[j],j,cur+[W[j]])
    rec(r,0,[]);return sorted(out)
pats={r:patterns(r)for r in ranks}
cuts=[]   # (i,orp,times,S,k)
def solve(hint):
    m=cp_model.CpModel();x={};y={}
    for (orp,i),(r,times)in win.items():
        for t in times:
            for w in W:x[t,i,orp,w]=m.NewIntVar(0,min(nw[w],120),'')
            m.Add(sum(x[t,i,orp,w]for w in W)<=120)
        for P in pats[r]:y[i,orp,P]=m.NewIntVar(0,120,'')
        m.Add(sum(y[i,orp,P]for P in pats[r])==120)
        for w in W:m.Add(sum(P.count(w)*y[i,orp,P]for P in pats[r])==sum(x[t,i,orp,w]for t in times))
        for S in SUBS:
            meet=sum(y[i,orp,P]for P in pats[r]if any(w in P for w in S))
            for t in times:m.Add(sum(x[t,i,orp,w]for w in S)<=meet)
    for (i,orp,times,S,k)in cuts:
        r=win[orp,i][0];m.Add(sum(x[t,i,orp,w]for t in times for w in S)<=sum(min(k,sum(P.count(w)for w in S))*y[i,orp,P]for P in pats[r]))
    for t in range(T):
        for w in W:m.Add(sum(x[t,i,orp,w]for(orp,i),(r,times)in win.items()if t in times)==nw[w])
    SC=1000;m.Minimize(sum(int(round(SC*g(r-sum(P))))*y[i,orp,P]for(orp,i),(r,times)in win.items()for P in pats[r]))
    if hint:
        for k,v in hint['x'].items():
            if k in x:m.AddHint(x[k],v)
        for k,v in hint['y'].items():
            if k in y:m.AddHint(y[k],v)
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=LIM;s.parameters.num_workers=8;st=s.Solve(m)
    if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        raise SystemExit('No feasible allocation: '+s.StatusName(st)+'; output not written')
    X={k:s.Value(v)for k,v in x.items()};Y={k:s.Value(v)for k,v in y.items()}
    return dict(status=s.StatusName(st),obj=s.ObjectiveValue()/SC,bound=s.BestObjectiveBound()/SC,x=X,y=Y)
def nominate(sol):
    """returns dict (i,orp)->port assignment or None, and new cuts"""
    fails=[];assign={}
    for (orp,i),(r,times)in win.items():
        xs={(t,w):v for (t,ii,oo,w),v in sol['x'].items()if(ii,oo)==(i,orp)and v}
        ports=[]
        for P in pats[r]:ports+=[P]*sol['y'][i,orp,P]
        need=[Counter(P)for P in ports];ts=sorted({t for t,w in xs})
        m=cp_model.CpModel();z={}
        for (t,w),v in xs.items():
            for p in range(120):
                if need[p][w]:z[t,w,p]=m.NewBoolVar('')
            m.Add(sum(z[t,w,p]for p in range(120)if(t,w,p)in z)==v)
        for p in range(120):
            for w in need[p]:m.Add(sum(z[t,w,p]for t in ts if(t,w,p)in z)==need[p][w])
            for t in ts:
                vs=[z[t,w,p]for w in need[p]if(t,w,p)in z]
                if len(vs)>1:m.Add(sum(vs)<=1)
        s=cp_model.CpSolver();s.parameters.max_time_in_seconds=30;s.parameters.num_workers=8;st=s.Solve(m)
        if st in(cp_model.OPTIMAL,cp_model.FEASIBLE):
            assign[i,orp]=[(t,w,p)for (t,w,p),var in z.items()if s.Value(var)];continue
        # find violated top-k cuts
        found=0
        for S in SUBS:
            load={t:sum(v for (tt,w),v in xs.items()if tt==t and w in S)for t in ts};tl=sorted(ts,key=lambda t:-load[t])
            slots=[sum(P.count(w)for w in S)for P in ports]
            for k in range(1,len(tl)+1):
                lhs=sum(load[t]for t in tl[:k]);rhs=sum(min(k,c)for c in slots)
                if lhs>rhs:cuts.append((i,orp,tl[:k],S,k));found+=1;break
        fails.append((i,orp,found,s.StatusName(st)))
    return assign,fails
hint=None
for it in range(ITERS):
    t0=time.time();sol=solve(hint);hint=sol
    assign,fails=nominate(sol)
    rem=Counter()
    for (orp,i),(r,times)in win.items():
        for P in pats[r]:
            v=sol['y'][i,orp,P]
            if v and r-sum(P):rem[r-sum(P)]+=v
    print(f"iter {it} {sol['status']} obj {sol['obj']:.1f} bound {sol['bound']:.1f} fails {len(fails)} cuts {len(cuts)} rem {dict(sorted(rem.items()))} t {time.time()-t0:.0f}s",flush=True)
    if fails:print('  fails',fails[:8],flush=True)
    if not fails or all(f[2]==0 for f in fails):break
out=dict(status=sol['status'],objective=sol['obj'],bound=sol['bound'],remainders={str(k):v for k,v in sorted(rem.items())},widths=nw,order=plan['order'],
    x=[[t,i,orp,w,v]for (t,i,orp,w),v in sol['x'].items()if v],y=[[i,orp,list(P),v]for (i,orp,P),v in sol['y'].items()if v],
    assign={f'{i},{orp}':a for (i,orp),a in assign.items()},fails=fails,cuts=[[i,orp,ts,list(S),k]for i,orp,ts,S,k in cuts])
json.dump(out,open(OUT,'w'));print('written',OUT,'unresolved fails',len(fails),flush=True)
