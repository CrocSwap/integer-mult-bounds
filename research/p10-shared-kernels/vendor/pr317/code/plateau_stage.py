#!/usr/bin/env python3
"""Literal ascent retiming, preserving the complete signed scalar/COPY event sequence.
Usage: scalar_plateau_apply.py INPUT SELECTION OUTPUT
"""
import json,sys,hashlib,shutil,struct,math
from array import array
from pathlib import Path
from collections import Counter
from functools import lru_cache
if not __debug__:raise SystemExit('assertions required')
P,SELP,O=map(Path,sys.argv[1:4]);assert P.resolve()!=O.resolve()
S=json.loads((P/'249-states.json').read_text());FJ=json.loads((P/'frames.json').read_text());F={int(k):v for k,v in FJ['frames'].items()};H=FJ['h'];M=5*H
V,n=S['v'],S['n'];I={int(k):v for k,v in S['initial'].items()};FINAL={int(k):v for k,v in S['final'].items()}
R=array('i');R.frombytes((P/'COHORT249-RECORDS.bin').read_bytes());N=len(R)//6
sha=lambda b:hashlib.sha256(b).hexdigest();sel=json.loads(SELP.read_text());assert sha(R.tobytes())==sel['input_raw_sha256']==S['record_sha256'];assert N==S['record_count']
# This emission presently admits only inherited exact frames.
assert not sel['new_frames'];D={k:v['dim']for k,v in F.items()}
@lru_cache(None)
def sub(a,b):return D[a]<=D[b] and all(sum(x*y for x,y in zip(ar,br))==0 for ar in F[b]['A']for br in F[a]['B'])
retime={}
for g in sel['gates']:
 i,old,new=g['record'],g['old_frame'],g['new_frame'];assert i not in retime and R[6*i]==1 and R[6*i+4]==old and D[new]>D[old] and sub(old,new);retime[i]=new
assert retime
out=array('i');state=dict(I);center=None;pairs=set()
def move(a,f):
 old=state[a]
 if old==f:return
 assert sub(old,f),(a,old,f)
 delta=D[f]-D[old];assert delta>=0 and len(F[old]['A'])-len(F[f]['A'])==delta
 out.extend((0,a,old,f,delta,0));state[a]=f;pairs.add((old,f))
for i in range(N):
 op,a,b,c,f,z=R[6*i:6*i+6]
 if op==1:
  f=retime.get(i,f);move(a,f);move(b,f);out.extend((op,a,b,c,f,z))
 elif op==2:
  assert center is None;move(a,c);out.extend((op,a,b,c,f,z));state[b]=f;center=(a,b,c)
 elif op==3:
  assert center==(a,b,c) and state[a]==c and state[b]==f;out.extend((op,a,b,c,f,z));del state[b];center=None
for a,f in sorted(FINAL.items()):move(a,f)
assert center is None and state==FINAL

def event_sequence(word):
 return [tuple(word[k:k+4])+tuple(word[k+5:k+6]) if word[k]==1 else tuple(word[k:k+6]) for k in range(0,len(word),6)if word[k]!=0]
assert event_sequence(R)==event_sequence(out),'signed scalar word changed'

def legality(word):
 state=dict(I);hist=Counter();center=None;cols=[1<<i for i in range(n)]+[0]
 for k in range(0,len(word),6):
  op,a,b,c,f,z=word[k:k+6]
  if op==0:
   assert state[a]==b and sub(b,c) and D[c]-D[b]==f and len(F[b]['A'])-len(F[c]['A'])==f
   state[a]=c
   if f:hist[f]+=1
  elif op==1:
   assert a!=b and c%2 and state[a]==state[b]==f
   if center is not None:assert a not in(center,n)
   cols[a]^=cols[b]
  elif op==2:
   assert center is None and b==n and state[a]==c and z==D[c];state[n]=f;cols[n]=cols[a];center=a;hist[z]+=1
  elif op==3:
   assert center==a and b==n and state[a]==c and state[n]==f;del state[n];cols[n]=0;center=None
  else:raise AssertionError(op)
 want=[1<<i for i in range(n)]
 for t in range(V):want[V+t]^=1<<t
 assert cols[:n]==want and state==FINAL and center is None
 return hist
