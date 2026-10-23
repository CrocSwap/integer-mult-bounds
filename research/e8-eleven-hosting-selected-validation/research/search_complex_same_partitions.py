"""Allow repeated target partitions and price extra helpers under hosting; nomination only."""
from pathlib import Path
import json,gzip,contextlib,io,math,sys,time
from collections import Counter
r=Path.cwd();out=r/'complex447-same-partitions';out.mkdir(exist_ok=True)
s=(r/'early-reuse-publication/research/split-centres-global/code/complex_construct.py').read_text().replace("INPUT=Path('work/complex-network/hamming');OUT=Path('split-centres');OUT.mkdir(exist_ok=True);", "INPUT=INPUT_OVERRIDE;OUT=OUT_OVERRIDE;OUT.mkdir(exist_ok=True);").replace('selected=(pi==parity)',"selected=(pi==CHOICES[tuple(c)][parity])").replace('assert len(cur)-240==560,(len(cur)-240)','assert len(cur)>240')
code=compile(s,'complex_construct_variable_partitions','exec');inp=(r/'hosted138-screen/work/complex-network/hamming').resolve();modules=json.loads(gzip.decompress((inp/'PACKET-PROGRAMS.json.gz').read_bytes()));blocks=sorted(tuple(z['receipt']['block']) for z in modules)
sys.path.insert(0,str(r/'complex447-search'));import hosting_core as HC
sys.path.insert(0,str(r/'source443-review/code/engines'));import moment as M
c=.001267453159029119;HC.cost=lambda rank,m:rank*math.expm1(c*math.log(m/rank))/c if rank else 0.
t=json.loads(gzip.decompress((r/'hosted138-screen/split-centres/GLOBAL-TEMPLATE.json.gz').read_bytes()));ranks={z['child']:z['rank'] for z in t['idle_children']};pairs={e['stage']:e['pair'] for e in t['recipe'] if e['kind']=='local'};sched=[]
for e in t['execution_schedule']:
 if e['kind']=='local_cover_sweep':sched.append(dict(kind='local',stage=e['stage'],pair=pairs[e['stage']]))
 elif e['kind']=='bridge':sched.append(dict(kind='bridge',dst=e['dst'],src=e['src']))
 elif e['kind']=='idle_cover_sweep':
  for ch in e['child_indices']:
   if ch in ranks:sched.append(dict(kind='idle',pair=e['pair'],rank=ranks[ch],idx=ch))
win={k:x for k,x in HC.windows(sched).items() if x[1]>=9 and x[2]};cache={};results=[]
configs=[('baseline',{b:(0,1) for b in blocks}),('one-repeat',{b:((0,0) if b==blocks[0] else (0,1)) for b in blocks})]+[(f'all-{x}{x}',{b:(x,x) for b in blocks}) for x in range(3)]
for tag,choices in configs:
 d=out/tag
 with contextlib.redirect_stdout(io.StringIO()):exec(code,dict(INPUT_OVERRIDE=inp,OUT_OVERRIDE=d,CHOICES=choices))
 a=json.loads((d/'FULL-DISCOVERY.json').read_text());R=a['R'];H={int(k):v for k,v in a['local_profile'].items()}
 if R not in cache:
  ys,zs,val=HC.solve(win,120,{(s,9):R for s in range(9)},73,pad_value=HC.cost(1,73)/8);slots,rem=HC.expand(win,ys,zs,{s:[(h,9) for h in range(R)] for s in range(9)},120);cache[R]=(ys,zs,val,slots,rem)
 ys,zs,val,slots,rem=cache[R];unhosted=9*R-len(slots);W=7680+unhosted;P=Counter({k:n*72 for k,n in H.items()});P[1]+=unhosted
 for it in t['idle_children']:
  rr=rem.get((it['child'],it['port']),it['rank'])
  if rr:P[rr]+=8
 assert 73*W-sum(k*n for k,n in P.items())==2496
 cert=M.certify(P,73,W,True);res=dict(tag=tag,R=R,live=W,hosted=len(slots)*8,local_profile=H,global_profile=dict(P),cert=cert,status='EXACT_CLEAN_WORD_AND_AGGREGATE_ONLY')
 (d/'HOSTED-PRICE.json').write_text(json.dumps(res,indent=2)+'\n');HC.save_selection(d/'HOSTING-SELECTION.json','complex',ys,zs,val);results.append(res);print(tag,R,W,cert['lower'],flush=True)
(out/'SUMMARY.json').write_text(json.dumps(results,indent=2)+'\n')
