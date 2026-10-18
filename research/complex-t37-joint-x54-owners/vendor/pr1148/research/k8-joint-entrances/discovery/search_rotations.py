"""Rotate equal-dimension entrances inside their exact backward frame ceilings."""
import os,sys,json,gzip,copy,itertools,time,functools
from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);args=ap.parse_args();OUT=args.work.resolve();assert not OUT.is_relative_to(ROOT);OUT.mkdir(parents=True,exist_ok=True)
os.environ['K8_BASE_WORD']=str(OUT/'candidate.json.gz');sys.path.insert(0,str(ROOT/'research/k8-eight-ends/discovery'));import screen_end_groups as S
orig=S.M.cone_ceilings;cache={}
def cone(w,n,v,low):
 key=json.dumps(low,sort_keys=True)
 if key not in cache:cache[key]=orig(w,n,v,low)
 return dict(cache[key])
S.M.cone_ceilings=cone;S.M.interval=functools.lru_cache(None)(S.M.interval)
census=json.loads((OUT/'INTERFACE-CENSUS.json').read_text());results=[];baseline=S.screen(S.w);winners=[]
for g in census:
 if g['old_dim']!=g['hi_dim']-1:continue
 hi=g['hi'];k=len(hi);options=set()
 for mask in range(1,1<<k):
  vec=[]
  for c in range(1,1<<k):
   if (c&mask).bit_count()%2:continue
   x=0
   for i,v in enumerate(hi):
    if c>>i&1:x^=v
   vec.append(x)
  options.add(S.M.basis(vec))
 best=None
 for start in sorted(options):
  if list(start)==g['old']:continue
  t=time.monotonic();w=copy.deepcopy(S.w)
  for h in g['helpers']:w['start_extra'][str(h)]=list(start)
  try:
   w=S.optimize(w);r=dict(helpers=g['helpers'],start=list(start),profile=w['report']['local_profile'],**S.screen(w))
   if best is None or r['kappa_relaxed']>best['kappa_relaxed']:
    best=r
    if r['kappa_relaxed']>baseline['kappa_relaxed']+1e-14:
     (OUT/f"rotate-{g['helpers'][0]}.json.gz").write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));print('IMPROVING',json.dumps(r),flush=True)
  except (AssertionError,RuntimeError,ValueError) as e:r=dict(helpers=g['helpers'],start=list(start),status='REJECTED',reason=str(e))
  r['seconds']=time.monotonic()-t;results.append(r);(OUT/'ROTATIONS.json').write_text(json.dumps(results,indent=2)+'\n')
 if best and best['kappa_relaxed']>baseline['kappa_relaxed']+1e-14:winners.append(best)
 print('GROUP_DONE',g['helpers'][0],best and best.get('kappa_relaxed'),len(results),flush=True)
(OUT/'ROTATION-WINNERS.json').write_text(json.dumps(winners,indent=2)+'\n')
w=copy.deepcopy(S.w)
for r in winners:
 for h in r['helpers']:w['start_extra'][str(h)]=r['start']
w=S.optimize(w);(OUT/'joint-rotations.json.gz').write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));joint=dict(profile=w['report']['local_profile'],**S.screen(w));(OUT/'JOINT-ROTATIONS.json').write_text(json.dumps(joint,indent=2)+'\n');print('JOINT',joint,flush=True)
