"""Evidence/export checks: temporary copies only, no source-tree writes."""
from pathlib import Path
import gzip,hashlib,json,os,shutil,subprocess,sys,tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok,message):
    if not ok:raise ValueError(message)

def run(root,script,*args):
    return subprocess.run([sys.executable,'-I','-O','-B',str(root/'research/p104-two-target-native'/script),*map(str,args)],cwd=root,capture_output=True,text=True,encoding='utf8',timeout=300)

def tree(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in root.rglob('*')if p.is_file()}

def main():
    with tempfile.TemporaryDirectory(prefix='p104-native-export-')as tmp:
        root=Path(tmp)/'export';package=root/'research/p104-two-target-native'
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        for name in json.loads((HERE/'VERIFY.json').read_text())['inputs']:
            target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
        before=tree(root)
        positive=run(root,'verify.py');need(positive.returncode==0,positive.stdout+positive.stderr)
        need(tree(root)==before,'Git-free verification changed export bytes')
        # An actual live source mutation must reject before importing executables.
        path=root/'research/p104-native-channel/vendor/native_verify.py';saved=path.read_bytes()
        path.write_bytes(b'raise RuntimeError("untrusted mutated source executed")\n')
        fault=run(root,'verify.py');need(fault.returncode!=0 and 'source bytes' in fault.stderr and 'untrusted mutated source executed'not in fault.stderr,'source mutation did not fail before import')
        path.write_bytes(saved)
        evidence=package/'NATIVE.json.gz';saved=evidence.read_bytes();evidence.unlink()
        fault=run(root,'verify.py');need(fault.returncode!=0 and not evidence.exists(),'missing evidence regenerated')
        evidence.write_bytes(saved)
        generated=Path(tmp)/'native-regenerated.json.gz'
        replay=run(root,'compile.py','--out',generated);need(replay.returncode==0,replay.stdout+replay.stderr)
        need(json.loads(gzip.decompress(generated.read_bytes()))==json.loads(gzip.decompress(evidence.read_bytes())),'complete native regeneration differs')
        need(tree(root)==before,'regeneration changed export bytes')
    print('PASS_P104_NATIVE_EXPORT source_before_import missing_evidence readonly_export complete_regeneration')

if __name__=='__main__':main()
