from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
"""Fresh full PR325 frame word with only 480 source retimings.
Independently authored; no upstream programs or old role maps executed/imported.
"""
from pathlib import Path
from collections import Counter,defaultdict
from functools import lru_cache
from fractions import Fraction as Q
import json,gzip,hashlib,sys
P=contract.FRAME;SRC=contract.SOURCE
if not __debug__:raise RuntimeError('Assertions must be enabled')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 b=Path(p).read_bytes();return json.loads(gzip.decompress(b)if str(p).endswith('.gz')else b)
def dump(n,x):
 b=(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode();(P/n).write_bytes(gzip.compress(b,mtime=0)if n.endswith('.gz')else b)
contract.verify_source()
for z in read(SRC/'MANIFEST.json')['files']:assert sha(SRC/z['path'])==z['sha256']
assert read(SRC/'RESULT.json')['checker_sha256']==contract.sha(contract.HERE/'source/check_retimings.py')
sys.path.insert(0,str(contract.HERE/'source'));from check_retimings import null,rr

def run():
 load=lambda name:read(SRC/'inputs'/('bitword__selected__bit__'+name+'_p10.json'+('.gz'if name in('word','frames')else'')))
 w,g,rawF=(load(n)for n in('word','graph','frames'));rawF={int(k):z for k,z in rawF['frames'].items()};events=read(SRC/'scalar-events.json.gz');receipt=read(SRC/'RESULT.json');assert receipt['checker_sha256']==contract.sha(contract.HERE/'source/check_retimings.py')
 aliases={b:a for a,b in w['pairs']};R=1+max(max(row[:2])for row in w['ops']);regs=sorted(set(range(R))-set(aliases));idx={r:1920+i for i,r in enumerate(regs)};physical={r:idx[aliases.get(r,r)]for r in range(R)};n=1920+len(regs);assert(n,R,len(aliases))==(10020,9060,960)
 ga={e['role']:e for e in w['gauges']};assert len(ga)==2160
 used={e['frame']for e in events}|set(w['source_frame'])|{e['frame']for r,e in ga.items()if r in idx}|{w['full_frame']}
 F={};source_map={};A={};B={};dim={}
 def frame_install(key,b,a,d):
  f=len(F);assert len(b)==d and len(a)==20-d
  F[f]=dict(key=list(key),rank=d,basis=[[str(x)for x in row]for row in b],annihilator=[[str(x)for x in row]for row in a]);A[f]=a;B[f]=b;dim[f]=d;return f
 for old in sorted(used):
  if old==-1:b=[];a=[[int(i==j)for j in range(20)]for i in range(20)];d=0
  else:
   z=rawF[old];b=z.get('b');a=z.get('a');d=z['dim'];b=null(a)if b is None else b;a=null(b)if a is None else a
  source_map[old]=frame_install(('PR325',old),b,a,d)
 ZERO=source_map[-1];FULL=source_map[w['full_frame']];assert dim[ZERO]==0 and dim[FULL]==20
 target_caps={}
 for q in range(960):
  a=[[3*int(j in g['labels'][q])-1 for j in range(20)]];target_caps[q]=frame_install(('target_cap',q),null(a),a,19)
 @lru_cache(None)
 def sub(a,b):return dim[a]<=dim[b]and all(sum(x*y for x,y in zip(u,v))==0 for u in A[b]for v in B[a])
 initial={q:source_map[w['source_frame'][q]]for q in range(960)};initial.update({960+q:ZERO for q in range(960)});initial.update({idx[r]:source_map[ga[r]['frame']]if r in ga else ZERO for r in regs})
 final={q:FULL for q in range(960)};final.update({960+q:target_caps[q]for q in range(960)});final.update({idx[r]:FULL for r in regs});assert len(initial)==len(final)==n
 assert Counter(dim[initial[idx[r]]]for r in regs)=={0:6900,16:1200}
 # Exact source frame IDs are rebound into this fresh local registry.
 original=[]
 for i,e in enumerate(events):e=dict(e,frame=source_map[e['frame']],original_index=i);original.append(e)
 events=original
 categories=sorted({e['semantic'][0]for e in events});category={s:i for i,s in enumerate(categories)}
 state=dict(initial);paths={q:[f]for q,f in initial.items()};records=[];H=Counter();temporary=None;operand_events=Counter();MOVE_pairs=set()
 def need(s,f):
  prev=state[s]
  if prev==f:return
  assert sub(prev,f),('frame chronology',s,prev,f,F[prev]['key'],F[f]['key']);gap=dim[f]-dim[prev];records.append([0,s,prev,f,gap,0]);paths[s].append(f);state[s]=f;MOVE_pairs.add((prev,f))
  if gap:H[gap]+=1
 for e in events:
  op,a,b,c,f=(e[k]for k in('op','a','b','c','frame'));operand_events[e['semantic'][0]]+=1
  if op==1:need(a,f);need(b,f);records.append([1,a,b,c,f,category[e['semantic'][0]]])
  elif op==2:
   assert temporary is None and b==n;need(a,f);state[b]=ZERO;paths[b]=[ZERO];temporary=(a,b,f);records.append([2,a,b,f,ZERO,dim[f]]);H[dim[f]]+=1
  else:
   assert op==3 and temporary==(a,b,f)and state[a]==f and state[b]==ZERO;records.append([3,a,b,f,ZERO,dim[f]]);del state[b];del paths[b];temporary=None
 for q,f in sorted(final.items()):need(q,f)
 assert temporary is None and state==final
 # Independent actual source/internal/target histogram partition from paths.
 parts={name:Counter()for name in('source','target','helper','copies')}
 for q,chain in paths.items():
  part='source'if q<960 else'target'if q<1920 else'helper'
  for a,b in zip(chain,chain[1:]):
   gap=dim[b]-dim[a]
   if gap:parts[part][gap]+=1
 for e in events:
  if e['op']==2:parts['copies'][dim[e['frame']]]+=1
 assert H==sum(parts.values(),Counter())and parts['source']=={17:960,2:960}and parts['copies']=={18:20}
 assert sum(r*c for r,c in H.items())==179640
 # Track all exact integer input-source coefficients through non-target ports.
 cols=[{q:1}if q<960 else{}for q in range(n+1)];checks=set();copied_support_checks=0
 def contained(f,q):
  if(f,q)not in checks:assert all(sum(row[j]for j in g['labels'][q])==0 for row in A[f]),('integer input source outside operand frame',f,q,F[f]['key']);checks.add((f,q))
 for e in events:
  op,a,b,c,f=(e[k]for k in('op','a','b','c','frame'))
  if op==2:
   for q in cols[a]:contained(f,q);copied_support_checks+=1
   cols[b]=dict(cols[a]);continue
  if op==3:assert cols[a]==cols[b];cols[b]={};continue
  # The copied work's ZERO-frame scatter uses the retained COPY contract;
  # it is not incorrectly claimed to contain the source in the ZERO subspace.
  for port in(a,b):
   if port!=n and not 960<=port<1920:
    for q in cols[port]:contained(f,q)
  if not 960<=a<1920:
   assert b<960 or b>=1920
   for q,x in cols[b].items():
    y=cols[a].get(q,0)+c*x
    if y:cols[a][q]=y
    else:cols[a].pop(q,None)
   for q in cols[a]:contained(f,q)
 assert cols[:960]==[{q:1}for q in range(960)]and all(not z for z in cols[1920:])
 # Every target path remains in its own exact terminal cap.
 for q in range(960):
  for f in paths[960+q]:assert sub(f,target_caps[q])
 # Primitive row-space checks and every rank/nondegeneracy are independently
 # repeated by validate_local.py; this builder supplies exact integer witnesses.
 endpoints=dict(n=n,initial=initial,final=final,removed_sink_columns=[],categories=categories,record_format='MOVE[0,stream,old_frame,new_frame,rank_gap,0]; ADD[1,dest,source,coefficient,frame,category_id]; COPY/ERASE[2or3,source,scratch,source_frame,zero_frame,rank].')
 rolemap=dict(virtual_roles=R,physical_helpers=len(regs),physical_by_virtual=physical,representative_by_physical={idx[r]:r for r in regs},aliases=aliases,source_helpers={q:physical[r]for q,r in map(lambda kv:(int(kv[0]),kv[1]),w['sources'].items())})
 dump('local-events.json.gz',events);dump('local-records.json.gz',records);dump('local-frames.json.gz',F);dump('local-endpoints.json',endpoints);dump('local-paths.json.gz',paths);dump('role-map.json',rolemap);dump('source-frame-map.json',source_map)
 fw,bw=receipt['forward_norm'],receipt['inverse_norm'];payload=64*fw**3*bw**2;assert payload<2**104
 result=dict(status='PASS_FRESH_PR325_480_RETIMINGS_FULL_LOCAL_FRAME_WORD',head=receipt['head'],candidate_sha256=receipt['word_gzip_sha256'],source_manifest_sha256=sha(SRC/'MANIFEST.json'),source_result_sha256=sha(SRC/'RESULT.json'),checker_sha256=sha(Path(__file__)),columns=n,physical_helpers=8100,records=len(records),frames=len(F),source_retimings=480,source_selections_imported_from_old_word=False,all_complete_source_helper_target_paths_nested=True,all_targets_in_terminal_caps=True,distinct_MOVE_containment_pairs=len(MOVE_pairs),one_stage_paid_histogram={str(r):c for r,c in sorted(H.items())},one_stage_calls=sum(H.values()),one_stage_rank_mass=sum(r*c for r,c in H.items()),histogram_parts={k:{str(r):c for r,c in sorted(v.items())}for k,v in parts.items()},initial_helper_rank_histogram={'0':6900,'16':1200},final_helper_rank_histogram={'20':8100},weighted_additions=receipt['weighted_additions'],literal_unit_additions=receipt['literal_unit_additions'],forward_norm=fw,inverse_norm=bw,payload_bound=payload,payload_bits=payload.bit_length(),integer_operand_source_support_checks=len(checks),all_nontarget_regular_operand_integer_sources_contained=True,copied_input_source_checks=copied_support_checks,copied_work_ZERO_scatter_uses_retained_COPY_contract=True,all_helper_integer_sources_restored=True,all_source_integer_values_restored=True,all_COPY_lifetimes_exact=True,scope='Fresh complete finite local frame stream on only the 480 source-retimed PR325 base. Rational all-frame verification is in the separately bound validator; arbitrary-dirty frame invariant and COPY theorem, global lowering, bank/invoice/price, prime/all-field, full-C/complex and all-size interfaces remain explicitly scoped.',artifacts={name:sha(P/name)for name in['local-events.json.gz','local-records.json.gz','local-frames.json.gz','local-endpoints.json','local-paths.json.gz','role-map.json','source-frame-map.json']})
 dump('RESULT.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':run()
