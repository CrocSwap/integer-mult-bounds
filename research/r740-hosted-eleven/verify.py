"""Fresh PR444 reconstruction, eleven-stage geometry, hosted ownership and exact composition.
Usage: python -B research/r740-hosted-eleven/verify.py /absolute/new/output [--quick]
--quick skips only PR443's already-inherited exhaustive negative controls.
Apache-2.0; chafreaky with OpenAI Codex assistance.
"""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
assert __debug__
ROOT=Path(__file__).resolve().parent
out=Path(sys.argv[1]).resolve();quick='--quick' in sys.argv[2:]
assert not out.exists() and not out.is_relative_to(ROOT.parent)
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(p):
    return {f.relative_to(p).as_posix():sha(f) for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
def integrity():
    actual=inventory(ROOT);actual.pop('MANIFEST.json')
    assert actual==read(ROOT/'MANIFEST.json'),'package manifest differs'
    for name,expected in read(ROOT/'SOURCE.json')['packages'].items():
        assert inventory(ROOT.parent/name)==expected['files'],('upstream package differs',name)
integrity();out.mkdir(parents=True)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHON=sys.executable)
env.pop('PYTHONOPTIMIZE',None);steps=[]
def run(name,cmd):
    log=out/(name+'.log');t=time.monotonic();print('RUN',name,flush=True)
    with log.open('w') as f:q=subprocess.run(list(map(str,cmd)),env=env,stdout=f,stderr=subprocess.STDOUT)
    if q.returncode:raise RuntimeError((name,q.returncode,log.read_text()[-4000:]))
    steps.append(dict(name=name,seconds=round(time.monotonic()-t,2),log_sha256=sha(log)))
    print('PASS',name,flush=True)
def py(name,path,*args):run(name,[sys.executable,'-B',path,*args])
try:
    args=['--quick'] if quick else []
    py('parent444',ROOT.parent/'r740-idle-hosted-replicas/verify.py',out/'parent444',*args)
    base=out/'parent444/base443/candidate';host=out/'bit'
    py('geometry',ROOT/'code/geometry.py','--source',ROOT.parent/'e8-r740-replica32/parent436','--out',host)
    py('emit',ROOT/'code/emit.py','--word',ROOT.parent/'e8-r740-replica32/data/word.json.gz',
       '--local-check',base,'--out',host,'--isometries',ROOT.parent/'e8-r740-replica32/data/residual-isometries.json')
    py('independent-audit',ROOT/'code/audit.py',base,host)
    assert len(read(host/'AUDIT.json')['mutations_rejected'])==22
    py('exact-assembly',ROOT/'code/assemble.py',out/'parent444',host)
    (out/'RESULT.json').write_bytes((host/'RESULT.json').read_bytes())
    actual=read(out/'RESULT.json')
    for k,v in read(ROOT/'EXPECTED.json').items():assert actual[k]==v,(k,actual[k],v)
    integrity()
    receipt=dict(status='PASS_R740_ELEVEN_STAGE_HOSTING',mode='quick' if quick else 'full',kappa=actual['kappa'],
                 manifest_sha256=sha(ROOT/'MANIFEST.json'),source_sha256=sha(ROOT/'SOURCE.json'),
                 emitted_program_sha256=actual['emitted_program_sha256'],checks=steps,python=sys.version.split()[0])
    (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
except BaseException as e:
    (out/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),completed=steps),indent=2)+'\n');raise
