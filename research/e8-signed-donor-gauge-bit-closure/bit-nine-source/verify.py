#!/usr/bin/env python3
"""Fresh offline reconstruction of both suppliers and their combined bound."""
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path
assert __debug__ and sys.version_info>=(3,11)
ROOT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def files(root):
    return {p.relative_to(root).as_posix():sha(p) for p in root.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}

ap=argparse.ArgumentParser(); ap.add_argument('--work',type=Path,required=True)
ap.add_argument('--bit-source',type=Path,default=ROOT.parent/'e8-bit')
ap.add_argument('--complex-source',type=Path,default=ROOT.parent/'nine-stage-complex-e8')
a=ap.parse_args(); wd=a.work.resolve(); bit=a.bit_source.resolve(); cx=a.complex_source.resolve()
assert not wd.exists() and not wd.is_relative_to(ROOT)
own=files(ROOT); own.pop('MANIFEST.json'); assert own==read(ROOT/'MANIFEST.json')['files']
pins=read(ROOT/'PINS.json')
assert files(bit)==pins['bit_files'] and sha(cx/'MANIFEST.json')==pins['complex_manifest_sha256']
assert not any(p.is_symlink() for p in ROOT.rglob('*'))
wd.mkdir(); (wd/'logs').mkdir(); steps=[]; started=time.monotonic()
env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'
env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env.get('PATH','')
includes=[str(ROOT/'portable-include')]
for p in ('/usr/local/include','/opt/homebrew/include'):
    if Path(p).is_dir(): includes.append(p)
if env.get('CPLUS_INCLUDE_PATH'): includes.append(env['CPLUS_INCLUDE_PATH'])
env['CPLUS_INCLUDE_PATH']=os.pathsep.join(includes)
def run(name,cmd):
    print(name,flush=True); start=time.monotonic(); log=wd/'logs'/(name+'.log')
    with log.open('w') as f: r=subprocess.run(cmd,cwd=wd,env=env,stdout=f,stderr=subprocess.STDOUT)
    assert r.returncode==0,(name,r.returncode,str(log))
    steps.append(dict(stage=name,returncode=0,seconds=time.monotonic()-start,log_sha256=sha(log)))
try:
    run('pinned-pr370-full-rebuild',['bash',str(bit/'verify.sh'),str(wd/'bit-local')])
    run('pinned-pr377-full-rebuild',[sys.executable,'-B',str(cx/'verify.py'),'--work',str(wd/'complex')])
    for name,script,args in [
        ('compressed-bit-geometry','geometry.py',['--source',str(bit),'--out',str(wd/'bit-nine')]),
        ('source-bound-bit-word','global_word.py',['--source',str(bit),'--local-check',str(wd/'bit-local'),'--out',str(wd/'bit-nine')]),
        ('independent-bit-template-audit','audit.py',['--local-check',str(wd/'bit-local'),'--out',str(wd/'bit-nine')]),
        ('two-moments-finite-bill-combined-assembly','certify.py',['--source',str(bit),'--out',str(wd/'bit-nine'),'--complex-check',str(wd/'complex')])]:
        run(name,[sys.executable,'-B',str(ROOT/script)]+args)
    result=read(wd/'bit-nine/COMBINED.json')
    assert result['status']=='PASS_CONDITIONAL_COMBINED_KAPPA_ABOVE_2_POW_MINUS_10'
    assert result['kappa']=='998243154231047/1000000000000000000'
    receipt=dict(status='PASS_FRESH_CONDITIONAL_E8_BIT_COMPLEX_NINE',source_manifest_sha256=sha(ROOT/'MANIFEST.json'),
                 pins_sha256=sha(ROOT/'PINS.json'),stages=steps,combined=result,
                 final_receipt_sha256=sha(wd/'bit-nine/COMBINED.json'),seconds=time.monotonic()-started,
                 scope='Offline fresh reconstruction. All inherited supplier/compiler/precision/analytic obligations remain explicit in PROOF.txt. No Lean or priority claim.')
    (wd/'VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'],result['kappa'],flush=True)
except BaseException as e:
    (wd/'FAILURE.json').write_text(json.dumps(dict(error=str(e),completed=steps),indent=2)+'\n')
    raise
