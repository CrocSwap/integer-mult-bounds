# Copyright 2026 icekylinx. Apache-2.0.
# Integration with OpenAI Codex assistance; see NOTICE.
"""Unrestricted source gauges and reverse target chains.
Adapted from partial_gauge.select; copyright 2026 icekylinx, Apache-2.0.
"""
from pathlib import Path
from collections import Counter
from itertools import combinations
import json
from partial_gauge.binary import load
from partial_gauge.lift import basis

def run(path,annfile,liftfile,wordfile):
 h,v,n,q,args,core,cover,roots,kind,active,oldrank,types=load(path)
 ann=json.loads(Path(annfile).read_text());d=json.loads(Path(liftfile).read_text())
 word=json.loads(Path(wordfile).read_text());ops=word['ops'];sources=set(word['sources'].values())
 R=d['R'];full=(1<<h)-1;first=[None]*R
 for a,b,x in ops:
  if first[a] is None:first[a]=x
  if first[b] is None:first[b]=x
 touched=set(sources)
 for i in word['phase1']:touched.update(ops[i][:2])
 triples=list(combinations(range(h),3));tid={sum(1<<j for j in t):i for i,t in enumerate(triples)}
 co=[0]*R
 for j,(x,s,k) in enumerate(zip(roots,word['rootroles'],kind)):
  co[s]|=((1<<v)-1) if k else 1<<tid[core[x]|(full^cover[x])]
 for a,b,x in reversed(ops):co[b]|=co[a]
 candidates=[s for s in range(R) if first[s] is not None and s not in touched]
 candidates.sort(key=lambda s:(len(ann[first[s]]),co[s].bit_count(),s))
 # None represents the full active ambient frame, whose annihilator is0.
 latest=[None]*v;target_ranks=[[] for _ in range(v)];selected=[];birth=Counter();residual=Counter();H=Counter(dict(enumerate(d['histogram'])))
 cache={};repaired=0
 for s in candidates:
  A=tuple(ann[first[s]]);r=h-len(A);rows=list(A);outs=[];bits=co[s]
  while bits:
   low=bits&-bits;t=low.bit_length()-1;bits^=low;outs.append(t)
   if latest[t] is not None:rows.extend(latest[t])
  capann=basis(rows)
  if capann not in cache:cache[capann]=capann
  sigma=cache[capann];a=h-len(sigma)
  if not a:continue
  assert a<=r
  H[r]-=1;H[r-a]+=1;birth[a]+=1;residual[r-a]+=1
  selected.append(dict(role=s,first_rank=r,gauge_rank=a,annihilator=sigma))
  for t in outs:
   latest[t]=sigma
   if not target_ranks[t] or target_ranks[t][-1]!=a:target_ranks[t].append(a)
 assert min(H.values())>=0
 Y=Counter()
 for ranks in target_ranks:
  prev=0
  for r in list(reversed(ranks))+[h-1]:assert r>=prev;Y[r-prev]+=1;prev=r
 result={k:d[k] for k in ['h','v','R','q','c','matched','loss']}
 result.update(selected_roles=len(selected),selected_rank_histogram=dict(birth),
  remaining_internal_histogram=[H[r] for r in range(h+1)],
  source_data_histogram={h-1:v},target_data_histogram=dict(Y),
  copied_centers_already=True,phase1_operations=len(word['phase1']),
  total_M_operations=len(ops),untouched_non_source_roles=len(candidates),
  selection='Full unrestricted intersections and source gauges; descending first-frame rank, then reached-target count, then role index; general_clifford_subspace_frames.txt proves all required ranks',
  partial_first_transition_histogram=dict(residual),distinct_caps=len(cache),
  repaired_caps=repaired,
  scalar_readout='Exact rational C=J M; Boolean support is a safe superset only',
  chronological_contract='Nondeferred reads at0; source V; center-closed M phase1; copied centers at0; selected partial-gauge reads in reverse selection order; remaining M; side scatter; inverse M/V atfull F')
 return result,dict(base_word=Path(wordfile).name,selected=selected)
