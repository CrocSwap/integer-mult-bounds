"""Fresh PR445 reconstruction, rank151 local records, residual projectors and exact composition.
Usage: python -B research/r740-hosted-rank151/verify.py /absolute/new/output [--quick]
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
    py('parent445',ROOT.parent/'r740-hosted-eleven/verify.py',out/'parent445',*args)
    old=ROOT.parent/'e8-r740-replica32';B=old/'parent436/code/bit'
    base=out/'local';host=out/'bit';word=ROOT/'data/word.json.gz'
    bins=out/'parent445/parent444/base443/parent/bin'
    py('rebuild',ROOT/'code/rebuild.py')
    py('export-records',B/'export_records.py',word,base/'records')
    py('stage-cohort',B/'regression/stage_cohort.py',base/'records',base/'records',base/'cin',base/'cout')
    run('official-legality',[bins/'legality',base/'cin',base/'cout',base/'cout/legality.json'])
    run('official-columns',[bins/'columns_h',base/'cout/COHORT249-RECORDS.bin',base/'cout/columns.json'])
    run('official-k4-columns',[bins/'columns_k4',base/'cout/COHORT249-RECORDS.bin',base/'cout/columns_k4.json'])
    py('record-mutations',B/'mutate_records.py',base/'records',base/'cin',base/'cout',bins/'legality',bins/'columns_k4',bins/'legality_ncopy_h')
    py('positive-gram',B/'checkers/gram_frames.py',base/'records','--gram','e8ham','--h',8,'--positive')
    py('geometry',ROOT/'code/geometry.py','--source',ROOT.parent/'e8-r740-replica32/parent436','--out',host)
    py('emit',ROOT/'code/emit.py','--word',word,
       '--local-check',base,'--out',host,'--isometries',ROOT/'data/residual-isometries.json')
    py('independent-audit',ROOT/'code/audit.py',base,out/'parent445/parent444/base443/candidate/nine',host)
    assert len(read(host/'AUDIT.json')['mutations_rejected'])==22
    complex_out=out/'complex';complex_out.mkdir()
    canonical=out/'parent445/parent444/upstream442/parent/changed/split-centres/CANONICAL-WORD.json.gz'
    py('complex-phases',ROOT/'code/complex_phases.py',canonical,complex_out/'DATA-PHASES.json')
    py('complex-emit',ROOT/'code/complex_emit.py',out/'parent445',complex_out)
    py('complex-independent-audit',ROOT/'code/complex_audit.py',out/'parent445',complex_out)
    assert len(read(complex_out/'AUDIT.json')['mutations_rejected'])==19
    py('exact-assembly',ROOT/'code/assemble.py',out/'parent445',host,complex_out)
    (out/'RESULT.json').write_bytes((host/'RESULT.json').read_bytes())
    actual=read(out/'RESULT.json')
    for k,v in read(ROOT/'EXPECTED.json').items():assert actual[k]==v,(k,actual[k],v)
    integrity()
    receipt=dict(status='PASS_DUAL_ELEVEN_RANK151_HOSTING',mode='quick' if quick else 'full',kappa=actual['kappa'],
                 manifest_sha256=sha(ROOT/'MANIFEST.json'),source_sha256=sha(ROOT/'SOURCE.json'),
                 emitted_program_sha256=actual['emitted_program_sha256'],checks=steps,python=sys.version.split()[0])
    (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
except BaseException as e:
    (out/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),completed=steps),indent=2)+'\n');raise
