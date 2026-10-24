"""Portable exact source-bound transfer checks. Apache-2.0.
Dugongue with substantial OpenAI Codex assistance. This does not establish the
inherited all-fiber, compiler, conditioning, analytic or recovery premises.
"""
from pathlib import Path
from hashlib import sha256
import json,subprocess,sys,tempfile,shutil
ROOT=Path(__file__).resolve().parent

def need(ok,why):
    if not ok:raise ValueError(why)

def authenticate(root):
    manifest=json.loads((root/'CONTENT-HASHES.json').read_bytes())
    actual={str(f.relative_to(root)).replace(chr(92),'/') for f in root.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f!=root/'CONTENT-HASHES.json'}
    need(actual==set(manifest),'Unexpected or missing package files')
    for n,h in manifest.items():need(sha256((root/n).read_bytes()).hexdigest()==h,'Source drift: '+n)
    return len(manifest)

def run(script,cache):
    r=subprocess.run([sys.executable,'-I','-B','-X','pycache_prefix='+str(cache),str(ROOT/script)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=180)
    need(r.returncode==0,script+' failed: '+r.stdout+' '+r.stderr)
    return json.loads(r.stdout)

def check():
    count=authenticate(ROOT)
    if '--hash-only' in sys.argv:return {'status':'PASS_COMPLETE_PACKAGE_HASHES','files':count}
    scripts=['transfer/verify.py','native-runtime/check_division.py','formal/check_newton_review.py','formal/check_lanes.py','formal/check_relocation.py','literature/verify_normalization.py','literature/verify_boundary.py']
    with tempfile.TemporaryDirectory(prefix='native-transfer-check-') as td:
        temp=Path(td);results={s:run(s,temp/('pycache-'+str(i))) for i,s in enumerate(scripts)}
        scratch=temp/'controls';shutil.copytree(ROOT,scratch,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        def control():return subprocess.run([sys.executable,'-I','-O','-B','-X','pycache_prefix='+str(temp/'control-cache'),str(scratch/'verify.py'),'--hash-only'],cwd=scratch,capture_output=True,timeout=30).returncode
        need(control()==0,'Unmodified control baseline must accept')
        controls={}
        for n in ['transfer/LATEST-ARITHMETIC.json','transfer/critical_engine.py']:
            f=scratch/n;b=f.read_bytes();f.write_bytes(b+bytes([10]))
            need(control()!=0,'Corrupted source accepted: '+n);f.write_bytes(b);need(control()==0,'Restored baseline must accept');controls[n]='REJECTED'
    need(results['transfer/verify.py']['word_ram_kappa']=='15108879/5000000000','Exact target changed')
    return {'status':'PASS_CONDITIONAL_DIVISION_FREE_NATIVE_TRANSFER','word_ram_kappa':'0.0030217758','previous_native_kappa':'0.0030217754','native_gain':'0.0000000004','paid_profile_changed':False,'new_global_raw_root_claimed':False,'authenticated_files':count,'components':results,'source_corruption_controls':controls,'scope':'Fresh exact arithmetic and finite component replays plus informal universal proofs. Inherited all-fiber, native phase, whole-job, compiler, conditioning, analytic and recovery premises remain explicit. No new Lean audit or complete executable multiplier.'}
if __name__=='__main__':print(json.dumps(check(),indent=2))
