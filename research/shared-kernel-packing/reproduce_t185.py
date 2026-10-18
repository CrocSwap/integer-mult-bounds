# SPDX-License-Identifier: Apache-2.0
"""Exact majorization screen on PR2857's actual rebuilt owner fill."""
from pathlib import Path
from collections import Counter,defaultdict
import json,gzip,hashlib,math,time
import argparse
cli=argparse.ArgumentParser();cli.add_argument('--baseline',type=Path,required=True);cli.add_argument('--relay-plan',type=Path,required=True);cli.add_argument('--out',type=Path,required=True);args=cli.parse_args()
R=Path(__file__).resolve().parent;S=args.baseline
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
FIXED={'CLAIM.json': 'c2a04b639c86f462caef654a29817545c57b8e5ba809e37d4d476d3577f5cd6f', 'DISPATCH.json': '5513481a70c83767b5836b15fb7ff204d2a8f8fca83c6bcaee90a20b3d1ec6c4', 'FILL.json.gz': '82218aaaf08825bd4a3cca676815c7e9c00d06d0da123b1c5ad234c8c91cb501', 'ORDER.json': '84f030a59dde4fa4635988ef0931ebae66964b3a202df79d38247fbe8a5592dc', 'PROFILE.json': 'f5d91190e5a062585a99c3959615b837271feca987eed04ae7d707d5714b17aa', 'PROVIDERS.json': 'b1e31d1b3af2c8db9b8dd8f1337fee7fc2570ee58c1d541c43963c640efa1aa2'}
for name,pin in FIXED.items():assert sha(S/name)==pin,'immutable PR2857 source '+name
paths=[S/n for n in ['FILL.json.gz','ORDER.json','DISPATCH.json','PROVIDERS.json','PROFILE.json','CLAIM.json']]
def fixture(name):return S/name if(S/name).exists()else S/'sources'/name
templatepath=fixture('PR2833-T37-TEMPLATE.json.gz');planpath=fixture('PR2833-PLAN.json.gz')
assert sha(templatepath)=='21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e'
assert hashlib.sha256(gzip.decompress(planpath.read_bytes())).hexdigest()=='163431bf8d3bc0d9b894994b1a3cfa7947367b2243b3c0b3a97d740195a1cb08'
paths += [templatepath,planpath];pins={p.name:sha(p)for p in paths}
order=rd(paths[1]);dispatch={(s,r):p for s,r,p in rd(paths[2])};providers=rd(paths[3]);fill=rd(paths[0]);rows=fill['rows'];template=rd(templatepath);plan=rd(planpath);T=37;assert len(order)==9*T
copies=5
old_order=order;old_dispatch=dispatch;old_rows=rows
order=[(s,r+37*b)for s,r in old_order for b in range(copies)]
dispatch={(s,r+37*b):p for(s,r),p in old_dispatch.items()for b in range(copies)}
rows=[[copies*t+b,h,o+37*b,c,p,z]for t,h,o,c,p,z in old_rows for b in range(copies)];T=37*copies
fill['rows']=rows
caps={e['child']:e['rank']for e in template['idle_children']};bins=defaultdict(list);calls=defaultdict(list)
def width(i):return providers[dispatch[tuple(order[rows[i][0]])]]['widths'][rows[i][1]]
for i,row in enumerate(rows):bins[tuple(row[2:5])].append(i);calls[row[0]].append(i)
used={key:sum(width(i)for i in indices)for key,indices in bins.items()};rem={key:caps[key[1]]-n for key,n in used.items()}
power=1-.0017193776586975867;cost=lambda r:r**power if r else 0

def best_swap():
 best=None
 for t,indices in calls.items():
  groups=defaultdict(list)
  for i in indices:groups[width(i),rem[tuple(rows[i][2:5])]].append(i)
  for(w1,r1),a in groups.items():
   for(w2,r2),b in groups.items():
    d=w1-w2
    if d<=0 or r2<d or max(r1+d,r2-d)<=max(r1,r2):continue
    pair=next(((i,j)for i in a for j in b if rows[i][2:5]!=rows[j][2:5]),None)
    if pair is None:continue
    delta=cost(r1+d)+cost(r2-d)-cost(r1)-cost(r2)
    if best is None or delta<best[0]:best=(delta,pair[0],pair[1],r1,r2,w1,w2)
 return best
