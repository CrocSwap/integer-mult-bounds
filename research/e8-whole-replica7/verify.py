"""Fresh PR454 supplier replay followed by seven-replica whole complex composition."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time
assert __debug__
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--parent-output',type=Path);ap.add_argument('--research-root',type=Path,default=ROOT.parent);a=ap.parse_args()
research=a.research_root.resolve();out=a.output.resolve();assert not out.exists() and not out.is_relative_to(research)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inv(p):return {f.relative_to(p).as_posix():sha(f) for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
def integrity():
 actual=inv(ROOT);actual.pop('MANIFEST.json');assert actual==read(ROOT/'MANIFEST.json')
 src=read(ROOT/'SOURCE.json');parent=research/'e8-target-mixing-whole'
 assert sha(parent/'MANIFEST.json')==src['parent_manifest_sha256'] and sha(parent/'SOURCE.json')==src['parent_source_sha256']
 actual=inv(parent);actual.pop('MANIFEST.json');assert actual==read(parent/'MANIFEST.json')
 for name,pin in read(parent/'SOURCE.json')['packages'].items():assert inv(research/name)==pin['files'],name
integrity();out.mkdir(parents=True);steps=[]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',E8_REPLAY_PHASES='1',PYTHON=sys.executable,PYTHONPATH=str(research/'idle-axis-hosting'));env.pop('PYTHONOPTIMIZE',None)
# The adapter changes shell word splitting only for the pinned PR436 shell.
if ' ' in str(research) or ' ' in str(out):env['BASH_ENV']=str(ROOT/'code/bash-env.sh')
if 'BOOST_INCLUDE' not in env and Path('/opt/homebrew/include/boost').exists():env['BOOST_INCLUDE']='/opt/homebrew/include'
def run(name,cmd):
 log=out/(name+'.log');start=time.monotonic();print('RUN',name,flush=True)
 with log.open('w') as f:proc=subprocess.run(list(map(str,cmd)),env=env,stdout=f,stderr=subprocess.STDOUT)
 assert proc.returncode==0,(name,log.read_text()[-4000:]);steps.append(dict(name=name,seconds=round(time.monotonic()-start,2),log_sha256=sha(log)));print('PASS',name,flush=True)
def py(name,path,*args):run(name,[sys.executable,'-B',path,*args])
try:
 parent=a.parent_output.resolve() if a.parent_output else out/'parent454'
 if a.parent_output:
  receipt=read(parent/'RECEIPT.json');assert receipt['status']=='PASS_TARGET_MIXING_WHOLE_HOSTING' and receipt['mode']=='full'
 else:py('full-parent454',research/'e8-target-mixing-whole/verify.py',parent)
 src=parent/'parent451/parent445/parent444/upstream442/parent/changed/split-centres'
 complex_out=out/'complex';complex_out.mkdir()
 py('complex-phases',research/'r740-hosted-rank149/code/complex_phases.py',src/'CANONICAL-WORD.json.gz',complex_out/'DATA-PHASES.json')
 py('emit',ROOT/'code/emit.py',src,complex_out)
 py('independent-audit',ROOT/'code/audit.py',src,complex_out)
 py('physical-route-controls',ROOT/'code/route_controls.py')
 py('invoice-and-outer',ROOT/'code/candidate_invoice.py',complex_out,research,parent)
 result=read(complex_out/'RESULT.json')
 for k,v in read(ROOT/'EXPECTED.json').items():assert result[k]==v,(k,result[k],v)
 (out/'RESULT.json').write_bytes((complex_out/'RESULT.json').read_bytes());integrity()
 receipt=dict(status='PASS_WHOLE_REPLICA7_COMPONENT_PARENT_REUSED' if a.parent_output else 'PASS_FULL_WHOLE_REPLICA7',python=sys.version.split()[0],kappa=result['kappa'],manifest_sha256=sha(ROOT/'MANIFEST.json'),parent_receipt_sha256=sha(parent/'RECEIPT.json'),shell_adapter_sha256=sha(ROOT/'code/bash-env.sh') if 'BASH_ENV' in env else None,steps=steps)
 (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
except BaseException as e:
 (out/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),steps=steps),indent=2)+'\n');raise
