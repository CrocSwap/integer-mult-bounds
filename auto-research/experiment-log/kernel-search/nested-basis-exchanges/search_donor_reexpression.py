"""Fixed-pivot donor reexpression with exact response relations and nested frame chains.
Discovery proxy only; each retained endpoint gets independent full local replay.
"""
from pathlib import Path
import random,time
r=Path.cwd();src=(r/'compose_pr485_promotions.py').read_text().split('\ntry:',1)[0].replace('pr485-promoted-composition','r715-donor-reexpression');exec(compile(src,'pinned_composition_setup','exec'))
# All first-frame intersections, closed over rational root-spanned flats.
firstsets=sorted(set(maskfirst.values()));candidates=set(firstsets);front=set(firstsets)
while front:
 fresh={aa&bb for aa in front for bb in firstsets if aa&bb}-candidates;candidates.update(fresh);front=fresh
candidates={e for e in candidates if 0<L.dim(e)<8};print('FRAME CANDIDATES',len(candidates),flush=True)
seeds=[('current110',json.loads((r/'source483-review/bit470/data/kernel-selection.json').read_text())['entries']),('promoted112',json.loads((r/'pr485-promoted-composition/promoted-0/SELECTION.json').read_text())['entries'])]
trials=[]
def asmask(lines):return sum(1<<i for i in lines)
for seedname,original in seeds:
 emit(original,seedname+'-baseline',[])
 if seedname=='current110':assert ledger[-1]['profile']=={int(k):v for k,v in json.loads((r/'pr483-local-exact.json').read_text())['profile'].items()},'pipeline baseline profile drift'
 for trial,penalty in enumerate([0.,.2,.5,1.]):
  rng=random.Random(485000+trial+(100 if seedname=='current110' else 0));chosen=copy.deepcopy(original);pivs={p for ee,p,ds in chosen};eligible=[h for h in first if h not in pivs and h not in w['ret']];moves=[];tested=0;represented=0;started=time.monotonic()
  cost=lambda k:k*math.log(78/k)+penalty*k if k else 0
  def chain_cost(h,frames):
   seq=[0]+sorted(frames,key=L.dim)+[maskfirst[h]]
   assert all(a&~b==0 for a,b in zip(seq,seq[1:]))
   return sum(cost(L.dim(b)-L.dim(a)) for a,b in zip(seq,seq[1:]))
  for sweep in range(30):
   bydonor={}
   for ix,(ee,p,ds) in enumerate(chosen):
    for d in ds:bydonor.setdefault(d,{}).setdefault(asmask(ee),set()).add(ix)
   best=None
   for ix,(ee,p,old_ds) in enumerate(chosen):
    old=asmask(ee);before={d:set(z) for d,z in bydonor.items()};without={d:{mask for mask,users in z.items() if users-{ix}} for d,z in bydonor.items()};old_donor_cost=sum(chain_cost(d,before[d])-chain_cost(d,without[d]) for d in old_ds)
    entrances=sorted(e for e in candidates if e&~maskfirst[p]==0 and old&~e==0)
    for entrance in entrances:
     tested+=1;donors=[]
     for d in eligible:
      if entrance&~maskfirst[d]:continue
      chain=without.get(d,set())
      if any(entrance&other not in (entrance,other) for other in chain):continue
      delta=chain_cost(d,chain|{entrance})-chain_cost(d,chain)
      donors.append((delta,d))
     if not donors:continue
     # Different cost-biased bases can represent the same response with different donors.
     for attempt in range(3):
      order=sorted(donors,key=lambda z:(z[0]*(1+(0 if attempt==0 else .5)*rng.random()),z[1]))
      basis={}
      for delta,d in order:
       x=response[d];combo=1<<d
       while x:
        bit=x.bit_length()-1
        if bit in basis:row,cs=basis[bit];x^=row;combo^=cs
        else:basis[bit]=(x,combo);break
      x=response[p];combo=0
      while x:
       bit=x.bit_length()-1
       if bit not in basis:break
       row,cs=basis[bit];x^=row;combo^=cs
      if x:continue
      represented+=1;ds=[d for delta,d in donors if combo>>d&1];assert len(ds)==combo.bit_count();ds.sort()
      delta=cost(L.dim(maskfirst[p])-L.dim(entrance))-cost(L.dim(maskfirst[p])-L.dim(old))-old_donor_cost
      delta+=sum(chain_cost(d,without.get(d,set())|{entrance})-chain_cost(d,without.get(d,set())) for d in ds)
      if delta < -1e-9 and(best is None or delta<best[0]):best=(delta,ix,entrance,ds)
   if best is None:break
   delta,ix,entrance,ds=best;ee,p,previous_ds=chosen[ix];newlines=[i for i in range(v) if entrance>>i&1];moves.append(dict(pivot=p,old_frame=ee,new_frame=newlines,old_donors=previous_ds,new_donors=ds,proxy_delta=delta));chosen[ix]=[newlines,p,ds]
   print('MOVE',seedname,trial,sweep,'pivot',p,'rank',L.dim(entrance),'proxy',delta,flush=True)
  else:print('BOUND 30 MOVES REACHED',seedname,trial,flush=True)
  tag=seedname+'-'+str(trial);emit(chosen,tag,moves);record=dict(tag=tag,seed=485000+trial+(100 if seedname=='current110' else 0),penalty=penalty,attempts_per_basis=3,move_limit=30,moves=len(moves),entrance_proposals=tested,represented=represented,seconds=round(time.monotonic()-started,3));trials.append(record);(out/'SEARCH-LEDGER.json').write_text(json.dumps(trials,indent=2)+'\n');print('TRIAL COMPLETE',record,flush=True)
(out/'COMPLETE.json').write_text(json.dumps(dict(status='FINISHED_LOCAL_DONOR_REEXPRESSION',trials=trials,cases=len(ledger),scope='All endpoints locally replayed; global pricing/native/physical/full certificate separate'),indent=2)+'\n')
