from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support as _portable
_portable.require_assertions()
"""Independent review of the incremental emitter's inert output files.
Does not import or execute the emitter or any upstream program.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from collections import Counter
import json,gzip,hashlib,struct
import numpy as np
if not __debug__:raise RuntimeError('Assertions required')
HERE=_portable.AUDIT;EMIT=_portable.LOWER;PAID=_portable.BANK/"split_49_11";AD=_portable.HERE/"admission"
def read(p):return json.loads(Path(p).read_text())
def sh(b):return hashlib.sha256(b).hexdigest()
def filehash(p):return sh(Path(p).read_bytes())
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def extract_object_array(path,key):
 # Parse one top-level pretty-printed object array without keeping the104MB
 # file or all verbose normalizer dictionaries in memory.
 with Path(path).open()as f:
  for line in f:
   if line==f'  "{key}": [\n':break
  else:raise AssertionError('Missing array')
  buf=[]
  for line in f:
   if not buf and line.startswith('  ]'):return
   buf.append(line)
   if line.startswith('    }'):
    s=''.join(buf).strip().rstrip(',');yield json.loads(s);buf=[]
  raise AssertionError('Truncated object array')
paid=read(PAID/'RESULT.json');assert paid['split']==[49,11]
word=read(_portable.WORD);assert filehash(_portable.WORD)==paid['word_sha256']
summary=read(_portable.ADM/'ADMISSION-RESULT.json');scalar=read(_portable.ADM/'scalar-recurrence-result.json')
record=read(EMIT/'local-scalar-binding.json');raw=gzip.decompress((EMIT/'local-scalar-operands.i32.gz').read_bytes());assert sh(raw)==record['records']['sha256']
local=np.frombuffer(raw,dtype='<i4').reshape(-1,5);assert local.shape==(336293,5)
assert np.array_equal(local[:,4],np.arange(len(local)))
roles=read(EMIT/'compact-role-index.json')['roles'];assert len(roles)==8221 and roles==sorted(set(roles))
allroles=sorted(set(range(9120))-{b for a,b in word['pairs']});original={r:1920+i for i,r in enumerate(allroles)};uncompact=list(range(1920))+[original[r]for r in roles]+[10148]
assert len(uncompact)==10142
# Fresh all-column scalar replays and both original event digests, reconstructed
# solely from the emitted compact template and its explicit role inverse map.
scalar_results=[]
for rev in [False,True]:
 state=[1<<i for i in range(10142)];norms=[1]*10142;center=None;count=Counter();d=hashlib.sha256();copy_count=0;reads=0
 seq=local[::-1]if rev else local
 for op,a,b,c,_ in seq.tolist():
  if op==1:
   assert a!=b and c%2==1;state[a]^=state[b];norms[a]+=abs(c)*norms[b];count[abs(c)]+=1
   src=center if b==10141 else b;assert src is not None
   if b==10141:reads+=1
   d.update((json.dumps([uncompact[a],uncompact[src],-c if rev else c],separators=(',',':'))+'\n').encode())
  elif op==(3 if rev else 2):assert center is None and b==10141;center=a;state[b]=state[a];norms[b]=norms[a];copy_count+=1;reads=0
  else:assert center==a and b==10141 and state[b]==state[a] and reads==144;center=None
 assert center is None and copy_count==20 and count=={1:335293,3:960}
 assert all(state[i]==((1<<i)^((1<<(i-960))if 960<=i<1920 else 0))for i in range(10141))
 expected=scalar['inverse'if rev else 'forward'];assert d.hexdigest()==expected['event_sha256'] and max(norms)==expected['max_row_l1']
 scalar_results.append({'reverse':rev,'all_columns':10141,'event_sha256':d.hexdigest(),'max_norm':max(norms),'copied_center_episodes':copy_count,'reads_per_episode':144})
print('Independent compact scalar+COPY replay passed',flush=True)
# The independently admitted bank assignment controls every actual namespace.
assign={}
for r,t,b,o,w,sc in struct.iter_unpack('>6I',gzip.decompress((PAID/'literal-assignments.bin.gz').read_bytes())):assign[r,t]=(b,o,w,sc)
assert len(assign)==8221*60
chartdata=json.loads(gzip.decompress((_portable.BASE_OUTPUT/"finite/endpoint-charts.json.gz").read_bytes()));chart={u['role']:u['program_id']for u in chartdata['role_uses']}
normalizer_ids={};count=0
for d in extract_object_array(EMIT/'normalizers.json','regular_normalizers'):
 s=d['stage'];o,e=d['support'];w=e-o;sc=d['scalar'];key=(s,o,w,sc,d['chart_program']);assert key not in normalizer_ids and d['id']==count
 orig=list(range(20*s,20*s+w));target=list(range(o,e));p=dict(zip(orig+[x for x in range(100)if x not in orig],target+[x for x in range(100)if x not in target]));pi=[p[x]for x in range(100)]
 assert d['permutation']==pi and d['rank']==w and 1<=sc<=25 and d['paid_factor_bound']==599
 outside=next(j for j in range(100)if not 20*s<=j<20*(s+1));assert d['unit_column_witness']==[pi[outside],sc]
 assert d['inverse_chart_window']==[20*s,20*(s+1)] and d['formula']=='N = scalar * Pi * embed_stage(B_inverse)'
 normalizer_ids[key]=4801+d['id'];count+=1
spaces=np.frombuffer(gzip.decompress((EMIT/'all-namespaces.i32.gz').read_bytes()),dtype='<i4').reshape(300,10142,2)
active=[(0,1),(1,0),(0,1),(3,2),(2,3)];receipts=read(EMIT/'namespace-receipts.json')
for s in range(5):
 for t in range(60):
  a=spaces[60*s+t];want=[]
  for i in range(1920):want.append(((4*t+active[s][int(i>=960)])*960+i%960,0 if s==0 else 1+s*960+i%960))
  for r in roles:
   b,o,w,sc=assign[r,t];want.append((230400+s*85575+b,normalizer_ids[s,o,w,sc,chart.get(r,-1)]))
  want.append((658275,-1));assert np.array_equal(a,np.array(want,dtype='<i4'))
  assert len(set(want))==10142
  assert sh(a.tobytes())==receipts[60*s+t]['namespace_sha256']
print('All300 namespaces independently reconstructed',flush=True)
phases=read(EMIT/'extended-phases.json');expected=read(PAID/'LOWERING-PLAN.json')['phases'];assert len(phases)==len(expected)==730
for i,(x,y)in enumerate(zip(phases,expected)):
 assert x['phase_index']==i and x['kind']==y['kind']
 for k in ['stage','replica','which','family','rank','coordinate_interval']:
  if k in y:assert x[k]==y[k]
 if x['kind']!='paid_bank_completion':continue
 d=x['descriptor'];r=x['rank'];support=list(range(*x['coordinate_interval']));assert d['coordinate_support']==support and d['Q_entries']==[[j,j,1]for j in support]
 U=np.zeros((200,r),dtype=np.int64);V=np.zeros((r,200),dtype=np.int64)
 for a,b,v in d['U_entries']:U[a,b]+=v
 for a,b,v in d['V_entries']:V[a,b]+=v
 D=np.eye(200,dtype=np.int64)
 for j in support:D[[j,199-j]]=D[[199-j,j]]
 assert np.array_equal(U@V,D-np.eye(200,dtype=np.int64)) and np.array_equal(V@U,-2*np.eye(r,dtype=np.int64))
 pi=d['permutation'];inv=d['inverse_permutation'];assert sorted(pi)==list(range(100)) and [pi[inv[j]]for j in range(100)]==list(range(100))
 assert {pi[j]for j in support}==set(range(r))
 # Pi^-1 Qfirst Pi=Qsupport, the exact route-out/generic/route-back equality.
 assert [int(pi[j]<r)for j in range(100)]==[int(j in support)for j in range(100)]
 for seq,want in [(d['chronological_coordinate_transpositions'],pi),(d['chronological_inverse_transpositions'],inv)]:
  images=list(range(100))
  for a,b in seq:images=[b if j==a else a if j==b else j for j in images]
  assert images==want
 assert [z['op']for z in x['operations']]==['ROUTE_RIGHT','COMPILE_SPLIT_IDEMPOTENT','ROUTE_RIGHT','RESTORE_ROW_RESERVE']
 assert x['operations'][0]['matrix']==inv and x['operations'][2]['matrix']==pi
 assert x['operations'][1]['coordinate_support']==list(range(r)) and x['operations'][1]['rank']==r
 assert all(z['family']==x['family']for z in x['operations'])
 assert d['fees']=={'route_movements':2,'selector_calls':1436348,'generic_wrappers':80008,'matrix_preparation':1024000000,'paid_child_overhead':1,'fallback_children_bound':320000,'fallback_child_ratio':'1/100','bad_class_fraction_bound':'1/10000000000000000'}
print('All10 routed integer completion descriptors independently checked',flush=True)
# Completion/boundary stream and all100,887,900 substituted scalar operands.
# No emitter source is called; regenerate the nine-column physical records.
result=read(EMIT/'RESULT.json');er={x['phase_index']:x for x in read(EMIT/'expanded-operand-receipts.json')};boundary=gzip.decompress((EMIT/'boundary-records.i32.gz').read_bytes());brows=list(struct.iter_unpack('<8i',boundary));pos=0;chain=hashlib.sha256();total=0
for x in phases:
 idx=x['phase_index'];chain.update(canon(x)+b'\n')
 if x['kind']=='helper':
  s=x['stage'];a=spaces[60*s+x['replica']];e=local.copy()if s not in [1,3]else local[::-1].copy()
  if s in [1,3]:
   op=e[:,0].copy();e[op==1,3]*=-1;e[op==2,0]=3;e[op==3,0]=2
  out=np.empty((len(e),9),dtype='<i4');out[:,0]=idx;out[:,1]=np.arange(len(e));out[:,2]=e[:,0];out[:,3:5]=a[e[:,1]];out[:,5:7]=a[e[:,2]];out[:,7]=e[:,3];out[:,8]=e[:,4]
  h=sh(out.tobytes());assert h==er[idx]['expanded_operand_sha256'];chain.update(bytes.fromhex(h));total+=len(e)
 elif x['kind']=='paid_bank_completion':chain.update(canon(x['operations'])+b'\n')
 else:
  t=x['replica'];kind=x['kind'];f=lambda b,j:(4*t+b)*960+j
  if kind=='idle':groups={0:[(2,38,0),(3,38,1)],1:[(2,19,2),(3,19,3)],2:[(0,42,4),(1,42,5),(2,4,6),(3,4,7)]}[x['which']];rs=[(idx,4,f(b,j),-1,0,r,k,j)for b,r,k in groups for j in range(960)]
  elif kind=='bridge':groups={0:[(0,2,1),(3,1,-1)],1:[(3,1,1),(0,2,-1)],2:[(1,3,-1),(2,0,1)]}[x['which']];rs=[(idx,5,f(a,j),f(b,j),c,0,x['which'],j)for a,b,c in groups for j in range(960)]
  else:assert kind=='terminal_exchange';rs=[(idx,7,f(a,j),f(b,j),-1,0,0,j)for a,b in [(0,1),(2,3)]for j in range(960)]
  assert brows[pos:pos+len(rs)]==rs
  for row in rs:chain.update(struct.pack('<8i',*row))
  pos+=len(rs)
assert pos==len(brows)==921600 and total==100887900
assert chain.hexdigest()==result['operand_binding']['extended_compositional_program_sha256']
assert result['invoice']['terms']==paid['finite_invoice']['terms'] and result['literal_profile']==paid['literal_profile']
assert result['whole_final_raw_frame_program_regenerated']is False and result['unconditional_all_size_theorem']is False
out={'status':'PASS_INDEPENDENT_COMPOSITIONAL_LOWERING_REVIEW','candidate_sha256':paid['word_sha256'],'scalar_replay':scalar_results,'normalizer_descriptors':count,'all_namespaces':300,'expanded_scalar_records':total,'boundary_records':pos,'completion_descriptors':10,'integer_UV_and_route_conjugation':True,'program_sha256':chain.hexdigest(),'emitter_result_sha256':filehash(EMIT/'RESULT.json'),'checker_sha256':filehash(Path(__file__)),'scope':'Closes new completion-phase/namespace/scalar-operand/boundary/fee integration at the stated compositional interface. The original final133reorders, regular raw frame program, generic compiler and all-size interfaces remain expressly inherited.','whole_final_raw_frame_program_regenerated':False}
(HERE/'LOWERING-REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
