from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_frame_binding()
"""Independent full-frame binding and positive copied-projector audit."""
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
from collections import Counter
import gzip,json,hashlib
import numpy as np
if not __debug__:raise RuntimeError('Assertions must be enabled')
HERE=contract.AUDIT;L=contract.FRAME;G=contract.GLOBAL;I=contract.GLOBAL
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.name.endswith('.gz')else b)
def fs(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sha(b):return hashlib.sha256(b).hexdigest()
result=read(G/'RESULT.json');manifest=read(G/'MANIFEST.json');frames=read(L/'local-frames.json.gz');records=read(L/'local-records.json.gz');overrides=read(G/'copied-work-projector-overrides.json');description=read(G/'projector-descriptors.json');bindings=read(G/'all-frame-bindings.json');phases=read(G/'extended-phases.json');localreceipt=read(L/'RESULT.json')
for n,h in manifest.items():assert fs(G/n)==h
assert result['source_identity']['local_result_sha256']==fs(L/'RESULT.json')and result['compiler_sha256']==fs(contract.HERE/'lowering/lower_pr325.py')
assert description['copied_work_sha256']==fs(G/'copied-work-projector-overrides.json')
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
# Independently instantiate new physical role/replica/address/chart bindings.
SRC=contract.SOURCE;BANK=contract.BANK
w=read(SRC/'inputs/bitword__selected__bit__word_p10.json.gz');graph=read(SRC/'inputs/bitword__selected__bit__graph_p10.json');ep=read(L/'local-endpoints.json');fmap=read(L/'source-frame-map.json')
assert description['array_lifting_contract_sha256']=='ed76761194988a01af77ead0ea6469cb5dcd29690ab985a0b5a4006b0f2b69bb'
assert 'Pointwise XOR on complete role arrays over F2' in description['ADD_semantics']
assert result['source_identity']['source_graph_sha256']==fs(SRC/'inputs/bitword__selected__bit__graph_p10.json')
assert result['source_identity']['bank_result_sha256']==fs(BANK/'BANK-RESULT.json')
assert result['source_identity']['local_validation_sha256']==fs(L/'VALIDATION.json')
roles=sorted(set(range(9060))-{b for a,b in w['pairs']});assert len(roles)==8100
assign={}
import struct
for role,t,b,off,width,scale in struct.iter_unpack('>6I',gzip.decompress((BANK/'literal-bank-assignments.bin.gz').read_bytes())):assign[role,t]=(b,off,width,scale)
assert len(assign)==486000
norm=read(G/'normalizers.json.gz');normalizers=norm['normalizers'];programs=norm['chart_programs'];gauges={z['role']:z['frame']for z in w['gauges']if z['role']in roles}
assert len(programs)==120
for name,p in programs.items():
 f=fmap[name];frm=frames[str(f)];assert frm['rank']==16
 cols=[[Q(x)for x in row]for row in p['basis_columns']];B=transpose(cols);BI=[[Q(x)for x in row]for row in p['inverse']]
 assert mm(B,BI)==mm(BI,B)==ident(20)
 A=[[Q(x)for x in row]for row in frm['annihilator']];BB=[[Q(x)for x in row]for row in frm['basis']]
 assert all(sum(x*y for x,y in zip(a,b))==0 for a in A for b in cols[4:])
 assert all(9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)==0 for a in cols[:4]for b in BB)
 temp=[row[:]for row in B]
 for op,a,b,c in p['factors']:
  if op=='swap':temp[a],temp[b]=temp[b],temp[a]
  elif op=='scale':temp[a]=[Q(c)*x for x in temp[a]]
  else:assert op=='add';temp[a]=[x+Q(c)*y for x,y in zip(temp[a],temp[b])]
 assert temp==ident(20)and p['factor_count']==len(p['factors'])<=150
maps=np.frombuffer(gzip.decompress((G/'all-namespaces.i32.gz').read_bytes()),dtype='<i4').reshape(5,60,10021,2)
active=[(0,1),(1,0),(0,1),(3,2),(2,3)]
ns_hashes=read(G/'namespace-hashes.json')
for s in range(5):
 for t in range(60):
  ns=maps[s,t]
  for q in range(1920):assert tuple(ns[q])==((4*t+active[s][int(q>=960)])*960+q%960,0 if s==0 else 1+s*960+q%960)
  for j,role in enumerate(roles):
   b,off,width,scale=assign[role,t];fam,nid=map(int,ns[1920+j]);assert fam==230400+s*85680+b
   z=normalizers[nid-4801];pid=gauges.get(role,-1);assert(z['stage'],z['support'],z['rank'],z['scalar'],z['chart_program'],z['paid_factor_bound'])==(s,[off,off+width],width,scale,pid,349)
   src=list(range(s*20,s*20+width));dst=list(range(off,off+width));pi=dict(zip(src+[q for q in range(100)if q not in src],dst+[q for q in range(100)if q not in dst]))
   assert z['permutation']==[pi[q]for q in range(100)]
   outside=z['outside_column'];assert not s*20<=outside<(s+1)*20 and z['unit_column_witness']==[pi[outside],scale]
  assert tuple(ns[-1])==(658800,-1)and len(set(map(tuple,ns.tolist())))==10021
  assert ns_hashes[s*60+t]['sha256']==sha(ns.tobytes())
