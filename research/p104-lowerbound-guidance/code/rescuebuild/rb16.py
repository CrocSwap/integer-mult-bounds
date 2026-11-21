"""rb16: mask-level SUP: maximize chat(.99) over designs under all encoded laws (CP-SAT, 1 thread). usage: rb16.py k [timelimit] [SKIP env]"""
import sys,os,time;sys.path.insert(0,'.')
from rb6 import *
k=int(sys.argv[1]);tl=float(sys.argv[2]) if len(sys.argv)>2 else 1800
m,c,O,val=build(k,bar=Dm(0),cellrank=True)
SC=10**6;obj=sum(c[i]*int(val[i]*SC) for i in range(len(O)));m.Maximize(obj)
sv=cp_model.CpSolver();sv.parameters.num_workers=1;sv.parameters.max_time_in_seconds=tl
t0=time.time();st=sv.Solve(m)
v=[sv.Value(x) for x in c];des=tuple(O[i] for i,x in enumerate(v) for _ in range(x))
best=float(sum(val[i]*x for i,x in enumerate(v))*104/k);ub=sv.BestObjectiveBound()/SC*104/k
print('k',k,'SKIP',os.environ.get('SKIP',''),sv.StatusName(st),'best %.3f  bound %.3f  t=%.0f'%(best,ub,time.time()-t0),flush=True)
print(canon(k,des))
