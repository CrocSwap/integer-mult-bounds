from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_source()
"""Independent finite hypotheses for the exact common-array-frame theorem."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from functools import lru_cache
from math import lcm,gcd
import gzip,json,hashlib
if not __debug__:raise RuntimeError('Assertions must be enabled')
HERE=contract.AUDIT;P=contract.FRAME;S=contract.SOURCE
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=read(P/'RESULT.json');v=read(P/'VALIDATION.json')
assert r['checker_sha256']==sha(contract.HERE/'frame/build_local.py')and v['checker_sha256']==sha(contract.HERE/'frame/validate_local.py')and v['builder_receipt_sha256']==sha(P/'RESULT.json')
for name,h in r['artifacts'].items():assert sha(P/name)==h
old_events=read(S/'scalar-events.json.gz');events=read(P/'local-events.json.gz');records=read(P/'local-records.json.gz');frames={int(k):z for k,z in read(P/'local-frames.json.gz').items()};fmap={int(k):v for k,v in read(P/'source-frame-map.json').items()};ep=read(P/'local-endpoints.json');paths={int(k):v for k,v in read(P/'local-paths.json.gz').items()}
w=read(S/'inputs/bitword__selected__bit__word_p10.json.gz');g=read(S/'inputs/bitword__selected__bit__graph_p10.json');rawF=read(S/'inputs/bitword__selected__bit__frames_p10.json.gz')['frames']
initial={int(k):v for k,v in ep['initial'].items()};final={int(k):v for k,v in ep['final'].items()};n=ep['n'];assert n==10020
assert len(events)==len(old_events)==350680 and len(records)==398660 and len(frames)==12885
for i,(e,o)in enumerate(zip(events,old_events)):assert e==dict(o,frame=fmap[o['frame']],original_index=i)
def integer(row):
 z=list(map(Q,row));d=lcm(*(x.denominator for x in z));a=[int(d*x)for x in z];h=gcd(*a)
 return [x//h for x in a]if h else a
MOD=65521
def rank(rows):
 if not rows:return 0
 a=[[x%MOD for x in row]for row in rows];k=0
 for col in range(len(a[0])):
  pivot=next((i for i in range(k,len(a))if a[i][col]),None)
  if pivot is None:continue
  a[k],a[pivot]=a[pivot],a[k];inv=pow(a[k][col],-1,MOD);a[k]=[(x*inv)%MOD for x in a[k]]
  for i in range(k+1,len(a)):
   c=a[i][col]
   if c:a[i]=[(x-c*y)%MOD for x,y in zip(a[i],a[k])]
  k+=1
  if k==len(a):break
 return k
def dot(a,b):return sum(x*y for x,y in zip(a,b))
A={};B={};dim={}
for f,z in frames.items():
 a=[integer(row)for row in z['annihilator']];b=[integer(row)for row in z['basis']];d=z['rank']
 assert len(a)==20-d and len(b)==d and rank(a)==20-d and rank(b)==d
 assert all(dot(x,y)==0 for x in a for y in b)
 rows,mult=(b,9)if d<=10 else(a,11)
 gram=[[mult*dot(x,y)-sum(x)*sum(y)for y in rows]for x in rows]
 assert rank(gram)==len(rows),('Gram',f)
 key=z['key']
 if key[0]=='PR325':
  src=key[1];assert fmap[src]==f
  if src==-1:assert d==0
  else:
   original=rawF[str(src)];assert d==original['dim']
   if 'a'in original:assert all(dot(x,y)==0 for x in original['a']for y in b)
   if 'b'in original:assert all(dot(x,y)==0 for x in a for y in original['b'])
 else:
  assert key[0]=='target_cap'and d==19 and a==[[3*int(j in g['labels'][key[1]])-1 for j in range(20)]]
 A[f]=a;B[f]=b;dim[f]=d
print('All rational frame spaces and nondegeneracy certificates verified',flush=True)
aliases={b:a for a,b in w['pairs']};regs=sorted(set(range(9060))-set(aliases));ga={z['role']:z for z in w['gauges']}
assert len(regs)==8100
for s in range(960):
 assert initial[s]==fmap[w['source_frame'][s]]and final[s]==fmap[w['full_frame']]
 assert dim[initial[960+s]]==0 and frames[final[960+s]]['key']==['target_cap',s]
for j,role in enumerate(regs):
 assert initial[1920+j]==fmap[ga[role]['frame']]if role in ga else dim[initial[1920+j]]==0
 assert final[1920+j]==fmap[w['full_frame']]
@lru_cache(None)
def contained(a,b):
 assert dim[a]<=dim[b]and all(dot(x,y)==0 for x in A[b]for y in B[a]),(a,b)
 return True
state=dict(initial);cursor=0;paid=Counter();computed_paths={s:[f]for s,f in initial.items()};copy=None;read_count=0;copy_count=0;all_pairs=set();gate_count=0
def need(s,f):
 global cursor
 old=state[s]
 if old==f:return
 contained(old,f);gap=dim[f]-dim[old]
 assert records[cursor]==[0,s,old,f,gap,0];cursor+=1
 state[s]=f;computed_paths[s].append(f);all_pairs.add((old,f))
 if gap:paid[gap]+=1
for e in events:
 op,a,b,c,f=(e[k]for k in ('op','a','b','c','frame'))
 if op==1:
  need(a,f);need(b,f)
  assert state[a]==state[b]==f
  assert records[cursor]==[1,a,b,c,f,ep['categories'].index(e['semantic'][0])];cursor+=1;gate_count+=1
  if b==n:assert copy is not None and a<1920 and a>=960;read_count+=1
  if copy is not None:assert a!=copy[0], 'COPY original was modified during read interval'
 elif op==2:
  assert copy is None and b==n;need(a,f);assert dim[f]==18
  zero=fmap[-1];copy=(a,b,f);state[b]=zero;computed_paths[b]=[zero];read_count=0
  assert records[cursor]==[2,a,b,f,zero,18];cursor+=1;paid[18]+=1
 else:
  assert op==3 and copy==(a,b,f)and state[a]==f and state[b]==fmap[-1]and read_count==144
  assert records[cursor]==[3,a,b,f,fmap[-1],18];cursor+=1;del state[b];del computed_paths[b];copy=None;copy_count+=1
for s,f in sorted(final.items()):need(s,f)
assert cursor==len(records)and state==final and computed_paths==paths and copy is None
assert(gate_count,copy_count,len(all_pairs))==(350640,20,40125)
assert paid==Counter({int(k):v for k,v in r['one_stage_paid_histogram'].items()})
assert(sum(paid.values()),sum(k*v for k,v in paid.items()))==(46844,179640)
for s,chain in paths.items():
 assert chain[0]==initial[s]and chain[-1]==final[s]
 if 960<=s<1920:
  for f in chain:contained(f,final[s])
# Recheck actual integer source incidences, including all regular helpers.
cols=[{q:1}if q<960 else{}for q in range(n+1)];checked=set();copy_checks=0
def support(f,port):
 for source in cols[port]:
  if(f,source)not in checked:
   assert all(sum(row[j]for j in g['labels'][source])==0 for row in A[f]);checked.add((f,source))
for e in events:
 op,a,b,c,f=(e[k]for k in ('op','a','b','c','frame'))
 if op==2:support(f,a);copy_checks+=len(cols[a]);cols[b]=dict(cols[a]);continue
 if op==3:assert cols[a]==cols[b];cols[b]={};continue
 for port in(a,b):
  if port!=n and not 960<=port<1920:support(f,port)
 if not 960<=a<1920:
  assert not 960<=b<1920
  for source,x in cols[b].items():
   y=cols[a].get(source,0)+c*x
   if y:cols[a][source]=y
   else:cols[a].pop(source,None)
  support(f,a)
assert len(checked)==563928 and copy_checks==2880
assert cols[:960]==[{q:1}for q in range(960)]and all(not row for row in cols[1920:])
manifest=read(S/'inputs/MANIFEST.json')['files'];proofs={}
for p in sorted((HERE/'inert').iterdir()):
 name=p.name.replace('__','/');assert sha(p)==manifest[name];proofs[name]=sha(p)
out={'status':'PASS_PR325_FULL_LOCAL_ARRAY_FRAME_CONTRACT',
 'source_result_sha256':sha(S/'RESULT.json'),'full_frame_result_sha256':sha(P/'RESULT.json'),
 'full_frame_validation_sha256':sha(P/'VALIDATION.json'),
 'checker_sha256':sha(__file__),'proof_sha256':sha(HERE/'FRAME-CONTRACT.md'),'pinned_theorems':proofs,
 'frames_rational_rank_and_Gram_checked':len(frames),'rank_witness_prime':MOD,
 'all_records_reconstructed':len(records),'common_frame_pointwise_ADDs':gate_count,
 'distinct_MOVE_pairs':len(all_pairs),'all10020_endpoint_chains_bound':True,
 'copies':copy_count,'reads_per_copy':144,'integer_source_checks':len(checked),'copied_input_checks':copy_checks,
 'local_paid_calls':sum(paid.values()),'local_rank_mass':sum(k*v for k,v in paid.items()),
 'arbitrary_dirty_operator_retained_by_common_array_frame_identity':True,
 'address_geometry_distinguished_from_F2_payload_values':True,
 'scope':'All finite hypotheses of the pinned common-array-frame and complete COPY identities are instantiated on the new PR325 local word. Generic address primitive implementation, uniform prime eligibility, global lowering, bank packing, price and all-size interfaces remain separate.'}
(HERE/'FULL-FRAME-AUDIT.json').write_text(json.dumps(contract.portable(out),indent=2)+'\n');print(json.dumps(contract.portable(out),indent=2))
