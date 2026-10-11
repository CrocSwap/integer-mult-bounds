"""Fresh parent replay, chronological reset reconstruction, banks and exact assembly."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
assert __debug__
ROOT=Path(__file__).resolve().parent;PARENT=ROOT.parent/'split-centres-global';out=Path(sys.argv[1]).resolve();assert not out.exists() and not out.is_relative_to(ROOT.parent)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
 assert {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}==read(ROOT/'MANIFEST.json')['files']
 assert sha(PARENT/'MANIFEST.json')==read(ROOT/'SOURCE.json')['parent_manifest_sha256']
integrity();out.mkdir(parents=True);env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None);steps=[]
def run(name,file,*args,cwd=None):
 t=time.monotonic();log=out/(name+'.log');print('RUN',name,flush=True)
 with log.open('w') as f:q=subprocess.run([sys.executable,'-B',str(file),*map(str,args)],cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT)
 if q.returncode:raise RuntimeError((name,q.returncode,log.read_text()[-2000:]))
 steps.append(dict(name=name,seconds=time.monotonic()-t,log_sha256=sha(log)));print('PASS',name,flush=True)
try:
 base=out/'baseline';run('full-parent433',PARENT/'verify.py',base,'--replay-phases')
 changed=out/'changed';changed.mkdir()
 for name in ('work','inherited','split-centres'):(changed/name).symlink_to(base/name,target_is_directory=True)
 bit=changed/'bit426-source-centres';bit.mkdir()
 run('reconstruct',ROOT/'replay.py',base/'bit426-source-centres/bit-source-centres.json',bit/'bit-source-centres.json')
 run('export',PARENT/'vendor/export_records.py',bit/'bit-source-centres.json',bit/'records')
 run('global-program',ROOT/'bit_global.py','--source',bit,'--local-check',bit,'--out',bit/'global',cwd=changed)
 run('independent-audit',ROOT/'bit_audit.py','--local-check',bit,'--out',bit/'global',cwd=changed)
 run('two-moments',ROOT/'bit_price.py',cwd=changed)
 env['E8_OUTPUT']=str(changed);run('finite-assembly',ROOT/'combined.py',cwd=changed)
 actual=read(changed/'RESULT.json');expected=read(ROOT/'EXPECTED.json')
 for k,v in expected.items():assert actual[k]==v,(k,actual[k],v)
 integrity();result=dict(status='PASS_FULL_PARENT_AND_EARLY_RESET_REUSE',kappa=actual['kappa'],kappa_decimal=actual['kappa_decimal'],source_manifest_sha256=sha(ROOT/'MANIFEST.json'),checks=steps,parent_phase_mode=read(base/'RESULT.json')['phase_mode']);(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
except BaseException as e:
 (out/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),completed=steps),indent=2)+'\n');raise
