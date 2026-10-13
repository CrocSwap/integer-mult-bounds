"""Choose kernel witnesses by their complete pooled moment, with exact local replay and cached exact frames."""
from pathlib import Path
from collections import Counter
import json,sys,math,random,types,hashlib
r=Path.cwd();prefix=(r/'search_r715_intersection_kernel.py').read_text().split('\nfor penalty in [',1)[0].replace("out=r/'r715-intersection-kernel-search'","out=r/'r715-full-pooled-search'");exec(prefix)
# Reuse exact frame computations only in this discovery process. Pinned source files stay unchanged.
def cached_lat(lines):
 assert [tuple(row) for row in lines]==L.lines
 return L
kernel.__globals__['Lat']=cached_lat
sys.path[:0]=[str(r/'complex447-search'),str(r/'source450-review/code')]
import hosting_core as HC
HK=types.ModuleType('cached_hosting');HK.__file__=str(r/'source450-review/code/hosting_k.py');exec(Path(HK.__file__).read_text().replace('options=dict(time_limit=time_limit, disp=False)','options=dict(time_limit=time_limit, mip_rel_gap=1e-11, disp=False)'),HK.__dict__)
K=5;T=8;m=78;stages=11;R=w['R'];W=240*K*T;current=1295598840660602111119/10**24
HK.cost=lambda rr,mm:rr*math.expm1(current*math.log(mm/rr))/current if rr else 0
ns={};txt=(r/'screen_whole454_complex.py').read_text();exec(('def schedule(K):'+txt.split('def schedule(K):',1)[1].split('\nfor L,T in',1)[0]).replace('rank=8*','rank=7*'),ns);sc=ns['schedule'](K);win={i:x for i,x in HC.windows(sc).items() if x[1] and x[2]}
cache={};best=None;ledger=[]
def assess(entries,label):
 global best
 word,ne,nr,nd=kernel(w,entries);wm=E.to_masks(word,L);a=E.replay(word,L=L,masks=wm,span_mode='z');assert not a['viol']
 widths=[8-L.dim(wm[f]) for f in word['start'][240:]];counts=Counter(widths);key=tuple(sorted(counts.items()))
 if key not in cache:
  y,z,_=HK.solve(win,240*T,{(s,width):n*T for s in range(stages) for width,n in counts.items()},m,host_all=True,maxk=max(x[1] for x in win.values())//min(widths),time_limit=120)
  slots,rem=HC.expand(win,y,z,{s:[(i,widths[i%R]) for i in range(R*T)] for s in range(stages)},240*T);assert len(slots)==R*T*stages
  idle=Counter()
  for e in sc:
   if e['kind']=='idle':
    for cp in range(240*T):
     k=rem[e['idx'],cp] if e['idx'] in win else e['rank']
     if k:idle[k]+=1
  cache[key]=(y,z,idle)
 y,z,idle=cache[key];P=Counter({k:n*stages*T for k,n in a['H'].items()});P.update(idle);deficit=m*W-sum(k*n for k,n in P.items());assert deficit==408*T
 F=32*m*m*sum(P.values());lo=0.;hi=.01
 for _ in range(65):
  c=(lo+hi)/2;value=sum(n*k*math.expm1(c*math.log(m/k)) for k,n in P.items())+1e-16*F*math.exp(c*math.log(m))-deficit
  if value>0:hi=c
  else:lo=c
 record=dict(label=label,entries=ne,entrance_rank=nr,donors=nd,root_float=lo,widths=dict(counts),local_profile=dict(a['H']),pooled_profile=dict(P),status='PASS_EXACT_LOCAL_FLOAT_GLOBAL_RANKING_ONLY');ledger.append(record)
 if best is None or lo>best['root_float']+1e-15:
  cert=E.moment.certify(P,m,W,True);from fractions import Fraction as Q
  low,upper=Q(cert['lower']),Q(cert['upper'])
  for x,below in [(low,True),(upper,False)]:
   aa,bb=E.other.moment(m,W,list(P.items()),x);cc,dd=E.other.moment(m,W,[(1,F)],x);assert bb+dd/10**16<1 if below else aa+cc/10**16>1
  best=dict(record,bit_lower=str(low),projected_kappa=float(low/(1+low)),scope='Exact local and moments only; physical replay, fresh invoice and final assembly pending')
  dest=out/('best-'+str(len(ledger)));dest.mkdir();(dest/'WORD.json').write_text(json.dumps(word,sort_keys=True,separators=(',',':')));(dest/'SELECTION.json').write_text(json.dumps(dict(entries=entries,entrance_rank=nr,donors=nd),indent=2)+'\n');HC.save_selection(dest/'HOSTING.json','bit',y,z,0);best['path']=str(dest);(dest/'RESULT.json').write_text(json.dumps(best,indent=2)+'\n');(out/'BEST.json').write_text(json.dumps(best,indent=2)+'\n');print('NEW BEST',label,ne,nr,nd,best['projected_kappa'],flush=True)
 (out/'LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n')
assess(json.loads((r/'source472-review/data/kernel.json').read_text()),'PR472 baseline')
assert best['bit_lower']=='1295598840660602111119/1000000000000000000000000'
limit=int(sys.argv[1]) if len(sys.argv)>1 else 100
for trial in range(limit):
 penalty=[0.,0.2,0.4,0.65,1.0][trial%5];cost=lambda rank:rank*math.log(78/rank)+penalty*rank if rank else 0
 ctx['os'].environ['PNOISE']=str([0.,.03,.1,.3][trial%4]);ctx['_R']=random.Random(9001+trial);rng=random.Random(117+trial)
 availp=set(eligible);availd=set(eligible);donorat={};chosen=[];plans={};fac={mask:1+[.1,.4,.8][trial%3]*rng.random() for mask in groups}
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
 entries=[[[i for i in range(v) if mask>>i&1],h,ds] for mask,h,ds in chosen]
 try:assess(entries,dict(trial=trial,penalty=penalty,donor_noise=ctx['os'].environ['PNOISE']))
 except Exception as exc:
  ledger.append(dict(label=dict(trial=trial,penalty=penalty),status='FAILED_CANDIDATE',error=repr(exc)));(out/'LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n');print('FAILED',trial,repr(exc),flush=True)
 if trial%10==9:print('PROGRESS',trial+1,'hosting inventories',len(cache),'best',best['projected_kappa'],flush=True)
(out/'COMPLETE.json').write_text(json.dumps(dict(status='FINISHED_FINITE_FULL_POOLED_SEARCH',trials=limit,records=len(ledger),hosting_inventories=len(cache),best=best),indent=2)+'\n');print('FINISHED',limit,flush=True)
