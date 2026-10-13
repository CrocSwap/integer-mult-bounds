"""Fresh coordinate-response kernel nominations on PR463; exact local replay required."""
from pathlib import Path
from collections import Counter
import sys,json,gzip,math,subprocess,ast,random,types
r=Path.cwd();out=r/'r714-kernel-transfer-pooled';out.mkdir(exist_ok=True)
sys.path[:0]=[str(r/'source454-review/e8-r740-replica32/code'),str(r/'source454-review/r740-hosted-rank149/code')]
import e8core as E
from hosted_kernel import kernel
w=E.load_word(str(r/'r714-precursor-check/PRECURSOR.json.gz'));L=E.Lat(w['lines']);masks=E.to_masks(w,L);dims=[L.dim(f) for f in masks]
a=E.replay(w,L=L,masks=masks,span_mode='z');assert not a['viol'],a['viol'][:5]
(out/'BASE-LOCAL.json').write_text(json.dumps(dict(profile=dict(a['H']),dims=dims,columns=a['n']),indent=2)+'\n');print('BASE PASS',a['n'],dict(a['H']),flush=True)
first={};response=Counter();v=w['v'];R=w['R']
for f,d,ss in w['D']:
 for h in ss:response[h]^=1<<(d-v)
for ph in ('A','B','C'):
 for f,d,ss in w[ph]:
  for h in [d]+ss:
   if h>=2*v and masks[f]:first.setdefault(h,f)
frames=[]
for fi,mask in enumerate(masks):
 axes={j for i in w['frames'][fi] for j,x in enumerate(w['lines'][i]) if x}
 if 0<dims[fi]<w['h'] and len(axes)==dims[fi]:frames.append(fi)

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
assess(json.loads((r/'r714-kernel-transfer/SELECTION.json').read_text())['entries'], 'R715 warm kernel transferred by checked response and state signatures')

limit=int(sys.argv[1]) if len(sys.argv)>1 else 100
for trial in range(limit):
 penalty=[0.,0.2,0.4,0.65,1.0][trial%5];cost=lambda rank:rank*math.log(78/rank)+penalty*rank if rank else 0
 ctx['os'].environ['PNOISE']=str([0.,.03,.1,.3][trial%4]);ctx['_R']=random.Random(715001+trial);rng=random.Random(715117+trial)
 availp=set(eligible);availd=set(eligible);donorat={};chosen=[];plans={};fac={mask:1+[.1,.4,.8][trial%3]*rng.random() for mask in groups}
 # Keep part of the best known witness and reconstruct the removed entrance groups.
 incumbent=json.loads((Path(best['path'])/'SELECTION.json').read_text())['entries'] if best else []
 entrance_groups=sorted({sum(1<<i for i in ee) for ee,h,ds in incumbent})
 remove_count=min(len(entrance_groups),max(1,math.ceil(len(entrance_groups)*[.15,.3,.5,.75][trial%4])))
 removed=set(rng.sample(entrance_groups,remove_count))
 for ee,h,ds in incumbent:
  mask=sum(1<<i for i in ee)
  if mask in removed:continue
  chosen.append([mask,h,ds]);availp.discard(h);availd.discard(h)
  for d in ds:
   assert donorat.setdefault(d,mask)==mask;availp.discard(d);availd.discard(d)

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
 try:assess(entries,dict(trial=trial,penalty=penalty,donor_noise=ctx['os'].environ['PNOISE'],removed_groups=sorted(removed),strategy='fresh-R714-kernel-then-retain-and-repair'))
 except Exception as exc:
  ledger.append(dict(label=dict(trial=trial,penalty=penalty),status='FAILED_CANDIDATE',error=repr(exc)));(out/'LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n');print('FAILED',trial,repr(exc),flush=True)
 if trial%10==9:print('PROGRESS',trial+1,'hosting inventories',len(cache),'best',best['projected_kappa'],flush=True)
(out/'COMPLETE.json').write_text(json.dumps(dict(status='FINISHED_FINITE_FULL_POOLED_SEARCH',trials=limit,records=len(ledger),hosting_inventories=len(cache),best=best),indent=2)+'\n');print('FINISHED',limit,flush=True)