# Expand the actual source chronology, including all bridges.
blocks={};stage=None;tail=[]
for ix,e in enumerate(template['execution_schedule']):
 if e['kind']in('bank_padding_cover_sweep','translate_every_live_family'):tail.append(ix);continue
 if e['kind']=='local_cover_sweep':stage=e['stage'];blocks[stage]=[]
 assert stage is not None;blocks[stage].append((ix,e))
assert tail==[30,31]
pair={e['stage']:e['pair']for e in template['recipe']if e['kind']=='local'};last={};windows={};clock=0;callclock=[];projection=defaultdict(list)
for t,(stage,rep)in enumerate(order):
 for ix,e in blocks[stage]:
  projection[rep].append(ix)
  if e['kind']=='local_cover_sweep':last[rep,pair[stage]]=clock;callclock.append(clock)
  elif e['kind']=='bridge':last[rep,e['src']]=last[rep,e['dst']]=clock
  elif e['kind']=='idle_cover_sweep':
   for ch in e['child_indices']:
    if ch in caps:windows[rep,ch]=(last.get((rep,e['pair']),-1),clock)
  clock+=1
assert len(callclock)==len(order) and len(projection)==T and all(x==list(range(30))for x in projection.values())
# Concentrate actual cold residues, preserving all original helper identifiers and call times.
from itertools import permutations
family=lambda k:k[0]*896+(2*plan['pairs'][str(k[1])]+plan['sides'][str(k[1])])*112+k[2]
familysets={t:{family(tuple(rows[i][2:5]))for i in ii}for t,ii in calls.items()}
def eligible(i,k):
 lo,hi=windows[k[:2]];return lo<callclock[rows[i][0]]<hi and family(k)not in familysets[rows[i][0]]
moves=[]
def relocate(i,kb,kind):
 before=rows[i][:];ka=tuple(before[2:5]);off=used[kb];w=width(i);assert eligible(i,kb),'strict relay window or family';assert off+w<=caps[kb[1]]
 rows[i][2:]=[*kb,off];bins[ka].remove(i);bins[kb].append(i);used[ka]-=w;used[kb]+=w;rem[ka]+=w;rem[kb]-=w
 familysets[rows[i][0]].remove(family(ka));familysets[rows[i][0]].add(family(kb))
 # Recompact the source immediately, preserving a used prefix after every move.
 off=0
 for j in sorted(bins[ka],key=lambda j:rows[j][5]):rows[j][5]=off;off+=width(j)
 moves.append(dict(kind=kind,before=[before],after=[rows[i][:]],source=list(ka),destination=list(kb)))
index={(r[0],r[1]):i for i,r in enumerate(rows)}
if copies>2:
 relay=rd(args.relay_plan)
 for move in relay['relay']:
  for b in range(copies):
   t,h,o,c,p,z=move['row'];kb=list(move['destination']);kb[0]+=37*b;relocate(index[copies*t+b,h],tuple(kb),'histogram-neutral width9 vacancy relay')
exception=[k for k in bins if caps[k[1]]==16 and rem[k]==9]
assert len(exception)==copies and all(len(bins[k])==1 and width(bins[k][0])==7 for k in exception)
choice=None
if copies==2:
 ka,kb=exception;i=bins[ka][0];assert eligible(i,kb);selection=[(i,kb)]
else:
 donorcap=32 if copies==3 else 48;donorrem=5 if copies==3 else 3
 for ka,ii in bins.items():
  if caps[ka[1]]!=donorcap or rem[ka]!=donorrem or len(ii)!=copies or any(width(i)!=9 for i in ii):continue
  for dests in permutations(exception):
   if all(eligible(i,k)for i,k in zip(ii,dests)):choice=list(zip(ii,dests));break
  if choice:break
 assert choice is not None,'no eligible actual whole-role donor';selection=choice
for i,kb in selection:relocate(i,kb,'whole-role residue concentration')
for k in list(bins):
 off=0
 for i in sorted(bins[k],key=lambda z:rows[z][5]):rows[i][5]=off;off+=width(i)
 used[k]=off;rem[k]=caps[k[1]]-off
