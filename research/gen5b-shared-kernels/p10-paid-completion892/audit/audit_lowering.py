from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions()
"""Independent incremental-emitter artifact audit. Executes no worker source."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import json,gzip,hashlib,struct
import numpy as np
if not __debug__:raise RuntimeError('Assertions must be enabled')
BASE=support.LOWER;HERE=support.AUDIT
PAID=support.BANK/"split_49_11"
AD=support.HERE/"admission";hashes={}
CORR=support.FRAME/"SOURCE-GEOMETRY-CORRECTION.json"
support.verify_correction()
correction=json.loads(CORR.read_bytes())
assert correction['source_columns']==960 and correction['retimed_setups']==480 and correction['all_actual_descent_frames_rank18']
assert sorted(z['source'] for z in correction['receipts'])==list(range(960))
assert correction['source_paid_histogram']=={'2':960,'17':960} and correction['source_rank_mass']==18240
def read(name):
 raw=(BASE/name).read_bytes();hashes[name]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
def packed(name,cols):
 raw=gzip.decompress((BASE/name).read_bytes());hashes[name]=hashlib.sha256(raw).hexdigest();return np.frombuffer(raw,dtype='<i4').reshape(-1,cols)
def sha(raw):return hashlib.sha256(raw).hexdigest()
ph=read('extended-phases.json');binding=read('local-scalar-binding.json');roles=read('compact-role-index.json')['roles'];norm=read('normalizers.json');receipts=read('namespace-receipts.json')
local=packed('local-scalar-operands.i32.gz',5);maps=packed('all-namespaces.i32.gz',2).reshape(300,10142,2)
assert sha(local.tobytes())==binding['records']['sha256'];assert len(local)==336293
assert len(roles)==8221 and roles==sorted(set(roles))
W=json.loads((support.WORD).read_bytes());rep=sorted(set(range(9120))-{b for a,b in W['pairs']});old={r:1920+i for i,r in enumerate(rep)}
to_old=list(range(1920))+[old[r]for r in roles]+[10148]
scalar=json.loads((support.ADM/'scalar-recurrence-result.json').read_bytes())
scalar_checks=[]
for reverse in (False,True):
 state=[1<<i for i in range(10142)];bounds=[1]*10142;center=None;count=0;hist=Counter();digest=hashlib.sha256();maxreads=0;reads=0
 for op,a,b,c,ordinal in (local[::-1]if reverse else local):
  op,a,b,c,ordinal=map(int,(op,a,b,c,ordinal))
  if op==1:
   assert a<10141 and a!=b and c%2
   state[a]^=state[b];bounds[a]+=abs(c)*bounds[b];count+=1;hist[abs(c)]+=1
   source=center if b==10141 else b
   assert source is not None
   digest.update((json.dumps([to_old[a],to_old[source],-c if reverse else c],separators=(',',':'))+'\n').encode())
   if b==10141:reads+=1
  elif op==(3 if reverse else 2):
   assert center is None and b==10141;center=a;state[b]=state[a];bounds[b]=bounds[a];reads=0
  else:
   assert op==(2 if reverse else 3) and center==a and state[b]==state[a] and reads==144
   center=None;maxreads=max(maxreads,reads)
 assert center is None
 assert all(state[i]==((1<<i)^((1<<(i-960))if 960<=i<1920 else 0))for i in range(10141))
 reference=scalar['inverse'if reverse else 'forward']
 assert count==reference['weighted_additions']==336253 and sum(k*v for k,v in hist.items())==338173
 assert max(bounds)==reference['max_row_l1'] and digest.hexdigest()==reference['event_sha256']
 scalar_checks.append({'inverse':reverse,'columns':10141,'max_l1':max(bounds),'event_sha256':digest.hexdigest(),'all_columns':True,'copy_reads':maxreads})
# Rebuild all physical namespaces from the real assignment ledger.
regular=list(struct.iter_unpack('>6I',gzip.decompress((PAID/'literal-assignments.bin.gz').read_bytes())))
slots={(role,t):(bank,off,width,scale)for role,t,bank,off,width,scale in regular}
normalizers={z['id']:z for z in norm['regular_normalizers']}
active=[(0,1),(1,0),(0,1),(3,2),(2,3)]
for s in range(5):
 for t in range(60):
  mp=maps[60*s+t];assert sha(mp.tobytes())==receipts[60*s+t]['namespace_sha256']
  assert len(set(map(tuple,mp.tolist())))==10142 and tuple(mp[-1])==(658275,-1)
  for i in range(1920):
   bank=active[s][i//960];port=i%960
   assert tuple(mp[i])==((4*t+bank)*960+port,0 if s==0 else 1+s*960+port)
  for i,role in enumerate(roles):
   bank,off,width,scale=slots[role,t];family,route=map(int,mp[1920+i]);z=normalizers[route-4801]
   assert family==230400+s*85575+bank
   assert(z['stage'],z['support'],z['rank'],z['scalar'])==(s,[off,off+width],width,scale)
   p=z['permutation'];assert sorted(p)==list(range(100)) and p[s*20:s*20+width]==list(range(off,off+width))
   assert z['paid_factor_bound']==599
# Exact phase order and explicit completion operation meaning.
expected=[]
for s in range(5):
 expected += [('helper',s,t)for t in range(60)]
 expected += [('paid_bank_completion',s,r)for r in (49,11)]
 if s in (1,2,4):expected +=[(kind,s,t)for t in range(60)for kind in ('idle','bridge')]
expected +=[('terminal_exchange',None,t)for t in range(60)]
assert len(ph)==len(expected)==730
for index,(z,(kind,stage,value))in enumerate(zip(ph,expected)):
 assert z['kind']==kind and z.get('stage')==stage and z['phase_index']==index
 assert z['rank'if kind=='paid_bank_completion'else'replica']==value
 if kind=='paid_bank_completion':
  off=40 if value==49 else 89;d=z['descriptor'];pi=d['permutation'];pinv=d['inverse_permutation'];ops=z['operations']
  assert z['family']==230400+(stage+1)*85575-1 and z['coordinate_interval']==[off,off+value]
  assert sorted(pi)==list(range(100)) and [pi[pinv[i]]for i in range(100)]==list(range(100))
  assert {pi[i]for i in range(off,off+value)}==set(range(value))
  assert [o['op']for o in ops]==['ROUTE_RIGHT','COMPILE_SPLIT_IDEMPOTENT','ROUTE_RIGHT','RESTORE_ROW_RESERVE']
  assert ops[0]['matrix']==pinv and ops[2]['matrix']==pi
  assert ops[1]['coordinate_support']==list(range(value)) and ops[1]['rank']==value
  assert all(o['family']==z['family']for o in ops)
  # At original cover g, route to h=g*pi^-1, compile h Q_prefix h^-1,
  # then return.  pi^-1 Q_prefix pi equals Q_support as integer matrices.
  assert {pinv[k]for k in range(value)}==set(range(off,off+value))
  for key,want in [('chronological_coordinate_transpositions',pi),('chronological_inverse_transpositions',pinv)]:
   images=list(range(100))
   for a,b in d[key]:images=[b if x==a else a if x==b else x for x in images]
   assert images==want
# Independently expand/hash every actual scalar operand record.
checks=[]
for z in ph:
 if z['kind']!='helper':continue
 s,t,idx=z['stage'],z['replica'],z['phase_index'];ev=local[::-1]if s in(1,3)else local;mp=maps[60*s+t]
 out=np.empty((len(ev),9),dtype='<i4');out[:,0]=idx;out[:,1]=np.arange(len(ev));out[:,2]=ev[:,0]
 if s in(1,3):out[:,2]=np.where(ev[:,0]==2,3,np.where(ev[:,0]==3,2,ev[:,0]))
 out[:,3:5]=mp[ev[:,1]];out[:,5:7]=mp[ev[:,2]];out[:,7]=ev[:,3];out[:,8]=ev[:,4]
 if s in(1,3):out[:,7]=np.where(ev[:,0]==1,-out[:,7],out[:,7])
 assert np.all(np.any(out[:,3:5]!=out[:,5:7],axis=1))
 checks.append({'phase_index':idx,'expanded_operand_sha256':sha(out.tobytes())})
(HERE/'EXPECTED-OPERAND-HASHES.json').write_text(json.dumps(checks,indent=2)+'\n')
if (BASE/'expanded-operand-receipts.json').exists():
 other=read('expanded-operand-receipts.json');assert checks==[{k:z[k]for k in ['phase_index','expanded_operand_sha256']}for z in other]
 matched=True
else:matched=False
result={'status':'PASS_INDEPENDENT_SCALAR_NAMESPACE_COMPLETION_CONTRACT_AUDIT','source_input_sha256':hashes,'source_word_sha256':sha((support.WORD).read_bytes()),'all_scalar_columns':scalar_checks,'all_namespaces_checked':300,'new_completion_sweeps':10,'all_phases_checked':730,'all_expanded_scalar_records':300*len(local),'emitter_operand_receipts_matched':matched,'permutation_direction_correct':True,'compositional_conclusion':'Concrete added completion emission closes the new endpoint, routing, index and fee obligation under the explicitly inherited regular arbitrary-dirty endpoint, final frame/reorder, and generic compiler interfaces.','source_chronology_correction_sha256':hashlib.sha256(CORR.read_bytes()).hexdigest(),'corrected_source_scope':'The original supplementary source-chain receipt covers original/pre-descent source frames. The separately bound correction supplies all480 actual rank18 descended setups and960 final source chains; code reviewed as inert source and receipt bindings verified here.','checker_sha256':sha(Path(__file__).read_bytes())}
(HERE/'LOWERING-AUDIT-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k!='source_input_sha256'},indent=2))