# Full phase-major barriers; no completion is necessary or allowed here.
expected_phases=[]
for s in range(5):
 expected_phases.extend(('helper',s,t)for t in range(60))
 if s in(1,2,4):expected_phases.extend((kind,s,t)for t in range(60)for kind in('idle','bridge'))
expected_phases.extend(('terminal_exchange',None,t)for t in range(60))
assert len(phases)==len(expected_phases)==720
for i,(p,x)in enumerate(zip(phases,expected_phases)):
 assert(p['kind'],p.get('stage'),p['replica'])==x and p['phase_index']==i
 if p['kind']=='helper':assert p['reverse_complement']==(p['stage']in(1,3))
# Fresh source triples and exact rational rho identities, then the universal
# port conjugacy transports the canonical eight boundary identities.
routes=read(G/'fresh-data-routes.json');assert routes['source_graph_sha256']==fs(SRC/'inputs/bitword__selected__bit__graph_p10.json')
J=np.eye(20,dtype=np.int64);qs=np.asarray([int(i<3)for i in range(20)],dtype=np.int64);PP=np.outer(qs,3*qs-1);KK=6*J-PP
assert np.array_equal(PP@PP,6*PP)and np.array_equal(KK@KK,6*KK)and not np.any(PP@KK)
canonical=np.block([[PP,KK],[KK,PP]])
for q,z in enumerate(routes['ports']):
 assert z['port']==q and z['label']==graph['labels'][q]and z['source_frame']==ep['initial'][str(q)]
 pi=np.zeros((20,20),dtype=np.int64)
 for col,row in enumerate(z['pi_columns']):pi[row,col]=1
 chi=np.asarray([int(i in graph['labels'][q])for i in range(20)],dtype=np.int64)
 assert np.array_equal(pi@qs,chi)and np.array_equal(pi@pi.T,J)
 PC=np.outer(chi,3*chi-1);R=np.block([[PC,pi@KK],[KK@pi.T,PP]]);T=np.block([[pi,0*J],[0*J,J]])
 assert np.array_equal(R,T@canonical@T.T)and np.array_equal(R@R,36*np.eye(40,dtype=np.int64))
def rho(s):
 R=6*np.eye(100,dtype=np.int64)
 if s:
  sl=slice(20*s,20*(s+1));R[:20,:20]=PP;R[sl,sl]=PP;R[:20,sl]=KK;R[sl,:20]=KK
 return R
def field(s,kind):
 R=np.zeros((100,100),dtype=np.int64);R[:20,:20]={'P':PP,'K':KK,'H':6*J,'0':0*J}[kind]
 for j in range(1,s+1):R[20*j:20*(j+1),20*j:20*(j+1)]=KK
 R=rho(s)@R@rho(s);assert not np.any(R%36);return R//36
