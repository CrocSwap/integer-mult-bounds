"""Exploratory nominations: all subsets of six best old codimension-one groups."""
import os,sys,json,gzip,copy,itertools,time
from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);args=ap.parse_args();OUT=args.work.resolve();assert not OUT.is_relative_to(ROOT);OUT.mkdir(parents=True,exist_ok=True)
os.environ['K8_BASE_WORD']=str(ROOT/'research/k8-eight-ends/FULL-WORD.json.gz')
sys.path.insert(0,str(ROOT/'research/k8-eight-ends/discovery'))
import screen_end_groups as S
rows=json.loads(gzip.decompress((ROOT/'research/k8-three-demotions/discovery/DEMOTION-5.json.gz').read_bytes()))
best={}
for r in rows:
 if 'kappa_relaxed' not in r:continue
 key=r['helpers'][0]
 if key not in best or best[key]['kappa_relaxed']<r['kappa_relaxed']:best[key]=r
print('choices',json.dumps(best),flush=True)
results=[];record=0
for n in range(7):
 for keys in itertools.combinations(sorted(best),n):
  t=time.monotonic();w=copy.deepcopy(S.w)
  for k in keys:
   for h in best[k]['helpers']:w['start_extra'][str(h)]=best[k]['start']
  try:
   w=S.optimize(w);r=dict(groups=keys,profile=w['report']['local_profile'],**S.screen(w))
   if r['kappa_relaxed']>record:
    record=r['kappa_relaxed'];(OUT/'best-composition.json.gz').write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));print('BEST',json.dumps(r),flush=True)
  except (AssertionError,RuntimeError,ValueError) as e:r=dict(groups=keys,status='REJECTED',reason=str(e))
  r['seconds']=time.monotonic()-t;results.append(r);(OUT/'COMPOSITIONS.json').write_text(json.dumps(results,indent=2)+'\n')
print('DONE',len(results),record,flush=True)
