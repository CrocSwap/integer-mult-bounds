from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import companion as packet
packet.require_assertions()
packet.verify_base()
packet.verify_sources()
"""Independent PR322/323 witness composition and full local frame emission.
Selections are inert immutable source data, credited to eumemic/OpenAI Codex.
The PR322 retiming mechanism retains Rohan Arun/PR287/Anthropic provenance.
New independent construction and audit: OpenAI assistance, Apache-2.0.
"""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as Q
from functools import lru_cache
import json,gzip,hashlib,copy,sys
P=packet.ADMISSION
BASE=packet.BASE_FRAME
ADM=packet.BASE_CODE/"admission"
EXP=packet.EXPERIMENT
if not __debug__:raise RuntimeError('Assertions must be enabled')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 raw=Path(p).read_bytes();return json.loads(gzip.decompress(raw)if str(p).endswith('.gz')else raw)
def dump(name,x):
 raw=(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode();(P/name).write_bytes(gzip.compress(raw,mtime=0)if name.endswith('.gz')else raw)
packet.verify_base()
sys.path.insert(0,str(ADM))
from weighted_source_data import read as source,verify,HEAD
from admission_config import OVER,OVER_SHA
from check_transport import rr,null
from check_scalar_recurrence import replay
verify();assert sha(OVER)==OVER_SHA
provenance=read(packet.SOURCE_PROVENANCE)
for z in provenance['files']:
 b=(packet.INPUTS/z['label']).read_bytes();assert len(b)==z['bytes']and hashlib.sha256(b).hexdigest()==z['sha256'];assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==z['sha']
assert sha(packet.INPUTS/'pr322-presink-selection.json')=='166fa4ce7259d35a020c51682c6f18256f3fdad260473f8209e53114285c8934'
assert sha(packet.INPUTS/'pr323-kernel2-selection.json')=='bcfdc7ec8a61d49201961077fbc512f516dcbebac4281d5cd7d2350ced3ee9e0'

def run():
 base=read(BASE/'RESULT.json');assert base["checker_sha256"]==sha(packet.BASE_CODE/"frame/build_local.py")
 events=read(BASE/'local-events.json.gz');end=read(BASE/'local-endpoints.json');F={int(k):v for k,v in read(BASE/'local-frames.json.gz').items()};initial={int(k):v for k,v in end['initial'].items()};final={int(k):v for k,v in end['final'].items()};n=end['n'];assert n==10141
 A={f:[[Q(x)for x in row]for row in z['annihilator']]for f,z in F.items()};B={f:[[Q(x)for x in row]for row in z['basis']]for f,z in F.items()};dim={f:z['rank']for f,z in F.items()};ZERO=next(f for f,d in dim.items()if d==0);FULL=next(f for f,d in dim.items()if d==20)
 def install(rows,label):
  assert len(rr(rows)[0])==len(rows);f=max(F)+1;F[f]=dict(rank=len(rows),key=[label,f],basis=[[str(x)for x in row]for row in rows],annihilator=[[str(x)for x in row]for row in null(rows)]);B[f]=list(map(lambda row:list(map(Q,row)),rows));A[f]=list(map(lambda row:list(map(Q,row)),F[f]['annihilator']));dim[f]=len(rows);return f
 @lru_cache(None)
 def sub(a,b):return dim[a]<=dim[b]and all(sum(x*y for x,y in zip(u,v))==0 for u in A[b]for v in B[a])
 w=read(OVER);old=source('bitword/selected/bit/word_p10.json.gz');ga={e['role']:e for e in w['gauges']};g=source('graph.json');removed=end['removed_sink_columns'];compact=lambda s:s-sum(x<s for x in removed)
 def lift(s):
  for r in removed:
   if r<=s:s+=1
  return s
 oldalias={b:a for a,b in old['pairs']};newalias={b:a for a,b in w['pairs']};oldregs=sorted(set(range(9120))-set(oldalias));newregs=sorted(set(range(9120))-set(newalias));oldinv={1920+i:r for i,r in enumerate(oldregs)};newids={r:1920+i for i,r in enumerate(newregs)}
 transport=lambda s:compact(newids[newalias.get(oldinv[lift(s)],oldinv[lift(s)])])if s>=1920 else s
 transport_pre=lambda s:compact(newids[newalias.get(oldinv[s],oldinv[s])])if s>=1920 else s
 assert 1920+len(oldregs)-7==10143 and 1920+len(newregs)-7==n
 R=read(packet.INPUTS/'pr322-presink-selection.json');K=read(packet.INPUTS/'pr323-kernel2-selection.json');assert K['n']==10143
 rolebind=[]
 for e in R['entries']:
  for s in e['scalar'][:2]:
   t=transport_pre(s);assert t==compact(s);rolebind.append(dict(witness='PR322',old_uncompact=s,virtual_role=oldinv[s],new_compact=t))
 for e in K['families']:
  for s in[e['pivot']]+e['donors']:
   t=transport(s);assert t==s;rolebind.append(dict(witness='PR323',old_compact=s,virtual_role=oldinv[lift(s)],new_compact=t))
 assert len(rolebind)==20
 # Reconstruct the pre-reorder scalar word from frozen semantic event IDs.
 # The133 moved frames revert to their original literal word frames here.
 mr=read(BASE/'reorder-receipts.json');byuid={e['original_index']:e for e in events};assert len(byuid)==len(events);bykey={tuple(z['key']):f for f,z in F.items()};moved={r['moved_event_index']:r for r in mr};assert len(moved)==133
 pre=copy.deepcopy(sorted(events,key=lambda e:e['original_index']))
 for e in pre:
  if e['original_index']in moved:
   sem=e['semantic'];assert sem[0]in('root','forward');key=('frame',w['root_frame'][sem[1]]if sem[0]=='root'else w['op_frame'][sem[1]]);e['frame']=bykey[key];e.pop('moved',None)
 def reorder(seq,check=False):
  where={e['original_index']:i for i,e in enumerate(seq)};before=defaultdict(list);after=defaultdict(list);ports=set();receipts=[]
  for uid,r in moved.items():
   i=where[uid];anchor=where[r['new_anchor_event_index']];e=seq[i];a,b=e['a'],e['b'];assert not{a,b}&ports;ports|={a,b};Fnew=byuid[uid]['frame'];target=seq[anchor];assert target['op']==1 and{target['a'],target['b']}&{a,b};assert dim[target['frame']]==dim[Fnew]and sub(target['frame'],Fnew)
   lo,hi=(i+1,anchor)if r['side']=='before'else(anchor+1,i);assert lo<=hi
   for z in seq[lo:hi]:
    if z['op']==1:assert z['b']!=a and z['a']!=b
    else:assert z['a']!=a
   e=dict(e,frame=Fnew,moved=True);(before if r['side']=='before'else after)[anchor].append((uid,e))
   receipts.append(dict(moved_uid=uid,anchor_uid=r['new_anchor_event_index'],new_pre_event=i,new_anchor_event=anchor,side=r['side'],frame=Fnew,moved_semantic=e['semantic'],anchor_semantic=target['semantic'],literal_crossed_interval_verified=True))
  out=[]
  for i,e in enumerate(seq):
   out.extend(e for _,e in sorted(before[i]))
   if e['original_index']not in moved:out.append(e)
   out.extend(e for _,e in sorted(after[i]))
  return out,receipts,ports
 assert reorder(pre)[0]==events
 # Four immutable constructed frames; exact scalar category and old basis hash.
 retimings=[];changed=set();retimed=copy.deepcopy(pre)
 for z in R['entries']:
  a,b=map(transport_pre,z['scalar'][:2]);hits=[i for i,e in enumerate(retimed)if e['op']==1 and(e['a'],e['b'],e['c'])==(a,b,z['scalar'][2])and e['semantic'][0]=='kernel_setup'];assert len(hits)==1;i=hits[0];e=retimed[i];f=e['frame'];assert dim[f]==z['old_dimension']
  ints=[[int(x)for x in row]for row in B[f]];assert all(Q(x)==y for x,y in zip(sum(ints,[]),sum(B[f],[])));assert hashlib.sha256(json.dumps(ints,separators=(',',':')).encode()).hexdigest()==z['old_basis_sha256']
  newf=install(z['new_basis'],'PR322-retime');assert dim[newf]==z['new_dimension'];e['frame']=newf;changed|={a,b};retimings.append(dict(uid=e['original_index'],semantic=e['semantic'],old_frame=f,new_frame=newf,source_record=z['record'],a=a,b=b))
 # Per-family literal chronology and all-column prefix responses at each own cut.
 families=copy.deepcopy(K['families']);members={s for z in families for s in[z['pivot']]+z['donors']};assert len(members)==12 and not members&changed
 for z in families:
  for s in[z['pivot']]+z['donors']:assert initial[s]==ZERO and final[s]==FULL
  z['frame']=install(z['basis'],'PR323-kernel2')
 first={};last={};reads=defaultdict(list)
 for i,e in enumerate(retimed):
  if e['op']==1 and e['b']in members and e['frame']==ZERO and e['semantic'][0]=='plain':assert 960<=e['a']<1920;last[e['b']]=i;reads[e['b']].append(i);continue
  for s in([e['a'],e['b']]if e['op']==1 else[e['a']]):
   if s in members:first.setdefault(s,(i,e['frame']))
 bycut=defaultdict(list);pivots={z['pivot']:z for z in families}
 for z in families:
  ms=[z['pivot']]+z['donors'];cut=max(last[s]for s in ms);e=retimed[cut];assert[e['a'],e['b'],e['c']]==z['cut_read'];assert cut<min(first[s][0]for s in ms);assert all(sub(z['frame'],first[s][1])for s in ms);z['cut']=cut;z['cut_uid']=e['original_index'];z['removed_reads']=len(reads[z['pivot']]);bycut[cut].append(z)
 bits={s:1<<j for j,s in enumerate(sorted(members))};columns=[bits.get(s,0)for s in range(n+1)];tmp=None;relations=0
 for i,e in enumerate(retimed[:max(bycut)+1]):
  op,a,b,c=e['op'],e['a'],e['b'],e['c']
  if op==1:assert c%2;columns[a]^=columns[b]
  elif op==2:assert tmp is None;tmp=a;columns[b]=columns[a]
  else:assert tmp==a;tmp=None
  for z in bycut[i]:
   assert tmp is None;mask=sum(bits[s]for s in[z['pivot']]+z['donors']);nonzero=0
   for q in range(n):
    if 960<=q<1920:assert(columns[q]&mask).bit_count()%2==0;nonzero+=bool(columns[q]&bits[z['pivot']]);relations+=1
    else:assert columns[q]&mask==bits.get(q,0)&mask
   assert nonzero==len(reads[z['pivot']])>0;z['nonzero_target_responses']=nonzero
   assert any(columns[q]&bits[z['pivot']]for q in range(960,1920))
 assert relations==2880
 starts=dict(initial);starts.update({z['pivot']:z['frame']for z in families});combined=[];deleted=[];newuid=-1
 for i,e in enumerate(retimed):
  if e['op']==1 and e['b']in pivots and e['frame']==ZERO and e['semantic'][0]=='plain':assert i<=pivots[e['b']]['cut'];deleted.append(e['original_index'])
  else:combined.append(copy.deepcopy(e))
  for z in bycut[i]:
   for d in z['donors']:combined.append(dict(op=1,a=d,b=z['pivot'],c=1,frame=z['frame'],semantic=['new_kernel2_setup',z['pivot'],d],original_index=newuid));newuid-=1
 for z in families:
  for d in z['donors']:combined.append(dict(op=1,a=d,b=z['pivot'],c=-1,frame=FULL,semantic=['new_kernel2_restore',z['pivot'],d],original_index=newuid));newuid-=1
 assert len(deleted)==32 and newuid==-19
 combined,reorders,ports=reorder(combined,True);assert not(changed|members)&ports
 print('All source bindings,4 retimings,3 own-cut kernels and133 actual anchors pass',flush=True)
 # Cross-check, without importing/executing the independent experiment program.
 other=read(EXP/'combined-events.json.gz');projection=lambda es:[(e['op'],e['a'],e['b'],e['c'],e['frame'],e['semantic'])for e in es];assert projection(combined)==projection(other)
 otherend=read(EXP/'combined-endpoints.json.gz');assert starts=={int(k):v for k,v in otherend['initial'].items()}and final=={int(k):v for k,v in otherend['final'].items()}
 # Build all local frames, MOVEs, ADDs and COPY/ERASE records independently.
 categories=sorted(set(end['categories'])|{'new_kernel2_setup','new_kernel2_restore'});cat={z:i for i,z in enumerate(categories)}
 def compile(es,begin):
  state=dict(begin);out=[];H=Counter();paths=defaultdict(list);tmp=None
  def need(s,f):
   old=state[s]
   if old==f:return
   assert sub(old,f),('frame chronology',s,old,f);gap=dim[f]-dim[old];out.append([0,s,old,f,gap,0]);state[s]=f;paths[s].append([old,f,gap]);
   if gap:H[gap]+=1
  for e in es:
   op,a,b,c,f=e['op'],e['a'],e['b'],e['c'],e['frame']
   if op==1:need(a,f);need(b,f);out.append([1,a,b,c,f,cat['reorder_moved'if e.get('moved')else e['semantic'][0]]])
   elif op==2:assert tmp is None and b==n;need(a,f);state[b]=ZERO;tmp=(a,b,f);out.append([2,a,b,f,ZERO,dim[f]]);H[dim[f]]+=1
   else:assert op==3 and tmp==(a,b,f)and state[a]==f and state[b]==ZERO;out.append([3,a,b,f,ZERO,dim[f]]);del state[b];tmp=None
  for s,f in sorted(final.items()):need(s,f)
  assert state==final and tmp is None
  return out,H,paths
 records,H,paths=compile(combined,starts)
 expected=Counter({int(k):v for k,v in base['one_stage_paid_histogram'].items()})
 for hist in[R['expected_local_histogram_delta'],K['expected_local_delta']]:expected.update({int(k):v for k,v in hist.items()})
 assert H==expected and sum(H.values())==48486 and sum(k*v for k,v in H.items())==179458
 fw=replay([(e['op'],e['a'],e['b'],e['c'],tuple(e['semantic']))for e in combined],n);bw=replay([(e['op'],e['a'],e['b'],e['c'],tuple(e['semantic']))for e in combined],n,True)
 assert fw['weighted_additions']==336239 and fw['literal_unit_additions']==338159 and fw['max_row_l1']==132195 and bw['max_row_l1']==1307808
 controls=[]
 for kind in('new_kernel2_setup','new_kernel2_restore'):
  replay([(e['op'],e['a'],e['b'],e['c'],tuple(e['semantic']))for e in combined],n,omit=kind);controls.append(kind)
 payload=64*fw['max_row_l1']**3*bw['max_row_l1']**2;assert payload<2**104
 print('Full local frame records and fresh scalar/norm replay pass',len(records),flush=True)
 # Full exact integer source-span coverage, not just newly introduced frames.
 cols=[{q:1}if q<960 else{}for q in range(n+1)];checks=set()
 for e in combined:
  op,a,b,c,f=e['op'],e['a'],e['b'],e['c'],e['frame']
  if op==2:cols[b]=dict(cols[a]);continue
  if op==3:continue
  if not 960<=a<1920:
   assert not 960<=b<1920
   for q,x in cols[b].items():
    y=cols[a].get(q,0)+c*x
    if y:cols[a][q]=y
    else:cols[a].pop(q,None)
  need=set(cols[a])if not 960<=a<1920 else set()
  if b!=n and not 960<=b<1920:need.update(cols[b])
  for q in need:
   if(f,q)not in checks:assert all(sum(row[j]for j in g['labels'][q])==0 for row in A[f]),('source span',e,q);checks.add((f,q))
 for z in families:
  for s in[z['pivot']]+z['donors']:assert not cols[s]
 used=set(starts.values())|set(final.values())|{e['frame']for e in combined};frames={str(f):F[f]for f in sorted(used)}
 dump('local-records.json.gz',records);dump('local-events.json.gz',combined);dump('local-frames.json.gz',frames);dump('local-endpoints.json',dict(n=n,initial=starts,final=final,removed_sink_columns=removed,categories=categories,record_format=end['record_format']));dump('local-paths.json.gz',paths);dump('reorder-receipts.json',reorders);dump('new-kernel-receipts.json',families);dump('retiming-receipts.json',retimings);dump('physical-rebinding.json',rolebind)
 result=dict(status='PASS_PR322_PR323_COMPOSED_FULL_LOCAL_FRAME_WORD',head=HEAD,source_heads={'PR322':provenance['metadata'][0]['head'],'PR323':provenance['metadata'][1]['head']},candidate_sha256=OVER_SHA,checker_sha256=sha(Path(__file__)),source_provenance_sha256=sha(packet.SOURCE_PROVENANCE),base_frame_result_sha256=sha(BASE/'RESULT.json'),columns=n,records=len(records),frames=len(frames),moves=133,all133_actual_anchors_rechecked=True,retimings=4,new_kernels=3,new_kernel_own_cut_target_comparisons=relations,new_kernel_removed_reads=len(deleted),new_kernel_added_ADDs=18,all20_selected_physical_ports_rebound=True,all_changed_role_sets_disjoint_from133moved_operands=True,source_descent_entries=480,one_stage_paid_histogram={str(k):v for k,v in sorted(H.items())},one_stage_calls=sum(H.values()),one_stage_rank_mass=sum(k*v for k,v in H.items()),forward=fw,inverse=bw,payload_bound=payload,payload_bits=payload.bit_length(),distinct_integer_source_support_checks=len(checks),all_integer_operand_source_spans_contained=True,all_new_kernel_helper_integer_sources_restored=True,omission_controls_rejected=controls,independent_experiment_event_and_endpoint_agreement=True,scope='New independently reconstructed local frame word; exact fixed PR322/323 witnesses recomposed on paid892, not upstream whole-program replay. Current paid892 publication unchanged. Global lowering, bank completion, finite invoice, prime and all-size interfaces remain separate.',artifacts={p.name:sha(p)for p in sorted(P.iterdir())if p.name.startswith('local-')or p.name in('reorder-receipts.json','new-kernel-receipts.json','retiming-receipts.json','physical-rebinding.json')})
 dump('RESULT.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':run()
