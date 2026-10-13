"""Run every PR543 check, with only generator gzip metadata normalized.

The original package is immutable. The temporary shell driver changes HERE
to the pinned package and routes its generator through the disclosed gzip
serialization wrapper. No mathematical assertion or native checker changes.
Prepared for chafreaky with Codex assistance, Apache-2.0.
"""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
if not __debug__:raise SystemExit('Assertions must remain enabled')
ap=argparse.ArgumentParser();ap.add_argument('package',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--cxx',default='c++');ap.add_argument('--boost-include',required=True,type=Path);a=ap.parse_args()
P=a.package.resolve();O=a.out.resolve();assert not O.exists();O.mkdir(parents=True)
source=P/'vendor/e8-bit-r420/verify.sh';old=source.read_text();new=old
anchor='HERE=$(cd "$(dirname "$0")" && pwd); WD='
assert new.count(anchor)==1
new=new.replace(anchor,'HERE='+repr(str(source.parent))+'; WD=')
anchor='NODEOPT=2000 $PY $C/gen_l3.py'
assert new.count(anchor)==1
new=new.replace(anchor,'NODEOPT=2000 $PY '+repr(str(P/'code/run.py'))+' $C/gen_l3.py')
driver=O/'verify-driver.sh';driver.write_text(new)
env=dict(os.environ,PYTHON=sys.executable,BOOST_INCLUDE=str(a.boost_include.resolve()),CXX=a.cxx,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0')
env.pop('PYTHONOPTIMIZE',None)
subprocess.run(['bash',str(driver),str(O/'replay')],env=env,check=True)
receipt=dict(status='PASS_COMPLETE_PR543_DRIVER',source_commit='2065fe4f72a914d907f1046603f5a36f17018535',source_sha256=hashlib.sha256(old.encode()).hexdigest(),driver_sha256=hashlib.sha256(new.encode()).hexdigest(),changes=['Pin HERE to the unchanged vendored package.','Run only the word generator through code/run.py to normalize gzip OS byte; all payload bytes and mathematical checks retained.'])
(O/'DRIVER.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],flush=True)
