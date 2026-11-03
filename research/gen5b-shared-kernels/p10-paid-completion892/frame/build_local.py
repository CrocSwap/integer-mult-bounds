from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions()
"""Independent local frame-tagged constructor. Upstream programs are inert.
Uses hash-verified independently authored scalar expansion and exact linear
algebra, with new semantic frame lowering and freshly screened actual reorders.
"""
from pathlib import Path
from collections import Counter,defaultdict
from functools import lru_cache
from fractions import Fraction as Q
import json,hashlib,gzip,sys
P=support.FRAME
ADM=support.HERE/"admission"
support.verify_admission()
m=json.loads((support.ADM/'MANIFEST.json').read_text())
for z in m['files']:
 p=support.admission_artifact(z['path']);assert len(p.read_bytes())==z['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==z['sha256'],z['path']
sys.path.insert(0,str(ADM))
from weighted_source_data import read,verify,HEAD
from admission_config import OVER,OVER_SHA
from check_scalar_recurrence import scalar_word,replay
from check_transport import rr,null,included
if not __debug__:raise RuntimeError('Assertions must be enabled')
def dump(name,d):
 raw=(json.dumps(d,separators=(',',':'),sort_keys=True)+'\n').encode();(P/name).write_bytes(gzip.compress(raw,mtime=0)if name.endswith('.gz')else raw)
def run():
 verify();assert hashlib.sha256(OVER.read_bytes()).hexdigest()==OVER_SHA
 w=json.loads(OVER.read_text());g=read('graph.json');F={int(k):v for k,v in read('frames.json')['frames'].items()};ks=read('kernel-selection.json');K=read('kchron.json')['entries'];D=read('descent-selection.json')['entries'];R=read('restore-selection.json')['entries'];T=read('target-selection.json')['groups'];S=read('sink-selection.json')['sinks'];Z=read('reorder-selection.json')
 ev,n,*_=scalar_word(w,[]);ga={e['role']:e for e in w['gauges']};aliases={b:a for a,b in w['pairs']};regs=sorted(set(range(9120))-set(aliases));sid0={r:1920+i for i,r in enumerate(regs)};sid=lambda r:sid0[aliases.get(r,r)]
 desc={(e['scalar'][0],e['scalar'][1]):i for i,e in enumerate(D)};assert len(desc)==480 and all(e['scalar'][2:]==[1,20]for e in D)
 restore={(e['helper'],e['donor']):i for i,e in enumerate(R)};target={int(q):j for j,e in enumerate(T)for q in e['dependent']};partners={e['carrier']:e for e in K};sinks={e['stream']:i for i,e in enumerate(S)}
 kernels=[dict(pivot=e['a'],donors=[e['b']],basis=e['basis'],rank=e['rank'])for e in ks['pairs']]+[dict(pivot=e['pivot'],donors=e['donors'],basis=e['basis'],rank=e['rank'])for e in ks['families']];kernel={e['pivot']:j for j,e in enumerate(kernels)}
 # Bind every old selected physical operand through its virtual representative.
 oldword=read('bitword/selected/bit/word_p10.json.gz');oldalias={b:a for a,b in oldword['pairs']};oldregs=sorted(set(range(9120))-set(oldalias));oldinv={1920+j:r for j,r in enumerate(oldregs)}
 xlat=lambda s:sid(oldinv[s])if s>=1920 else s
 assert set(oldregs)-set(regs)=={9118,9119}and not set(regs)-set(oldregs)
 assert all(sid0[r]==s for s,r in oldinv.items()if r in sid0)
 selected_ports={s for e in kernels for s in[e['pivot']]+e['donors']}|{e[k]for e in R for k in('helper','donor')}|{e['stream']for e in S}
 assert all(xlat(s)==s for s in selected_ports)
 oldremoved=sorted(e['stream']for e in S)
 def lift(s):
  for r in oldremoved:
   if r<=s:s+=1
  return s
 assert all(xlat(lift(s))==lift(s)for e in Z['moves']for s in e['incidence'][:2])
 binding=dict(old_representatives=len(oldregs),new_representatives=len(regs),removed_representatives=[9118,9119],all_retained_representative_ids_unchanged=True,selected_uncompacted_ports=len(selected_ports),all_selected_kernel_restore_sink_ports_rebound_and_unchanged=True,all266_reorder_ports_rebound_and_unchanged=True)
 registry={};framekeys={};infos={}
 def fid(key):
  if key not in framekeys:framekeys[key]=len(framekeys);registry[framekeys[key]]=key
  return framekeys[key]
 ZERO=fid(('zero',0));FULL=fid(('frame',w['full_frame']))
 @lru_cache(None)
 def info(f):
  kind,x=registry[f]
  if kind=='zero':return 0,[[int(i==j)for j in range(20)]for i in range(20)],[]
  if kind=='frame':
   z=F[x];dim=z['dim'];a=z.get('a');b=z.get('b');return dim,a if a is not None else null(b),b
  if kind=='cap':return 19,[[3*int(j in g['labels'][x])-1 for j in range(20)]],None
  rows={'descent':D[x]['new_basis']if kind=='descent'else None,'restore':R[x]['basis']if kind=='restore'else None,'target':T[x]['close_basis']if kind=='target'else None,'sink':S[x]['root_frame_basis']if kind=='sink'else None,'kernel':kernels[x]['basis']if kind=='kernel'else None,'reorder':Z['moves'][x]['frame_basis']if kind=='reorder'else None}[kind]
  assert len(rr(rows)[0])==len(rows);return len(rows),null(rows),rows
 @lru_cache(None)
 def sub(a,b):
  if a==b:return True
  da,A,_=info(a);db,B,_=info(b)
  return da<=db and included(B,A)
 def equal(a,b):return info(a)[0]==info(b)[0]and sub(a,b)
 def frame(sem):
  k=sem[0]
  if k in('plain','center_read','target_setup','sink_setup'):return ZERO
  if k in('cleanup','uninject','partner_cleanup','kernel_restore'):return FULL
  if k=='inject':return fid(('frame',w['source_frame'][sem[1]]))
  if k in('forward','sink_redirect'):return fid(('frame',w['op_frame'][sem[1]if k=='forward'else sem[2]]))
  if k=='gauge':return fid(('frame',ga[sem[1]]['frame']))
  if k in('root','center'):return fid(('frame',w['root_frame'][sem[1]]))
  if k=='target_restore':return fid(('target',target[sem[1]]))
  if k=='partner_setup':return fid(('descent',desc[sem[1],sem[2]]))
  if k=='partner_delivery':return fid(('frame',partners[sem[1]]['deliver_frame']))
  if k=='early_restore':return fid(('restore',restore[sem[1],sem[2]]))
  if k=='kernel_setup':return fid(('kernel',kernel[sem[1]]))
  if k=='sink_restore':return fid(('sink',sinks[sem[1]]))
  raise AssertionError(sem)
 initial={q:fid(('frame',w['source_frame'][q]))for q in range(960)}|{q:ZERO for q in range(960,1920)}|{sid0[r]:fid(('frame',ga[r]['frame']))if r in ga else ZERO for r in regs}
 initial.update({e['pivot']:fid(('kernel',j))for j,e in enumerate(kernels)})
 final={q:FULL for q in initial};final.update({960+q:fid(('cap',q))for q in range(960)});final.update({e['helper']:fid(('restore',j))for j,e in enumerate(R)})
 removed=sorted(e['stream']for e in S)
 assert all(not any(a==s or b==s for op,a,b,c,sem in ev)for s in removed)
 compact=lambda s:s-sum(x<s for x in removed)
 nn=n-len(removed);initial={compact(s):f for s,f in initial.items()if s not in removed};final={compact(s):f for s,f in final.items()if s not in removed}
 events=[dict(op=op,a=compact(a),b=compact(b),c=c,frame=frame(sem),semantic=list(sem),original_index=i)for i,(op,a,b,c,sem)in enumerate(ev)]
 print('Built semantic frames',len(events),'columns',nn,'frames',len(registry),flush=True)
 incidence=defaultdict(list)
 for i,e in enumerate(events):
  incidence[e['a']].append(i)
  if e['op']==1:incidence[e['b']].append(i)
 def chain_hist(port,ordered):
  chain=[initial[port]]+[f for i,f in ordered]+[final[port]];h=Counter()
  for a,b in zip(chain,chain[1:]):
   if not sub(a,b):return None
   if info(b)[0]>info(a)[0]:h[info(b)[0]-info(a)[0]]+=1
  return h
 # Independently choose actual semantic anchors with exactly the frozen frame
 # and side, rejecting every noncommuting crossing and any nonnested endpoint.
 moves={};before=defaultdict(list);after=defaultdict(list);move_receipts=[];allports=set();delta=Counter()
 for j,z in enumerate(Z['moves']):
  a,b,c=z['incidence'];assert not{a,b}&allports;allports|={a,b}
  kinds=lambda e:'forward_gate'if e['semantic'][0]=='forward'else'side_root'if e['semantic'][0]=='root'else e['semantic'][0]
  hits=[i for i in incidence[a]if events[i]['op']==1 and[events[i]['a'],events[i]['b'],events[i]['c']]==[a,b,c]and kinds(events[i])==z['category']];assert len(hits)==1;at=hits[0];nf=fid(('reorder',j));assert info(events[at]['frame'])[0]==z['old_frame_rank']and info(nf)[0]==z['frame_rank']
  ports={a,b};candidates=[i for i in sorted(set(incidence[a]+incidence[b]),reverse=z['side']=='after')if events[i]['op']==1 and((i>at)if z['side']=='before'else(i<at))and equal(events[i]['frame'],nf)]
  valid=[]
  for anchor in candidates:
   lo,hi=(at+1,anchor)if z['side']=='before'else(anchor+1,at)
   if any((e['op']==1 and(e['b']==a or e['a']==b))or(e['op']in(2,3)and e['a']==a)for e in events[lo:hi]):continue
   localdelta=Counter();position=anchor-0.5 if z['side']=='before'else anchor+0.5
   for port in(a,b):
    oldpath=[(i,events[i]['frame'])for i in incidence[port]];newpath=sorted([(i,f)for i,f in oldpath if i!=at]+[(position,nf)])
    oldh=chain_hist(port,oldpath);newh=chain_hist(port,newpath)
    assert oldh is not None
    if newh is None:break
    localdelta.update(newh);localdelta.subtract(oldh)
   else:valid.append((anchor,localdelta));break
  assert valid,('no valid anchor',j,z['record'],len(candidates))
  anchor,ld=valid[0];delta.update(ld);moves[at]=dict(events[at],frame=nf,moved=True);(before if z['side']=='before'else after)[anchor].append(at)
  move_receipts.append(dict(selection_index=j,old_selected_record=z['record'],old_selected_anchor=z['anchor'],moved_event_index=at,new_anchor_event_index=anchor,new_anchor_semantic=events[anchor]['semantic'],side=z['side'],local_delta={str(k):v for k,v in ld.items()if v},literal_crossed_interval_checked=True,nested_paths_checked=True))
 assert {str(k):v for k,v in sorted(delta.items())if v}==Z['expected_local_delta'],('reorder delta',delta,Z['expected_local_delta'])
 reordered=[]
 for i,e in enumerate(events):
  reordered.extend(moves[j]for j in sorted(before[i]))
  if i not in moves:reordered.append(e)
  reordered.extend(moves[j]for j in sorted(after[i]))
 print('All133 explicit reorders screened; compiling MOVE records',flush=True)
 categories=sorted({e['semantic'][0]for e in events}|{'reorder_moved'});catid={k:j for j,k in enumerate(categories)}
 def compile(events):
  state=dict(initial);out=[];hist=Counter();tmp=None;paths=defaultdict(list)
  def need(s,f):
   old=state[s]
   if old==f:return
   assert sub(old,f),('frame chain',s,registry[old],registry[f])
   gap=info(f)[0]-info(old)[0];out.append([0,s,old,f,gap,0]);state[s]=f
   if gap:hist[gap]+=1
   paths[s].append([old,f,gap])
  for e in events:
   op,a,b,c,f=e['op'],e['a'],e['b'],e['c'],e['frame']
   if op==1:
    need(a,f)
    if b!=nn:need(b,f)
    else:assert tmp is not None and f==ZERO
    out.append([1,a,b,c,f,catid['reorder_moved'if e.get('moved')else e['semantic'][0]]])
   elif op==2:
    assert tmp is None and b==nn;need(a,f);state[b]=ZERO;tmp=(a,b,f);out.append([2,a,b,f,ZERO,info(f)[0]]);hist[info(f)[0]]+=1
   else:
    assert op==3 and tmp==(a,b,f)and state[a]==f and state[b]==ZERO;out.append([3,a,b,f,ZERO,info(f)[0]]);del state[b];tmp=None
  for s,f in sorted(final.items()):need(s,f)
  assert state==final and tmp is None
  return out,hist,paths
 pre,preH,_=compile(events);records,H,paths=compile(reordered)
 assert Counter(H)-Counter(preH)==+delta and Counter(preH)-Counter(H)==-delta
 # Independent scalar/COPY endpoint replay on the actual compact reordered word.
 projected=[(e['op'],e['a'],e['b'],e['c'],tuple(e['semantic']))for e in reordered]
 fw=replay(projected,nn);bw=replay(projected,nn,True)
 assert fw['weighted_additions']==336253 and fw['literal_unit_additions']==338173 and fw['max_row_l1']==132143 and bw['max_row_l1']==1307556
 print('Compiled records',len(records),'paid calls',sum(H.values()),'rank mass',sum(k*v for k,v in H.items()),'scalar identity PASS',flush=True)
 # Exact integer source-support containment for every non-target operand.
 columns=[{q:1}if q<960 else{}for q in range(nn+1)];support_checks=set();copy=None
 for e in reordered:
  op,a,b,c,f=e['op'],e['a'],e['b'],e['c'],e['frame']
  if op==2:assert copy is None;columns[b]=dict(columns[a]);copy=a;continue
  if op==3:assert copy==a;copy=None;continue
  if not 960<=a<1920:
   assert not 960<=b<1920
   ca=columns[a]
   for q,x in columns[b].items():
    y=ca.get(q,0)+c*x
    if y:ca[q]=y
    else:ca.pop(q,None)
  sources=set()
  if not 960<=a<1920:sources.update(columns[a])
  if b!=nn and not 960<=b<1920:sources.update(columns[b])
  for q in sources:
   if(f,q)in support_checks:continue
   assert all(sum(row[j]for j in g['labels'][q])==0 for row in info(f)[1]),('source span',e,q,registry[f]);support_checks.add((f,q))
 print('Every gate source-support frame passes',len(support_checks),'distinct checks',flush=True)
 used=set(initial.values())|set(final.values())|{e['frame']for e in reordered};frames={str(i):dict(key=registry[i],rank=info(i)[0],annihilator=[[str(x)for x in row]for row in info(i)[1]],basis=[[str(x)for x in row]for row in(info(i)[2]if info(i)[2]is not None else null(info(i)[1]))])for i in sorted(used)}
 dump('local-records.json.gz',records);dump('local-events.json.gz',reordered);dump('local-frames.json.gz',frames);dump('local-endpoints.json',dict(n=nn,initial=initial,final=final,removed_sink_columns=removed,categories=categories,record_format='Six integer fields: MOVE[0,stream,old_frame,new_frame,rank_gap,0]; ADD[1,dest,source,coefficient,frame,category_id]; COPY/ERASE[2or3,source,scratch,source_frame,zero_frame,rank]. Scratch is exactly n; all physical streams are0..n-1.'));dump('local-paths.json.gz',paths);dump('reorder-receipts.json',move_receipts)
 out=dict(status='PASS_EXPLICIT_LOCAL892_FRAME_WORD',head=HEAD,candidate_sha256=OVER_SHA,checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),columns=nn,records=len(records),frames=len(frames),moves=133,one_stage_paid_histogram={str(k):v for k,v in sorted(H.items())},one_stage_calls=sum(H.values()),one_stage_rank_mass=sum(k*v for k,v in H.items()),pre_reorder_histogram={str(k):v for k,v in sorted(preH.items())},reorder_delta={str(k):v for k,v in sorted(delta.items())if v},forward=fw,inverse=bw,distinct_integer_source_support_checks=len(support_checks),all_integer_operand_source_spans_contained=True,source_descent_entries=480,scope='Explicit local frame word with actual 133 newly screened equivalent-anchor reorders. Fixed frame nondegeneracy and global compilation/prime/all-size interfaces remain separate. No upstream program execution.',artifacts={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(P.iterdir())if p.name.startswith('local-')or p.name=='reorder-receipts.json'})
 out['physical_rebinding']=binding
 dump('RESULT.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':run()
