"""OpenAI Codex independent serialized ASYNCHRONOUS controller/spectator audit.
Imports no emitter, optimizer, expander, edge-coloring, or source hosting code.
CLI: BASE HOSTED REPORT [--mutation-controls]
Each provider is independently read from BASE/providers, never from a baseline width histogram.
OpenAI Codex two-provider width-seven extension; retains all inherited independent controller checks.
The exact 63 width-seven and 9 plain calls are frozen below.
"""
import sys,json,gzip,hashlib,copy
assert __debug__, 'Assertions must remain enabled'
from pathlib import Path
from collections import Counter,defaultdict
import sys as _s,pathlib as _p;_s.path.insert(0,str(_p.Path(__file__).resolve().parent))
from witness import *
from generated_identity import artifact_identities
BASE,OUT,REPORT=map(lambda p:Path(p).resolve(),sys.argv[1:4]);read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
parent=read(BASE/'split-centres/GLOBAL-TEMPLATE.json.gz')
ph=read(BASE/'work/complex-nine-native/DATA-PHASES.json')
ct=read(OUT/'GLOBAL-TEMPLATE.json.gz');summary=read(OUT/'HOSTED.json')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
provider_ids=PIDS
providers={};registry={};phase_semantic_hashes={};artifact_semantic_hashes={}
required_artifacts={'work/complex-nine-native/DATA-PHASES.json'}
provider_files=('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json',
 'INDEPENDENT-LOCAL-REPLAY.json','RESIDUAL-ADAPTERS.json','CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json')
