"""Test nested donor entrances on the repaired R715 kernel; finite exact replay required."""
from pathlib import Path
import ast,random,types,copy,math,json,hashlib
r=Path.cwd();out=r/'r715-nested-donor-reselection';assert not out.exists();out.mkdir()
prefix=(r/'search_r715_intersection_kernel.py').read_text().split('\nfor penalty in [',1)[0].replace("out=r/'r715-intersection-kernel-search'","out=r/'r715-nested-donor-reselection'");exec(prefix)
# Pinned local kernel constructor is not changed; this experimental constructor permits nested donor frames.
def nested_kernel(word,entries):
 z=copy.deepcopy(word);frameids={sum(1<<j for j in frame):i for i,frame in enumerate(z['frames'])}
 def fid(mask):
  if mask not in frameids:frameids[mask]=len(z['frames']);z['frames'].append([i for i in range(v) if mask>>i&1])
  return frameids[mask]
 piv={};chains={};byd={}
 for lines,p,ds in entries:
  mask=sum(1<<i for i in lines);assert mask==L.close(mask) and mask and p not in piv and p not in chains and p not in z['ret']
  assert mask&~maskfirst[p]==0;x=response[p]
  for d in ds:
   assert d not in piv and d not in z['ret'] and mask&~maskfirst[d]==0
   x^=response[d];ch=chains.setdefault(d,set());assert all(mask&old in (mask,old) for old in ch);ch.add(mask);byd.setdefault((d,mask),[]).append(p)
  assert x==0;piv[p]=mask
 for p,mask in piv.items():z['start'][p]=fid(mask)
 z['D']=[[f,t,[s for s in ss if s not in piv]] for f,t,ss in z['D']]
 ordered=sorted(byd,key=lambda dm:(dm[0],L.dim(dm[1]),dm[1]))
 z['A']=[[fid(mask),d,sorted(byd[d,mask])] for d,mask in ordered]+z['A']
 full=(1<<v)-1;z['C']=z['C']+[[fid(full),d,sorted(byd[d,mask])] for d,mask in ordered]
 return z,piv,chains
