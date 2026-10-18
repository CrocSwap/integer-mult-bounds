"""Two-provider width-seven whole-owner derivative, adapted with OpenAI Codex assistance.
Based on PR514 and its credited PR484/507 lineage.
CLI: --base VERIFIED_VARIANT --owners ASYNC-OWNERS.json.gz --plan ASYNC-PLAN.json --out OUT
No optimizer or unpublished word builder runs. The frozen map explicitly names
one whole helper per family per complete invocation, plus borrowed spectators.
"""
import sys,json,gzip,hashlib,copy,argparse
from pathlib import Path
from collections import Counter,defaultdict
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--base',type=Path,required=True);parser.add_argument('--owners',type=Path,required=True);parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
a=parser.parse_args();BASE,MAP,PLAN,OUT=(p.resolve()for p in(a.base,a.owners,a.plan,a.out));assert not OUT.exists();OUT.mkdir(parents=True)
class OH:
 @staticmethod
 def idle_basis(q):
  z=next(i for i in range(9)if not(q>>i)&1);u=q^(1<<z);order=list(range(9));order[0],order[z]=order[z],order[0]
  return[(1<<i)^(u if u>>i&1 else 0)for i in order]+[1<<i for i in range(9,73)]
 @staticmethod
 def spectators(q,pending,off,w):
  B=OH.idle_basis(q);occ=[B.index(v)for v in pending[off:off+w]]
  return[j for j in range(73)if j not in occ][:9-w]
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
plan=read(PLAN);call_order=[tuple(x)for x in plan['order']];assert len(call_order)==len(set(call_order))==72;at={x:i for i,x in enumerate(call_order)}
parent=read(BASE/'split-centres/GLOBAL-TEMPLATE.json.gz');t=copy.deepcopy(parent);canon=read(BASE/'split-centres/CANONICAL-WORD.json.gz');ph=read(BASE/'work/complex-nine-native/DATA-PHASES.json');roles=read(MAP);T=8;V=canon['v'];M=73;R=canon['R'];DATA=8*T*V;assert(V,canon['h'])==(112,9)
assert(len(roles),len(canon['start']),len(ph['recipes']))==(72*R,2*V+R,V)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
provider_files=('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','RESIDUAL-ADAPTERS.json','CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json')
registry={};source_artifacts={'work/complex-nine-native/DATA-PHASES.json':sha(BASE/'work/complex-nine-native/DATA-PHASES.json')}
for provider_id in sorted(plan['provider_registry']):
 assert provider_id in('fourcold_eight', 'width7_eight')
 directory=BASE/'providers'/provider_id
 assert all((directory/f).is_file()for f in provider_files)
 pc=read(directory/'CANONICAL-WORD.json.gz');checks=read(directory/'LOCAL-CHECKS.json');programs=read(directory/'LOCAL-PROGRAMS.json.gz');replay=read(directory/'INDEPENDENT-LOCAL-REPLAY.json')
 assert(pc['v'],pc['h'],pc['R'],pc['ports'],pc['centers'])==(V,9,R,canon['ports'],canon['centers'])
 assert replay['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
 assert replay['canonical_word_sha256']==sha(directory/'CANONICAL-WORD.json.gz')and replay['local_programs_sha256']==sha(directory/'LOCAL-PROGRAMS.json.gz')
 widths=[9-len(pc['frames'][pc['start'][2*V+h]])for h in range(R)]
 assert widths==plan['provider_registry'][provider_id]['widths']
 for name in provider_files:
  value=sha(directory/name);assert value==plan['provider_registry'][provider_id]['artifact_sha256'][name]
  source_artifacts[f'providers/{provider_id}/{name}']=value
 registry[provider_id]=dict(local_programs=programs,canonical_word_sha256=sha(directory/'CANONICAL-WORD.json.gz'),local_programs_sha256=sha(directory/'LOCAL-PROGRAMS.json.gz'),local_program_checks=checks,exact_local_clifford_recipe_sha256=sha(directory/'CLIFFORD-RECIPES.json'),residual_adapter_sha256=sha(directory/'RESIDUAL-ADAPTERS.json'),v=V,h=9,R=R,ports=pc['ports'],centers=pc['centers'],widths=widths)
selected={(c['stage'],c['replica']):c for c in plan['provider_calls']}
assert len(selected)==72 and set(selected)==set(call_order)
assert Counter(c['provider']for c in selected.values())=={'width7_eight': 63, 'fourcold_eight': 9}
per_call_widths={(c['stage'],c['replica']):c['widths']for c in plan['per_call_widths']}
for key,c in selected.items():
 assert c['time']==at[key] and c['provider']in registry
 assert per_call_widths[key]==registry[c['provider']]['widths']
for key in('local_programs','exact_local_clifford_recipe_sha256','residual_adapter_sha256'):t.pop(key)
t['local_providers']=registry
rank={z['child']:z['rank']for z in parent['idle_children']};side={};pairs={}
for e in parent['execution_schedule']:
 if e['kind']=='idle_cover_sweep':
  for sd,ch in enumerate(e['child_indices']):side[ch]=sd;pairs[ch]=e['pair']
bycall=defaultdict(dict);used=defaultdict(set);sigmas={};digest=hashlib.sha256();entering=0
for z in roles:
 s,rep,h=z['stage'],z['replica'],z['helper'];i,cp,off,w,f=z['child'],z['copy'],z['offset'],z['width'],z['family'];orp,port=divmod(cp,V)
 assert 0<=s<9 and 0<=rep<T and 0<=h<R and w==registry[selected[s,rep]['provider']]['widths'][h] and 0<=orp<T
 assert f==orp*(8*V)+(2*pairs[i]+side[i])*V+port
 assert(h not in bycall[s,rep])and off>=0 and off+w<=rank[i]
 assert z['time']==at[s,rep] and z['time'] in plan['windows'][f'{orp},{i}'][1]
 B=OH.idle_basis(canon['ports'][port]);pending=list(map(int,ph['recipes'][port]['idle_children'][i]['orthogonal_axes']));assert len(pending)==rank[i]
 occ=[B.index(v)for v in pending[off:off+w]];sp=OH.spectators(canon['ports'][port],pending,off,w)if w<9 else[]
 order=occ+sp+[j for j in range(M)if j not in occ and j not in sp];assert len(order)==len(set(order))==M
 sigma=[B[j]for j in order];sigmahash=hashlib.sha256(json.dumps(sigma,separators=(',',':')).encode()).hexdigest();sigmas[sigmahash]=sigma
 route=[4,i,off,w,sp]if w<9 else[3,i,off];bycall[s,rep][h]=[f,route];entering+=w<9
 cells=set(range(off,off+w));assert not used[i,orp,port]&cells;used[i,orp,port]|=cells
 digest.update(json.dumps([s,rep,h,f,sigmahash],separators=(',',':')).encode()+b'\n')
for c in t['calls']:
 k=(c['stage'],c['replica']);assert set(bycall[k])==set(range(R))
 c['owners']=c['owners'][:(2*V)]+[bycall[k][h]for h in range(R)];assert len({f for f,r in c['owners']})==2*V+R and all(f<DATA for f,r in c['owners'])
 pc=selected[k];provider_id=pc['provider'];assert c['orientation']==pc['orientation']
 c['provider_id']=provider_id;c['local_program_sha256']=registry[provider_id]['local_program_checks'][c['orientation']]['sha256']
 assert c['local_program_sha256']==pc['local_program_sha256']
newidle=[];paid=Counter()
for c in t['calls']:
 for r,n in registry[c['provider_id']]['local_program_checks'][c['orientation']]['paid_profile'].items():paid[int(r)]+=n
for old in parent['idle_children']:
 i,port=old['child'],old['port']
 for rep in range(T):
  u=used[i,rep,port];assert u==set(range(len(u)));left=old['rank']-len(u)
  if left:
   f=rep*(8*V)+(2*pairs[i]+side[i])*V+port;newidle.append(dict(child=i,port=port,replica=rep,replicas=1,family=f,rank=left,hosted=len(u),pending_offset=len(u)));paid[left]+=1
assert M*DATA-sum(r*n for r,n in paid.items())==2560
C=len(canon['centers']);physical=DATA+C+R+2
assert parent['physical']-parent['live']==C+R+2
# Local circuits, exact phase recipes, normalized wrappers and data routes stay
# byte-identical; only full-family helper placement and idle remainders change.
t.update(version='round20-R504-asynchronous-whole-owner-v1',live=DATA,physical=physical,idle_children=newidle,private_namespace={'centers':[DATA,DATA+C],'reserved_tableau':[DATA+C,DATA+C+R],'coefficient':[physical-2,physical]})
t['hosting']=dict(rule='one-helper-per-physical-family-per-complete-invocation',max_helpers_per_physical_family_per_call=1,scope='asynchronously interleaved data replicas; each whole helper occurs once per(stage,invocation replica)',pooled_slots=roles,banks=[0]*9,owner_map_sha256=hashlib.sha256(MAP.read_bytes()).hexdigest(),idle_remainder_semantics='Each idle_children item acts once, on its explicit replica/family, at pending_offset with the stated rank; replicas=1.')
t['route_semantics']['helper']='Whole physical family may belong to another replica; actual orthogonal port basis followed by residual/spectator coordinate permutation. Entering helpers have paid wrappers around the complete invocation; at most one helper and no active data wire uses that family in that invocation. Route[4,child,offset,width,spectators], width9 route[3,child,offset].'
t['bank_padding']['families']=[];t['bank_padding']['children']=[];t['cover_final_correction']['families']=[0,DATA];t['cover_final_correction']['charged_calls_per_cover']=DATA
for e in t['execution_schedule']:
 if e['kind']=='bank_padding_cover_sweep':e['families']=[DATA,DATA]
 elif e['kind']=='translate_every_live_family':e.update(t['cover_final_correction'])
# Expand the retained controller into one-replica blocks; each block consists
# of its full local cover sweep and every following replica-local event before
# its next local sweep. Final whole-stock correction remains after all replicas.
blocks={};globals_=[];st=None
for ei,e in enumerate(parent['execution_schedule']):
 if e['kind']in('bank_padding_cover_sweep','translate_every_live_family'):
  globals_.append((ei,e));continue
 if e['kind']=='local_cover_sweep':st=e['stage'];blocks[st]=[]
 assert st is not None
 blocks[st].append((ei,e))
new_schedule=[]
for tm,(s,rep)in enumerate(call_order):
 for ei,e in blocks[s]:
  ne=copy.deepcopy(e);ne.update(replica=rep,replicas=[rep],source_event=ei,time=tm)
  if ne['kind']=='local_cover_sweep':ne['provider_id']=selected[s,rep]['provider']
  new_schedule.append(ne)
for ei,e in globals_:
 ne=copy.deepcopy(e);ne['source_event']=ei
 if e['kind']=='bank_padding_cover_sweep':ne['families']=[DATA,DATA]
 else:ne.update(t['cover_final_correction'])
 new_schedule.append(ne)
t['execution_schedule']=new_schedule
cmap={(c['stage'],c['replica']):c for c in t['calls']}
t['calls']=[dict(cmap[s,rep],time=tm)for tm,(s,rep)in enumerate(call_order)]
t['loop_order']='Follow the explicit asynchronous execution_schedule. Each local invocation completes before the next, including its entire cover sweep and normalization wrappers. Per-replica source event order is preserved; each idle remainder executes before that replica next touches its family.'
t['async_schedule']=dict(order=[list(x)for x in call_order],source_plan_sha256=hashlib.sha256(PLAN.read_bytes().replace(b'\r\n',b'\n')).hexdigest(),source_schedule=parent['execution_schedule'],source_call_order=[[c['stage'],c['replica']]for c in parent['calls']],scope='Only independent replica controllers are interleaved. Owner windows are measured on the owner replica timeline; no within-cover or within-invocation interleaving.')
assert dict(sorted(paid.items()))=={int(k):v for k,v in plan['profile'].items()}
assert M*M>2*max(paid)**2

assert all(c['local_program_sha256']==registry[c['provider_id']]['local_program_checks'][c['orientation']]['sha256']for c in t['calls'])
t['provider_dispatch']='For each indivisible local_cover_sweep, execute local_providers[call.provider_id].local_programs[call.orientation] with that provider residual adapters and Clifford recipes. The sweep provider_id must equal its call provider_id.'
raw=json.dumps(t,sort_keys=True,separators=(',',':')).encode();(OUT/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(raw,mtime=0))
res=dict(status='EMITTED_MIXED_PROVIDER_ASYNCHRONOUS_WHOLE_OWNER_COMPLEX_TEMPLATE',
 template_sha256=hashlib.sha256(raw).hexdigest(),
 parent_template_sha256=hashlib.sha256(gzip.decompress((BASE/'split-centres/GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest(),
 live=DATA,physical=physical,global_profile=dict(sorted(paid.items())),
 rank_mass=sum(r*n for r,n in paid.items()),deficit=2560,maxchild=max(paid),
 hosted_residuals=len(roles),banks_per_stage=[0]*9,entering_helper_roles=entering,
 unique_actual_73column_sigmas=len(sigmas),sigma_stream_sha256=digest.hexdigest(),
 cross_replica_helper_roles=sum(z['replica']!=z['owner_replica']for z in roles),
 asynchronous_order_sha256=hashlib.sha256(json.dumps(call_order,separators=(',',':')).encode()).hexdigest(),
 source_artifacts=source_artifacts,provider_counts=dict(Counter(c['provider_id']for c in t['calls'])),
 scope='Two actual verified plain/width-seven providers dispatched per complete invocation; independent controller/spectator/normalization and complete finite invoice admission required.')
(OUT/'HOSTED.json').write_text(json.dumps(res,indent=2)+'\n');(OUT/'ACTUAL-SIGMAS.json.gz').write_bytes(gzip.compress(json.dumps(sigmas,separators=(',',':')).encode(),mtime=0));print(json.dumps(res,indent=2))