for pid in provider_ids:
 p=BASE/'providers'/pid
 c=read(p/'CANONICAL-WORD.json.gz');checks=read(p/'LOCAL-CHECKS.json')
 programs=read(p/'LOCAL-PROGRAMS.json.gz');replay=read(p/'INDEPENDENT-LOCAL-REPLAY.json')
 phase=read(p/'CLIFFORD-REVIEW.json');adapters=read(p/'RESIDUAL-ADAPTERS.json')['recipes']
 widths=[len(c['frames'][c['final'][2*c['v']+h]])-len(c['frames'][c['start'][2*c['v']+h]])for h in range(c['R'])]   # HPE: residual width |final|-|start|
 assert tuple(widths[h]for h in SPOT)==spot_widths();pin('providers.%s.inventory'%pid,{str(k):v for k,v in sorted(Counter(widths).items())})
 canonical_sha=sha(p/'CANONICAL-WORD.json.gz');programs_sha=sha(p/'LOCAL-PROGRAMS.json.gz')
 assert replay['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
 assert replay['canonical_word_sha256']==canonical_sha and replay['local_programs_sha256']==programs_sha
 assert replay['v']==c['v'] and replay['helpers']==c['R']
 assert set(programs)==set(checks)==set(replay['local'])==set(replay['paid_profiles'])=={'forward','backward'}
 for orientation,events in programs.items():
  ck=checks[orientation];rr=replay['local'][orientation]
  assert hashlib.sha256(json.dumps(events,sort_keys=True,separators=(',',':')).encode()).hexdigest()==ck['sha256']
  assert ck['events']==len(events) and ck['all_columns']==2*c['v']+c['R']
  assert ck['private_centers_cleared'] and ck['private_coefficient_stream_cleared_after_each_macro']
  assert rr['all_exact_columns']==2*c['v']+c['R'] and rr['private_work_erased']
  literal=Counter(e[-1]for e in events if e[0]in('climb','center'))
  assert dict(literal)=={int(r):n for r,n in ck['paid_profile'].items()}=={int(r):n for r,n in c['local_profile'].items()}
  assert ck['paid_profile']==replay['paid_profiles'][orientation]
 assert phase['canonical_word_sha256']==canonical_sha and phase['recipe_sha256']==sha(p/'CLIFFORD-RECIPES.json')
 assert phase['all_child_equalities_include_global_phase']
 artifact_semantic_hashes[pid]=artifact_identities(p)
 pin('providers.%s.artifact_semantic_sha256'%pid,artifact_semantic_hashes[pid])
 phase_semantic_hashes[pid]=artifact_semantic_hashes[pid]['CLIFFORD-REVIEW.json']
 for h,w in enumerate(widths):
  assert 0<w<=c['h']
  f=c['start'][2*c['v']+h];u=c['final'][2*c['v']+h]
  # COLD-HPE: a cold helper (f == 0) may end below FULL too; its wrapper is the '0:U' recipe (E = bottom instance of #593)
  if u!=1:   # HPE: wrapper for T_U T_E^-1, keyed 'E:U', rank |U|-|E|
   a=adapters['%d:%d'%(f,u)]
   assert a['frame']==f and a['terminal']==u and a['vectors']==c['frames'][f] and a['terminal_vectors']==c['frames'][u]
   assert a['rank']==w==len(c['frames'][u])-len(c['frames'][f]) and a['entrance_rank']==len(c['frames'][f]) and a['terminal_rank']==len(c['frames'][u])<c['h']
  elif w<c['h']:
   a=adapters[str(f)]
   assert a['frame']==f and a['vectors']==c['frames'][f] and a['rank']==w and a['entrance_rank']==c['h']-w
 providers[pid]=dict(canonical=c,checks=checks,widths=widths)
 registry[pid]=dict(local_programs=programs,canonical_word_sha256=canonical_sha,local_programs_sha256=programs_sha,
  local_program_checks=checks,exact_local_clifford_recipe_sha256=sha(p/'CLIFFORD-RECIPES.json'),
  residual_adapter_sha256=sha(p/'RESIDUAL-ADAPTERS.json'),
  **{k:c[k]for k in('v','h','R','ports','centers')},widths=widths)
 required_artifacts.update('providers/'+pid+'/'+fn for fn in provider_files)
canon=providers[provider_ids[0]]['canonical'];V=canon['v'];R=canon['R'];N=2*V+R;CENTRES=len(canon['centers'])
assert V==112 and canon['h']==9
assert all(providers[p]['canonical'][k]==canon[k]for p in provider_ids for k in('v','h','R','ports'))
# Independently compare ordered common frames; exact local carrier names remain
# bound to each canonical word, program, phase receipt and residual adapters.
for p in provider_ids:
 c=providers[p]['canonical']
 assert len(c['centers'])==len(c['center_frames'])==8
 assert [c['frames'][f]for f in c['center_frames']]==[canon['frames'][f]for f in canon['center_frames']]
parent_canon=read(BASE/'split-centres/CANONICAL-WORD.json.gz')
assert [canon['frames'][f]for f in canon['center_frames']]==[parent_canon['frames'][f]for f in parent_canon['center_frames']]
assert required_artifacts<=set(summary['source_artifacts'])
prank={e['child']:e['rank']for e in parent['idle_children']};M=73;T=REPLICAS;DATA=8*T*V;PHYSICAL=DATA+CENTRES+R+2;CALLS=CALLS;HOSTED=CALLS*R
# The selected map is an input to check, not a claim from the emitter.

assert len(DISPATCH)==CALLS and Counter(DISPATCH.values())==COUNTS
expected_provider=lambda stage,replica:DISPATCH[stage,replica]

def orthobasis(port):
 q=canon['ports'][port];z=next(i for i in range(9)if(q>>i)&1==0);a=q^(1<<z);order=list(range(9));order[z],order[0]=order[0],order[z]
 b=[(1<<i)^(a if a>>i&1 else 0)for i in order]+[1<<i for i in range(9,73)]
 assert len(b)==73 and all((x&y).bit_count()%2==int(i==j)for i,x in enumerate(b)for j,y in enumerate(b));return b
bases=[orthobasis(p)for p in range(V)]

def audit(t):
 assert(t['live'],t['physical'])==(DATA,PHYSICAL)
 assert t['local_providers']==registry and t['recipe']==parent['recipe']and 'each local invocation completes before the next' in t['loop_order'].lower()
 assert not any(k in t for k in('local_programs','exact_local_clifford_recipe_sha256','residual_adapter_sha256'))
 assert len(t['calls'])==CALLS and t['hosting']['max_helpers_per_physical_family_per_call']==1 and t['hosting']['banks']==[0]*9
 for key in('exact_data_phase_recipe_sha256','adapter_policy'):assert t[key]==parent[key]
 assert t['exact_data_phase_recipe_sha256']==sha(BASE/'work/complex-nine-native/DATA-PHASES.json')
 # Independently project the literal schedule onto every data replica.
 src=parent['execution_schedule'];assert t['async_schedule']['source_schedule']==src
 assert t['async_schedule']['source_call_order']==[[c['stage'],c['replica']]for c in parent['calls']]
 order=[(c['stage'],c['replica'])for c in t['calls']]
 assert [list(x)for x in order]==t['async_schedule']['order'] and len(set(order))==CALLS
 all_local=[];perrep={r:[]for r in range(REPLICAS)};globals_=[]
 for e in t['execution_schedule']:
  j=e['source_event'];old=copy.deepcopy(src[j])
  if 'replica'in e:
   r=e['replica'];assert 0<=r<REPLICAS and j<30;perrep[r].append(j)
   expected=old|dict(source_event=j,replica=r,replicas=[r],time=e['time'])
   if e['kind']=='local_cover_sweep':expected['provider_id']=expected_provider(e['stage'],r)
   assert e==expected
   assert 0<=e['time']<CALLS and order[e['time']][1]==r
   if e['kind']=='local_cover_sweep':
    assert order[e['time']]==(e['stage'],r);all_local.append((e['stage'],r,e['time']))
  else:
   globals_.append(j);expected=old|dict(source_event=j)
   if e['kind']=='bank_padding_cover_sweep':expected['families']=[DATA,DATA]
   if e['kind']=='translate_every_live_family':expected.update(families=[0,DATA],charged_calls_per_cover=DATA)
   assert e==expected
 assert all(v==list(range(30))for v in perrep.values()) and globals_==[30,31]
 assert all_local==[(st,r,i)for i,(st,r)in enumerate(order)]
 assert all('replica'in e for e in t['execution_schedule'][:-2])
 assert [e['source_event']for e in t['execution_schedule'][-2:]]==[30,31]
 # Local cover calls are indivisible; a block then runs the source events
 # up to that replica's next local invocation.
 block=-1
 for e in t['execution_schedule'][:-2]:
  if e['kind']=='local_cover_sweep':block+=1
  assert e['time']==block
 assert t['bank_padding']==dict(parent['bank_padding'],families=[],children=[])
 assert t['cover_final_correction']==dict(parent['cover_final_correction'],families=[0,DATA],charged_calls_per_cover=DATA)
 assert t['private_namespace']=={'centers':[DATA,DATA+CENTRES],'reserved_tableau':[DATA+CENTRES,DATA+CENTRES+R],'coefficient':[DATA+CENTRES+R,PHYSICAL]}
 # Actual physical touch intervals include every individual bridge.
 pairs={};sides={};windows={};last={};callpos={};stagepair={e['stage']:e['pair']for e in parent['recipe']if e['kind']=='local'}
 for pos,e in enumerate(t['execution_schedule']):
  if 'replica'not in e:continue
  rep=e['replica']
  if e['kind']=='local_cover_sweep':
   pair=stagepair[e['stage']];callpos[e['stage'],rep]=pos;last[rep,pair]=pos
  elif e['kind']=='bridge':last[rep,e['src']]=last[rep,e['dst']]=pos
  elif e['kind']=='idle_cover_sweep':
   for side,i in enumerate(e['child_indices']):
    if i not in prank:continue
    pairs[i]=e['pair'];sides[i]=side;windows[rep,i]=(last.get((rep,e['pair']),-1),pos)
 used=defaultdict(set);roles={};paid=Counter();sigmas={};digest=hashlib.sha256();entering=0;cross=0;touches=defaultdict(list)
 for call in t['calls']:
  old=next(z for z in parent['calls']if(z['stage'],z['replica'])==(call['stage'],call['replica']))
  assert {k:v for k,v in call.items()if k not in('owners','time','provider_id','local_program_sha256')}=={k:v for k,v in old.items()if k not in('owners','local_program_sha256')}
  pid=expected_provider(call['stage'],call['replica']);assert call['provider_id']==pid
  width=providers[pid]['widths'];checks=providers[pid]['checks']
  assert call['local_program_sha256']==checks[call['orientation']]['sha256']
  s,rep,pair=call['stage'],call['replica'],call['pair'];assert call['time']==t['async_schedule']['order'].index([s,rep]);own=call['owners'];assert len(own)==N and len({f for f,rt in own})==N and all(0<=f<DATA for f,rt in own)
  assert own[:(2*V)]==old['owners'][:(2*V)]
  for h,(family,route)in enumerate(own[(2*V):]):
   w=width[h];typ,i,off=route[:3];ownerrep,sub=divmod(family,(8*V));fampair,sub=divmod(sub,(2*V));side,port=divmod(sub,V)
   assert windows[ownerrep,i][0]<callpos[s,rep]<windows[ownerrep,i][1] and fampair==pairs[i] and side==sides[i] and 0<=off and off+w<=prank[i]
   B=bases[port];pend=[int(x)for x in ph['recipes'][port]['idle_children'][i]['orthogonal_axes']];assert len(pend)==prank[i]
   occ=[B.index(v)for v in pend[off:off+w]];sp=[j for j in range(M)if j not in occ][:9-w]
   assert route==([3,i,off]if w==9 else[4,i,off,w,sp]);assert len(set(occ+sp))==9
   order=occ+sp+[j for j in range(M)if j not in occ and j not in sp];assert sorted(order)==list(range(M));sigma=[B[j]for j in order]
   assert sigma[:w]==pend[off:off+w]and sigma[w:9]==[B[j]for j in sp]
   sh=hashlib.sha256(json.dumps(sigma,separators=(',',':')).encode()).hexdigest();sigmas[sh]=sigma;digest.update(json.dumps([s,rep,h,family,sh],separators=(',',':')).encode()+b'\n')
   key=(i,ownerrep,port);cells=set(range(off,off+w));assert not used[key]&cells;used[key]|=cells
   role=(s,rep,h);assert role not in roles;roles[role]=dict(stage=s,replica=rep,helper=h,family=family,owner_replica=ownerrep,child=i,copy=ownerrep*V+port,port=port,offset=off,width=w)
   touches[family].append((s,rep,h));entering+=w<9;cross+=rep!=ownerrep
  for r,n in checks[call['orientation']]['paid_profile'].items():paid[int(r)]+=n
 assert set(roles)=={(s,rep,h)for s in range(9)for rep in range(REPLICAS)for h in range(R)}
 # The frozen pooled metadata must bind the actual serialized owner maps.
 assert len(t['hosting']['pooled_slots'])==HOSTED
 for z in t['hosting']['pooled_slots']:
  key=(z['stage'],z['replica'],z['helper']);assert key in roles
  assert {k:z[k]for k in roles[key]}==roles[key]
 assert len({(z['stage'],z['replica'],z['helper'])for z in t['hosting']['pooled_slots']})==HOSTED
 rem={};wanted=[]
 for old in parent['idle_children']:
  i,port=old['child'],old['port']
  for rep in range(T):
   u=used[i,rep,port];assert u==set(range(len(u)));r=old['rank']-len(u)
   if r:
    f=rep*(8*V)+(2*pairs[i]+sides[i])*V+port;wanted.append(dict(child=i,port=port,replica=rep,replicas=1,family=f,rank=r,hosted=len(u),pending_offset=len(u)));paid[r]+=1
 assert t['idle_children']==wanted
 mass=sum(r*n for r,n in paid.items());assert73=73*DATA-mass;assert assert73==DEFICIT and 73**2>2*max(paid)**2
 return dict(profile=dict(sorted(paid.items())),mass=mass,hosted=HOSTED,entering=entering,cross_replica=cross,sigma_digest=digest.hexdigest(),sigmas=sigmas,idle_remainders=len(wanted),busy_family_checks=len(roles),invocations=CALLS)

r=audit(ct);raw=gzip.decompress((OUT/'GLOBAL-TEMPLATE.json.gz').read_bytes());assert hashlib.sha256(raw).hexdigest()==summary['template_sha256'];assert r['profile']=={int(k):v for k,v in summary['global_profile'].items()};assert r['sigmas']==read(OUT/'ACTUAL-SIGMAS.json.gz');assert r['sigma_digest']==summary['sigma_stream_sha256']
assert all(hashlib.sha256((BASE/name).read_bytes()).hexdigest()==value for name,value in summary['source_artifacts'].items())
controls=[]
def reject(name,mut):
 if '--mutation-controls' not in sys.argv[4:]:return
 q=copy.deepcopy(ct);mut(q)
 try:audit(q)
 except(AssertionError,KeyError,IndexError,ValueError,TypeError):controls.append(name)
 else:raise AssertionError('ACCEPTED '+name)
enter=lambda q:next(o for c in q['calls']for o in c['owners'][(2*V):]if o[1][0]==4)
reject('alias two whole owners',lambda q:q['calls'][0]['owners'].__setitem__((2*V+1),q['calls'][0]['owners'][(2*V)]))
reject('helper on active data family',lambda q:q['calls'][0]['owners'][(2*V)].__setitem__(0,q['calls'][0]['owners'][0][0]))
reject('owner in private namespace',lambda q:q['calls'][0]['owners'][(2*V)].__setitem__(0,DATA))
reject('wrong residual width',lambda q:enter(q)[1].__setitem__(3,enter(q)[1][3]-1))
reject('wrong spectator coordinate',lambda q:enter(q)[1][4].__setitem__(0,72))
reject('omit idle remainder',lambda q:q['idle_children'].pop())
reject('understate physical reserve',lambda q:q.__setitem__('physical',PHYSICAL-1))
# Single-provider dispatch still has all source/program/width binding controls.
if len(provider_ids)==1:
 P=provider_ids[0]
 at_p=lambda q:next(c for c in q['calls']if c['provider_id']==P)
 narrow=next(h for h in range(R)if providers[P]['widths'][h]<9)
 reject(P+': wrong provider at its invocation',lambda q:at_p(q).__setitem__('provider_id','__unregistered__'))
 reject(P+': stale per-call local program hash',lambda q:at_p(q).__setitem__('local_program_sha256','0'*64))
 reject(P+': stale serialized provider program',lambda q:q['local_providers'][P]['local_programs']['forward'].pop())
 reject(P+': unbound residual adapter hash',lambda q:q['local_providers'][P].__setitem__('residual_adapter_sha256','0'*64))
 reject(P+': wrong provider width registry',lambda q:q['local_providers'][P]['widths'].__setitem__(narrow,providers[P]['widths'][narrow]-1))
 reject(P+': wrong per-call residual width',lambda q:at_p(q)['owners'][2*V+narrow][1].__setitem__(3,at_p(q)['owners'][2*V+narrow][1][3]-1))
 reject(P+': wrong sweep provider',lambda q:next(e for e in q['execution_schedule']if e['kind']=='local_cover_sweep').__setitem__('provider_id','__unregistered__'))
 reject(P+': entering helper width silently restored to nine',lambda q:q['local_providers'][P]['widths'].__setitem__(narrow,9))
else:
 # Per-provider substitution controls: every provider is swapped against a partner provider.
 for P in provider_ids:
  Qp=partner(P)
  at_p=lambda q,P=P:next(c for c in q['calls']if c['provider_id']==P)
  diff=[h for h in range(R)if providers[P]['widths'][h]!=providers[Qp]['widths'][h]]
  narrow=next(h for h in range(R)if providers[P]['widths'][h]<9)
  reject(P+': wrong provider at its invocation',lambda q,P=P,Qp=Qp,at_p=at_p:at_p(q).__setitem__('provider_id',Qp))
  reject(P+': stale per-call local program hash',lambda q,Qp=Qp,at_p=at_p:at_p(q).__setitem__('local_program_sha256',registry[Qp]['local_program_checks'][at_p(q)['orientation']]['sha256']))
  reject(P+': stale serialized provider program',lambda q,P=P,Qp=Qp:q['local_providers'][P].__setitem__('local_programs',registry[Qp]['local_programs']))
  reject(P+': unbound residual adapter hash',lambda q,P=P:q['local_providers'][P].__setitem__('residual_adapter_sha256','0'*64))
  if diff:reject(P+': partner width in provider width registry',lambda q,P=P,Qp=Qp,h=diff[0]:q['local_providers'][P]['widths'].__setitem__(h,providers[Qp]['widths'][h]))
  reject(P+': wrong per-call residual width',lambda q,at_p=at_p,h=narrow:at_p(q)['owners'][2*V+h][1].__setitem__(3,at_p(q)['owners'][2*V+h][1][3]-1))
  reject(P+': wrong sweep provider',lambda q,P=P,Qp=Qp:next(e for e in q['execution_schedule']if e['kind']=='local_cover_sweep'and DISPATCH[e['stage'],e['replica']]==P).__setitem__('provider_id',Qp))
  reject(P+': entering helper width silently restored to nine',lambda q,P=P,h=narrow:q['local_providers'][P]['widths'].__setitem__(h,9))

report=dict(status='PASS_INDEPENDENT_ASYNC_WHOLE_OWNER_CONTROLLER_PHASES_AND_SPECTATORS',template_sha256=summary['template_sha256'],complex_template_sha256=summary['template_sha256'],complex_live=DATA,complex_profile=r['profile'],complex_hosted_residuals=HOSTED,physical=PHYSICAL,rank_mass=r['mass'],deficit=DEFICIT,entering_helper_roles=r['entering'],cross_replica_helper_roles=r['cross_replica'],one_owner_per_complete_invocation=True,helper_busy_family_window_checks=r['busy_family_checks'],complete_invocations=r['invocations'],actual_orthogonal_73column_maps=len(r['sigmas']),actual_sigma_stream_sha256=r['sigma_digest'],all_actual_residual_and_spectator_charts=True,idle_remainders=r['idle_remainders'],mutations_rejected=controls,mutation_controls_run='--mutation-controls' in sys.argv[4:],provider_phase_semantic_sha256=phase_semantic_hashes,provider_artifact_semantic_sha256=artifact_semantic_hashes,widths_by_provider={pid:dict(sorted(Counter(providers[pid]['widths']).items()))for pid in provider_ids},provider_counts=dict(Counter(c['provider_id']for c in ct['calls'])),all_provider_program_phase_and_wrapper_bindings=True,scope='Independent exact asynchronous chronology, per-replica phase projection, owner/chart/paid-profile audit. Uses per-invocation local providers bound by exact scalar, phase and residual-wrapper receipts; all-size compilation and complete coefficient invoice are separate inherited obligations.')
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

owners=dict(status='PASS_INDEPENDENT_ASYNC_OWNERS_AND_PROFILE',template_sha256=summary['template_sha256'],paid_profile=r['profile'],live=DATA,physical=PHYSICAL,rank_mass=r['mass'],deficit=DEFICIT,hosted_residuals=HOSTED,banked_residuals=0,all_live_owners_per_call_distinct=True,owners_per_call=N,actual_helper_owner_charts=HOSTED,actual_73column_sigmas=len(r['sigmas']),cross_replica_helper_roles=r['cross_replica'],explicit_idle_remainder_children=r['idle_remainders'],source_idle_children_charged=sum(x['replicas']for x in parent['idle_children']),source_artifacts=summary['source_artifacts'],provider_phase_semantic_sha256=phase_semantic_hashes,provider_artifact_semantic_sha256=artifact_semantic_hashes,controller_audit_sha256=hashlib.sha256(REPORT.read_bytes()).hexdigest())
(REPORT.parent/'OWNERS-AND-PROFILE.json').write_text(json.dumps(owners,indent=2)+'\n')

# Literal residual frames are a compact export of the already checked offsets,
# not another global replay. Every row names its actual inherited axes.
frames=[]
for z in ct['idle_children']:
 axes=list(map(int,ph['recipes'][z['port']]['idle_children'][z['child']]['orthogonal_axes']))
 tail=axes[z['pending_offset']:]
 assert len(tail)==z['rank']
 frames.append(dict(z,orthogonal_axes=tail))
frame_raw=json.dumps(frames,sort_keys=True,separators=(',',':')).encode()
portable=bytearray(gzip.compress(frame_raw,mtime=0));portable[9]=255
(OUT/'IDLE-REMAINDER-FRAMES.json.gz').write_bytes(bytes(portable))
frame_receipt=dict(status='PASS_LITERAL_IDLE_REMAINDER_FRAMES',template_sha256=summary['template_sha256'],
 uncompressed_frames_sha256=hashlib.sha256(frame_raw).hexdigest(),children=len(frames),
 rank_profile=dict(sorted(Counter(z['rank']for z in frames).items())),
 source_data_phase_sha256=hashlib.sha256((BASE/'work/complex-nine-native/DATA-PHASES.json').read_bytes()).hexdigest(),
 scope='Actual orthogonal axes after the independently checked whole-owner prefix in each inherited pending child.')
(REPORT.parent/'IDLE-REMAINDER-FRAMES.json').write_text(json.dumps(frame_receipt,indent=2)+'\n')
