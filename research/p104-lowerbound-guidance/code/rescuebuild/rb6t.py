import sys;sys.path.insert(0,'.')
from rb6 import *
k=int(sys.argv[1]);bar=Dm(sys.argv[2]);cr=sys.argv[3]=='1'
m,c,O,val=build(k,bar=bar,cellrank=cr)
sv=cp_model.CpSolver();sv.parameters.num_workers=1;sv.parameters.enumerate_all_solutions=True;sv.parameters.max_time_in_seconds=600
cb=Col(c,200000);st=sv.Solve(m,cb);seen={}
for s in cb.sols:
    des=tuple(O[i] for i,x in enumerate(s) for _ in range(x));seen.setdefault(canon(k,des),float(sum(val[i]*x for i,x in enumerate(s))*104/k))
print('k',k,'bar',bar,'cr',cr,sv.StatusName(st),'raw',len(cb.sols),'canon',len(seen))
for d,v in sorted(seen.items(),key=lambda x:-x[1])[:8]:print(round(v,3),d)
