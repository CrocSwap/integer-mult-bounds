"""Replay the finite914 frame closures and70 emitted refit/alias invoices.
No new domain expansion or supplier claim; outputs stay external.
"""
if not __debug__:raise RuntimeError('Assertions are required; run without -O')
import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import sys,json,gzip,copy,argparse,multiprocessing as mp,hashlib,time
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE/'vendor'));from bounds import Bounds
from refit import Refit
import alias_build,eval1
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
B=None
def init():
 global B;B=Bounds(str(HERE/'inputs/BASELINE-base.json.gz'))
def frame(task):
 t,op=task;b=copy.deepcopy(B);R=Refit(b);x=R.lower(t,b.lo[t])if op=='lower'else R.raise_(t,b.hi[t]);assert not isinstance(x,str);profile,inv=alias_build.profile(b.Wd.w);return t,op,profile,len(x)
def alias(task):
 tag,h,L=task;w,log=eval1.apply_stack(str(HERE/f'inputs/BASELINE-{tag}.json.gz'),[(h,L)]);assert w is not None,log;return tag,h,L,w['report']['local_profile'],w['report']['width_inventory']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--workers',type=int,default=1);ap.add_argument('--smoke',action='store_true');a=ap.parse_args();assert __debug__ and 1<=a.workers<=16 and not a.work.exists()and not a.work.resolve().is_relative_to(HERE);a.work.mkdir(parents=True);start=time.monotonic()
 pins=read(HERE/'SOURCE-PINS.json')['sha256'];assert all(hashlib.sha256((HERE/n).read_bytes()).hexdigest()==h for n,h in pins.items());base=Bounds(str(HERE/'inputs/BASELINE-base.json.gz'));tasks=[(t,'lower')for t in base.lo if base.lo[t]!=base.Wd.gateframe[t]]+[(t,'raise')for t in base.hi if base.hi[t]!=base.Wd.gateframe[t]];assert len(tasks)==914
 records=[json.loads(x)for x in(HERE/'receipts/FRAME-PROFILES.jsonl').read_text().splitlines()];stored={(x['time'],x['op']):x for x in records};assert set(stored)==set(tasks);pairs=read(HERE/'receipts/PAIRS-base.json')['pairs'];assert[(h,L)for h,L,*_ in pairs]==[(h,L)for h,L,*_ in read(HERE/'receipts/PAIRS-extra.json')['pairs']];alias_tasks=[(tag,h,L)for h,L,*_ in pairs for tag in ['base','extra']];assert len(alias_tasks)==70;alias_stored={(x['provider'],x['follower'],x['lender']):x for x in[json.loads(s)for s in(HERE/'receipts/ALIAS-PROFILES.jsonl').read_text().splitlines()]};assert set(alias_stored)==set(alias_tasks)
 if a.smoke:tasks=[(12235,'lower'),tasks[0]];alias_tasks=[('base',606,550),('extra',606,550)]
 with mp.get_context('fork').Pool(a.workers,initializer=init)as pool:
  for t,op,profile,count in pool.imap_unordered(frame,tasks):assert profile==stored[t,op]['profile']and count==stored[t,op]['changes'],(t,op)
  for tag,h,L,profile,inv in pool.imap_unordered(alias,alias_tasks):assert profile==alias_stored[tag,h,L]['profile']and inv==alias_stored[tag,h,L]['width_inventory'],(tag,h,L)
 result={'status':'PASS_FINITE_INVOICE_REPLAY','frame_domain':914,'alias_domain':70,'frames_replayed':len(tasks),'aliases_replayed':len(alias_tasks),'smoke_only':a.smoke,'seconds':time.monotonic()-start,'scope':'Exact match to stored invoices for the declared single-extreme closures and minimal-change one-alias proposals only; no all-frame or all-alias optimum.'};(a.work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
