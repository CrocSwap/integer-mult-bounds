from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions()
"""Independent full-frame binding and positive copied-projector audit."""
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
from collections import Counter
import gzip,json,hashlib
import numpy as np
if not __debug__:raise RuntimeError('Assertions must be enabled')
HERE=support.AUDIT;L=support.FRAME;G=support.OUTPUT/"full-frame";I=support.LOWER
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.name.endswith('.gz')else b)
def fs(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sha(b):return hashlib.sha256(b).hexdigest()
result=read(G/'RESULT.json');manifest=read(G/'MANIFEST.json');frames=read(L/'local-frames.json.gz');records=read(L/'local-records.json.gz');overrides=read(G/'copied-work-projector-overrides.json');description=read(G/'projector-descriptors.json');bindings=read(G/'all-final-frame-bindings.json');phases=read(G/'extended-final-frame-phases.json');localreceipt=read(L/'RESULT.json')
for n,h in manifest.items():assert fs(G/n)==h
assert result['local_result_sha256']==fs(L/'RESULT.json')and result['compiler_sha256']==fs(support.HERE/'lowering/bind_full_frames.py')
assert description['copied_work_override_sha256']==fs(G/'copied-work-projector-overrides.json')
assert len(overrides)==100 and Counter(z['difference_orientation']for z in overrides)=={-1:60,1:40}
# Exact rational projector from the two-row annihilator of each real center.
def mm(A,B):
 bt=list(zip(*B));return [[sum(x*y for x,y in zip(row,col))for col in bt]for row in A]
def ident(n):return [[Q(i==j)for j in range(n)]for i in range(n)]
def add(A,B,sign=1):return [[x+sign*y for x,y in zip(a,b)]for a,b in zip(A,B)]
def transpose(A):return list(map(list,zip(*A)))
@lru_cache(None)
def projector(fid):
 A=[[Q(x)for x in row]for row in frames[str(fid)]['annihilator']];assert len(A)==2 and frames[str(fid)]['rank']==18
 invG=[[Q(i==j,9)-Q(1,99)for j in range(20)]for i in range(20)]
 U=mm(invG,transpose(A));B=mm(A,U);det=B[0][0]*B[1][1]-B[0][1]*B[1][0];assert det
 Bi=[[B[1][1]/det,-B[0][1]/det],[-B[1][0]/det,B[0][0]/det]]
 P=add(ident(20),mm(mm(U,Bi),A),-1)
 assert mm(P,P)==P and sum(P[i][i]for i in range(20))==18
 assert all(not x for row in mm(A,P)for x in row)
 return P
def D(P):
 eye=ident(20);TL=add(eye,P,-1);TR=[list(reversed(row))for row in P];BL=list(reversed(P));BR=[list(reversed(row))for row in reversed(TL)]
 return [a+b for a,b in zip(TL,TR)]+[a+b for a,b in zip(BL,BR)]
I20=ident(20);I40=ident(40);F40=D(I20);matrix_checks=[]
for f in sorted({z['old_frame']for z in overrides}):
 P=projector(f);DP=D(P);negative=[[-x for x in row]for row in P];DN=D(negative)
 assert mm(DP,DP)==I40
 assert mm(DP,D(add(I20,P,-1)))==F40
 assert mm(negative,negative)!=negative and mm(DN,DN)!=I40
 # Thus forward D_P D_P = I and reflected D_P D_(I-P) = D_I.
 # Unchanged Kstar stage blocks and all common QA/d conjugations cancel.
 matrix_checks.append({'source_frame':f,'rank':18,'rational_idempotent':True,'all40_active_columns':True,'forward_copy_endpoint_conjugacy':True,'reflected_copy_endpoint_conjugacy':True,'negative_projector_rejected':True,'negative_D_not_involution':True})
print('Actual center projectors: positive idempotence/copy conjugacy pass; negative direction rejected',flush=True)
# Independently rebuild all five templates, check every copied lifetime and
# every MOVE orientation, then lower every literal namespace and hash it.
spaces=np.frombuffer(gzip.decompress((I/'all-namespaces.i32.gz').read_bytes()),dtype='<i4').reshape(5,60,10142,2)
phaseid={(z['stage'],z['replica']):z['phase_index']for z in phases if z['kind']=='helper'}
overrides_by={(z['stage'],z['template_record']):z for z in overrides};expecthist=Counter({int(k):v for k,v in localreceipt['one_stage_paid_histogram'].items()});globalhist=Counter();whole=hashlib.sha256();total=0;opcounts=Counter()
for s in range(5):
 rev=s in(1,3);expected=[]
 for idx in(range(len(records)-1,-1,-1)if rev else range(len(records))):
  op,a,b,c,f,z=records[idx]
  if op==0:expected.append([0,a,c if rev else b,b if rev else c,f,0,s,int(rev),idx])
  elif op==1:expected.append([1,a,b,-c if rev else c,f,z,s,int(rev),idx])
  elif op==(3 if rev else 2):
   expected +=[[2,b,a,0,c,0,s,int(rev),idx],[0,b,c,f,frames[str(c)]['rank'],0,s,int(rev),idx]]
  else:
   assert op==(2 if rev else 3);expected.append([3,b,-1,0,f,0,s,int(rev),idx])
 expected=np.asarray(expected,dtype='<i4');actual=np.frombuffer(gzip.decompress((G/f'stage-{s}-template.i32.gz').read_bytes()),dtype='<i4').reshape(-1,9)
 assert np.array_equal(expected,actual)and len(actual)==389243
 center=None;reads=0;localcopy=0;H=Counter()
 for ordinal,row in enumerate(actual):
  op,a,b,c,f,z,stage,rv,idx=map(int,row);assert(stage,rv)==(s,int(rev))
  if op==2:
   assert center is None and a==10141 and b<10141;center=(b,f);reads=0;localcopy+=1
  elif op==0:
   signed=(frames[str(c)]['rank']-frames[str(b)]['rank'])*(-1 if rev else 1)
   if a==10141:
    o=overrides_by[s,ordinal];assert o['family']==658275 and o['route']=='external_work0'
    assert(o['old_frame'],o['new_frame'],o['rank'],o['local_source_record'])==(b,c,18,idx)
    assert center is not None and center[1]==b and c==0 and f==18
    assert o['difference_orientation']*signed==18 and o['difference_orientation']==(1 if rev else -1)
    assert f==frames[str(b)]['rank']and frames[str(c)]['rank']==0
   else:assert signed==f>=0
   if f:H[f]+=1
  elif op==1:
   assert a!=10141
   if b==10141:assert center is not None and f==0;reads+=1
  else:
   assert op==3 and a==10141 and center is not None and reads==144;center=None
 assert center is None and localcopy==20 and H==expecthist
 mask=(actual[:,0]==1)|(actual[:,0]==2)
 for t in range(60):
  mp=spaces[s,t];out=np.empty((len(actual),12),dtype='<i4');out[:,0]=phaseid[s,t];out[:,1]=actual[:,0]
  out[:,2:4]=mp[actual[:,1]];out[:,4]=actual[:,2];out[:,5]=-2;out[mask,4:6]=mp[actual[mask,2]];out[:,6:]=actual[:,3:]
  h=sha(out.tobytes());receipt=bindings[s*60+t]
  assert(receipt['stage'],receipt['replica'],receipt['phase_index'],receipt['records'],receipt['sha256'])==(s,t,phaseid[s,t],len(actual),h)
  whole.update(bytes.fromhex(h));globalhist.update(H);total+=len(actual)
 print('Independent full frame stage',s,'all60namespace hashes match',flush=True)
boundary=np.frombuffer(gzip.decompress((I/'boundary-records.i32.gz').read_bytes()),dtype='<i4').reshape(-1,8)
for r in boundary[boundary[:,1]==4,5]:globalhist[int(r)]+=1
for z in phases:
 if z['kind']=='paid_bank_completion':globalhist[z['rank']]+=1
whole.update(json.dumps(phases,sort_keys=True,separators=(',',':')).encode());whole.update(boundary.tobytes())
whole.update((G/'projector-descriptors.json').read_bytes());whole.update((G/'copied-work-projector-overrides.json').read_bytes())
assert total==116772900 and whole.hexdigest()==result['full_program_binding_sha256']
assert globalhist==Counter({int(k):v for k,v in result['literal_global_paid_histogram'].items()})
assert(sum(globalhist.values()),sum(k*v for k,v in globalhist.items()),max(globalhist))==(15002710,65705100,49)
for n,h in manifest.items():assert fs(G/n)==h
out={'status':'PASS_INDEPENDENT_CORRECTED_FULL_FRAME_BINDING','global_result_sha256':fs(G/'RESULT.json'),'global_manifest_sha256':fs(G/'MANIFEST.json'),'local_result_sha256':fs(L/'RESULT.json'),'copy_override_sha256':fs(G/'copied-work-projector-overrides.json'),'all_local_records':389223,'all_global_stage_records':total,'all_namespaces':300,'actual_positive_center_projector_checks':matrix_checks,'copy_overrides_checked':100,'copy_lifetimes_per_stage':20,'copy_reads_per_lifetime':144,'all_copy_negative_directions_rejected':True,'global_paid_calls':15002710,'global_rank_mass':65705100,'max_rank':49,'program_binding':whole.hexdigest(),'scope':'Actual final local/full global IR bindings and corrected positive copied-work projectors. No production primitive execution, uniform prime admission, or unconditional all-size claim.','checker_sha256':fs(__file__)}
(HERE/'GLOBAL-AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='actual_positive_center_projector_checks'},indent=2))
