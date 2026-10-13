"""Compose the PR485 selection with our retimed precursor, nested promotions and response packets."""
from pathlib import Path
from collections import Counter,defaultdict
import ast,copy,json,sys,math,hashlib,importlib.util
r=Path.cwd();out=r/'pr485-promoted-composition';assert not out.exists();out.mkdir()
setup=(r/'search_r715_kernel.py').read_text().split('for penalty in [')[0].replace("out=r/'r715-kernel-search'","out=r/'pr485-promoted-composition'").replace('source463-review/data/R715_FP_final.json.gz','r715-delivery-kernel-search/PRECURSOR.json.gz');exec(setup)
maskfirst={h:masks[f] for h,f in first.items()}
sp=importlib.util.spec_from_file_location('factor',r/'source483-review/code/schur_constructor.py');Factor=importlib.util.module_from_spec(sp);sp.loader.exec_module(Factor);factors=json.loads((r/'source483-review/code/SELECTION473.json').read_text())['selected']
code=ast.parse((r/'search_r715_nested_donors.py').read_text());fn=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name=='nested_kernel'];exec(compile(ast.Module(body=fn,type_ignores=[]),'nested_kernel_pinned','exec'))
sys.path.insert(0,str(r/'source483-review/code'));from algebra_constructor import responses
original=json.loads((r/'source485-review/data/kernel-selection.json').read_text());ledger=[]
def emit(chosen,tag,moves):
 z,pivs,chains=nested_kernel(w,chosen);z,_=Factor.rewrite(z,factors);a=E.replay(z,L=L,masks=E.to_masks(z,L),span_mode='z');assert not a['viol']
 grouped=defaultdict(list)
 for i,key in responses(z).items():grouped[key].append(i)
 deleted=[]
 for key,ids in sorted(grouped.items()):
  deleted+=ids if key[1]==0 else ids[:len(ids)//2*2]
 zz=copy.deepcopy(z);zz['A']=[g for i,g in enumerate(z['A']) if i not in set(deleted)];zz['C']=[[1,d,ss] for f,d,ss in reversed(zz['A'])]
 b=E.replay(zz,L=L,masks=E.to_masks(zz,L),span_mode='z');assert not b['viol'];Factor.check(zz,[L.dim(x) for x in E.to_masks(zz,L)])
 d=out/tag;d.mkdir();blob=json.dumps(zz,sort_keys=True,separators=(',',':')).encode();(d/'WORD.json').write_bytes(blob);(d/'SELECTION.json').write_text(json.dumps(dict(entries=chosen,moves=moves,deleted_A_indices=deleted),indent=2)+'\n');result=dict(status='PASS_COMPOSED_EXACT_LOCAL_ONLY',tag=tag,pivots=len(pivs),entrance_rank=sum(L.dim(e) for e in pivs.values()),donors=len(chains),profile=dict(b['H']),before_packet_profile=dict(a['H']),deleted_injections=len(deleted),word_sha256=hashlib.sha256(blob).hexdigest(),scope='Exact955dirtycolumns,rationalframes,integeroperandspans;physicalnativehostingandfinalcompositionpending');(d/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');ledger.append(result);(out/'LEDGER.json').write_text(json.dumps(ledger,indent=2)+'\n');print(result,flush=True)
try:
 emit(original,'baseline112',[])
 for trial,penalty in enumerate([0.,.2,.5,1.]):
  chosen=copy.deepcopy(original);moves=[];cost=lambda k:k*math.log(78/k)+penalty*k if k else 0
  def donor_path(h,entries):return [0]+sorted(set(sum(1<<i for i in ee) for ee,p,ds in entries if h in ds),key=L.dim)+[maskfirst[h]]
  def pathcost(path):return sum(cost(L.dim(b)-L.dim(a)) for a,b in zip(path,path[1:]))
  while True:
   best=None
   for ix,(ee,p,ds) in enumerate(chosen):
    old=sum(1<<i for i in ee);cap=maskfirst[p]
    for d in ds:cap&=maskfirst[d]
    if cap==old or old&~cap:continue
    # Meet of closed first frames is closed; only the maximal common entrance is nominated here.
    trial_entries=copy.deepcopy(chosen);trial_entries[ix][0]=[i for i in range(v) if cap>>i&1];delta=cost(L.dim(maskfirst[p])-L.dim(cap))-cost(L.dim(maskfirst[p])-L.dim(old));ok=True
    for d in ds:
     path=donor_path(d,trial_entries)
     if any(a&~b for a,b in zip(path,path[1:])):ok=False;break
     delta+=pathcost(path)-pathcost(donor_path(d,chosen))
    if ok and delta< -1e-10 and(best is None or delta<best[0]):best=(delta,ix,cap)
   if best is None:break
   delta,ix,cap=best;moves.append(dict(pivot=chosen[ix][1],old=chosen[ix][0],new=[i for i in range(v) if cap>>i&1],proxy_delta=delta));chosen[ix][0]=moves[-1]['new']
  emit(chosen,'promoted-'+str(trial),moves)
 (out/'COMPLETE.json').write_text(json.dumps(dict(status='FINISHED',cases=len(ledger)),indent=2)+'\n')
except BaseException as e:
 (out/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),completed=len(ledger)),indent=2)+'\n');raise
