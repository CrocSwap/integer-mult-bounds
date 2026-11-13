"""Portable exact-core replay for the changed #7480 producer.

The complete physical, precision and signed application is run_full.py.
"""
from pathlib import Path
from hashlib import sha256
import gzip,json,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
assert __debug__,'Run Python without -O'
checks=[]
def run(name,args):
 print('RUN',name,flush=True);t=time.time()
 subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,check=True)
 checks.append({'check':name,'seconds':time.time()-t})
source=ROOT/'inputs/pr7480/WORD.json.gz'
assert sha256(source.read_bytes()).hexdigest()=='50bf196026a78b7f6d3539befc22d78aeb6dd518ddcd9f5950c7844bad4c19b0'
assert sha256(gzip.decompress(source.read_bytes())).hexdigest()=='5044adee019f073f286789ccb688ffca76d42b60518242bb4daea818d33d337a'
caller=ROOT/'inputs/pr7113/ODD-TYPE-AB-CALLER.json'
assert sha256(caller.read_bytes()).hexdigest()=='255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
run('literal emission, arbitrary-input equality, all frames and exact native adjoint',[HERE/'reroute/build.py','--native'])
run('independent emitter, all formal current rows, and chronology',[HERE/'reroute/independent_check.py'])
run('adversarial guards and exact mutation counterexamples',[HERE/'reroute/adversarial.py'])
run('fresh common grid and all interior COPY destinations',[ROOT/'inputs/pr7480/derive_grid.py',HERE/'reroute/WORD.json.gz',HERE/'reroute/GRID.json'])
r=json.loads((HERE/'reroute/RESULT.json').read_text());g=json.loads((HERE/'reroute/GRID.json').read_text())
assert r['candidate_canonical_sha256']=='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
assert r['paid_delta']=={'1':1,'3':-1,'4':-1,'6':1}
assert r['productive_endpoint_delta']=={}
assert(r['new_events'],r['new_lifetimes'],r['new_peak'])==(76475,74,50)
assert(g['odd_scale'],g['fractional_bits'])==(1125,25)
print(json.dumps({'status':'PASS_EXACT_CHANGED_PRODUCER_CORE','checks':checks},indent=2),flush=True)
