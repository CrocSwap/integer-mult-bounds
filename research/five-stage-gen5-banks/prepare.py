"""Clean gen5 preparation: the arc-aware local-design paired-cube bit word with its physical layer.

The bit word (gen5bit/selected/bit) is admitted by PR200's unmodified physical-word classes
(gen5bit/bit/word.py, base_word.py) over PR168-v4's unmodified exact checker. The context exposes
the interface of the retained source527 scalar program (scalar/word.py, byte-identical); every
source527-specific selection (source loans, aggregation/rank/echelon groups, fresh and paired
source reads, terminal sinks, early mixes, retimed prefixes) is empty for this word.
No payload execution occurs here.
Prepared by DreamingOfClouds with Anthropic Claude assistance; Apache-2.0.
"""
from pathlib import Path
from collections import Counter,defaultdict
from types import SimpleNamespace
import hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
WORD_SHA='e675d4eb9d90ff0b44279fae0b46f1a8b39f65421cc38454b70a6b75d0e10b42'

def prepare():
 G=HERE/'gen5bit'
 spec=importlib.util.spec_from_file_location('gen5_pr200_physical_word',G/'bit/word.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 W=module.Candidate();C=W.C
 # Exact decoder/geometry of the virtual graph, and every changed operation frame and alias handoff.
 C.decoder();C.geometry();W.exact_frames()
 W.changed_frames=[i for i,(a,b)in enumerate(zip(W.original_opframe,W.opframe))if a!=b]
 W.endframe={r:W.opframe[ii[-1]]for r,ii in W.role_ops.items()}
 assert W.R==17292 and len(W.pairs)==1406 and len(W.gauge)==3960 and W.v==1760 and W.h==24 and len(W.changed_frames)==1710
 assert all(0<=W.readtime[s]<=W.first[s]for s in W.gauge)
 assert all(W.last[d]<W.readtime[b]and C.sub(W.endframe[d],W.gauge[b]['frame'])for b,d in W.pairs)
 assert all(not(set(W.gauge)&set(W.ops[i][:2]))for i in W.phase1)
 # The centre prefix is exactly phase one, executed in its listed order.
 schedule=dict(events=[dict(kind='gate',op=i)for i in W.phase1],center_prefix_events=list(range(len(W.phase1))),deferred_ops=[],new_phase1=list(W.phase1),new_untouched_roles=[])
 selection=[];gauge_selection=[];new_gauge_selection=[];extra_selection=[];new_phase_roles=set()
 borrow={};by_source={};omitted=set();early={};gauge_borrow={}
 kpair={e['passive']:e for e in W.k['entries']};assert len(kpair)==880
 adj=[{}for _ in range(W.R)]
 for r,s in zip(W.g['roots'],W.w['rootroles']):
  for t in r['targets']:adj[s][t]=adj[s].get(t,0)+1
 for i in reversed(W.phase1+W.rest):
  a,b,_=W.ops[i]
  for t,c in adj[a].items():adj[b][t]=adj[b].get(t,0)+c
 assert adj==W.adjoint()
 assert all(set(adj[s])==set(z['targets'])for s,z in W.gauge.items()),'gauge targets are exact response supports'
 terminal=[];removed=set();deletedroots=set();bywrite={};afterwrite={}
 regs=sorted(set(W.phys.values())-set(borrow)-removed);idx={r:2*W.v+j for j,r in enumerate(regs)}
 assert len(regs)==W.R-len(W.pairs)==15886
 at=defaultdict(list)
 for b in W.order:at[W.readtime[b]].append(b)
 deliveries=defaultdict(list)
 for e in W.k['entries']:deliveries[e['deliver_after_root']].append(e)
 m=SimpleNamespace(W=W,C=C,schedule=schedule,selection=selection,gauge_selection=gauge_selection,new_gauge_selection=new_gauge_selection,
  extra_selection=extra_selection,new_phase_roles=new_phase_roles,borrow=borrow,by_source=by_source,omitted=omitted,early=early,
  gauge_borrow=gauge_borrow,kpair=kpair,adj=adj,terminal=terminal,removed=removed,deletedroots=deletedroots,bywrite=bywrite,
  afterwrite=afterwrite,regs=regs,idx=idx,at=at,deliveries=deliveries,deferred=[],
  agg=[],role_groups={},target_group={},read_frames={},extra_byrole={},rankgroups=[],rankowner={},echelon=[],eowner={},
  fresh={},pair_byalias={},pair_bydirty={},pair_selection=[],zero=W.register([]),source_head='gen5')
 # Names the retained scalar program reads from its preparation namespace.
 m.Counter,m.defaultdict,m.json,m.sys,m.hashlib,m.Path=Counter,defaultdict,json,sys,hashlib,Path
 m.SOURCE_TEXT=(HERE/'scalar/word.py').read_text()
 assert hashlib.sha256(m.SOURCE_TEXT.encode()).hexdigest()==WORD_SHA
 m.input_pins={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(G.rglob('*'))if p.is_file()}
 m.portable_source_pins=dict(m.input_pins)
 return dict(m.__dict__)
