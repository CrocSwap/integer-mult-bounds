"""Reject omission of the new middle Steinberg shear with cleanup regenerated."""
import argparse,copy,gzip,hashlib,json,os,subprocess,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--auditor',type=Path,required=True);ap.add_argument('--selection',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
if not __debug__:raise SystemExit('Assertions must remain enabled.')
raw=gzip.decompress(a.candidate.read_bytes());assert hashlib.sha256(raw).hexdigest()=='6a02824c7484b9fd768a39d87b9c65dbe5221a877032ed1f74d11afb2acdd7d8'
w=json.loads(raw);assert w['B'][937]==['add',616,299,1,1,[290,162,98,24,6]];w['B'].pop(937)
def inverse(e):
 e=copy.deepcopy(e)
 if e[0]=='add':e[3]*=-1
 else:e[2],e[3]=e[3],e[2]
 e[-1]=[1<<i for i in reversed(range(9))]
 return e
w['cleanup']=[inverse(e)for e in reversed(w['A']+w['B'])if not 112<=e[1]<224]
a.out.mkdir(exist_ok=False);mut=a.out/'OMITTED-MIDDLE.json.gz';mut.write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0))
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
p=subprocess.run([sys.executable,'-B',str(a.auditor),str(mut),str(a.selection),str(a.out/'UNEXPECTED-AUDIT.json')],env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(a.out/'REJECTION.log').write_text(p.stdout)
assert p.returncode==1 and 'assert replay(program)==expected' in p.stdout,(p.returncode,p.stdout)
receipt=dict(status='PASS_REJECTED_OMITTED_NEW_STEINBERG_SHEAR',candidate_content_sha256=hashlib.sha256(raw).hexdigest(),omitted=['add',616,299,1,1,[290,162,98,24,6]],cleanup_regenerated=True,observed_exit_code=p.returncode,rejection='Exact arbitrary-input forward endpoint assertion',log_sha256=hashlib.sha256(p.stdout.encode()).hexdigest())
(a.out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'])
