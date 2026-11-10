"""Measure serial fresh-process native replays; do not replace frozen evidence."""
from pathlib import Path
import subprocess,json,time,hashlib,platform,statistics,sys,argparse
py=sys.executable
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
output=Path(args.output)
if output.exists():raise ValueError('Use a new benchmark output path')
p=Path(__file__).resolve().parent
runs=[]
for pair in range(3):
 for engine in (['gated','prefix'] if pair%2==0 else ['prefix','gated']):
  start=time.monotonic();z=subprocess.run([py,'-B',str(p/'run.py'),engine],text=True,capture_output=True,timeout=600)
  if z.returncode:raise RuntimeError(z.stderr)
  r=json.loads(z.stdout);r.update(pair=pair,engine=engine,wall_seconds=time.monotonic()-start);runs.append(r)
  print(engine,r['seconds'],flush=True)
need_same=all(r['native']==runs[0]['native'] for r in runs)
if not need_same:raise RuntimeError('Different native receipt')
med={k:statistics.median(r['wall_seconds'] for r in runs if r['engine']==k) for k in ['gated','prefix']}
result={'status':'PASS_ALTERNATING_FULL_NATIVE_BENCHMARK','python':subprocess.check_output([py,'--version'],text=True).strip(),'platform':platform.platform(),'runs':runs,'median_wall_seconds':med,'speedup':med['gated']/med['prefix'],'source_sha256':{str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.rglob('*.py'))},'input_sha256':{str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((p/'inputs').iterdir())},'scope':'Complete native component, compared against prior gate tables; not complete caller or end-to-end multiplication.'}
output.write_text(json.dumps(result,indent=2)+'\n')
