"""Fresh parent454, exact kernel, paid residual adapters and global composition.
Usage: python -B research/e8-complex-adapted-kernel/verify.py NEW_ABSOLUTE_OUT [--quick]
Quick mode skips only inherited PR443 exhaustive controls. Apache-2.0.
Chafreaky with OpenAI Codex assistance.
"""
from pathlib import Path
import gzip,hashlib,json,os,shutil,subprocess,sys,time
assert __debug__
ROOT=Path(__file__).resolve().parent;out=Path(sys.argv[1]).resolve();quick='--quick' in sys.argv[2:]
assert not out.exists() and not out.is_relative_to(ROOT.parent)
ld=lambda p:json.loads(gzip.decompress(p.read_bytes())) if p.suffix=='.gz' else json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(p):return {f.relative_to(p).as_posix():sha(f) for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
def integrity():
 actual=inventory(ROOT);actual.pop('MANIFEST.json');assert actual==ld(ROOT/'MANIFEST.json')
 for name,expected in ld(ROOT/'SOURCE.json')['packages'].items():assert inventory(ROOT.parent/name)==expected['files'],name
integrity();out.mkdir(parents=True)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHON=sys.executable);env.pop('PYTHONOPTIMIZE',None);steps=[]
def py(name,path,*args,cwd=None):
 log=out/(name+'.log');start=time.monotonic();print('RUN',name,flush=True)
 with log.open('w') as f:r=subprocess.run([sys.executable,'-B',str(path),*map(str,args)],env=env,cwd=cwd,stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError((name,r.returncode,log.read_text()[-5000:]))
 steps.append(dict(name=name,seconds=round(time.monotonic()-start,2),log_sha256=sha(log)));print('PASS',name,flush=True)
def workspace(dst,word,source):
 (dst/'split-centres').mkdir(parents=True)
 shutil.copy2(word,dst/'split-centres/FULL-WORD.json.gz')
 for f in ['higher-stage-e8/verified/gcert1-e8-retimed.json.gz','odd-stages/clifford_exact.py']:
  target=dst/'work'/f;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/'work'/f,target)
try:
 py('parent454',ROOT.parent/'e8-target-mixing-whole/verify.py',out/'parent454',*(['--quick'] if quick else []))
 parent451=out/'parent454/parent451';source=parent451/'parent445/parent444/upstream442/parent/changed'
 baseline=out/'baseline';changed=out/'changed';local=changed/'split-centres';complex_out=out/'complex'
 workspace(baseline,source/'split-centres/FULL-WORD.json.gz',source)
 py('baseline-scalar',ROOT/'upstream449/audit_cxg.py',cwd=baseline)
 py('baseline-programs',ROOT/'upstream449/emit_cxg.py',cwd=baseline)
 a=ld(baseline/'split-centres/LOCAL-PROGRAMS.json.gz');b=ld(source/'split-centres/GLOBAL-TEMPLATE.json.gz')['local_programs'];assert a==b
 assert ld(baseline/'split-centres/LOCAL-CHECKS.json')==ld(source/'split-centres/LOCAL-CHECKS.json')
 ac=ld(baseline/'split-centres/CANONICAL-WORD.json.gz');bc=ld(source/'split-centres/CANONICAL-WORD.json.gz')
 assert ac.pop('target_levels')=={}
 ae=set(map(tuple,ac.pop('edges')));be=set(map(tuple,bc.pop('edges')));extra={(0,f) for f in ac['center_frames']}|{(f,0) for f in ac['center_frames']}
 assert ae==be|extra and ac==bc
 (out/'DEFAULT-REGRESSION.json').write_text(json.dumps(dict(status='PASS_FRESH_DEFAULT_LOCAL_PROGRAM_REGRESSION',local_programs_equal=True,local_checks_equal=True,canonical_only_differences=['empty target_levels metadata','explicit center directed edge inventory'],additional_edges=sorted(ae-be),fresh_program_sha256=sha(baseline/'split-centres/LOCAL-PROGRAMS.json.gz')),indent=2)+'\n')
 py('kernel-rebuild',ROOT/'code/rebuild.py',source/'split-centres/FULL-WORD.json.gz',out/'REBUILD.json')
 workspace(changed,ROOT/'data/word.json.gz',source)
 py('kernel-scalar',ROOT/'upstream449/audit_cxg.py',cwd=changed)
 py('kernel-programs',ROOT/'upstream449/emit_cxg.py',cwd=changed)
 py('kernel-exact-phases',ROOT/'upstream449/phases_cxg.py',cwd=changed)
 py('residual-adapters',ROOT/'code/adapters.py',local)
 py('independent-local-audit',ROOT/'code/local_audit.py',local)
 assert len(ld(local/'LOCAL-REVIEW.json')['mutations_rejected'])==7
 py('global-emit',ROOT/'code/emit.py',parent451/'complex',local,complex_out)
 py('independent-global-audit',ROOT/'code/audit.py',parent451/'complex',local,complex_out)
 assert len(ld(complex_out/'AUDIT.json')['mutations_rejected'])==25
 py('exact-assembly',ROOT/'code/assemble.py',out/'parent454',complex_out)
 (out/'RESULT.json').write_bytes((complex_out/'RESULT.json').read_bytes());result=ld(out/'RESULT.json')
 for k,v in ld(ROOT/'EXPECTED.json').items():assert result[k]==v,(k,result[k],v)
 integrity()
 receipt=dict(status='PASS_COMPLEX_ADAPTED_KERNEL_FULL_COMPOSITION',mode='quick' if quick else 'full',kappa=result['kappa'],manifest_sha256=sha(ROOT/'MANIFEST.json'),source_sha256=sha(ROOT/'SOURCE.json'),complex_emitted_program_sha256=result['complex_emitted_program_sha256'],checks=steps,python=sys.version.split()[0])
 (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
except BaseException as e:
 (out/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),completed=steps),indent=2)+'\n');raise
