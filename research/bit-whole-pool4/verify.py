"""Fresh full PR460 composition followed by four-replica whole bit pooling."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time
assert __debug__
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--research-root',type=Path,default=ROOT.parent);ap.add_argument('--parent-output',type=Path);a=ap.parse_args();out=a.output.resolve();research=a.research_root.resolve();assert not out.exists() and not out.is_relative_to(research)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inv(p):return {f.relative_to(p).as_posix():sha(f) for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
def integrity():
 actual=inv(ROOT);actual.pop('MANIFEST.json');assert actual==read(ROOT/'MANIFEST.json')
 pin=read(ROOT/'SOURCE.json');parent=research/'complex-kernel-mixed151';assert sha(parent/'MANIFEST.json')==pin['parent_manifest_sha256'] and sha(parent/'SOURCE.json')==pin['parent_source_sha256']
 actual=inv(parent);actual.pop('MANIFEST.json');assert actual==read(parent/'MANIFEST.json')
 assert sha(ROOT/'data/word.json.gz')==pin['unchanged_bit_word_sha256']
integrity();out.mkdir(parents=True);steps=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHON=sys.executable,E8_REPLAY_PHASES='1',PYTHONPATH=os.pathsep.join([str(research/'e8-r740-replica32/code'),str(research/'idle-axis-hosting')]));env.pop('PYTHONOPTIMIZE',None)
def run(name,path,*args):
 log=out/(name+'.log');start=time.monotonic();print('RUN',name,flush=True)
 with log.open('w') as f:q=subprocess.run([sys.executable,'-B',str(path),*map(str,args)],env=env,stdout=f,stderr=subprocess.STDOUT)
 if q.returncode:raise RuntimeError((name,q.returncode,log.read_text()[-5000:]))
 steps.append(dict(name=name,seconds=round(time.monotonic()-start,2),log_sha256=sha(log)));print('PASS',name,flush=True)
try:
 parent=a.parent_output.resolve() if a.parent_output else out/'parent460'
 if not a.parent_output:run('full-parent460',research/'complex-kernel-mixed151/verify.py',parent,'--research-root',research)
 receipt=read(parent/'RECEIPT.json');pin=read(ROOT/'SOURCE.json');assert receipt['status']=='PASS_FULL_COMPLEX_KERNEL_MIXED151_COMPOSITION' and receipt['manifest_sha256']==pin['parent_manifest_sha256'] and receipt['source_sha256']==pin['parent_source_sha256']
 base=parent/'bit459';bit=out/'bit'
 run('geometry',ROOT/'code/geometry.py','--source',research/'e8-r740-replica32/parent436','--out',bit)
 run('emit',ROOT/'code/emit.py','--word',ROOT/'data/word.json.gz','--local-check',base/'local','--out',bit,'--isometries',ROOT/'data/residual-isometries.json')
 run('independent-audit',ROOT/'code/audit.py',base/'local',base/'parent445/parent444/base443/candidate/nine',bit)
 run('fresh-invoice-and-outer',ROOT/'assemble.py',bit,research,parent)
 result=read(bit/'RESULT.json')
 for k,v in read(ROOT/'EXPECTED.json').items():assert result[k]==v,(k,result[k],v)
 (out/'RESULT.json').write_bytes((bit/'RESULT.json').read_bytes());integrity()
 receipt=dict(status='PASS_POOL4_COMPONENT_COMPLETED_PARENT_REUSED' if a.parent_output else 'PASS_FULL_BIT_WHOLE_POOL4',python=sys.version.split()[0],kappa=result['kappa'],manifest_sha256=sha(ROOT/'MANIFEST.json'),parent_receipt_sha256=sha(parent/'RECEIPT.json'),steps=steps)
 (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
except BaseException as e:
 (out/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),steps=steps),indent=2)+'\n');raise
