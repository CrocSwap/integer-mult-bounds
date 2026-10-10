"""PR200 hybrid: actual bank incidence, terminal structure and scalar bill only.
Not a replacement for full physical/column/prime replay.
"""
from pathlib import Path
from collections import Counter,defaultdict
import gzip,hashlib,importlib.util,json,sys,time,resource
assert __debug__;sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;S=None;pins={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 pins[str(p)]=sha(p);b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def run(bit_root,fresh):
 global S
 S=Path(bit_root)/'research/paired-cube-diagonal-bit-168'
 start=time.monotonic();w=read(S/'selected/bit/word_p12.json.gz');g=read(S/'selected/bit/graph_p12.json');k=read(S/'selected/bit/kchron_p12.json');pre=read(S/'selected/bit/profile_p12.json')
 c=dict(head='a1175449f34d39ff933d9d8ab23ced1f32b290ec',bit_profile=fresh['profile'],terminal=dict(selected=fresh['terminal_selected']))
 H=Counter({int(r):3*n for r,n in fresh['profile']['child_histogram'].items()});assert H.pop(60)==6600
 profile=dict(m=72,W=56402,N=5808,L=0,child_multiplicities=dict(sorted(H.items())),total_rank=sum(r*n for r,n in H.items()),maxchild=max(H));assert profile['total_rank']==4055136
 price=dict(profile=profile,conditional_selector_calls_if_186_chart_bound=5701209426)
 chart=check_charts(w,read(S/'selected/bit/frames_p12.json.gz')['frames'],bit_root)
 R=pre['R'];v=g['v'];h=g['h'];ops=w['ops'];M=len(ops);gauges={z['role']:z for z in w['gauges']};donors={a for a,b in w['pairs']};recipients={b for a,b in w['pairs']};sinks={e['role'] for e in c['terminal']['selected']};source={int(n):s for n,s in w['sources'].items()}
 assert (R,v,h,M)==(18908,1760,24,41288);physical=sorted(set(range(R))-recipients-sinks);ren={s:i for i,s in enumerate(physical)};smallroles=sorted(set(gauges)-recipients);large=sorted(set(physical)-set(smallroles));assert (len(physical),len(smallroles),len(large))==(17114,2200,14914)
 packpath=HERE/'packing_core.py';pins[str(packpath)]=sha(packpath);sp=importlib.util.spec_from_file_location('p200',packpath);pack=importlib.util.module_from_spec(sp);sp.loader.exec_module(pack)
 fam={4:smallroles,24:large};counts=Counter();left=[];right=[];offsets=[];bank=0
 for pattern,n in (({4:6,24:2},3300),({24:3},42542)):
  for _ in range(n):
   off=0
   for rank,mult in sorted(pattern.items()):
    for _ in range(mult):
     s=fam[rank][counts[rank]//9];left.append(ren[s]);right.append(bank);offsets.append(off);counts[rank]+=1;off+=rank
   assert off==72;bank+=1
 assert bank==45842 and len(left)==154026
 colors,stats=pack.color_incidence(left,right,len(physical),bank,9);pack.check_coloring(left,right,colors,len(physical),bank,9,full_left=True)
 first={};rejected=False
 for e,s in enumerate(left):
  if s not in first:first[s]=e;continue
  old=colors[e];colors[e]=colors[first[s]]
  try:pack.check_coloring(left,right,colors,len(physical),bank,9,full_left=True)
  except AssertionError:rejected=True
  finally:colors[e]=old
  break
 assert rejected
 digest=hashlib.sha256()
 for row in zip(left,right,colors,offsets):digest.update((','.join(map(str,row))+'\n').encode())
 # Independently rebuild the ORIGINAL F2 transpose, including all deleted roots.
 resp=[0]*R;pruned=[0]*R;adjmajor=[0]*R
 for j,(r,s) in enumerate(zip(g['roots'],w['rootroles'])):
  mask=sum(1<<t for t in r['targets']);assert mask.bit_count()==len(r['targets']);resp[s]^=mask;adjmajor[s]+=len(r['targets'])
  if s not in sinks:pruned[s]^=mask
 for a,b,_ in reversed(ops):resp[b]^=resp[a];pruned[b]^=pruned[a];adjmajor[b]+=adjmajor[a]
 # Cheap, actual chronology/structural admission of all 34 selected terminal roles.
 writes=defaultdict(list);uses=defaultdict(list);rootids=defaultdict(list)
 for i,(a,b,_) in enumerate(ops):writes[a].append(i);uses[b].append(i)
 for j,s in enumerate(w['rootroles']):rootids[s].append(j)
 phase=set(w['phase1']);rest=[i for i in range(M) if i not in phase];pos={i:j for j,i in enumerate(rest)};readtime={s:int(w['reads'].get(str(s),len(phase)))-len(phase) for s in gauges};first=[len(rest)+1]*v
 for s,z in gauges.items():
  assert readtime[s]>=0
  for t in z['targets']:first[t]=min(first[t],readtime[s])
 ts=set();bywrite={};preshears=0;removedroot=0
 for e in c['terminal']['selected']:
  j,s,pivot=e['root'],e['role'],e['pivot'];r=g['roots'][j];assert w['rootroles'][j]==s and r['kind']=='side' and r['targets']==e['targets'];assert not ts&set(r['targets']);ts.update(r['targets']);assert pivot in r['targets']
  assert s not in set(source.values())|set(gauges)|donors|recipients;assert rootids[s]==[j] and not uses[s];assert writes[s]==e['writes'] and writes[s];assert not phase&set(writes[s]);assert first[pivot]>max(pos[i] for i in writes[s]);assert w['root_frame'][j]==e['root_frame'];assert e['root_rank']==21
  for i in writes[s]:assert i not in bywrite;bywrite[i]=e
  preshears+=len(r['targets'])-1;removedroot+=len(r['targets'])
 assert len(bywrite)==90 and preshears==102 and removedroot==136
 response_before=sum(x.bit_count() for x in resp);response_after=sum(x.bit_count() for s,x in enumerate(resp) if s not in sinks);assert response_before-response_after==136
 roots_before=sum(len(r['targets']) for r in g['roots']);roots_after=roots_before-removedroot;mix=len(k['entries']);deliver=sum(len(e['receivers']) for e in k['entries'])
 baseline=2*M+2*len(source)+response_before+roots_before+2*mix+deliver
 parts=dict(retained_auxiliary_forward_xors=M-len(bywrite),redirected_target_write_xors=len(bywrite),retained_auxiliary_inverse_xors=M-len(bywrite),source_inject_and_uninject_xors=2*len(source),original_retained_old_value_response_xors=response_after,retained_root_read_xors=roots_after,target_pre_and_post_xors=2*preshears,partner_mix_and_unmix_xors=2*mix,partner_delivery_xors=deliver)
 total=sum(parts.values());assert total==baseline-158
 changed=sum(resp[s]!=pruned[s] for s in range(R) if s not in sinks);assert changed>0
 # Original baseline expanded-readout reserve; no physical-only discount.
 updates=M+len(source);guard=4*(updates+v)+10*v+4*h*v+4*h*h+8*h+8+2*h+8*R*v*(updates+16)+32*v
 assert total<baseline<guard and max(adjmajor).bit_length()<=updates+1
 oldguard=17663702937368;assert guard<oldguard
 selector=18*((price['profile']['W']-1)+len(physical)*72*(186+71));assert selector==price['conditional_selector_calls_if_186_chart_bound']==5701209426
 return dict(status='PASS fresh-profile incidence, exact charts, terminal windows and complete scalar counting',source_head=c['head'],profile=price['profile'],physical_chains=len(physical),rank4_chains=len(smallroles),rank24_chains=len(large),banks=bank,incidences=len(left),colors=9,color_stats=stats,incidence_sha256=digest.hexdigest(),duplicate_color_control_rejected=True,fresh_charts=chart,terminal_structural_conditions_checked=34,terminal_geometry_and_target_chronology='Bound to the separately admitted fresh bit replay',scalar=dict(parts=parts,total_literal_xors_per_core=total,baseline_literal_xors_per_core=baseline,terminal_delta=total-baseline,all_nine_invocations_literal_xors=9*total,retained_original_response=True,retained_roles_corrupted_by_pruning_response=changed,logical_scalar_reserve=R,baseline_forward_unit_updates=updates,expanded_readout_bits=updates+16,baseline_guard_per_core=guard,nine_invocation_guard=9*guard,conservative_existing_v4_guard_per_core=oldguard,nine_invocation_existing_v4_guard=9*oldguard,selector_calls_separate=selector,maximum_original_adjoint_row_l1=max(adjmajor)),limitations=['Incidence coloring is literal and checked, but bank endpoint remains conditional on geometric completed-core residual separation','No supplier mutation, new physical frames or stock transplantation'],inputs_sha256=pins,seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024 if sys.platform=='darwin' else 1))


def check_charts(w,frames,bit_root):
 from fractions import Fraction as Q
 from math import gcd
 import packing_core as pc
 p=Path(bit_root)/'research/paired-cube-diagonal-bit-168/references/pr168-v4/research/paired-cube-bit/check_paired_cube_bit.py'
 sp=importlib.util.spec_from_file_location('chart_backend',p);backend=importlib.util.module_from_spec(sp);sp.loader.exec_module(backend)
 recipients={b for a,b in w['pairs']};gauges={z['role']:z for z in w['gauges']};inv=Counter(gauges[s]['frame'] for s in set(gauges)-recipients);assert len(inv)==220
 maximum=0;maxnum=0;maxden=0;dig=hashlib.sha256()
 for f,count in sorted(inv.items()):
  A=frames[str(f)]['a'];B,_=backend.kernel(A,24);assert len(A)==4 and len(B)==20
  R=[]
  for a in A:
   row=[15*x-sum(a) for x in a];d=gcd(*row);R.append([x//d for x in row])
  assert all(9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)==0 for a in R for b in B)
  E=list(map(list,zip(*(R+B))));I,d,ops=pc.inverse_integer(E)
  for X,Y in ((E,I),(I,E)):assert all(sum(x*y for x,y in zip(row,col))==d*int(i==j) for i,row in enumerate(X) for j,col in enumerate(zip(*Y)))
  replay=[list(map(Q,row)) for row in E]
  for op,i,j,num,den in ops:
   if op=='swap':replay[i],replay[j]=replay[j],replay[i]
   elif op=='scale':replay[i]=[Q(num,den)*x for x in replay[i]]
   else:assert op=='add';replay[i]=[x+Q(num,den)*y for x,y in zip(replay[i],replay[j])]
  assert all(x==int(i==j) for i,row in enumerate(replay) for j,x in enumerate(row))
  maximum=max(maximum,len(ops));maxnum=max(maxnum,max(abs(op[3]) for op in ops));maxden=max(maxden,d,max(op[4] for op in ops));dig.update(json.dumps([f,count,E,I,d,ops],separators=(',',':')).encode())
 assert maximum==186 and maxnum==5 and maxden==18 and max(maxnum,maxden)<2**80
 return dict(charts=220,max_chart_factors=maximum,max_num=maxnum,max_den=maxden,chart_sha256=dig.hexdigest(),fresh_exact_chart_replay=True)
