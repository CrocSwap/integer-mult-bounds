"""Whole signed provider audit; candidate and admitted reference are inputs."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,struct,hashlib,sys
P=Path(sys.argv[1]).resolve();REF=Path(sys.argv[2]).resolve();OUT=Path(sys.argv[3]).resolve();OUT.mkdir(parents=True,exist_ok=True)
E=list(struct.iter_unpack('<6i',(P/'signed-records.bin').read_bytes()));F=json.load(open(P/'records/frames.json'))['frames'];st=json.load(open(P/'records/249-states.json'));ref=json.load(open(REF/'decoder-and-dirt.json'));n=980
initial=[{i:Q(1)}for i in range(n)]+[{}]
def adds(A,d,s,c):
 for k,x in list(A[s].items()):
  A[d][k]=A[d].get(k,0)+c*x
  if not A[d][k]:del A[d][k]
def contained(a,b):return all(sum(Q(x)*Q(y)for x,y in zip(u,v))==0 for u in F[str(a)]['B']for v in F[str(b)]['A'])
def replay(events,A=None,reverse=False):
 A=[dict(r)for r in initial]if A is None else[dict(r)for r in A];state={int(k):v for k,v in(st['final']if reverse else st['initial']).items()};H=Counter();units=0;prefix=1
 for op,a,b,c,f,z in events:
  if op==0:
   old,new=(c,b)if reverse else(b,c);assert state[a]==old
   assert contained(new,old)if reverse else contained(old,new)
   state[a]=new;H[abs(F[str(c)]['dim']-F[str(b)]['dim'])]+=1
  elif op==1:
   assert state[a]==state[b]==f;adds(A,a,b,-c if reverse else c);units+=abs(c);prefix=max(prefix,sum(map(abs,A[a].values())))
  elif op==(3 if reverse else 2):
   assert b==980 and b not in state and state[a]==c;A[b]=dict(A[a]);state[b]=f;H[8]+=1
  elif op==(2 if reverse else 3):
   assert b==980 and state[a]==c and state[b]==f and A[a]==A[b];A[b]={};state.pop(b)
  else:raise AssertionError(op)
 assert state=={int(k):v for k,v in(st['initial']if reverse else st['final']).items()};H.pop(0,None)
 return A,H,units,prefix
actual,H,units,prefix=replay(E);expected=[dict(r)for r in initial]
for t,row in enumerate(ref['M']):
 for k,x in row.items():expected[120+t][int(k)]=expected[120+t].get(int(k),0)+Q(x)
assert actual==expected,'Provider does not implement entire admitted Z operator with arbitrary dirty targets/helpers'
back,Hback,_,backprefix=replay(list(reversed(E)),actual,True);assert back==initial and Hback==H
# Independent adjoint propagation of each target output through actual ADD,
# COPY and ERASE assignment matrices (scratch input fixed zero).
for t in range(120):
 cov={120+t:Q(1)}
 for op,a,b,c,f,z in reversed(E):
  if op==1:cov[b]=cov.get(b,0)+c*cov.get(a,0)
  elif op==2:cov[a]=cov.get(a,0)+cov.get(b,0);cov[b]=0
  elif op==3:cov[b]=0
 assert {k:x for k,x in cov.items()if x and k<980}==expected[120+t]
# A provider may change dirty compensation and cold kernel events. Compare
# the actual clean source rows at EVERY surviving labelled scalar incidence
# against a separately supplied admitted caller, rather than trusting spans.
clean_source_ledger=None
if len(sys.argv)>4:
 BASE=Path(sys.argv[4]).resolve()
 def ledger(events):
  A=[{i:Q(1)}if i<120 else{}for i in range(981)];seen=Counter();snap={}
  for e in events:
   op,a,b,c,f,z=e
   if op==1:
    key=(e,seen[e]);seen[e]+=1;snap[key]=(tuple(sorted(A[a].items())),tuple(sorted(A[b].items())))
    adds(A,a,b,c)
   elif op==2:A[b]=dict(A[a])
   elif op==3:A[b]={}
  return snap
 old=ledger(list(struct.iter_unpack('<6i',(BASE/'signed-records.bin').read_bytes())));new=ledger(E);common=old.keys()&new.keys()
 for key in common:assert old[key]==new[key],('changed fresh source response at surviving scalar',key)
 clean_source_ledger=dict(common_signed_scalar_incidences=len(common),all_actual_clean_source_rows_identical=True,baseline_sha256=hashlib.sha256((BASE/'signed-records.bin').read_bytes()).hexdigest())
result=dict(status='PASS_INDEPENDENT_SIGNED_PROVIDER_ALL980_DIRT_FRAME_LITERAL_INVERSE',columns=980,independent_target_adjoints=120,whole_admitted_decoder=True,clean_source_ledger=clean_source_ledger,profile=dict(H),rankmass=sum(r*c for r,c in H.items()),signed_unit_additions=units,actual_row_norm_prefix=str(prefix),inverse_from_endpoint_prefix=str(backprefix),initial_frame_rank=sum(F[str(f)]['dim']for h,f in st['initial'].items()if int(h)>=240),pins={f:hashlib.sha256((P/f).read_bytes()).hexdigest()for f in ['signed-records.bin','records/frames.json','records/249-states.json','word.json']},reference_decoder_sha256=hashlib.sha256((REF/'decoder-and-dirt.json').read_bytes()).hexdigest(),scope='Complete signed local operator equality and exact rational monotone frame ledger. Different positiveentrances/residualowner allocation require freshglobal hosting/inventory/commonframe sourcefunctional and fullinvoice; no rowwiseF2/Q-span transfer.')
(OUT/'LOCAL.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