oldhist=legality(R);hist=legality(out)
# Independent inverse payload run (every formal dirty/source/target column).
cols=[1<<i for i in range(n)]+[0];center=None
for k in range(len(out)-6,-1,-6):
 op,a,b,c,f,z=out[k:k+6]
 if op==1:cols[a]^=cols[b]
 elif op==3:assert center is None;center=a;cols[n]=cols[a]
 elif op==2:assert center==a;center=None;cols[n]=0
want=[1<<i for i in range(n)]
for t in range(V):want[V+t]^=1<<t
assert cols[:n]==want and center is None
# Exact source content changes in the same signed order; every retimed frame
# contains its old frame. Hence every old source-span incidence remains legal.
# Direct arbitrary-integer output check provides an additional independent test.
content=[[0]*H for _ in range(n+1)]
for i in range(V):assert D[I[i]]==1;content[i]=list(F[I[i]]['B'][0])
checked=bad=0;cache={};maxabs=0
for k in range(0,len(out),6):
 op,a,b,c,f,z=out[k:k+6]
 if op==1:
  for r in(a,b):
   if V<=r<2*V or r==n:continue
   key=(f,tuple(content[r]))
   if key not in cache:cache[key]=all(sum(x*y for x,y in zip(ar,content[r]))==0 for ar in F[f]['A'])
   checked+=1;bad+=not cache[key]
  content[a]=[x+c*y for x,y in zip(content[a],content[b])];maxabs=max(maxabs,max(map(abs,content[a]),default=0))
 elif op==2:content[n]=list(content[a])
 elif op==3:content[n]=[0]*H
assert not bad
phi=lambda h:sum(c*d*math.log(M/d)for d,c in h.items()if d)
delta=hist.copy();delta.subtract(oldhist);delta={str(d):c for d,c in sorted(delta.items())if c};saving=phi(oldhist)-phi(hist)
assert abs(saving-sel['local_phi_saving'])<1e-6 and sum(int(d)*c for d,c in delta.items())==0
O.mkdir(exist_ok=True)
for p in P.iterdir():
 if p.is_file():shutil.copy2(p,O/p.name)
raw=out.tobytes();outsha=sha(raw)
for name in('COHORT249-RECORDS.bin','249-records.bin'):O.joinpath(name).write_bytes(raw)
S.update(record_sha256=outsha,record_count=len(out)//6);O.joinpath('249-states.json').write_text(json.dumps(S,sort_keys=True,indent=2)+'\n')
compact_sha=None
if (P/'SOURCE-BINDING.json').exists():
 bind=json.loads((P/'SOURCE-BINDING.json').read_text());freed=set(bind['freed_roles']);mp={r:i for i,r in enumerate(r for r in range(n)if r not in freed)};mp[n]=len(mp)
 compact=b''.join(struct.pack('<6i',op,mp[a],b if op==0 else mp[b],c,f,z) for op,a,b,c,f,z in struct.iter_unpack('<6i',raw));compact_sha=sha(compact);O.joinpath('COMPACT-RECORDS.bin').write_bytes(compact)
 bind.update(word_sha256=outsha,compact_word_sha256=compact_sha);O.joinpath('SOURCE-BINDING.json').write_text(json.dumps(bind,sort_keys=True,indent=2)+'\n')
shutil.copyfile(SELP,O/'PLATEAU-SELECTION.json')
receipt=dict(status='PASS_ACTUAL_SIGNED_WORD_PRESERVING_PLATEAU_ASCENT',input_record_sha256=sel['input_raw_sha256'],output_record_sha256=outsha,compact_word_sha256=compact_sha,selection_sha256=sha(SELP.read_bytes()),records_in=N,records_out=len(out)//6,retimed_adds=len(retime),new_frames=0,signed_scalar_and_copy_word_unchanged=True,forward=True,inverse=True,all_independent_columns=n,dirty_restoration=True,both_reflected_local_ledgers=True,checked_frame_pairs=len(pairs),source_span_checked=checked,source_span_violations=bad,maximum_absolute_source_coefficient=maxabs,paid_histogram=dict(sorted(hist.items())),histogram_delta=delta,local_phi_saving=saving)
O.joinpath('PLATEAU-STAGE.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(json.dumps(receipt,indent=1))
