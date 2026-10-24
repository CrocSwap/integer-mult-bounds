"""Portable exact replay of the repaired typed quotient. Apache-2.0.
Prepared for Dugongue with substantial OpenAI Codex assistance.
"""
from pathlib import Path
from hashlib import sha256
import gzip,json,subprocess,sys,tempfile,shutil
HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)

def hashes(root):
    manifest=json.loads((root/'CONTENT-HASHES.json').read_text(encoding='utf-8'))
    actual={str(p.relative_to(root)).replace('\\','/') for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=root/'CONTENT-HASHES.json'}
    need(actual==set(manifest),'Missing or unexpected package files')
    for name,h in manifest.items():need(sha256((root/name).read_bytes()).hexdigest()==h,'Changed source: '+name)
    return len(manifest)

def run(root,name,*args):
    r=subprocess.run([sys.executable,'-I','-B',str(root/name),*map(str,args)],cwd=root,text=True,encoding='utf-8',capture_output=True,timeout=180)
    need(r.returncode==0,name+' failed:\n'+r.stdout+'\n'+r.stderr)
    return r.stdout

def backward_check():
    # Exact Laurent-polynomial 2x2 matrices: Q and D are commuting,
    # invertible symmetric address operators on disjoint axes.
    def mono(q=0,d=0,c=1):return {(q,d):c} if c else {}
    def plus(a,b):
        z=dict(a)
        for k,v in b.items():z[k]=z.get(k,0)+v
        return {k:v for k,v in z.items() if v}
    def times(a,b):
        z={}
        for (q,d),v in a.items():
            for (r,e),w in b.items():
                k=(q+r,d+e);z[k]=z.get(k,0)+v*w
        return {k:v for k,v in z.items() if v}
    def matmul(a,b):return [[plus(times(a[i][0],b[0][j]),times(a[i][1],b[1][j])) for j in range(2)] for i in range(2)]
    def diag(a,b):return [[a,{}],[{},b]]
    I=diag(mono(),mono());controls=[]
    for kind in (0,1):
        F=[[mono(d=1),{}],[mono(q=kind-1,d=1),mono(q=kind,d=1)]]
        raw=[[mono(d=-1),mono(q=-1,d=-1,c=-1)],[{},mono(q=-kind,d=-1)]]
        transpose=[[F[j][i] for j in range(2)] for i in range(2)]
        need(matmul(transpose,raw)==I,'Exact raw inverse transpose')
        corrected=matmul(matmul(diag(mono(),mono(q=-2)),raw),diag(mono(),mono(q=2)))
        desired=[[mono(d=-1),mono(q=1,d=-1,c=-1)],[{},mono(q=-kind,d=-1)]]
        need(corrected==desired,'Explicit even-power monomial conjugation')
        need(matmul(transpose,desired)!=I,'Missing-conjugation control')
        controls.append('REJECTED')
    return dict(status='PASS_EXACT_LAURENT_BACKWARD_NORMALIZATION',types=2,missing_conjugation_controls=controls)

def check():
    count=hashes(HERE)
    if '--hash-only' in sys.argv:return {'status':'PASS_CONTENT_HASHES','files':count}
    with tempfile.TemporaryDirectory(prefix='typed-quotient-') as td:
        root=Path(td)/'package';shutil.copytree(HERE,root,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        outputs=['REPAIRED-WARP-WORD.json.gz','REPAIRED-WARP-PHASES.json.gz','TYPED-PAIR-NORMALIZERS.json.gz']
        before={f:gzip.decompress((root/f).read_bytes()) for f in outputs}
        run(root,'repair_shared_warps.py','--source-root',root/'v')
        run(root,'typed_pair_normalizers.py','--source-root',root/'v')
        for f,b in before.items():need(gzip.decompress((root/f).read_bytes())==b,'Fresh regenerated payload differs: '+f)
        rr=json.loads((root/'REPAIRED-WARP-RECEIPT.json').read_text())
        tr=json.loads((root/'TYPED-PAIR-RECEIPT.json').read_text())
        source=root/'v/research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py'
        phase=json.loads(run(root,'phase_form_check.py','--source',source))
        need(phase['lagrangians']==153 and phase['ordered_pairs']==18459,'Complete small phase-space census')
        # Mutate one mathematical input and one implementation source independently.
        controls={}
        for name in ['QUOTIENT-WORD.json.gz','v/research/fresh-helper-boundary/native.py']:
            f=root/name;b=f.read_bytes();f.write_bytes(b+b'\n')
            r=subprocess.run([sys.executable,'-I','-O','-B',str(root/'verify.py'),'--hash-only'],cwd=root,capture_output=True,timeout=30)
            need(r.returncode!=0,'Source drift accepted: '+name);controls[name]='REJECTED';f.write_bytes(b)
    return dict(backward_normalization=backward_check(),status='PASS_EXACT_TYPED_QUOTIENT_INTERFACE_NO_NEW_KAPPA',authenticated_files=count,regenerated_payloads=outputs,warp_classes=rr['actual_warp_classes'],typed_interface=tr,phase_charts=phase,drift_controls=controls,scope='Exact finite symbolic and Clifford certificates; universal all-fiber theorem is the supplied group-algebra and block-entry proof. No complete profitable controller or improved kappa.')
if __name__=='__main__':print(json.dumps(check(),indent=2))
