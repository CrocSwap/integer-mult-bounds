"""Independent serialized mixed-stage owner/chart/profile and schedule audit.
Imports no emitter, coloring, optimizer, or upstream geometry implementation.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,gzip,hashlib,copy,sys
ROOT=Path(__file__).resolve().parent;R=Path(sys.argv[1]).resolve();BASE=R/'local';O=R/'mixed'
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def blob(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
t=read(O/'GLOBAL-TEMPLATE.json.gz');parent=read(BASE/'baseline/split-centres/GLOBAL-TEMPLATE.json.gz');ph=read(BASE/'baseline/work/complex-nine-native/DATA-PHASES.json');hashes=read(O/'ACTUAL-SIGMAS.json.gz');summary=read(O/'HOSTED.json');assert hashlib.sha256(gzip.decompress((O/'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest()==summary['template_sha256']
expected={}
for name in ['baseline','middle']:
 d=BASE/name/'split-centres';expected[name]={k:read(d/f) for k,f in [('canonical','CANONICAL-WORD.json.gz'),('programs','LOCAL-PROGRAMS.json.gz'),('checks','LOCAL-CHECKS.json'),('recipes','CLIFFORD-RECIPES.json'),('adapters','RESIDUAL-ADAPTERS.json')]}
assert expected['baseline']['canonical']['ports']==expected['middle']['canonical']['ports'];ports=expected['baseline']['canonical']['ports'];bases=[]
for q in ports:
 j=next(i for i in range(9) if not(q>>i)&1);u=q^(1<<j);order=[j if z==0 else 0 if z==j else z for z in range(9)];B=[(1<<i)^u if ((1<<i)&u).bit_count()%2 else 1<<i for i in order]+[1<<i for i in range(9,73)];assert len(B)==73 and all((a&b).bit_count()%2==(i==j) for i,a in enumerate(B) for j,b in enumerate(B));bases.append(B)
rank={e['child']:e['rank'] for e in parent['idle_children']};pairs={};sides={};windows={};last={};prior=[];stagepair={e['stage']:e['pair'] for e in parent['recipe'] if e['kind']=='local'}
for pos,e in enumerate(parent['execution_schedule']):
 if e['kind']=='local_cover_sweep':p=stagepair[e['stage']];prior.append((pos,e['stage'],p));last[p]=pos
 elif e['kind']=='bridge':last[e['src']]=last[e['dst']]=pos
 elif e['kind']=='idle_cover_sweep':
  for sd,i in enumerate(e['child_indices']):pairs[i]=e['pair'];sides[i]=sd;windows[i]={s for at,s,p in prior if at>last.get(e['pair'],-1) and p!=e['pair']}
locals={};digests={}
for name,v in expected.items():
 for ori,es in v['programs'].items():
  H=Counter()
  for e in es:
   if e[0]=='climb':H[e[5]]+=1
   elif e[0]=='center':H[e[4]]+=1
  assert H==Counter({int(r):n for r,n in v['checks'][ori]['paid_profile'].items()});locals[name,ori]=H;digests[name,ori]=hashlib.sha256(blob(es)).hexdigest()
def audit(x,table):
 assert x['version']=='stage-dependent-pooled-whole-owner-v1' and (x['live'],x['physical'])==(7680,8258)
 assert x['local_variants']==expected and 'local_programs' not in x
 assert x['recipe']==parent['recipe'] and x['loop_order']==parent['loop_order'] and 'each local invocation completes before the next' in x['loop_order']
 ex=copy.deepcopy(parent['execution_schedule'])
 for e in ex:
  if e['kind']=='bank_padding_cover_sweep':e['families']=[7680,7680]
  elif e['kind']=='translate_every_live_family':e['families']=[0,7680];e['charged_calls_per_cover']=7680
 assert x['execution_schedule']==ex and not x['bank_padding']['families'];assert x['hosting']['banks']==[0]*9 and x['hosting']['max_helpers_per_physical_family_per_call']==1
 assert x['private_namespace']=={'centers':[7680,7696],'reserved_tableau':[7696,8256],'coefficient':[8256,8258]}
 paid=Counter();used=defaultdict(set);calls=set();sigmas={};rolelist=[]
 for call in x['calls']:
  s,rep=call['stage'],call['replica'];name='middle' if s==4 else 'baseline';assert call['variant']==name and (s,rep) not in calls;calls.add((s,rep));c=expected[name]['canonical'];ori=call['orientation'];assert call['local_program_sha256']==digests[name,ori]
  old=next(c for c in parent['calls'] if (c['stage'],c['replica'])==(s,rep));assert call['pair']==old['pair'] and ori==old['orientation'];own=call['owners'];assert own[:240]==old['owners'][:240] and len(own)==800 and len({f for f,_ in own})==800;assert all(0<=f<7680 for f,_ in own);paid.update(locals[name,ori])
  for h,(f,rt) in enumerate(own[240:]):
   w=9-len(c['frames'][c['start'][240+h]]);i,off=rt[1:3];rp,sub=divmod(f,960);pair,sub=divmod(sub,240);side,port=divmod(sub,120);assert pair==pairs[i] and side==sides[i] and s in windows[i] and pair!=call['pair'];assert 0<=off and off+w<=rank[i]
   assert (rt[0]==3)==(w==9)
   if w<9:assert rt[0]==4 and rt[3]==w
   B=bases[port];pend=ph['recipes'][port]['idle_children'][i]['orthogonal_axes'];occ=[B.index(a) for a in pend[off:off+w]];sp=[j for j in range(73) if j not in occ][:9-w];assert len(occ)==w
   if w<9:assert rt[4]==sp
   order=occ+sp+[j for j in range(73) if j not in occ+sp];assert len(set(order))==73;sig=[B[j] for j in order];sigmas[hashlib.sha256(blob(sig)).hexdigest()]=sig
   key=i,rp,port;cells=set(range(off,off+w));assert not cells&used[key];used[key]|=cells;rolelist.append(dict(stage=s,replica=rep,helper=h,child=i,copy=rp*120+port,owner_replica=rp,offset=off,width=w,family=f))
 assert calls=={(s,r) for s in range(9) for r in range(8)};assert sorted(rolelist,key=lambda z:(z['stage'],z['replica'],z['helper']))==x['hosting']['pooled_slots'];assert sigmas==table
 remainder={}
 for z in parent['idle_children']:
  i,port=z['child'],z['port']
  for rep in range(8):
   cells=used[i,rep,port];assert cells==set(range(len(cells)));left=z['rank']-len(cells)
   if left:remainder[i,rep,port]=(left,len(cells),rep*960+(2*pairs[i]+sides[i])*120+port);paid[left]+=1
 seen=set()
 for z in x['idle_children']:
  key=z['child'],z['replica'],z['port'];assert key not in seen;seen.add(key);assert z['replicas']==1 and z['copy']==120*z['replica']+z['port'];assert (z['rank'],z['pending_offset'],z['family'])==remainder[key]
 assert seen==set(remainder);assert paid==Counter({int(r):n for r,n in summary['global_profile'].items()});assert 73*7680-sum(r*n for r,n in paid.items())==2496
 return dict(profile=dict(sorted(paid.items())),actual_charts=len(sigmas),helper_roles=len(rolelist),invocations=len(calls),idle_remainders=len(remainder))
r=audit(t,hashes);mutants=[]
def reject(name,edit):
 x=copy.deepcopy(t);edit(x)
 try:audit(x,hashes)
 except (AssertionError,KeyError,IndexError,StopIteration):mutants.append(name)
 else:raise AssertionError('accepted '+name)
reject('wrong-middle-word',lambda x:x['calls'][32].__setitem__('variant','baseline'))
reject('wrong-program-digest',lambda x:x['calls'][0].__setitem__('local_program_sha256','bad'))
reject('aliased-helper-family',lambda x:x['calls'][0]['owners'][241].__setitem__(0,x['calls'][0]['owners'][240][0]))
reject('missing-call',lambda x:x['calls'].pop())
reject('missing-residual-role',lambda x:x['hosting']['pooled_slots'].pop())
reject('remainder-charge-missing',lambda x:x['idle_children'].pop())
reject('wrong-remainder-offset',lambda x:x['idle_children'][0].__setitem__('pending_offset',999))
reject('missing-bridge',lambda x:x['execution_schedule'].pop(next(i for i,e in enumerate(x['execution_schedule']) if e['kind']=='bridge')))
reject('wrong-variant-scalar',lambda x:x['local_variants']['middle']['programs']['forward'].pop())
reject('wrong-physical-reserve',lambda x:x.__setitem__('physical',8257))
r.update(status='PASS_INDEPENDENT_MIXED_WHOLE_OWNER_CHARTS_AND_PROFILE',template_sha256=summary['template_sha256'],mutations_rejected=mutants,scope='Exact finite program selection, owner injection, idle windows, orthogonal charts and paid profile. Local operator and full invoice checks are separate.')
(O/'AUDIT.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
