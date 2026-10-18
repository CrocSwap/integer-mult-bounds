"""Optimized relocation and on-disk rejection controls for the finite package."""
from pathlib import Path
import json,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,msg):
    if not ok:raise ValueError(msg)
def main():
    scratch=Path(tempfile.mkdtemp(prefix='probe-check-',dir=HERE)).resolve()
    need(scratch.parent==HERE,'temporary path containment')
    try:
        package=scratch/'research'/HERE.name;package.mkdir(parents=True)
        for name in ('verify.py','independent.py','find.py','SOURCES.json','WITNESS.json','CERTIFICATE.json'):
            shutil.copyfile(HERE/name,package/name)
        manifest=json.loads((HERE/'SOURCES.json').read_bytes())
        for name in manifest['files']:
            target=scratch/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
        def call(*args,success=True):
            p=subprocess.run([sys.executable,'-I','-O','-B',str(package/'verify.py'),*args],cwd=scratch,capture_output=True,text=True)
            need((p.returncode==0)==success,'unexpected process result '+p.stdout+p.stderr)
        call()
        original={name:(package/name).read_bytes() for name in ('CERTIFICATE.json','WITNESS.json','SOURCES.json')}
        call('--write-certificate')
        need(json.loads((package/'CERTIFICATE.json').read_bytes())==json.loads(original['CERTIFICATE.json']),'regeneration mismatch')
        corruptions=[]
        def mutate(name,value,label):
            (package/name).write_text(json.dumps(value),encoding='utf8');call(success=False)
            (package/name).write_bytes(original[name]);corruptions.append(label)
        c=json.loads(original['CERTIFICATE.json']);c['minimum_probes']=1;mutate('CERTIFICATE.json',c,'claimed minimum')
        c=json.loads(original['CERTIFICATE.json']);c['expanded_ADDs']=True;mutate('CERTIFICATE.json',c,'Boolean count')
        c=json.loads(original['CERTIFICATE.json']);c['two_omission_blind_witness']['input_register']=229;mutate('CERTIFICATE.json',c,'false pair witness')
        w=json.loads(original['WITNESS.json']);w['probes'][0]=w['probes'][1];mutate('WITNESS.json',w,'repeated probe')
        m=json.loads(original['SOURCES.json']);m['files'].pop(next(iter(m['files'])));mutate('SOURCES.json',m,'missing pin')
        (package/'CERTIFICATE.json').write_text('{"minimum_probes":2,"minimum_probes":1}',encoding='utf8');call(success=False)
        (package/'CERTIFICATE.json').write_bytes(original['CERTIFICATE.json']);corruptions.append('duplicate certificate key')
        name=next(iter(manifest['files']));raw=(scratch/name).read_bytes();(scratch/name).write_bytes(raw[:-1]+bytes([raw[-1]^1]));call(success=False)
        (scratch/name).write_bytes(raw);corruptions.append('corrupted source')
        # Discovery is deterministic but never part of default acceptance.
        p=subprocess.run([sys.executable,'-I','-B',str(package/'find.py')],cwd=scratch,capture_output=True,text=True)
        need(p.returncode==0,'discovery replay failed')
        need(json.loads((package/'WITNESS.json').read_bytes())==json.loads(original['WITNESS.json']),'discovery witness mismatch')
        print('PASS_R439_PROBE_PACKAGE relocation=1 regeneration=1 discovery=1 corruptions='+str(len(corruptions)))
    finally:
        need(scratch.parent==HERE and scratch.name.startswith('probe-check-'),'cleanup containment')
        shutil.rmtree(scratch)
if __name__=='__main__':main()
