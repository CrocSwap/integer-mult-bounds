"""Full reconstruction; Python3.11+, SymPy. OpenAI Codex assistance, Apache-2.0."""
from pathlib import Path
import gzip,hashlib,json,os,subprocess,sys,time
assert __debug__
ROOT=Path(__file__).resolve().parent;PARENT=ROOT.parent/'e8-hosting-selected-kernel'
OUT=Path(sys.argv[1]).resolve();assert not OUT.exists() and not OUT.is_relative_to(ROOT.parent)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
 actual={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'MANIFEST.json' and '__pycache__' not in p.parts}
 assert actual==read(ROOT/'MANIFEST.json')
 assert sha(PARENT/'MANIFEST.json')==read(ROOT/'SOURCE.json')['parent_manifest_sha256']
integrity();OUT.mkdir(parents=True);steps=[]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
def run(name,path,*args):
 log=OUT/(name+'.log');t=time.monotonic();print('RUN',name,flush=True)
 with log.open('w') as f:q=subprocess.run([sys.executable,'-B',str(path),*map(str,args)],env=env,stdout=f,stderr=subprocess.STDOUT)
 assert q.returncode==0,(name,log.read_text()[-3000:])
 steps.append(dict(name=name,seconds=round(time.monotonic()-t,2),log_sha256=sha(log)));print('PASS',name,flush=True)
try:
 run('parent-full',PARENT/'verify.py',OUT/'parent')
 b=OUT/'parent/changed/bit426-source-centres';candidate=OUT/'candidate';candidate.mkdir()
 for n in ('records','nine'):(candidate/n).symlink_to(b/('global' if n=='nine' else n),target_is_directory=True)
 (candidate/'word.json.gz').write_bytes(gzip.compress((b/'bit-source-centres.json').read_bytes(),mtime=0))
 template=json.loads(gzip.decompress((b/'global/GLOBAL-TEMPLATE.json.gz').read_bytes()))
 (candidate/'isometries.json').write_text(json.dumps(template['residual_isometries']))
 host=OUT/'bit'
 run('geometry',ROOT/'code/geometry.py','--source',ROOT.parent/'e8-rank138-idle-hosting/upstream443/parent436','--out',host)
 run('emit',ROOT/'code/emit.py','--word',candidate/'word.json.gz','--local-check',candidate,'--out',host,'--isometries',candidate/'isometries.json')
 run('independent-audit',ROOT/'code/audit.py',candidate,host)
 assert len(read(host/'AUDIT.json')['mutations_rejected'])==22
 run('exact-assembly',ROOT/'code/assemble.py',OUT/'parent',host)
 (OUT/'RESULT.json').write_bytes((host/'RESULT.json').read_bytes())
 actual=read(OUT/'RESULT.json')
 for k,v in read(ROOT/'EXPECTED.json').items():assert actual[k]==v,(k,actual[k],v)
 integrity();receipt=dict(status='PASS_FULL_ELEVEN_HOSTING_SELECTED',python=sys.version.split()[0],kappa=actual['kappa'],manifest_sha256=sha(ROOT/'MANIFEST.json'),checks=steps)
 (OUT/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
except BaseException as e:
 (OUT/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),completed=steps),indent=2)+'\n');raise