print('ACTUAL_RESIDUE_TRANSFERS',copies,len(moves),flush=True)
def audit(data):
 masks={};helpers=[0]*len(order);families=[set()for _ in order]
 for row in data:
  assert len(row)==6 and all(type(z)is int for z in row),'integer row'
  t,h,o,c,p,z=row;assert 0<=t<len(order)and 0<=h<408 and 0<=o<T and 0<=p<112 and z>=0,'range'
  w=providers[dispatch[tuple(order[t])]]['widths'][h];lo,hi=windows[o,c];assert lo<callclock[t]<hi,'source window'
  fam=o*896+(2*plan['pairs'][str(c)]+plan['sides'][str(c)])*112+p
  assert fam not in families[t],'family collision';families[t].add(fam)
  assert not helpers[t]>>h&1,'duplicate helper';helpers[t]|=1<<h
  key=o,c,p;bits=((1<<w)-1)<<z;assert z+w<=caps[c],'capacity';assert not masks.get(key,0)&bits,'mask overlap';masks[key]=masks.get(key,0)|bits
 assert len(data)==408*len(order)and all(x==(1<<408)-1 for x in helpers),'complete helpers'
 idle=Counter()
 for o in range(T):
  for c,cap in caps.items():
   for p in range(112):
    mask=masks.get((o,c,p),0);assert not mask&(mask+1),'used prefix';r=cap-mask.bit_count()
    if r:idle[r]+=1
 H=Counter(idle)
 for call in order:H.update({int(k):v for k,v in providers[dispatch[tuple(call)]]['actual_paid_profile'].items()})
 assert sum(k*v for k,v in H.items())==65088*T,'rank mass'
 return dict(sorted(H.items())),dict(sorted(idle.items()))
H,idle=audit(rows);oldH={int(k):copies*v for k,v in rd(S/'PROFILE.json').items()};deltaH=Counter(H);deltaH.subtract(oldH);deltaH={k:v for k,v in deltaH.items()if v}
controls=[]
def reject(name,fn,reason):
 a=[row[:]for row in rows];fn(a)
 try:audit(a)
 except AssertionError as e:assert str(e)==reason,(name,str(e));controls.append(dict(name=name,reason=reason))
 else:raise ValueError('accepted mutant '+name)
reject('missing_last_helper',lambda a:a.pop(),'complete helpers')
reject('noninteger_call_time',lambda a:a[0].__setitem__(0,.5),'integer row')
reject('capacity_overflow',lambda a:a[0].__setitem__(5,100),'capacity')
# Copy a full role onto another role at the same call; physical-family duplication must fail.
first=next(t for t in calls if len(calls[t])>1);i,j=calls[first][:2]
reject('duplicate_physical_family',lambda a:a[j].__setitem__(slice(2,5),a[i][2:5]),'family collision')
out=args.out;assert not out.exists();out.mkdir()
fill['rows']=rows
objects={'FILL.json.gz':fill,'ORDER.json':order,'DISPATCH.json':[[s,r,p]for(s,r),p in sorted(dispatch.items())],'PROVIDERS.json':providers,'PROFILE.json':H}
for name,obj in objects.items():
 p=out/name;lock=p.with_suffix(p.suffix+'.lock')
 with lock.open('x')as h:
  h.write('Exclusive literal same-call improvement\n');h.flush();b=json.dumps(obj,sort_keys=True,separators=(',',':')).encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
 lock.unlink()
result=dict(status='PASS_LITERAL_PR2857_RESIDUE_CONCENTRATION',replicas=T,live=896*T,physical=896*T+490,roles=len(rows),calls=len(order),moves=moves,profile=H,idle=idle,profile_delta=deltaH,rank_mass=sum(k*v for k,v in H.items()),controls=controls,input_sha256=pins,candidate_sha256={n:sha(out/n)for n in objects},scope='Actual full owner/source-event/family/mask/profile validation and actual copied chronology, unchanged native providers, complete owner/source/family/mask/profile recount; exact moment and full release separate. Exact moment and full native/admission separate.')
p=out/'OWNER-RECEIPT.json';lock=p.with_suffix('.json.lock')
with lock.open('x')as h:h.write('Exclusive full owner receipt\n');h.flush();p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
lock.unlink();assert pins=={p.name:sha(p)for p in paths}
print(json.dumps({k:result[k]for k in ['status','profile','profile_delta','candidate_sha256']}),flush=True)