# Keep all known entrance choices; allow a new pivot to reuse a donor at a nested entrance.
old=json.loads((r/'r715-warm-pooled-search/best-36/SELECTION.json').read_text())['entries']
import importlib.util
sp=importlib.util.spec_from_file_location('factor',r/'source478-review/code/schur_constructor.py');Factor=importlib.util.module_from_spec(sp);sp.loader.exec_module(Factor);factors=json.loads((r/'source478-review/code/SELECTION473.json').read_text())['selected']
# Preserve reference source hashes and exact baseline before any search.
base,_,_=nested_kernel(w,old);base,_=Factor.rewrite(base,factors);bm=E.to_masks(base,L);ba=E.replay(base,L=L,masks=bm,span_mode='z');assert not ba['viol'];assert base==json.loads((r/'pr472-delivery-publication/research/r715-factor-replica84/data/word.json').read_text())
print('BASELINE EXACT WORD MATCH',len(old),flush=True)
from fractions import Fraction as Q
current=float(Q(json.loads((r/'r715-factor-replica84-strong-RESULT.json').read_text())['bit_lower']))
for trial in range(20):
 penalty=[0.,.2,.5,1.][trial%4];fraction=[0.,.25,.5,.75,1.][trial//4];rng=random.Random(84000+trial)
 chosen=copy.deepcopy(rng.sample(old,round(len(old)*fraction)));piv={p for _,p,ds in chosen};chains={}
 for lines,p,ds in chosen:
  mask=sum(1<<i for i in lines)
  for d in ds:chains.setdefault(d,set()).add(mask)
 cost=lambda k:k*math.expm1(current*math.log(78/k))/current+penalty*k if k else 0
 def donor_cost(h,mask):
  ch=chains.get(h,set())
  if any(mask&old not in (mask,old) for old in ch):return None
  if mask in ch:return 0.
  path=[0]+sorted(ch,key=lambda t:L.dim(t))+[maskfirst[h]];dim=L.dim(mask)
  for a,b in zip(path,path[1:]):
   if mask&a==a and mask&b==mask:return cost(dim-L.dim(a))+cost(L.dim(b)-dim)-cost(L.dim(b)-L.dim(a))
  raise AssertionError('no compatible donor interval')
 def plan_nested(mask):
  group=[h for h in groups[mask] if h not in piv];e=L.dim(mask);members=[]
  for h in group:
   dc=donor_cost(h,mask);pg=cost(L.dim(maskfirst[h]))-cost(L.dim(maskfirst[h])-e) if h not in chains else None
   if dc is not None or pg is not None:members.append((h,dc,pg))
  members.sort(key=lambda t:(t[1] if t[1] is not None else float('inf'),t[2] if t[2] is not None else -1,t[0]))
  basis={};slots=[];possible=[]
  for h,dc,pg in members:
   rem,cm=ctx['reduce_vec'](response[h],basis)
   if not rem and pg is not None and pg>0:possible.append((h,cm,pg))
   elif rem and dc is not None:
    k=len(slots);slots.append((h,dc));basis[rem.bit_length()-1]=(rem,cm^(1<<k))
  if not possible:return None
  used={}
  for h,cm,pg in possible:
   for k in range(len(slots)):
    if cm>>k&1:used.setdefault(k,set()).add(h)
  keep=possible[:]
  while keep:
   drops=[]
   for i,(h,cm,pg) in enumerate(keep):
    freed=sum(slots[k][1] for k in used if cm>>k&1 and len(used[k])==1)
    if freed>pg:drops.append((freed-pg,i))
   if not drops:break
   _,i=max(drops);h,cm,pg=keep.pop(i)
   for k in list(used):
    if cm>>k&1:
     used[k].discard(h)
     if not used[k]:del used[k]
  gain=sum(pg for h,cm,pg in keep)-sum(slots[k][1] for k in used)
  return (gain,[(h,[slots[k][0] for k in range(len(slots)) if cm>>k&1]) for h,cm,pg in keep]) if gain>1e-10 else None
 plans={mask:plan_nested(mask) for mask in groups};moves=[]
 while any(plans.values()):
  gain,mask=max((z[0],mask) for mask,z in plans.items() if z);_,ents=plans[mask];touched=set()
  for h,ds in ents:
   chosen.append([[i for i in range(v) if mask>>i&1],h,ds]);piv.add(h);touched.add(h)
   for d in ds:chains.setdefault(d,set()).add(mask);touched.add(d)
  moves.append({'frame':mask,'gain':gain,'entries':ents})
  for other in plans:
   if touched.intersection(groups[other]):plans[other]=plan_nested(other)
 word,ps,chs=nested_kernel(w,chosen);word,_=Factor.rewrite(word,factors);mm=E.to_masks(word,L);audit=E.replay(word,L=L,masks=mm,span_mode='z');assert not audit['viol'];Factor.check(word,[L.dim(x) for x in mm])
 dest=out/('trial-'+str(trial));dest.mkdir();raw=json.dumps(word,sort_keys=True,separators=(',',':')).encode();(dest/'WORD.json').write_bytes(raw);(dest/'SELECTION.json').write_text(json.dumps({'entries':chosen},indent=2)+'\n')
 result=dict(status='PASS_EXACT_NESTED_DONOR_LOCAL_GLOBAL_PENDING',trial=trial,penalty=penalty,retained_fraction=fraction,seed=84000+trial,entries=len(ps),entrance_rank=sum(L.dim(e) for e in ps.values()),donors=len(chs),multi_entrance_donors=sum(len(ch)>1 for ch in chs.values()),profile=dict(audit['H']),baseline_profile=dict(ba['H']),word_sha256=hashlib.sha256(raw).hexdigest(),new_pivots=len(ps)-len(old),moves=moves,scope='Finite955-column/frame/integer-support replay only; signed formal native checks, global hosting, physical prefix and full composition pending. New nested donor mechanism is experimental.')
 (dest/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print('TRIAL',trial,'new',result['new_pivots'],'entrance rank',result['entrance_rank'],'multi',result['multi_entrance_donors'],'profile',result['profile'],flush=True)
