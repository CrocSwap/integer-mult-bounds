"""Exact portable replay; Apache-2.0. Dugongue with OpenAI Codex assistance."""
from pathlib import Path
from hashlib import sha256
from concurrent.futures import ThreadPoolExecutor
import json,gzip,subprocess,sys,tempfile,shutil
H=Path(__file__).resolve().parent

def need(ok,why):
    if not ok:raise ValueError(why)

def authenticate(root):
    m=json.loads((root/'CONTENT-HASHES.json').read_text())
    actual={str(p.relative_to(root)).replace('\\','/') for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=root/'CONTENT-HASHES.json'}
    need(actual==set(m),'Unexpected or missing files')
    for n,h in m.items():need(sha256((root/n).read_bytes()).hexdigest()==h,'Source drift: '+n)
    return len(m)

def run(root,script):
    r=subprocess.run([sys.executable,'-I','-B',str(root/script),'--source-root',str(root/'v')],cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=650)
    need(r.returncode==0,script+' failed:\n'+r.stdout+'\n'+r.stderr)

def pipeline(kind,folder):
    root=folder/kind;shutil.copytree(H,root,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    if kind=='C':
        scripts=['intersection_newer_base.py','admit_newer_base.py','admit_newer_main.py'];prefix='INTERSECTION153-ROUND3'
    else:
        scripts=['quotient_newer_base.py','admit_newer_quotient.py','admit_newer_quotient_main.py'];prefix='QUOTIENT153-ROUND3'
    names=[prefix+s for s in ['-ACTUAL-WORD.json.gz','-MAIN-NORMALIZERS.json.gz','-WARP-PHASES.json.gz','-PAID-HELPER-PHASES.json.gz']]
    original={n:gzip.decompress((root/n).read_bytes()) for n in names}
    for script in scripts:run(root,script)
    for n,b in original.items():need(gzip.decompress((root/n).read_bytes())==b,'Regenerated mathematical payload differs: '+n)
    receipt=json.loads((root/(prefix+'-MAIN-RECEIPT.json')).read_text())
    return dict(provider=kind,regenerated_payloads=names,receipt=receipt)

def check():
    count=authenticate(H)
    if '--hash-only' in sys.argv:return dict(status='PASS_CONTENT_HASHES',files=count)
    with tempfile.TemporaryDirectory(prefix='native-dual-') as td:
        folder=Path(td)
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda k:pipeline(k,folder),['B','C']))
        # Corruption checks run against a scratch copy, including optimized entry.
        root=folder/'controls';shutil.copytree(H,root,ignore=shutil.ignore_patterns('__pycache__','*.pyc'));controls={}
        baseline=subprocess.run([sys.executable,'-I','-O','-B',str(root/'verify.py'),'--hash-only'],cwd=root,capture_output=True,timeout=30)
        need(baseline.returncode==0,'Unmodified control baseline rejected')
        for name in ['BASE-ROUND3-WORD.json.gz','v/research/fresh-helper-boundary/native.py']:
            f=root/name;b=f.read_bytes();f.write_bytes(b+b'\n')
            r=subprocess.run([sys.executable,'-I','-O','-B',str(root/'verify.py'),'--hash-only'],cwd=root,capture_output=True,timeout=30)
            need(r.returncode!=0,'Corrupted source accepted: '+name);f.write_bytes(b);controls[name]='REJECTED'
        # Receipts contain regenerated times; payload equality is checked separately.
    return dict(status='PASS_COMPLETE_NATIVE_DUAL_SUPPLIERS_NO_NEW_KAPPA',authenticated_files=count,providers=results,controls=controls,scope='Exact source/Clifford/formal-word certificates plus supplied all-f proofs. No profitable complete controller or improved multiplication kappa.')
if __name__=='__main__':print(json.dumps(check(),indent=2))
