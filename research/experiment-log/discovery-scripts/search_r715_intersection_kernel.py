"""Shared-donor group search from pinned PR417 on fresh PR463 word."""
from pathlib import Path
import ast,random,types
s=Path('search_r715_kernel.py').read_text();exec(s.split('for penalty in [')[0].replace("out=r/'r715-kernel-search'","out=r/'r715-intersection-kernel-search'").replace("source463-review/data/R715_FP_final.json.gz","r715-delivery-kernel-search/PRECURSOR.json.gz"))
source=(r/'source417-discovery/kernel.py').read_text();tree=ast.parse(source);funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('reduce_vec','plan_E')];ctx=dict(os=__import__('os'),_R=random.Random(17));exec(compile(ast.Module(body=funcs,type_ignores=[]),'pinned417_functions','exec'),ctx);plan=ctx['plan_E']
maskfirst={h:masks[f] for h,f in first.items()};eligible=[h for h in first if h not in w['ret']];firstsets=sorted(set(maskfirst[h] for h in eligible));candidates=set(firstsets)
for mask in firstsets:
 for i in range(v):
  if mask>>i&1:candidates.add(1<<i)
for i,aa in enumerate(firstsets):
 for bb in firstsets[i+1:]:
  if aa&bb:candidates.add(aa&bb)
# Intersections of closed flats are closed; enumerate the generated meet closure.
frontier=set(candidates)
while frontier:
 fresh={aa&bb for aa in frontier for bb in firstsets if aa&bb}-candidates
 print('INTERSECTION CLOSURE',len(candidates),'new',len(fresh),flush=True)
 candidates.update(fresh);frontier=fresh
candidates={L.close(x) for x in candidates};groups={mask:[h for h in eligible if mask&maskfirst[h]==mask] for mask in candidates if 0<L.dim(mask)<8};groups={mask:hs for mask,hs in groups.items() if len(hs)>1};print('EXPANDED FRAMES',len(groups),flush=True)

for penalty in [0.4,0.65,1.0]:
 cost=lambda rank:rank*math.log(78/rank)+penalty*rank if rank else 0
 rng=random.Random(117);best=None
 for trial in range(20):
  availp=set(eligible);availd=set(eligible);donorat={};chosen=[];plans={};noise=0 if trial==0 else .6;fac={mask:1+noise*rng.random() for mask in groups}
  def refresh(mask):plans[mask]=plan(mask,groups[mask],response,maskfirst,L.dim,cost,availp,availd,donorat)
  for mask in groups:refresh(mask)
  while True:
   live=[(p[0]*fac[mask],mask) for mask,p in plans.items() if p]
   if not live:break
   _,mask=max(live);gain,ents=plans[mask];touched=set()
   for h,ds in ents:
    chosen.append([mask,h,ds]);availp.discard(h);availd.discard(h);touched.add(h)
    for d in ds:donorat[d]=mask;availp.discard(d);availd.discard(d);touched.add(d)
   for ee in groups:
    if plans[ee] and (ee==mask or touched.intersection(groups[ee])):refresh(ee)
  value=0;seen=set()
  for mask,h,ds in chosen:
   er=L.dim(mask);fd=L.dim(maskfirst[h]);value+=cost(fd)-cost(fd-er)
   for d in ds:
    if d not in seen:
     fd=L.dim(maskfirst[d]);value-=cost(er)+cost(fd-er)-cost(fd);seen.add(d)
  if best is None or value>best[0]:best=(value,chosen);print('best',penalty,trial,'entries',len(chosen),'rank',sum(L.dim(e) for e,h,ds in chosen),'value',value,flush=True)
 chosen=best[1];entries=[[[i for i in range(v) if mask>>i&1],h,ds] for mask,h,ds in chosen];word,ne,nr,nd=kernel(w,entries);audit=E.replay(word,span_mode='z');assert not audit['viol'],audit['viol'][:5]
 tag=str(penalty).replace('-','neg').replace('.','p');wp=out/f'KERNEL-{tag}.json';wp.write_text(json.dumps(word,separators=(',',':')));(out/f'SELECTION-{tag}.json').write_text(json.dumps(dict(entries=entries,entrance_rank=nr,donors=nd,local_profile=dict(audit['H'])),indent=2)+'\n')
 # The precursor already retains the target mixing; do not apply it twice.
print('SHARED KERNEL LOCAL PASS',tag,ne,nr,nd,flush=True)
