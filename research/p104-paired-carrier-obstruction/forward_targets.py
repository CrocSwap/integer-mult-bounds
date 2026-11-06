from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
import contextlib,io,runpy
from collections import Counter
checks=[];OUTDIR=Path(sys.argv[1])
for script,key in [(str(HERE/'adjacent.py'),'intervals'),(str(HERE/'disjoint.py'),'iv')]:
 sys.argv=[script,str(OUTDIR/(key+'.json'))]
 with contextlib.redirect_stdout(io.StringIO()):d=runpy.run_path(script)
 p=d['p'];w=d['w'];n=d['n'];N=d['N'];P=d['MOD'];q=d['scalar'];full={r for r,f in enumerate(w['final'])if f==127}
 for c in d[key]:
  err=[0]*N;obs={};exports=set(c['exports']);a=1;copy_index=0;copies=sum(e[0]=='COPY'for e in p)
  for i,e in enumerate(p):
   op,r=e[:2]
   if op=='COPY':
    if err[r]:obs[n+copies-1-copy_index]=err[r]
    copy_index+=1
   if i in exports:
    if err[e[2]]:raise ValueError('Removed export has source feedback')
    err[r]=(err[r]-q(e[3])*a)%P
   elif op in ('ADD','COPY'):err[r]=(err[r]+q(e[3])*err[e[2]])%P
   elif op=='SCALE':err[r]=err[r]*q(e[2])%P
   elif op in ('INIT','CLEAR'):err[r]=0
   if c['first']<i<c['second']and op=='SCALE'and r==c['role']:a=a*q(e[2])%P
  obs.update({r:err[r]for r in range(n)if r not in full and err[r]})
  expected={k:-v%P for k,v in c['target'].items()if v}
  if obs!=expected:raise ValueError('Forward target mismatch '+str((c['role'],c['first'],c['second'])))
  checks.append((c['role'],c['first'],c['second']))
print('PASS_FORWARD_COMBINED_ERROR',len(checks),'pair targets; all deleted-export source errors zero; final proper rows and COPY monitor match')
