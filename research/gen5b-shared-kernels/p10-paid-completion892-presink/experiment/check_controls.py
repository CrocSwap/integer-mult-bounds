from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import companion as packet
packet.require_assertions()
packet.verify_base()
packet.verify_sources()
"""Hard negative controls for the isolated PR322/323 witness admission.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,gzip,hashlib,copy,subprocess,sys
if not __debug__:raise RuntimeError('Assertions required')
P=packet.EXPERIMENT;B=packet.BASE_FRAME
def read(p):
 x=Path(p).read_bytes();return json.loads(gzip.decompress(x)if str(p).endswith('.gz')else x)
R=read(P/'RESULT.json');bank=read(P/'BANK-RESULT.json');frames={int(k):v for k,v in read(P/'combined-frames.json.gz').items()};old_events=read(B/'local-events.json.gz');ends=read(B/'local-endpoints.json');selection=read(packet.INPUTS/'pr322-presink-selection.json')
def contained(basis,frame):return all(sum(Q(a)*Q(b)for a,b in zip(row,v))==0 for row in frames[frame]['annihilator']for v in basis)
def resolve(entry):
 c=lambda a:a-sum(v<a for v in ends['removed_sink_columns']);a,b,x,_=entry['scalar'];a,b=c(a),c(b)
 hits=[(i,e)for i,e in enumerate(old_events)if e['op']==1 and[e['a'],e['b'],e['c']]==[a,b,x]and e['semantic'][0]=='kernel_setup'];assert len(hits)==1
 i,e=hits[0];f=frames[e['frame']];basis=[[int(Q(x))for x in row]for row in f['basis']]
 assert f['rank']==entry['old_dimension']and hashlib.sha256(json.dumps(basis,separators=(',',':')).encode()).hexdigest()==entry['old_basis_sha256']
 assert entry['new_dimension']==len(entry['new_basis'])
 # The new frame must nest exactly between the actual preceding/following
 # frames of BOTH live operands, with current fixed endpoints.
 for s in [a,b]:
  prior=[z['frame']for z in old_events[:i]if z['a']==s or(z['op']==1 and z['b']==s)]
  later=[z['frame']for z in old_events[i+1:]if z['a']==s or(z['op']==1 and z['b']==s)]
  p=prior[-1]if prior else ends['initial'][str(s)];q=later[0]if later else ends['final'][str(s)]
  assert frames[p]['rank']<=len(entry['new_basis'])<=frames[q]['rank']
  # If lower frame is old entrance, inclusion follows rank plus solving a
  # full rational row span via an independent elimination test.
  A=[list(map(Q,row))for row in entry['new_basis']];piv=[];z=0
  for j in range(20):
   k=next((k for k in range(z,len(A))if A[k][j]),None)
   if k is None:continue
   A[k],A[z]=A[z],A[k];v=A[z][j];A[z]=[x/v for x in A[z]]
   for k in range(len(A)):
    if k!=z and A[k][j]:v=A[k][j];A[k]=[x-v*y for x,y in zip(A[k],A[z])]
   piv.append(j);z+=1
   if z==len(A):break
  assert z==len(entry['new_basis'])
  for row in frames[p]['basis']:
   v=list(map(Q,row))
   for row,j in zip(A,piv):
    q0=v[j];v=[x-q0*y for x,y in zip(v,row)]
   assert not any(v)
  assert contained(entry['new_basis'],q)
 return True
for e in selection['entries']:assert resolve(e)
controls=[]
def reject(name,fn):
 try:fn()
 except(AssertionError,KeyError):controls.append(name)
 else:raise AssertionError('Corruption accepted: '+name)
def mutate322(field,value):
 e=copy.deepcopy(selection['entries'][0]);e[field]=value;return resolve(e)
reject('stale_old_basis_sha',lambda:mutate322('old_basis_sha256','0'*64))
reject('changed_scalar_port',lambda:mutate322('scalar',[8725,8729,1,30]))
reject('wrong_new_rank',lambda:mutate322('new_dimension',8))
reject('wrong_old_rank',lambda:mutate322('old_dimension',9))
e=copy.deepcopy(selection['entries'][0]);e['new_basis'][0]=[int(j==0)for j in range(20)];reject('nonnested_constructed_basis',lambda:resolve(e))
# Independently validate emitted kernel entry cut triples and first-frame gates.
def kernel(e):
 ms=[e['pivot']]+e['donors'];assert len(set(ms))==4 and e['rank']==2 and len(e['basis'])==2
 assert all(ends['initial'][str(s)]==0 for s in ms)
 z=old_events[e['cut']];assert[z['a'],z['b'],z['c']]==e['cut_read']
 first={s:next(i for i,t in enumerate(old_events)if(t['a']==s or(t['op']==1 and t['b']==s))and not(t['op']==1 and t['b']==s and t['frame']==0 and t['semantic'][0]=='plain'))for s in ms}
 assert e['cut']<min(first.values())
 assert all(contained(e['basis'],old_events[first[s]]['frame'])for s in ms)
 return True
for e in R['new_kernel_entries']:assert kernel(e)
e=copy.deepcopy(R['new_kernel_entries'][0]);e['cut_read'][0]+=1;reject('wrong_cut_scalar_target',lambda:kernel(e))
e=copy.deepcopy(R['new_kernel_entries'][0]);e['cut']=len(old_events)-1;reject('setup_after_first_use',lambda:kernel(e))
e=copy.deepcopy(R['new_kernel_entries'][0]);e['donors'][0]=e['pivot'];reject('pivot_reused_as_donor',lambda:kernel(e))
e=copy.deepcopy(R['new_kernel_entries'][0]);e['basis'][0]=[int(j==0)for j in range(20)];reject('rank2_basis_outside_first_frame',lambda:kernel(e))
assert [x['wrong_rows']for x in R['omission_controls']]==[41,9];controls+=['omitted_kernel_setup_fails41rows','omitted_kernel_restoration_fails9rows']
def endpoint(extra):
 state=list(range(200));blocks=[(0,20),(20,20)]+[(40+4*i,4)for i in range(10)]+extra
 for o,w in blocks:
  for j in range(o,o+w):state[j],state[199-j]=state[199-j],state[j]
 assert state==list(range(199,-1,-1))
endpoint([(80,20)]);reject('unpaid20coordinate_padding',lambda:endpoint([]));reject('duplicated_rank20_completion',lambda:endpoint([(80,20),(80,20)]));reject('wrong_rank20_support',lambda:endpoint([(79,20)]))
for name in ['check_composition.py','check_changed_banks.py','price_candidate.py']:
 p=subprocess.run([sys.executable,'-O',str(packet.HERE/'experiment'/name)],capture_output=True,text=True)
 assert p.returncode!=0 and'Assertions must be enabled'in p.stderr;controls.append('assertion_disabled_'+name)
out={'status':'PASS_17_HARD_NEGATIVE_CONTROLS','count':len(controls),'controls':controls,'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Corrupted source identity, live frame boundaries, kernel cut/rank/chronology, scalar omission, paid endpoint and assertion-disable controls. No upstream executable was run.'};assert len(controls)==17
(P/'CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
