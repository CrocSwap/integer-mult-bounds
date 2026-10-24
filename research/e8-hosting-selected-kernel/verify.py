"""Full rank-138 / idle-hosting composition; Python 3.11+, standard library.
Rebuild the full R740/complex parent, reconstruct the hosting-selected kernel, emit and audit
64 bit replicas, then host both suppliers. Complex replication remains eight.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
import gzip, hashlib, json, os, subprocess, sys, time
assert __debug__
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'e8-rank138-idle-hosting'
ORIGINAL=ROOT.parent/'e8-joint-frame-retiming'
OUT=Path(sys.argv[1]).resolve()
assert not OUT.exists() and not OUT.is_relative_to(ROOT.parent)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def integrity():
    m=read(ROOT/'MANIFEST.json')
    actual={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'MANIFEST.json' and '__pycache__' not in p.parts}
    assert actual==m['files']
    assert sha(PARENT/'MANIFEST.json')==m['parent_manifest_sha256']
integrity();OUT.mkdir(parents=True)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
steps=[]
def run(name,file,*args,cwd=None):
    log=OUT/(name+'.log');start=time.monotonic();print('RUN',name,flush=True)
    with log.open('w') as f:q=subprocess.run([sys.executable,'-B',str(file),*map(str,args)],cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT)
    assert q.returncode==0,(name,log.read_text()[-3000:])
    steps.append(dict(name=name,seconds=round(time.monotonic()-start,2),log_sha256=sha(log)))
    print('PASS',name,flush=True)
try:
    run('parent-full',PARENT/'verify.py',OUT/'parent')
    changed=OUT/'changed';changed.mkdir()
    for d in ('work','inherited','split-centres'):
        (changed/d).symlink_to(OUT/'parent/changed'/d,target_is_directory=True)
    b=changed/'bit426-source-centres'
    run('kernel-rebuild',ROOT/'rebuild.py',b)
    run('export-records',ORIGINAL/'vendor/export_records.py',b/'bit-source-centres.json',b/'records')
    run('bit-global-64',ROOT/'code/bit_global.py','--source',b,'--local-check',b,'--out',b/'global',cwd=changed)
    run('bit-global-audit',ROOT/'code/bit_audit.py','--local-check',b,'--out',b/'global',cwd=changed)
    run('bit-hosting',ROOT/'code/bit_hosted.py',b/'global',b,OUT/'bit',cwd=changed)
    run('complex-hosting',ROOT/'code/complex_hosted.py',changed/'split-centres',OUT/'complex',cwd=changed)
    run('independent-hosting-audit',ROOT/'code/audit.py',changed,OUT/'bit',OUT/'complex',OUT/'AUDIT.json')
    run('exact-assembly',ROOT/'code/assemble.py',changed,OUT/'bit',OUT/'complex',OUT/'AUDIT.json',OUT/'RESULT.json')
    actual=read(OUT/'RESULT.json')
    for k,v in read(ROOT/'EXPECTED.json').items():assert actual[k]==v,(k,actual[k],v)
    integrity()
    receipt=dict(status='PASS_FULL_HOSTING_SELECTED_KERNEL',python=sys.version.split()[0],kappa=actual['kappa'],kappa_decimal=actual['kappa_decimal'],manifest_sha256=sha(ROOT/'MANIFEST.json'),checks=steps)
    (OUT/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
except BaseException as e:
    (OUT/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),completed=steps),indent=2)+'\n');raise
