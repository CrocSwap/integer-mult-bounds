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
from collections import deque
empty=[b for b in range(len(bins)) if cap[b]==32 and gap[b]==32]
full=[b for b in range(len(bins)) if cap[b]==32 and gap[b]==0]
parent={b:None for b in empty};queue=deque(empty)
while queue:
 dest=queue.popleft()
 for b in full:
  if b not in parent and not(used[b]&~allow[dest]):parent[b]=dest;queue.append(b)
print('reachable32',len(parent),'windows',len({allow[b] for b in parent}),flush=True)
byallow={}
for b in parent:byallow.setdefault(allow[b],[]).append(b)
def chain_nodes(d):
 while parent[d] is not None:
  yield d;d=parent[d]
 yield d
found=False;firstmoves=0;secondmoves=0;bestmass=0
empties=[b for b in range(len(bins)) if cap[b]==32 and not bins[b]]
for b0 in range(len(bins)):
 if gap[b0]!=4:continue
 for i0 in bins[b0]:
  for j1 in bywidth.get(width[i0]+4,[]):
   b1=where[j1]
   if b1==b0:continue
   t0,t1=timebit[i0],timebit[j1]
   if not(allow[b0]&t1 and allow[b1]&t0):continue
   if (used[b0]^t0)&t1 or (used[b1]^t1)&t0:continue
   firstmoves+=1;items1=[i for i in bins[b1] if i!=j1]+[i0];used1=used[b1]^t0^t1
   for i1 in items1:
    for j2 in bywidth.get(width[i1]+4,[]):
     b2=where[j2]
     if b2 in (b0,b1) or cap[b2]!=48:continue
     ti,tj=timebit[i1],timebit[j2]
     if not(allow[b1]&tj and allow[b2]&ti):continue
     if (used1^ti)&tj or (used[b2]^tj)&ti:continue
     secondmoves+=1
     for mask, dests in byallow.items():
      dest=next((d for d in dests if d!=b1 and not any(x==b1 for x in chain_nodes(d))),None)
      if dest is None:continue
      candidates=[k for k in bins[b2] if k!=j2]+[i1];dp={0:[]}
      mass=sum(width[k] for k in candidates if allow[dest]&timebit[k]);bestmass=max(bestmass,mass)
      if mass<32:continue
      for k in candidates:
       if not allow[dest]&timebit[k]:continue
       for total,chosen in list(dp.items()):
        if total+width[k]<=32 and total+width[k] not in dp:dp[total+width[k]]=chosen+[k]
      transfer=next((x for x in range(32,28,-1) if x in dp),None)
      if transfer is None:continue
      chain=[];cur=dest
      while parent[cur] is not None:chain.append((cur,parent[cur]));cur=parent[cur]
      for frm,to in reversed(chain):
       bins[to]=bins[frm];bins[frm]=[];used[to]=used[frm];used[frm]=0;gap[to]=0;gap[frm]=32
       for k in bins[to]:where[k]=to
      applyswap(i0,j1,b0,b1);applyswap(i1,j2,b1,b2)
      for k in dp[transfer]:bins[b2].remove(k);bins[dest].append(k);where[k]=dest;used[b2]^=timebit[k];used[dest]|=timebit[k]
      gap[b2]=4+transfer;gap[dest]=32-transfer;score+=V[4+transfer]+V[32-transfer]-V[4]-V[32];strict+=1;found=True
      print('TWO STEP BUNDLE',{'bins':[keys[b0],keys[b1],keys[b2],keys[dest]],'swaps':[(rows[i0]['time'],rows[i0]['helper'],rows[j1]['time'],rows[j1]['helper']),(rows[i1]['time'],rows[i1]['helper'],rows[j2]['time'],rows[j2]['helper'])],'bundle':[(rows[k]['time'],rows[k]['helper'],width[k]) for k in dp[transfer]]},flush=True);break
     if found:break
    if found:break
   if found:break
  if found:break
 if found:break
print('scan',firstmoves,secondmoves,'best eligible rank',bestmass,flush=True)
if not found:raise SystemExit(2)
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
