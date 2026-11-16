#!/usr/bin/env python3
"""Frozen one-stage differential-case execution inside the verified service cgroup."""
import argparse,hashlib,json,os,resource,subprocess,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--freeze-sha',required=True);a=ap.parse_args()
 out=a.out.resolve()
 if out!=ROOT/"run":raise ValueError("continuation requires fixed run path")
 out.mkdir();start=time.monotonic();results=[]
 receipt={'differential_case_completed':False,'source_executed':False,'stages':results}
 try:
  freeze=ROOT/'FREEZE.json';assert sha(freeze)==a.freeze_sha,'freeze receipt mismatch'
  spec=json.loads(freeze.read_bytes())
  for row in spec['files']:
   p=Path(row['path']);assert p.is_file()and not p.is_symlink()and sha(p)==row['sha256'],str(p)
  plan_path=ROOT/'PLAN.json'
  for required in (plan_path,ROOT/'launch.py',ROOT/'controlled_entry.py',ROOT/'run_once.py'):
   assert any(Path(row['path']).resolve()==required.resolve() and row['sha256']==sha(required) for row in spec['files']),'required file not frozen: '+str(required)
  plan=json.loads(plan_path.read_bytes());package=Path(plan['package'])
  frozen_paths={str(Path(row['path']).resolve()) for row in spec['files']}
  assert plan['required_frozen'] and set(plan['required_frozen'])<=frozen_paths,'declared scientific closure missing from freeze'
  assert all(str(p.resolve()) in frozen_paths for p in ROOT.glob('*.py')),'local executable omitted from freeze'
  assert len(plan['stages'])==1 and plan['stages'][0]['timeout_seconds']==3295,'expected one 3295-second stage'
  name=plan['stages'][0]['name'];assert name and name not in ('.','..') and Path(name).name==name,'invalid stage name'
  assert isinstance(plan['stages'][0]['argv'],list) and plan['stages'][0]['argv'],'invalid argv'
  receipt['source_executed']=True
  for stage in plan['stages']:
   assert time.monotonic()-start<3295,'whole job deadline'
   argv=[v.replace('{python}',sys.executable).replace('{package}',str(package)).replace('{out}',str(out))for v in stage['argv']]
   t=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
   with(out/(stage['name']+'.stdout')).open('x')as stdout,(out/(stage['name']+'.stderr')).open('x')as stderr:
    p=subprocess.run(argv,stdout=stdout,stderr=stderr,check=False,timeout=min(stage['timeout_seconds'],3295-(time.monotonic()-start)),env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'))
   after=resource.getrusage(resource.RUSAGE_CHILDREN)
   row={'name':stage['name'],'argv':argv,'exit_code':p.returncode,'wall_seconds':time.monotonic()-t,'aggregate_child_cpu_seconds':(after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime)}
   results.append(row);write(out/'PARTIAL.json',receipt)
   if p.returncode:raise RuntimeError('failed stage '+stage['name'])
   for frozen_row in spec['files']:
    frozen_path=Path(frozen_row['path']);assert frozen_path.is_file()and not frozen_path.is_symlink()and sha(frozen_path)==frozen_row['sha256'],'frozen source changed: '+str(frozen_path)
  receipt['differential_case_completed']=True
 except BaseException as e:
  receipt['error']=repr(e)
 finally:
  r0=resource.getrusage(resource.RUSAGE_SELF);r1=resource.getrusage(resource.RUSAGE_CHILDREN)
  receipt.update(wall_seconds=time.monotonic()-start,aggregate_cpu_seconds=r0.ru_utime+r0.ru_stime+r1.ru_utime+r1.ru_stime,conservative_self_plus_child_peak_rss_KiB=r0.ru_maxrss+r1.ru_maxrss)
  try:
   group=Path('/sys/fs/cgroup')/Path('/proc/self/cgroup').read_text().strip().split('::')[-1].lstrip('/')
   receipt['observed_cgroup_memory_peak_bytes']=int((group/'memory.peak').read_text());receipt['cgroup_cpu_stat']=(group/'cpu.stat').read_text()
  except OSError as e:receipt['measurement_gap']=str(e)
  write(out/'RESOURCE.json',receipt);print(json.dumps(receipt,sort_keys=True),flush=True)
  if not receipt['differential_case_completed']:raise SystemExit(1)
if __name__=='__main__':main()
