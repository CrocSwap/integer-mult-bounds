"""Independent event/value and address chronology audit of the actual471 retiming."""
from pathlib import Path
from collections import Counter,defaultdict
import importlib.util,json,sys,hashlib
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('scalar471',HERE/'replay.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);W=m.W;C=m.C
schedule=m.schedule;events=[]
def port(s):
 p=W.phys[s];return('x',m.borrow[p])if p in m.borrow else('z',p)
for e in schedule['events']:
 i=e['op']
 if e['kind']=='early_mix':
  r=m.early[i];events.append(dict(op=i,kind='early_mix',dest=('x',r['partner']),source=('x',r['source']),frame=m.kpair[r['source']]['mix_frame']))
 else:
  a,b,n=W.ops[i];events.append(dict(op=i,kind='operation',dest=port(a),source=port(b),frame=W.opframe[i]))
prefix=schedule['center_prefix_events'];deferred=schedule['deferred_events'];rest=schedule['remaining_events'];neworder=prefix+deferred+rest
assert [events[k]['op']for k in prefix if events[k]['kind']=='operation']==W.phase1
assert [events[k]['op']for k in deferred+rest if events[k]['kind']=='operation']==W.rest
assert len(neworder)==len(set(neworder))==len(events)
def trace(order):
 writes={};inputs={};frames={};edges=0;paths=defaultdict(list)
 for k in order:
  e=events[k];a,b,f=e['dest'],e['source'],e['frame'];inputs[k]=(writes.get(a,-1),writes.get(b,-1))
  for p in[a,b]:
   old=frames.get(p)
   assert old is None or C.sub(old,f),('address descent',k,p,old,f)
   if old is not None:edges+=1
   frames[p]=f;paths[p].append(f)
  writes[a]=k
 return inputs,writes,frames,edges,paths
oldinput,oldwrite,oldframes,oldedges,oldpaths=trace(range(len(events)));newinput,newwrite,newframes,newedges,newpaths=trace(neworder)
assert oldinput==newinput and oldwrite==newwrite and oldframes==newframes
assert set(oldpaths)==set(newpaths)
def jumps(path):
 previous=0;out=Counter()
 for f in path:
  d=C.dimf[f];assert d>=previous
  if d>previous:out[d-previous]+=1
  previous=d
 return out
assert all(jumps(oldpaths[p])==jumps(newpaths[p])for p in oldpaths)
assert all([C.dimf[f]for f in oldpaths[p]]==[C.dimf[f]for f in newpaths[p]]for p in oldpaths), 'complete actual address-frame dimension stream changed' 
assert all(all(C.sub(a,b)and C.sub(b,a)for a,b in zip(oldpaths[p],newpaths[p]))for p in oldpaths), 'complete exact physical subspace stream changed'
_,prefixwrite,prefixframes,_,_=trace(prefix)
for r,s in zip(W.g['roots'],W.w['rootroles']):
 if r['kind']=='center':assert prefixwrite[port(s)]==oldwrite[port(s)]
centerports={port(s)for r,s in zip(W.g['roots'],W.w['rootroles'])if r['kind']=='center'}
assert all(not(centerports&{events[k]['dest'],events[k]['source']})for k in deferred+rest),'no later middle consumer bypassed atcopied center'
center_ranks=Counter()
for j,(r,s)in enumerate(zip(W.g['roots'],W.w['rootroles'])):
 if r['kind']=='center':
  f=W.w['root_frame'][j];assert C.sub(prefixframes[port(s)],f)and C.sub(f,prefixframes[port(s)])
  center_ranks[C.dimf[f]]+=1
newports={port(s)for s in m.new_phase_roles}
assert all(not(newports&{events[k]['dest'],events[k]['source']})for k in prefix)
assert {events[k]['op']for k in prefix if events[k]['kind']=='early_mix'}==set(m.early)
assert all(events[k]['kind']=='operation'for k in deferred+rest)
assert all(W.readtime[s]==0 for s in m.new_phase_roles)
assert all(W.readtime[s]>=168 for s in W.gauge if s not in m.new_phase_roles)
assert all(W.readtime[s]<=W.first[s]for s in W.gauge)
assert all(W.last[d]<W.readtime[b]for b,d in W.pairs)
# The only pre-center target reads remain original ungauged corrections at0.
# New source/Kmix movement affects X only; all gauge corrections followcenter.
receipt=dict(status='PASS_SOURCE471_EXACT_EVENT_AND_ADDRESS_RETIMING',events=len(events),center_prefix_events=len(prefix),center_prefix_operations=len(W.phase1),deferred_operations=len(deferred),early_source_mixes_in_prefix=len(m.early),source_heads=len(m.borrow),formal_columns=2*W.v+len(m.regs),every_actual_input_preceding_write_preserved=True,every_final_write_preserved=True,all_physical_frame_paths_nested=True,all_actual_address_frame_dimension_streams_preserved=True,all_exact_address_subspace_streams_preserved=True,all_address_jump_histograms_preserved=True,physical_frame_inclusions_checked=newedges,all_center_reads_see_identical_last_write=True,no_later_center_middle_consumer=True,copied_center_rank_histogram=dict(center_ranks),copied_center_paid_copy_rank_mass=sum(d*n for d,n in center_ranks.items()),new_source_heads_physically_untouched_before_centers=True,all_target_gauge_reads_after_center_scatter=True,all_new_gauges_before_deferred_ops=True,all_original_gauge_reads_shifted_by168=True,all_alias_lifetimes_retained=True,input_pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in[HERE/'replay.py',HERE/'selection.json',HERE/'schedule.json',Path(__file__)]})
(HERE/'schedule-audit.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2),flush=True)
