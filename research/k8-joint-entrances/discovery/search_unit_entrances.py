"""Screen colder copies: remove rank-one entrances and refit the recursive word."""
import os,sys,json,gzip,copy,time,functools
from pathlib import Path
from collections import defaultdict
import argparse
ROOT=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);args=ap.parse_args();OUT=args.work.resolve();assert not OUT.is_relative_to(ROOT);OUT.mkdir(parents=True,exist_ok=True)
os.environ['K8_BASE_WORD']=str(OUT/'candidate.json.gz');sys.path.insert(0,str(ROOT/'research/k8-eight-ends/discovery'));import screen_end_groups as S
# Reuse the efficient finite subspace enumerator from our joint-frame search.
s=Path(__file__).with_name('search_joint_frames.py').read_text();enum=s[s.index('@functools.lru_cache(None)'):s.index('w=copy.deepcopy(S.w)')];ns={'functools':functools,'M':S.M};exec(enum,ns)
S.M.interval=ns['interval'];oldcone=S.M.cone_ceilings;cache={}
def cone(w,n,v,low):
 key=json.dumps(low,sort_keys=True)
 if key not in cache:cache[key]=oldcone(w,n,v,low)
 return dict(cache[key])
S.M.cone_ceilings=cone
oldlp=S.linprog
def bounded_lp(*args,**kw):
 kw['options']=dict(kw.get('options',{}),time_limit=30);return oldlp(*args,**kw)
S.linprog=bounded_lp
units=sorted(int(h) for h,fr in S.w['start_extra'].items() if len(fr)==1);cohorts=defaultdict(list)
for h in units:cohorts[tuple(S.w['start_extra'][str(h)])].append(h)
cases=[('all',units)]+[(f'point-{fr[0]}',hs) for fr,hs in cohorts.items()]+[(f'single-{h}',[h]) for h in units]
# Search smaller interventions before the simultaneous all-cold trial.
cases=cases[1:]+cases[:1];results=[];record=S.screen(S.w)['kappa_relaxed']
for label,hs in cases:
 t=time.monotonic();w=copy.deepcopy(S.w)
 for h in hs:w['start_extra'][str(h)]=[]
 try:
  w=S.optimize(w);r=dict(label=label,helpers=hs,status='NOMINATED_REQUIRES_NATIVE_AND_PHYSICAL_PACKING',profile=w['report']['local_profile'],**S.screen(w))
  if r['kappa_relaxed']>record+1e-14:
   record=r['kappa_relaxed'];(OUT/'best-unit-entrances.json.gz').write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));print('IMPROVING',json.dumps(r),flush=True)
 except (AssertionError,RuntimeError,ValueError) as e:r=dict(label=label,helpers=hs,status='NO_NOMINATION_FROM_SCREEN',exception=type(e).__name__,reason=str(e))
 r['seconds']=time.monotonic()-t;results.append(r);(OUT/'UNIT-ENTRANCES.json').write_text(json.dumps(results,indent=2)+'\n')
 if len(results)%10==0 or label.startswith('point') or label=='all':print('PROGRESS',len(results),label,r.get('kappa_relaxed',r.get('reason')),flush=True)
print('DONE',len(results),'best_relaxed',record,flush=True)
