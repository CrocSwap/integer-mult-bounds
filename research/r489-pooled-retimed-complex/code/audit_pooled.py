"""OpenAI Codex independent serialized cross-replica controller/spectator audit.
Imports no emitter, optimizer, expander, edge-coloring, or source hosting code.
CLI: VERIFIED_VARIANT POOLED_HOSTED OUT.json
"""
import sys,json,gzip,hashlib,copy
from pathlib import Path
from collections import Counter,defaultdict
BASE,OUT,REPORT=map(lambda p:Path(p).resolve(),sys.argv[1:4]);read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
parent=read(BASE/'split-centres/GLOBAL-TEMPLATE.json.gz');canon=read(BASE/'split-centres/CANONICAL-WORD.json.gz');checks=read(BASE/'split-centres/LOCAL-CHECKS.json');ph=read(BASE/'work/complex-nine-native/DATA-PHASES.json');ct=read(OUT/'GLOBAL-TEMPLATE.json.gz');summary=read(OUT/'HOSTED.json');width=[9-len(canon['frames'][canon['start'][240+h]])for h in range(560)];prank={e['child']:e['rank']for e in parent['idle_children']};M=73;T=8;DATA=7680

def orthobasis(port):
 q=canon['ports'][port];z=next(i for i in range(9)if(q>>i)&1==0);a=q^(1<<z);order=list(range(9));order[z],order[0]=order[0],order[z]
 b=[(1<<i)^(a if a>>i&1 else 0)for i in order]+[1<<i for i in range(9,73)]
 assert len(b)==73 and all((x&y).bit_count()%2==int(i==j)for i,x in enumerate(b)for j,y in enumerate(b));return b
bases=[orthobasis(p)for p in range(120)]

def audit(t):
 assert(t['live'],t['physical'])==(7680,8258)
 assert t['local_programs']==parent['local_programs']and t['recipe']==parent['recipe']and t['loop_order']==parent['loop_order']and 'each local invocation completes before the next' in t['loop_order']
 assert len(t['calls'])==72 and t['hosting']['max_helpers_per_physical_family_per_call']==1 and t['hosting']['banks']==[0]*9
 for key in('exact_data_phase_recipe_sha256','exact_local_clifford_recipe_sha256','residual_adapter_sha256','adapter_policy'):assert t[key]==parent[key]
 # Schedule is unchanged except for absent banks and the new live range.
 expect=copy.deepcopy(parent['execution_schedule'])
 for e in expect:
  if e['kind']=='bank_padding_cover_sweep':e['families']=[7680,7680]
  elif e['kind']=='translate_every_live_family':e['families']=[0,7680];e['charged_calls_per_cover']=7680
 assert t['execution_schedule']==expect
 assert t['bank_padding']==dict(parent['bank_padding'],families=[])
 assert t['cover_final_correction']==dict(parent['cover_final_correction'],families=[0,7680],charged_calls_per_cover=7680)
 assert t['private_namespace']=={'centers':[7680,7696],'reserved_tableau':[7696,8256],'coefficient':[8256,8258]}
 # Last physical pair touch, including both sides of every bridge.
 pairs={};sides={};windows={};last={};seen=[];stagepair={e['stage']:e['pair']for e in parent['recipe']if e['kind']=='local'}
 for pos,e in enumerate(t['execution_schedule']):
  if e['kind']=='local_cover_sweep':p=stagepair[e['stage']];seen.append((pos,e['stage'],p));last[p]=pos
  elif e['kind']=='bridge':last[e['src']]=last[e['dst']]=pos
  elif e['kind']=='idle_cover_sweep':
   for side,i in enumerate(e['child_indices']):
    if i not in prank:continue
    pairs[i]=e['pair'];sides[i]=side;windows[i]={s for loc,s,p in seen if loc>last.get(e['pair'],-1)and p!=e['pair']}
 used=defaultdict(set);roles={};paid=Counter();sigmas={};digest=hashlib.sha256();entering=0;cross=0;touches=defaultdict(list)
 for call,old in zip(t['calls'],parent['calls']):
  assert {k:v for k,v in call.items()if k!='owners'}=={k:v for k,v in old.items()if k!='owners'}
  s,rep,pair=call['stage'],call['replica'],call['pair'];own=call['owners'];assert len(own)==800 and len({f for f,rt in own})==800 and all(0<=f<DATA for f,rt in own)
  assert own[:240]==old['owners'][:240]
  for h,(family,route)in enumerate(own[240:]):
   w=width[h];typ,i,off=route[:3];ownerrep,sub=divmod(family,960);fampair,sub=divmod(sub,240);side,port=divmod(sub,120)
   assert s in windows[i]and fampair==pairs[i]!=pair and side==sides[i] and 0<=off and off+w<=prank[i]
   B=bases[port];pend=[int(x)for x in ph['recipes'][port]['idle_children'][i]['orthogonal_axes']];assert len(pend)==prank[i]
   occ=[B.index(v)for v in pend[off:off+w]];sp=[j for j in range(M)if j not in occ][:9-w]
   assert route==([3,i,off]if w==9 else[4,i,off,w,sp]);assert len(set(occ+sp))==9
   order=occ+sp+[j for j in range(M)if j not in occ and j not in sp];assert sorted(order)==list(range(M));sigma=[B[j]for j in order]
   assert sigma[:w]==pend[off:off+w]and sigma[w:9]==[B[j]for j in sp]
   sh=hashlib.sha256(json.dumps(sigma,separators=(',',':')).encode()).hexdigest();sigmas[sh]=sigma;digest.update(json.dumps([s,rep,h,family,sh],separators=(',',':')).encode()+b'\n')
   key=(i,ownerrep,port);cells=set(range(off,off+w));assert not used[key]&cells;used[key]|=cells
   role=(s,rep,h);assert role not in roles;roles[role]=dict(stage=s,replica=rep,helper=h,family=family,owner_replica=ownerrep,child=i,copy=ownerrep*120+port,port=port,offset=off,width=w)
   touches[family].append((s,rep,h));entering+=w<9;cross+=rep!=ownerrep
  for r,n in checks[call['orientation']]['paid_profile'].items():paid[int(r)]+=n
 assert set(roles)=={(s,rep,h)for s in range(9)for rep in range(8)for h in range(560)}
 # The frozen pooled metadata must bind the actual serialized owner maps.
 assert len(t['hosting']['pooled_slots'])==40320
 for z in t['hosting']['pooled_slots']:
  key=(z['stage'],z['replica'],z['helper']);assert key in roles
  assert {k:z[k]for k in roles[key]}==roles[key]
 assert len({(z['stage'],z['replica'],z['helper'])for z in t['hosting']['pooled_slots']})==40320
 rem={};wanted=[]
 for old in parent['idle_children']:
  i,port=old['child'],old['port']
  for rep in range(T):
   u=used[i,rep,port];assert u==set(range(len(u)));r=old['rank']-len(u)
   if r:
    f=rep*960+(2*pairs[i]+sides[i])*120+port;wanted.append(dict(child=i,port=port,replica=rep,replicas=1,family=f,rank=r,hosted=len(u),pending_offset=len(u)));paid[r]+=1
 assert t['idle_children']==wanted
 mass=sum(r*n for r,n in paid.items());assert73=73*7680-mass;assert assert73==2496 and max(paid)==8
 return dict(profile=dict(sorted(paid.items())),mass=mass,hosted=40320,entering=entering,cross_replica=cross,sigma_digest=digest.hexdigest(),sigmas=sigmas,idle_remainders=len(wanted),busy_family_checks=len(roles),invocations=72)

