"""Aggregate asynchronous whole-owner allocation (stage 1 of PR505's two-stage method, rebuilt).
Usage: aggregate_milp.py PLAN.json WIDTHS(json dict) OUT.json [seconds] [cost=phi|moment:c]
Variables: x[t,i,orp,w] roles of width w at call time t hosted on child (i,orp); y[i,orp,P] ports of (i,orp)
tiled by width multiset P. Each call places all its helpers; at most one role per call per port (whole owner);
patterns cover the 120 ports; cost = sum over ports of g(remainder)."""
import json,math,sys,itertools,time
from collections import Counter,defaultdict
from ortools.sat.python import cp_model
PLAN,WID,OUT=sys.argv[1:4];LIM=float(sys.argv[4])if len(sys.argv)>4 else 300;COST=sys.argv[5]if len(sys.argv)>5 else'phi'
plan=json.load(open(PLAN));nw={int(k):v for k,v in json.loads(WID).items()};M=73
if not nw or any(w<=0 or not isinstance(n,int) or n<0 for w,n in nw.items()):
    raise SystemExit('Widths must be positive integers with nonnegative integer counts')
order=[tuple(x)for x in plan['order']];T=len(order);assert T==72
win={tuple(map(int,k.split(','))):(v[0],sorted(v[1]))for k,v in plan['windows'].items()}   # (orp,i)->(rank,times)
ranks=sorted({r for r,_ in win.values()});W=sorted(nw)
def g(r):
    if r==0:return 0
    if COST=='phi':return r*math.log(M/r)
    c=float(COST.split(':')[1]);return r*(M/r)**c
def patterns(r):
    out=set()
    def rec(rem,start,cur):
        out.add(tuple(cur))
        for j in range(start,len(W)):
            if W[j]<=rem:rec(rem-W[j],j,cur+[W[j]])
    rec(r,0,[]);return sorted(out)
pats={r:patterns(r)for r in ranks};print({r:len(p)for r,p in pats.items()},flush=True)
m=cp_model.CpModel();x={};y={}
for (orp,i),(r,times)in win.items():
    for t in times:
        for w in W:x[t,i,orp,w]=m.NewIntVar(0,min(nw[w],120),f'x{t}_{i}_{orp}_{w}')
        m.Add(sum(x[t,i,orp,w]for w in W)<=120)
    for P in pats[r]:y[i,orp,P]=m.NewIntVar(0,120,f'y{i}_{orp}_{len(P)}_{hash(P)%10**6}')
    m.Add(sum(y[i,orp,P]for P in pats[r])==120)
    # Hall conditions for the literal nomination: roles of one call must sit in distinct ports, so for every
    # subset S of widths the roles of call t with widths in S need that many ports whose pattern meets S.
    for k in range(1,len(W)+1):
        for Sset in itertools.combinations(W,k):
            ports_meeting=sum(y[i,orp,P]for P in pats[r]if any(w in P for w in Sset))
            for t in times:m.Add(sum(x[t,i,orp,w]for w in Sset)<=ports_meeting)
    for w in W:m.Add(sum(P.count(w)*y[i,orp,P]for P in pats[r])==sum(x[t,i,orp,w]for t in times))
for t in range(T):
    for w in W:
        m.Add(sum(x[t,i,orp,w]for(orp,i),(r,times)in win.items()if t in times)==nw[w])
SC=1000
m.Minimize(sum(int(round(SC*g(r-sum(P))))*y[i,orp,P]for(orp,i),(r,times)in win.items()for P in pats[r]))
s=cp_model.CpSolver();s.parameters.max_time_in_seconds=LIM;s.parameters.num_workers=8;t0=time.time();st=s.Solve(m)
print('status',s.StatusName(st),'obj',s.ObjectiveValue()/SC,'bound',s.BestObjectiveBound()/SC,'t',round(time.time()-t0),flush=True)
if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):
    raise SystemExit('No feasible allocation: '+s.StatusName(st)+'; output not written')
rem=Counter();X=[];Y=[]
for (orp,i),(r,times)in win.items():
    for P in pats[r]:
        v=s.Value(y[i,orp,P])
        if v:rem[r-sum(P)]+=v;Y.append([i,orp,list(P),v])
    for t in times:
        for w in W:
            v=s.Value(x[t,i,orp,w])
            if v:X.append([t,i,orp,w,v])
rem={r:n for r,n in sorted(rem.items())if r}
print('remainders',rem,'phi',round(sum(n*r*math.log(M/r)for r,n in rem.items()),1),flush=True)
json.dump(dict(status=s.StatusName(st),objective=s.ObjectiveValue()/SC,bound=s.BestObjectiveBound()/SC,remainders=rem,widths=nw,order=plan['order'],x=X,y=Y,cost=COST),open(OUT,'w'))
