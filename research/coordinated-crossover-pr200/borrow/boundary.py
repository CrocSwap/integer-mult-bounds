#!/usr/bin/env python3
"""Independent source-slot endpoint and paid-path audit for440 copy elisions.
Prepared with OpenAI Codex assistance; no scalar replay duplicated here.
"""
import sys,json,importlib.util
from pathlib import Path
from collections import Counter,defaultdict
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;p=HERE.parent/'joint/joint_word.py'
spec=importlib.util.spec_from_file_location('boundary_seed',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
w=m.Candidate();C=w.C;C.decoder();C.geometry()
selection=json.loads((HERE/'selection.json').read_text())
recipient={d:b for b,d in w.pairs};kpair={e['passive']:e for e in w.k['entries']}
roots=defaultdict(list)
for j,s in enumerate(w.w['rootroles']):roots[s].append((j,w.w['root_frame'][j]))
full=w.w['full_frame'];source_roles=set(w.source.values())
results=[];delta=Counter();alias_count=0;all_early_delta=Counter()
def histogram(start,events):
 prev=start;hist=Counter()
 for tag,f in events:
  assert prev is None or C.sub(prev,f),('nonnested',tag,prev,f)
  d=C.dimf[f]-(C.dimf[prev] if prev is not None else 0)
  if d:hist[d]+=1
  prev=f
 return hist
for r in selection:
 s,n,i,early=r['role'],r['source'],r['omit_copy'],r['early']
 assert s not in w.gauge and s not in source_roles and s not in w.donor
 assert i==w.role_ops[s][0] and w.ops[i][0]==s and w.ops[i][2]==n
 assert i in w.phase1
 e=kpair[n];line=w.w['source_frame'][n];mix=e['mix_frame']
 assert e['carrier']==r['partner'] and e['passive']==n
 physical=[s]+([recipient[s]] if s in recipient else [])
 events=[]
 for j,role in enumerate(physical):
  if j:
   alias_count+=1
   assert w.gauge[role]['role']==role and w.phys[role]==s
   assert w.last[s]<w.readtime[role]
   events.append((('alias_gauge',role),w.gauge[role]['frame']))
  for op in w.role_ops[role]:events.append((('op',op),w.opframe[op]))
  for root,f in roots[role]:events.append((('root',root),f))
 events.append((('full',s),full))
 old=histogram(None,events)
 revised=[];inserted=False
 for tag,f in events:
  if tag==('op',i):continue
  if tag==('op',early):revised.append((('early_source_mix',s),mix));inserted=True
  revised.append((tag,f))
 assert inserted
 # The early partner mix reads the original passive value before any write.
 for tag,f in revised:
  if tag==('early_source_mix',s):break
  if tag[0]=='op':assert w.phys[w.ops[tag[1]][0]]!=s,('borrowed source written before early mix',s,tag)
 assert C.sub(w.w['source_frame'][e['carrier']],mix)
 new=histogram(line,revised)
 old_passive=histogram(e['passive_chain'][0],[(('old_source',k),f) for k,f in enumerate(e['passive_chain'][1:])])
 assert old_passive==Counter({1:1,22:1})
 got=Counter(new)
 got.subtract(old);got.subtract(old_passive)
 assert sum(rank*count for rank,count in got.items())==-w.h
 # The complementary reverse chain has the same positive jump multiset;
 # dim(I−P)=h−dim(P) and reverse order preserves these differences exactly.
 dims=[C.dimf[line]]+[C.dimf[f] for tag,f in revised]
 reflected=[w.h-d for d in reversed(dims)]
 reflected_hist=Counter(b-a for a,b in zip(reflected,reflected[1:]) if b>a)
 assert reflected_hist==new
 delta.update(got)
 results.append(dict(role=s,source=n,aliased_recipient=recipient.get(s),
    original_source_endpoint_frame=line,omitted_copy=i,early_mix=early,
    old_aux_histogram=dict(sorted(old.items())),new_source_histogram=dict(sorted(new.items())),
    local_histogram_delta={rank:count for rank,count in sorted(got.items()) if count},
    reflected_histogram_equal=True))
assert len(results)==440 and alias_count==67
out=dict(scope='INDEPENDENT EXACT SOURCE ENDPOINT AND FRAME-PATH AUDIT; SCALAR ADMISSION OWNED BY SEPARATE EXECUTOR',
 sources_borrowed=len(results),borrowed_physical_donor_alias_chains=alias_count,
 all_source_start_frames_preserved=True,all_source_end_frames_full=True,
 every_spliced_frame_inclusion_checked=True,all_reflected_path_histograms_equal=True,
 local_histogram_delta={rank:count for rank,count in sorted(delta.items()) if count},
 shared_histogram_delta={rank:3*count for rank,count in sorted(delta.items()) if count},
 local_rank_mass_delta=sum(rank*count for rank,count in delta.items()),
 shared_rank_mass_delta=3*sum(rank*count for rank,count in delta.items()),
 physical_role_stock_delta=-len(results),shared_m=3*w.h,
 deficit_change=-(3*w.h)*len(results)-3*sum(rank*count for rank,count in delta.items()),
 results=results)
assert out['deficit_change']==0
(HERE/'boundary.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2))
