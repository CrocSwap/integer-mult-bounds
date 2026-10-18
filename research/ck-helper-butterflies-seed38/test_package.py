"""Optimized minimal relocation and four actual corrupted-package controls."""
from pathlib import Path
import json,subprocess,sys,tempfile,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,msg):
    if not ok:raise ValueError(msg)
def main():
    scratch=Path(tempfile.mkdtemp(prefix='butterfly-check-',dir=HERE)).resolve()
    need(scratch.parent==HERE,'scratch containment')
    try:
        package=scratch/'research'/HERE.name;package.mkdir(parents=True)
        for name in ('verify.py','independent.py','SOURCES.json','WITNESS.json','CERTIFICATE.json'):
            shutil.copyfile(HERE/name,package/name)
        manifest=json.loads((HERE/'SOURCES.json').read_bytes())
        for name in manifest['files']:
            p=scratch/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
        def call(success=True):
            result=subprocess.run([sys.executable,'-I','-O','-B',str(package/'verify.py')],cwd=scratch,capture_output=True,text=True)
            need((result.returncode==0)==success,'unexpected acceptance '+result.stdout+result.stderr)
        call()
        originals={n:(package/n).read_bytes() for n in ('SOURCES.json','WITNESS.json','CERTIFICATE.json')}
        def mutation(name,value):
            (package/name).write_text(json.dumps(value),encoding='utf8');call(False);(package/name).write_bytes(originals[name])
        m=json.loads(originals['SOURCES.json']);m['files'].pop(next(iter(m['files'])));mutation('SOURCES.json',m)
        w=json.loads(originals['WITNESS.json']);w['butterfly_matching']['pairs'].append(w['butterfly_matching']['pairs'][0]);mutation('WITNESS.json',w)
        c=json.loads(originals['CERTIFICATE.json']);c['complete_scalar_programs']['butterfly']['forward']['columns']=True;mutation('CERTIFICATE.json',c)
        p=scratch/next(iter(manifest['files']));raw=p.read_bytes();p.write_bytes(raw[:-1]+bytes([raw[-1]^1]));call(False);p.write_bytes(raw)
        print('PASS_CK_BUTTERFLY_PACKAGE relocation=1 corruptions=4')
    finally:
        need(scratch.parent==HERE and scratch.name.startswith('butterfly-check-'),'cleanup containment');shutil.rmtree(scratch)
if __name__=='__main__':main()