zero=np.zeros((100,100),dtype=np.int64);eye=6*np.eye(100,dtype=np.int64);p=field(0,'P')
pairs=[(p,field(1,'H')),(zero,field(1,'K')),(field(2,'P'),field(3,'P')),(field(2,'0'),field(3,'0')),(field(2,'H'),eye),(field(2,'K'),eye-p),(field(4,'H'),eye),(field(4,'K'),eye-p)]
ranklist=[]
for a,b in pairs:
 d=b-a;assert np.array_equal(a@b,6*a)and np.array_equal(b@a,6*a)and np.array_equal(d@d,6*d);ranklist.append(int(np.trace(d)//6))
assert ranklist==[38,38,19,19,42,42,4,4]
bp=read(G/'boundary-projectors.json');assert bp['ranks']==ranklist and bp['fresh_data_routes_sha256']==fs(G/'fresh-data-routes.json')
assert description['fresh_data_routes_sha256']==fs(G/'fresh-data-routes.json')and description['boundary_projectors_sha256']==fs(G/'boundary-projectors.json')
print('All fresh charts,300 actual namespaces,960 route conjugacies and720 phases pass',flush=True)
# Independently rebuild all five templates, check every copied lifetime and
# every MOVE orientation, then lower every literal namespace and hash it.
spaces=np.frombuffer(gzip.decompress((I/'all-namespaces.i32.gz').read_bytes()),dtype='<i4').reshape(5,60,10021,2)
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
 assert np.array_equal(expected,actual)and len(actual)==398680
 center=None;reads=0;localcopy=0;H=Counter()
 for ordinal,row in enumerate(actual):
  op,a,b,c,f,z,stage,rv,idx=map(int,row);assert(stage,rv)==(s,int(rev))
  if op==2:
   assert center is None and a==10020 and b<10020;center=(b,f);reads=0;localcopy+=1
  elif op==0:
   signed=(frames[str(c)]['rank']-frames[str(b)]['rank'])*(-1 if rev else 1)
   if a==10020:
    o=overrides_by[s,ordinal];assert o['family']==658800
    assert(o['old_frame'],o['new_frame'],o['rank'],o['local_source_record'])==(b,c,18,idx)
    assert center is not None and center[1]==b and c==0 and f==18
    assert o['difference_orientation']*signed==18 and o['difference_orientation']==(1 if rev else -1)
    assert f==frames[str(b)]['rank']and frames[str(c)]['rank']==0
   else:assert signed==f>=0
   if f:H[f]+=1
  elif op==1:
   assert a!=10020
   if b==10020:assert center is not None and f==0;reads+=1
  else:
   assert op==3 and a==10020 and center is not None and reads==144;center=None
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
# Independently derive every signed boundary record at the new phase IDs.
cursor=0
for p in phases:
 kind=p['kind']
 if kind in('helper','paid_bank_completion'):continue
 idx=p['phase_index'];t=p['replica'];rows=[]
 def family(b,port):return (4*t+b)*960+port
 if kind=='idle':
  patterns={0:[(2,38,0),(3,38,1)],1:[(2,19,2),(3,19,3)],2:[(0,42,4),(1,42,5),(2,4,6),(3,4,7)]}[p['which']]
  for bank,rank,pid in patterns:
   for port in range(960):rows.append([idx,4,family(bank,port),-1,0,rank,pid,port])
 elif kind=='bridge':
  patterns={0:[(0,2,1),(3,1,-1)],1:[(3,1,1),(0,2,-1)],2:[(1,3,-1),(2,0,1)]}[p['which']]
  for dst,src,sign in patterns:
   for port in range(960):rows.append([idx,5,family(dst,port),family(src,port),sign,0,p['which'],port])
 else:
  assert kind=='terminal_exchange'
  for dst,src in [(0,1),(2,3)]:
   for port in range(960):rows.append([idx,7,family(dst,port),family(src,port),-1,0,0,port])
 assert np.array_equal(boundary[cursor:cursor+len(rows)],np.asarray(rows,dtype='<i4'));cursor+=len(rows)
assert cursor==len(boundary)==921600
assert all(p['kind']!='paid_bank_completion'for p in phases)
for r in boundary[boundary[:,1]==4,5]:globalhist[int(r)]+=1
for z in phases:
 if z['kind']=='paid_bank_completion':globalhist[z['rank']]+=1
for name in ('extended-phases.json','copied-work-projector-overrides.json','projector-descriptors.json','fresh-data-routes.json','boundary-projectors.json'):whole.update((G/name).read_bytes())
whole.update(boundary.tobytes())
assert total==119604000 and whole.hexdigest()==result['full_program_sha256']
assert globalhist==Counter({int(k):v for k,v in result['literal_histogram'].items()})
assert(sum(globalhist.values()),sum(k*v for k,v in globalhist.items()),max(globalhist))==(14514000,65757600,42)
for n,h in manifest.items():assert fs(G/n)==h
out={'status':'PASS_INDEPENDENT_PR325_GLOBAL_FRAME_BINDING','global_result_sha256':fs(G/'RESULT.json'),'global_manifest_sha256':fs(G/'MANIFEST.json'),'local_result_sha256':fs(L/'RESULT.json'),'copy_override_sha256':fs(G/'copied-work-projector-overrides.json'),'all_local_records':398660,'all_global_stage_records':total,'all_namespaces':300,'phases':720,'completion_children':0,'fresh_chart_programs':120,'fresh_rho_conjugacies':960,'boundary_ranks':ranklist,'actual_positive_center_projector_checks':matrix_checks,'copy_overrides_checked':100,'copy_lifetimes_per_stage':20,'copy_reads_per_lifetime':144,'all_copy_negative_directions_rejected':True,'global_paid_calls':14514000,'global_rank_mass':65757600,'max_rank':42,'program_binding':whole.hexdigest(),'scope':'Actual final local/full global IR bindings and corrected positive copied-work projectors. No production primitive execution, uniform prime admission, or unconditional all-size claim.','checker_sha256':fs(__file__)}
(HERE/'GLOBAL-AUDIT.json').write_text(json.dumps(contract.portable(out),indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='actual_positive_center_projector_checks'},indent=2))
