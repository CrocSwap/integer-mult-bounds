"""Literal width-swap/one-role owner search. Chi Zhao with substantial Codex assistance."""
import json,gzip,random,math,time,argparse,hashlib
from pathlib import Path
from collections import Counter,defaultdict
ap=argparse.ArgumentParser();ap.add_argument('--plan',required=True);ap.add_argument('--owners',required=True);ap.add_argument('--out',required=True);ap.add_argument('--seconds',type=float,default=120);ap.add_argument('--seed',type=int,default=13);a=ap.parse_args()
p=json.load(open(a.plan));rows=json.load(gzip.open(a.owners));rng=random.Random(a.seed);W=[4,5,7,8,9];q=.00164;V=[(r-r**(1-q))/q if r else 0 for r in range(49)]
keys=[];lookup={};cap=[];allow=[];bins=[];used=[];fam=[]
for key,(c,ts) in p['windows'].items():
 r,ch=map(int,key.split(','))
 for port in range(112):
  lookup[r,ch,port]=len(keys);keys.append((r,ch,port));cap.append(c);allow.append(sum(1<<t for t in ts));bins.append([]);used.append(0);fam.append(r*896+(2*p['pairs'][str(ch)]+p['sides'][str(ch)])*112+port)
# Different segments of a physical family have disjoint eligible time windows.
fm={}
for i,f in enumerate(fam):assert fm.get(f,0)&allow[i]==0;fm[f]=fm.get(f,0)|allow[i]
where=[];width=[];timebit=[];bywidth=defaultdict(list)
for i,row in enumerate(rows):
 b=lookup[row['owner_replica'],row['child'],row['port']];where.append(b);width.append(row['width']);tb=1<<row['time'];timebit.append(tb);assert not used[b]&tb;used[b]|=tb;bins[b].append(i);bywidth[width[-1]].append(i)
gap=[c-sum(width[i] for i in b) for c,b in zip(cap,bins)];assert min(gap)>=0
score=sum(V[g] for g in gap);initial=score;best=score;steps=0;strict=0;neutral=0;started=time.time();active=[]
def applyswap(i,j,bi,bj):
 global score,strict,neutral
 wi,wj=width[i],width[j];d=wj-wi;gi,gj=gap[bi],gap[bj]
 gain=V[gi-d]+V[gj+d]-V[gi]-V[gj]
 if gain < -1e-8:return
 ti,tj=timebit[i],timebit[j]
 if not (allow[bi]&tj and allow[bj]&ti):return
 if (used[bi]^ti)&tj or (used[bj]^tj)&ti:return
 bins[bi].remove(i);bins[bj].remove(j);bins[bi].append(j);bins[bj].append(i);where[i],where[j]=bj,bi;used[bi]^=ti^tj;used[bj]^=ti^tj;gap[bi]-=d;gap[bj]+=d;score+=gain
 if gain>1e-8:strict+=1
 else:neutral+=1
while time.time()-started<a.seconds:
 if steps%10000==0:active=[b for b in range(len(bins)) if gap[b] and bins[b]]
 steps+=1
 if not active:break
 bi=rng.choice(active);gi=gap[bi]
 if not gi or not bins[bi]:continue
 # Move an entire role into sufficiently large slack, usually consolidating.
 if gi>=4 and rng.random()<.25:
  valid=[w for w in W if w<=gi];w=rng.choice(valid);i=rng.choice(bywidth[w]);bj=where[i]
  if bj==bi:continue
  ti=timebit[i]
  if not allow[bi]&ti or used[bi]&ti:continue
  gain=V[gi-w]+V[gap[bj]+w]-V[gi]-V[gap[bj]]
  if gain< -1e-8:continue
  bins[bj].remove(i);bins[bi].append(i);where[i]=bi;used[bj]^=ti;used[bi]|=ti;gap[bi]-=w;gap[bj]+=w;score+=gain
  if gain>1e-8:strict+=1
  else:neutral+=1
 else:
  i=rng.choice(bins[bi]);wi=width[i];valid=[w for w in W if wi<w<=wi+gi]
  if not valid:continue
  wj=rng.choice(valid);j=rng.choice(bywidth[wj]);bj=where[j]
  if bi==bj:continue
  applyswap(i,j,bi,bj)
 if steps%100000==0:print('progress',steps,round(time.time()-started,1),score-initial,strict,neutral,flush=True)
print('done',steps,'gain',score-initial,'strict',strict,'neutral',neutral,flush=True)
rem=Counter(g for g in gap if g);prof=Counter()
for call in p['provider_calls']:prof.update({int(r):n for r,n in p['provider_registry'][call['provider']]['actual_paid_profile'].items()})
prof.update(rem);assert sum(r*n for r,n in prof.items())==520704
seen=defaultdict(set)
for b,items in enumerate(bins):
 offset=0;r,ch,port=keys[b]
 for i in sorted(items,key=lambda i:(rows[i]['time'],rows[i]['helper'])):
  row=rows[i];t=row['time'];assert allow[b]>>t&1 and fam[b] not in seen[t];seen[t].add(fam[b]);row.update(owner_replica=r,child=ch,port=port,copy=r*112+port,family=fam[b],offset=offset);offset+=width[i]
 assert offset<=cap[b]
rows.sort(key=lambda x:(x['time'],x['helper']));assert len({(r['time'],r['helper']) for r in rows})==35424
packed=gzip.compress(json.dumps(rows,sort_keys=True,separators=(',',':')).encode(),mtime=0);packed=packed[:9]+b'\xff'+packed[10:];out=Path(a.out);out.mkdir(parents=True,exist_ok=True);(out/'OWNERS.json.gz').write_bytes(packed)
p['profile']={str(r):n for r,n in sorted(prof.items())};p['assignment_sha256']=hashlib.sha256(packed).hexdigest();(out/'PROVISIONAL-PLAN.json').write_text(json.dumps(p,indent=2)+'\n')
lo,hi=0,.01
for _ in range(70):
 z=(lo+hi)/2
 if sum(r*n*math.expm1(z*math.log(73/r)) for r,n in prof.items())<2560:lo=z
 else:hi=z
res={'idle_profile':dict(sorted(rem.items())),'profile':dict(sorted(prof.items())),'numerical_complex':lo,'numerical_kappa':lo/(1+lo),'objective_gain':score-initial,'moves':strict,'neutral_moves':neutral,'seed':a.seed,'seconds':time.time()-started,'provider_bindings_pending':p.get('provider_bindings_pending',False)};(out/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res),flush=True)
