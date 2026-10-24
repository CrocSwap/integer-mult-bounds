#!/usr/bin/env python3
"""Authenticate the frozen capsule and replay scoped independent engines serially."""
import sys
if not sys.flags.isolated:
    import posix
    posix.execv(sys.executable,[sys.executable,'-I',*(['-O']*sys.flags.optimize),'-B',*sys.argv])
import argparse,hashlib,json,os,shutil,subprocess,tempfile,time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).absolute().parent
BOOTSTRAP={'source_guard.py': '1b7b89c87d89a595b501adbc1afcfa477f3eee10e87a4fe8e6b1f2b693fda2ba', 'receipt_guard.py': '367e385862c9c8a907dbd95b9cc83934420bd518cc8bee263dcff68732785c35', 'engine_adapter.py': '4a3de4a9ca3d65d0485826aa17368789015af7815e7febd74d335302b7dfb42b'}
MANIFEST_SHA256='ea8ea2ff3db043d33ec3f4ea84f9ab760950eea1768f8a5ee9db91d0abb840e3'
COMMANDS_SHA256='a0de48101c6b8f8771c2d54a762feccf0f2be6c21b078c0d24d1341434ca3fd5'
def need(ok,message):
    if not ok:raise ValueError(message)
for part in [HERE,*HERE.parents]:need(not part.is_symlink(),'Symlink package ancestor')
for name,digest in [('SOURCE-BINDINGS.json',MANIFEST_SHA256),('COMMANDS.json',COMMANDS_SHA256),*BOOTSTRAP.items()]:
    path=HERE/name
    need(not path.is_symlink() and path.is_file() and path.stat().st_nlink==1,'Aliased bootstrap '+name)
    need(hashlib.sha256(path.read_bytes()).hexdigest()==digest,'Changed bootstrap '+name)
helpers={}
for name in ['source_guard.py','receipt_guard.py']:
    raw=(HERE/name).read_bytes();space={'__name__':'_authenticated_'+name[:-3],'__file__':str(HERE/name)}
    exec(compile(raw,str(HERE/name),'exec',dont_inherit=True,optimize=0),space);helpers[name]=space
check=helpers['source_guard.py']['check'];validate=helpers['receipt_guard.py']['validate']
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--bindings-only',action='store_true');ap.add_argument('--output',type=Path);args=ap.parse_args()
    before=check(HERE)
    if args.bindings_only:
        print(json.dumps({'status':before['status'],'files':before['files'],'source_history':before.get('source_history')}));return
    root=Path(tempfile.mkdtemp(prefix='neutral-completion-replay-'));root.chmod(0o700)
    destination=(args.output or root/'REPLAY.json').absolute()
    for part in [destination,*destination.parents]:need(not part.is_symlink(),'Symlink output component')
    need(not destination.exists(),'Immutable output exists')
    need(not destination.resolve().is_relative_to(HERE.resolve()),'Output inside frozen package')
    commands=json.loads((HERE/'COMMANDS.json').read_bytes())['commands']
    report={'status':'RUNNING','wrapper_optimization':sys.flags.optimize,'scientific_compile_optimization':0,'python':sys.version,'bindings':before,'runs':[],'scratch':str(root)}
    try:
        shutil.copytree(HERE/'capsule',root,dirs_exist_ok=True)
        for path in [root,*root.rglob('*')]:
            if path.is_dir():path.chmod(0o700)
        for row in json.loads((HERE/'SOURCE-BINDINGS.json').read_bytes())['files']:
            if row['path'].startswith('capsule/'):
                need(hashlib.sha256((root/row['path'][8:]).read_bytes()).hexdigest()==row['sha256'],'Scratch input changed')
        workspace=root/'workspace'
        for index,command in enumerate(commands):
            cache=root/f'cache-{index}';cache.mkdir(mode=0o700)
            env=os.environ.copy()
            for key in ['PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','PYTHONSTARTUP','PYTHONINSPECT']:env.pop(key,None)
            env['PYTHONDONTWRITEBYTECODE']='1'
            argv=[sys.executable,'-I',*(['-O']*sys.flags.optimize),'-B','-X','pycache_prefix='+str(cache),str(HERE/'engine_adapter.py'),str(workspace),command['engine'],*command['argv']]
            started=time.monotonic()
            run=subprocess.run(argv,cwd=workspace,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=command['timeout_seconds'])
            (root/f'run-{index}.stdout').write_bytes(run.stdout);(root/f'run-{index}.stderr').write_bytes(run.stderr)
            report['runs'].append({'name':command['name'],'returncode':run.returncode,'seconds':time.monotonic()-started,'stdout_sha256':hashlib.sha256(run.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(run.stderr).hexdigest()})
            need(run.returncode==0,'Replay failed '+command['name']+'; '+str(root/f'run-{index}.stderr'))
        report['fresh_scientific_summary']=validate(HERE,workspace,commands)
        need(check(HERE)==before,'Frozen package changed during replay')
        report['status']='PASS_CONDITIONAL_COMPLETE_NEUTRAL_CALLER_AND_FUNDED_KAPPA'
        report['scope']=json.loads((HERE/'CLAIMS.json').read_bytes())
    except BaseException as error:
        report['status']='FAIL';report['error']=repr(error);raise
    finally:
        destination.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w',dir=destination.parent,prefix='.neutral-receipt-',delete=False) as out:
            out.write(json.dumps(report,indent=2,sort_keys=True)+'\n');temporary=Path(out.name)
        os.replace(temporary,destination)
        print(json.dumps({'status':report['status'],'receipt':str(destination),'scratch':str(root)}))
if __name__=='__main__':main()
