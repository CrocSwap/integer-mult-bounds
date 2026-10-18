"""OpenAI Codex independent serialized ASYNCHRONOUS controller/spectator audit.
Imports no emitter, optimizer, expander, edge-coloring, or source hosting code.
CLI: VERIFIED_VARIANT POOLED_HOSTED OUT.json [--mutation-controls]
The local provider is read from VERIFIED_VARIANT, never from a baseline width histogram.
"""
import sys,json,gzip,hashlib,copy
from pathlib import Path
from collections import Counter,defaultdict
BASE,OUT,REPORT=map(lambda p:Path(p).resolve(),sys.argv[1:4]);read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
parent=read(BASE/'split-centres/GLOBAL-TEMPLATE.json.gz');canon=read(BASE/'split-centres/CANONICAL-WORD.json.gz');checks=read(BASE/'split-centres/LOCAL-CHECKS.json');ph=read(BASE/'work/complex-nine-native/DATA-PHASES.json');ct=read(OUT/'GLOBAL-TEMPLATE.json.gz');summary=read(OUT/'HOSTED.json');V=canon['v'];R=canon['R'];N=2*V+R;CENTRES=len(canon['centers']);assert V==112 and canon['h']==9; width=[9-len(canon['frames'][canon['start'][2*V+h]])for h in range(R)];prank={e['child']:e['rank']for e in parent['idle_children']};M=73;T=8;DATA=8*T*V;PHYSICAL=DATA+CENTRES+R+2;CALLS=72;HOSTED=CALLS*R

def orthobasis(port):
 q=canon['ports'][port];z=next(i for i in range(9)if(q>>i)&1==0);a=q^(1<<z);order=list(range(9));order[z],order[0]=order[0],order[z]
 b=[(1<<i)^(a if a>>i&1 else 0)for i in order]+[1<<i for i in range(9,73)]
 assert len(b)==73 and all((x&y).bit_count()%2==int(i==j)for i,x in enumerate(b)for j,y in enumerate(b));return b
bases=[orthobasis(p)for p in range(V)]
# Bind the selected provider's actual normalization recipes, including newly
# selected entrance frames; a baseline recipe registry cannot silently survive.
required_artifacts={'split-centres/CANONICAL-WORD.json.gz','split-centres/LOCAL-PROGRAMS.json.gz','split-centres/LOCAL-CHECKS.json','split-centres/RESIDUAL-ADAPTERS.json','work/complex-nine-native/DATA-PHASES.json'}
assert required_artifacts <= set(summary['source_artifacts'])
adapter_path=BASE/'split-centres/RESIDUAL-ADAPTERS.json'
assert hashlib.sha256(adapter_path.read_bytes()).hexdigest()==parent['residual_adapter_sha256']
adapters=read(adapter_path)['recipes']
for h,w in enumerate(width):
 if w<9:
  f=canon['start'][(2*V)+h];a=adapters[str(f)]
  assert a['frame']==f and a['vectors']==canon['frames'][f] and a['rank']==w and a['entrance_rank']==9-w

