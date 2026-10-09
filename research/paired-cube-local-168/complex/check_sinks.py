#!/usr/bin/env python3
"""Author exact finite check for target-accumulating disjoint-root deletion.

Portability-only adaptation by Chafik Boukhalfa with OpenAI Codex assistance.
Original PR166 author James Chang. Uses frozen selected complex data; never imports upstream programs,
regenerates a source graph, searches a new producer, or computes a new kappa.
Python standard library. Copyright 2026; Apache-2.0.
"""
import argparse,gzip,hashlib,json,resource,signal,sys,time
from collections import Counter
from fractions import Fraction
from pathlib import Path


def main():
 if sys.flags.optimize:raise SystemExit('Run without -O')
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--candidate',type=Path,required=True)
 ap.add_argument('--output',type=Path,required=True)
 a=ap.parse_args();start_time=time.monotonic()
 resource.setrlimit(resource.RLIMIT_CPU,(60,60));signal.alarm(60)
 pins=json.loads((a.candidate/'result.json').read_text())['pins'];data={}
 for name in ['graph','word','frames','physical-frames','physical-pairs','profile-before','profile']:
  name+='.json.gz';b=(a.candidate/name).read_bytes();assert hashlib.sha256(b).hexdigest()==pins[name]
  data[name[:-8]]=json.loads(gzip.decompress(b))
 g,w,fw,changes,pairs,row,profile=[data[n] for n in ['graph','word','frames','physical-frames','physical-pairs','profile-before','profile']]
 H,V,R=g['h'],g['v'],row['R'];assert (H,V)==(22,1320)
 def basis(rows):
  b={}
  for x in rows:
   for p,y in sorted(b.items(),reverse=True):
    if x>>p&1:x^=y
   if x:
    p=x.bit_length()-1
    for k,y in list(b.items()):
     if y>>p&1:b[k]=y^x
    b[p]=x
  return tuple(b[k] for k in sorted(b,reverse=True))
 def perp(rows):
  rows=basis(rows);p={r.bit_length()-1:r for r in rows};out=[]
  for j in range(H):
   if j in p:continue
   x=1<<j
   for k,r in p.items():
    if r>>j&1:x|=1<<k
   out.append(x)
  return basis(out)
 def within(A,B):return len(basis(tuple(A)+tuple(B)))==len(B)
 def fmt(c):return {str(k):v for k,v in sorted(c.items()) if v}
 FULL=basis(1<<i for i in range(H));sources={int(k):v for k,v in w['sources'].items()}
 aliases={b:a for a,b,t in pairs};donors={a:b for a,b,t in pairs};deadline={b:t for a,b,t in pairs};alias=lambda s:aliases.get(s,s)
 live=set(range(R))-set(aliases);assert len(live)==profile['physical_R']
 phase=set(w['phase1']);chron=w['phase1']+[i for i in range(len(w['ops'])) if i not in phase];when={i:j for j,i in enumerate(chron)}
 ofs=[perp(fw['annihilators'][n]) for aa,bb,n in w['ops']]
 for i,F in changes:assert basis(F)==tuple(F);ofs[i]=tuple(F)
 roleops=[[] for _ in range(R)];roots_of=[[] for _ in range(R)]
 for i,(aa,bb,n) in enumerate(w['ops']):
  assert alias(aa)!=alias(bb);roleops[aa].append(i);roleops[bb].append(i)
 for j,s in enumerate(w['rootroles']):roots_of[s].append(j)
 spans=[()]*len(g['args'])
 for n,args in enumerate(g['args']):spans[n]=(g['inputs'][n],) if args is None else basis(spans[args[0]]+spans[args[1]])
 rootframes=[spans[r['node']] if r['kind']=='center' else perp(g['inputs'][t] for t in r['targets']) for r in g['roots']]
 selected={z['role']:z for z in w['selected']};first_read=[len(chron)+1]*V
 for z in selected.values():
  t=deadline.get(z['role']);position=len(phase) if t is None else when[t]
  for y in z['targets']:first_read[y]=min(first_read[y],position)
 # Recount the complete old physical row paths and compare every positive bin.
 starts=[()]*R
 for n,s in sources.items():starts[s]=(g['inputs'][n-1],)
 for s,z in selected.items():starts[s]=perp(z['annihilator'])
 rframe={s:rootframes[j] for j,s in enumerate(w['rootroles'])};rkind={s:g['roots'][j]['kind'] for j,s in enumerate(w['rootroles'])}
 def chain(s):return [starts[s]]+[ofs[i] for i in roleops[s]]+([rframe[s]] if s in rframe else [])+[FULL]
 local=Counter()
 for s in live:
  seq=chain(s)
  if s in donors:seq=seq[:-1]+chain(donors[s])
  assert all(within(A,B) for A,B in zip(seq,seq[1:]))
  local.update(len(B)-len(A) for A,B in zip(seq,seq[1:]) if len(B)>len(A))
  if s in sources.values():local[1]+=1
  for t in (s,donors.get(s)):
   if t is not None and rkind.get(t)=='center':local[len(rframe[t])]+=1
 assert fmt(local)==profile['local_histogram']
 source=Counter({int(k):v for k,v in profile['source_data_histogram'].items()});target=Counter({int(k):v for k,v in profile['target_data_histogram'].items()})
 def children(L,T):
  c=Counter({r:3*n for r,n in L.items() if r});c.update({r:3*n for r,n in T.items() if r});c.update({r:3*n for r,n in source.items() if r});c[2]+=2*V
  for s,z in selected.items():
   if s not in aliases:c[3*z['rank']]+=1
  return c
 oldchildren=children(local,target);assert fmt(oldchildren)==profile['child_histogram']
 rejected=Counter();eligible=[]
 for j,r in enumerate(g['roots']):
  if r.get('channel')!='disjoint':continue
  s=w['rootroles'][j];writes=[i for i in roleops[s] if w['ops'][i][0]==s];uses=[i for i in roleops[s] if w['ops'][i][1]==s];why=[];U=rootframes[j]
  if s in aliases or s in donors:why.append('alias_or_donor')
  if s in sources.values():why.append('source_injection')
  if s in selected:why.append('selected_gauge')
  if roots_of[s]!=[j]:why.append('multiple_roots')
  if uses:why.append('retained_producer_consumer')
  if not writes:why.append('no_writes')
  if any(w['opcoeff'][i][0]!=1 for i in writes):why.append('nonadditive_destination')
  if any(not within(ofs[i],U) for i in writes):why.append('outside_read_frame')
  if any(i in phase for i in writes):why.append('center_phase_touch')
  available_pivots=[t for t in r['targets'] if writes and first_read[t]>max(when[i] for i in writes)]
  if not available_pivots:why.append('no_uncorrected_pivot')
  if why:rejected.update(why);continue
  assert len(r['targets'])==8 and len(U)==18 and r['coefficients']==['1/2']*8
  # The sink's whole original trajectory is copied by only one target pivot.
  # Every other target stays at0 until the common rank18 post-read.
  path=[()]+[ofs[i] for i in writes]+[U];assert all(within(A,B) for A,B in zip(path,path[1:]))
  prefix=[len(B)-len(A) for A,B in zip(path,path[1:]) if len(B)>len(A)]
  assert sum(prefix)==18
  eligible.append(dict(root_index=j,role=s,targets=r['targets'],pivot=available_pivots[0],writes=writes,write_ranks=[len(ofs[i]) for i in writes],prefix_children=prefix,pre_at_phase_cut_after_center_before_old_reads=True,post_after_op=writes[-1],last_write_chronology=max(when[i] for i in writes),first_pivot_old_read=first_read[available_pivots[0]],first_any_old_read=min(first_read[t] for t in r['targets'])))
 assert len(set(t for x in eligible for t in x['targets']))==8*len(eligible)
 removed={x['role'] for x in eligible};removed_ops={i for x in eligible for i in x['writes']}
 assert all(aa not in removed and bb not in removed for i,(aa,bb,n) in enumerate(w['ops']) if i not in removed_ops)
 # All formal source and dirty coefficients of every selected sink are checked
 # by exact adjoint pullback of its current final value through actual aliases.
 # Remaining source/dirty identity follows from literal inverse cancellation
 # of the unchanged retained word; no sampler or packed-digit hypothesis.
 def final_form(s,stop):
  c={s:1}
  for i in reversed(chron[:stop+1]):
   aa,bb,n=w['ops'][i];aa,bb=alias(aa),alias(bb);ca,cb=w['opcoeff'][i];v=c.get(aa,0)
   if v:
    c[aa]=ca*v;c[bb]=c.get(bb,0)+cb*v
    if not c[bb]:del c[bb]
  fresh={n-1:c[alias(s)] for n,s in sources.items() if c.get(alias(s),0)}
  return c,fresh
 dirtyterms=[]
 for item in eligible:
  s=item['role'];c,fresh=final_form(s,item['last_write_chronology']);assert c[s]==1
  assert not (set(c)&(removed-{s}))
  cube={x//2 for x in g['labels'][item['targets'][0]]}
  expected={n:1 for n,t in enumerate(g['labels']) if cube.isdisjoint(x//2 for x in t)}
  assert fresh==expected and len(fresh)==448;dirtyterms.append(len(c)-1)
  # Exact independent-target/sink/accumulation-symbol sandwich, both signs.
  # Algebra includes arbitrary previous target corrections in y[t].
  for direction in (1,-1):
   N=16+len(item['writes']);ys=[[Fraction(int(i==t)) for i in range(N)] for t in range(8)]
   for t in range(1,8):ys[t]=[a-b for a,b in zip(ys[t],ys[0])]
   # Arbitrary intervening non-pivot corrections are explicit independent
   # columns. The chosen pivot has none until after its post-read.
   for t in range(1,8):ys[t][8+len(item['writes'])+t]+=1
   for k,i in enumerate(item['writes']):ys[0][8+k]+=direction*Fraction(w['opcoeff'][i][1],2)
   for t in range(1,8):ys[t]=[a+b for a,b in zip(ys[t],ys[0])]
   for t in range(8):
    expected=[Fraction(int(i==t)) if i<8 else direction*Fraction(w['opcoeff'][item['writes'][i-8]][1],2) if i<8+len(item['writes']) else Fraction(int(t>0 and i==8+len(item['writes'])+t)) for i in range(N)]
    assert ys[t]==expected
 # Whole simultaneous local and shared three-core ledger.
 L=local.copy();T=target.copy()
 for item in eligible:
  L.subtract(Counter(item['prefix_children']+[4]));T[18]-=1;T.update(item['prefix_children'])
 assert all(v>=0 for v in L.values()) and all(v>=0 for v in T.values())
 # Replay every target event in the actual deadline order, interleaving the
 # new pivot writes and post-reads. Pre-shears are at the common zero frame
 # just after the center phase and before its first compensation read.
 by_write={i:item for item in eligible for i in item['writes']}
 after={item['writes'][-1]:item for item in eligible}
 read_at={}
 for z in reversed(w['selected']):
  d=deadline.get(z['role']);position=len(phase) if d is None else when[d]
  read_at.setdefault(position,[]).append(z)
 current=[() for _ in range(V)];actual_target=Counter();target_events=[]
 def move_target(t,U,kind,index):
  U=tuple(U);assert within(current[t],U),(kind,index,t,current[t],U)
  actual_target[len(U)-len(current[t])]+=1
  target_events.append([kind,index,t,list(current[t]),list(U)])
  current[t]=U
 for position,i in enumerate(chron):
  for z in read_at.get(position,[]):
   U=perp(z['annihilator'])
   for t in z['targets']:move_target(t,U,'old-read',z['role'])
  if i in by_write:
   item=by_write[i];move_target(item['pivot'],ofs[i],'pivot-write',i)
  if i in after:
   item=after[i];U=rootframes[item['root_index']]
   for t in item['targets']:move_target(t,U,'post-read',i)
   assert all(current[t]==current[item['pivot']]==U for t in item['targets'])
 for j,r in enumerate(g['roots']):
  if r['kind']=='side' and w['rootroles'][j] not in removed:
   for t in r['targets']:move_target(t,rootframes[j],'retained-root',j)
 for t,q in enumerate(g['inputs']):move_target(t,perp((q,)),'target-finish',t)
 assert fmt(Counter({r:n for r,n in actual_target.items() if r}))==fmt(Counter({r:n for r,n in T.items() if r}))
 # Independent reverse of each scalar sandwich, including arbitrary inserted
 # non-pivot corrections, yields the inverse rather than assuming a sign rule.
 for item in eligible:
  N=16+len(item['writes']);initial=[[Fraction(int(i==t)) for i in range(N)] for t in range(8)]
  state=[r[:] for r in initial];events=[]
  for t in range(1,8):events.append(('shear',t,0,Fraction(-1)))
  for k,i in enumerate(item['writes']):events.append(('basis',0,8+k,Fraction(w['opcoeff'][i][1],2)))
  for t in range(1,8):events.append(('basis',t,8+len(item['writes'])+t,Fraction(1)))
  for t in range(1,8):events.append(('shear',t,0,Fraction(1)))
  def apply(e,sign):
   kind,t,s,c=e;c*=sign
   if kind=='basis':state[t][s]+=c
   else:state[t]=[a+c*b for a,b in zip(state[t],state[s])]
  for e in events:apply(e,1)
  for e in reversed(events):apply(e,-1)
  assert state==initial
 C=children(L,T);n=len(eligible);delta={str(k):C[k]-oldchildren[k] for k in C.keys()|oldchildren.keys() if C[k]!=oldchildren[k]}
 assert delta==({'4':-3*n,'18':-3*n} if n else {});W=profile['W_per_vertex']-n;rank=sum(k*v for k,v in C.items());assert rank==profile['rank_per_vertex']-66*n and 66*W-rank==1320
 result=dict(status='AUTHOR_EXACT_FINITE_COMPILER_CHECK_PASS',scope='Only all-eight disjoint roots; retained full proof contracts unchanged',input_pins={k:pins[k] for k in pins if k in [n+'.json.gz' for n in data]},h=H,v=V,old_physical_R=len(live),new_physical_R=len(live)-n,old_W=profile['W_per_vertex'],new_W=W,old_rank=profile['rank_per_vertex'],new_rank=rank,deficit=1320,eligible_count=n,rejected_conditions=dict(rejected),targets_disjoint=True,simultaneous_compatible=True,all_formal_source_and_dirty_coefficients=True,formal_original_source_dirty_target_columns=2*V+len(live),remaining_formal_columns=2*V+len(live)-n,chronological_inverse_by_literal_reverse=True,full_old_physical_histogram_verified=True,all_new_target_events_replayed=True,scalar_sandwich_literal_reverse_checked=True,shared_child_delta=delta,scalar_gate_delta=-sum(len(x['writes'])+2 for x in eligible),new_odd_denominator=False,new_kappa_claimed=False,local_histogram=fmt(L),target_histogram=fmt(T),child_histogram=fmt(C),sinks=eligible,dirty_coefficient_nonzero_range=[min(dirtyterms),max(dirtyterms)],seconds=time.monotonic()-start_time,rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
 a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['sinks','local_histogram','target_histogram','child_histogram','input_pins']},indent=2))
if __name__=='__main__':main()
