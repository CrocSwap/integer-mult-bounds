"""Original exact adversarial check of reset compensation; no upstream imports."""
import sys,os
if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):raise RuntimeError('Assertions required')
from fractions import Fraction as F
from random import Random
from pathlib import Path
import json,time,resource
T0=time.monotonic()
def add(a,b,c=F(1)):
 for i,x in enumerate(b):a[i]+=c*x

def response(events,R,X,Y,cut=True):
 B=[[F(0)for _ in range(Y)]for _ in range(R)];M=[[F(0)for _ in range(Y)]for _ in range(X)];D={}
 for k in range(len(events)-1,-1,-1):
  e=events[k];kind,r=e[:2]
  if kind=='read':_,r,t,c=e;B[r][t]+=c
  elif kind=='gate':_,r,s,c=e;add(B[s],B[r],c)
  elif kind=='source':_,r,j,c=e;add(M[j],B[r],c)
  elif kind=='birth':
   D[k]=B[r][:]
   if cut:B[r]=[F(0)for _ in range(Y)]
  else:raise AssertionError(e)
 return B,M,D

def run(events,R,X,Y,x,z,D=None,uncompute=True,omit=None,fresh_only=False):
 a=z[:];out=[F(0)for _ in range(Y)];gates=[];births=[]
 for k,e in enumerate(events):
  kind,r=e[:2]
  if kind=='birth':
   if D is None:a[r]=F(0)
   else:
    g=a[r];births.append((k,g))
    if k!=omit:
     for t,d in enumerate(D[k]):out[t]-=d*g
  elif kind=='gate':_,r,s,c=e;a[r]+=c*a[s];gates.append(e)
  elif kind=='source':_,r,j,c=e;a[r]+=c*x[j];gates.append(e)
  elif kind=='read':_,r,t,c=e;out[t]+=c*a[r]
 if D is not None and uncompute:
  for e in reversed(gates):
   kind,r,j,c=e;a[r]-=c*(a[j]if kind=='gate'else x[j])
 return out,a,births
rng=Random(114113);basis_checks=0;dependent_nonzero_births=0;coefficient_max=F(0)
for case in range(96):
 R=1+case%5;X=1+(case//5)%4;Y=1+(case//20)%4
 events=[('birth',r)for r in range(R)]
 for step in range(24):
  kind=rng.choice(['birth','source','read','gate']if R>1 else['birth','source','read'])
  r=rng.randrange(R);c=rng.choice([F(1),F(-1),F(2),F(-2),F(1,2),F(-1,3)])
  if kind=='birth':events.append((kind,r))
  elif kind=='source':events.append((kind,r,rng.randrange(X),c))
  elif kind=='read':events.append((kind,r,rng.randrange(Y),c))
  else:
   s=rng.choice([i for i in range(R)if i!=r]);events.append((kind,r,s,c))
 # Force a genuinely used reuse with a nonzero old-source offset.
 events += [('source',0,0,F(1)),('read',0,0,F(1)),('birth',0),('source',0,0,F(2)),('read',0,Y-1,F(1))]
 B,M,D=response(events,R,X,Y);assert all(not any(row)for row in B)
 coefficient_max=max(coefficient_max,max((abs(c)for row in D.values()for c in row),default=F(0)))
 for b in range(X+R):
  x=[F(i==b)for i in range(X)];z=[F(X+i==b)for i in range(R)]
  expected=run(events,R,X,Y,x,[F(0)]*R)[0]
  actual,restored,births=run(events,R,X,Y,x,z,D)
  assert actual==expected and restored==z
  assert expected==[sum(M[i][t]*x[i]for i in range(X))for t in range(Y)]
  basis_checks+=1;dependent_nonzero_births+=sum(bool(g)for _,g in births)
 # Dense signed rational source/dirty inputs exercise dependent birth values.
 x=[F(rng.randrange(-7,8),rng.randrange(1,5))for _ in range(X)];z=[F(rng.randrange(-7,8),rng.randrange(1,5))for _ in range(R)]
 assert run(events,R,X,Y,x,z,D)[:2]==(run(events,R,X,Y,x,[F(0)]*R)[0],z)
# A one-slot two-life example: x0 is still in the slot at its second birth.
e=[('birth',0),('source',0,0,F(1)),('read',0,0,F(1)),('birth',0),('source',0,1,F(1)),('read',0,1,F(1))]
B,M,D=response(e,1,2,2);x=[F(3),F(5)];z=[F(7)]
out,restored,births=run(e,1,2,2,x,z,D);assert out==x and restored==z and births==[(0,F(7)),(3,F(10))]
controls={}
controls['omit_reuse_readout']=run(e,1,2,2,x,z,D,omit=3)[0]!=x
controls['do_not_cut_next_birth']=run(e,1,2,2,x,z,response(e,1,2,2,cut=False)[2])[0]!=x
controls['omit_inverse_workspace']=run(e,1,2,2,x,z,D,uncompute=False)[1]!=z
# Grouping negative source injections at the end fails after role aliasing.
e2=[('birth',0),('birth',1),('source',0,0,F(1)),('gate',1,0,F(1)),('read',1,0,F(1)),('birth',0),('source',0,1,F(1)),('read',0,1,F(1))]
_,_,D2=response(e2,2,2,2);z2=[F(7),F(11)]
assert run(e2,2,2,2,x,z2,D2)[:2]==(x,z2)
a=run(e2,2,2,2,x,z2,D2,uncompute=False)[1]
for kind,r,s,c in reversed([v for v in e2 if v[0]=='gate']):a[r]-=c*a[s]
for kind,r,j,c in reversed([v for v in e2 if v[0]=='source']):a[r]-=c*x[j]
controls['group_negative_sources_at_end']=a!=z2
# The gate/readout model forbids source-target-workspace aliasing by construction.
assert all(controls.values())
result=dict(status='PASS exact scalar lemma controls; no actual114 word or bound yet',cases=96,complete_source_dirty_basis_vectors=basis_checks,dense_rational_cases=96,nonzero_dependent_birth_values=dependent_nonzero_births,largest_test_response_coefficient=str(coefficient_max),rejected_controls=controls,one_slot_example=dict(source=['3','5'],dirty='7',birth_values=['7','10'],output=['3','5'],restored='7'),seconds=time.monotonic()-T0,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
Path(__file__).with_name('CHECKS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
