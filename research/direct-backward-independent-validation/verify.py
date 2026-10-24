#!/usr/bin/env python3
"""Serial independent review replay with immutable inputs and private outputs."""
import sys
# Builtin-only bootstrap: isolate Python's path before loading any nonbuiltin
# module. A rogue json.py/hashlib.py or legacy .pyc beside this script cannot
# execute before the package inventory guard rejects it.
if not sys.flags.isolated:
    import posix
    _flags=['-O']*sys.flags.optimize
    posix.execv(sys.executable,[sys.executable,'-I',*_flags,'-B',sys.argv[0],*sys.argv[1:]])
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

_CACHE=tempfile.TemporaryDirectory(prefix='direct-backward-bootstrap-cache-')
sys.pycache_prefix=_CACHE.name
sys.dont_write_bytecode=True
HERE=Path(__file__).absolute().parent
# The committed/exported wrapper is the trust anchor. Final freeze fills hashes.
BOOTSTRAP={'source_guard.py': '3c0c94897b224d702dc322cd6568e3f2dc8bbf75ad60a0d26a6d3e3084c3a654', 'receipt_guard.py': '455d6ab38f259d4b5ec1515918f4185670aee2cdefe2f81713423319d96a8a70'}
MANIFEST_SHA256='f1bea22a358c338d15bbf06cd5e0b6126e87c3cf3c43d7ca6d28c900ffb75635'
COMMANDS_SHA256='c1e6bc787b59f590385a32445d0250798a4090021d95166ddaf07aebc430d140'
_helpers={};_authenticated={}
for _ancestor in [HERE,*HERE.parents]:
    if _ancestor.is_symlink():raise ValueError('Symlink package ancestor: '+str(_ancestor))
# Authenticate both helpers completely before executing either one.
for _name,_digest in BOOTSTRAP.items():
    _path=HERE/_name
    if _path.is_symlink() or not _path.is_file() or _path.stat().st_nlink!=1:raise ValueError('Missing or aliased helper: '+_name)
    _raw=_path.read_bytes()
    if hashlib.sha256(_raw).hexdigest()!=_digest:raise ValueError('Changed helper bytes: '+_name)
    _authenticated[_name]=(_path,_raw)
for _name,(_path,_raw) in _authenticated.items():
    _namespace={'__name__':'_authenticated_'+_name.removesuffix('.py'),'__file__':str(_path)}
    exec(compile(_raw,str(_path),'exec'),_namespace)
    _helpers[_name]=_namespace
if set(_helpers)!={'source_guard.py','receipt_guard.py'}:raise ValueError('Package freeze is incomplete')
check=_helpers['source_guard.py']['check'];require=_helpers['source_guard.py']['require'];validate=_helpers['receipt_guard.py']['validate']

def prepare_scratch(source,destination):
    shutil.copytree(source,destination,dirs_exist_ok=True)
    destination.chmod(0o700)
    for path in destination.rglob('*'):
        if path.is_dir():path.chmod(0o700)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--bindings-only',action='store_true');ap.add_argument('--output',type=Path);args=ap.parse_args()
    require(hashlib.sha256((HERE/'SOURCE-BINDINGS.json').read_bytes()).hexdigest()==MANIFEST_SHA256,'Changed binding manifest')
    require(hashlib.sha256((HERE/'COMMANDS.json').read_bytes()).hexdigest()==COMMANDS_SHA256,'Changed scientific schedule')
    before=check(HERE)
    if args.bindings_only:print(json.dumps({'status':before['status'],'files':before['files']}));return
    claims=json.loads((HERE/'CLAIMS.json').read_bytes())
    require(claims['review_status']=='READY_FOR_COLD_REPLAY','Scientific freeze is incomplete')
    schedule=(HERE/'COMMANDS.json').read_bytes()
    require(hashlib.sha256(schedule).hexdigest()==COMMANDS_SHA256,'Changed scientific schedule')
    commands=json.loads(schedule)['commands'];require(len(commands)==3,'Fresh caller, numeric and precision commands required')
    root=Path(tempfile.mkdtemp(prefix='direct-backward-replay-'))
    destination=(args.output or root/'REPLAY.json').absolute()
    for component in [destination,*destination.parents]:require(not component.is_symlink(),'Symlink output component: '+str(component))
    require(not destination.exists() or destination.is_file() and destination.stat().st_nlink==1,'Aliased output file')
    destination=destination.resolve();require(not destination.is_relative_to(HERE.resolve()),'Receipt must stay outside frozen package')
    report={'status':'RUNNING','optimization':sys.flags.optimize,'bindings':before,'runs':[],'python':sys.version,'scratch':str(root)}
    try:
        prepare_scratch(HERE/'capsule',root)
        manifest=json.loads((HERE/'SOURCE-BINDINGS.json').read_bytes())
        for row in manifest['files']:
            if row['path'].startswith('capsule/'):
                target=root/row['path'].removeprefix('capsule/')
                require(hashlib.sha256(target.read_bytes()).hexdigest()==row['sha256'],'Scratch input changed')
        for index,command in enumerate(commands):
            cache=root/f'cache-{index}';cache.mkdir()
            env=os.environ.copy()
            for key in ('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','PYTHONSTARTUP','PYTHONINSPECT'):env.pop(key,None)
            env['PYTHONPYCACHEPREFIX']=str(cache);env['PYTHONDONTWRITEBYTECODE']='1'
            flags=['-O']*sys.flags.optimize
            argv=[sys.executable,*flags,'-B','-X','pycache_prefix='+str(cache),*command['argv']]
            started=time.monotonic();run=subprocess.run(argv,cwd=root,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=command['timeout_seconds'])
            (root/f'run-{index}.stdout').write_text(run.stdout);(root/f'run-{index}.stderr').write_text(run.stderr)
            report['runs'].append({'name':command['name'],'argv':argv,'returncode':run.returncode,'seconds':time.monotonic()-started,'stdout_sha256':hashlib.sha256(run.stdout.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(run.stderr.encode()).hexdigest()})
            require(run.returncode==0,'Scientific replay failed: '+command['name']+'; see '+str(root/f'run-{index}.stderr'))
        report['fresh_scientific_summary']=validate(root,claims,before)
        require(before==check(HERE),'Frozen package changed during replay')
        report['status']='PASS_INDEPENDENT_DIRECT_BACKWARD_SAME_PREMISES'
        report['limits']=['Five literal framework premises remain required.','Unchanged PR5383 supplier proofs and historical native/BIT sources are authenticated reuse.','No unconditional theorem, formal-kernel acceptance, practical speedup or selected-record promotion.']
    except BaseException as error:
        report['status']='FAIL';report['error']=repr(error);raise
    finally:
        destination.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w',dir=destination.parent,prefix='.direct-backward-receipt-',delete=False) as output:
            output.write(json.dumps(report,indent=2,sort_keys=True)+'\n');temporary=Path(output.name)
        os.replace(temporary,destination)
        print(json.dumps({'status':report['status'],'receipt':str(destination),'scratch':str(root)}))

if __name__=='__main__':main()
