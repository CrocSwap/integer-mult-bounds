"""Explore pivot/donor basis exchanges, then legal nested entrance promotions.
Every accepted state has exact response/frame/role constraints; endpoints get independent replay.
"""
from pathlib import Path
import random,time
r=Path.cwd();s=(r/'compose_pr485_promotions.py').read_text().split('\ntry:',1)[0].replace('pr485-promoted-composition','r715-nested-basis-exchanges');exec(compile(s,'pinned_composition_setup','exec'))
def mask(lines):return sum(1<<i for i in lines)
seeds=[('current110',json.loads((r/'source483-review/bit470/data/kernel-selection.json').read_text())['entries']),('promoted112',json.loads((r/'pr485-promoted-composition/promoted-0/SELECTION.json').read_text())['entries'])]
DIMS={f:L.dim(f) for f in set(maskfirst.values())|{0}}
def dim(f):
 if f not in DIMS:DIMS[f]=L.dim(f)
 return DIMS[f]
def validate(entries):
 piv={p for e,p,ds in entries}
 if len(piv)!=len(entries):return None,'duplicate pivot'
 ch={}
 for e,p,ds in entries:
  if not e or e&~maskfirst[p] or p in w['ret']:return None,'pivot frame'
  v=response[p]
  if len(ds)!=len(set(ds)):return None,'duplicate donor'
  for d in ds:
   if d in piv or d in w['ret'] or e&~maskfirst[d]:return None,'donor role/frame'
   v^=response[d];ch.setdefault(d,set()).add(e)
  if v:return None,'response'
 for frames in ch.values():
  chain=sorted(frames,key=dim)
  if any(a&~b for a,b in zip(chain,chain[1:])):return None,'donor chain'
 return ch,None
def serial(entries):return [[[i for i in range(v) if e>>i&1],p,ds] for e,p,ds in entries]
trials=[]
for name,init in seeds:
 for trial,penalty in enumerate([.2,.8]):
  rng=random.Random(488000+trial+(100 if name=='current110' else 0));state=[[mask(e),p,ds] for e,p,ds in init];cost=lambda k:k*math.log(78/k)+penalty*k if k else 0
  def score(st,ch):
   val=sum(cost(dim(maskfirst[p])-dim(e))-cost(dim(maskfirst[p])) for e,p,ds in st)
   for d,frames in ch.items():
    path=[0]+sorted(frames,key=dim)+[maskfirst[d]];val+=sum(cost(dim(b)-dim(a)) for a,b in zip(path,path[1:]))-cost(dim(maskfirst[d]))
   return val
  def promote(st):
   for sweep in range(5):
    ch,reason=validate(st);assert reason is None;oldscore=score(st,ch);best=None
    for ix,(e,p,ds) in enumerate(st):
     cap=maskfirst[p]
     for d in ds:cap&=maskfirst[d]
     if cap==e:continue
     test=[x[:] for x in st];test[ix]=[cap,p,ds];cc,reason=validate(test)
     if reason is not None:continue
     val=score(test,cc)
     if val<oldscore-1e-9 and(best is None or val<best[0]):best=(val,test)
    if best is None:break
    st=best[1]
   return st
  ch,reason=validate(state);assert reason is None;current=score(state,ch);best=current;bs=copy.deepcopy(state);history=[];bestrows=[];rejects=Counter();accepted=0;started=time.monotonic()
  for step in range(5000):
   ix=rng.randrange(len(state));e,p,ds=state[ix]
   if not ds:rejects['empty relation']+=1;continue
   donor=rng.choice(ds);replacement=set(ds)-{donor}|{p};candidate=[]
   for j,(f,q,qq) in enumerate(state):
    if j==ix:candidate.append([f,donor,sorted(replacement)])
    else:candidate.append([f,q,sorted(set(qq)^{donor}^replacement) if donor in qq else qq[:]])
   ch,reason=validate(candidate)
   if reason is not None:rejects[reason]+=1;continue
   val=score(candidate,ch);temp=.25*(1-step/5000)+.02
   if val<=current+1e-10 or rng.random()<math.exp((current-val)/temp):
    accepted+=1;history.append(dict(step=step,pivot=p,donor=donor,entry=ix));state=candidate
    # Periodically promote after exploring equal-cost basis changes.
    if accepted%20==0:state=promote(state)
    ch,reason=validate(state);assert reason is None;current=score(state,ch)
    if current<best-1e-9:
     best=current;bs=copy.deepcopy(state);bestrows.append(dict(step=step,score=best,entrance_rank=sum(dim(e) for e,p,ds in bs),entries=serial(bs)));print('BEST',name,trial,step,'rank',bestrows[-1]['entrance_rank'],'score',best,flush=True)
   else:rejects['annealing rejected']+=1
  bs=promote(bs);ch,reason=validate(bs);assert reason is None;best=score(bs,ch);tag=name+'-'+str(trial);emit(serial(bs),tag,history)
  data=dict(tag=tag,seed=488000+trial+(100 if name=='current110' else 0),steps=5000,penalty=penalty,accepted=accepted,rejected=dict(rejects),best_proxy=best,best_states=bestrows,seconds=round(time.monotonic()-started,3));(out/tag/'SEARCH.json').write_text(json.dumps(data,indent=2)+'\n');trials.append({k:v for k,v in data.items() if k!='best_states'});(out/'SEARCH-LEDGER.json').write_text(json.dumps(trials,indent=2)+'\n');print('FINISHED TRIAL',trials[-1],flush=True)
(out/'COMPLETE.json').write_text(json.dumps(dict(status='FINISHED_EXACT_LOCAL_BASIS_EXCHANGE_SEARCH',trials=trials,cases=len(ledger)),indent=2)+'\n')
