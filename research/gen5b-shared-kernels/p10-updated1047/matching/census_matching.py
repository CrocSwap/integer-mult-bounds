"""Original complete dimension-path census for two bounded matching witnesses."""
from pathlib import Path
from collections import Counter,defaultdict
import sys,json,gzip,hashlib
CODE=Path(__file__).resolve().parent;sys.path.insert(0,str(CODE.parent));import support
P=support.OUTPUT
w=support.read('bitword/selected/bit/word_p10.json.gz');G=support.read('bitword/selected/bit/graph_p10.json');K=support.read('bitword/selected/bit/kchron_p10.json');F=support.read('bitword/selected/bit/frames_p10.json.gz')['frames']
dim=lambda f:F[str(f)]['dim']
def clean(c):return {r:n for r,n in sorted(c.items())if n}
def difference(a,b):
 c=Counter(b);c.subtract(a);return clean(c)
def census(w):
 gauges={x['role']:x for x in w['gauges']};source={r:int(s)for s,r in w['sources'].items()};pairs=dict(w['pairs']);roles=sorted(set(range(9120))-set(pairs.values()));uses=defaultdict(list);roots=defaultdict(list);phase=sorted(w['phase1']);ps=set(phase);order=phase+[i for i in range(len(w['ops']))if i not in ps]
 for i in order:
  for r in w['ops'][i][:2]:uses[r].append(w['op_frame'][i])
 for r,f in zip(w['rootroles'],w['root_frame']):roots[r].append(f)
 def price(ds):
  c=Counter()
  for a,b in zip(ds,ds[1:]):
   assert a<=b,(a,b,ds)
   if a<b:c[b-a]+=1
  return c
 internal=Counter();residual=Counter();firstdims={};trails={}
 for r in roles:
  start=dim(gauges[r]['frame'])if r in gauges else dim(w['source_frame'][source[r]])if r in source else 0
  fs=uses[r]+roots[r]
  if r in pairs:
   q=pairs[r];fs=fs+[gauges[q]['frame']]+uses[q]+roots[q]
  ds=[start]+[dim(f)for f in fs]+[20];internal.update(price(ds));firstdims[r]=dim(fs[0]);trails[r]=ds
  if r in source:internal[1]+=1
  residual[20-(dim(gauges[r]['frame'])if r in gauges else 0)]+=1
 for j,r in enumerate(G['roots']):
  if r['kind']=='center':internal[dim(w['root_frame'][j])]+=1
 src=Counter()
 for e in K['entries']:
  for key in ['carrier_chain','passive_chain']:src.update(price([dim(f)for f in e[key]]))
 tp=[[0]for _ in range(960)]
 for _,e in sorted(enumerate(reversed(w['gauges'])),key=lambda x:(w['reads'].get(str(x[1]['role']),len(phase)),x[0])):
  for t in e['targets']:tp[t].append(dim(e['frame']))
 deliveries=defaultdict(list)
 for e in K['entries']:deliveries[e['deliver_after_root']].append(e)
 for j,r in enumerate(G['roots']):
  if r['kind']=='side':
   for t in r['targets']:tp[t].append(dim(w['root_frame'][j]))
  for e in deliveries[j]:
   for t in e['receivers']:tp[t].append(dim(e['deliver_frame']))
 target=Counter()
 for path in tp:target.update(price(path+[19]))
 helper=internal+src+target
 return dict(internal=clean(internal),source=clean(src),target=clean(target),helper=clean(helper),mass=sum(r*n for r,n in helper.items()),residual=clean(residual),residual_mass=sum(r*n for r,n in residual.items()),roles=roles,firstdims=firstdims,trails=trails)
old=census(w);assert old['mass']==181050
old_roles=old['roles'];stream={1920+i:r for i,r in enumerate(old_roles)};entries=support.read('kernel-selection.json')['families'];piv={stream[e['pivot']]:e['rank']for e in entries};visits=defaultdict(set)
for e in entries:
 for s in [e['pivot']]+e['donors']:visits[stream[s]].add(e['rank'])
def kernel_delta(c):
 out=Counter()
 for r,ds in visits.items():
  first=c['firstdims'][r];out[first]-=1;prev=piv.get(r,0)
  for d in sorted(ds)+[first]:
   assert prev<=d
   if d>prev:out[d-prev]+=1
   prev=d
 return clean(out)
oldkd=kernel_delta(old);assert oldkd=={int(k):n for k,n in support.read('kernel-selection.json')['expected_local_delta'].items()}
reports={}
for name in ['weighted890']:
 raw=(P/'matching'/('word_'+name+'.json')).read_bytes();new=census(json.loads(raw));kd=kernel_delta(new);assert kd==oldkd
 hd=difference(old['helper'],new['helper']);rd=difference(old['residual'],new['residual']);assert sum(r*n for r,n in hd.items())==sum(r*n for r,n in rd.items())==0
 assert old['source']==new['source']and old['target']==new['target']
 members={stream[s]for e in entries for s in[e['pivot']]+e['donors']};changed={r for p in set(map(tuple,w['pairs']))^set(map(tuple,json.loads(raw)['pairs']))for r in p}
 reports[name]=dict(label=name+' on1047kernelbaseline',histogram_delta=hd,residual_delta=rd,old_helper=old['helper'],new_helper=new['helper'],old_mass=old['mass'],new_mass=new['mass'],kernel_delta=kd,kernel_delta_unchanged=True,affected_kernel_entries=sum(bool({stream[s]for s in[e['pivot']]+e['donors']}&changed)for e in entries),changed_roles=len(changed),changed_first_dimensions={r:[old['firstdims'].get(r),new['firstdims'].get(r)]for r in members if old['firstdims'].get(r)!=new['firstdims'].get(r)},source_target_histograms_unchanged=True,candidate_sha256=hashlib.sha256(raw).hexdigest(),scope='Full dimension paths and kernel rank-chain delta only; exact spaces, cuts, scalar chronology, charts and finite admission separate.')
 (P/'matching'/(name+'-delta.json')).write_text(json.dumps(reports[name],indent=2)+'\n')
print(json.dumps({name:{k:v for k,v in r.items()if k not in ['old_helper','new_helper','kernel_delta']}for name,r in reports.items()},indent=2))
