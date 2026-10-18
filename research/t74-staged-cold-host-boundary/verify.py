"""Exact host-only staged recovery obstruction for PR2823 pair 473->277.
New scoped analysis for Yiyang, with substantial OpenAI Codex assistance.
Inherits PR2823's immutable Model/recovery implementation, credited in output.
"""
import sys,json,gzip,hashlib,types
from fractions import Fraction
from collections import defaultdict
from pathlib import Path
BASE=Path(__file__).resolve().parent

def require(p,message):
 if not p:raise ValueError(message)

def authenticate():
 manifest=json.loads((BASE/'SOURCE-PINS.json').read_text())
 authenticated={}
 for pin in manifest['files']:
  data=(BASE/pin['path']).read_bytes()
  require(hashlib.sha256(data).hexdigest()==pin['sha256'],'source SHA256 mismatch: '+pin['path'])
  require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==pin['git_blob'],'source Git blob mismatch')
  authenticated[pin['path']]=data
 return authenticated

# Compile exactly the authenticated source bytes, bypassing import and stale pyc.
AUTHENTICATED=authenticate()
_engine_path=BASE/'vendor/frame_engine.py'
ENGINE=types.ModuleType('pinned_frame_engine')
ENGINE.__file__=str(_engine_path)
exec(compile(AUTHENTICATED['vendor/frame_engine.py'],str(_engine_path),'exec'),ENGINE.__dict__)
Model,recovery,join,subset,regs,basis=(getattr(ENGINE,n) for n in ('Model','recovery','join','subset','regs','basis'))

def prefix_invertible(w,cut):
 n=2*w['report']['v']+w['report']['R'];live=set(range(n))-set(w['removed'])
 prefix=w['precondition']+w['compensation']+w['A']+w['cut']+w['B'][:cut]
 for g in prefix:
  require(set(regs(g))<=live,'prefix touches a non-live register')
  if g[0]=='add':require(g[1]!=g[2] and g[4]!=0,'noninvertible shear')
  elif g[0]=='scale':require(g[2]!=0 and g[3]!=0,'noninvertible scale')
  elif g[0]=='warp':require(1<=abs(g[2])<=len(w['warps']),'unknown inverse operator')
  else:require(False,'unknown prefix event')
 for c in w['initial_corrections']:
  require(c['source'] in live and c['target'] in live and c['source']!=c['target'],'noninvertible correction shear')
  require(all(1<=abs(op)<=len(w['warps']) for op in c['operator_word']),'unknown correction operator')
 for rec in w['warps']:
  require(len(rec[2])==9 and len(basis(tuple(rec[2])))==9,'singular warp')
 return dict(live_registers=len(live),scalar_and_A_warp_events=len(prefix),correction_shears=len(w['initial_corrections']),warp_matrices=len(w['warps']))

def check(w):
 m=Model(w);require(not m.violations,'baseline frames infeasible')
 rr,_=recovery(w,m);first=rr[0]
 require(first['section']=='B' and first['slot']==1202,'last-use boundary changed')
 require(first['expression']=={'277':'1','100':'-1','226':'-1','54':'1'},'required recovery changed')
 cut=1202;host=277;prefix=prefix_invertible(w,cut)
 require(all(rec[0]<cut for rec in w['warps']),'future warp/equality pin outside theorem scope')
 require(not any(host in regs(g) for g in w['B'][cut:]+w['restore']),'host used after staged cut')
 require(not any(rec[1]==host and rec[0]>=cut for rec in w['warps']),'host warped after staged cut')
 H=m.floor(host,m.positions['B',cut-1]);require(len(H)==7,'host floor changed')
 pairs=[(100,112,1429),(67,169,1430)];witnesses=[]
 for q,t,i in pairs:
  require(w['B'][i][0]=='add' and w['B'][i][1:3]==[t,q],'forced future target read changed')
  require(33 in H and not subset((33,),m.end[t]),'target port obstruction absent')
  require((33&w['ports'][t-m.v]).bit_count()%2==1,'port parity witness invalid')
  require(not any(rec[1] in (q,t,host) and rec[0]>=cut for rec in w['warps']),'intervening warp invalidates monotone witness')
  U=m.floor(q,m.positions['B',i]);require(len(join(H,U))==9,'late host read not full rank')
  witnesses.append(dict(source=q,target=t,target_read=i,missing_vector=33,source_floor_after=list(U),late_join_rank=9))
 # Track a perturbation of only register100 at the cut through every inherited event.
 # The inherited prefix is invertible, so this cut coordinate is independent.
 a=defaultdict(Fraction,{100:Fraction(1)});ever=set(a);nonzero_steps=0
 for sec,seq in [('B',w['B'][cut:]),('restore',w['restore'])]:
  for offset,g in enumerate(seq):
   i=offset+cut if sec=='B' else offset
   require(g[0] in ('add','scale'),'unsupported scalar event')
   if g[0]=='add':a[g[1]]+=Fraction(g[3],g[4])*a[g[2]]
   else:a[g[1]]*=Fraction(g[2],g[3])
   a=defaultdict(Fraction,{r:c for r,c in a.items() if c});ever.update(a)
   require(set(a)<= {100,67,112,169},'cut coordinate reaches another register')
   nonzero_steps+=1
 require(ever=={100,67,112,169},'support fixture changed')
 require(a=={100:Fraction(1),67:Fraction(-1,2),112:Fraction(-1,2),169:Fraction(-1,2)},'final coordinate changed')
 return dict(prefix_invertibility=prefix,status='PASS_HOST_ONLY_STAGED_BLOCKER',host_floor=list(H),cut=dict(section='B',slot=cut),required_a_coefficient='-1',coordinate_support=sorted(ever),source_read_witnesses=witnesses,propagated_events=nonzero_steps)

def main():
 out=[]
 for label in 'be':
  p=BASE/f'inputs/hosted-{label}-473-277.json.gz';data=AUTHENTICATED[f'inputs/hosted-{label}-473-277.json.gz'];w=json.loads(gzip.decompress(data));r=check(w)
  # Positive control: reading54 alone at the same cut is legal at rank8.
  mm=Model(w);H=mm.floor(277,mm.positions['B',1201]);U=join(H,mm.floor(54,mm.positions['B',1201]))
  fixture=Model(w,('B',1202,[54]),(277,U),True)
  require(len(U)==8 and not fixture.violations,'positive staged read failed')
  import copy
  rejected=[]
  mutants=[]
  bad=copy.deepcopy(w);bad['B'][1429][2]=54;mutants.append(('changed-coordinate-target-read',bad))
  bad=copy.deepcopy(w);bad['restore'].append(['add',277,54,1,1,list(U)]);mutants.append(('inherited-host-tail-use',bad))
  bad=copy.deepcopy(w);bad['A'].append(['scale',54,0,1,[]]);mutants.append(('noninvertible-prefix',bad))
  for name,bad in mutants:
   try:check(bad)
   except (ValueError,ZeroDivisionError,IndexError):rejected.append(name)
   else:require(False,'mutant accepted: '+name)
  r.update(provider=label,input_sha256=hashlib.sha256(data).hexdigest(),positive_controls=['rank8-single-read54'],rejected_mutants=rejected);out.append(r)
 print(json.dumps(dict(schema=1,scope='Only additional host277-targeting scalar gates after its final inherited B read; fixed other scalar gates, warps and target ends, arbitrary refits and arbitrary staging; host end rank<=8. No new precomputation or writes to other registers.',inherited_engine_sha256=hashlib.sha256(AUTHENTICATED['vendor/frame_engine.py']).hexdigest(),results=out),indent=2))
if __name__=='__main__':main()