def audit(t):
 assert(t['live'],t['physical'])==(DATA,PHYSICAL)
 assert t['local_programs']==parent['local_programs']and t['recipe']==parent['recipe']and 'each local invocation completes before the next' in t['loop_order'].lower()
 assert len(t['calls'])==72 and t['hosting']['max_helpers_per_physical_family_per_call']==1 and t['hosting']['banks']==[0]*9
 for key in('exact_data_phase_recipe_sha256','exact_local_clifford_recipe_sha256','residual_adapter_sha256','adapter_policy'):assert t[key]==parent[key]
 # Independently project the literal schedule onto every data replica.
 src=parent['execution_schedule'];assert t['async_schedule']['source_schedule']==src
 assert t['async_schedule']['source_call_order']==[[c['stage'],c['replica']]for c in parent['calls']]
 order=[(c['stage'],c['replica'])for c in t['calls']]
 assert [list(x)for x in order]==t['async_schedule']['order'] and len(set(order))==72
 all_local=[];perrep={r:[]for r in range(8)};globals_=[]
 for e in t['execution_schedule']:
  j=e['source_event'];old=copy.deepcopy(src[j])
  if 'replica'in e:
   r=e['replica'];assert 0<=r<8 and j<30;perrep[r].append(j)
   expected=old|dict(source_event=j,replica=r,replicas=[r],time=e['time'])
   assert e==expected
   assert 0<=e['time']<72 and order[e['time']][1]==r
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
  assert {k:v for k,v in call.items()if k not in('owners','time')}=={k:v for k,v in old.items()if k!='owners'}
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
 assert set(roles)=={(s,rep,h)for s in range(9)for rep in range(8)for h in range(R)}
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
 mass=sum(r*n for r,n in paid.items());assert73=73*DATA-mass;assert assert73==2560 and 73**2>2*max(paid)**2
 return dict(profile=dict(sorted(paid.items())),mass=mass,hosted=HOSTED,entering=entering,cross_replica=cross,sigma_digest=digest.hexdigest(),sigmas=sigmas,idle_remainders=len(wanted),busy_family_checks=len(roles),invocations=72)

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
report=dict(status='PASS_INDEPENDENT_ASYNC_WHOLE_OWNER_CONTROLLER_PHASES_AND_SPECTATORS',template_sha256=summary['template_sha256'],complex_template_sha256=summary['template_sha256'],complex_live=DATA,complex_profile=r['profile'],complex_hosted_residuals=HOSTED,physical=PHYSICAL,rank_mass=r['mass'],deficit=2560,entering_helper_roles=r['entering'],cross_replica_helper_roles=r['cross_replica'],one_owner_per_complete_invocation=True,helper_busy_family_window_checks=r['busy_family_checks'],complete_invocations=r['invocations'],actual_orthogonal_73column_maps=len(r['sigmas']),actual_sigma_stream_sha256=r['sigma_digest'],all_actual_residual_and_spectator_charts=True,idle_remainders=r['idle_remainders'],mutations_rejected=controls,mutation_controls_run='--mutation-controls' in sys.argv[4:],widths=dict(sorted(Counter(width).items())),scope='Independent exact asynchronous chronology, per-replica phase projection, owner/chart/paid-profile audit. Uses the new selected local program bound by fresh scalar, phase and residual-wrapper receipts; all-size compilation and complete coefficient invoice are separate inherited obligations.')
REPORT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

owners=dict(status='PASS_INDEPENDENT_ASYNC_OWNERS_AND_PROFILE',template_sha256=summary['template_sha256'],paid_profile=r['profile'],live=DATA,physical=PHYSICAL,rank_mass=r['mass'],deficit=2560,hosted_residuals=HOSTED,banked_residuals=0,all_live_owners_per_call_distinct=True,owners_per_call=N,actual_helper_owner_charts=HOSTED,actual_73column_sigmas=len(r['sigmas']),cross_replica_helper_roles=r['cross_replica'],explicit_idle_remainder_children=r['idle_remainders'],source_idle_children_charged=sum(x['replicas']for x in parent['idle_children']),source_artifacts=summary['source_artifacts'],controller_audit_sha256=hashlib.sha256(REPORT.read_bytes()).hexdigest())
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
(OUT/'IDLE-REMAINDER-FRAMES.json.gz').write_bytes(gzip.compress(frame_raw,mtime=0))
frame_receipt=dict(status='PASS_LITERAL_IDLE_REMAINDER_FRAMES',template_sha256=summary['template_sha256'],
 uncompressed_frames_sha256=hashlib.sha256(frame_raw).hexdigest(),children=len(frames),
 rank_profile=dict(sorted(Counter(z['rank']for z in frames).items())),
 source_data_phase_sha256=hashlib.sha256((BASE/'work/complex-nine-native/DATA-PHASES.json').read_bytes()).hexdigest(),
 scope='Actual orthogonal axes after the independently checked whole-owner prefix in each inherited pending child.')
(REPORT.parent/'IDLE-REMAINDER-FRAMES.json').write_text(json.dumps(frame_receipt,indent=2)+'\n')

