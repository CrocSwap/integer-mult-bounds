#!/usr/bin/env python3
EXPECTED_OUTPUT_SHA256='a972abfe4fcd7f8b245b06a3af7a2131a1f1635ea6076ecdcce870cce19d2526'
import sys
if not __debug__: raise SystemExit("Assertions required; refusing -O")
sys.dont_write_bytecode = True
import json,hashlib,struct,time,argparse
from array import array
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import sympy as sp
from sympy.polys.matrices import DomainMatrix
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--source-dir',type=Path,required=True);ap.add_argument('--export-dir',type=Path,required=True);ap.add_argument('--screen',type=Path,required=True);a=ap.parse_args();t=time.time();D=Path(__file__).parent;P=a.source_dir;X=a.export_dir;out=a.output;out.mkdir(parents=True,exist_ok=True)
def load(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
screen=load(a.screen);cut=screen['cut'];edits=sorted(screen['candidates'],key=lambda e:e['role'])[:438];assert len(edits)==438 and len(screen['candidates'])==440;A={e['role']for e in edits};skip={e['incidences'][0][0]for e in edits};assert all(len(e['incidences'])==1 for e in edits)   # 40 replicas: 438*40 slots of width 3 tile 146 banks exactly;A={e['role']for e in edits};skip={e['incidences'][0][0]for e in edits};assert all(len(e['incidences'])==1 for e in edits)
base=load(X/'249-states.json');MOVED=base['physical']['category_names'].index('cleanup_gate');n,v=base['n'],base['v'];fs={int(k):r for k,r in load(X/'frames.json')['frames'].items()};extras=load(P/'COHORT249-FRAMES.json');fs.update({int(k):r for k,r in extras.items()});newfs={e['frame']:screen['newframes'][str(e['frame'])]for e in edits}
for z in newfs.values():   # exact integer annihilator rows for the native checkers
 z['A']=[[(lambda q:(q.numerator if q.denominator==1 else (_ for _ in ()).throw(AssertionError('non-integral annihilator entry'))))(Q(str(x)))for x in row]for row in z['A']]
assert not set(newfs).intersection(fs);fs.update(newfs)
initial={int(k):f for k,f in load(P/'COHORT249-INITIAL.json').items()};final={int(k):f for k,f in load(P/'COHORT249-FINAL.json').items()};final.update({e['role']:e['frame']for e in edits});state=dict(initial)
q=2**127-1;G=9*sp.eye(24)-sp.ones(24);aud=[]
for f,z in newfs.items():
 B=sp.Matrix(z['B']);AA=sp.Matrix(z['A']);d=z['dim'];assert B.shape==(d,24) and AA.shape==(24-d,24);assert AA*B.T==sp.zeros(24-d,d);assert DomainMatrix.from_Matrix(AA).rank()==24-d
 det=sp.Rational(DomainMatrix.from_Matrix(B*G*B.T).det());assert det and int(det.p)%q and int(det.q)%q
 aud.append(dict(frame=f,dim=d,cleared_gram_determinant=str(det)))
print('exact newframes',len(aud),'seconds',time.time()-t,flush=True)
raw=(P/'COHORT249-RECORDS.bin').read_bytes();old=array('i');old.frombytes(raw)
# Each moved gate commutes over Z with the entire crossed interval: no other
# use of its destination and no intervening write to its donor. Thus the exact
# signed scalar operator and original maximum coefficient bound are retained.
first_write={}; uses={role:[] for role in A}
for i in range(cut,len(old)//6):
 op,dest,src,coef,frame,tag=old[6*i:6*i+6]
 assert op not in (2,3), 'COPY lifetime crosses cleanup interval'
 if op==1:
  first_write.setdefault(dest,i)
  if dest in uses:uses[dest].append(i)
  if src in uses:uses[src].append(i)
for e in edits:
 idx=e['incidences'][0][0];role=e['role'];donor=e['donors'][0]
 assert uses[role]==[idx]
 assert tuple(old[6*idx:6*idx+3])==(1,role,donor)
 assert first_write.get(donor,len(old)//6)>idx
new=array('i');cols=[1<<i for i in range(n)]+[0];checked=set();inherited={(old[i+2],old[i+3])for i in range(0,len(old),6)if old[i]==0};basis={f:[[Q(x)for x in row]for row in z['B']]for f,z in fs.items()};ann={f:[[Q(x)for x in row]for row in z['A']]for f,z in fs.items()}
def move(role,f):
 before=state[role]
 if before==f:return
 if (before,f)not in inherited and (before,f)not in checked:
  assert all(sum(x*y for x,y in zip(u,w))==0 for u in basis[before]for w in ann[f]),('not nested',role,before,f);checked.add((before,f))
 rank=fs[f]['dim']-fs[before]['dim'];assert rank>=0
 new.extend((0,role,before,f,rank,0));state[role]=f
def emit(r):
 op,a,b,c,f,z=r
 if op==1:
  move(a,f);move(b,f)
  if c%2:cols[a]^=cols[b]
 elif op==2:
  move(a,c);assert b==n and cols[b]==0;cols[b]=cols[a];state[b]=f
 elif op==3:
  assert cols[a]==cols[b] and state[a]==c and state[b]==f;cols[b]=0;del state[b]
 else:raise AssertionError(r)
 new.extend(r)
movedkeys={(e['role'],e['donors'][0],e['frame'])for e in edits}
for i in range(len(old)//6):
 if i==cut:
  for e in edits:
   emit((1,e['role'],e['donors'][0],old[6*e['incidences'][0][0]+3],e['frame'],MOVED));assert cols[e['role']]==1<<e['role']
 r=old[6*i:6*i+6]
 if r[0]!=0 and i not in skip:emit(r)
for role in range(n):move(role,final[role])
expected=[(1<<i)^((1<<(i-v))if v<=i<2*v else 0)for i in range(n)]
assert cols==expected+[0];assert state==final
# Full reverse word with fresh COPY at each reverse ERASE and erase at each reverse COPY.
def reverse(start):
 cols=list(start)+[0];ss=dict(final)
 for i in range(len(new)//6-1,-1,-1):
  op,a,b,c,f,z=new[6*i:6*i+6]
  if op==0:assert ss[a]==c;ss[a]=b
  elif op==1:
   assert ss[a]==ss[b]==f
   if c%2:cols[a]^=cols[b]
  elif op==3:assert cols[b]==0 and b not in ss and ss[a]==c;cols[b]=cols[a];ss[b]=f
  elif op==2:assert cols[a]==cols[b] and ss[a]==c and ss[b]==f;cols[b]=0;del ss[b]
 assert ss==initial
 return cols
assert reverse([1<<i for i in range(n)])==expected+[0]
assert reverse(expected)==[1<<i for i in range(n)]+[0]
# Omit one moved restoration: corruption must be detected on the full formal basis.
bad=[1<<i for i in range(n)]+[0];omitted=False
for i in range(0,len(new),6):
 op,a,b,c,f,z=new[i:i+6]
 if op==1:
  if (a,b,f) in movedkeys and not omitted:omitted=True
  elif c%2:bad[a]^=bad[b]
 elif op==2:bad[b]=bad[a]
 elif op==3:assert bad[a]==bad[b];bad[b]=0
wrong=sum(x!=y for x,y in zip(bad,expected+[0]));assert wrong

def hist(r):
 H=Counter()
 for i in range(0,len(r),6):
  op,a,b,c,f,z=r[i:i+6]
  if op==0 and f:H[f]+=1
  elif op==2:H[z]+=1
 return H
H0=hist(old);H=hist(new);delta=H.copy();delta.subtract(H0);delta={str(r):c for r,c in sorted(delta.items())if c};assert delta=={'1':3*len(edits),'2':-2*len(edits)},delta;assert sum(int(r)*c for r,c in delta.items())==-len(edits)
blob=new.tobytes();print('OUTPUT_SHA',sha(blob),flush=True);assert sha(blob)==EXPECTED_OUTPUT_SHA256 if EXPECTED_OUTPUT_SHA256 else True;(out/'COHORT249-RECORDS.bin').write_bytes(blob);(out/'COHORT249-INITIAL.json').write_bytes((P/'COHORT249-INITIAL.json').read_bytes());(out/'COHORT249-FINAL.json').write_text(json.dumps(final,sort_keys=True)+'\n');extras.update({str(k):x for k,x in newfs.items()});(out/'COHORT249-FRAMES.json').write_text(json.dumps(extras,sort_keys=True)+'\n')
newstates=dict(base);newstates.update(initial=initial,final=final,record_count=len(new)//6,record_sha256=sha(blob));(out/'249-states.json').write_text(json.dumps(newstates,sort_keys=True)+'\n')
receipt=dict(status='PASS_EXACT_NEW_FRAMES_FORWARD_INVERSE_ROUNDTRIP',input_sha256=sha(raw),output_sha256=sha(blob),retired_helpers=len(edits),cut=cut,formal_columns=n,scalar_additions=len([i for i in range(0,len(new),6)if new[i]==1]),record_count=len(new)//6,histogram={str(r):c for r,c in sorted(H.items())},histogram_delta=delta,endpoint_rank_mass_drop=len(edits),exact_new_connector_pairs=len(checked),omission_wrong_rows=wrong,signed_scalar_operator_preserved_by_exact_commutation=True,maximum_formal_coefficient_bound_does_not_increase=True,frames_audit=aud,edits=edits,seconds=time.time()-t)
(out/'CLEANUP-REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n');print({k:x for k,x in receipt.items()if k not in ('edits','frames_audit','histogram')},flush=True)
