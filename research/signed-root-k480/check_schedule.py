"""Reproduce the signed schedule and reject damaged positive triangles.
These controls exercise the unchanged constructor's mathematical assertions.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse,copy,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
from nominate_schedule import nominate

P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--hamming',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
a=ap.parse_args()
if not __debug__:raise RuntimeError('Assertions must remain enabled')
expected=json.loads((P/'data/TRI-SCHEDULE.json').read_text())
assert nominate(a.hamming,P/'data/BASE-K492-SCHEDULE.json')==expected
results=[]
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp)
 def trial(name,schedule):
  f=root/(name+'.json');f.write_text(json.dumps(schedule))
  env=dict(os.environ);env.pop('PYTHONOPTIMIZE',None)
  run=subprocess.run([sys.executable,'-B',str(P/'code/construct_k_triangle.py'),str(a.hamming),str(root/name),str(f)],capture_output=True,text=True,env=env)
  if name=='valid':
   assert run.returncode==0,run.stderr
   import gzip
   content=hashlib.sha256(gzip.decompress((root/name/'FULL-WORD.json.gz').read_bytes())).hexdigest()
   spec=json.loads((P/'data/SPEC.json').read_text())
   assert content==spec['build']['providers']['jp8']['base']['content_sha256']
   return
  assert run.returncode!=0 and 'AssertionError' in run.stderr,(name,run.stdout,run.stderr)
  results.append(dict(name=name,reason=run.stderr.strip().splitlines()[-1]))
 trial('valid',expected)
 for j,t in enumerate(expected['triangles']):
  if t['e']!=1:continue
  label='positive-'+str(t['p'][0])
  bad=copy.deepcopy(expected);bad['triangles'][j]['reads'].pop(0);trial(label+'-missing-read',bad)
  bad=copy.deepcopy(expected);bad['triangles'][j]['reads'][0]=copy.deepcopy(bad['triangles'][j]['reads'][1]);trial(label+'-duplicate-read',bad)
  bad=copy.deepcopy(expected);bad['triangles'][j]['reads'][0][2]=(t['reads'][0][2]+1)%24;trial(label+'-wrong-source',bad)
  bad=copy.deepcopy(expected);bad['triangles'][j]['reads'][0][0]=expected['triangles'][j-1]['reads'][0][0];trial(label+'-wrong-sign-target',bad)
a.out.write_text(json.dumps(dict(status='PASS_SIGNED_SCHEDULE_REPRODUCTION_AND_MUTATIONS',triangles=8,positive_read_count=120,controls=results),indent=2)+'\n')
print('PASS signed-root schedule reproduction;',len(results),'damaged schedules rejected')
