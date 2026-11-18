"""Sequential verification without imposed resource limits; fresh outputs only."""
from pathlib import Path
import argparse,hashlib,json,os,platform,signal,subprocess,sys,time
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
commands=[('finite225',[str(ROOT/'verify.py'),'--mode','finite','--grid',str(225*2**14)]),('controls',[str(ROOT/'verify.py'),'--mode','controls'])]
for label,exponent in [('price-low','0.99627065682194'),('price-high','0.99627065682193')]:commands.append((label,[str(ROOT/'vendor/evaluate_recursive_power.py'),str(ROOT/'caller16/INVOICE-ZERO.json'),str(ROOT/'candidate/INVOICE.json'),'--exponent',exponent,'--bits','256']))
manifest=json.loads((ROOT/'INPUT-MANIFEST.json').read_bytes())
def check_inputs():
 for item in manifest['files']:
  if hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()!=item['sha256']:raise ValueError('INPUT_PIN:'+item['path'])
check_inputs()
receipts=[]
for label,argv in commands:
 cmd=[sys.executable,'-I','-B']+argv;start=time.monotonic();timedout=False
 with (a.out/(label+'.stdout.json')).open('xb') as stdout,(a.out/(label+'.stderr.txt')).open('xb') as stderr:
  child=subprocess.Popen(cmd,cwd=ROOT,stdout=stdout,stderr=stderr,start_new_session=True)
  print(json.dumps({'started':label,'pid':child.pid,'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}),flush=True)
  try:
   rc=child.wait()
  except BaseException:
   # Cleanup only this runner's still-owned child/session after interruption/error.
   if child.poll() is None:
    try:os.killpg(child.pid,signal.SIGTERM)
    except ProcessLookupError:pass
   child.wait()
   raise

 receipt={'name':label,'command':cmd,'cwd':str(ROOT),'pid':child.pid,'returncode':rc,'wall_seconds':time.monotonic()-start,'timed_out':timedout,'owned_child_reaped':child.poll() is not None,'stdout':label+'.stdout.json','stderr':label+'.stderr.txt'}
 receipts.append(receipt)
 (a.out/'RUNS.json').write_text(json.dumps({'runtime':sys.version,'executable':sys.executable,'platform':platform.platform(),'runs':receipts},indent=2)+'\n')
 print(json.dumps(receipt),flush=True)
 if rc!=0:raise SystemExit('Verification stopped after nonzero exit; not counted as expected control')
 report=json.loads((a.out/(label+'.stdout.json')).read_bytes())
 if label.startswith('price-'):
  expected='new_cost_lower' if label=='price-low' else 'new_cost_higher'
  if report.get('classification')!=expected:raise SystemExit('Unexpected price classification')
check_inputs()
print('PASS_ALL_SCOPED_VERIFICATION')