r=audit(ct);raw=gzip.decompress((OUT/'GLOBAL-TEMPLATE.json.gz').read_bytes());assert hashlib.sha256(raw).hexdigest()==summary['template_sha256'];assert r['profile']=={int(k):v for k,v in summary['global_profile'].items()};assert r['sigmas']==read(OUT/'ACTUAL-SIGMAS.json.gz');assert r['sigma_digest']==summary['sigma_stream_sha256']
controls=[]
def reject(name,mut):
 q=copy.deepcopy(ct);mut(q)
 try:audit(q)
 except(AssertionError,KeyError,IndexError,ValueError,TypeError):controls.append(name)
 else:raise AssertionError('ACCEPTED '+name)
enter=lambda q:next(o for c in q['calls']for o in c['owners'][240:]if o[1][0]==4)
reject('alias two whole owners',lambda q:q['calls'][0]['owners'].__setitem__(241,q['calls'][0]['owners'][240]))
reject('helper on active data family',lambda q:q['calls'][0]['owners'][240].__setitem__(0,q['calls'][0]['owners'][0][0]))
reject('owner in private namespace',lambda q:q['calls'][0]['owners'][240].__setitem__(0,7680))
reject('unbound change of owner replica',lambda q:q['calls'][0]['owners'][240].__setitem__(0,(q['calls'][0]['owners'][240][0]+960)%7680))
reject('omit complete invocation',lambda q:q['calls'].pop())
reject('reorder invocation replicas',lambda q:q['calls'].__setitem__(0,q['calls'][1]))
reject('interleave local invocations',lambda q:q.__setitem__('loop_order','interleaved local instructions'))
reject('change local instruction stream',lambda q:q['local_programs']['forward'].pop())
reject('wrong residual width',lambda q:enter(q)[1].__setitem__(3,enter(q)[1][3]-1))
reject('wrong spectator coordinate',lambda q:enter(q)[1][4].__setitem__(0,72))
reject('omit spectator route',lambda q:enter(q).__setitem__(1,enter(q)[1][:3]))
reject('overlap residual footprint',lambda q:q['calls'][0]['owners'][240][1].__setitem__(2,100))
reject('omit idle remainder',lambda q:q['idle_children'].pop())
reject('underpay idle remainder',lambda q:q['idle_children'][0].__setitem__('rank',0))
reject('omit bridge touch',lambda q:q['execution_schedule'].pop(next(i for i,e in enumerate(q['execution_schedule'])if e['kind']=='bridge')))
reject('remove one-owner rule',lambda q:q['hosting'].pop('max_helpers_per_physical_family_per_call'))
reject('duplicate frozen role',lambda q:q['hosting']['pooled_slots'].__setitem__(1,q['hosting']['pooled_slots'][0]))
reject('understate physical reserve',lambda q:q.__setitem__('physical',8257))
report=dict(status='PASS_INDEPENDENT_POOLED_WHOLE_OWNER_CONTROLLER_AND_SPECTATORS',template_sha256=summary['template_sha256'],complex_template_sha256=summary['template_sha256'],complex_live=7680,complex_profile=r['profile'],complex_hosted_residuals=40320,physical=8258,rank_mass=r['mass'],deficit=2496,entering_helper_roles=r['entering'],cross_replica_helper_roles=r['cross_replica'],one_owner_per_complete_invocation=True,helper_busy_family_window_checks=r['busy_family_checks'],complete_invocations=r['invocations'],actual_orthogonal_73column_maps=len(r['sigmas']),actual_sigma_stream_sha256=r['sigma_digest'],all_actual_residual_and_spectator_charts=True,idle_remainders=r['idle_remainders'],mutations_rejected=controls,widths=dict(sorted(Counter(width).items())),scope='Independent exact finite controller/owner/chart/paid-profile audit. Uses unchanged source local program and normalized residual-wrapper identities; all-size compilation and complete coefficient invoice are separate inherited obligations.')
REPORT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
