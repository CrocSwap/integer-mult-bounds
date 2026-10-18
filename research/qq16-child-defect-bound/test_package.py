"""Git-free relocation, read-only replay and real source/receipt corruption."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def invoke(p,ok,phrase,auth=False):
    args=[sys.executable,'-I','-O','-B',str(p/'verify.py')]
    if auth:args+=['--authenticate-only']
    run=subprocess.run(args,capture_output=True,text=True,timeout=300)
    if (run.returncode==0)!=ok or phrase not in run.stdout+run.stderr:raise ValueError(run.stdout+run.stderr)
def hashes(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
def main():
    with tempfile.TemporaryDirectory(prefix='qq16-defect-') as temp:
        root=Path(temp);p=root/'research/qq16-child-defect-bound'
        shutil.copytree(HERE,p,ignore=shutil.ignore_patterns('__pycache__'))
        manifest=json.loads((HERE/'SOURCES.json').read_text())
        for row in manifest['files']:
            if row['usage']=='input':
                dst=root/row['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['path'],dst)
        before=hashes(root);invoke(p,True,'PASS_QQ16_CHILD_DEFECT')
        if hashes(root)!=before:raise ValueError('normal replay wrote files')
        row=next(r for r in manifest['files'] if r['usage']=='input')
        for path,message in [(root/row['path'],'input hash'),(p/'vendor/pr2540/verify.py','snapshot hash')]:
            raw=path.read_bytes();path.write_bytes(raw+b'\nraise RuntimeError("MUST_NOT_EXECUTE")\n')
            invoke(p,False,message,True);path.write_bytes(raw)
        path=p/'RESULT.json';raw=path.read_bytes();value=json.loads(raw);value['schema_version']=True
        path.write_text(json.dumps(value),encoding='utf-8');invoke(p,False,'typed complete receipt');path.write_bytes(raw)
    print('PASS_QQ16_DEFECT_PACKAGE Git-free/read-only replay;3 source/typed-receipt corruptions')
if __name__=='__main__':main()
